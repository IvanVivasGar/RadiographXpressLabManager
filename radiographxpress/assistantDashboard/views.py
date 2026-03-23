"""
Views for the Assistant Dashboard.
Handles UI rendering for hospital front-desk staff, including listing active study requests,
creating new requests, printing patient tickets, and managing assistant profiles.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from core.mixins import AssistantRequiredMixin
from .models import Assistant, StudyRequest
from .forms import StudyRequestForm
from patientsDashboard.models import Patient
from django.utils import timezone
from datetime import timedelta


class AssistantDashboardView(AssistantRequiredMixin, TemplateView):
    """
    Main dashboard view for Assistants.
    Displays:
    1. Active tickets (study requests that have not expired).
    2. Pending associate doctors who need account verification.
    Requires the user to belong to the 'Assistants' group.
    """
    template_name = 'assistantDashboard/assistant_dashboard.html'
    
    def get_context_data(self, **kwargs):
        """
        Adds active study requests and unverified associate doctors to the template context.
        Active tickets are either never printed or printed within the last 12 hours.
        """
        context = super().get_context_data(**kwargs)
        cutoff = timezone.now() - timedelta(hours=12)
        
        from django.db.models import Q
        context['active_tickets'] = StudyRequest.objects.filter(
            Q(first_printed_at__isnull=True) | Q(first_printed_at__gte=cutoff)
        ).select_related('id_patient__user').order_by('-created_at')

        from associateDoctorDashboard.models import AssociateDoctor
        context['pending_doctors'] = AssociateDoctor.objects.filter(
            is_email_verified=True, is_verified=False
        ).select_related('user').order_by('-user__date_joined')

        return context


class AllStudyRequestsView(AssistantRequiredMixin, ListView):
    """
    Paginated list view displaying all historical study requests in the system.
    Used for auditing and past reference.
    """
    model = StudyRequest
    template_name = 'assistantDashboard/all_requests.html'
    context_object_name = 'study_requests'
    paginate_by = 20

    def get_queryset(self):
        """
        Optimize database queries by selecting related user objects.
        Orders requests from newest to oldest.
        """
        return StudyRequest.objects.all().select_related(
            'id_patient__user', 'id_associate_doctor__user'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Injects the same active tickets and pending doctors summary as the main dashboard
        to maintain a consistent sidebar/header experience.
        """
        context = super().get_context_data(**kwargs)
        cutoff = timezone.now() - timedelta(hours=12)
        
        from django.db.models import Q
        context['active_tickets'] = StudyRequest.objects.filter(
            Q(first_printed_at__isnull=True) | Q(first_printed_at__gte=cutoff)
        ).select_related('id_patient__user').order_by('-created_at')

        from associateDoctorDashboard.models import AssociateDoctor
        context['pending_doctors'] = AssociateDoctor.objects.filter(
            is_email_verified=True, is_verified=False
        ).select_related('user').order_by('-user__date_joined')

        return context


class StudyRequestCreateView(AssistantRequiredMixin, CreateView):
    """
    Class-based view handling the creation of a new radiological StudyRequest.
    Includes logic to securely integrate with the Raditech PACS/RIS API synchronously
    before saving the local record.
    """
    model = StudyRequest
    form_class = StudyRequestForm
    template_name = 'assistantDashboard/new_study_request.html'
    success_url = reverse_lazy('assistant_dashboard')

    def form_valid(self, form):
        """
        Called when valid form data has been POSTed.
        1. Validates the selected patient ID from the hidden UI field.
        2. Saves the base StudyRequest locally.
        3. Attempts to register the patient and schedule the visit in the external Raditech API.
        4. Broadcasts a WebSocket event notifying other dashboards of the new request.
        """
        # Get patient from the hidden field populated by the JavaScript search
        patient_id = self.request.POST.get('id_patient')
        if not patient_id:
            form.add_error(None, 'Debe seleccionar un paciente.')
            return self.form_invalid(form)
        
        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            form.add_error(None, 'El paciente seleccionado no existe.')
            return self.form_invalid(form)
        
        form.instance.id_patient = patient
        messages.success(self.request, 'Solicitud de estudio creada exitosamente.')
        response = super().form_valid(form)

        # ── Raditech PACS/RIS Integration Section ──
        study_request = self.object
        try:
            from core.raditech_client import get_raditech_client, RaditechAPIError
            from core.raditech_mapping import get_raditech_mapping
            from core.models import Study
            from datetime import date

            client = get_raditech_client()

            # 1. Register patient in Raditech if not already registered
            if not patient.raditech_patient_id:
                # Auto-generate local Medical Record Number (MRN) if missing
                if not patient.mrn:
                    patient.mrn = f"RX-{patient.id_patient}"

                patient_data = client.add_patient(patient)
                patient.raditech_patient_id = patient_data.get("_id")
                # Use the MRN returned by Raditech to keep systems synchronized
                patient.mrn = patient_data.get("MRNumber", patient.mrn)
                patient.save(update_fields=["raditech_patient_id", "mrn"])

            # 2. Look up the Raditech modality/procedure IDs based on our local study name
            mapping = get_raditech_mapping(study_request.requested_study)
            if mapping:
                # 3. Schedule the visit procedure in the external RIS
                visit_data = client.add_visit_procedure(
                    patient=patient,
                    procedure_id=mapping["procedure_id"],
                    modality_id=mapping["modality_station_id"],
                    clinical_history=study_request.diagnosis,
                    scan_day=date.today().strftime("%Y-%m-%d"),
                )

                # Extract the accession number generated by Raditech
                accession = None
                investigations = visit_data.get("Investigations", [])
                if investigations:
                    accession = investigations[0].get("AccessionNumber")

                # 4. Create the core Study record in our database
                # Note: 'pacs_url' is left empty. It will be populated later by the background sync worker.
                Study.objects.create(
                    pacs_url="",
                    email_sent=False,
                    date=date.today(),
                    raditech_visit_id=visit_data.get("_id"),
                    accession_number=accession,
                    id_study_request=study_request,
                    id_report=None,
                    id_patient=patient,
                )
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    "No Raditech mapping found for study type '%s'. "
                    "Study record created without PACS scheduling.",
                    study_request.requested_study
                )
                # Fallback: Create a local Study record without external Raditech identifiers
                Study.objects.create(
                    pacs_url="",
                    email_sent=False,
                    date=date.today(),
                    id_study_request=study_request,
                    id_report=None,
                    id_patient=patient,
                )

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Raditech integration error during study creation: %s", e, exc_info=True)
            # The study request was already saved locally, so we only warn the user
            # instead of failing the entire HTTP creation request.
            messages.warning(
                self.request,
                f'La solicitud se creó pero hubo un error al sincronizar con PACS/RIS: {e}'
            )

        # Notify connected clients (Assistants, Doctors) via WebSocket
        from core.notifications import notify_study_request_created
        notify_study_request_created(self.object)

        return response


class AssistantProfileView(AssistantRequiredMixin, DetailView):
    """
    Displays the profile settings page for the currently logged-in Assistant.
    """
    model = Assistant
    template_name = 'assistantDashboard/assistant_profile.html'
    context_object_name = 'assistant'

    def get_object(self):
        """Returns the assistant profile associated with the active user."""
        return self.request.user.assistant_profile


@login_required
def print_ticket(request, study_request_id):
    """
    Renders a simple printable HTML ticket containing the patient's generated
    PDF password and study barcodes.
    
    The first time this view is accessed for a ticket, it sets the `first_printed_at`
    timestamp on the StudyRequest, which starts a 12-hour expiration countdown.
    
    Args:
        request: The HTTP request object.
        study_request_id: Primary key of the StudyRequest to print.
    """
    study_request = get_object_or_404(StudyRequest, pk=study_request_id)
    if not study_request.first_printed_at:
        study_request.first_printed_at = timezone.now()
        study_request.save(update_fields=['first_printed_at'])
        
    return render(request, 'assistantDashboard/ticket.html', {
        'study_request': study_request,
    })


@login_required
def assistant_logout(request):
    """
    Handles the Assistant logout process and redirects to the public login page.
    """
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from core.mixins import AssistantRequiredMixin
from .models import Assistant, StudyRequest
from .forms import StudyRequestForm
from patientsDashboard.models import Patient
from django.utils import timezone
from datetime import timedelta


class AssistantDashboardView(AssistantRequiredMixin, ListView):
    """Main dashboard: active tickets + all study requests."""
    model = StudyRequest
    template_name = 'assistantDashboard/assistant_dashboard.html'
    context_object_name = 'study_requests'

    def get_queryset(self):
        return StudyRequest.objects.all().select_related(
            'id_patient__user', 'id_associate_doctor__user'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cutoff = timezone.now() - timedelta(hours=12)
        # Active tickets: never printed OR printed within 12hrs
        from django.db.models import Q
        context['active_tickets'] = StudyRequest.objects.filter(
            Q(first_printed_at__isnull=True) | Q(first_printed_at__gte=cutoff)
        ).select_related('id_patient__user').order_by('-created_at')
        return context


class StudyRequestCreateView(AssistantRequiredMixin, CreateView):
    """Form to create a new study request with patient search."""
    model = StudyRequest
    form_class = StudyRequestForm
    template_name = 'assistantDashboard/new_study_request.html'
    success_url = reverse_lazy('assistant_dashboard')

    def form_valid(self, form):
        # Get patient from the hidden field
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

        # Notify via WebSocket
        from core.notifications import notify_study_request_created
        notify_study_request_created(self.object)

        return response


class AssistantProfileView(AssistantRequiredMixin, DetailView):
    """Assistant profile page."""
    model = Assistant
    template_name = 'assistantDashboard/assistant_profile.html'
    context_object_name = 'assistant'

    def get_object(self):
        return self.request.user.assistant_profile


@login_required
def print_ticket(request, study_request_id):
    """Render a simple printable ticket with the PDF password.
    Marks first_printed_at on first access to start the 12hr countdown."""
    study_request = get_object_or_404(StudyRequest, pk=study_request_id)
    if not study_request.first_printed_at:
        study_request.first_printed_at = timezone.now()
        study_request.save(update_fields=['first_printed_at'])
    return render(request, 'assistantDashboard/ticket.html', {
        'study_request': study_request,
    })


@login_required
def assistant_logout(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect, get_object_or_404
from core.models import Study, Report
from .models import ReportingDoctor
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from core.mixins import DoctorRequiredMixin
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


class PendingStudiesView(DoctorRequiredMixin, ListView):
    """
    Displays the grid of studies waiting for analysis.
    Corresponds to the 'Estudios Pendientes' image.
    """
    model = Study
    template_name = 'doctorsDashboard/pending_studies.html'
    context_object_name = 'studies'

    def get_queryset(self):
        # Filter for studies that are pending.
        # "Pending" now means: No report associated with it.
        # If a report exists, it's either In Progress (locked) or Completed.
        return Study.objects.filter(id_report__isnull=True).order_by('date')

class StudiesInProgressView(DoctorRequiredMixin, ListView):
    """
    Displays studies locked by the current doctor.
    """
    model = Study
    template_name = 'doctorsDashboard/studies_in_progress.html'
    context_object_name = 'studies'
    
    def get_queryset(self):
        # Show studies where the report is IN_PROGRESS and handled by THIS doctor
        try:
            if hasattr(self.request.user, 'reporting_doctor_profile'):
                doctor = self.request.user.reporting_doctor_profile
                return Study.objects.filter(
                    id_report__status=Report.IN_PROGRESS,
                    id_report__doctor_in_charge=doctor
                ).order_by('date')
            else:
                return Study.objects.none()
        except ReportingDoctor.DoesNotExist:
            return Study.objects.none()

class DoctorProfileView(DoctorRequiredMixin, DetailView):
    """
    Shows the doctor's profile and their history of completed studies.
    """
    model = ReportingDoctor
    template_name = 'doctorsDashboard/doctor_profile.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Assuming we can filter reports by this doctor
        # Note: You might need to adjust the filter based on how Study links to Report/Doctor in your DB logic
        context['history_studies'] = Study.objects.filter(
            id_report__doctor_in_charge=self.object
        ).order_by('-date')
        return context

class StudyReportCreateView(DoctorRequiredMixin, CreateView):
    """
    The main workspace for the doctor to view the X-ray and write the report.
    Corresponds to the 'Generar Reporte' split-screen image.
    """
    model = Report
    template_name = 'doctorsDashboard/study_report.html'
    fields = ['about', 'findings', 'conclusions', 'recommendations', 'patients_description']
    
    def dispatch(self, request, *args, **kwargs):
        # We need the study ID to know what we are reporting on
        self.study = get_object_or_404(Study, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the study to the template to display the X-ray (pacs_url)
        context['study'] = self.study
        return context

    def form_valid(self, form):
        # 1. Assign the logged-in doctor
        # We assume the logged-in Django User is linked to a ReportingDoctor
        try:
            if hasattr(self.request.user, 'reporting_doctor_profile'):
                reporting_doctor = self.request.user.reporting_doctor_profile
                form.instance.doctor_in_charge = reporting_doctor
            else:
                 raise ValueError(f"No ReportingDoctor profile linked to user {self.request.user.username}")
        except Exception: 
            # Should be caught by hasattr check theoretically, but for safety
            raise ValueError(f"Error accessing profile for user {self.request.user.username}")
        
        # 2. Update status to COMPLETED
        form.instance.status = Report.COMPLETED

        # 3. Generate Secure Password (18 chars)
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        secure_password = ''.join(secrets.choice(alphabet) for i in range(18))
        form.instance.password = secure_password
        
        # 4. Save the report
        self.object = form.save()

        # 5. Link the new report to the Study
        self.study.id_report = self.object
        # self.study.status = Study.COMPLETED  <-- REMOVED, FIELD DELETED
        self.study.save()

        return super().form_valid(form)

    def get_success_url(self):
        # Redirect back to the pending list after finishing
        return reverse_lazy('pendingStudies')

@require_POST
@login_required
def lock_study(request, study_id):
    """
    API to lock a study for the current doctor.
    Creates an empty Report with status IN_PROGRESS.
    """
    try:
        study = Study.objects.get(pk=study_id)
        
        if not hasattr(request.user, 'reporting_doctor_profile'):
             return JsonResponse({'status': 'error', 'message': 'Doctor profile not found'}, status=403)
             
        doctor = request.user.reporting_doctor_profile
        
        # Check if already locked
        if study.id_report and study.id_report.status == Report.IN_PROGRESS:
            if study.id_report.doctor_in_charge != doctor:
                 return JsonResponse({'status': 'error', 'message': 'Study already locked by another doctor'}, status=403)
            else:
                 return JsonResponse({'status': 'ok', 'message': 'Already locked by you'})
        
        # Create new In Progress Report
        report = Report.objects.create(
            status=Report.IN_PROGRESS,
            doctor_in_charge=doctor,
            about="", 
            patients_description="",
            findings="",
            conclusions="",
            recommendations=""
        )
        
        # Link to Study
        study.id_report = report
        study.save()
        
        return JsonResponse({'status': 'ok'})
        
    except (Study.DoesNotExist, ReportingDoctor.DoesNotExist, AttributeError):
        return JsonResponse({'status': 'error', 'message': 'Study or Doctor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def doctor_logout(request):
    """
    Cleans up any "In Progress" reports for the current doctor before logging out.
    This ensures locked studies are returned to the pool.
    """
    if request.user.is_authenticated:
        try:
            # We use the relation to get the profile
            if hasattr(request.user, 'reporting_doctor_profile'):
                doctor = request.user.reporting_doctor_profile
                
                # Find all reports in progress for this doctor
                reports_in_progress = Report.objects.filter(
                    status=Report.IN_PROGRESS,
                    doctor_in_charge=doctor
                )
                
                for report in reports_in_progress:
                    # 1. Find associated studies
                    # Note: Study.id_report is a ForeignKey to Report.
                    studies = Study.objects.filter(id_report=report)
                    for study in studies:
                        # CRITICAL: Unlink the report from the study so deleting the report doesn't cascade delete the study
                        # Because on_delete=models.CASCADE is set on Study.id_report
                        study.id_report = None
                        study.save()
                    
                    # 2. Delete the report draft
                    report.delete()
                    
        except Exception as e:
            # Log error but proceed with logout
            print(f"Error during logout cleanup: {e}")
            
    logout(request)
    return redirect("/")

@login_required
def my_profile(request):
    """
    Redirects to the profile of the currently logged-in doctor.
    """
    try:
        if hasattr(request.user, 'reporting_doctor_profile'):
            doctor = request.user.reporting_doctor_profile
            return redirect('doctorProfile', pk=doctor.pk)
        else:
             # Fallback or error
             return redirect('/')
    except ReportingDoctor.DoesNotExist:        
        return redirect('/') # Or error page
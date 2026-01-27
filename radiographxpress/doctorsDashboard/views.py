from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient, Study, Report, AssociatedDoctor, StudyRequest, ReportingDoctor
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from radiographxpress.mixins import DoctorRequiredMixin
from django.contrib.auth import logout

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# ... (existing imports)

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
            doctor = ReportingDoctor.objects.get(email=self.request.user.email)
            return Study.objects.filter(
                id_report__status=Report.IN_PROGRESS,
                id_report__doctor_in_charge=doctor
            ).order_by('date')
        except ReportingDoctor.DoesNotExist:
            return Study.objects.none()

@require_POST
@login_required
def lock_study(request, study_id):
    """
    API to lock a study for the current doctor.
    Creates an empty Report with status IN_PROGRESS.
    """
    try:
        study = Study.objects.get(pk=study_id)
        doctor = ReportingDoctor.objects.get(email=request.user.email)
        
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
        
    except (Study.DoesNotExist, ReportingDoctor.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Study or Doctor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ... (keep existing DoctorProfileView etc)

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
        # We assume the logged-in Django User's email matches the ReportingDoctor's email
        try:
            reporting_doctor = ReportingDoctor.objects.get(email=self.request.user.email)
            form.instance.doctor_in_charge = reporting_doctor
        except ReportingDoctor.DoesNotExist:
            # Handle case where no doctor matches the user (should ideally not happen if data is consistent)
            # For now, maybe raise error or redirect. In prod, log this.
            # We'll fail loudly for now so we catch it during dev.
            raise ValueError(f"No ReportingDoctor found for email {self.request.user.email}")
        
        # 2. Update status to COMPLETED
        form.instance.status = Report.COMPLETED
        
        # 3. Save the report
        self.object = form.save()

        # 4. Link the new report to the Study
        self.study.id_report = self.object
        # self.study.status = Study.COMPLETED  <-- REMOVED, FIELD DELETED
        self.study.save()

        return super().form_valid(form)

    def get_success_url(self):
        # Redirect back to the pending list after finishing
        return reverse_lazy('pendingStudies')

def doctor_logout(request):
    """
    Cleans up any "In Progress" reports for the current doctor before logging out.
    This ensures locked studies are returned to the pool.
    """
    if request.user.is_authenticated:
        try:
            # We use filter().first() or loop because multiple might exist in edge cases
            doctor_qs = ReportingDoctor.objects.filter(email=request.user.email)
            if doctor_qs.exists():
                doctor = doctor_qs.first()
                
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
        doctor = ReportingDoctor.objects.get(email=request.user.email)
        return redirect('doctorProfile', pk=doctor.pk)
    except ReportingDoctor.DoesNotExist:
        return redirect('/') # Or error page
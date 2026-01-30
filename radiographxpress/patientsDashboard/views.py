from django.shortcuts import render, redirect
from core.models import Study, Report
from patientsDashboard.models import Patient
from associateDoctorDashboard.models import AssociateDoctor
from assistantDashboard.models import StudyRequest
from doctorsDashboard.models import ReportingDoctor
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from core.mixins import PatientRequiredMixin
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# PATIENT VIEWS
class PatientDashboardView(PatientRequiredMixin, ListView):
    model = Study
    template_name = 'patientsDashboard/patientsDashboard.html'
    context_object_name = 'studies'

    def get_queryset(self):
        # We need the patient profile to filter studies
        if hasattr(self.request.user, 'patient_profile'):
            patient = self.request.user.patient_profile
            # Show studies for this patient that have a report (completed diagnosis)
            return Study.objects.filter(
                id_patient=patient,
                id_report__isnull=False
            ).order_by('-date')
        return Study.objects.none()

class PatientProfileView(PatientRequiredMixin, DetailView):
    model = Patient
    template_name = 'patientsDashboard/patient_profile.html'
    context_object_name = 'patient'

@login_required
def patient_logout(request):
    logout(request)
    return redirect('patientsDashboard:patients_login')

def signup(request):
    # Placeholder for signup view
    return render(request, 'registration/signup.html') # Placeholder template, might not exist yet

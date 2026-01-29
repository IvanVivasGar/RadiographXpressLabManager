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
    model = Patient
    template_name = 'patientsDashboard/patient_dashboard.html'
    context_object_name = 'patient'

class PatientProfileView(PatientRequiredMixin, DetailView):
    model = Patient
    template_name = 'patientsDashboard/patient_profile.html'
    context_object_name = 'patient'

@login_required
def logout(request):
    logout(request)
    return redirect('login')

def signup(request):
    # Placeholder for signup view
    return render(request, 'registration/signup.html') # Placeholder template, might not exist yet

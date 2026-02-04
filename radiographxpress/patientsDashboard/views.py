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
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .forms import PatientForm

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
    template_name = 'patientsDashboard/profile.html'
    context_object_name = 'patient'

    def get_object(self):
        return self.request.user.patient_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Mi Perfil'
        return context

class PatientProfileUpdateView(PatientRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patientsDashboard/profile_edit.html'
    success_url = reverse_lazy('patientsDashboard:profile')

    def get_object(self):
        return self.request.user.patient_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Perfil'
        return context

@login_required
def patient_logout(request):
    logout(request)
    return redirect('login')

from django.contrib.auth import login
from .forms import PatientSignupForm

def signup(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            patient = form.save()
            login(request, patient.user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('patientsDashboard:patientsDashboard')
    else:
        form = PatientSignupForm()
    
    return render(request, 'patientsDashboard/registration/signup.html', {'form': form})

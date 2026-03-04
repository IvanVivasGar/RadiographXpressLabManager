from django.shortcuts import render, redirect
from django.views.generic import ListView
from core.mixins import AssociatedDoctorRequiredMixin
from patientsDashboard.models import Patient
from associateDoctorDashboard.models import AssociateDoctor
from .forms import AssociateDoctorSignupForm

class DashboardView(AssociatedDoctorRequiredMixin, ListView):
    template_name = 'associateDoctorDashboard/associateDashboard.html'
    context_object_name = 'patients'

    def get_queryset(self):
        # returns all patients associated with the current doctor
        if hasattr(self.request.user, 'associate_doctor_profile'):
            doctor = self.request.user.associate_doctor_profile
            return doctor.patients.all().prefetch_related('study_set')
        return Patient.objects.none()

def signup(request):
    if request.method == 'POST':
        form = AssociateDoctorSignupForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            return redirect('login')
    else:
        form = AssociateDoctorSignupForm()
    
    return render(request, 'associateDoctorDashboard/registration/signup.html', {'form': form})

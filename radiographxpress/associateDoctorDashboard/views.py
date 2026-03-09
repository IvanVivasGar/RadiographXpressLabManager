from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from core.mixins import AssociatedDoctorRequiredMixin
from patientsDashboard.models import Patient
from associateDoctorDashboard.models import AssociateDoctor
from .forms import AssociateDoctorSignupForm
from core.email_service import send_verification_email
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

class DashboardView(AssociatedDoctorRequiredMixin, ListView):
    template_name = 'associateDoctorDashboard/associateDashboard.html'
    context_object_name = 'patients'

    def get_queryset(self):
        # returns all patients associated with the current doctor
        if hasattr(self.request.user, 'associate_doctor_profile'):
            doctor = self.request.user.associate_doctor_profile
            return doctor.patients.all().prefetch_related('study_set')
        return Patient.objects.none()

class ProfileView(AssociatedDoctorRequiredMixin, DetailView):
    model = AssociateDoctor
    template_name = 'associateDoctorDashboard/profile.html'
    context_object_name = 'doctor'

    def get_object(self):
        return self.request.user.associate_doctor_profile

def signup(request):
    if request.method == 'POST':
        form = AssociateDoctorSignupForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            # Deactivate user until email is verified
            doctor.user.is_active = False
            doctor.user.save()
            # Send verification email
            send_verification_email(doctor.user, request)
            return render(request, 'core/emails/verification_pending.html')
    else:
        form = AssociateDoctorSignupForm()
    
    return render(request, 'associateDoctorDashboard/registration/signup.html', {'form': form})

@login_required
def associate_logout(request):
    auth_logout(request)
    return redirect('login')

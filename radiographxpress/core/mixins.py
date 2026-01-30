from django.contrib.auth.mixins import UserPassesTestMixin

class DoctorRequiredMixin(UserPassesTestMixin):
    """
    Ensures the user is a member of the 'Doctors' group.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Doctors').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'reporting_doctor_profile'):
            context['reporting_doctor'] = self.request.user.reporting_doctor_profile
        return context

class PatientRequiredMixin(UserPassesTestMixin):
    """
    Ensures the user is a member of the 'Patients' group.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Patients').exists()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'patient_profile'):
            context['patient'] = self.request.user.patient_profile
        return context

class AssociatedDoctorRequiredMixin(UserPassesTestMixin):
    """
    Ensures the user is a member of the 'AssociatedDoctors' group.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='AssociatedDoctors').exists()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'associated_doctor_profile'):
            context['associated_doctor'] = self.request.user.associated_doctor_profile
        return context

class AssistantRequiredMixin(UserPassesTestMixin):
    """
    Ensures the user is a member of the 'Assistants' group.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'assistant_profile'):
            context['assistant'] = self.request.user.assistant_profile
        return context

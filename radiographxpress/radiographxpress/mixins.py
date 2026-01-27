from django.contrib.auth.mixins import UserPassesTestMixin

class DoctorRequiredMixin(UserPassesTestMixin):
    """
    Ensures the user is a member of the 'Doctors' group.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Doctors').exists()

class PatientRequiredMixin(UserPassesTestMixin):
    """
    Ensures the user is a member of the 'Patients' group.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Patients').exists()

class AssistantRequiredMixin(UserPassesTestMixin):
    """
    Ensures the user is a member of the 'Assistants' group.
    """
    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()

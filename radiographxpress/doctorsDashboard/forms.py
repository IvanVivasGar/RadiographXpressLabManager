from django import forms
from .models import Patient, Study, Report, AssociatedDoctor, StudyRequest, ReportingDoctor

# CRUD - Create
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'last_name', 'password', 'email', 'address', 'phone']

class ReportingDoctorForm(forms.ModelForm):
    class Meta:
        model = ReportingDoctor
        fields = ['name', 'last_name', 'password', 'email', 'address', 'phone', 'university', 'professional_id', 'specialty']

class AssociatedDoctorForm(forms.ModelForm):
    class Meta:
        model = AssociatedDoctor
        fields = ['name', 'last_name', 'password', 'email', 'address', 'phone']

class StudyRequestForm(forms.ModelForm):
    class Meta:
        model = StudyRequest
        fields = ['email_doctor', 'requested_study']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['about', 'patients_description', 'findings', 'conclusions', 'recommendations']

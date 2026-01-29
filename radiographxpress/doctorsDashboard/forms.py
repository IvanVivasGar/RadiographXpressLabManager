from django import forms
from core.models import Study, Report
from .models import ReportingDoctor

# CRUD - Create
class ReportingDoctorForm(forms.ModelForm):
    class Meta:
        model = ReportingDoctor
        fields = ['name', 'last_name', 'password', 'email', 'address', 'phone', 'university', 'professional_id', 'specialty']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['about', 'patients_description', 'findings', 'conclusions', 'recommendations']

from django import forms
from .models import AssociateDoctor

class AssociatedDoctorForm(forms.ModelForm):
    class Meta:
        model = AssociateDoctor
        fields = ['name', 'last_name', 'password', 'email', 'address', 'phone']

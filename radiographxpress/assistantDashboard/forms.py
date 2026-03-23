"""
Form definitions for the Assistant Dashboard.
Provides Django ModelForms for securely receiving and validating data 
when creating new Study Requests from the front-desk interface.
"""
from django import forms
from .models import StudyRequest


class StudyRequestForm(forms.ModelForm):
    """
    Form tightly coupled to the StudyRequest model.
    Used by the Assistant to capture the preliminary details of a patient's study
    (Diagnosis, Study Type, and an optional referring Associate Doctor).
    The Patient association is handled dynamically in the View via a hidden input,
    so it is excluded from these explicit fields.
    """
    class Meta:
        model = StudyRequest
        fields = ['diagnosis', 'requested_study', 'id_associate_doctor']
        labels = {
            'diagnosis': 'Diagnóstico',
            'requested_study': 'Estudio Solicitado',
            'id_associate_doctor': 'Doctor Asociado (Opcional)',
        }
        widgets = {
            'diagnosis': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ingrese el diagnóstico',
            }),
            'requested_study': forms.Select(attrs={
                'class': 'form-input',
            }),
            'id_associate_doctor': forms.Select(attrs={
                'class': 'form-input',
            }),
        }

from django import forms
from .models import StudyRequest


class StudyRequestForm(forms.ModelForm):
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
            'requested_study': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Radiografía de Tórax',
            }),
            'id_associate_doctor': forms.Select(attrs={
                'class': 'form-input',
            }),
        }

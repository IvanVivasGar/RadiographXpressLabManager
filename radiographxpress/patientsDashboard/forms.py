from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    email = forms.EmailField(label='Email')

    class Meta:
        model = Patient
        fields = ['address', 'phone', 'gender']

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        patient = super(PatientForm, self).save(commit=False)
        if self.cleaned_data.get('first_name'):
            patient.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            patient.user.last_name = self.cleaned_data['last_name']
        if self.cleaned_data.get('email'):
            patient.user.email = self.cleaned_data['email']
        
        if commit:
            patient.user.save()
            patient.save()
        return patient

class PatientSignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellidos')
    email = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Contraseña')

    class Meta:
        model = Patient
        fields = ['address', 'phone', 'gender']
        labels = {
            'address': 'Dirección',
            'phone': 'Teléfono',
            'gender': 'Género'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Patient.objects.filter(user__email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        from django.contrib.auth.models import User
        
        # Create user
        # We use email as username since login expects email
        user = User.objects.create_user(
            username=self.cleaned_data['email'], 
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        patient = super(PatientSignupForm, self).save(commit=False)
        patient.user = user
        
        if commit:
            patient.save()
        return patient

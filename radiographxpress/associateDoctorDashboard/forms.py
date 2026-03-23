"""
Form definitions for the Associate Doctor Dashboard.
Handles the secure signup process and validation for new referring physicians.
"""
from django import forms
from .models import AssociateDoctor
from django.contrib.auth.models import User

class AssociateDoctorSignupForm(forms.ModelForm):
    """
    Custom registration form for Associate Doctors.
    Collects both base User data (email, name, password) and specific 
    AssociateDoctor profile data (professional ID, university) in a single step.
    """
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellidos')
    email = forms.EmailField(label='Correo Electrónico')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Contraseña')
    
    # Associate Doctor specific fields
    professional_id = forms.CharField(label='Cédula Profesional', max_length=100)
    university = forms.CharField(label='Universidad', max_length=100)

    class Meta:
        model = AssociateDoctor
        fields = ['address', 'phone', 'university', 'professional_id']
        labels = {
            'address': 'Dirección',
            'phone': 'Teléfono',
        }

    def clean_email(self):
        """
        Validates that the provided email address is unique across the entire 
        system (checked against the base Django User model).
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        """
        Cross-field validation.
        Ensures that the password and password_confirm fields match exactly.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        """
        Overrides default save to handle the dual-model creation logic.
        1. Creates the base auth.User object with the validated credentials.
        2. Assigns the newly created User to the AssociateDoctor profile.
        3. Persists the profile to the database.
        
        Args:
            commit (bool): If True, both the User and Profile are saved to DB.
        
        Returns:
            AssociateDoctor: The newly created profile instance.
        """
        # Create base user instance
        user = User.objects.create_user(
            username=self.cleaned_data['email'], 
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        # Instantiate profile without saving yet
        doctor = super(AssociateDoctorSignupForm, self).save(commit=False)
        doctor.user = user
        
        if commit:
            doctor.save()
        return doctor

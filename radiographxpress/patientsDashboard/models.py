from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='patient_profile')
    id_patient = models.AutoField(primary_key=True)
    # name and last name are in the user model
    # password field removed
    # email field removed
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=OTHER)
    associated_doctors = models.ManyToManyField('associateDoctorDashboard.AssociateDoctor', related_name='patients')

    @property
    def first_name(self):
        if self.user:
            return self.user.first_name
        return ""

    @property
    def last_name(self):
        if self.user:
            return self.user.last_name
        return ""
    
    @property
    def email(self):
        if self.user:
            return self.user.email
        return ""
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
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    # name and last name are in the user model
    # password field removed
    # email field removed
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=OTHER)
    is_email_verified = models.BooleanField(default=False)
    raditech_patient_id = models.CharField(max_length=100, null=True, blank=True)
    mrn = models.CharField(max_length=50, null=True, blank=True, unique=True)
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
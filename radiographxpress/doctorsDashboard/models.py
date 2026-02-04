from django.db import models
from django.contrib.auth.models import User
    
class ReportingDoctor(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='reporting_doctor_profile')
    id_doctor = models.AutoField(primary_key=True)
    # name and last name are in the user model
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=OTHER)
    # email field removed
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    professional_id = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)

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
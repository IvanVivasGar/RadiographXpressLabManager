from django.db import models
from django.contrib.auth.models import User

class AssociateDoctor(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='associate_doctor_profile')
    id_associate_doctor = models.AutoField(primary_key=True)
    # name and last name are in the user model
    # email field removed
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    professional_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    university = models.CharField(max_length=100, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=OTHER)
    
    def first_name(self):
        return self.user.first_name
    
    def last_name(self):
        return self.user.last_name

    def __str__(self):
        if self.user:
            prefix = 'Dra.' if self.gender == self.FEMALE else 'Dr.'
            return f"{prefix} {self.user.first_name} {self.user.last_name}"
        return f"Doctor Asociado #{self.pk}"
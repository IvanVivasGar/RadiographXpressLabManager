from django.db import models
from django.contrib.auth.models import User

class AssociateDoctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='associate_doctor_profile')
    id_associate_doctor = models.CharField(primary_key=True) # Note: CharField PK might cause issues if not managed carefully
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # password field removed
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
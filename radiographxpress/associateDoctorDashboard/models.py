from django.db import models
from django.contrib.auth.models import User

class AssociateDoctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='associate_doctor_profile')
    id_associate_doctor = models.AutoField(primary_key=True)
    # name and last name are in the user model
    # email field removed
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    professional_id = models.CharField(max_length=100, null=True, blank=True)
    university = models.CharField(max_length=100, null=True, blank=True)
    
    def first_name(self):
        return self.user.first_name
    
    def last_name(self):
        return self.user.last_name
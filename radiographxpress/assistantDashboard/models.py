from django.db import models
from django.contrib.auth.models import User

class Assistant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='assistant_profile')
    id_assistant = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # password field removed
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

class StudyRequest(models.Model):
    id_solicitud_estudio = models.IntegerField(primary_key=True)
    email_doctor = models.EmailField(max_length=100)
    diagnosis = models.CharField(max_length=100)
    requested_study = models.CharField(max_length=100)
    id_patient = models.ForeignKey('patientsDashboard.Patient', on_delete=models.CASCADE)
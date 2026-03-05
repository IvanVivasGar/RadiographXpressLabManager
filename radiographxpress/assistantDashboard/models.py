from django.db import models
from django.contrib.auth.models import User
import secrets
import string

class Assistant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='assistant_profile')
    id_assistant = models.AutoField(primary_key=True)
    # name and last name are in the user model
    # email field removed
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

class StudyRequest(models.Model):
    id_solicitud_estudio = models.IntegerField(primary_key=True)
    diagnosis = models.CharField(max_length=100)
    requested_study = models.CharField(max_length=100)
    pdf_password = models.CharField(max_length=18, blank=True)
    id_patient = models.ForeignKey('patientsDashboard.Patient', on_delete=models.CASCADE)
    id_associate_doctor = models.ForeignKey('associateDoctorDashboard.AssociateDoctor', on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pdf_password:
            alphabet = string.ascii_letters + string.digits
            self.pdf_password = ''.join(secrets.choice(alphabet) for _ in range(18))
        super().save(*args, **kwargs)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
    id_solicitud_estudio = models.AutoField(primary_key=True)
    diagnosis = models.CharField(max_length=100)
    requested_study = models.CharField(max_length=100)
    pdf_password = models.CharField(max_length=18, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    first_printed_at = models.DateTimeField(null=True, blank=True)
    id_patient = models.ForeignKey('patientsDashboard.Patient', on_delete=models.CASCADE)
    id_associate_doctor = models.ForeignKey('associateDoctorDashboard.AssociateDoctor', on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pdf_password:
            alphabet = string.ascii_letters + string.digits
            self.pdf_password = ''.join(secrets.choice(alphabet) for _ in range(18))
        super().save(*args, **kwargs)

    @property
    def is_ticket_printable(self):
        """
        Ticket is always available until first printed.
        Once printed, it stays active for 12 hours from first print time.
        """
        if not self.first_printed_at:
            return True
        return timezone.now() - self.first_printed_at < timezone.timedelta(hours=12)
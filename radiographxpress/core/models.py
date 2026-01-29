from django.db import models

class Study(models.Model):
    id_study = models.AutoField(primary_key=True)
    pacs_url = models.CharField(max_length=100)
    email_sent = models.BooleanField(default=False)
    date = models.DateField()
    id_study_request = models.ForeignKey('assistantDashboard.StudyRequest', on_delete=models.CASCADE)
    id_report = models.ForeignKey('Report', on_delete=models.CASCADE, null=True, blank=True)
    id_patient = models.ForeignKey('patientsDashboard.Patient', on_delete=models.CASCADE)

class Report(models.Model):
    PENDING = 'PEN'
    IN_PROGRESS = 'PRO'
    COMPLETED = 'COM'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    id_report = models.AutoField(primary_key=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=PENDING)
    about = models.CharField(max_length=200)
    patients_description = models.CharField(max_length=200)
    findings = models.TextField()
    conclusions = models.TextField()
    recommendations = models.TextField()
    password = models.CharField(max_length=18, default="")
    doctor_in_charge = models.ForeignKey('doctorsDashboard.ReportingDoctor', on_delete=models.CASCADE)
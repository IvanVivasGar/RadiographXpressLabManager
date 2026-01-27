from django.db import models

# Create your models here.
class Patient(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    id_patient = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=OTHER)
    associated_doctors = models.ManyToManyField('AssociatedDoctor', related_name='patients')
    
class Study(models.Model):
    id_study = models.AutoField(primary_key=True)
    pacs_url = models.CharField(max_length=100)
    email_sent = models.BooleanField(default=False)
    date = models.DateField()
    id_study_request = models.ForeignKey('StudyRequest', on_delete=models.CASCADE)
    id_report = models.ForeignKey('Report', on_delete=models.CASCADE, null=True, blank=True)
    id_patient = models.ForeignKey('Patient', on_delete=models.CASCADE)

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
    doctor_in_charge = models.ForeignKey('ReportingDoctor', on_delete=models.CASCADE)
    
class AssociatedDoctor(models.Model):
    id_associated_doctor = models.CharField(primary_key=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

class StudyRequest(models.Model):
    id_solicitud_estudio = models.IntegerField(primary_key=True)
    email_doctor = models.EmailField(max_length=100)
    diagnosis = models.CharField(max_length=100)
    requested_study = models.CharField(max_length=100)
    id_associated_doctor = models.ForeignKey('AssociatedDoctor', on_delete=models.CASCADE)
    
class ReportingDoctor(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'O'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    id_doctor = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=OTHER)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    professional_id = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)

"""
Create a model for the assistant.
"""
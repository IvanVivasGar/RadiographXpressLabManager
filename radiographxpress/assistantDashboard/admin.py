from django.contrib import admin
from doctorsDashboard.models import Patient, AssociatedDoctor, StudyRequest

# Register your models here.
admin.site.register(Patient)
admin.site.register(AssociatedDoctor)
admin.site.register(StudyRequest)
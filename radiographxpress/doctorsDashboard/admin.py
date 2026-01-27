from django.contrib import admin
from .models import ReportingDoctor, Report, Study

# Register your models here.
admin.site.register(ReportingDoctor)
admin.site.register(Report)
admin.site.register(Study)

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('report/<int:report_id>/pdf/', views.generate_report_pdf, name='report_pdf'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
]

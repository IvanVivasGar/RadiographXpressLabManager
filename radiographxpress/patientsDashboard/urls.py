from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'patientsDashboard'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='patientsDashboard/login.html'), name='patients_login'),
    # Placeholder for signup, will be implemented later or if user requests
    path('signup/', views.signup, name='signup'), 
    path('profile/', views.PatientProfileView.as_view(), name='profile'),
    path('patientsDashboard/', views.PatientDashboardView.as_view(), name='patientsDashboard'),
    path('logout/', views.patient_logout, name='logout'),
]
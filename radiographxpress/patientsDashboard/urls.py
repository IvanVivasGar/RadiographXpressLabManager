from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api
from core import views as core_views

app_name = 'patientsDashboard'

urlpatterns = [
    # Placeholder for signup, will be implemented later or if user requests
    path('signup/', views.signup, name='signup'),
    path('profile/', views.PatientProfileView.as_view(), name='profile'),
    path('profile/edit/', views.PatientProfileUpdateView.as_view(), name='profile_edit'),
    path('', views.PatientDashboardView.as_view(), name='patientsDashboard'),
    path('studyDetail/<int:id_study>/', core_views.study_detail, name='studyDetail'),
    path('logout/', views.patient_logout, name='logout'),
    path('manage-doctors/', views.ManageDoctorsView.as_view(), name='manage_doctors'),
    path('api/doctor-search/', api.doctor_search, name='doctor_search_api'),
    path('api/toggle-doctor/', api.toggle_doctor, name='toggle_doctor_api'),
]
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.PendingStudiesView.as_view(), name='pendingStudies'),
    path('doctorProfile/<int:pk>/', views.DoctorProfileView.as_view(), name='doctorProfile'),
    path('studyReportCreate/<int:pk>/', views.StudyReportCreateView.as_view(), name='studyReportCreate'),
    path('lockStudy/<int:study_id>/', views.lock_study, name='lockStudy'),
    path('studiesInProgress/', views.StudiesInProgressView.as_view(), name='studiesInProgress'),
    path('myProfile/', views.my_profile, name='myProfile'),
    path('logout/', views.doctor_logout, name='doctor_logout'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='doctor_login'),
]
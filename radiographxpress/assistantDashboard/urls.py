from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.AssistantDashboardView.as_view(), name='assistant_dashboard'),
    path('all-requests/', views.AllStudyRequestsView.as_view(), name='all_study_requests'),
    path('new-request/', views.StudyRequestCreateView.as_view(), name='new_study_request'),
    path('profile/', views.AssistantProfileView.as_view(), name='assistant_profile'),
    path('logout/', views.assistant_logout, name='assistant_logout'),
    path('ticket/<int:study_request_id>/', views.print_ticket, name='print_ticket'),
    path('api/patient-search/', api.patient_search, name='patient_search_api'),
    path('api/create-patient/', api.create_patient, name='create_patient_api'),
    path('api/verify-doctor/', api.verify_doctor, name='verify_doctor_api'),
]
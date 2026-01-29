from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'patientsDashboard'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='patientsDashboard/login.html'), name='login'),
    # Placeholder for signup, will be implemented later or if user requests
    path('signup/', views.signup, name='signup'), 
]
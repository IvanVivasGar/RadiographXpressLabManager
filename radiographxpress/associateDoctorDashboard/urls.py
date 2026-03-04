from django.urls import path
from . import views
from core import views as core_views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='associate_dashboard'),
    path('signup/', views.signup, name='associate_signup'),
    path('studyDetail/<int:id_study>/', core_views.study_detail, name='studyDetail'),
]

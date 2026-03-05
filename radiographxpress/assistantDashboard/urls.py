from django.urls import path
from . import views

urlpatterns = [
    path('ticket/<int:study_request_id>/', views.print_ticket, name='print_ticket'),
]
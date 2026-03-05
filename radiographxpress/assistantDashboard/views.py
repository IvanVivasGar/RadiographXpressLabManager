from django.shortcuts import render, get_object_or_404
from .models import StudyRequest


def print_ticket(request, study_request_id):
    """Render a simple printable ticket with the PDF password."""
    study_request = get_object_or_404(StudyRequest, pk=study_request_id)
    return render(request, 'assistantDashboard/ticket.html', {
        'study_request': study_request,
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Study

def login_success(request):
    """
    Redirects users to their specific dashboard based on their group membership.
    """
    if request.user.groups.filter(name='Doctors').exists():
        return redirect('pendingStudies')
    elif request.user.groups.filter(name='Patients').exists():
        return redirect('patientsDashboard:patientsDashboard') 
    elif request.user.groups.filter(name='Assistants').exists():
        # TODO: Update with real URL name when Assistant app is ready
        return redirect('admin:index')
    
    # Fallback for superusers or unassigned users
    return redirect('home')

def study_detail(request, id_study):
    study = get_object_or_404(Study, id_study=id_study)
    return render(request, 'core/study_report_detail.html', {'study': study})
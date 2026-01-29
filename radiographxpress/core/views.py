from django.shortcuts import redirect

def login_success(request):
    """
    Redirects users to their specific dashboard based on their group membership.
    """
    if request.user.groups.filter(name='Doctors').exists():
        return redirect('pendingStudies')
    elif request.user.groups.filter(name='Patients').exists():
        # TODO: Update with real URL name when Patient app is ready
        return redirect('admin:index') 
    elif request.user.groups.filter(name='Assistants').exists():
        # TODO: Update with real URL name when Assistant app is ready
        return redirect('admin:index')
    
    # Fallback for superusers or unassigned users
    return redirect('home')
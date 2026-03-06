from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from patientsDashboard.models import Patient


@login_required
def patient_search(request):
    """
    JSON endpoint for live patient search.
    Searches by first name, last name, email, or phone.
    Returns max 10 results.
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    patients = Patient.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(user__email__icontains=query) |
        Q(phone__icontains=query)
    ).select_related('user')[:10]
    
    results = [
        {
            'id': p.pk,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'email': p.email,
            'phone': p.phone,
        }
        for p in patients
    ]
    
    return JsonResponse(results, safe=False)

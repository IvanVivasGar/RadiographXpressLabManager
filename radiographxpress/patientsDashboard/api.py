from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from associateDoctorDashboard.models import AssociateDoctor


def patient_required(view_func):
    """Decorator that ensures the user is in the 'Patients' group."""
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='Patients').exists():
            return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


@login_required
@patient_required
def doctor_search(request):
    """
    JSON endpoint for live associate doctor search.
    Searches by first name, last name.
    Returns max 10 results.
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)

    patient = request.user.patient_profile
    # Exclude doctors already granted access
    granted_ids = patient.associated_doctors.values_list('pk', flat=True)

    doctors = AssociateDoctor.objects.filter(
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query)
    ).exclude(pk__in=granted_ids).select_related('user')[:10]

    results = [
        {
            'id': d.pk,
            'name': str(d),
            'university': d.university or '',
            'professional_id': d.professional_id or '',
            'phone': d.phone or '',
            'email': d.user.email or '',
        }
        for d in doctors
    ]

    return JsonResponse(results, safe=False)


@login_required
@patient_required
@require_POST
def toggle_doctor(request):
    """
    Grant or revoke access for an associate doctor.
    Expects POST with: doctor_id, action ('grant' or 'revoke')
    """
    doctor_id = request.POST.get('doctor_id')
    action = request.POST.get('action')

    if not doctor_id or action not in ('grant', 'revoke'):
        return JsonResponse({'success': False, 'error': 'Parámetros inválidos.'}, status=400)

    try:
        doctor = AssociateDoctor.objects.get(pk=doctor_id)
    except (AssociateDoctor.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Doctor no encontrado.'}, status=404)

    patient = request.user.patient_profile

    if action == 'grant':
        patient.associated_doctors.add(doctor)
    else:
        patient.associated_doctors.remove(doctor)

    return JsonResponse({'success': True, 'action': action, 'doctor_id': doctor.pk})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from patientsDashboard.models import Patient


def assistant_required(view_func):
    """Decorator that ensures the user is in the 'Assistants' group."""
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='Assistants').exists():
            return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


@login_required
@assistant_required
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


@login_required
@assistant_required
@require_POST
def create_patient(request):
    """
    Create a new patient account from the assistant dashboard.
    User is created as inactive with a random password.
    Verification email is sent so patient can activate and set password.
    """
    import secrets
    import string
    from django.contrib.auth.models import User, Group

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    gender = request.POST.get('gender', 'O').strip()
    address = request.POST.get('address', '').strip()

    # Validation
    errors = []
    if not first_name:
        errors.append('El nombre es requerido.')
    if not last_name:
        errors.append('El apellido es requerido.')
    if not email:
        errors.append('El correo es requerido.')
    if not phone:
        errors.append('El teléfono es requerido.')
    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    # Check for duplicate email
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'success': False,
            'errors': ['Ya existe un usuario con este correo electrónico.']
        }, status=400)

    # Generate random password (patient will set their own after verification)
    random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

    # Create user
    user = User.objects.create_user(
        username=email,
        email=email,
        password=random_password,
        first_name=first_name,
        last_name=last_name,
    )
    user.is_active = False
    user.save()

    # Add to Patients group
    group, _ = Group.objects.get_or_create(name='Patients')
    user.groups.add(group)

    # Create patient profile
    patient = Patient.objects.create(
        user=user,
        address=address,
        phone=phone,
        gender=gender,
    )

    # Send verification email
    from core.email_service import send_verification_email
    try:
        send_verification_email(user, request)
    except Exception:
        pass  # Don't fail the creation if email fails

    return JsonResponse({
        'success': True,
        'patient': {
            'id': patient.pk,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
        }
    })


@login_required
@assistant_required
@require_POST
def verify_doctor(request):
    """
    Approve or deny an associate doctor account.
    If approved, activates account and sends welcome email.
    If denied, deletes account and sends rejection email.
    """
    from associateDoctorDashboard.models import AssociateDoctor
    from core.notifications import notify_doctor_approved, notify_doctor_denied
    from core.email_service import send_doctor_approved_email, send_doctor_denied_email

    doctor_id = request.POST.get('doctor_id')
    action = request.POST.get('action')

    if action not in ['approve', 'deny']:
        return JsonResponse({'success': False, 'error': 'Acción inválida.'}, status=400)

    try:
        doctor = AssociateDoctor.objects.get(pk=doctor_id)
        user = doctor.user
    except (AssociateDoctor.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Doctor no encontrado.'}, status=404)

    if action == 'approve':
        doctor.is_verified = True
        doctor.save()

        user.is_active = True
        user.save()

        # Send WS notification and email
        notify_doctor_approved(doctor)
        try:
            send_doctor_approved_email(user)
        except Exception as e:
            # We don't want a failed email to break the approval flow
            pass

        return JsonResponse({'success': True, 'message': 'Doctor aprobado exitosamente.'})

    elif action == 'deny':
        # Store data for email/WS before deleting
        doctor_pk = doctor.pk
        doctor_email = user.email
        doctor_name = f"{user.first_name} {user.last_name}"

        # Delete associate doctor profile and the underlying user
        doctor.delete()
        user.delete()

        # Send WS notification and email
        notify_doctor_denied(doctor_pk)
        try:
            send_doctor_denied_email(doctor_email, doctor_name)
        except Exception as e:
            pass

        return JsonResponse({'success': True, 'message': 'Doctor rechazado y eliminado exitosamente.'})

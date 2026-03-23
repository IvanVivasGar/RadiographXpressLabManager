"""
API Endpoints for the Assistant Dashboard.
Provides AJAX endpoints for dynamically interacting with patient and doctor records
without reloading the page (e.g., patient search, doctor approval, patient creation).
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from patientsDashboard.models import Patient


def assistant_required(view_func):
    """
    Security Decorator that ensures the incoming request belongs to an authenticated
    user within the 'Assistants' Django Group.
    
    Returns a 403 Forbidden JSON response if the user lacks the proper role,
    protecting critical administrative endpoints from Patients or Doctors.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='Assistants').exists():
            return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)
        return view_func(request, *args, **kwargs)
        
    # Preserve original function metadata for Django URL resolution
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


@login_required
@assistant_required
def patient_search(request):
    """
    GET JSON endpoint for live patient search in UI dropdowns.
    
    Searches the database across multiple fields (first name, last name, email, phone)
    using case-insensitive matching (`icontains`).
    
    Args:
        request: HTTP GET request containing a 'q' query parameter.
        
    Returns:
        JsonResponse: A list of up to 10 serialized patient dictionaries.
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # Use Django Q objects for complex OR querying
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
    POST API to rapidly create a new Patient account from the front-desk UI.
    
    Workflow:
    1. Validates form data (name, email, phone, etc.).
    2. Ensures the email is unique across the entire user base.
    3. Provisions a new `auth.User` and links it to a new `Patient` profile.
    4. By default, the account is marked `is_active=False` and given a secure 
       randomized password.
    5. Dispatches an email verification link so the patient can self-activate 
       their account and set their permanent password.
       
    Returns:
        JsonResponse: Success flag along with the new patient's serialized data,
        or a list of validation errors.
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

    # Data Validation
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

    # Check for duplicate email across the system
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'success': False,
            'errors': ['Ya existe un usuario con este correo electrónico.']
        }, status=400)

    # Generate an unguessable placeholder password
    random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

    # Provision base user identity
    user = User.objects.create_user(
        username=email,
        email=email,
        password=random_password,
        first_name=first_name,
        last_name=last_name,
    )
    user.is_active = False # Account locked until email verification
    user.save()

    # Assign Django security role
    group, _ = Group.objects.get_or_create(name='Patients')
    user.groups.add(group)

    # Provision Patient profile data
    patient = Patient.objects.create(
        user=user,
        address=address,
        phone=phone,
        gender=gender,
    )

    # Dispatch welcome & verification email
    from core.email_service import send_verification_email
    try:
        send_verification_email(user, request)
    except Exception:
        pass  # We catch email failures silently to not halt the UI response

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
    POST API to approve or deny an Associate Doctor's registration application.
    
    When an external physician registers, their account is inactive until front-desk 
    staff formally verify their medical license credentials.
    
    Workflow if Approved:
      - Activates the `AssociateDoctor` boolean flag and the underlying Django User.
      - Dispatches a WebSocket notification to UI grids.
      - Sends an approval confirmation email to the doctor.
      
    Workflow if Denied:
      - Caches the doctor's details in RAM.
      - Hard deletes the `AssociateDoctor` profile and underlying `User` from the DB.
      - Sends a rejection explanation email to the doctor.
      
    Returns:
        JsonResponse: Success flag and message. Handles 400 for bad actions 
        and 404 for invalid doctor IDs.
    """
    from associateDoctorDashboard.models import AssociateDoctor
    from core.notifications import notify_doctor_approved, notify_doctor_denied
    from core.email_service import send_doctor_approved_email, send_doctor_denied_email

    doctor_id = request.POST.get('doctor_id')
    action = request.POST.get('action')

    # Validate action intent
    if action not in ['approve', 'deny']:
        return JsonResponse({'success': False, 'error': 'Acción inválida.'}, status=400)

    # Fetch targeted entity safely
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

        # Alert the ecosystem asynchronously
        notify_doctor_approved(doctor)
        try:
            send_doctor_approved_email(user)
        except Exception as e:
            pass # Fail gracefully 

        return JsonResponse({'success': True, 'message': 'Doctor aprobado exitosamente.'})

    elif action == 'deny':
        # Store necessary data in memory before deletion to fuel the notification engines
        doctor_pk = doctor.pk
        doctor_email = user.email
        doctor_name = f"{user.first_name} {user.last_name}"

        # Hard destruction of credentials
        doctor.delete()
        user.delete()

        # Alert the ecosystem asynchronously
        notify_doctor_denied(doctor_pk)
        try:
            send_doctor_denied_email(doctor_email, doctor_name)
        except Exception as e:
            pass

        return JsonResponse({'success': True, 'message': 'Doctor rechazado y eliminado exitosamente.'})

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Study, Report
from .email_service import _verify_token, send_welcome_email
import os
import base64
from django.conf import settings
# WeasyPrint is lazy-imported in generate_report_pdf to avoid loading at startup


def verify_email(request, token):
    """
    Verifies a user's email using a signed token.
    Activates the account, marks email as verified, sends welcome email.
    """
    user_pk = _verify_token(token)
    if user_pk is None:
        return render(request, 'core/emails/verification_failed.html')
    
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return render(request, 'core/emails/verification_failed.html')
    
    # Activate the user (unless associate doctor — needs assistant approval)
    if hasattr(user, 'associate_doctor_profile'):
        # Mark email verified but keep account inactive until assistant approves
        user.associate_doctor_profile.is_email_verified = True
        user.associate_doctor_profile.save()
        
        # Notify assistants that a new doctor is pending approval
        from core.notifications import notify_doctor_pending_approval
        notify_doctor_pending_approval(user.associate_doctor_profile)
        
        messages.success(request, 'Tu correo ha sido verificado. Tu cuenta está pendiente de aprobación por el laboratorio.')
        return render(request, 'core/emails/verification_pending_approval.html')
    
    # For all other roles (patients, etc.) — activate immediately
    user.is_active = True
    user.save()
    
    # Mark email as verified on the profile
    if hasattr(user, 'patient_profile'):
        user.patient_profile.is_email_verified = True
        user.patient_profile.save()
    
    # Send welcome email
    send_welcome_email(user)
    
    messages.success(request, '¡Tu correo ha sido verificado exitosamente! Ya puedes iniciar sesión.')
    return redirect('login')
def login_success(request):
    """
    Redirects users to their specific dashboard based on their group membership.
    """
    if request.user.groups.filter(name='Doctors').exists():
        return redirect('pendingStudies')
    elif request.user.groups.filter(name='Patients').exists():
        return redirect('patientsDashboard:patientsDashboard') 
    elif request.user.groups.filter(name='AssociatedDoctors').exists():
        return redirect('associate_dashboard')
    elif request.user.groups.filter(name='Assistants').exists():
        return redirect('assistant_dashboard')
    
    # Fallback for superusers or unassigned users
    return redirect('home')

def study_detail(request, id_study):
    study = get_object_or_404(Study, id_study=id_study)
    hide_download_btn = request.user.is_authenticated and request.user.groups.filter(name__in=['AssociatedDoctors', 'Doctors']).exists()
    return render(request, 'core/study_report_detail.html', {'study': study, 'hide_download_btn': hide_download_btn})

def logout(request):
    logout(request)
    return redirect('login')


@login_required
def generate_report_pdf(request, report_id):
    """
    Generate a PDF for a completed report.
    Only allows download if the user owns the report and it's completed.
    """
    report = get_object_or_404(Report, id_report=report_id)
    
    # Get the study to find the patient
    study = Study.objects.filter(id_report=report).first()
    if not study:
        return HttpResponse("No study associated with this report.", status=404)
    
    patient = study.id_patient
    
    # Explicitly block doctors and associate doctors from downloading PDFs to protect patient data
    if request.user.groups.filter(name__in=['AssociatedDoctors', 'Doctors']).exists():
        return HttpResponse("Unauthorized", status=403)
        
    # Security: Verify the requesting user owns the report
    if hasattr(request.user, 'patient_profile'):
        if request.user.patient_profile != patient:
            return HttpResponse("Unauthorized", status=403)
    elif not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    # Only allow download for completed reports
    if report.status != Report.COMPLETED:
        return HttpResponse("Report is not yet completed.", status=400)
    
    # Generate unprotected PDF for platform download
    pdf = generate_pdf_bytes(report, study)
    
    # Return PDF response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{report.id_report}.pdf"'
    return response


def generate_pdf_bytes(report, study):
    """
    Generate PDF bytes for a report. Reusable by both the download view
    and the email service.
    """
    patient = study.id_patient
    doctor = report.doctor_in_charge
    
    # Load CSS
    css_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'css', 'report_pdf.css')
    with open(css_path, 'r') as f:
        css_content = f.read()
    
    # Load background image
    bg_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'assets', 'img', 'background', 'report_background.png')
    with open(bg_path, "rb") as image_file:
        bg_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    bg_data_uri = f"data:image/png;base64,{bg_base64}"
    
    style_tag = f'<style>{css_content}</style>'
    
    # Load logo image
    logo_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'assets', 'img', 'logos', 'radiographxpress_logo.png')
    with open(logo_path, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    logo_data_uri = f"data:image/png;base64,{logo_base64}"
    
    # Fetch Associate Doctor
    associate_doctor = None
    if study and study.id_study_request and study.id_study_request.id_associate_doctor:
        associate_doctor = study.id_study_request.id_associate_doctor

    # Render HTML template
    html_string = render_to_string('core/pdf/report_template.html', {
        'report': report,
        'patient': patient,
        'doctor': doctor,
        'associate_doctor': associate_doctor,
        'style_tag': style_tag,
        'bg_data_uri': bg_data_uri,
        'logo_data_uri': logo_data_uri,
    })
    
    # Lazy import WeasyPrint
    from weasyprint import HTML
    
    # Generate PDF
    html = HTML(string=html_string)
    return html.write_pdf()
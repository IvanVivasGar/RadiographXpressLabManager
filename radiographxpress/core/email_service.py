from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


signer = TimestampSigner()


def _make_verification_token(user):
    """Create a signed token containing the user's pk."""
    return signer.sign(str(user.pk))


def _verify_token(token, max_age=86400):
    """
    Validate a signed token and return the user pk.
    Default max_age is 24 hours (86400 seconds).
    """
    try:
        value = signer.unsign(token, max_age=max_age)
        return int(value)
    except (BadSignature, SignatureExpired):
        return None


def send_verification_email(user, request):
    """Send an email verification link to the user."""
    token = _make_verification_token(user)
    
    # Build absolute verification URL
    verify_url = request.build_absolute_uri(f'/core/verify-email/{token}/')
    
    subject = 'Verifica tu correo — Radiograph Xpress'
    html_message = render_to_string('core/emails/verification_email.html', {
        'user': user,
        'verify_url': verify_url,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(user):
    """Send a branded welcome email after verification."""
    subject = '¡Bienvenido a Radiograph Xpress!'
    html_message = render_to_string('core/emails/welcome_email.html', {
        'user': user,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_study_completed_email(study):
    """Notify the patient that their study report is ready, with encrypted PDF attached."""
    from django.core.mail import EmailMessage
    import pikepdf
    import io
    from .views import generate_pdf_bytes
    
    patient = study.id_patient
    if not patient.user or not patient.user.email:
        return
    
    report = study.id_report
    if not report:
        return
    
    subject = 'Tu estudio está listo — Radiograph Xpress'
    html_message = render_to_string('core/emails/study_completed_email.html', {
        'patient': patient,
        'study': study,
        'report': report,
    })
    plain_message = strip_tags(html_message)
    
    # Build the email
    email = EmailMessage(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [patient.user.email],
    )
    email.content_subtype = 'html'
    email.body = html_message
    
    # Generate and encrypt the PDF
    try:
        pdf_bytes = generate_pdf_bytes(report, study)
        
        # Encrypt PDF with pikepdf using the StudyRequest password
        password = study.id_study_request.pdf_password
        input_pdf = io.BytesIO(pdf_bytes)
        output_pdf = io.BytesIO()
        
        with pikepdf.open(input_pdf) as pdf:
            pdf.save(
                output_pdf,
                encryption=pikepdf.Encryption(
                    owner=password,
                    user=password,
                    aes=True,
                    R=6,  # AES-256
                )
            )
        
        output_pdf.seek(0)
        email.attach(
            f'reporte_{report.id_report}.pdf',
            output_pdf.read(),
            'application/pdf'
        )
    except Exception as e:
        print(f"Error generating/encrypting PDF for email: {e}")
        # Still send the email without attachment
    
    email.send(fail_silently=False)

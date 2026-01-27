from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ReportingDoctor

@receiver(post_save, sender=ReportingDoctor)
def create_or_update_user_for_doctor(sender, instance, created, **kwargs):
    """
    When a ReportingDoctor is created or updated (e.g. via Admin),
    ensure a corresponding Django User exists so they can log in.
    """
    email = instance.email
    password = instance.password  # In a real app complexity, manage hashing carefully.
    
    if created:
        # Create a new User
        if not User.objects.filter(email=email).exists():
            User.objects.create_user(username=email, email=email, password=password)
    else:
        # Update existing user if needed (e.g. password change)
        try:
            user = User.objects.get(email=email)
            # If plain text pass stored in ReportingDoctor matches user check, good.
            # If changed, we might want to update.
            # For simplicity in this prototype, we'll reset the password if it doesn't match hash
            if not user.check_password(password):
                user.set_password(password)
                user.save()
        except User.DoesNotExist:
            # If email changed or user deleted, recreate
            User.objects.create_user(username=email, email=email, password=password)

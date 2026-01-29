from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    Recognizes the user by email instead of username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"DEBUG: EmailBackend.authenticate check. Username: {username}")
        UserModel = get_user_model()
        try:
            # We look for the user by email (case insensitive)
            # Note: We use 'username' argument because Django's LoginView sends the form field 'username' to this method
            user = UserModel.objects.filter(email__iexact=username).first()
            if user:
                print(f"DEBUG: Found user by email: {user.username}")
            else:
                print("DEBUG: User not found by email.")
        except UserModel.DoesNotExist:
            print("DEBUG: User not found (DoesNotExist exception).")
            return None
        
        # If user found and password matches
        if user and user.check_password(password) and self.user_can_authenticate(user):
            print("DEBUG: Password matched. Authentication successful.")
            return user
        if user:
            print(f"DEBUG: Authentication failed. Check pass: {user.check_password(password)}, Can auth: {self.user_can_authenticate(user)}")
        return None

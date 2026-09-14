from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class CaseInsensitiveEmailOrUsernameBackend(ModelBackend):
    """
    Authenticate using case-insensitive username or email,
    and tolerate leading/trailing whitespaces.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        clean_username = str(username).strip()
        clean_password = str(password).strip()

        # Find user by case-insensitive username or email
        user = User.objects.filter(
            Q(username__iexact=clean_username) | Q(email__iexact=clean_username)
        ).first()

        if user:
            # Check with stripped password or original password
            if user.check_password(clean_password) or user.check_password(password):
                return user
        return None

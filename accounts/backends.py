"""
Custom authentication backend for MongoEngine User model.
Replaces Django's default ORM-based backend.
"""
from core.models import User


class MongoEngineBackend:
    """
    Authenticate against the MongoEngine User document.
    Used in settings.AUTHENTICATION_BACKENDS.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """Return User if credentials are valid, else None."""
        if not email or not password:
            return None
        try:
            user = User.objects.get(email=email.lower().strip())
        except User.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active and not user.is_blocked:
            return user
        return None

    def get_user(self, user_id):
        """Return User by string ID (stored in session)."""
        try:
            return User.objects.get(id=user_id)
        except (User.DoesNotExist, Exception):
            return None

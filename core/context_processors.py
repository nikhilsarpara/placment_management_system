"""
Template context processors that inject session user and notification count
into every template context automatically.
"""
from core.models import User, Notification, UniversityProfile, CompanyProfile, StudentProfile


def user_context(request):
    """Inject `current_user`, `user_role`, and `unread_count` into all templates."""
    context = {
        'current_user': None,
        'user_role': None,
        'unread_count': 0,
        'user_profile': None,
    }
    user_id = request.session.get('user_id')
    if not user_id:
        return context

    try:
        user = User.objects.get(id=user_id)
        context['current_user'] = user
        context['user_role'] = user.role

        # Unread notification count
        context['unread_count'] = Notification.objects(user=user, is_read=False).count()

        # Role-specific profile for navbar display
        if user.role == 'UNIVERSITY':
            context['user_profile'] = UniversityProfile.objects(user=user).first()
        elif user.role == 'COMPANY':
            context['user_profile'] = CompanyProfile.objects(user=user).first()
        elif user.role == 'STUDENT':
            context['user_profile'] = StudentProfile.objects(user=user).first()

    except Exception:
        pass

    return context

"""
Role-based access control decorators and mixins.
All views that need authentication should use these.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from core.models import User, Roles


def get_current_user(request):
    """Return the current User object from session, or None."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id)
    except Exception:
        return None


def login_required(view_func):
    """Redirect to login if not authenticated."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Please log in to continue.')
            return redirect(f'/accounts/login/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """Restrict access to specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get('user_id'):
                messages.warning(request, 'Please log in to continue.')
                return redirect(f'/accounts/login/?next={request.path}')
            user_role = request.session.get('user_role')
            if user_role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('/')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    return role_required(Roles.ADMIN)(view_func)


def university_required(view_func):
    return role_required(Roles.UNIVERSITY)(view_func)


def company_required(view_func):
    return role_required(Roles.COMPANY)(view_func)


def student_required(view_func):
    return role_required(Roles.STUDENT)(view_func)

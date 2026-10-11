"""
Accounts app views: login, logout, register (all roles),
password reset flow (email token via console backend).
"""
import uuid
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.views.decorators.http import require_http_methods

from core.models import (
    User, UniversityProfile, CompanyProfile, StudentProfile,
    Roles, ApprovalStatus
)
from accounts.utils import save_uploaded_file, log_activity


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def _get_redirect_url_for_role(role):
    redirects = {
        Roles.ADMIN: '/admin-panel/dashboard/',
        Roles.UNIVERSITY: '/university/dashboard/',
        Roles.COMPANY: '/company/dashboard/',
        Roles.STUDENT: '/student/dashboard/',
    }
    return redirects.get(role, '/')


# ─────────────────────────────────────────────────────────────
#  LOGIN / LOGOUT
# ─────────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def login_view(request):
    """Unified login for all roles."""
    if request.session.get('user_id'):
        role = request.session.get('user_role')
        return redirect(_get_redirect_url_for_role(role))

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        user = authenticate(request, email=email, password=password)
        if user:
            # Store in session manually (MongoEngine user, not ORM)
            request.session['user_id'] = str(user.id)
            request.session['user_email'] = user.email
            request.session['user_role'] = user.role
            log_activity(user, 'LOGIN', f'User logged in from {request.META.get("REMOTE_ADDR")}',
                         request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Welcome back!')
            next_url = request.GET.get('next', _get_redirect_url_for_role(user.role))
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Clear session and redirect to login."""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            log_activity(user, 'LOGOUT', 'User logged out', request.META.get('REMOTE_ADDR'))
        except Exception:
            pass
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# ─────────────────────────────────────────────────────────────
#  REGISTRATION - UNIVERSITY
# ─────────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def register_university(request):
    """University registration – creates User + UniversityProfile (status=PENDING)."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        name = request.POST.get('name', '').strip()

        # Validation
        errors = []
        if not email or not password or not name:
            errors.append('Email, password, and university name are required.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if User.objects(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/register_university.html', {'post': request.POST})

        # Create user
        user = User(email=email, role=Roles.UNIVERSITY)
        user.set_password(password)
        user.save()

        # Handle file uploads
        logo_path = save_uploaded_file(request.FILES.get('logo'), 'logos/universities/')
        doc_path = save_uploaded_file(request.FILES.get('verification_doc'), 'docs/universities/')

        # Create university profile
        profile = UniversityProfile(
            user=user,
            name=name,
            affiliation=request.POST.get('affiliation', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            website=request.POST.get('website', '') or None,
            placement_officer=request.POST.get('placement_officer', ''),
            contact_phone=request.POST.get('contact_phone', ''),
            contact_email=request.POST.get('contact_email', email),
            logo_path=logo_path,
            verification_doc_path=doc_path,
            status=ApprovalStatus.PENDING,
        )
        profile.save()
        log_activity(user, 'REGISTER', f'University registered: {name}',
                     request.META.get('REMOTE_ADDR'))
        messages.success(request,
            'Registration submitted! Your account will be activated after admin approval.')
        return redirect('accounts:login')

    return render(request, 'accounts/register_university.html')


# ─────────────────────────────────────────────────────────────
#  REGISTRATION - COMPANY
# ─────────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def register_company(request):
    """Company registration – creates User + CompanyProfile (status=PENDING)."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        company_name = request.POST.get('company_name', '').strip()

        errors = []
        if not email or not password or not company_name:
            errors.append('Email, password, and company name are required.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if User.objects(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/register_company.html', {'post': request.POST})

        user = User(email=email, role=Roles.COMPANY)
        user.set_password(password)
        user.save()

        logo_path = save_uploaded_file(request.FILES.get('logo'), 'logos/companies/')
        doc_path = save_uploaded_file(request.FILES.get('verification_doc'), 'docs/companies/')

        profile = CompanyProfile(
            user=user,
            company_name=company_name,
            industry=request.POST.get('industry', ''),
            size=request.POST.get('size', ''),
            website=request.POST.get('website', '') or None,
            hr_name=request.POST.get('hr_name', ''),
            hr_email=request.POST.get('hr_email', email),
            hr_phone=request.POST.get('hr_phone', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            logo_path=logo_path,
            verification_doc_path=doc_path,
            description=request.POST.get('description', ''),
            status=ApprovalStatus.PENDING,
        )
        profile.save()
        log_activity(user, 'REGISTER', f'Company registered: {company_name}',
                     request.META.get('REMOTE_ADDR'))
        messages.success(request,
            'Registration submitted! Your account will be activated after admin approval.')
        return redirect('accounts:login')

    return render(request, 'accounts/register_company.html')


# ─────────────────────────────────────────────────────────────
#  REGISTRATION - STUDENT
# ─────────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def register_student(request):
    """Student registration – linked to a university."""
    universities = UniversityProfile.objects(status=ApprovalStatus.APPROVED)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        university_id = request.POST.get('university_id', '')

        errors = []
        if not email or not password or not first_name or not last_name:
            errors.append('All required fields must be filled.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if User.objects(email=email).first():
            errors.append('An account with this email already exists.')

        university = None
        if university_id:
            try:
                university = UniversityProfile.objects.get(id=university_id)
            except Exception:
                errors.append('Selected university not found.')
        else:
            errors.append('Please select your university.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/register_student.html',
                          {'universities': universities, 'post': request.POST})

        user = User(email=email, role=Roles.STUDENT)
        user.set_password(password)
        user.save()

        profile = StudentProfile(
            user=user,
            university=university,
            first_name=first_name,
            last_name=last_name,
            phone=request.POST.get('phone', ''),
            roll_number=request.POST.get('roll_number', ''),
        )
        profile.save()
        log_activity(user, 'REGISTER', f'Student registered: {first_name} {last_name}',
                     request.META.get('REMOTE_ADDR'))
        messages.success(request,
            'Account created! You can now log in. Complete your profile to apply for jobs.')
        return redirect('accounts:login')

    return render(request, 'accounts/register_student.html', {'universities': universities})


# ─────────────────────────────────────────────────────────────
#  PASSWORD RESET (simplified - console email)
# ─────────────────────────────────────────────────────────────
# In-memory token store (use Redis/DB in production)
_reset_tokens = {}


def password_reset_request(request):
    """Ask for email and send reset link (printed to console)."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects(email=email).first()
        if user:
            token = str(uuid.uuid4())
            _reset_tokens[token] = {
                'user_id': str(user.id),
                'expires': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            reset_url = request.build_absolute_uri(f'/accounts/password-reset/confirm/{token}/')
            # Console email backend will print this
            from django.core.mail import send_mail
            send_mail(
                subject='Password Reset – Placement Management',
                message=f'Click the link to reset your password:\n\n{reset_url}\n\n'
                        f'This link expires in 1 hour.',
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )
        # Always show success to prevent email enumeration
        messages.success(request,
            'If that email exists, a reset link has been sent. Check your console logs in dev.')
        return redirect('accounts:login')
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm(request, token):
    """Confirm reset with new password."""
    token_data = _reset_tokens.get(token)
    if not token_data or token_data['expires'] < datetime.datetime.utcnow():
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('accounts:password_reset')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/password_reset_confirm.html', {'token': token})
        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/password_reset_confirm.html', {'token': token})
        try:
            user = User.objects.get(id=token_data['user_id'])
            user.set_password(password)
            user.save()
            del _reset_tokens[token]
            messages.success(request, 'Password reset successfully. Please log in.')
            return redirect('accounts:login')
        except Exception:
            messages.error(request, 'An error occurred. Please try again.')

    return render(request, 'accounts/password_reset_confirm.html', {'token': token})

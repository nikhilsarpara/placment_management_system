"""Core app views: landing page, 404, 500 error pages."""
from django.shortcuts import render
from core.models import (
    User, UniversityProfile, CompanyProfile, StudentProfile,
    Job, Application, PlacementDrive, JobStatus, ApprovalStatus
)


def landing_page(request):
    """Public landing page with stats and role-based register buttons."""
    # Redirect logged-in users to their dashboard
    user_role = request.session.get('user_role')
    if user_role:
        redirects = {
            'ADMIN': '/admin-panel/dashboard/',
            'UNIVERSITY': '/university/dashboard/',
            'COMPANY': '/company/dashboard/',
            'STUDENT': '/student/dashboard/',
        }
        from django.shortcuts import redirect
        return redirect(redirects.get(user_role, '/'))

    # Platform stats for landing page
    stats = {
        'students': StudentProfile.objects.count(),
        'companies': CompanyProfile.objects(status=ApprovalStatus.APPROVED).count(),
        'universities': UniversityProfile.objects(status=ApprovalStatus.APPROVED).count(),
        'placements': Application.objects(status='SELECTED').count(),
    }
    return render(request, 'core/landing.html', {'stats': stats})


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)

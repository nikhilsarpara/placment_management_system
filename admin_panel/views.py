"""Admin panel views for managing the platform."""
import csv
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

from accounts.decorators import admin_required, get_current_user
from accounts.utils import log_activity, send_notification
from core.models import (
    User, UniversityProfile, CompanyProfile, StudentProfile,
    Job, Application, PlacementDrive, Notification, Announcement,
    ActivityLog, Roles, ApprovalStatus, ApplicationStatus, JobStatus
)


# ─── Dashboard ───────────────────────────────────────────────
@admin_required
def dashboard(request):
    """Admin dashboard with platform-wide stats and charts."""
    user = get_current_user(request)

    # Aggregate stats
    total_students = StudentProfile.objects.count()
    total_companies = CompanyProfile.objects.count()
    total_universities = UniversityProfile.objects.count()
    active_jobs = Job.objects(status=JobStatus.OPEN).count()
    total_placements = Application.objects(status=ApplicationStatus.SELECTED).count()
    total_applications = Application.objects.count()
    placement_rate = round((total_placements / total_applications * 100), 1) if total_applications else 0

    pending_universities = UniversityProfile.objects(status=ApprovalStatus.PENDING).count()
    pending_companies = CompanyProfile.objects(status=ApprovalStatus.PENDING).count()

    # Recent activity
    recent_logs = ActivityLog.objects.order_by('-timestamp').limit(10)

    # Chart data: placements per month (last 6 months)
    placements_chart = _get_placements_per_month()
    top_recruiters = _get_top_recruiters()

    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_universities': total_universities,
        'active_jobs': active_jobs,
        'total_placements': total_placements,
        'placement_rate': placement_rate,
        'pending_universities': pending_universities,
        'pending_companies': pending_companies,
        'recent_logs': recent_logs,
        'placements_chart': placements_chart,
        'top_recruiters': top_recruiters,
    }
    return render(request, 'admin_panel/dashboard.html', context)


def _get_placements_per_month():
    """Return list of {month, count} for last 6 months."""
    result = []
    now = datetime.datetime.utcnow()
    for i in range(5, -1, -1):
        d = now - datetime.timedelta(days=i * 30)
        label = d.strftime('%b %Y')
        count = Application.objects(
            status=ApplicationStatus.SELECTED,
            updated_at__gte=d.replace(day=1),
            updated_at__lt=(d.replace(day=1) + datetime.timedelta(days=31)).replace(day=1)
        ).count()
        result.append({'month': label, 'count': count})
    return result


def _get_top_recruiters():
    """Return top 5 companies by number of selections."""
    companies = CompanyProfile.objects(status=ApprovalStatus.APPROVED)
    recruiter_data = []
    for company in companies:
        jobs = Job.objects(company=company)
        count = 0
        for job in jobs:
            count += Application.objects(job=job, status=ApplicationStatus.SELECTED).count()
        recruiter_data.append({'name': company.company_name, 'count': count})
    return sorted(recruiter_data, key=lambda x: x['count'], reverse=True)[:5]


# ─── Manage Universities ──────────────────────────────────────
@admin_required
def university_list(request):
    """View and manage all universities."""
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')
    universities = UniversityProfile.objects.all()
    if status_filter:
        universities = universities.filter(status=status_filter)
    if query:
        universities = universities.filter(name__icontains=query)
    return render(request, 'admin_panel/university_list.html', {
        'universities': universities,
        'status_filter': status_filter,
        'query': query,
        'status_choices': ApprovalStatus.CHOICES,
    })


@admin_required
def approve_university(request, uni_id):
    """Approve a university registration."""
    user = get_current_user(request)
    try:
        uni = UniversityProfile.objects.get(id=uni_id)
        uni.status = ApprovalStatus.APPROVED
        uni.rejection_reason = ''
        uni.save()
        send_notification(uni.user, 'Registration Approved',
                          f'Your university "{uni.name}" has been approved.',
                          link='/university/dashboard/')
        log_activity(user, 'APPROVE_UNIVERSITY', f'Approved: {uni.name}',
                     request.META.get('REMOTE_ADDR'))
        messages.success(request, f'"{uni.name}" has been approved.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:university_list')


@admin_required
def reject_university(request, uni_id):
    """Reject a university with a reason."""
    user = get_current_user(request)
    try:
        uni = UniversityProfile.objects.get(id=uni_id)
        reason = request.POST.get('reason', 'No reason provided.')
        uni.status = ApprovalStatus.REJECTED
        uni.rejection_reason = reason
        uni.save()
        send_notification(uni.user, 'Registration Rejected',
                          f'Your registration has been rejected. Reason: {reason}')
        log_activity(user, 'REJECT_UNIVERSITY', f'Rejected: {uni.name}',
                     request.META.get('REMOTE_ADDR'))
        messages.warning(request, f'"{uni.name}" has been rejected.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:university_list')


@admin_required
def suspend_university(request, uni_id):
    user = get_current_user(request)
    try:
        uni = UniversityProfile.objects.get(id=uni_id)
        uni.status = ApprovalStatus.SUSPENDED
        uni.save()
        send_notification(uni.user, 'Account Suspended',
                          'Your university account has been suspended. Contact admin.')
        log_activity(user, 'SUSPEND_UNIVERSITY', f'Suspended: {uni.name}',
                     request.META.get('REMOTE_ADDR'))
        messages.warning(request, f'"{uni.name}" has been suspended.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:university_list')


# ─── Manage Companies ─────────────────────────────────────────
@admin_required
def company_list(request):
    """View and manage all companies."""
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')
    companies = CompanyProfile.objects.all()
    if status_filter:
        companies = companies.filter(status=status_filter)
    if query:
        companies = companies.filter(company_name__icontains=query)
    return render(request, 'admin_panel/company_list.html', {
        'companies': companies,
        'status_filter': status_filter,
        'query': query,
        'status_choices': ApprovalStatus.CHOICES,
    })


@admin_required
def approve_company(request, company_id):
    user = get_current_user(request)
    try:
        company = CompanyProfile.objects.get(id=company_id)
        company.status = ApprovalStatus.APPROVED
        company.rejection_reason = ''
        company.save()
        send_notification(company.user, 'Registration Approved',
                          f'Your company "{company.company_name}" has been approved.',
                          link='/company/dashboard/')
        log_activity(user, 'APPROVE_COMPANY', f'Approved: {company.company_name}',
                     request.META.get('REMOTE_ADDR'))
        messages.success(request, f'"{company.company_name}" has been approved.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:company_list')


@admin_required
def reject_company(request, company_id):
    user = get_current_user(request)
    try:
        company = CompanyProfile.objects.get(id=company_id)
        reason = request.POST.get('reason', 'No reason provided.')
        company.status = ApprovalStatus.REJECTED
        company.rejection_reason = reason
        company.save()
        send_notification(company.user, 'Registration Rejected',
                          f'Your registration has been rejected. Reason: {reason}')
        log_activity(user, 'REJECT_COMPANY', f'Rejected: {company.company_name}',
                     request.META.get('REMOTE_ADDR'))
        messages.warning(request, f'"{company.company_name}" has been rejected.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:company_list')


@admin_required
def suspend_company(request, company_id):
    user = get_current_user(request)
    try:
        company = CompanyProfile.objects.get(id=company_id)
        company.status = ApprovalStatus.SUSPENDED
        company.save()
        send_notification(company.user, 'Account Suspended',
                          'Your company account has been suspended. Contact admin.')
        log_activity(user, 'SUSPEND_COMPANY', f'Suspended: {company.company_name}',
                     request.META.get('REMOTE_ADDR'))
        messages.warning(request, f'"{company.company_name}" has been suspended.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:company_list')


# ─── Manage Users ─────────────────────────────────────────────
@admin_required
def user_list(request):
    """List all platform users with search and filter."""
    role_filter = request.GET.get('role', '')
    query = request.GET.get('q', '')
    users = User.objects.all()
    if role_filter:
        users = users.filter(role=role_filter)
    if query:
        users = users.filter(email__icontains=query)
    return render(request, 'admin_panel/user_list.html', {
        'users': users,
        'role_filter': role_filter,
        'query': query,
        'role_choices': Roles.CHOICES,
    })


@admin_required
def block_user(request, user_id):
    admin_user = get_current_user(request)
    try:
        target = User.objects.get(id=user_id)
        target.is_blocked = True
        target.save()
        log_activity(admin_user, 'BLOCK_USER', f'Blocked user: {target.email}',
                     request.META.get('REMOTE_ADDR'))
        messages.warning(request, f'User {target.email} has been blocked.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:user_list')


@admin_required
def unblock_user(request, user_id):
    admin_user = get_current_user(request)
    try:
        target = User.objects.get(id=user_id)
        target.is_blocked = False
        target.save()
        log_activity(admin_user, 'UNBLOCK_USER', f'Unblocked user: {target.email}',
                     request.META.get('REMOTE_ADDR'))
        messages.success(request, f'User {target.email} has been unblocked.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:user_list')


@admin_required
def delete_user(request, user_id):
    admin_user = get_current_user(request)
    if request.method == 'POST':
        try:
            target = User.objects.get(id=user_id)
            email = target.email
            target.delete()
            log_activity(admin_user, 'DELETE_USER', f'Deleted user: {email}',
                         request.META.get('REMOTE_ADDR'))
            messages.success(request, f'User {email} has been deleted.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('admin_panel:user_list')


# ─── Jobs Management ──────────────────────────────────────────
@admin_required
def job_list(request):
    """View and moderate all job postings."""
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')
    jobs = Job.objects.all()
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    if query:
        jobs = jobs.filter(title__icontains=query)
    return render(request, 'admin_panel/job_list.html', {
        'jobs': jobs,
        'status_filter': status_filter,
        'query': query,
    })


@admin_required
def close_job(request, job_id):
    user = get_current_user(request)
    try:
        job = Job.objects.get(id=job_id)
        job.status = JobStatus.CLOSED
        job.save()
        log_activity(user, 'CLOSE_JOB', f'Closed job: {job.title}',
                     request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Job "{job.title}" closed.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('admin_panel:job_list')


# ─── Reports ──────────────────────────────────────────────────
@admin_required
def reports(request):
    """Platform-wide report with filters."""
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    university_id = request.GET.get('university_id', '')
    company_id = request.GET.get('company_id', '')

    apps = Application.objects.all()
    if date_from:
        try:
            apps = apps.filter(applied_at__gte=datetime.datetime.strptime(date_from, '%Y-%m-%d'))
        except Exception:
            pass
    if date_to:
        try:
            apps = apps.filter(applied_at__lte=datetime.datetime.strptime(date_to, '%Y-%m-%d'))
        except Exception:
            pass

    universities = UniversityProfile.objects(status=ApprovalStatus.APPROVED)
    companies = CompanyProfile.objects(status=ApprovalStatus.APPROVED)

    context = {
        'applications': apps,
        'universities': universities,
        'companies': companies,
        'total': apps.count(),
        'selected': apps.filter(status=ApplicationStatus.SELECTED).count(),
        'rejected': apps.filter(status=ApplicationStatus.REJECTED).count(),
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'university_id': university_id,
            'company_id': company_id,
        }
    }
    return render(request, 'admin_panel/reports.html', context)


@admin_required
def export_report_csv(request):
    """Export applications as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="placement_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student', 'University', 'Job', 'Company', 'Status', 'Applied At'])
    for app in Application.objects.all():
        try:
            writer.writerow([
                app.student.full_name if app.student else '',
                app.student.university.name if app.student and app.student.university else '',
                app.job.title if app.job else '',
                app.job.company.company_name if app.job and app.job.company else '',
                app.status,
                app.applied_at.strftime('%Y-%m-%d') if app.applied_at else '',
            ])
        except Exception:
            continue
    return response


# ─── Announcements ────────────────────────────────────────────
@admin_required
def announcements(request):
    """Send and view announcements."""
    if request.method == 'POST':
        admin_user = get_current_user(request)
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        target_role = request.POST.get('target_role', '') or None

        if not title or not content:
            messages.error(request, 'Title and content are required.')
        else:
            ann = Announcement(
                sender=admin_user,
                title=title,
                content=content,
                target_role=target_role,
            )
            ann.save()

            # Send notifications to target users
            users = User.objects.all()
            if target_role:
                users = users.filter(role=target_role)
            for u in users:
                send_notification(u, title, content[:200], notif_type='ANNOUNCEMENT')

            log_activity(admin_user, 'SEND_ANNOUNCEMENT', f'Sent: {title}',
                         request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Announcement sent to {users.count()} users.')
            return redirect('admin_panel:announcements')

    all_announcements = Announcement.objects.order_by('-created_at').limit(20)
    return render(request, 'admin_panel/announcements.html', {
        'announcements': all_announcements,
        'role_choices': Roles.CHOICES,
    })


# ─── Activity Logs ────────────────────────────────────────────
@admin_required
def activity_logs(request):
    logs = ActivityLog.objects.order_by('-timestamp').limit(100)
    return render(request, 'admin_panel/activity_logs.html', {'logs': logs})

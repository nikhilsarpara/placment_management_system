"""Company module views."""
import csv
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

from accounts.decorators import company_required, get_current_user
from accounts.utils import log_activity, send_notification
from core.models import (
    User, CompanyProfile, Job, Application, UniversityProfile,
    PlacementDrive, Interview, Offer, StudentProfile,
    ApprovalStatus, JobStatus, JobType, ApplicationStatus,
    InterviewMode, EligibilityCriteria
)


def _get_company(request):
    user = get_current_user(request)
    return user, CompanyProfile.objects(user=user).first()


# ─── Dashboard ───────────────────────────────────────────────
@company_required
def dashboard(request):
    user, company = _get_company(request)
    if not company or company.status != ApprovalStatus.APPROVED:
        messages.warning(request, 'Your account is pending admin approval.')
        return render(request, 'companies/pending.html', {'profile': company})

    jobs = Job.objects(company=company)
    active_jobs = jobs.filter(status=JobStatus.OPEN).count()
    all_apps = []
    for job in jobs:
        all_apps += list(Application.objects(job=job))

    total_apps = len(all_apps)
    shortlisted = sum(1 for a in all_apps if a.status == ApplicationStatus.SHORTLISTED)
    hired = sum(1 for a in all_apps if a.status == ApplicationStatus.SELECTED)

    recent_apps = sorted(all_apps, key=lambda a: a.applied_at, reverse=True)[:5]

    context = {
        'company': company,
        'active_jobs': active_jobs,
        'total_jobs': jobs.count(),
        'total_applications': total_apps,
        'shortlisted': shortlisted,
        'hired': hired,
        'recent_applications': recent_apps,
    }
    return render(request, 'companies/dashboard.html', context)


# ─── Profile ─────────────────────────────────────────────────
@company_required
def profile(request):
    user, company = _get_company(request)
    if request.method == 'POST':
        from accounts.utils import save_uploaded_file
        company.company_name = request.POST.get('company_name', company.company_name)
        company.industry = request.POST.get('industry', company.industry)
        company.size = request.POST.get('size', company.size)
        company.website = request.POST.get('website', company.website) or None
        company.hr_name = request.POST.get('hr_name', company.hr_name)
        company.hr_email = request.POST.get('hr_email', company.hr_email)
        company.hr_phone = request.POST.get('hr_phone', company.hr_phone)
        company.address = request.POST.get('address', company.address)
        company.city = request.POST.get('city', company.city)
        company.description = request.POST.get('description', company.description)
        if request.FILES.get('logo'):
            company.logo_path = save_uploaded_file(request.FILES['logo'], 'logos/companies/')
        company.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('companies:profile')
    return render(request, 'companies/profile.html', {'company': company})


# ─── Job Management ───────────────────────────────────────────
@company_required
def job_list(request):
    user, company = _get_company(request)
    status_filter = request.GET.get('status', '')
    jobs = Job.objects(company=company)
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    return render(request, 'companies/job_list.html', {
        'jobs': jobs, 'company': company,
        'status_filter': status_filter, 'status_choices': JobStatus.CHOICES,
    })


@company_required
def create_job(request):
    user, company = _get_company(request)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        skills_raw = request.POST.get('skills', '')
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]

        if not title or not description:
            messages.error(request, 'Title and description are required.')
            return render(request, 'companies/create_job.html', {'company': company})

        deadline_str = request.POST.get('deadline', '')
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            except Exception:
                pass

        eligibility = EligibilityCriteria(
            min_cgpa=float(request.POST.get('min_cgpa', 0) or 0),
            max_backlogs=int(request.POST.get('max_backlogs', 0) or 0),
        )
        batch_years_raw = request.POST.get('batch_years', '')
        if batch_years_raw:
            try:
                eligibility.batch_years = [int(y.strip()) for y in batch_years_raw.split(',') if y.strip()]
            except Exception:
                pass

        job = Job(
            company=company,
            title=title,
            description=description,
            skills_required=skills,
            ctc=request.POST.get('ctc', ''),
            location=request.POST.get('location', ''),
            job_type=request.POST.get('job_type', JobType.FULL_TIME),
            eligibility=eligibility,
            application_deadline=deadline,
            openings=int(request.POST.get('openings', 1) or 1),
        )
        job.save()
        log_activity(user, 'CREATE_JOB', f'Posted job: {title}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'Job "{title}" posted successfully.')
        return redirect('companies:jobs')

    return render(request, 'companies/create_job.html', {
        'company': company, 'job_types': JobType.CHOICES
    })


@company_required
def edit_job(request, job_id):
    user, company = _get_company(request)
    try:
        job = Job.objects.get(id=job_id, company=company)
    except Exception:
        messages.error(request, 'Job not found.')
        return redirect('companies:jobs')

    if request.method == 'POST':
        job.title = request.POST.get('title', job.title)
        job.description = request.POST.get('description', job.description)
        skills_raw = request.POST.get('skills', '')
        job.skills_required = [s.strip() for s in skills_raw.split(',') if s.strip()]
        job.ctc = request.POST.get('ctc', job.ctc)
        job.location = request.POST.get('location', job.location)
        job.job_type = request.POST.get('job_type', job.job_type)
        job.openings = int(request.POST.get('openings', job.openings) or job.openings)
        job.status = request.POST.get('status', job.status)
        job.save()
        messages.success(request, 'Job updated successfully.')
        return redirect('companies:jobs')

    return render(request, 'companies/edit_job.html', {
        'job': job, 'company': company, 'job_types': JobType.CHOICES,
        'job_statuses': JobStatus.CHOICES,
    })


@company_required
def close_job(request, job_id):
    user, company = _get_company(request)
    try:
        job = Job.objects.get(id=job_id, company=company)
        job.status = JobStatus.CLOSED
        job.save()
        messages.success(request, f'Job "{job.title}" closed.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('companies:jobs')


# ─── Applicant Management ─────────────────────────────────────
@company_required
def applicant_list(request, job_id=None):
    user, company = _get_company(request)
    jobs = Job.objects(company=company)
    selected_job = None
    apps = []

    if job_id:
        try:
            selected_job = Job.objects.get(id=job_id, company=company)
            apps = list(Application.objects(job=selected_job))
        except Exception:
            pass
    else:
        for job in jobs:
            apps += list(Application.objects(job=job))

    # Filters
    status_filter = request.GET.get('status', '')
    cgpa_min = request.GET.get('cgpa_min', '')
    if status_filter:
        apps = [a for a in apps if a.status == status_filter]
    if cgpa_min:
        try:
            cgpa_min_val = float(cgpa_min)
            apps = [a for a in apps if a.student and a.student.cgpa >= cgpa_min_val]
        except Exception:
            pass

    return render(request, 'companies/applicant_list.html', {
        'applications': apps,
        'jobs': jobs,
        'selected_job': selected_job,
        'status_filter': status_filter,
        'cgpa_min': cgpa_min,
        'status_choices': ApplicationStatus.CHOICES,
        'company': company,
    })


@company_required
def update_application_status(request, app_id):
    """Update a single application status (shortlist, reject, select, etc.)."""
    user, company = _get_company(request)
    if request.method == 'POST':
        try:
            app = Application.objects.get(id=app_id)
            # Verify this app belongs to the company
            if app.job.company.id != company.id:
                messages.error(request, 'Not authorized.')
                return redirect('companies:applicants')

            new_status = request.POST.get('status', '')
            note = request.POST.get('note', '')
            if new_status not in ApplicationStatus.CHOICES:
                messages.error(request, 'Invalid status.')
                return redirect('companies:applicants')

            app.update_status(new_status, note)
            app.save()

            # Notify student
            status_msg = {
                ApplicationStatus.SHORTLISTED: 'You have been shortlisted!',
                ApplicationStatus.SELECTED: 'Congratulations! You have been selected!',
                ApplicationStatus.REJECTED: 'Unfortunately, your application was not selected.',
                ApplicationStatus.INTERVIEW: 'You have been invited for an interview.',
            }.get(new_status, f'Your application status has been updated to {new_status}.')
            send_notification(app.student.user, f'Application Update – {app.job.title}',
                              status_msg, notif_type='APPLICATION',
                              link='/student/applications/')
            messages.success(request, f'Status updated to {new_status}.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect(request.META.get('HTTP_REFERER', 'companies:applicants'))


# ─── Interview Scheduling ─────────────────────────────────────
@company_required
def schedule_interview(request, app_id):
    user, company = _get_company(request)
    try:
        app = Application.objects.get(id=app_id)
    except Exception:
        messages.error(request, 'Application not found.')
        return redirect('companies:applicants')

    if request.method == 'POST':
        round_name = request.POST.get('round_name', 'Technical Interview')
        scheduled_at_str = request.POST.get('scheduled_at', '')
        mode = request.POST.get('mode', InterviewMode.ONLINE)
        link_or_venue = request.POST.get('link_or_venue', '')
        try:
            scheduled_at = datetime.datetime.strptime(scheduled_at_str, '%Y-%m-%dT%H:%M') \
                if scheduled_at_str else None
            interview = Interview(
                application=app,
                round_name=round_name,
                scheduled_at=scheduled_at,
                mode=mode,
                link_or_venue=link_or_venue,
            )
            interview.save()
            app.update_status(ApplicationStatus.INTERVIEW, f'Interview scheduled: {round_name}')
            app.save()
            send_notification(app.student.user, f'Interview Scheduled – {app.job.title}',
                              f'Your interview "{round_name}" is scheduled for '
                              f'{scheduled_at.strftime("%d %b %Y %H:%M") if scheduled_at else "TBD"}. '
                              f'Mode: {mode}. Details: {link_or_venue}',
                              notif_type='INTERVIEW', link='/student/applications/')
            messages.success(request, 'Interview scheduled and student notified.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('companies:applicants')

    return render(request, 'companies/schedule_interview.html', {
        'application': app, 'modes': InterviewMode.CHOICES
    })


# ─── Export Applicants CSV ────────────────────────────────────
@company_required
def export_applicants(request, job_id):
    user, company = _get_company(request)
    try:
        job = Job.objects.get(id=job_id, company=company)
        apps = Application.objects(job=job)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="applicants_{job.title}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'University', 'Department', 'CGPA', 'Batch', 'Status', 'Applied At'])
        for app in apps:
            s = app.student
            if not s:
                continue
            writer.writerow([
                s.full_name,
                s.user.email if s.user else '',
                s.university.name if s.university else '',
                s.department.name if s.department else '',
                s.cgpa,
                s.batch_year,
                app.status,
                app.applied_at.strftime('%Y-%m-%d') if app.applied_at else '',
            ])
        return response
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('companies:jobs')


# ─── Send Offer ───────────────────────────────────────────────
@company_required
def send_offer(request, app_id):
    user, company = _get_company(request)
    try:
        app = Application.objects.get(id=app_id)
    except Exception:
        messages.error(request, 'Application not found.')
        return redirect('companies:applicants')

    if request.method == 'POST':
        from accounts.utils import save_uploaded_file
        ctc_offered = request.POST.get('ctc_offered', '')
        joining_date_str = request.POST.get('joining_date', '')
        offer_letter = request.FILES.get('offer_letter')
        joining_date = None
        if joining_date_str:
            try:
                joining_date = datetime.datetime.strptime(joining_date_str, '%Y-%m-%d')
            except Exception:
                pass
        offer_path = save_uploaded_file(offer_letter, 'offers/') if offer_letter else None
        Offer(
            application=app,
            ctc_offered=ctc_offered,
            offer_letter_path=offer_path,
            joining_date=joining_date,
        ).save()
        app.update_status(ApplicationStatus.OFFER_SENT, 'Offer letter sent.')
        app.save()
        send_notification(app.student.user, f'Offer Letter – {app.job.title}',
                          f'You have received an offer! CTC: {ctc_offered}.',
                          notif_type='OFFER', link='/student/offers/')
        messages.success(request, 'Offer sent to student.')
        return redirect('companies:applicants')

    return render(request, 'companies/send_offer.html', {'application': app})

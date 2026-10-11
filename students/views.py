"""Student module views."""
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages

from accounts.decorators import student_required, get_current_user
from accounts.utils import log_activity, send_notification, save_uploaded_file
from core.models import (
    User, StudentProfile, UniversityProfile, Department,
    Job, Application, PlacementDrive, Interview, Offer,
    Notification, ApplicationStatus, JobStatus, ApprovalStatus,
    ApplicationStatusEntry
)


def _get_student(request):
    user = get_current_user(request)
    return user, StudentProfile.objects(user=user).first()


def _check_eligibility(student, job):
    """Return (is_eligible, reason) for a student-job pair."""
    e = job.eligibility
    if e:
        if e.min_cgpa and student.cgpa < e.min_cgpa:
            return False, f'Minimum CGPA {e.min_cgpa} required (yours: {student.cgpa})'
        if e.max_backlogs is not None and student.backlogs > e.max_backlogs:
            return False, f'Max {e.max_backlogs} backlogs allowed (yours: {student.backlogs})'
        if e.batch_years and student.batch_year not in e.batch_years:
            return False, f'Batch {student.batch_year} not eligible'
    return True, ''


# ─── Dashboard ───────────────────────────────────────────────
@student_required
def dashboard(request):
    user, student = _get_student(request)
    if not student:
        messages.warning(request, 'Please complete your profile.')
        return redirect('students:profile')

    # Applications summary
    apps = Application.objects(student=student)
    my_apps_count = apps.count()
    shortlisted = apps.filter(status=ApplicationStatus.SHORTLISTED).count()
    selected = apps.filter(status=ApplicationStatus.SELECTED).count()

    # Upcoming interviews
    upcoming_interviews = []
    for app in apps.filter(status=ApplicationStatus.INTERVIEW):
        interviews = Interview.objects(application=app).order_by('scheduled_at').limit(1)
        for iv in interviews:
            upcoming_interviews.append({'interview': iv, 'app': app})

    # Recommended jobs (open, student is eligible)
    all_open_jobs = Job.objects(status=JobStatus.OPEN).order_by('-created_at').limit(20)
    recommended = []
    applied_job_ids = {str(a.job.id) for a in apps if a.job}
    for job in all_open_jobs:
        eligible, reason = _check_eligibility(student, job)
        recommended.append({
            'job': job,
            'eligible': eligible,
            'reason': reason,
            'applied': str(job.id) in applied_job_ids,
        })
    recommended = recommended[:6]

    context = {
        'student': student,
        'my_apps_count': my_apps_count,
        'shortlisted': shortlisted,
        'selected': selected,
        'upcoming_interviews': upcoming_interviews,
        'recommended_jobs': recommended,
        'profile_complete': student.profile_complete,
    }
    return render(request, 'students/dashboard.html', context)


# ─── Profile ─────────────────────────────────────────────────
@student_required
def profile(request):
    user, student = _get_student(request)
    departments = []
    if student and student.university:
        departments = Department.objects(university=student.university)

    if request.method == 'POST':
        if not student:
            messages.error(request, 'Student profile not found.')
            return redirect('students:profile')

        student.first_name = request.POST.get('first_name', student.first_name)
        student.last_name = request.POST.get('last_name', student.last_name)
        student.phone = request.POST.get('phone', student.phone)
        student.address = request.POST.get('address', student.address)
        student.gender = request.POST.get('gender', student.gender)
        try:
            student.cgpa = float(request.POST.get('cgpa', student.cgpa) or student.cgpa)
        except Exception:
            pass
        try:
            student.batch_year = int(request.POST.get('batch_year', student.batch_year) or student.batch_year)
        except Exception:
            pass
        try:
            student.backlogs = int(request.POST.get('backlogs', student.backlogs) or student.backlogs)
        except Exception:
            pass

        skills_raw = request.POST.get('skills', '')
        student.skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
        student.github_url = request.POST.get('github_url', student.github_url) or None
        student.linkedin_url = request.POST.get('linkedin_url', student.linkedin_url) or None
        student.roll_number = request.POST.get('roll_number', student.roll_number)

        dept_id = request.POST.get('department_id', '')
        if dept_id:
            try:
                student.department = Department.objects.get(id=dept_id)
            except Exception:
                pass

        if request.FILES.get('photo'):
            student.photo_path = save_uploaded_file(request.FILES['photo'], 'photos/students/')
        if request.FILES.get('resume'):
            resume_file = request.FILES['resume']
            if resume_file.content_type == 'application/pdf':
                student.resume_path = save_uploaded_file(resume_file, 'resumes/')
            else:
                messages.error(request, 'Resume must be a PDF file.')

        student.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('students:profile')

    return render(request, 'students/profile.html', {
        'student': student,
        'departments': departments,
    })


# ─── Job Browse & Search ──────────────────────────────────────
@student_required
def job_list(request):
    user, student = _get_student(request)
    query = request.GET.get('q', '')
    job_type = request.GET.get('type', '')
    location = request.GET.get('location', '')
    eligible_only = request.GET.get('eligible_only', '') == 'on'

    jobs = Job.objects(status=JobStatus.OPEN).order_by('-created_at')
    if query:
        jobs = [j for j in jobs if query.lower() in j.title.lower()
                or query.lower() in (j.location or '').lower()]
    else:
        jobs = list(jobs)
    if job_type:
        jobs = [j for j in jobs if j.job_type == job_type]
    if location:
        jobs = [j for j in jobs if location.lower() in (j.location or '').lower()]

    applied_job_ids = set()
    if student:
        applied_job_ids = {str(a.job.id) for a in Application.objects(student=student) if a.job}

    job_data = []
    for job in jobs:
        eligible, reason = _check_eligibility(student, job) if student else (True, '')
        if eligible_only and not eligible:
            continue
        job_data.append({
            'job': job,
            'eligible': eligible,
            'reason': reason,
            'applied': str(job.id) in applied_job_ids,
        })

    return render(request, 'students/job_list.html', {
        'job_data': job_data,
        'query': query,
        'job_type': job_type,
        'location': location,
        'eligible_only': eligible_only,
        'job_types': ['FULL_TIME', 'INTERNSHIP', 'PART_TIME'],
        'student': student,
    })


@student_required
def job_detail(request, job_id):
    user, student = _get_student(request)
    try:
        job = Job.objects.get(id=job_id, status=JobStatus.OPEN)
    except Exception:
        messages.error(request, 'Job not found or closed.')
        return redirect('students:jobs')

    eligible, reason = _check_eligibility(student, job) if student else (False, 'Profile required')
    already_applied = False
    if student:
        already_applied = Application.objects(job=job, student=student).count() > 0

    return render(request, 'students/job_detail.html', {
        'job': job,
        'eligible': eligible,
        'reason': reason,
        'already_applied': already_applied,
        'student': student,
    })


# ─── Apply to Job ─────────────────────────────────────────────
@student_required
def apply_job(request, job_id):
    user, student = _get_student(request)
    if not student:
        messages.error(request, 'Complete your profile before applying.')
        return redirect('students:profile')

    try:
        job = Job.objects.get(id=job_id, status=JobStatus.OPEN)
    except Exception:
        messages.error(request, 'Job not found or closed.')
        return redirect('students:jobs')

    # Prevent duplicate
    if Application.objects(job=job, student=student).count() > 0:
        messages.warning(request, 'You have already applied to this job.')
        return redirect('students:job_detail', job_id=job_id)

    # Eligibility check
    eligible, reason = _check_eligibility(student, job)
    if not eligible:
        messages.error(request, f'Not eligible: {reason}')
        return redirect('students:job_detail', job_id=job_id)

    cover_note = request.POST.get('cover_note', '')
    app = Application(
        job=job,
        student=student,
        status=ApplicationStatus.APPLIED,
        cover_note=cover_note,
        status_history=[ApplicationStatusEntry(
            status=ApplicationStatus.APPLIED,
            timestamp=datetime.datetime.utcnow(),
            note='Application submitted.',
        )],
    )
    app.save()
    log_activity(user, 'APPLY_JOB', f'Applied to: {job.title}', request.META.get('REMOTE_ADDR'))
    messages.success(request, f'Successfully applied to "{job.title}"!')
    return redirect('students:applications')


# ─── Application Tracking ─────────────────────────────────────
@student_required
def my_applications(request):
    user, student = _get_student(request)
    if not student:
        return redirect('students:profile')
    apps = Application.objects(student=student).order_by('-applied_at')
    return render(request, 'students/applications.html', {
        'applications': apps, 'student': student
    })


@student_required
def application_detail(request, app_id):
    user, student = _get_student(request)
    try:
        app = Application.objects.get(id=app_id, student=student)
    except Exception:
        messages.error(request, 'Application not found.')
        return redirect('students:applications')
    interviews = Interview.objects(application=app).order_by('scheduled_at')
    return render(request, 'students/application_detail.html', {
        'application': app, 'interviews': interviews, 'student': student
    })


# ─── Offers ───────────────────────────────────────────────────
@student_required
def my_offers(request):
    user, student = _get_student(request)
    if not student:
        return redirect('students:profile')
    apps = Application.objects(student=student,
                                status__in=[ApplicationStatus.OFFER_SENT,
                                            ApplicationStatus.OFFER_ACCEPTED,
                                            ApplicationStatus.OFFER_DECLINED])
    offers_data = []
    for app in apps:
        offer = Offer.objects(application=app).first()
        if offer:
            offers_data.append({'application': app, 'offer': offer})

    return render(request, 'students/offers.html', {
        'offers_data': offers_data, 'student': student
    })


@student_required
def respond_offer(request, offer_id):
    user, student = _get_student(request)
    if request.method == 'POST':
        try:
            offer = Offer.objects.get(id=offer_id)
            response_val = request.POST.get('response', '')
            if response_val in ['ACCEPTED', 'DECLINED']:
                offer.student_response = response_val
                offer.responded_at = datetime.datetime.utcnow()
                offer.save()
                # Update application status
                app = offer.application
                new_status = (ApplicationStatus.OFFER_ACCEPTED
                              if response_val == 'ACCEPTED' else ApplicationStatus.OFFER_DECLINED)
                app.update_status(new_status)
                app.save()
                messages.success(request, f'Offer {response_val.lower()}.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('students:offers')

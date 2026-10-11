"""University module views."""
import csv
import io
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

from accounts.decorators import university_required, get_current_user
from accounts.utils import log_activity, send_notification
from core.models import (
    User, UniversityProfile, CompanyProfile, StudentProfile,
    Department, PlacementDrive, Application, Job,
    Announcement, ApprovalStatus, ApplicationStatus, DriveStatus,
    EligibilityCriteria, Roles
)


def _get_university(request):
    user = get_current_user(request)
    return user, UniversityProfile.objects(user=user).first()


# ─── Dashboard ───────────────────────────────────────────────
@university_required
def dashboard(request):
    user, uni = _get_university(request)
    if not uni or uni.status != ApprovalStatus.APPROVED:
        messages.warning(request, 'Your account is pending admin approval.')
        return render(request, 'universities/pending.html', {'profile': uni})

    students = StudentProfile.objects(university=uni)
    departments = Department.objects(university=uni)
    drives = PlacementDrive.objects(university=uni)
    active_drives = drives.filter(status__in=[DriveStatus.SCHEDULED, DriveStatus.ONGOING])
    placed = 0
    for student in students:
        if Application.objects(student=student, status=ApplicationStatus.SELECTED).count() > 0:
            placed += 1

    context = {
        'uni': uni,
        'total_students': students.count(),
        'total_departments': departments.count(),
        'active_drives': active_drives.count(),
        'placed_students': placed,
        'placement_rate': round((placed / students.count() * 100), 1) if students.count() else 0,
        'recent_drives': drives.order_by('-created_at').limit(5),
    }
    return render(request, 'universities/dashboard.html', context)


# ─── Profile ─────────────────────────────────────────────────
@university_required
def profile(request):
    user, uni = _get_university(request)
    if request.method == 'POST':
        from accounts.utils import save_uploaded_file
        uni.name = request.POST.get('name', uni.name)
        uni.affiliation = request.POST.get('affiliation', uni.affiliation)
        uni.address = request.POST.get('address', uni.address)
        uni.city = request.POST.get('city', uni.city)
        uni.state = request.POST.get('state', uni.state)
        uni.website = request.POST.get('website', uni.website) or None
        uni.placement_officer = request.POST.get('placement_officer', uni.placement_officer)
        uni.contact_phone = request.POST.get('contact_phone', uni.contact_phone)
        uni.contact_email = request.POST.get('contact_email', uni.contact_email)
        if request.FILES.get('logo'):
            uni.logo_path = save_uploaded_file(request.FILES['logo'], 'logos/universities/')
        uni.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('universities:profile')
    return render(request, 'universities/profile.html', {'uni': uni})


# ─── Departments ─────────────────────────────────────────────
@university_required
def department_list(request):
    user, uni = _get_university(request)
    departments = Department.objects(university=uni).order_by('name')
    return render(request, 'universities/departments.html', {
        'departments': departments, 'uni': uni
    })


@university_required
def add_department(request):
    user, uni = _get_university(request)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        if not name:
            messages.error(request, 'Department name is required.')
        else:
            Department(university=uni, name=name, code=code).save()
            messages.success(request, f'Department "{name}" added.')
        return redirect('universities:departments')
    return redirect('universities:departments')


@university_required
def delete_department(request, dept_id):
    user, uni = _get_university(request)
    if request.method == 'POST':
        try:
            dept = Department.objects.get(id=dept_id, university=uni)
            dept.delete()
            messages.success(request, 'Department deleted.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('universities:departments')


# ─── Student Management ───────────────────────────────────────
@university_required
def student_list(request):
    user, uni = _get_university(request)
    query = request.GET.get('q', '')
    dept_filter = request.GET.get('dept', '')
    verified_filter = request.GET.get('verified', '')
    students = StudentProfile.objects(university=uni)
    if query:
        students = [s for s in students if query.lower() in s.full_name.lower()
                    or query.lower() in (s.roll_number or '').lower()]
    if dept_filter:
        try:
            dept = Department.objects.get(id=dept_filter)
            students = [s for s in students if s.department and str(s.department.id) == dept_filter]
        except Exception:
            pass
    if verified_filter == 'yes':
        students = [s for s in students if s.is_verified]
    elif verified_filter == 'no':
        students = [s for s in students if not s.is_verified]
    departments = Department.objects(university=uni)
    return render(request, 'universities/student_list.html', {
        'students': students, 'departments': departments,
        'query': query, 'dept_filter': dept_filter, 'verified_filter': verified_filter,
    })


@university_required
def verify_student(request, student_id):
    user, uni = _get_university(request)
    try:
        student = StudentProfile.objects.get(id=student_id, university=uni)
        student.is_verified = True
        student.save()
        send_notification(student.user, 'Profile Verified',
                          'Your student profile has been verified by your university.',
                          link='/student/profile/')
        messages.success(request, f'{student.full_name} verified.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('universities:students')


@university_required
def bulk_upload_students(request):
    """Bulk upload students via CSV."""
    user, uni = _get_university(request)
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        try:
            data = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(data))
            created = 0
            errors = []
            for i, row in enumerate(reader, 1):
                try:
                    email = row.get('email', '').strip().lower()
                    if not email or User.objects(email=email).first():
                        errors.append(f'Row {i}: Invalid or duplicate email "{email}"')
                        continue
                    u = User(email=email, role=Roles.STUDENT)
                    u.set_password(row.get('password', 'Welcome@123'))
                    u.save()
                    StudentProfile(
                        user=u,
                        university=uni,
                        first_name=row.get('first_name', '').strip(),
                        last_name=row.get('last_name', '').strip(),
                        roll_number=row.get('roll_number', '').strip(),
                        cgpa=float(row.get('cgpa', 0) or 0),
                        batch_year=int(row.get('batch_year', 0) or 0),
                    ).save()
                    created += 1
                except Exception as e:
                    errors.append(f'Row {i}: {e}')
            messages.success(request, f'{created} students uploaded.')
            if errors:
                messages.warning(request, f'{len(errors)} rows had errors: {"; ".join(errors[:3])}')
        except Exception as e:
            messages.error(request, f'CSV processing error: {e}')
        return redirect('universities:students')
    return render(request, 'universities/bulk_upload.html', {'uni': uni})


# ─── Placement Drives ─────────────────────────────────────────
@university_required
def drive_list(request):
    user, uni = _get_university(request)
    drives = PlacementDrive.objects(university=uni).order_by('-created_at')
    return render(request, 'universities/drive_list.html', {
        'drives': drives, 'uni': uni
    })


@university_required
def create_drive(request):
    user, uni = _get_university(request)
    companies = CompanyProfile.objects(status=ApprovalStatus.APPROVED)
    jobs = Job.objects(status='OPEN')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        company_id = request.POST.get('company_id', '')
        drive_date_str = request.POST.get('drive_date', '')
        venue = request.POST.get('venue', '')
        description = request.POST.get('description', '')
        min_cgpa = float(request.POST.get('min_cgpa', 0) or 0)
        max_backlogs = int(request.POST.get('max_backlogs', 0) or 0)

        if not title or not company_id:
            messages.error(request, 'Title and company are required.')
            return render(request, 'universities/create_drive.html',
                          {'companies': companies, 'jobs': jobs})
        try:
            company = CompanyProfile.objects.get(id=company_id)
            drive_date = datetime.datetime.strptime(drive_date_str, '%Y-%m-%dT%H:%M') \
                if drive_date_str else None
            eligibility = EligibilityCriteria(
                min_cgpa=min_cgpa,
                max_backlogs=max_backlogs,
            )
            drive = PlacementDrive(
                university=uni,
                company=company,
                title=title,
                drive_date=drive_date,
                venue=venue,
                description=description,
                eligibility=eligibility,
            )
            drive.save()
            log_activity(user, 'CREATE_DRIVE', f'Created drive: {title}',
                         request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Drive "{title}" created successfully.')
            return redirect('universities:drives')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'universities/create_drive.html', {
        'companies': companies, 'jobs': jobs
    })


@university_required
def drive_detail(request, drive_id):
    user, uni = _get_university(request)
    try:
        drive = PlacementDrive.objects.get(id=drive_id, university=uni)
    except Exception:
        messages.error(request, 'Drive not found.')
        return redirect('universities:drives')

    # Applications for the jobs linked to this drive
    apps = Application.objects(drive=drive)
    return render(request, 'universities/drive_detail.html', {
        'drive': drive,
        'applications': apps,
        'status_choices': ['APPLIED', 'SHORTLISTED', 'REJECTED'],
    })


# ─── Reports ─────────────────────────────────────────────────
@university_required
def placement_report(request):
    user, uni = _get_university(request)
    students = StudentProfile.objects(university=uni)
    departments = Department.objects(university=uni)

    report_data = []
    for student in students:
        selected = Application.objects(student=student, status=ApplicationStatus.SELECTED).first()
        report_data.append({
            'student': student,
            'applications': Application.objects(student=student).count(),
            'placed': selected is not None,
            'company': selected.job.company.company_name if selected and selected.job and selected.job.company else '-',
            'ctc': selected.job.ctc if selected and selected.job else '-',
        })

    export = request.GET.get('export', '')
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="university_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student', 'Department', 'CGPA', 'Batch', 'Applications', 'Placed', 'Company', 'CTC'])
        for r in report_data:
            s = r['student']
            writer.writerow([
                s.full_name,
                s.department.name if s.department else '-',
                s.cgpa,
                s.batch_year,
                r['applications'],
                'Yes' if r['placed'] else 'No',
                r['company'],
                r['ctc'],
            ])
        return response

    return render(request, 'universities/placement_report.html', {
        'report_data': report_data,
        'uni': uni,
        'departments': departments,
    })


# ─── Announcements ────────────────────────────────────────────
@university_required
def send_announcement(request):
    user, uni = _get_university(request)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if not title or not content:
            messages.error(request, 'Title and content are required.')
        else:
            students = StudentProfile.objects(university=uni)
            for s in students:
                send_notification(s.user, title, content[:200],
                                  notif_type='ANNOUNCEMENT')
            Announcement(sender=user, title=title, content=content,
                         target_role=Roles.STUDENT, target_university=uni).save()
            messages.success(request, f'Announcement sent to {students.count()} students.')
            return redirect('universities:dashboard')
    return render(request, 'universities/announcement.html', {'uni': uni})

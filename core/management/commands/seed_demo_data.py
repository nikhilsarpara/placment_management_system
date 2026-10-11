"""Management command to populate database with rich demo data for PlacePro."""
import datetime
from django.core.management.base import BaseCommand
from core.models import (
    User, Roles, ApprovalStatus, JobStatus, JobType, ApplicationStatus,
    InterviewMode, UniversityProfile, CompanyProfile, Department,
    StudentProfile, Job, PlacementDrive, DriveRound, Application,
    ApplicationStatusEntry, Interview, Offer, Notification, Announcement,
    EligibilityCriteria
)


class Command(BaseCommand):
    help = 'Seeds database with realistic demo data for testing and evaluation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting demo data population...'))

        # 1. Admin Account
        admin_email = 'admin@placepro.com'
        admin_user = User.objects(email=admin_email).first()
        if not admin_user:
            admin_user = User(email=admin_email, role=Roles.ADMIN)
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created Admin: {admin_email} / admin123'))
        else:
            admin_user.set_password('admin123')
            admin_user.save()

        # 2. Universities
        # Apex Institute
        apex_email = 'apex.admin@apex.edu'
        apex_user = User.objects(email=apex_email).first()
        if not apex_user:
            apex_user = User(email=apex_email, role=Roles.UNIVERSITY)
            apex_user.set_password('apex123')
            apex_user.save()

        apex_uni = UniversityProfile.objects(user=apex_user).first()
        if not apex_uni:
            apex_uni = UniversityProfile(
                user=apex_user,
                name='Apex Institute of Technology',
                affiliation='AICTE / NAAC A++',
                address='100 Knowledge Boulevard, Tech Park',
                city='Bangalore',
                state='Karnataka',
                website='https://www.apextech.edu',
                placement_officer='Dr. Ramesh Nair',
                contact_phone='+91 98765 43210',
                contact_email='tpo@apextech.edu',
                status=ApprovalStatus.APPROVED,
            )
            apex_uni.save()

        # National Engineering University
        neu_email = 'neu.admin@neu.edu'
        neu_user = User.objects(email=neu_email).first()
        if not neu_user:
            neu_user = User(email=neu_email, role=Roles.UNIVERSITY)
            neu_user.set_password('neu123')
            neu_user.save()

        neu_uni = UniversityProfile.objects(user=neu_user).first()
        if not neu_uni:
            neu_uni = UniversityProfile(
                user=neu_user,
                name='National Engineering University',
                affiliation='UGC Recognized',
                address='Central Campus, University Road',
                city='Pune',
                state='Maharashtra',
                website='https://www.neu.edu.in',
                placement_officer='Prof. Sunita Deshmukh',
                contact_phone='+91 98220 11223',
                contact_email='placements@neu.edu.in',
                status=ApprovalStatus.APPROVED,
            )
            neu_uni.save()

        self.stdout.write(self.style.SUCCESS('Created Universities: Apex Institute & National Engineering University'))

        # 3. Departments
        apex_cse = Department.objects(university=apex_uni, code='CSE').first()
        if not apex_cse:
            apex_cse = Department(university=apex_uni, name='Computer Science and Engineering', code='CSE').save()
        apex_it = Department.objects(university=apex_uni, code='IT').first()
        if not apex_it:
            apex_it = Department(university=apex_uni, name='Information Technology', code='IT').save()
        apex_ece = Department.objects(university=apex_uni, code='ECE').first()
        if not apex_ece:
            apex_ece = Department(university=apex_uni, name='Electronics and Communication', code='ECE').save()

        neu_cse = Department.objects(university=neu_uni, code='CS-AI').first()
        if not neu_cse:
            neu_cse = Department(university=neu_uni, name='Computer Science & AI', code='CS-AI').save()

        # 4. Companies
        # Google
        google_email = 'recruiter@google.com'
        google_user = User.objects(email=google_email).first()
        if not google_user:
            google_user = User(email=google_email, role=Roles.COMPANY)
            google_user.set_password('google123')
            google_user.save()

        google_company = CompanyProfile.objects(user=google_user).first()
        if not google_company:
            google_company = CompanyProfile(
                user=google_user,
                company_name='Google Cloud',
                industry='Cloud & Software',
                size='10000+',
                website='https://cloud.google.com',
                hr_name='Vikramaditya Roy',
                hr_email='vikram.roy@google.com',
                hr_phone='+91 80 6789 0000',
                address='Google Signature Towers, Outer Ring Road',
                city='Bangalore',
                description='Google Cloud provides organizations with leading infrastructure, platform capabilities and industry solutions.',
                status=ApprovalStatus.APPROVED,
            ).save()

        # Infosys
        infy_email = 'campus@infosys.com'
        infy_user = User.objects(email=infy_email).first()
        if not infy_user:
            infy_user = User(email=infy_email, role=Roles.COMPANY)
            infy_user.set_password('infosys123')
            infy_user.save()

        infy_company = CompanyProfile.objects(user=infy_user).first()
        if not infy_company:
            infy_company = CompanyProfile(
                user=infy_user,
                company_name='Infosys Technologies',
                industry='IT Services & Consulting',
                size='50000+',
                website='https://www.infosys.com',
                hr_name='Ananya Sen Gupta',
                hr_email='ananya.sen@infosys.com',
                hr_phone='+91 80 2852 0261',
                address='Electronics City, Hosur Road',
                city='Bangalore',
                description='Infosys is a global leader in next-generation digital services and consulting.',
                status=ApprovalStatus.APPROVED,
            ).save()

        # Tech Mahindra
        techm_email = 'careers@techmahindra.com'
        techm_user = User.objects(email=techm_email).first()
        if not techm_user:
            techm_user = User(email=techm_email, role=Roles.COMPANY)
            techm_user.set_password('techm123')
            techm_user.save()

        techm_company = CompanyProfile.objects(user=techm_user).first()
        if not techm_company:
            techm_company = CompanyProfile(
                user=techm_user,
                company_name='Tech Mahindra',
                industry='Digital Transformation & AI',
                size='25000+',
                website='https://www.techmahindra.com',
                hr_name='Kunal Varma',
                hr_email='kunal.varma@techmahindra.com',
                hr_phone='+91 40 6636 1000',
                address='Hitech City, Madhapur',
                city='Hyderabad',
                description='Connected world experiences delivering innovative and customer-centric information technology experiences.',
                status=ApprovalStatus.APPROVED,
            ).save()

        self.stdout.write(self.style.SUCCESS('Created Companies: Google Cloud, Infosys, Tech Mahindra'))

        # 5. Students
        # Student 1: Rahul Sharma
        rahul_email = 'rahul@apex.edu'
        rahul_user = User.objects(email=rahul_email).first()
        if not rahul_user:
            rahul_user = User(email=rahul_email, role=Roles.STUDENT)
            rahul_user.set_password('student123')
            rahul_user.save()

        rahul_st = StudentProfile.objects(user=rahul_user).first()
        if not rahul_st:
            rahul_st = StudentProfile(
                user=rahul_user,
                university=apex_uni,
                department=apex_cse,
                first_name='Rahul',
                last_name='Sharma',
                roll_number='APEX-2022-CS014',
                phone='+91 98111 22334',
                gender='Male',
                cgpa=8.85,
                batch_year=2026,
                backlogs=0,
                skills=['Python', 'Django', 'MongoDB', 'Docker', 'Kubernetes', 'FastAPI'],
                github_url='https://github.com',
                linkedin_url='https://linkedin.com',
                is_verified=True,
            )
            rahul_st.save()

        # Student 2: Priya Patel
        priya_email = 'priya@apex.edu'
        priya_user = User.objects(email=priya_email).first()
        if not priya_user:
            priya_user = User(email=priya_email, role=Roles.STUDENT)
            priya_user.set_password('student123')
            priya_user.save()

        priya_st = StudentProfile.objects(user=priya_user).first()
        if not priya_st:
            priya_st = StudentProfile(
                user=priya_user,
                university=apex_uni,
                department=apex_it,
                first_name='Priya',
                last_name='Patel',
                roll_number='APEX-2022-IT009',
                phone='+91 98222 33445',
                gender='Female',
                cgpa=9.32,
                batch_year=2026,
                backlogs=0,
                skills=['Java', 'Spring Boot', 'React', 'TypeScript', 'AWS', 'PostgreSQL'],
                github_url='https://github.com',
                linkedin_url='https://linkedin.com',
                is_verified=True,
            )
            priya_st.save()

        # Student 3: Amit Kumar
        amit_email = 'amit@apex.edu'
        amit_user = User.objects(email=amit_email).first()
        if not amit_user:
            amit_user = User(email=amit_email, role=Roles.STUDENT)
            amit_user.set_password('student123')
            amit_user.save()

        amit_st = StudentProfile.objects(user=amit_user).first()
        if not amit_st:
            amit_st = StudentProfile(
                user=amit_user,
                university=apex_uni,
                department=apex_ece,
                first_name='Amit',
                last_name='Kumar',
                roll_number='APEX-2022-EC032',
                phone='+91 98333 44556',
                gender='Male',
                cgpa=7.45,
                batch_year=2026,
                backlogs=0,
                skills=['C++', 'Embedded Systems', 'IoT', 'Python', 'Linux'],
                is_verified=True,
            )
            amit_st.save()

        self.stdout.write(self.style.SUCCESS('Created Students: Rahul Sharma, Priya Patel, Amit Kumar'))

        # 6. Jobs
        job_gc_sde = Job.objects(company=google_company, title='Cloud Solutions Engineer').first()
        if not job_gc_sde:
            job_gc_sde = Job(
                company=google_company,
                title='Cloud Solutions Engineer',
                description='As a Cloud Solutions Engineer, you will build and architect next-generation cloud architectures for enterprises using GCP, Kubernetes, and Golang/Python microservices.',
                skills_required=['Python', 'Cloud Architecture', 'Kubernetes', 'Networking', 'Linux'],
                ctc='18 LPA',
                location='Bangalore / Hybrid',
                job_type=JobType.FULL_TIME,
                eligibility=EligibilityCriteria(min_cgpa=8.0, max_backlogs=0, batch_years=[2026]),
                openings=5,
                application_deadline=datetime.datetime.utcnow() + datetime.timedelta(days=25),
                status=JobStatus.OPEN,
            ).save()

        job_gc_intern = Job.objects(company=google_company, title='Site Reliability Intern').first()
        if not job_gc_intern:
            job_gc_intern = Job(
                company=google_company,
                title='Site Reliability Intern',
                description='Work alongside SRE teams ensuring high availability, continuous performance optimization, and telemetry pipelines for hyperscale cloud platforms.',
                skills_required=['Python', 'Docker', 'Linux Internals', 'Automation'],
                ctc='₹65,000 / month',
                location='Remote / Bangalore',
                job_type=JobType.INTERNSHIP,
                eligibility=EligibilityCriteria(min_cgpa=7.5, max_backlogs=0, batch_years=[2026, 2027]),
                openings=4,
                application_deadline=datetime.datetime.utcnow() + datetime.timedelta(days=15),
                status=JobStatus.OPEN,
            ).save()

        job_infy = Job.objects(company=infy_company, title='Systems Engineer Specialist').first()
        if not job_infy:
            job_infy = Job(
                company=infy_company,
                title='Systems Engineer Specialist',
                description='Design and implement enterprise software solutions, full-stack applications, and backend systems in Java/J2EE and modern web frameworks.',
                skills_required=['Java', 'Spring Boot', 'SQL', 'Web Services'],
                ctc='6.5 LPA',
                location='Pune / Bangalore',
                job_type=JobType.FULL_TIME,
                eligibility=EligibilityCriteria(min_cgpa=6.5, max_backlogs=1, batch_years=[2026]),
                openings=12,
                application_deadline=datetime.datetime.utcnow() + datetime.timedelta(days=30),
                status=JobStatus.OPEN,
            ).save()

        job_techm = Job.objects(company=techm_company, title='Associate Software Engineer').first()
        if not job_techm:
            job_techm = Job(
                company=techm_company,
                title='Associate Software Engineer',
                description='Join our core engineering cohorts focusing on cloud native microservices, generative AI integrations, and mobile APIs.',
                skills_required=['C++', 'Python', 'Algorithms', 'Databases'],
                ctc='8.0 LPA',
                location='Hyderabad',
                job_type=JobType.FULL_TIME,
                eligibility=EligibilityCriteria(min_cgpa=7.0, max_backlogs=0, batch_years=[2026]),
                openings=8,
                application_deadline=datetime.datetime.utcnow() + datetime.timedelta(days=20),
                status=JobStatus.OPEN,
            ).save()

        self.stdout.write(self.style.SUCCESS('Created Jobs: Google Cloud SDE, SRE Intern, Infosys SES, TechM ASE'))

        # 7. Placement Drives
        drive_google = PlacementDrive.objects(university=apex_uni, company=google_company).first()
        if not drive_google:
            drive_google = PlacementDrive(
                university=apex_uni,
                company=google_company,
                title='Google Cloud Campus Hiring 2026',
                drive_date=datetime.datetime.utcnow() + datetime.timedelta(days=10),
                venue='Apex Central Auditorium / Google Meet',
                description='All eligible CSE & IT candidates must attend the pre-placement talk at 9:30 AM with college ID card and printed resumes.',
                eligibility=EligibilityCriteria(min_cgpa=8.0, max_backlogs=0),
                rounds=[
                    DriveRound(round_number=1, round_name='Online Coding Challenge', scheduled_at=datetime.datetime.utcnow() + datetime.timedelta(days=10, hours=2)),
                    DriveRound(round_number=2, round_name='Technical Architecture Round', scheduled_at=datetime.datetime.utcnow() + datetime.timedelta(days=11)),
                    DriveRound(round_number=3, round_name='Managerial & Googliness', scheduled_at=datetime.datetime.utcnow() + datetime.timedelta(days=12)),
                ]
            ).save()

        # 8. Applications, Interviews & Offers
        # Rahul -> Google Cloud SDE
        app_rahul = Application.objects(job=job_gc_sde, student=rahul_st).first()
        if not app_rahul:
            app_rahul = Application(
                job=job_gc_sde,
                student=rahul_st,
                drive=drive_google,
                status=ApplicationStatus.OFFER_SENT,
                cover_note='Eager to contribute to Google Cloud systems with my background in distributed systems and Docker.',
                status_history=[
                    ApplicationStatusEntry(status=ApplicationStatus.APPLIED, note='Application submitted online.'),
                    ApplicationStatusEntry(status=ApplicationStatus.SHORTLISTED, note='Shortlisted after coding round.'),
                    ApplicationStatusEntry(status=ApplicationStatus.INTERVIEW, note='Cleared technical interview rounds.'),
                    ApplicationStatusEntry(status=ApplicationStatus.OFFER_SENT, note='Official offer letter issued.'),
                ]
            ).save()

            Interview(
                application=app_rahul,
                round_name='System Design & Microservices',
                scheduled_at=datetime.datetime.utcnow() + datetime.timedelta(days=1),
                mode=InterviewMode.ONLINE,
                link_or_venue='https://meet.google.com/xyz-demo-test',
                result='Passed',
                feedback='Exceptional architectural grasp and clean algorithms.'
            ).save()

            Offer(
                application=app_rahul,
                ctc_offered='18 LPA',
                joining_date=datetime.datetime.utcnow() + datetime.timedelta(days=90),
                student_response='PENDING'
            ).save()

        # Priya -> Google Cloud SDE
        app_priya = Application.objects(job=job_gc_sde, student=priya_st).first()
        if not app_priya:
            app_priya = Application(
                job=job_gc_sde,
                student=priya_st,
                drive=drive_google,
                status=ApplicationStatus.SELECTED,
                cover_note='Passionate about scalable distributed storage and cloud reliability.',
                status_history=[
                    ApplicationStatusEntry(status=ApplicationStatus.APPLIED, note='Application submitted.'),
                    ApplicationStatusEntry(status=ApplicationStatus.SHORTLISTED, note='Online test cleared.'),
                    ApplicationStatusEntry(status=ApplicationStatus.SELECTED, note='Selected by Google Cloud!'),
                ]
            ).save()

        # Amit -> Infosys
        app_amit = Application.objects(job=job_infy, student=amit_st).first()
        if not app_amit:
            app_amit = Application(
                job=job_infy,
                student=amit_st,
                status=ApplicationStatus.SHORTLISTED,
                cover_note='Strong foundation in C++ and Object-Oriented design.',
                status_history=[
                    ApplicationStatusEntry(status=ApplicationStatus.APPLIED, note='Resume submitted.'),
                    ApplicationStatusEntry(status=ApplicationStatus.SHORTLISTED, note='Shortlisted for technical round.'),
                ]
            ).save()

        # 9. Announcements & Notifications
        ann = Announcement.objects(title='Campus Placement Season 2026 Officially Open!').first()
        if not ann:
            Announcement(
                sender=admin_user,
                title='Campus Placement Season 2026 Officially Open!',
                content='Welcome to the 2026 placement cycle on PlacePro. Please review your profiles and upload current resumes before applying to verified employer listings.',
                target_role=Roles.STUDENT,
            ).save()

        Notification(
            user=rahul_user,
            title='Formal Job Offer: Google Cloud',
            message='Congratulations! Google Cloud has sent you a formal offer of 18 LPA.',
            notification_type='OFFER',
            link='/student/offers/'
        ).save()

        self.stdout.write(self.style.SUCCESS('\n=========================================='))
        self.stdout.write(self.style.SUCCESS('DEMO DATA GENERATED SUCCESSFULLY!'))
        self.stdout.write(self.style.SUCCESS('=========================================='))
        self.stdout.write('Login Credentials for testing:')
        self.stdout.write('  Admin:      admin@placepro.com     / admin123')
        self.stdout.write('  University: apex.admin@apex.edu    / apex123')
        self.stdout.write('  Company:    recruiter@google.com   / google123')
        self.stdout.write('  Student:    rahul@apex.edu         / student123')
        self.stdout.write('==========================================\n')

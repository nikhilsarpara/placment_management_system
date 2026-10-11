"""
MongoEngine models for the Placement Management Platform.
All collections are defined here as a single source of truth.
Each app imports from here as needed.
"""
import datetime
from mongoengine import (
    Document, EmbeddedDocument, StringField, IntField, FloatField,
    BooleanField, DateTimeField, ListField, EmbeddedDocumentField,
    ReferenceField, URLField, EmailField, CASCADE
)
from django.contrib.auth.hashers import make_password, check_password


# ─────────────────────────────────────────────────────────────
#  ENUMS (as string constants)
# ─────────────────────────────────────────────────────────────
class Roles:
    ADMIN = 'ADMIN'
    COMPANY = 'COMPANY'
    UNIVERSITY = 'UNIVERSITY'
    STUDENT = 'STUDENT'
    CHOICES = [ADMIN, COMPANY, UNIVERSITY, STUDENT]


class ApprovalStatus:
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    SUSPENDED = 'SUSPENDED'
    CHOICES = [PENDING, APPROVED, REJECTED, SUSPENDED]


class JobStatus:
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    DRAFT = 'DRAFT'
    CHOICES = [OPEN, CLOSED, DRAFT]


class JobType:
    FULL_TIME = 'FULL_TIME'
    INTERNSHIP = 'INTERNSHIP'
    PART_TIME = 'PART_TIME'
    CHOICES = [FULL_TIME, INTERNSHIP, PART_TIME]


class ApplicationStatus:
    APPLIED = 'APPLIED'
    SHORTLISTED = 'SHORTLISTED'
    INTERVIEW = 'INTERVIEW'
    SELECTED = 'SELECTED'
    REJECTED = 'REJECTED'
    OFFER_SENT = 'OFFER_SENT'
    OFFER_ACCEPTED = 'OFFER_ACCEPTED'
    OFFER_DECLINED = 'OFFER_DECLINED'
    CHOICES = [APPLIED, SHORTLISTED, INTERVIEW, SELECTED, REJECTED,
               OFFER_SENT, OFFER_ACCEPTED, OFFER_DECLINED]


class DriveStatus:
    SCHEDULED = 'SCHEDULED'
    ONGOING = 'ONGOING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    CHOICES = [SCHEDULED, ONGOING, COMPLETED, CANCELLED]


class InterviewMode:
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    CHOICES = [ONLINE, OFFLINE]


class NotificationType:
    JOB = 'JOB'
    APPLICATION = 'APPLICATION'
    INTERVIEW = 'INTERVIEW'
    OFFER = 'OFFER'
    ANNOUNCEMENT = 'ANNOUNCEMENT'
    SYSTEM = 'SYSTEM'
    CHOICES = [JOB, APPLICATION, INTERVIEW, OFFER, ANNOUNCEMENT, SYSTEM]


# ─────────────────────────────────────────────────────────────
#  EMBEDDED DOCUMENTS
# ─────────────────────────────────────────────────────────────
class EligibilityCriteria(EmbeddedDocument):
    """Embedded in Job and PlacementDrive to define eligibility."""
    min_cgpa = FloatField(default=0.0)
    allowed_branches = ListField(StringField(), default=list)
    max_backlogs = IntField(default=0)
    batch_years = ListField(IntField(), default=list)


class ProjectEntry(EmbeddedDocument):
    title = StringField(max_length=200)
    description = StringField()
    url = URLField()
    technologies = ListField(StringField())


class CertificationEntry(EmbeddedDocument):
    name = StringField(max_length=200)
    issuer = StringField(max_length=200)
    year = IntField()
    url = URLField()


class InternshipEntry(EmbeddedDocument):
    company = StringField(max_length=200)
    role = StringField(max_length=200)
    duration = StringField(max_length=100)
    description = StringField()


class DriveRound(EmbeddedDocument):
    round_number = IntField()
    round_name = StringField(max_length=100)
    description = StringField()
    scheduled_at = DateTimeField()


class ApplicationStatusEntry(EmbeddedDocument):
    """Timeline entry for application status history."""
    status = StringField(choices=ApplicationStatus.CHOICES)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    note = StringField()


# ─────────────────────────────────────────────────────────────
#  USER
# ─────────────────────────────────────────────────────────────
class User(Document):
    """
    Central user document. Role determines which profile collection has details.
    Passwords stored as Django-hashed strings (PBKDF2).
    """
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    role = StringField(required=True, choices=Roles.CHOICES)
    is_active = BooleanField(default=True)
    is_blocked = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': ['email', 'role', 'is_active'],
        'ordering': ['-created_at'],
    }

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)

    # Django auth compatibility properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def pk(self):
        return str(self.id)

    def __str__(self):
        return f"{self.email} ({self.role})"


# ─────────────────────────────────────────────────────────────
#  UNIVERSITY PROFILE
# ─────────────────────────────────────────────────────────────
class UniversityProfile(Document):
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    name = StringField(required=True, max_length=300)
    affiliation = StringField(max_length=300)
    address = StringField()
    city = StringField(max_length=100)
    state = StringField(max_length=100)
    website = URLField()
    placement_officer = StringField(max_length=200)
    contact_phone = StringField(max_length=20)
    contact_email = EmailField()
    logo_path = StringField()
    verification_doc_path = StringField()
    status = StringField(choices=ApprovalStatus.CHOICES, default=ApprovalStatus.PENDING)
    rejection_reason = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'university_profiles',
        'indexes': ['user', 'status'],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────
#  COMPANY PROFILE
# ─────────────────────────────────────────────────────────────
class CompanyProfile(Document):
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    company_name = StringField(required=True, max_length=300)
    industry = StringField(max_length=200)
    size = StringField(max_length=100)
    website = URLField()
    hr_name = StringField(max_length=200)
    hr_email = EmailField()
    hr_phone = StringField(max_length=20)
    address = StringField()
    city = StringField(max_length=100)
    logo_path = StringField()
    verification_doc_path = StringField()
    description = StringField()
    status = StringField(choices=ApprovalStatus.CHOICES, default=ApprovalStatus.PENDING)
    rejection_reason = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'company_profiles',
        'indexes': ['user', 'status'],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name


# ─────────────────────────────────────────────────────────────
#  DEPARTMENT
# ─────────────────────────────────────────────────────────────
class Department(Document):
    university = ReferenceField(UniversityProfile, required=True, reverse_delete_rule=CASCADE)
    name = StringField(required=True, max_length=200)
    code = StringField(max_length=20)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'departments',
        'indexes': ['university'],
    }

    def __str__(self):
        return f"{self.name} ({self.code})"


# ─────────────────────────────────────────────────────────────
#  STUDENT PROFILE
# ─────────────────────────────────────────────────────────────
class StudentProfile(Document):
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    university = ReferenceField(UniversityProfile, required=True)
    department = ReferenceField(Department)
    roll_number = StringField(max_length=50)
    first_name = StringField(required=True, max_length=100)
    last_name = StringField(required=True, max_length=100)
    phone = StringField(max_length=20)
    dob = DateTimeField()
    gender = StringField(max_length=20)
    address = StringField()
    cgpa = FloatField(default=0.0)
    batch_year = IntField()
    backlogs = IntField(default=0)
    skills = ListField(StringField(max_length=100), default=list)
    projects = ListField(EmbeddedDocumentField(ProjectEntry), default=list)
    certifications = ListField(EmbeddedDocumentField(CertificationEntry), default=list)
    internships = ListField(EmbeddedDocumentField(InternshipEntry), default=list)
    github_url = URLField()
    linkedin_url = URLField()
    photo_path = StringField()
    resume_path = StringField()
    is_verified = BooleanField(default=False)
    profile_complete = IntField(default=0)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'student_profiles',
        'indexes': ['user', 'university', 'cgpa', 'batch_year'],
    }

    def compute_completeness(self):
        """Compute profile completeness as a percentage (0-100)."""
        fields = [
            self.first_name, self.last_name, self.phone, self.cgpa,
            self.batch_year, self.skills, self.resume_path, self.photo_path,
            self.github_url, self.linkedin_url,
        ]
        filled = sum(1 for f in fields if f)
        self.profile_complete = int((filled / len(fields)) * 100)
        return self.profile_complete

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        self.compute_completeness()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


# ─────────────────────────────────────────────────────────────
#  JOB
# ─────────────────────────────────────────────────────────────
class Job(Document):
    company = ReferenceField(CompanyProfile, required=True, reverse_delete_rule=CASCADE)
    title = StringField(required=True, max_length=300)
    description = StringField(required=True)
    skills_required = ListField(StringField(max_length=100), default=list)
    ctc = StringField(max_length=100)
    location = StringField(max_length=200)
    job_type = StringField(choices=JobType.CHOICES, default=JobType.FULL_TIME)
    eligibility = EmbeddedDocumentField(EligibilityCriteria, default=EligibilityCriteria)
    application_deadline = DateTimeField()
    status = StringField(choices=JobStatus.CHOICES, default=JobStatus.OPEN)
    openings = IntField(default=1)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'jobs',
        'indexes': ['company', 'status', 'job_type', '-created_at'],
        'ordering': ['-created_at'],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────
#  PLACEMENT DRIVE
# ─────────────────────────────────────────────────────────────
class PlacementDrive(Document):
    university = ReferenceField(UniversityProfile, required=True)
    company = ReferenceField(CompanyProfile, required=True)
    job = ReferenceField(Job)
    title = StringField(max_length=300, required=True)
    drive_date = DateTimeField()
    venue = StringField(max_length=300)
    eligibility = EmbeddedDocumentField(EligibilityCriteria, default=EligibilityCriteria)
    rounds = ListField(EmbeddedDocumentField(DriveRound), default=list)
    status = StringField(choices=DriveStatus.CHOICES, default=DriveStatus.SCHEDULED)
    description = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'placement_drives',
        'indexes': ['university', 'company', 'status'],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────
#  APPLICATION
# ─────────────────────────────────────────────────────────────
class Application(Document):
    job = ReferenceField(Job, required=True, reverse_delete_rule=CASCADE)
    student = ReferenceField(StudentProfile, required=True)
    drive = ReferenceField(PlacementDrive)
    status = StringField(choices=ApplicationStatus.CHOICES, default=ApplicationStatus.APPLIED)
    status_history = ListField(EmbeddedDocumentField(ApplicationStatusEntry), default=list)
    cover_note = StringField()
    applied_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'applications',
        'indexes': ['job', 'student', 'status', '-applied_at'],
        'ordering': ['-applied_at'],
    }

    def update_status(self, new_status, note=''):
        self.status = new_status
        self.status_history.append(ApplicationStatusEntry(
            status=new_status,
            timestamp=datetime.datetime.utcnow(),
            note=note
        ))
        self.updated_at = datetime.datetime.utcnow()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────
#  INTERVIEW
# ─────────────────────────────────────────────────────────────
class Interview(Document):
    application = ReferenceField(Application, required=True, reverse_delete_rule=CASCADE)
    round_name = StringField(max_length=100)
    scheduled_at = DateTimeField()
    mode = StringField(choices=InterviewMode.CHOICES, default=InterviewMode.ONLINE)
    link_or_venue = StringField(max_length=500)
    result = StringField()
    feedback = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'interviews',
        'indexes': ['application'],
    }


# ─────────────────────────────────────────────────────────────
#  OFFER
# ─────────────────────────────────────────────────────────────
class Offer(Document):
    application = ReferenceField(Application, required=True, reverse_delete_rule=CASCADE)
    ctc_offered = StringField(max_length=100)
    offer_letter_path = StringField()
    joining_date = DateTimeField()
    student_response = StringField(
        choices=['PENDING', 'ACCEPTED', 'DECLINED'],
        default='PENDING'
    )
    responded_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'offers',
        'indexes': ['application'],
    }


# ─────────────────────────────────────────────────────────────
#  NOTIFICATION
# ─────────────────────────────────────────────────────────────
class Notification(Document):
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    title = StringField(required=True, max_length=300)
    message = StringField(required=True)
    notification_type = StringField(choices=NotificationType.CHOICES, default=NotificationType.SYSTEM)
    link = StringField(max_length=500)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'notifications',
        'indexes': ['user', 'is_read', '-created_at'],
        'ordering': ['-created_at'],
    }

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────
#  ANNOUNCEMENT
# ─────────────────────────────────────────────────────────────
class Announcement(Document):
    sender = ReferenceField(User, required=True)
    title = StringField(required=True, max_length=300)
    content = StringField(required=True)
    target_role = StringField(choices=Roles.CHOICES)
    target_university = ReferenceField(UniversityProfile)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'announcements',
        'indexes': ['target_role', '-created_at'],
        'ordering': ['-created_at'],
    }


# ─────────────────────────────────────────────────────────────
#  ACTIVITY LOG
# ─────────────────────────────────────────────────────────────
class ActivityLog(Document):
    user = ReferenceField(User)
    action = StringField(required=True, max_length=300)
    details = StringField()
    ip_address = StringField(max_length=50)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'activity_logs',
        'indexes': ['user', '-timestamp'],
        'ordering': ['-timestamp'],
    }

    def __str__(self):
        return f"{self.action} by {self.user}"

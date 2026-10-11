# PlacePro – Placement Management Platform

PlacePro is a full-featured campus placement management and recruitment portal connecting **Students**, **Universities (Training & Placement Cells)**, and **Corporate Recruiters**, moderated by a central **Administrator**.

---

## 🛠 Tech Stack

- **Backend Framework:** Django 5.0
- **Primary Database:** MongoDB (via MongoEngine)
- **Session & Auth Cache:** SQLite (Django sessions)
- **Frontend / Styling:** Vanilla CSS Design System (`static/css/style.css`), Bootstrap 5, FontAwesome 6, Chart.js
- **Environment Management:** `django-environ`, `python-dotenv`

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- MongoDB Community Server running locally on `localhost:27017`

### 2. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Run Migrations & Check
```powershell
python manage.py migrate
python manage.py check
```

### 4. Seed Demo Data
Populate the database with universities, companies, student candidates, jobs, campus placement drives, and application lifecycles:
```powershell
python manage.py seed_demo_data
```

### 5. Start Development Server
```powershell
python manage.py runserver
```
Visit: [http://localhost:8000](http://localhost:8000)

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Access Portal |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@placepro.com` | `admin123` | `/admin-panel/dashboard/` |
| **University TPO** | `apex.admin@apex.edu` | `apex123` | `/university/dashboard/` |
| **Company Recruiter** | `recruiter@google.com` | `google123` | `/company/dashboard/` |
| **Student** | `rahul@apex.edu` | `student123` | `/student/dashboard/` |

---

## 🌟 Modules & Features

### 1. Admin Control Center (`/admin-panel/`)
- Platform-wide KPI counters and placement charts (Chart.js)
- Verification & moderation of universities and corporate recruiters
- User account management (block/unblock/delete)
- Job postings moderation
- Filterable application reports with CSV export
- System-wide broadcast announcements and security audit trails

### 2. University TPO Portal (`/university/`)
- Dashboard tracking total placements and departmental conversion rates
- Academic department and branch management
- Student directory with eligibility verification
- Bulk student onboarding via CSV file import
- Campus placement drive organization with round tracking
- University placement compliance report export (CSV)

### 3. Corporate Recruiter Portal (`/company/`)
- Job posting manager with criteria (min CGPA, max backlogs, batches)
- Applicant Tracking System (ATS) with status pipeline (Shortlisted, Interview, Selected, Rejected)
- Interview scheduling with date/time, mode (online/offline), and meeting links
- Official offer letter generator with salary/CTC and joining dates
- Applicant list export to CSV

### 4. Student Career Hub (`/student/`)
- Dynamic dashboard with profile completion indicator and recommendation engine
- Comprehensive profile editor with resume upload (PDF), GitHub, LinkedIn, skills, and projects
- Job search with eligibility matching
- One-click application with cover note
- Multi-stage timeline tracking for all submitted applications
- Job offer acceptance / decline portal

### 5. Public & Auth
- Modern responsive landing page showcasing live platform stats
- Public job directory
- Secure role-based authentication, registration forms, and password reset flows
- Notification inbox

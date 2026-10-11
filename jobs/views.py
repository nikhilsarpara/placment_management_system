"""Jobs app views (shared public-facing job listing)."""
from django.shortcuts import render
from core.models import Job, JobStatus


def job_list(request):
    """Public job board (no auth required)."""
    jobs = Job.objects(status=JobStatus.OPEN).order_by('-created_at')
    return render(request, 'jobs/public_list.html', {'jobs': jobs})

"""URL patterns for jobs app."""
from django.urls import path
from jobs import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
]

"""URL patterns for companies app."""
from django.urls import path
from companies import views

app_name = 'companies'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('jobs/', views.job_list, name='jobs'),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/<str:job_id>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<str:job_id>/close/', views.close_job, name='close_job'),
    path('jobs/<str:job_id>/applicants/', views.applicant_list, name='job_applicants'),
    path('jobs/<str:job_id>/export/', views.export_applicants, name='export_applicants'),
    path('applicants/', views.applicant_list, name='applicants'),
    path('applicants/<str:app_id>/status/', views.update_application_status, name='update_status'),
    path('applicants/<str:app_id>/interview/', views.schedule_interview, name='schedule_interview'),
    path('applicants/<str:app_id>/offer/', views.send_offer, name='send_offer'),
]

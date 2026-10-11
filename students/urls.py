"""URL patterns for students app."""
from django.urls import path
from students import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('jobs/', views.job_list, name='jobs'),
    path('jobs/<str:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<str:job_id>/apply/', views.apply_job, name='apply_job'),
    path('applications/', views.my_applications, name='applications'),
    path('applications/<str:app_id>/', views.application_detail, name='application_detail'),
    path('offers/', views.my_offers, name='offers'),
    path('offers/<str:offer_id>/respond/', views.respond_offer, name='respond_offer'),
]

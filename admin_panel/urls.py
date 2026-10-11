"""URL patterns for admin_panel app."""
from django.urls import path
from admin_panel import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    # University management
    path('universities/', views.university_list, name='university_list'),
    path('universities/<str:uni_id>/approve/', views.approve_university, name='approve_university'),
    path('universities/<str:uni_id>/reject/', views.reject_university, name='reject_university'),
    path('universities/<str:uni_id>/suspend/', views.suspend_university, name='suspend_university'),
    # Company management
    path('companies/', views.company_list, name='company_list'),
    path('companies/<str:company_id>/approve/', views.approve_company, name='approve_company'),
    path('companies/<str:company_id>/reject/', views.reject_company, name='reject_company'),
    path('companies/<str:company_id>/suspend/', views.suspend_company, name='suspend_company'),
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/<str:user_id>/block/', views.block_user, name='block_user'),
    path('users/<str:user_id>/unblock/', views.unblock_user, name='unblock_user'),
    path('users/<str:user_id>/delete/', views.delete_user, name='delete_user'),
    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<str:job_id>/close/', views.close_job, name='close_job'),
    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_report_csv, name='export_report'),
    # Announcements
    path('announcements/', views.announcements, name='announcements'),
    # Activity logs
    path('logs/', views.activity_logs, name='activity_logs'),
]

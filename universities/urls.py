"""URL patterns for universities app."""
from django.urls import path
from universities import views

app_name = 'universities'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('departments/', views.department_list, name='departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<str:dept_id>/delete/', views.delete_department, name='delete_department'),
    path('students/', views.student_list, name='students'),
    path('students/bulk-upload/', views.bulk_upload_students, name='bulk_upload'),
    path('students/<str:student_id>/verify/', views.verify_student, name='verify_student'),
    path('drives/', views.drive_list, name='drives'),
    path('drives/create/', views.create_drive, name='create_drive'),
    path('drives/<str:drive_id>/', views.drive_detail, name='drive_detail'),
    path('reports/', views.placement_report, name='reports'),
    path('announce/', views.send_announcement, name='announce'),
]

"""URL patterns for the accounts app."""
from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/university/', views.register_university, name='register_university'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/student/', views.register_student, name='register_student'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
]

"""URL patterns for notifications app."""
from django.urls import path
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('<str:notif_id>/read/', views.mark_read, name='mark_read'),
]

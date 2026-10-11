"""URL patterns for core app."""
from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.landing_page, name='landing'),
]

"""
Root URL configuration for placement_management project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),                        # Landing page
    path('accounts/', include('accounts.urls')),           # Auth: login, logout, register, reset
    path('admin-panel/', include('admin_panel.urls')),     # Admin dashboard
    path('university/', include('universities.urls')),     # University module
    path('company/', include('companies.urls')),           # Company module
    path('student/', include('students.urls')),            # Student module
    path('jobs/', include('jobs.urls')),                   # Job listings (shared)
    path('notifications/', include('notifications.urls')), # Notifications
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

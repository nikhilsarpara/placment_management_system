"""Utility helpers shared across apps."""
import os
import uuid
from django.conf import settings
from core.models import ActivityLog, Notification, NotificationType


def save_uploaded_file(file_obj, subdir):
    """
    Save an uploaded file to MEDIA_ROOT/<subdir>/<uuid_filename>.
    Returns the relative path (from MEDIA_ROOT) or None if no file provided.
    Validates mime type and size.
    """
    if not file_obj:
        return None

    allowed_types = (
        settings.ALLOWED_UPLOAD_IMAGES + settings.ALLOWED_UPLOAD_DOCS
    )
    if hasattr(file_obj, 'content_type') and file_obj.content_type not in allowed_types:
        return None  # Silently skip invalid types (view should pre-validate)

    max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if file_obj.size > max_size:
        return None

    ext = os.path.splitext(file_obj.name)[1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(save_path, exist_ok=True)

    full_path = os.path.join(save_path, filename)
    with open(full_path, 'wb+') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    return os.path.join(subdir, filename).replace('\\', '/')


def log_activity(user, action, details='', ip_address=''):
    """Create an ActivityLog entry."""
    try:
        ActivityLog(
            user=user,
            action=action,
            details=details,
            ip_address=ip_address,
        ).save()
    except Exception:
        pass  # Never break the main flow for logging


def send_notification(user, title, message, notif_type=NotificationType.SYSTEM, link=''):
    """Create an in-app Notification for a user."""
    try:
        Notification(
            user=user,
            title=title,
            message=message,
            notification_type=notif_type,
            link=link,
        ).save()
    except Exception:
        pass


def get_unread_notification_count(user_id):
    """Return the count of unread notifications for a user by ID string."""
    from core.models import User, Notification
    try:
        user = User.objects.get(id=user_id)
        return Notification.objects(user=user, is_read=False).count()
    except Exception:
        return 0

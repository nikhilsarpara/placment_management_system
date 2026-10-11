"""Notifications app views."""
from django.shortcuts import render, redirect
from django.contrib import messages

from accounts.decorators import login_required, get_current_user
from core.models import User, Notification


@login_required
def notification_list(request):
    """View all notifications for the logged-in user."""
    user = get_current_user(request)
    notifications = Notification.objects(user=user).order_by('-created_at').limit(50)
    # Mark all as read
    Notification.objects(user=user, is_read=False).update(set__is_read=True)
    return render(request, 'notifications/list.html', {
        'notifications': notifications
    })


@login_required
def mark_read(request, notif_id):
    """Mark a single notification as read."""
    user = get_current_user(request)
    try:
        notif = Notification.objects.get(id=notif_id, user=user)
        notif.is_read = True
        notif.save()
    except Exception:
        pass
    return redirect(request.META.get('HTTP_REFERER', '/'))

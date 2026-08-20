from .models import Notification

def user_notifications(request):
    if request.user.is_authenticated:
        # Get up to 5 unread notifications for the dropdown
        unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False)[:5]
        # Get the total number to show in the little red badge
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {
            'unread_notifications': unread_notifications,
            'unread_count': unread_count
        }
    return {}
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def read_notification(request, notif_id):
    """Marks a single notification as read and redirects the user."""
    notification = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    # If the notification has a destination link, send them there
    if notification.link:
        return redirect(notification.link)
        
    # Fallback redirect if no link was provided when the notification was created
    if request.user.profile.role == 'instructor':
        return redirect('instructor_dashboard')
    return redirect('student_dashboard')

@login_required
def mark_all_notifications_read(request):
    """Instantly marks all of a user's notifications as read."""
    # .update() is a fast way to update multiple rows in the database at once!
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    messages.success(request, "All notifications marked as read.")
    
    # Redirect the user back to the exact page they were just on
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page:
        return redirect(previous_page)
        
    if request.user.profile.role == 'instructor':
        return redirect('instructor_dashboard')
    return redirect('student_dashboard')
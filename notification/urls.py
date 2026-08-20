from django.urls import path
from . import views

urlpatterns = [
    path('notifications/read/<int:notif_id>/', views.read_notification, name='read_notification'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='read_all_notifications'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name="instructor_dashboard"),
    path('settings/', views.settings_view, name='settings'),
    path('settings/delete-account/', views.delete_account, name='delete_account'),
    path('profile/', views.profile_view, name='profile'),
    path('instructor/profile/', views.instructor_profile_view, name='instructor_profile'),
]
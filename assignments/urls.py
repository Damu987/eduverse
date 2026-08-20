from django.urls import path
from . import views

urlpatterns = [
   # Instructor Assignment URLs
    path('courses/<int:course_id>/assignments/', views.manage_assignments, name="manage_assignments"),
    path('courses/<int:course_id>/assignments/create/', views.create_assignment, name="create_assignment"),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/edit/', views.edit_assignment, name="edit_assignment"),
    path('courses/<int:course_id>/assignments/<int:assignment_id>/delete/', views.delete_assignment, name="delete_assignment"),
    #grade assigning urls
    path('courses/<int:course_id>/assignments/<int:assignment_id>/submissions/', views.grade_submissions, name="grade_submissions"),
    #student assignment urls
    path('assignments/<int:assignment_id>/', views.submit_assignment, name="submit_assignment"),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
]
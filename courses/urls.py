from django.urls import path
from . import views

urlpatterns = [
    # Maps to www.eduverse.com/courses/
    #course crud
    path('courses/managecourses/', views.manage_courses, name='manage_courses'),
    path('courses/create/', views.create_course, name="create_course"),
    path('courses/<int:course_id>/edit/', views.edit_course, name="edit_course"),
    path("courses/<int:course_id>/delete/", views.delete_course, name="delete_course"),

   #lessons crud
    path('courses/<int:course_id>/lessons/', views.manage_lessons, name="manage_lessons"),
    path('courses/<int:course_id>/lessons/create/', views.create_lesson, name="create_lesson"),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/edit/', views.edit_lesson, name="edit_lesson"),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/delete/', views.delete_lesson, name="delete_lesson"),

    #course_details
    path('course/<int:course_id>/', views.course_details, name='course_details'),

    #enroll
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    #checkout
    path('course/<int:course_id>/checkout/', views.checkout, name='checkout'),
    path('course/<int:course_id>/process_payment/', views.process_payment, name="process_payment"), 
]
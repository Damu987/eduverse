from django.urls import path
from . import views

urlpatterns = [

       # Learning player routes
        path('course/<int:course_id>/learn/', views.start_learning, name='start_learning'),
        path('course/<int:course_id>/learn/<int:lesson_id>/', views.start_learning, name='start_learning_lesson'),
        #mark lesson progress
        path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name="mark_lesson_complete"),
    
        #student dashboard path
        path('student/dashboard/', views.student_dashboard, name="student_dashboard"),  
    
        #instructor dashboard
        path('instructor/dashboard/', views.instructor_dashboard, name="instructor_dashboard"), 

        #student_management
        path('instructor/students/', views.student_management, name='student_management'),
         #analytics
        path('instructor/analytics/', views.instructor_analytics, name='instructor_analytics'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Instructor Quiz URLs
    path('courses/<int:course_id>/quizzes/', views.manage_quizzes, name="manage_quizzes"),
    path('courses/<int:course_id>/quizzes/create/', views.quiz_builder, name="create_quiz"),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/edit/', views.quiz_builder, name="edit_quiz"),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/delete/', views.delete_quiz, name="delete_quiz"),

    #student quiz taker
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/take/', views.take_quiz, name="take_quiz"),

    # Instructor URL
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/results/', views.instructor_quiz_results, name="instructor_quiz_results"),
    
    # Student URL 
    path('student/quizzes/', views.student_quiz_history, name="student_quizzes"),
    
]

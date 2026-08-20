from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import instructor_required
from django.db.models import Sum, Count, Avg
from courses.models import Course, Lesson, Enrollment
from quizzes.models import QuizSubmission, Quiz
from assignments.models import Assignment, AssignmentSubmission
from .models import LessonProgress
from certificate.models import Certificate
from notification.models import Notification
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

# Create your views here.

#--------------------------- START LEARNING ------------------
@login_required
def start_learning(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id, published=True)
    
    # 1. Verify Enrollment
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled and course.instructor != request.user:
        messages.error(request, "You must enroll in this course first.")
        return redirect("course_details", course_id=course.id)

    lessons = course.lessons.all().order_by('order')
    if not lessons.exists():
        messages.warning(request, "No lessons available yet.")
        return redirect('course_details', course_id=course.id)

    # 2. Determine Current Lesson
    if lesson_id:
        current_lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    else:
        current_lesson = lessons.first()

    # 3. Safe Progress Handling (Won't crash if LessonProgress table is empty or missing)
    completed_lesson_ids = []
    try:
        completed_lesson_ids = list(LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course,
            completed=True
        ).values_list('lesson_id', flat=True))
    except Exception:
        pass

    total_lessons = lessons.count()
    completed_count = len(completed_lesson_ids)
    progress_percentage = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0

    # 4. Find Next and Previous Lessons 
    previous_lesson = lessons.filter(order__lt=current_lesson.order).order_by('-order').first()
    next_lesson = lessons.filter(order__gt=current_lesson.order).order_by('order').first()

    # 5. Safe Quiz Handling
    quizzes = []
    completed_quiz_ids = []
    try:
        quizzes = course.quizzes.all().order_by('created_at')
        completed_quiz_ids = list(QuizSubmission.objects.filter(
            student=request.user, quiz__course=course
        ).values_list('quiz_id', flat=True))
    except Exception:
        pass

    return render(request, 'student/lesson.html', {
        'course': course,
        'lessons': lessons,
        'current_lesson': current_lesson,
        'completed_lesson_ids': completed_lesson_ids,
        'progress_percentage': progress_percentage,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'is_completed': current_lesson.id in completed_lesson_ids,
        'quizzes': quizzes,
        'completed_quiz_ids': completed_quiz_ids,
    })

#--------------------- MARK LESSON COMPLETE ------------------
@login_required
def mark_lesson_complete(request, lesson_id):
    if request.method == "POST":
        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = Enrollment.objects.filter(student=request.user, course=lesson.course).first()
        
        if enrollment:
            # 1. Mark this specific lesson as complete
            progress, created = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)
            if not progress.completed:
                progress.completed = True
                progress.completed_at = timezone.now()
                progress.save()

            # 2. Check for 100% Course Completion
            total_lessons = lesson.course.lessons.count()
            completed_lessons = LessonProgress.objects.filter(
                student=request.user, 
                lesson__course=lesson.course, 
                completed=True
            ).count()

            # If all lessons are done and the enrollment wasn't already marked complete
            if total_lessons > 0 and completed_lessons == total_lessons and not enrollment.completed:
                enrollment.completed = True
                enrollment.save()
                
                # Generate the Certificate automatically!
                cert, created_cert = Certificate.objects.get_or_create(student=request.user, course=lesson.course)
                
                # NEW: Send a notification to the student!
                if created_cert:
                    Notification.objects.create(
                        recipient=request.user,
                        title="Course Completed! 🎓",
                        message=f"Congratulations! You've finished '{lesson.course.title}' and earned your certificate.",
                        link="/student/certificates/" # Links them directly to their certificates page
                    )
                    messages.success(request, "Course Completed! Your certificate has been generated.")

            # 3. Redirect to the next lesson or stay on current if finished
            next_lesson = lesson.course.lessons.filter(order__gt=lesson.order).order_by('order').first()
            if next_lesson:
                return redirect('start_learning_lesson', course_id=lesson.course.id, lesson_id=next_lesson.id)
            else:
                return redirect('start_learning_lesson', course_id=lesson.course.id, lesson_id=lesson.id)
                
    return redirect('course_catalog')


@instructor_required
def student_management(request):
    instructor = request.user
    
    # Get all enrollments for courses taught by this instructor
    # select_related optimizes the database query!
    enrollments = Enrollment.objects.filter(
        course__instructor=instructor
    ).select_related('student', 'course').order_by('-enrolled_at')
    
    student_data = []
    for enrollment in enrollments:
        course = enrollment.course
        student = enrollment.student
        
        # Calculate progress
        total_lessons = course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            student=student,
            lesson__course=course,
            completed=True
        ).count()
        
        progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        
        student_data.append({
            'enrollment': enrollment,
            'student': student,
            'course': course,
            'progress': progress,
        })
        
    return render(request, 'instructor/student_management.html', {
        'student_data': student_data
    })

#------------------------------STUDENT DASHOBARD--------------------------
@login_required
def student_dashboard(request):
    student = request.user
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    # 1. Top Metrics
    total_courses = enrollments.count()
    completed_courses = enrollments.filter(completed=True).count()
    total_certificates = Certificate.objects.filter(student=student).count()
    
    # 2. Upcoming Tasks (Pending Assignments)
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    submitted_assignment_ids = AssignmentSubmission.objects.filter(student=student).values_list('assignment_id', flat=True)
    
    pending_assignments = Assignment.objects.filter(
        course__id__in=enrolled_course_ids
    ).exclude(
        id__in=submitted_assignment_ids
    ).order_by('due_date')[:5]

    # 3. Recent Activity (Last 5 completed lessons)
    recent_lessons = LessonProgress.objects.filter(
        student=student, 
        completed=True
    ).select_related('lesson__course').order_by('-completed_at')[:5]
    
    return render(request, 'student/dashboard.html', {
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'total_certificates': total_certificates,
        'pending_assignments': pending_assignments,
        'recent_lessons': recent_lessons,
        'recent_enrollments': enrollments[:3] # Show up to 3 active courses
    })

#----------------------------Instructor dashboard---------------------
@instructor_required
def instructor_dashboard(request):
    instructor = request.user
    
    # Courses created by this instructor
    courses = Course.objects.filter(instructor=instructor)
    
    # Statistics
    total_courses = courses.count()
    published_courses = courses.filter(published=True).count()
    draft_courses = courses.filter(published=False).count()

    # Count assignments that have been submitted but NOT graded yet
    pending_reviews = AssignmentSubmission.objects.filter(
        assignment__course__in=courses, 
        is_graded=False
    ).count()

    # Recent Students (Last 5 enrollments)
    recent_enrollments = Enrollment.objects.filter(
        course__in=courses
    ).select_related('student', 'course').order_by('-enrolled_at')[:5]

    # course_instructor
    total_students = Enrollment.objects.filter(course__instructor=instructor).values("student").distinct().count()
    
    # Course-wise statistics
    course_data = []
    for course in courses:
        student_count = Enrollment.objects.filter(course=course).count()
        lesson_count = course.lessons.count()
        course_data.append({
            'course': course,
            'student_count': student_count,
            'lesson_count': lesson_count,
        })

    context = {
        "total_courses": total_courses,
        "published_courses": published_courses,
        "draft_courses": draft_courses,
        'total_students': total_students,
        'course_data': course_data,
        'pending_reviews': pending_reviews,
        'recent_enrollments': recent_enrollments,
    }
    return render(request, 'instructor/dashboard.html', context)

#---------------------ANALYTICS- view ---------------------
@instructor_required
def instructor_analytics(request):
    instructor = request.user
    instructor_courses = Course.objects.filter(instructor=instructor)
    
    # 1. Financial Analytics (Total Revenue simulated by multiplying price with enrollments)
    total_enrollments = Enrollment.objects.filter(course__instructor=instructor)
    
    # Calculate total earnings (sum of course prices for all active enrollments)
    total_revenue = sum(enrollment.course.price for enrollment in total_enrollments)
    
    # 2. Key Performance Metrics
    total_courses = instructor_courses.count()
    published_courses = instructor_courses.filter(published=True).count()
    unique_students = total_enrollments.values('student').distinct().count()
    
    # 3. Completion Analytics
    completed_enrollments = total_enrollments.filter(completed=True).count()
    overall_completion_rate = int((completed_enrollments / total_enrollments.count()) * 100) if total_enrollments.count() > 0 else 0

    # 4. Course-wise breakdown for analytics table
    course_analytics = []
    for course in instructor_courses:
        c_enrollments = Enrollment.objects.filter(course=course)
        c_revenue = sum(e.course.price for e in c_enrollments)
        c_completed = c_enrollments.filter(completed=True).count()
        c_rate = int((c_completed / c_enrollments.count()) * 100) if c_enrollments.count() > 0 else 0
        
        course_analytics.append({
            'course': course,
            'enrollments': c_enrollments.count(),
            'revenue': c_revenue,
            'completion_rate': c_rate,
        })

    context = {
        'total_revenue': total_revenue,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'unique_students': unique_students,
        'overall_completion_rate': overall_completion_rate,
        'course_analytics': course_analytics,
    }
    
    return render(request, 'instructor/analytics.html', context)



@staff_member_required
def admin_dashboard(request):
    # 1. Platform-wide Statistics
    total_users = User.objects.count()
    total_students = User.objects.filter(is_staff=False).count()
    total_instructors = User.objects.filter(is_staff=True).count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    # Calculate global platform revenue
    total_revenue = sum(enrollment.course.price for enrollment in Enrollment.objects.select_related('course'))

    # 2. Recent Users & Recent Courses
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_courses = Course.objects.select_related('instructor').order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_revenue': total_revenue,
        'recent_users': recent_users,
        'recent_courses': recent_courses,
    }
    
    return render(request, 'admin/custom_dashboard.html', context)
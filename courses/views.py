from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, CourseOutcome, CourseRequirement, Lesson, Enrollment
from .forms import CourseForm, LessonForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from accounts.decorators import instructor_required
from notification.models import Notification

# --- HELPER FUNCTIONS ---
def _save_course_metadata(request, course):
    """Helper to cleanly save outcomes and requirements, avoiding repetition."""
    # Delete old ones first (useful for edits; harmless for creations)
    course.outcomes.all().delete()
    course.requirements.all().delete()

    outcomes = request.POST.getlist('outcomes[]')
    requirements = request.POST.getlist('requirements[]')

    for outcome in outcomes:
        if outcome.strip():
            CourseOutcome.objects.create(course=course, text=outcome.strip())

    for req in requirements:
        if req.strip():
            CourseRequirement.objects.create(course=course, text=req.strip())


# --- CUSTOM DECORATOR ---
def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check if user has an instructor or admin role via UserProfile
        has_permission = False
        if request.user.is_superuser:
            has_permission = True
        elif hasattr(request.user, 'profile') and request.user.profile.role in ['instructor', 'admin']:
            has_permission = True
            
        if not has_permission:
            messages.error(request, "You are authenticated, but are not authorized to access the instructor portal.")
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --------- CRUD OPERATIONS FOR COURSE -----------------------
@instructor_required
def manage_courses(request):
    courses = Course.objects.filter(instructor=request.user).order_by("-created_at")
    return render(request, 'instructor/managecourses.html', {
        'courses': courses,
        'total_courses': courses.count(),
        'published_courses': courses.filter(published=True).count(),
        'draft_courses': courses.filter(published=False).count(),
    })

@csrf_exempt
@instructor_required
def create_course(request):
    form = CourseForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST" and form.is_valid():
        course = form.save(commit=False)
        course.instructor = request.user
        course.save()
        messages.success(request, 'Course created successfully.')
        return redirect("manage_courses")

    return render(request, 'instructor/createcourse.html', {'form': form})

@csrf_exempt
@instructor_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    
    if request.method == "POST":
        if form.is_valid():
            course = form.save()
            
            # Safely update requirements using the related_name='requirements'
            requirements = request.POST.getlist('requirements[]')
            if requirements:
                course.requirements.all().delete()
                for req in requirements:
                    if req.strip():
                        CourseRequirement.objects.create(course=course, text=req.strip())
                        
            # Safely update outcomes using the related_name='outcomes'
            outcomes = request.POST.getlist('outcomes[]')
            if outcomes:
                course.outcomes.all().delete()
                for outcome in outcomes:
                    if outcome.strip():
                        CourseOutcome.objects.create(course=course, text=outcome.strip())

            messages.success(request, 'Course updated successfully.')
            return redirect("manage_courses")
        else:
            print(form.errors) # Prints validation issues to your terminal if form fails

    return render(request, 'instructor/editcourse.html', {'form': form, 'course': course})

@instructor_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == "POST":
        course.delete()
        messages.success(request, 'Course deleted.')
    return redirect("manage_courses")

# ------------------ CRUD OPERATIONS FOR LESSON ---------------------

@instructor_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    return render(request, 'instructor/managelessons.html', {
        "course": course,
        "lessons": course.lessons.all().order_by("order")
    })

@csrf_exempt
@instructor_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    form = LessonForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST" and form.is_valid():
        lesson = form.save(commit=False)
        lesson.course = course
        lesson.save()
        messages.success(request, 'Lesson added successfully.')
        return redirect("manage_lessons", course_id=course.id)

    # FIX: Render lesson_form instead of managelessons when showing the form or handling errors
    return render(request, "instructor/lesson_form.html", {"form": form, "course": course})

@csrf_exempt
@instructor_required
def edit_lesson(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    form = LessonForm(request.POST or None, request.FILES or None, instance=lesson)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lesson updated successfully.')
        return redirect("manage_lessons", course_id=course.id)

    return render(request, "instructor/lesson_form.html", {"form": form, "course": course, "lesson": lesson})

@instructor_required
def delete_lesson(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, 'Lesson deleted.')
    return redirect("manage_lessons", course_id=course.id)


# --- HELPER FUNCTION FOR NOTIFICATIONS ---
def _trigger_enrollment_notifications(student, course):
    """Sends a notification to both the student and the instructor upon enrollment."""
    # 1. Notify the Student
    Notification.objects.create(
        recipient=student,
        title="Enrollment Successful!",
        message=f"You are now enrolled in '{course.title}'. Happy learning!",
        link=f"/student/dashboard/" # Redirects to their dashboard when clicked
    )
    # 2. Notify the Instructor
    Notification.objects.create(
        recipient=course.instructor,
        title="New Student Enrolled!",
        message=f"{student.first_name or student.username} just enrolled in '{course.title}'.",
        link="/instructor/dashboard/"
    )

#------------------- COURSE DETAILS -------------------------
@login_required
def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id, published=True)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    return render(request, 'student/course-details.html', {
        "course": course,
        "enrollment": enrollment,
    })

#----------------------ENROLLMENT PROCESS------------------------------
@login_required
def enroll_course(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(Course, id=course_id, published=True)
        
        # Use get_or_create to check if they are already enrolled
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        
        if created:
            # Trigger our notification helper!
            _trigger_enrollment_notifications(request.user, course)
        
        messages.success(request, f"Successfully enrolled in {course.title}! You can start learning now.")
        # Redirect them straight to the learning player!
        return redirect('start_learning', course_id=course.id)
        
    return redirect('course_details', course_id=course_id)

#----------------------------- CHECKOUT ---------------------------
@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id, published=True)

    # Prevent instructors from enrolling in their own course
    if course.instructor == request.user:
        messages.warning(request, "You cannot enroll in a course you teach.")
        return redirect('course_details', course_id=course.id)

    # Check if student is already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return redirect('course_details', course_id=course.id)

    # If the course is free, enroll instantly and skip payment page
    if course.price == 0:
        # BUG FIX: changed 'curse=course' to 'course=course'
        Enrollment.objects.create(student=request.user, course=course)
        
        # Trigger our notification helper!
        _trigger_enrollment_notifications(request.user, course)
        
        messages.success(request, f'Successfully enrolled in {course.title}!')
        return redirect('start_learning', course_id=course.id)

    # If paid, send them to checkout page
    return render(request, 'student/checkout.html', {'course': course})

#--------------------------- PAYMENT ---------------------
@login_required
def process_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id, published=True)

    if request.method == 'POST':
        # For now, simulate a successful payment
        # We use get_or_create to prevent IntegrityErrors
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )

        if created:
            # Trigger our notification helper!
            _trigger_enrollment_notifications(request.user, course)
            messages.success(request, "Payment successful! You can now start learning.")
            return redirect('start_learning', course_id=course.id)

        return redirect('course_details', course_id=course.id)
        
    return redirect("checkout", course_id=course.id)



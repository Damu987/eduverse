from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import instructor_required
from .models import Assignment, AssignmentSubmission
from .forms import AssignmentForm, SubmissionForm
from courses.models import Enrollment, Course

# ------------------- ASSIGNMENT CRUD BY INSTRUCTOR -----------------

@instructor_required
def manage_assignments(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    return render(request, 'instructor/manage_assignments.html', {
        'course': course, 
        'assignments': course.assignments.all().order_by('due_date')
    })

@instructor_required 
def create_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    form = AssignmentForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        assignment.course = course
        assignment.save()
        messages.success(request, 'Assignment created successfully.')
        return redirect('manage_assignments', course_id=course.id)

    return render(request, 'instructor/assignment_form.html', {'form': form, 'course': course})

@instructor_required
def edit_assignment(request, course_id, assignment_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    form = AssignmentForm(request.POST or None, instance=assignment)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, 'Assignment updated successfully.')
        return redirect('manage_assignments', course_id=course.id)

    return render(request, 'instructor/assignment_form.html', {'form': form, 'course': course, 'assignment': assignment})

@instructor_required 
def delete_assignment(request, course_id, assignment_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted.')
        
    return redirect('manage_assignments', course_id=course.id)

@instructor_required
def grade_submissions(request, course_id, assignment_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    
    if request.method == "POST":
        submission = get_object_or_404(AssignmentSubmission, id=request.POST.get('submission_id'), assignment=assignment)
        marks = request.POST.get('marks_awarded')
        
        if marks:
            submission.marks_awarded = int(marks)
            submission.feedback = request.POST.get('feedback')
            submission.is_graded = True
            submission.save()
            student_name = submission.student.first_name or submission.student.username
            messages.success(request, f"Successfully graded {student_name}'s assignment.")
        else:
            messages.error(request, "You must provide a mark to grade the submission.")
        return redirect('grade_submissions', course_id=course.id, assignment_id=assignment.id)

    return render(request, 'instructor/grade_submissions.html', {
        'course': course,
        'assignment': assignment,
        'submissions': assignment.submissions.select_related('student').order_by('-submitted_at')
    })

# ------------------- STUDENT ASSIGNMENT SUBMISSION -----------------

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Verify enrollment directly in the query (faster)
    if not Enrollment.objects.filter(student=request.user, course=assignment.course).exists():
        messages.error(request, "You must be enrolled to view assignments.")
        return redirect('course_catalog')

    submission = AssignmentSubmission.objects.filter(student=request.user, assignment=assignment).first()
    
    # Allow request.FILES to pass through properly for file uploads
    form = SubmissionForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if submission:
            messages.warning(request, "You have already submitted this assignment.")
        elif form.is_valid():
            new_submission = form.save(commit=False)
            new_submission.student = request.user
            new_submission.assignment = assignment
            new_submission.save()
            messages.success(request, 'Assignment submitted successfully')
        return redirect('submit_assignment', assignment_id=assignment.id)

    return render(request, 'student/assignment.html', {
        'assignment': assignment,
        'course': assignment.course,
        'form': form,
        'submission': submission,
    })
#-------------------------studetn assignment---------------------------
@login_required
def student_assignments(request):
    # 1. Get all courses the current student is enrolled in
    enrolled_courses = Enrollment.objects.filter(student=request.user).values_list('course', flat=True)
    
    # 2. Get all assignments for those enrolled courses, ordered by due date
    assignments = Assignment.objects.filter(course__in=enrolled_courses).select_related('course').order_by('due_date')
    
    # 3. Get IDs of assignments the student has already submitted
    submitted_assignment_ids = AssignmentSubmission.objects.filter(
        student=request.user
    ).values_list('assignment_id', flat=True)

    return render(request, 'student/assignment.html', {
        'assignments': assignments,
        'submitted_assignment_ids': submitted_assignment_ids,
    })
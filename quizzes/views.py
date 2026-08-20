import json
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import instructor_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quiz, Question, Choice, QuizSubmission
from courses.models import Course, Enrollment

# 1. Manage Quizzes (Table View)
@instructor_required
def manage_quizzes(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    quizzes = course.quizzes.all().order_by('-created_at')
    
    return render(request, 'instructor/manage_quizzes.html', {
        'course': course,
        'quizzes': quizzes
    })

# 2. All-In-One Quiz Builder (Create & Edit)
@instructor_required
def quiz_builder(request, course_id, quiz_id=None):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    quiz = None
    questions_json = "[]" # Default empty array for JS

    # If a quiz_id is provided, we are editing an existing quiz
    if quiz_id:
        quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
        
        # Package existing questions into JSON for the JavaScript builder
        q_list = []
        for q in quiz.questions.all():
            c_list = []
            correct_idx = 0
            for idx, c in enumerate(q.choices.all()):
                c_list.append(c.text)
                if c.is_correct:
                    correct_idx = idx
            q_list.append({
                'text': q.text,
                'marks': q.marks,
                'choices': c_list,
                'correctIndex': correct_idx
            })
        questions_json = json.dumps(q_list)

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        questions_data = request.POST.get('questions_data') # The hidden JSON field

        # Save the main Quiz object
        if quiz:
            quiz.title = title
            quiz.description = description
            quiz.save()
            quiz.questions.all().delete() # Clear old questions to replace them
        else:
            quiz = Quiz.objects.create(course=course, title=title, description=description)

        # Parse the JSON and save Questions and Choices
        if questions_data:
            data = json.loads(questions_data)
            for q_data in data:
                new_q = Question.objects.create(quiz=quiz, text=q_data['text'], marks=q_data['marks'])
                
                for idx, choice_text in enumerate(q_data['choices']):
                    # Only save choice if text is provided
                    if choice_text.strip():
                        is_correct = (idx == int(q_data['correctIndex']))
                        Choice.objects.create(question=new_q, text=choice_text, is_correct=is_correct)

        messages.success(request, "Quiz saved successfully!")
        return redirect('manage_quizzes', course_id=course.id)

    return render(request, 'instructor/quiz_builder.html', {
        'course': course,
        'quiz': quiz,
        'questions_json': questions_json
    })

# 3. Delete Quiz
@instructor_required
def delete_quiz(request, course_id, quiz_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    if request.method == "POST":
        quiz.delete()
        messages.success(request, "Quiz deleted successfully.")
    return redirect('manage_quizzes', course_id=course.id)


#------------------------------student quiz taker -----------------------------------
#quiz taker
@login_required
def take_quiz(request, course_id, quiz_id):
    course = get_object_or_404(Course, id=course_id, published=True)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    
    # Verify enrollment
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You must be enrolled to take quizzes.")
        return redirect('course_details', course_id=course.id)

    # Check if student already took this quiz
    submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).first()
    
    questions = quiz.questions.all().prefetch_related('choices')
    total_possible_marks = sum(q.marks for q in questions)

    if request.method == "POST" and not submission:
        total_score = 0
        
        # Grade the submission
        for question in questions:
            # The HTML inputs will be named 'question_1', 'question_2', etc.
            selected_choice_id = request.POST.get(f'question_{question.id}')
            
            if selected_choice_id:
                # Find the selected choice
                selected_choice = question.choices.filter(id=selected_choice_id).first()
                if selected_choice and selected_choice.is_correct:
                    total_score += question.marks
        
        # Calculate final percentage
        percentage = (total_score / total_possible_marks * 100) if total_possible_marks > 0 else 0
        passed = percentage >= 60.0 # Standard 60% pass mark

        # Save to database
        submission = QuizSubmission.objects.create(
            student=request.user,
            quiz=quiz,
            score=total_score,
            total_marks=total_possible_marks,
            percentage=percentage,
            passed=passed
        )
        
        messages.success(request, "Quiz submitted successfully!")
        return redirect('take_quiz', course_id=course.id, quiz_id=quiz.id)

    return render(request, 'student/take_quiz.html', {
        'course': course,
        'quiz': quiz,
        'questions': questions,
        'total_marks': total_possible_marks,
        'submission': submission,
    })


# --- INSTRUCTOR VIEW: See all student scores for a specific quiz ---
@instructor_required
def instructor_quiz_results(request, course_id, quiz_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    
    # Get all submissions for this quiz
    submissions = quiz.submissions.all().select_related('student').order_by('-percentage')
    
    return render(request, 'instructor/quiz_results.html', {
        'course': course,
        'quiz': quiz,
        'submissions': submissions
    })

# --- STUDENT VIEW: See personal quiz history ---
@login_required
def student_quiz_history(request):
    # Get all quizzes the student has taken across all courses
    submissions = QuizSubmission.objects.filter(student=request.user).select_related('quiz__course').order_by('-submitted_at')
    
    return render(request, 'student/quiz_history.html', {
        'submissions': submissions
    })
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):
    category_choices = [
        ("Programming", 'programming'),
        ('Web Development', 'web development'),
        ('Data Science', 'data science'),
    ]
    level_choices = [
        ('Beginner', 'beginner'),
        ('Intermediate', 'intermediate'),
        ('Advanced', 'advanced'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices = category_choices)
    description = models.TextField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = 'courses'
    )

    level = models.CharField(max_length=50, choices=level_choices)

    duration = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to="courses/", blank=True, null = True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title=models.CharField(max_length=200)
    description = models.TextField()
    video=models.FileField(upload_to="lessons/", blank=True, null=True)
    order=models.PositiveBigIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course"
            )
        ]
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class CourseOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='outcomes')
    text = models.CharField(max_length=255)
    def __str__(self):
        return self.text

class CourseRequirement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='requirements')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
from django.db import models
from courses.models import Lesson
from django.contrib.auth.models import User

# Create your models here.
class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return (
            f"{self.student.username} - "
            f"{self.lesson.title}"
        )
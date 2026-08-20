from django.db import models
import uuid
from courses.models import Course
from django.contrib.auth.models import User


# Create your models here.
class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Generates a unique 32-character ID automatically (e.g., a8f3b2c1...)
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        # A student can only get one certificate per course
        unique_together = ('student', 'course') 

    def __str__(self):
        return f"Certificate: {self.student.username} - {self.course.title}"
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    #1.define the available roles
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    #2.add the role field, defaulting to 'student'
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')

    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #get_role_display() will show 'Instructor' 
        return f'{self.user.username} - { self.get_role_display()}'

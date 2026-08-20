from django import forms
from .models import Course, Lesson

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields=[
            "title",
            'category',
            'description',
            'level',
            'duration',
            'price',
            'image',
            'published',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    "class": "form-control",
                    'placeholder': "Enter course title"
                }
            ),
            "category": forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Enter course description'
                }
            ),
            'level': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'duration': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: 12 Hours'
                }
            ),

            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter course price (e.g., 3500)',
                    'step': '0.01',
                    'min': '0'
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'published': forms.CheckboxInput(
                attrs={
                    "class": 'form-check-input'
                }
            ),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson  
        fields = [
            'title',
            'description',
            'video',
            'order',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Lesson title'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': "Enter lesson description"
                }
            ),
            'video': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'order': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1
                }
            ),
        }
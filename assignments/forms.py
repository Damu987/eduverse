from .models import Assignment, AssignmentSubmission
from django import forms

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields=['title', 'description', 'due_date', 'total_marks']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter assignment title'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Describe what the students need to do.'
                }
            ),
            'due-date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'total_marks': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1'
                }
            ),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['text_answer', 'file']
        widgets = {
            'text_answer': forms.Textarea(
                attrs = {
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Type your answer here (optional if attaching a file)'
                }
            ),
            'file': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

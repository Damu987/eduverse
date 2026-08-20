from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget = forms.PasswordInput)
    confirm_password = forms.CharField(widget = forms.PasswordInput)
    role = forms.ChoiceField(choices = UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        }

    def clean(self):
          cleaned_data = super().clean()
          password = cleaned_data.get('password')
          confirm_password = cleaned_data.get('confirm_password')
          
          if password and confirm_password:
              if password != confirm_password:
                  # ADDED 'confirm_password' as the first argument
                  self.add_error('confirm_password', "Passwords do not match.")
  
          #check if email is already taken
          email = cleaned_data.get('email')
          if User.objects.filter(email=email).exists():
              # ADDED 'email' as the first argument
              self.add_error('email', "This email is already registered.")
  
          return cleaned_data

    def save(self, commit=True):
        #save the User object, but don't hit the db yet (commit=False)
        user = super().save(commit=False)

        #split the fullname into first and last name for django
        name_parts = self.cleaned_data['full_name'].split(" ", 1)
        if len(name_parts) > 1:
            user.last_name = name_parts[1]

        #hash the password securely
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save() #save the user to db
            #create the UserProfile and attach the choosen role
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone_number = self.cleaned_data.get('phone', '')
            )
        return user
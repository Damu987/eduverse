from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .decorators import student_required, instructor_required, admin_required
from .models import UserProfile

# --- HELPER FUNCTIONS ---
def _update_user_data(request, user):
    """Helper to save duplicate profile update logic."""
    user.first_name = request.POST.get('first_name', user.first_name)
    user.last_name = request.POST.get('last_name', user.last_name)
    user.email = request.POST.get('email', user.email)
    user.save()
    
    user.profile.phone_number = request.POST.get('phone_number', user.profile.phone_number)
    user.profile.bio = request.POST.get('bio', user.profile.bio) # Safe for both roles
    if 'avatar' in request.FILES:
        user.profile.avatar = request.FILES['avatar']
    user.profile.save()

def _style_password_form(form):
    """Helper to add Bootstrap classes to Django forms."""
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control bg-light'
    return form

# --- AUTHENTICATION VIEWS ---
def register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        # 1. Don't commit yet so we can assign the role to the profile
        user = form.save(commit=False)
        user.save() # Save the user first to generate the user instance ID
        
        # 2. Get the role selected by the user from the POST request
        # (Assumes your form/dropdown field is named 'role')
        selected_role = request.POST.get('role')
        
        # 3. Update or create the profile with the selected role (default to 'guest' if empty)
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = selected_role if selected_role else 'guest'
        profile.save()
        
        messages.success(request, 'Account created successfully! You can log in.')
        return redirect('login')
        
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            
            # NEW: Check if there is a 'next' parameter so we can send them back to the course they were looking at!
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
                
            # Otherwise, use the dictionary to route them to their dashboard
            routes = {'student': 'student_dashboard', 'instructor': 'instructor_dashboard', 'admin': '/admin/'}
            return redirect(routes.get(user.profile.role, 'student_dashboard'))
        
        messages.error(request, "Invalid username or password")
        
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# --- DASHBOARD VIEWS ---
@student_required
def student_dashboard(request): return render(request, 'student/dashboard.html')

@instructor_required
def instructor_dashboard(request): return render(request, 'instructor/dashboard.html')

@admin_required
def admin_dashboard(request): return render(request, 'admin/dashboard.html')

# --- PROFILE & SETTINGS VIEWS ---
@login_required
def profile_view(request):
    if request.method == 'POST':
        _update_user_data(request, request.user)
        messages.success(request, "Profile updated successfully!")
        return redirect('profile') 
    return render(request, 'student/profile.html')

@login_required
def settings_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            update_session_auth_hash(request, form.save())
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'student/settings.html', {'form': _style_password_form(form)})

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        # Optional: You can perform extra checks or password verification here if desired
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('home') # Redirect to your homepage or login page
        
    return redirect('settings')


@login_required
@instructor_required
def instructor_profile_view(request):
    # Only bind POST data to the form if the action was specifically 'change_password'
    is_pwd_action = request.POST.get('action') == 'change_password'
    form = PasswordChangeForm(request.user, request.POST if is_pwd_action else None)

    if request.method == 'POST':
        if request.POST.get('action') == 'update_profile':
            _update_user_data(request, request.user)
            messages.success(request, "Profile information updated successfully!")
            return redirect('instructor_profile')
            
        elif is_pwd_action:
            if form.is_valid():
                update_session_auth_hash(request, form.save())
                messages.success(request, 'Your password was successfully updated!')
                return redirect('instructor_profile')
            messages.error(request, 'Please correct the errors in the password form.')

    return render(request, 'instructor/profile.html', {'password_form': _style_password_form(form)})


from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def student_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.profile.role != 'student':
            messages.error(
                request,
                "You are not authorized to access this page."
            )
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper


def instructor_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.profile.role != 'instructor':
            messages.error(
                request,
                "You are not authorized to access this page."
            )
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.profile.role != 'admin':
            messages.error(request, "You are not authorized to access this page.")
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return wrapper
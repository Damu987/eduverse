from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from courses.models import Course, Enrollment


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        # Dictionary routing instead of if/else
        routes = {'instructor': 'instructor_dashboard', 'student': 'student_dashboard'}
        return redirect(routes.get(request.user.profile.role, 'student_dashboard'))
    return render(request, 'pages/index.html')

def about(request): return render(request, 'pages/about.html')
def contact(request): return render(request, 'pages/contact.html')


# --- COURSE CATALOG ---
def course_catalog(request):
    """Combines search, filtering (category/level), and pagination into one optimized view."""
    courses_list = Course.objects.filter(published=True).order_by('-created_at')

    # 1. Handle Search (accepts 'q' or 'search' from the URL)
    search_query = request.GET.get('q', request.GET.get('search', ''))
    if search_query:
        courses_list = courses_list.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # 2. Handle Category Filter
    category = request.GET.get('category', '')
    if category and category != 'All Categories':
        courses_list = courses_list.filter(category=category)

    # 3. Handle Level Filter
    level = request.GET.get('level', '')
    if level and level != 'All Levels':
        courses_list = courses_list.filter(level=level)

    # 4. Pagination (6 per page)
    paginator = Paginator(courses_list, 6)
    page_number = request.GET.get('page')
    try:
        courses = paginator.page(page_number)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    return render(request, 'pages/course_catalog.html', {
        'courses': courses,
        'categories': [c[0] for c in Course.category_choices],
        'levels': [l[0] for l in Course.level_choices],
        'search_query': search_query,
        'selected_category': category,
        'selected_level': level,
    })


# --- COURSE DETAILS ---
def course_details(request, course_id):
    """Public details page. Checks if a user is logged in before verifying enrollment."""
    course = get_object_or_404(Course, id=course_id, published=True)
    
    is_enrolled = False
    if request.user.is_authenticated:
        # Optimized with .exists() instead of loading the whole object
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    return render(request, 'public/course_details.html', {
        'course': course,
        'lessons': course.lessons.all().order_by('order'),
        'is_enrolled': is_enrolled
    })
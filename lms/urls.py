from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pages import views as page_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public Pages
    path("", page_views.home, name='home'),
    path("about/", page_views.about, name="about"),
    path("contact/", page_views.contact, name="contact"),
    path('courses/', page_views.course_catalog, name='course_catalog'), 
    
    path('courses/<int:course_id>/', page_views.course_details, name='course_details'),
    path('accounts/', include('accounts.urls')),
    path("", include('courses.urls')),
    path("", include('assignments.urls')),
    path("", include('certificate.urls')),
    path("", include('learning.urls')),
    path("", include('notification.urls')),
    path("", include('quizzes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
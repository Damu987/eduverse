from django.urls import path
from . import views

urlpatterns = [
    path('student/certificates/', views.student_certificates, name='student_certificates'),
    path('student/certificates/<uuid:certificate_id>/', views.view_certificate, name='view_certificate'),
]
from django.shortcuts import render, get_object_or_404
from .models import Certificate
from django.contrib.auth.decorators import login_required


#-------------------------Course Completion Generate Certificate-------------------------
@login_required
def student_certificates(request):
    certificates = Certificate.objects.filter(student=request.user).order_by('-issued_at')
    return render(request, 'student/certificate_list.html', {'certificates': certificates})

@login_required
def view_certificate(request, certificate_id):
    # UUIDs are passed via the URL to find the exact certificate
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user)
    return render(request, 'student/certificate_detail.html', {'certificate': certificate})

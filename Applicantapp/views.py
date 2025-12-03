# views.py
from django.shortcuts import get_object_or_404, render, redirect
from .forms import ApplicantApplyForm
from Companyapp.models import Application, JobAdvertised
from django.contrib import messages
from .tasks import process_resume_task  # Import the Celery task

def apply_for_job(request):
    if request.method == "POST":
        form = ApplicantApplyForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Save data
            applicant = form.save()
            job_advert = form.cleaned_data['job']
            Application.objects.create(applicant=applicant, post=job_advert.post)

            # 2. Hand off to Celery (Instant Return)
            # .delay() sends the ID to Redis. The worker picks it up later.
            process_resume_task.delay(applicant.applicant_id)

            # 3. Notify User
            messages.success(request, "Application received! Processing in background.")
            return redirect("apply_job")
    else:
        form = ApplicantApplyForm()

    jobs = JobAdvertised.objects.all()
    return render(request, "job_application.html", {"form": form, "jobs": jobs})






    
from Extractionapp.models import ResumeExtraction

def view_resume_insights(request, applicant_id):
    # Get the extraction object or return 404 if not ready yet
    extraction = get_object_or_404(ResumeExtraction, applicant_id=applicant_id)
    
    context = {
        "applicant": extraction.applicant,
        "raw_text": extraction.extracted_text,
        "skills": extraction.skills,
        "experience": extraction.work_experience,
        "projects": extraction.projects,
        "education": extraction.education,
    }
    return render(request, "resume_insights.html", context)
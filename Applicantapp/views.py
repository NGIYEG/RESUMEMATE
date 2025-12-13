# views.py
from django.shortcuts import get_object_or_404, render, redirect
from .forms import ApplicantApplyForm
from Companyapp.models import Application, JobAdvertised
from django.contrib import messages
from .tasks import process_resume_task  # Import the Celery task


def job_feed(request):
    """
    Displays active jobs in a blog-like format.
    """
    jobs = JobAdvertised.objects.all().order_by('-created_at') # Assuming created_at exists
    
    # Optional: Pre-process skills for bullet points (split by comma)
    for job in jobs:
        if job.required_skills:
            job.skill_list = [s.strip() for s in job.required_skills.split(',')]
            
    return render(request, 'applicant_feed.html', {'jobs': jobs})

def apply_for_job(request):
    # 1. Get job_id from the URL query string (e.g., ?job_id=5)
    job_id = request.GET.get('job_id') 
    
    selected_job = None
    initial_data = {}

    # 2. If ID exists, fetch the job
    if job_id:
        selected_job = get_object_or_404(JobAdvertised, id=job_id)
        initial_data = {'job': selected_job}

    if request.method == "POST":
        form = ApplicantApplyForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save()
            job_advert = form.cleaned_data['job']
            Application.objects.create(applicant=applicant, post=job_advert.post)
            
            # Trigger Celery Task
            process_resume_task.delay(applicant.applicant_id)

            messages.success(request, "Application received! Processing in background.")
            return redirect("job_feed")
    else:
        form = ApplicantApplyForm(initial=initial_data)

    jobs = JobAdvertised.objects.all()

    return render(request, "job_application.html", {
        "form": form, 
        "jobs": jobs,
        "selected_job": selected_job
    })

    
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
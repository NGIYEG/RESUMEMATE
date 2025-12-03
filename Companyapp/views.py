from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from .matcher import calculate_match_percentage
from .models import Application
from Extractionapp.models import ResumeExtraction
from Extractionapp.models import ResumeExtraction
from .forms import DepartmentForm, PostForm, JobAdvertisedForm
from .models import Department, JobAdvertised, Post
from django.contrib import messages
from django.http import JsonResponse
 
# Create your views here.

def add_department_and_post(request):
    dept_form = DepartmentForm()
    post_form = None   # Post form hidden at first

    if request.method == "POST":
        if "add_department" in request.POST:
            dept_form = DepartmentForm(request.POST)
            if dept_form.is_valid():
                dept_form.save()
                return redirect('add')

        if "add_post" in request.POST:
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post_form.save()
                return redirect('add')

    # Only show post form if there is at least one department
    if Department.objects.exists():
        post_form = PostForm()

    context = {
        'dept_form': dept_form,
        'post_form': post_form,
    }
    return render(request, "add_dept_post.html", context)
   

def create_job_advert(request):
    if request.method == "POST":
        form = JobAdvertisedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Job advertisement created successfully!")
            return redirect("job_advert")  # change to your desired URL name
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = JobAdvertisedForm()

    return render(request, "advertise_job.html", {"form": form})




def load_posts(request):
    department_id = request.GET.get("department")
    posts = Post.objects.filter(department_id=department_id).values("id", "title")
    return JsonResponse(list(posts), safe=False)




def applicants(request, job_id):
    job = JobAdvertised.objects.get(id=job_id)
    applications = Application.objects.filter(job=job)
    
    scored_applicants = []
    
    for app in applications:
        # 1. Get Resume Data (from DB)
        try:
            # Assuming you saved the extraction to the DB earlier
            extraction = ResumeExtraction.objects.get(applicant=app.applicant)
            resume_data = extraction.extracted_data # This is the JSON/Dict
        except ResumeExtraction.DoesNotExist:
            resume_data = {}

        # 2. Get LinkedIn Data (Placeholder)
        linkedin_data = {} # app.applicant.linkedin_data 

        # 3. CALCULATE SCORE
        match_score = calculate_match_percentage(job, resume_data, linkedin_data)
        
        scored_applicants.append({
            'applicant': app.applicant,
            'score': match_score,
            'resume_data': resume_data
        })

    # Sort by highest score
    scored_applicants.sort(key=lambda x: x['score'], reverse=True)

    return render(request, 'applicant_list.html', {
        'job': job,
        'applicants': scored_applicants
    })


def job_applicants_ranked(request, job_id):
    # 1. Get the Job
    job = get_object_or_404(JobAdvertised, id=job_id)
    
    # 2. Get all applications for this job
    applications = Application.objects.filter(job=job)
    
    ranked_candidates = []

    for app in applications:
        # --- A. Fetch Resume Data ---
        try:
            extraction = ResumeExtraction.objects.get(applicant=app.applicant)
            resume_data = extraction.extracted_data
        except ResumeExtraction.DoesNotExist:
            resume_data = {} # No resume parsed yet

        # --- B. Fetch LinkedIn Data (Placeholder) ---
        # If you have a LinkedIn model, fetch it here. 
        # For now, we pass empty dict.
        linkedin_data = {} 

        # --- C. Run the Math ---
        score = calculate_match_percentage(job, resume_data, linkedin_data)
        
        # --- D. Prepare Data for Template ---
        ranked_candidates.append({
            'applicant': app.applicant,
            'score': score,
            'resume_skills': resume_data.get('skills', []),
            'resume_experience': resume_data.get('work_experience', []),
            'resume_education': resume_data.get('education', []),
            'application_date': app.applied_at,
        })

    # 3. Sort by Score (Highest First)
    # reverse=True means Descending order (100% -> 0%)
    ranked_candidates.sort(key=lambda x: x['score'], reverse=True)

    context = {
        'job': job,
        'candidates': ranked_candidates
    }
    return render(request, 'ranked_applicants.html', context)
from .models import JobAdvertised

def global_job_id(request):
    """
    Ensures 'sidebar_job_id' is ALWAYS available.
    1. Checks the current URL for a job_id.
    2. If missing, finds the most recent job added to the database.
    3. If database is empty, returns 0 (to prevent crash, leads to 404).
    """
    
    # 1. Try to get ID from the current URL (e.g., /job/5/applicants/)
    url_id = request.resolver_match.kwargs.get('job_id')
    
    if url_id:
        return {'sidebar_job_id': url_id}

    # 2. Fallback: If on a page like /advertise-job/, get the LATEST job
    # (You can filter this by user if needed: .filter(user=request.user))
    latest_job = JobAdvertised.objects.order_by('-id').first()
    
    if latest_job:
        return {'sidebar_job_id': latest_job.id}

    # 3. Last Resort: Return 0 so the template tag doesn't crash
    return {'sidebar_job_id': 0}
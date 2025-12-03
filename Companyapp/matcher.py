import re

def calculate_match_percentage(job_advert, resume_data, linkedin_data=None):
    """
    Compares JobAdvertised requirements vs. Resume Extraction data.
    Returns a score from 0 to 100.
    """
    score = 0
    total_weight = 0

    # ==============================
    # 1. SKILLS MATCHING (Weight: 40%)
    # ==============================
    required_skills = [s.strip().lower() for s in job_advert.required_skills.split(',') if s.strip()]
    candidate_skills = [s.lower() for s in resume_data.get('skills', [])]
    
    # Add LinkedIn skills if available
    if linkedin_data and 'skills' in linkedin_data:
        candidate_skills += [s.lower() for s in linkedin_data['skills']]

    if required_skills:
        # Find intersection (skills present in both lists)
        matches = set(required_skills).intersection(set(candidate_skills))
        skill_score = (len(matches) / len(required_skills)) * 100
        score += skill_score * 0.40  # 40% weight
        total_weight += 0.40
    else:
        # If no skills required, give full points for this section
        score += 40
        total_weight += 0.40

    # ==============================
    # 2. EXPERIENCE MATCHING (Weight: 30%)
    # ==============================
    required_years = job_advert.min_experience_years
    candidate_years = 0

    # Extract years from resume strings like "Software Dev (2 Years)"
    # We sum up all years found
    for job in resume_data.get('work_experience', []):
        years_found = re.findall(r'\((\d+)\s*Years\)', job)
        if years_found:
            candidate_years += int(years_found[0])
    
    # Add LinkedIn experience logic here if needed
    
    if required_years > 0:
        if candidate_years >= required_years:
            exp_score = 100
        else:
            # Partial credit (e.g., has 1 year but needs 2 = 50%)
            exp_score = (candidate_years / required_years) * 100
        
        score += exp_score * 0.30
        total_weight += 0.30
    else:
        score += 30
        total_weight += 0.30

    # ==============================
    # 3. EDUCATION MATCHING (Weight: 30%)
    # ==============================
    # Simple hierarchy mapping
    edu_levels = {'Certificate': 1, 'Diploma': 2, 'Bachelor': 3, 'Master': 4, 'PhD': 5}
    req_level = edu_levels.get(job_advert.required_education, 1)
    
    candidate_max_level = 0
    candidate_education = resume_data.get('education', [])
    
    # Check what levels the candidate has
    for edu in candidate_education:
        edu_lower = edu.lower()
        if 'phd' in edu_lower or 'doctorate' in edu_lower:
            candidate_max_level = max(candidate_max_level, 5)
        elif 'master' in edu_lower:
            candidate_max_level = max(candidate_max_level, 4)
        elif 'bachelor' in edu_lower or 'bsc' in edu_lower or 'degree' in edu_lower:
            candidate_max_level = max(candidate_max_level, 3)
        elif 'diploma' in edu_lower:
            candidate_max_level = max(candidate_max_level, 2)
        elif 'certificate' in edu_lower:
            candidate_max_level = max(candidate_max_level, 1)

    if candidate_max_level >= req_level:
        edu_score = 100
    else:
        # Penalize if underqualified
        edu_score = 0 
    
    score += edu_score * 0.30
    total_weight += 0.30

    return round(score, 1)
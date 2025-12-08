import re
from difflib import SequenceMatcher

def fuzzy_match(skill_required, skill_candidate, threshold=0.8):
    """
    Returns True if skills are similar enough.
    Example: 'JavaScript' matches 'Javascript', 'JS'
    """
    skill_req = skill_required.lower().strip()
    skill_can = skill_candidate.lower().strip()
    
    # Exact match
    if skill_req == skill_can:
        return True
    
    # One contains the other (e.g., 'react' in 'react.js')
    if skill_req in skill_can or skill_can in skill_req:
        return True
    
    # Similarity ratio
    ratio = SequenceMatcher(None, skill_req, skill_can).ratio()
    return ratio >= threshold


def match_academic_courses(job_courses, candidate_education, threshold=0.75):
    """
    Match candidate's education with job's accepted courses.
    Returns matched courses and match percentage.
    
    Args:
        job_courses: List of course names accepted for the job
        candidate_education: List of education entries from resume
        threshold: Similarity threshold for fuzzy matching
    
    Returns:
        dict with 'matched_courses' list and 'match_percentage' float
    """
    if not job_courses:
        # No course requirements = full score
        return {
            'matched_courses': [],
            'match_percentage': 100.0
        }
    
    if not candidate_education:
        # No education data = no match
        return {
            'matched_courses': [],
            'match_percentage': 0.0
        }
    
    matched_courses = []
    
    # Normalize job courses for comparison
    job_courses_normalized = [course.lower().strip() for course in job_courses]
    
    # Combine all education entries into searchable text
    education_text = " ".join(candidate_education).lower()
    
    for idx, course in enumerate(job_courses):
        course_lower = job_courses_normalized[idx]
        
        # Method 1: Direct substring match
        if course_lower in education_text:
            matched_courses.append(course)
            continue
        
        # Method 2: Word-by-word matching
        course_words = course_lower.split()
        matches = sum(1 for word in course_words if len(word) > 3 and word in education_text)
        
        if len(course_words) > 0 and matches / len(course_words) >= 0.6:
            matched_courses.append(course)
            continue
        
        # Method 3: Fuzzy matching against each education entry
        for edu_entry in candidate_education:
            edu_lower = edu_entry.lower()
            
            # Check similarity ratio
            ratio = SequenceMatcher(None, course_lower, edu_lower).ratio()
            if ratio >= threshold:
                matched_courses.append(course)
                break
            
            # Check if course words appear in education entry
            if any(word in edu_lower for word in course_words if len(word) > 3):
                matched_courses.append(course)
                break
    
    # Calculate match percentage
    match_percentage = (len(matched_courses) / len(job_courses)) * 100 if job_courses else 100.0
    
    return {
        'matched_courses': list(set(matched_courses)),  # Remove duplicates
        'match_percentage': round(match_percentage, 1)
    }


def calculate_match_percentage(job_advert, resume_data, linkedin_data=None, job_courses=None):
    """
    Compares JobAdvertised requirements vs. Resume Extraction data.
    Now includes academic course matching.
    
    Weights:
    - Skills: 45%
    - Experience: 35%
    - Education Level: 15%
    - Academic Courses: 5%
    
    Returns a detailed score breakdown.
    """
    breakdown = {
        'total_score': 0,
        'skills_score': 0,
        'experience_score': 0,
        'education_score': 0,
        'course_match_score': 0,
        'matched_skills': [],
        'missing_skills': [],
        'matched_courses': [],
        'candidate_years': 0,
        'required_years': 0
    }

    required_skills = [
        s.strip().lower() 
        for s in job_advert.required_skills.split(',') 
        if s.strip()
    ]
    
    candidate_skills = [
        s.lower().strip() 
        for s in resume_data.get('skills', []) 
        if s.strip()
    ]
    
    # Merge LinkedIn skills
    if linkedin_data and 'skills' in linkedin_data:
        candidate_skills += [
            s.lower().strip() 
            for s in linkedin_data['skills'] 
            if s.strip()
        ]
    
    # Remove duplicates
    candidate_skills = list(set(candidate_skills))

    if required_skills:
        matched_skills = []
        
        for req_skill in required_skills:
            # Check for exact or fuzzy match
            for can_skill in candidate_skills:
                if fuzzy_match(req_skill, can_skill):
                    matched_skills.append(req_skill)
                    break
        
        breakdown['matched_skills'] = matched_skills
        breakdown['missing_skills'] = [
            s for s in required_skills 
            if s not in matched_skills
        ]
        
        skill_score = (len(matched_skills) / len(required_skills)) * 100
        breakdown['skills_score'] = round(skill_score, 1)
        breakdown['total_score'] += skill_score * 0.30  # 30% weight
    else:
        # No skills required = full points
        breakdown['skills_score'] = 100
        breakdown['total_score'] += 30

    # ==============================
    # 2. EXPERIENCE MATCHING (Weight: 25%)
    # ==============================
    required_years = job_advert.min_experience_years
    candidate_years = 0

    # Extract years from work experience entries
    for job_entry in resume_data.get('work_experience', []):
        # Pattern 1: "Software Dev (2 Years)"
        years_pattern1 = re.findall(r'\((\d+)\s*[Yy]ears?\)', job_entry, re.IGNORECASE)
        if years_pattern1:
            candidate_years += int(years_pattern1[0])
            continue
        
        # Pattern 2: "Started 2020" (assume 1 year)
        if 'started' in job_entry.lower():
            candidate_years += 1
            continue
        
        # Pattern 3: Look for year ranges "2020-2023"
        year_range = re.findall(r'20\d{2}\s*-\s*20\d{2}', job_entry)
        if year_range:
            years = re.findall(r'20\d{2}', year_range[0])
            if len(years) == 2:
                candidate_years += int(years[1]) - int(years[0])
    
    # Add LinkedIn experience if available
    if linkedin_data and 'years_experience' in linkedin_data:
        candidate_years += linkedin_data['years_experience']
    
    breakdown['candidate_years'] = candidate_years
    breakdown['required_years'] = required_years
    
    if required_years > 0:
        if candidate_years >= required_years:
            exp_score = 100
        else:
            # Partial credit with diminishing returns
            exp_score = min((candidate_years / required_years) * 100, 100)
        
        breakdown['experience_score'] = round(exp_score, 1)
        breakdown['total_score'] += exp_score * 0.25  # 25% weight
    else:
        breakdown['experience_score'] = 100
        breakdown['total_score'] += 25

    # ==============================
    # 3. EDUCATION LEVEL MATCHING (Weight: 25%)
    # ==============================
    edu_levels = {
        'Certificate': 1, 
        'Diploma': 2, 
        'Bachelor': 3, 
        'Master': 4, 
        'PhD': 5
    }
    
    req_level = edu_levels.get(job_advert.required_education, 1)
    candidate_max_level = 0
    candidate_education = resume_data.get('education', [])
    
    # Parse education entries
    for edu in candidate_education:
        if not edu:
            continue
            
        edu_lower = edu.lower()
        
        # Check from highest to lowest
        if any(term in edu_lower for term in ['phd', 'doctorate', 'doctoral']):
            candidate_max_level = max(candidate_max_level, 5)
        elif any(term in edu_lower for term in ['master', 'msc', 'ma', 'mba']):
            candidate_max_level = max(candidate_max_level, 4)
        elif any(term in edu_lower for term in ['bachelor', 'bsc', 'ba', 'b.sc', 'b.a', 'degree']):
            candidate_max_level = max(candidate_max_level, 3)
        elif 'diploma' in edu_lower:
            candidate_max_level = max(candidate_max_level, 2)
        elif 'certificate' in edu_lower:
            candidate_max_level = max(candidate_max_level, 1)

    breakdown['candidate_education_level'] = candidate_max_level
    breakdown['required_education_level'] = req_level
    
    if candidate_max_level >= req_level:
        edu_score = 100
    elif candidate_max_level == req_level - 1:
        # Close but not quite (e.g., Diploma when Bachelor required)
        edu_score = 50
    else:
        # Significantly underqualified
        edu_score = 0
    
    breakdown['education_score'] = round(edu_score, 1)
    breakdown['total_score'] += edu_score * 0.25  # 25% weight

    # ==============================
    # 4. ACADEMIC COURSE MATCHING (Weight: 20%)
    # ==============================
    if job_courses:
        course_match_result = match_academic_courses(
            job_courses, 
            candidate_education
        )
        
        breakdown['matched_courses'] = course_match_result['matched_courses']
        breakdown['course_match_score'] = course_match_result['match_percentage']
        
        # Add to total score with 20% weight
        breakdown['total_score'] += course_match_result['match_percentage'] * 0.20
    else:
        # No course requirements = full score
        breakdown['course_match_score'] = 100
        breakdown['total_score'] += 20

    # Final score
    breakdown['total_score'] = round(breakdown['total_score'], 1)
    
    return breakdown


def get_match_rating(score):
    """
    Convert numerical score to qualitative rating.
    """
    if score >= 80:
        return "Excellent Match"
    elif score >= 60:
        return "Good Match"
    elif score >= 40:
        return "Fair Match"
    else:
        return "Poor Match"
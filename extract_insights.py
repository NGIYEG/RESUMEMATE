import re
from datetime import datetime
from transformers import pipeline

_nlp_pipeline = None

def get_nlp_pipeline():
    global _nlp_pipeline
    if _nlp_pipeline is None:
        print("   🧠 [System] Loading Flan-T5 Model...")
        _nlp_pipeline = pipeline("text2text-generation", model="google/flan-t5-base") 
    return _nlp_pipeline

def smart_split(text):
    """
    Splits text by Commas, Newlines, or Bullets.
    Handles cases where AI forgets commas.
    """
    # Regex: Split by comma OR newline OR bullet point
    tokens = re.split(r'[,|\n|•|;]', text)
    return [t.strip() for t in tokens if t.strip()]

def extract_insights(text):
    nlp = get_nlp_pipeline()
    
    # Pre-cleaning: Turn newlines into commas to help the AI understand the list structure
    clean_text = text.replace("\n", ", ").strip()[:3000]

    print("   🧠 [Debug] asking AI for details...")

    # --- Q1: SKILLS ---
    raw_skills = nlp(
        f"List specific technical tools, software, and programming languages (comma separated):\nContext: {clean_text}", 
        max_length=128
    )[0]["generated_text"]

    # --- Q2: EDUCATION ---
    raw_education = nlp(
        f"List Degrees, Universities, and Colleges only (comma separated):\nContext: {clean_text}", 
        max_length=128
    )[0]["generated_text"]

    # --- Q3: EXPERIENCE ---
    raw_experience = nlp(
        f"List Job Titles and Dates (comma separated):\nContext: {clean_text}", 
        max_length=256
    )[0]["generated_text"]

    # =========================================
    # 🧹 CLEANING ENGINES
    # =========================================
    
    def clean_skills(raw_text):
        cleaned = []
        bad_words = ["responsible", "experience", "collaborating", "team", "strong", "bachelor", "bsc", "degree", "university", "summary", "profile"]
        
        # USE SMART SPLIT instead of just .split(',')
        for item in smart_split(raw_text):
            # Strict Rule: Max 4 words per skill
            if 1 < len(item.split()) < 5 and not any(w in item.lower() for w in bad_words):
                cleaned.append(item.title())
        return cleaned

    def clean_education(raw_text):
        cleaned = []
        edu_keywords = ["university", "college", "degree", "bsc", "bachelor", "master", "diploma", "certificate", "academy"]
        
        for item in smart_split(raw_text):
            if any(k in item.lower() for k in edu_keywords) or len(item) > 4:
                 if "experience" not in item.lower() and "work" not in item.lower():
                    cleaned.append(item)
        return cleaned

    def calculate_experience_chopper(raw_text):
        processed_jobs = []
        current_year = datetime.now().year

        # USE SMART SPLIT
        for item in smart_split(raw_text):
            if len(item) < 4: continue 

            # 1. THE CHOPPER (Fixes Long Paragraphs)
            title_only = re.split(r'\d{4}', item)[0].strip()
            
            # Cut text if description words are found
            split_words = [" with ", " responsible ", " adept ", " working ", " using ", " expertise "]
            for sword in split_words:
                if sword in title_only.lower():
                    title_only = title_only.lower().split(sword)[0].title()

            # Hard Limit: Max 6 words
            words = title_only.split()
            if len(words) > 6:
                short_title = " ".join(words[:6])
            else:
                short_title = title_only

            # 2. THE MATH (Calculates Years)
            years_found = re.findall(r'20\d{2}', item)
            years_found = [int(y) for y in years_found]
            
            duration_str = ""
            if years_found:
                is_current = "present" in item.lower() or "now" in item.lower()
                if is_current:
                    start = min(years_found)
                    diff = current_year - start
                    duration_str = f"{diff} Years"
                elif len(years_found) >= 2:
                    diff = max(years_found) - min(years_found)
                    duration_str = f"{diff} Years"
                else:
                    duration_str = f"Started {years_found[0]}"

            if duration_str:
                processed_jobs.append(f"{short_title} ({duration_str})")
            elif len(short_title) > 3:
                processed_jobs.append(short_title)

        return processed_jobs

    return {
        "skills": clean_skills(raw_skills),
        "education": clean_education(raw_education),
        "work_experience": calculate_experience_chopper(raw_experience),
        "projects": [] 
    }
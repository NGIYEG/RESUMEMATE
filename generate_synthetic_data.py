import json
import random

# --- DATA POOLS ---
NAMES = ["John Doe", "Alice Smith", "Bob Johnson", "Emily Davis", "Michael Brown"]
SKILLS_DB = ["Python", "Django", "JavaScript", "React", "PostgreSQL", "Docker", "AWS", "Git", "Java", "C++"]
DEGREES = ["BSc Computer Science", "MSc Data Science", "B.E. Software Engineering", "PhD Artificial Intelligence"]
UNIVERSITIES = ["MIT", "Stanford", "Oxford", "University of Nairobi", "Harvard", "Jkuat"]
COMPANIES = ["Google", "Microsoft", "Amazon", "Safaricom", "Andela", "Oracle"]
ROLES = ["Software Engineer", "Backend Developer", "Data Analyst", "Product Manager", "DevOps Engineer"]
PROJECTS = ["E-commerce Platform", "AI Chatbot", "Resume Parser", "Weather App", "Portfolio Site"]

def generate_complex_sample():
    # 1. Random Selection
    name = random.choice(NAMES)
    skills = random.sample(SKILLS_DB, k=random.randint(3, 6))
    degree = random.choice(DEGREES)
    uni = random.choice(UNIVERSITIES)
    company = random.choice(COMPANIES)
    role = random.choice(ROLES)
    project = random.choice(PROJECTS)
    
    # 2. Construct the "Raw" Resume Text (Varied Formats)
    # We create different layouts to make the model robust
    layout_type = random.randint(1, 3)
    
    if layout_type == 1:
        # Paragraph style
        raw_resume = (
            f"My name is {name}. I am a {role} with experience at {company}. "
            f"I graduated with a {degree} from {uni}. "
            f"My technical skills include {', '.join(skills)}. "
            f"I recently built a {project}. "
            "I also enjoy swimming and reading." # Irrelevant info to test filtering
        )
    elif layout_type == 2:
        # Header style
        raw_resume = (
            f"RESUME: {name}\n"
            f"PROFESSIONAL SUMMARY: Experienced {role} at {company}.\n"
            f"EDUCATION: {uni} - {degree}\n"
            f"TECH STACK: {', '.join(skills)}\n"
            f"KEY PROJECTS: {project}\n"
            "HOBBIES: Hiking, Chess."
        )
    else:
        # Bullet style
        raw_resume = (
            f"{name}\n"
            f"* {role} @ {company}\n"
            f"* {degree}, {uni}\n"
            f"* Skills: {skills[0]}, {skills[1]}, {skills[2]}\n"
            f"* Project: {project}"
        )

    # 3. Construct the "Instruction" Input
    # THIS MUST MATCH YOUR extract_insights.py PROMPT EXACTLY
    input_text = f"""
    Extract this resume into structured JSON with fields:
    - skills (list)
    - work_experience (list)
    - projects (list)
    - education (list)

    Resume text:
    {raw_resume}
    """

    # 4. Construct the Target JSON (The "Correct Answer")
    target_json = {
        "skills": skills,
        "work_experience": [f"{role} at {company}"],
        "projects": [project],
        "education": [f"{degree} from {uni}"]
    }

    return {
        "text": input_text,           # The model sees this
        "target": json.dumps(target_json) # The model learns to output this
    }

def create_dataset(num_samples=500):
    data = [generate_complex_sample() for _ in range(num_samples)]
    
    with open("synthetic_resume_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Generated {num_samples} instruction-tuned samples.")

if __name__ == "__main__":
    create_dataset()
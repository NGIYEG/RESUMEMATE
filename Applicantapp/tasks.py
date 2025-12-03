from celery import shared_task
from django.conf import settings
import os
import fitz  # PyMuPDF
from Applicantapp.models import Applicant
from Extractionapp.models import ResumeExtraction
import easyocr 

@shared_task
def process_resume_task(applicant_id):
    try:
        print(f"🚀 [Celery] Processing Applicant ID: {applicant_id}")
        
        # 1. Initialize EasyOCR Reader
        # gpu=False (CPU) is safer for local windows setups unless you configured CUDA
        reader = easyocr.Reader(['en'], gpu=False) 

        # 2. Load NLP Function (Lazy Import)
        # We import it HERE to avoid loading heavy NLP models when Django starts
        from extract_insights import extract_insights

        applicant = Applicant.objects.get(applicant_id=applicant_id)
        
        # 3. PDF to Images
        pdf_path = applicant.resume.path
        output_folder = os.path.join(settings.MEDIA_ROOT, "resume_images", str(applicant.applicant_id))
        os.makedirs(output_folder, exist_ok=True)

        doc = fitz.open(pdf_path)
        image_paths = []
        full_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Zoom in (Scale x2) for better OCR accuracy
            mat = fitz.Matrix(2.0, 2.0) 
            pix = page.get_pixmap(matrix=mat)
            
            img_name = f"page_{page_num+1}.jpg"
            img_path = os.path.join(output_folder, img_name)
            pix.save(img_path)
            
            image_paths.append(f"resume_images/{applicant.applicant_id}/{img_name}")

            # 4. RUN EASYOCR
            print(f"   🔍 Reading Text on Page {page_num+1}...")
            
            # detail=0 returns just the list of text strings
            result = reader.readtext(img_path, detail=0) 
            
            # CRITICAL: Join with newlines to preserve Resume Structure
            page_text = "\n".join(result) 
            
            full_text += page_text + "\n\n"

        # Update Images in DB
        applicant.converted_images = image_paths
        applicant.save()

        # 5. Run NLP Analysis
        print("   🧠 Running NLP Analysis...")
        # Now we pass the clear, newline-separated text to your NLP model
        insights = extract_insights(full_text)

        # 6. Save Results
        extraction, _ = ResumeExtraction.objects.get_or_create(applicant=applicant)
        extraction.extracted_text = full_text
        extraction.skills = insights.get("skills", [])
        extraction.work_experience = insights.get("work_experience", [])
        extraction.projects = insights.get("projects", [])
        extraction.education = insights.get("education", [])
        extraction.processed = True
        extraction.save()

        print(f"✅ [Celery] Success! Read {len(full_text)} characters.")
        return "Success"

    except Exception as e:
        print(f"💥 [Celery] Critical Error: {e}")
        return f"Failed: {e}"
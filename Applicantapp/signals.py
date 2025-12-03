from django.db.models.signals import post_save
from django.dispatch import receiver
from Applicantapp.models import Applicant
from Extractionapp.models import ResumeExtraction
# from django.conf import settings
# from PIL import Image
# import os

# IMPORTANT: These imports are commented out to prevent double-loading 
# the AI models into RAM. The logic is now handled in views.py.
# from ocr.trocr_model import processor, model
# from ocr.extract_insights import extract_insights

@receiver(post_save, sender=Applicant)
def extract_text_with_trocr(sender, instance, created, **kwargs):
    """
    DEPRECATED: Extraction logic has been moved to views.py 
    to support fine-tuned model loading and better error handling.
    """
    pass
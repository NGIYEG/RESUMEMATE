# import os
# from django.conf import settings
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# # Path to your fine-tuned model
# LOCAL_MODEL_PATH = os.path.join(settings.BASE_DIR, "fine_tuned_models/trocr")

# if os.path.exists(LOCAL_MODEL_PATH):
#     print("Loading Fine-Tuned TrOCR Model...")
#     processor = TrOCRProcessor.from_pretrained(LOCAL_MODEL_PATH)
#     model = VisionEncoderDecoderModel.from_pretrained(LOCAL_MODEL_PATH)
# else:
#     print("Loading Base TrOCR Model (Warning: Not Fine-Tuned)...")
#     processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
#     model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")


# from transformers import TrOCRProcessor, VisionEncoderDecoderModel
# import os
# from django.conf import settings

# # --- FORCE BASE MODEL FOR DEBUGGING ---
# # Comment out the logic that looks for "fine_tuned_models/trocr"
# # LOCAL_MODEL_PATH = os.path.join(settings.BASE_DIR, "fine_tuned_models/trocr")

# print("Loading Base Microsoft TrOCR Model (Debugging)...")
# processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
# model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")



from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import os
from django.conf import settings

# --- FORCE BASE MODEL (Standard Microsoft Version) ---
# We are intentionally ignoring your local fine_tuned_models folder for now
print("🔄 Loading Base Microsoft TrOCR Model...")

# Load the base model directly from Hugging Face
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

# Configure it to be less repetitive
model.config.eos_token_id = processor.tokenizer.sep_token_id
model.config.max_length = 64
model.config.early_stopping = True
model.config.no_repeat_ngram_size = 3
model.config.length_penalty = 2.0
model.config.num_beams = 4
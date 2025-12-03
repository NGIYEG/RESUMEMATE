import os
import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image
from transformers import (
    TrOCRProcessor, 
    VisionEncoderDecoderModel, 
    Seq2SeqTrainer, 
    Seq2SeqTrainingArguments, 
    default_data_collator
)

# --- CONFIGURATION ---
BASE_MODEL = "microsoft/trocr-base-printed"
DATA_DIR = "./training_data/images"  # Folder containing your resume images
LABEL_FILE = "./training_data/labels.csv" # CSV with 'file_name' and 'text' columns
OUTPUT_DIR = "./fine_tuned_models/trocr"

# --- DATASET CLASS ---
class ResumeOCRDataset(Dataset):
    def __init__(self, root_dir, df, processor, max_target_length=128):
        self.root_dir = root_dir
        self.df = df
        self.processor = processor
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        file_name = self.df.iloc[idx]['file_name']
        text = self.df.iloc[idx]['text']
        
        # Load and process image
        image_path = os.path.join(self.root_dir, file_name)
        image = Image.open(image_path).convert("RGB")
        pixel_values = self.processor(image, return_tensors="pt").pixel_values

        # Process label (text)
        labels = self.processor.tokenizer(
            text, 
            padding="max_length", 
            max_length=self.max_target_length
        ).input_ids
        
        # Mask padding tokens so they don't affect loss
        labels = [label if label != self.processor.tokenizer.pad_token_id else -100 for label in labels]

        return {"pixel_values": pixel_values.squeeze(), "labels": torch.tensor(labels)}

# --- MAIN TRAINING LOOP ---
def train():
    # 1. Load Processor and Model
    processor = TrOCRProcessor.from_pretrained(BASE_MODEL)
    model = VisionEncoderDecoderModel.from_pretrained(BASE_MODEL)

    # Set special tokens
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.vocab_size = model.config.decoder.vocab_size

    # 2. Load Data
    df = pd.read_csv(LABEL_FILE)
    # Split into train/test (80/20)
    train_df = df.sample(frac=0.8, random_state=42)
    eval_df = df.drop(train_df.index)

    train_dataset = ResumeOCRDataset(DATA_DIR, train_df, processor)
    eval_dataset = ResumeOCRDataset(DATA_DIR, eval_df, processor)

    # 3. Training Arguments
    training_args = Seq2SeqTrainingArguments(
        predict_with_generate=True,
        evaluation_strategy="steps",
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        output_dir=OUTPUT_DIR,
        logging_steps=100,
        save_steps=500,
        eval_steps=500,
        num_train_epochs=5,  # Increase this for better results
    )

    # 4. Initialize Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        tokenizer=processor.feature_extractor,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=default_data_collator,
    )

    # 5. Train and Save
    print("Starting OCR Training...")
    trainer.train()
    
    print(f"Saving model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    processor.save_pretrained(OUTPUT_DIR)

if __name__ == "__main__":
    train()
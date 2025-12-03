# train_extraction.py
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import Dataset

# 1. PREPARE DATA
# List of dicts: {"text": "Resume raw text...", "target": "{ 'skills': ['Python'], ... }"}
data = [
    {"text": "Extract fields: John Doe, Python Dev...", "target": "{\"skills\": [\"Python\"], \"education\": []}"},
    # ... add HUNDREDS of examples here ...
]
dataset = Dataset.from_list(data)

model_id = "google/flan-t5-base"
tokenizer = T5Tokenizer.from_pretrained(model_id)
model = T5ForConditionalGeneration.from_pretrained(model_id)

# 2. PREPROCESS FUNCTION
def preprocess_function(examples):
    inputs = [doc for doc in examples["text"]]
    model_inputs = tokenizer(inputs, max_length=512, truncation=True)

    # Tokenize targets (the JSON string)
    labels = tokenizer(text_target=examples["target"], max_length=512, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True)

# 3. TRAIN
training_args = Seq2SeqTrainingArguments(
    output_dir="./fine_tuned_flan",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    save_strategy="epoch",
    learning_rate=5e-5,
)

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

print("Starting Flan-T5 training...")
trainer.train()

# 4. SAVE
model.save_pretrained("./custom_resume_nlp")
tokenizer.save_pretrained("./custom_resume_nlp")
print("NLP Model saved to ./custom_resume_nlp")
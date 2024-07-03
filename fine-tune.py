from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import Dataset
import json


with open('datasets/text-to-ui-color-palet.json') as f:
    data = json.load(f)


dataset = Dataset.from_dict(data)


model_id = "EleutherAI/gpt-neo-125M"  # or any other pre-trained model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)


def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)


training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    eval_dataset=tokenized_datasets,
)


trainer.train()


model.save_pretrained('models/text-to-ui-color-palet')
tokenizer.save_pretrained('models/text-to-ui-color-palet')

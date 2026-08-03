"""
Hugging Face Basic Fine-Tuning Example

This script demonstrates standard fine-tuning using the Hugging Face Trainer API.
It serves as a test fixture for the Project Scanner.
"""

import yaml
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)


def load_config(config_path: str) -> dict:
    """Load training configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    # Load configuration
    config = load_config("config.yaml")

    # Model and tokenizer
    model_name = config.get("model_name", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Load dataset
    dataset = load_dataset("json", data_files=config["dataset_path"], split="train")

    # Tokenize function
    def tokenize_function(examples):
        return tokenizer(
            examples["instruction"],
            examples["response"],
            truncation=True,
            max_length=config.get("max_seq_length", 2048),
            padding="max_length",
        )

    # Tokenize dataset
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=config.get("output_dir", "./results"),
        num_train_epochs=config.get("epochs", 3),
        per_device_train_batch_size=config.get("batch_size", 8),
        learning_rate=config.get("learning_rate", 5e-5),
        weight_decay=config.get("weight_decay", 0.01),
        logging_steps=config.get("logging_steps", 10),
        save_steps=config.get("save_steps", 500),
        eval_steps=config.get("eval_steps", 100),
        evaluation_strategy="steps",
        fp16=config.get("fp16", True),
        gradient_checkpointing=config.get("gradient_checkpointing", True),
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    # Train
    trainer.train()

    # Save model
    trainer.save_model()
    tokenizer.save_pretrained(training_args.output_dir)


if __name__ == "__main__":
    main()
"""
PEFT LoRA Fine-Tuning Example

This script demonstrates fine-tuning using LoRA (Low-Rank Adaptation) from the PEFT library.
It serves as a test fixture for detecting LoRA configurations.
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
from peft import LoraConfig, get_peft_model, TaskType


def load_config(config_path: str) -> dict:
    """Load training configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    # Load configuration
    config = load_config("lora_config.yaml")

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

    # LoRA Configuration
    lora_config = LoraConfig(
        r=config.get("lora_r", 8),
        lora_alpha=config.get("lora_alpha", 16),
        target_modules=config.get("lora_target_modules", ["q_proj", "v_proj"]),
        lora_dropout=config.get("lora_dropout", 0.05),
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    # Apply LoRA to model
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Training arguments
    training_args = TrainingArguments(
        output_dir=config.get("output_dir", "./lora-output"),
        num_train_epochs=config.get("epochs", 3),
        per_device_train_batch_size=config.get("batch_size", 4),
        learning_rate=config.get("learning_rate", 2e-4),
        weight_decay=config.get("weight_decay", 0.01),
        logging_steps=config.get("logging_steps", 10),
        save_steps=config.get("save_steps", 500),
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

    # Save LoRA adapter
    model.save_pretrained(training_args.output_dir)


if __name__ == "__main__":
    main()
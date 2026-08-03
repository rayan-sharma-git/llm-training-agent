"""
TRL SFT Fine-Tuning Example

This script demonstrates supervised fine-tuning using TRL's SFTTrainer.
It serves as a test fixture for detecting TRL framework configurations.
"""

import yaml
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)
from trl import SFTTrainer, SFTConfig


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

    # Formatting function for SFTTrainer
    def formatting_prompts_func(examples):
        texts = []
        for instruction, response in zip(examples["instruction"], examples["response"]):
            text = f"### Question:\n{instruction}\n\n### Answer:\n{response}"
            texts.append(text)
        return texts

    # SFT Configuration
    sft_config = SFTConfig(
        output_dir=config.get("output_dir", "./sft-output"),
        max_seq_length=config.get("max_seq_length", 2048),
        per_device_train_batch_size=config.get("batch_size", 4),
        gradient_accumulation_steps=config.get("gradient_accumulation_steps", 4),
        learning_rate=config.get("learning_rate", 2e-4),
        num_train_epochs=config.get("epochs", 3),
        logging_steps=config.get("logging_steps", 10),
        save_steps=config.get("save_steps", 500),
        warmup_steps=config.get("warmup_steps", 100),
        fp16=config.get("fp16", True),
        bf16=config.get("bf16", False),
        packing=config.get("packing", False),
    )

    # SFT Trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        formatting_func=formatting_prompts_func,
        args=sft_config,
    )

    # Train
    trainer.train()

    # Save model
    trainer.save_model(sft_config.output_dir)


if __name__ == "__main__":
    main()
# Hugging Face Basic Fine-Tuning Project

## Framework

Hugging Face Transformers + Trainer API

## Purpose

Standard fine-tuning project using the Hugging Face Trainer. Suitable for testing basic framework detection and analysis.

## Project Structure

```
huggingface_basic/
├── README.md
├── train.py
├── config.yaml
├── dataset/
│   └── sample.jsonl
├── prompts/
│   └── system_prompt.txt
└── requirements.txt
```

## Model

TinyLlama/TinyLlama-1.1B-Chat-v1.0

## Dataset

Uses the high_quality sample dataset with instruction-following format.

## Expected Scanner Detection

- Framework: Hugging Face Transformers
- Model: TinyLlama-1.1B-Chat-v1.0
- Dataset: JSONL format
- Configuration: YAML
- Training Script: train.py
- LoRA: Not detected
- Tokenizer: AutoTokenizer
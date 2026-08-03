# PEFT LoRA Fine-Tuning Project

## Framework

Hugging Face Transformers + PEFT (LoRA)

## Purpose

Fine-tuning project using Parameter-Efficient Fine-Tuning with Low-Rank Adaptation. Tests the scanner's ability to detect LoRA configurations.

## Project Structure

```
peft_lora/
├── README.md
├── train.py
├── lora_config.yaml
├── dataset/
│   └── sample.jsonl
└── requirements.txt
```

## Model

TinyLlama/TinyLlama-1.1B-Chat-v1.0

## Dataset

Same high_quality dataset as basic project.

## Expected Scanner Detection

- Framework: PEFT (LoRA)
- Model: TinyLlama-1.1B-Chat-v1.0
- Dataset: JSONL format
- Configuration: YAML
- Training Script: train.py
- LoRA: Detected (rank=8, alpha=16)
- Target Modules: q_proj, v_proj, k_proj, o_proj
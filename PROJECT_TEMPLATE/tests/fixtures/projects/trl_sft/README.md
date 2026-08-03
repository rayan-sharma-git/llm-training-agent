# TRL Supervised Fine-Tuning Project

## Framework

TRL (Transformer Reinforcement Learning) - SFT Trainer

## Purpose

Fine-tuning project using TRL's SFTTrainer for supervised fine-tuning. Tests scanner's ability to detect TRL framework and SFT-specific configurations.

## Project Structure

```
trl_sft/
├── README.md
├── train.py
├── config.yaml
├── dataset/
│   └── sample.jsonl
└── requirements.txt
```

## Model

TinyLlama/TinyLlama-1.1B-Chat-v1.0

## Dataset

Same high_quality dataset as other projects.

## Expected Scanner Detection

- Framework: TRL (SFT)
- Model: TinyLlama-1.1B-Chat-v1.0
- Dataset: JSONL format
- Configuration: YAML
- Training Script: train.py
- LoRA: Detected (if configured)
- Special: SFTTrainer usage
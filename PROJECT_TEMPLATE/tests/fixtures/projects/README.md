# Example Fine-Tuning Projects

## Purpose

Complete example projects that the Project Scanner and analyzers can be tested against. These simulate real-world LLM fine-tuning projects.

## Projects

### huggingface_basic/

Standard Hugging Face Transformers fine-tuning project.

**Structure:**
- train.py: Training script
- config.yaml: Training configuration
- dataset/: Sample dataset
- prompts/: Prompt templates
- README.md: Project documentation

**Framework:** Hugging Face Transformers + Trainer

### peft_lora/

PEFT/LoRA fine-tuning project.

**Structure:**
- train.py: PEFT training script
- lora_config.yaml: LoRA configuration
- dataset/: Sample dataset
- README.md

**Framework:** Hugging Face + PEFT

### trl_sft/

TRL supervised fine-tuning project.

**Structure:**
- train.py: TRL SFT script
- config.yaml: SFT configuration
- dataset/: Sample dataset
- README.md

**Framework:** TRL (Transformer Reinforcement Learning)

## Usage

Each project should be scanned to verify:
1. Framework detection
2. Model identification
3. Dataset discovery
4. Configuration parsing
5. Script recognition
6. LoRA/PEFT detection
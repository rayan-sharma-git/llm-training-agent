# Sample Configuration Files

## Purpose

These configuration files verify that analyzers correctly parse and validate training configurations.

## Formats

### yaml/

YAML configurations from popular fine-tuning frameworks.

**Examples:**
- Axolotl training configs
- Hugging Face training arguments
- LoRA/PEFT configurations
- TRL SFT configurations

**Use cases:**
- Verify hyperparameter extraction
- Test configuration validation
- Validate model detection
- Ensure LoRA configuration parsing

### json/

JSON configurations for various tools.

**Examples:**
- Hugging Face model configs
- Tokenizer configurations
- Training scripts with config sections
- Dataset metadata

## Expected Validations

Each config should be tested for:
1. Correct parsing
2. Required field detection
3. Invalid value detection
4. Missing field warnings
5. Framework identification
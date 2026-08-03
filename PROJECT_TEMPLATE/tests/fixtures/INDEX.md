# Test Fixtures Index

## Quick Reference

This index provides a quick reference for all test fixtures and their purposes.

## Datasets

### high_quality/sample.jsonl
- **Records:** 12
- **Purpose:** Validates analyzer recognizes good datasets
- **Expected Quality:** >0.85
- **Expected Duplicates:** 0%
- **Expected Issues:** None significant

### low_quality/sample.jsonl
- **Records:** 24
- **Purpose:** Validates detection of data quality issues
- **Expected Quality:** <0.50
- **Expected Duplicates:** 16.67%
- **Expected Issues:** Missing fields, empty responses, near-duplicates

### edge_cases/sample.jsonl
- **Records:** 18
- **Purpose:** Validates boundary condition handling
- **Expected Quality:** Variable
- **Test Cases:** Very short/long responses, empty fields, Unicode

## Projects

### huggingface_basic/
- **Framework:** Hugging Face Transformers + Trainer
- **Model:** TinyLlama-1.1B-Chat-v1.0
- **LoRA:** No
- **Test:** Framework detection, config parsing, basic analysis

### peft_lora/
- **Framework:** Hugging Face + PEFT/LoRA
- **Model:** TinyLlama-1.1B-Chat-v1.0
- **LoRA:** Yes (r=8, alpha=16)
- **Test:** LoRA detection, target module identification, PEFT config parsing

### trl_sft/
- **Framework:** TRL SFTTrainer
- **Model:** TinyLlama-1.1B-Chat-v1.0
- **LoRA:** No
- **Test:** TRL detection, SFTConfig parsing, TRL-specific features

## Prompts

### effective/system_prompt.txt
- **Quality:** High
- **Expected Clarity:** >0.85
- **Expected Issues:** Minor (missing context handling)
- **Test:** Validates good prompt recognition

### problematic/system_prompt.txt
- **Quality:** Low
- **Expected Clarity:** <0.40
- **Expected Issues:** Conflicts, leakage, missing role
- **Test:** Validates problem detection

## Configurations

### yaml/axolotl_basic.yml
- **Framework:** Axolotl
- **Model:** Mistral-7B
- **LoRA:** Yes
- **Test:** Axolotl config parsing, hyperparameter extraction

### json/huggingface_trainer_config.json
- **Framework:** Hugging Face Trainer
- **Model:** TinyLlama-1.1B
- **LoRA:** No
- **Test:** JSON config parsing, training arguments extraction

## Expected Outputs

### dataset_analysis/high_quality_expected.json
- **Use with:** datasets/high_quality/sample.jsonl
- **Validates:** Quality scoring, duplicate detection, issue identification

### dataset_analysis/low_quality_expected.json
- **Use with:** datasets/low_quality/sample.jsonl
- **Validates:** Problem detection, warning generation, recommendations

### prompt_analysis/effective_prompt_expected.json
- **Use with:** prompts/effective/system_prompt.txt
- **Validates:** Quality scoring, minor issue detection

### prompt_analysis/problematic_prompt_expected.json
- **Use with:** prompts/problematic/system_prompt.txt
- **Validates:** Conflict detection, leakage detection, scoring

### hyperparameter_analysis/axolotl_config_expected.json
- **Use with:** configs/yaml/axolotl_basic.yml
- **Validates:** Config parsing, LoRA validation, recommendations

## Usage Statistics

- **Total Datasets:** 3
- **Total Projects:** 3
- **Total Prompts:** 2
- **Total Configs:** 2
- **Total Expected Outputs:** 5
- **Total Test Files:** (to be created in backend/tests/ and extension/tests/)

## Coverage Matrix

| Analyzer | Datasets | Projects | Prompts | Configs |
|----------|----------|----------|---------|---------|
| Project Scanner | - | ✓ (3) | - | ✓ (2) |
| Dataset Intelligence | ✓ (3) | - | - | - |
| Prompt Intelligence | - | - | ✓ (2) | - |
| Hyperparameter Advisor | - | - | - | ✓ (2) |
| Cost Estimator | - | ✓ (3) | - | - |
| Model Advisor | - | ✓ (3) | - | - |

## Maintenance

- **Created:** 2025-01-03
- **Version:** 1.0
- **Maintainer:** LLM Training Agent Project
- **Last Updated:** 2025-01-03

## Notes

All fixtures use TinyLlama/TinyLlama-1.1B-Chat-v1.0 as the base model for consistency.

Datasets contain real ML engineering content (not Lorem ipsum) to ensure realistic testing.

Expected outputs document ground truth and should be treated as specifications for analyzer behavior.
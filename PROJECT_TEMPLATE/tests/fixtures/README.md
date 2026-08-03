# Test Fixtures

## Purpose

This directory contains sample datasets, prompt templates, and example projects used to verify that every analyzer produces correct outputs.

## Why This Exists

The requirements specify that features must be verified against sample data before being considered complete:

- Milestone 4: "Scanner successfully analyzes multiple sample projects"
- Milestone 5: "Dataset reports are accurate"
- Milestone 6: "Prompt analysis integrated with reports"

Without sample data, correctness cannot be demonstrated.

## Directory Structure

```
tests/fixtures/
├── README.md                    # This file
├── datasets/                    # Sample training datasets
│   ├── high_quality/           # Well-formed dataset
│   ├── low_quality/            # Dataset with intentional issues
│   ├── edge_cases/             # Boundary conditions
│   └── README.md
├── projects/                    # Complete example projects
│   ├── huggingface_basic/      # Standard HF Transformers project
│   ├── peft_lora/              # PEFT/LoRA fine-tuning
│   ├── trl_sft/                # TRL supervised fine-tuning
│   └── README.md
├── prompts/                     # Sample prompt templates
│   ├── effective/              # Well-written prompts
│   ├── problematic/            # Prompts with issues
│   └── README.md
├── configs/                     # Training configuration files
│   ├── yaml/                   # YAML configs (Axolotl, etc.)
│   ├── json/                   # JSON configs
│   └── README.md
└── expected_outputs/            # Ground truth for validation
    ├── dataset_analysis/
    ├── prompt_analysis/
    ├── hyperparameter_analysis/
    └── README.md
```

## Usage

Every analyzer test should:
1. Load sample input from this directory
2. Execute the analyzer
3. Compare output against expected_outputs
4. Assert correctness

## Naming Convention

- Use descriptive names: `dataset_duplicates_high_quality.json`
- Include metadata: `README.md` in each subdirectory explains the test case
- Version fixtures: Changes to fixtures require justification

## Maintenance

- Add new fixtures when adding new test cases
- Never modify existing fixtures without updating all dependent tests
- Document the purpose of each fixture
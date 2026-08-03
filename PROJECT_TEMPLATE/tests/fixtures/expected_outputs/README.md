# Expected Outputs (Ground Truth)

## Purpose

These files define the expected analyzer outputs for given inputs. Tests compare actual analyzer results against these expected outputs to verify correctness.

## Structure

```
expected_outputs/
├── README.md
├── dataset_analysis/
│   ├── high_quality_expected.json
│   ├── low_quality_expected.json
│   └── edge_cases_expected.json
├── prompt_analysis/
│   ├── effective_prompt_expected.json
│   └── problematic_prompt_expected.json
└── hyperparameter_analysis/
    └── axolotl_config_expected.json
```

## Usage in Tests

```python
def test_dataset_analysis():
    # Load input
    dataset = load_fixture("datasets/high_quality/sample.jsonl")
    
    # Run analyzer
    result = dataset_analyzer.analyze(dataset)
    
    # Load expected output
    expected = load_fixture("expected_outputs/dataset_analysis/high_quality_expected.json")
    
    # Assert
    assert result.quality_score == expected["quality_score"]
    assert result.duplicate_percentage == expected["duplicate_percentage"]
    # ... more assertions
```

## Maintaining Expected Outputs

When analyzer logic changes:
1. Update expected outputs
2. Document why the change occurred
3. Verify all tests pass
4. Never modify expected outputs to match incorrect behavior
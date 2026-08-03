# Testing Strategy with Sample Data

## Overview

This document explains how sample datasets and example projects verify feature correctness throughout development.

## Philosophy

**"No feature is complete without test data proving it works correctly."**

Every analyzer, scanner, and module must be tested against:
1. Known-good inputs (high_quality)
2. Known-bad inputs (low_quality)
3. Boundary conditions (edge_cases)
4. Real project structures (example projects)

## Testing Workflow

### 1. Unit Tests with Fixtures

```python
def test_dataset_analyzer_high_quality():
    """Verify analyzer correctly identifies high-quality datasets."""
    # Arrange
    dataset = load_fixture("datasets/high_quality/sample.jsonl")
    expected = load_fixture("expected_outputs/dataset_analysis/high_quality_expected.json")
    
    # Act
    result = dataset_analyzer.analyze(dataset)
    
    # Assert
    assert result.quality_score == pytest.approx(expected["quality_score"], abs=0.05)
    assert result.duplicate_percentage == expected["duplicate_percentage"]
    assert len(result.warnings) == len(expected["warnings"])
```

### 2. Integration Tests with Projects

```python
def test_scanner_detects_huggingface_framework():
    """Verify scanner identifies Hugging Face project correctly."""
    # Arrange
    project_path = load_fixture("projects/huggingface_basic")
    
    # Act
    context = scanner.scan_project(project_path)
    
    # Assert
    assert context.detected_framework == "huggingface_transformers"
    assert "TinyLlama" in context.base_model
    assert len(context.dataset_paths) > 0
```

### 3. Regression Tests

Every bug fix must include:
1. A test fixture that reproduces the bug
2. A test that fails before the fix
3. A test that passes after the fix

## Fixture Organization

### Datasets

| Fixture | Purpose | Expected Outcome |
|---------|---------|------------------|
| `high_quality/sample.jsonl` | Well-formed data | Quality score >0.85, no duplicates |
| `low_quality/sample.jsonl` | Intentional issues | Duplicates detected, quality <0.50 |
| `edge_cases/sample.jsonl` | Boundary conditions | No crashes, graceful handling |

### Projects

| Project | Framework | Key Test Cases |
|---------|-----------|----------------|
| `huggingface_basic` | HF Transformers | Framework detection, config parsing |
| `peft_lora` | PEFT/LoRA | LoRA config detection, target modules |
| `trl_sft` | TRL | SFTTrainer detection, TRL config |

### Expected Outputs

Each expected output file:
- Defines ground truth for a specific input
- Includes all fields the analyzer should return
- Documents expected confidence levels
- Specifies tolerance for numerical values

## Test Implementation Priority

### Milestone 4: Project Scanner
```python
test_scanner_detects_huggingface_basic()
test_scanner_detects_peft_lora()
test_scanner_detects_trl_sft()
test_scanner_identifies_model()
test_scanner_finds_dataset()
test_scanner_parses_config()
```

### Milestone 5: Dataset Intelligence
```python
test_dataset_analyzer_high_quality()
test_dataset_analyzer_low_quality()
test_dataset_analyzer_detects_duplicates()
test_dataset_analyzer_detects_missing_fields()
test_dataset_analyzer_calculates_quality_score()
```

### Milestone 6: Prompt Intelligence
```python
test_prompt_analyzer_effective_prompt()
test_prompt_analyzer_problematic_prompt()
test_prompt_analyzer_detects_conflicts()
test_prompt_analyzer_scores_clarity()
```

## Assertions and Tolerance

### Exact Matches
- Framework names
- File paths
- Error messages
- Issue descriptions

### Approximate Matches
```python
# Quality scores: ±0.05 tolerance
assert result.quality_score == pytest.approx(0.94, abs=0.05)

# Percentages: ±1% tolerance
assert result.duplicate_percentage == pytest.approx(16.67, abs=1.0)

# Token counts: ±10% tolerance (tokenization varies)
assert result.token_count == pytest.approx(2847, rel=0.1)
```

### Conditional Matches
```python
# Warnings: check if expected subset exists
assert all(w in result.warnings for w in expected["warnings"])

# Recommendations: check severity and category
assert any(r["severity"] == "warning" for r in result.recommendations)
```

## Test Data Maintenance

### Adding New Fixtures

1. Create input data in appropriate `tests/fixtures/` subdirectory
2. Create expected output in `expected_outputs/`
3. Write test that uses both
4. Document purpose in README

### Modifying Fixtures

**Never modify existing fixtures without:**
1. Updating all dependent tests
2. Documenting the reason
3. Running full test suite
4. Updating version/date in README

### Fixture Versioning

```
tests/fixtures/
├── v1/                    # Version 1 fixtures
│   ├── datasets/
│   └── projects/
├── v2/                    # Version 2 fixtures (if breaking changes)
└── current -> v1/         # Symlink to current version
```

## Continuous Integration

Every CI run must:
1. Load all fixtures
2. Run all analyzer tests
3. Compare against expected outputs
4. Fail if any assertion fails
5. Generate test coverage report

## Quality Gates

A feature cannot be merged unless:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Test coverage >80% for new code
- [ ] Fixtures are included
- [ ] Expected outputs are documented
- [ ] Edge cases are tested

## Debugging Failed Tests

When a test fails:
1. Compare actual vs expected output
2. Check if fixture is correct
3. Check if analyzer logic changed
4. Update fixture only if analyzer is wrong
5. Update analyzer if fixture represents correct behavior
6. Never update both to "make it pass"

## Example: Complete Test Flow

```python
def test_complete_dataset_analysis():
    """End-to-end test of dataset analyzer with fixtures."""
    # Load input
    dataset_path = tests.fixtures / "datasets/low_quality/sample.jsonl"
    dataset = Dataset.load(dataset_path)
    
    # Run analyzer
    analyzer = DatasetAnalyzer()
    result = analyzer.analyze(dataset)
    
    # Load expected
    expected_path = tests.fixtures / "expected_outputs/dataset_analysis/low_quality_expected.json"
    expected = json.loads(expected_path.read_text())
    
    # Assertions
    assert result.sample_count == expected["sample_count"]
    assert result.quality_score == pytest.approx(expected["quality_score"], abs=0.05)
    assert result.duplicate_percentage >= expected["duplicate_percentage"] * 0.9
    assert len(result.warnings) >= len(expected["warnings"])
    
    # Verify specific issues detected
    assert "duplicate" in " ".join(result.findings).lower()
    assert "missing" in " ".join(result.findings).lower()
```

## Conclusion

Sample data is not optional. It is required to:
- Prove features work correctly
- Prevent regressions
- Document expected behavior
- Enable confident refactoring
- Support continuous integration

**"If you can't test it with sample data, it's not ready."**
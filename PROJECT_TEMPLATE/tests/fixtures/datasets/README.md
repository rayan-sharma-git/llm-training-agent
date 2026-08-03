# Sample Datasets

## Purpose

These datasets verify that the Dataset Intelligence module correctly identifies quality issues, duplicates, formatting problems, and other characteristics.

## Datasets

### high_quality/

A well-formed instruction-following dataset suitable for fine-tuning.

**Expected characteristics:**
- No duplicates
- Consistent formatting
- Complete records
- Clear instructions
- Varied responses
- High quality score (>0.85)

**Use cases:**
- Verify analyzer recognizes good datasets
- Test that no false positives are reported
- Validate quality scoring for clean data

### low_quality/

A dataset with intentional problems for testing detection capabilities.

**Expected issues:**
- 15% duplicate records
- 10% near-duplicates
- 5% empty responses
- 8% missing fields
- Inconsistent formatting
- Mixed languages
- Low quality score (<0.50)

**Use cases:**
- Verify duplicate detection
- Test missing field detection
- Validate quality scoring for poor data
- Ensure recommendations are generated

### edge_cases/

Boundary conditions and unusual scenarios.

**Expected characteristics:**
- Very short responses (<5 tokens)
- Very long responses (>2000 tokens)
- Single record dataset
- Empty dataset
- Malformed JSON
- Unicode edge cases
- Special characters

**Use cases:**
- Test boundary conditions
- Verify error handling
- Ensure no crashes on unusual input
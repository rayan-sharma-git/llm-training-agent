# Sample Prompt Templates

## Purpose

These prompt templates verify that the Prompt Intelligence module correctly evaluates prompt quality, identifies issues, and provides improvement recommendations.

## Templates

### effective/

Well-crafted prompt templates suitable for fine-tuning.

**Expected characteristics:**
- Clear, specific instructions
- Consistent formatting
- Appropriate complexity
- No ambiguity
- Well-defined role
- Quality score >0.80

### problematic/

Templates with intentional issues for testing detection.

**Expected issues:**
- Conflicting instructions
- Missing placeholders
- Ambiguous language
- Inconsistent formatting
- Prompt leakage
- Quality score <0.60

## Usage

Each template should be tested against the Prompt Intelligence analyzer to verify:
1. Quality scores are within expected ranges
2. Issues are correctly identified
3. Recommendations are relevant
4. Confidence scores reflect certainty
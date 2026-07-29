# REVIEW_CHECKLIST.md

Version: 1.0

---

# Purpose

This document defines the review process for every deliverable.

The objective is to detect issues before they reach production.

Every document, design, API, prompt, test and source code must be reviewed.

Never skip review.

---

# Review Workflow

For every deliverable:

Create

↓

Self Review

↓

Improve

↓

Reviewer Review

↓

Fix Issues

↓

Final Review

↓

Engineer Approval

↓

Continue

Never present the first draft.

---

# Review Levels

Level 1 — Self Review

Performed by the creator.

Level 2 — AI Reviewer

Performed by an independent reviewer agent.

Level 3 — Human Engineer

Final approval.

Every deliverable should pass all three levels.

---

# General Checklist

## Requirements

☐ Every requirement has been addressed.

☐ No requirement has been ignored.

☐ No unnecessary feature has been added.

---

## Completeness

☐ Deliverable is complete.

☐ No placeholders remain.

☐ No TODOs remain without justification.

---

## Correctness

☐ Logic is correct.

☐ Assumptions are documented.

☐ Edge cases considered.

---

## Consistency

☐ Matches project architecture.

☐ Matches previous documentation.

☐ Terminology is consistent.

---

## Readability

☐ Easy to understand.

☐ Clear naming.

☐ Clear structure.

---

## Maintainability

☐ Modular.

☐ Low duplication.

☐ Easy to modify.

---

## Scalability

☐ Design allows future growth.

☐ No obvious scalability issues.

---

## Security

☐ Inputs validated.

☐ Secrets protected.

☐ No obvious vulnerabilities.

---

## Performance

☐ No unnecessary work.

☐ Reasonable algorithms.

☐ No obvious bottlenecks.

---

## Testing

☐ Tests exist.

☐ Tests pass.

☐ Edge cases tested.

☐ Regression risk considered.

---

## Documentation

☐ Documentation updated.

☐ Public interfaces documented.

☐ Examples included where useful.

---

# Deliverable-Specific Checks

## Requirements Analysis

☐ Functional requirements complete.

☐ Non-functional requirements complete.

☐ Risks identified.

☐ Assumptions documented.

☐ Ambiguities highlighted.

---

## AI Design

☐ Architecture complete.

☐ Modules clearly defined.

☐ Data flow explained.

☐ Failure handling included.

☐ Memory strategy defined.

---

## Prompt Design

☐ System prompt defined.

☐ Guardrails defined.

☐ Context strategy defined.

☐ Output strategy defined.

☐ Hallucination prevention included.

---

## API Specification

☐ Endpoints complete.

☐ Request models complete.

☐ Response models complete.

☐ Error responses documented.

☐ Validation rules documented.

---

## JSON Schemas

☐ Required fields defined.

☐ Optional fields defined.

☐ Validation rules defined.

☐ Error schema included.

---

## Source Code

☐ Builds successfully.

☐ Coding standards followed.

☐ Error handling present.

☐ No dead code.

☐ No duplicated logic.

☐ Logging appropriate.

---

## Tests

☐ Unit tests complete.

☐ Integration tests complete.

☐ Regression tests pass.

☐ AI evaluation complete (if applicable).

---

# Review Decision

Choose one.

✅ APPROVED

Quality is production ready.

---

🟡 APPROVED WITH MINOR CHANGES

Small improvements only.

No architectural changes required.

---

🟠 REQUIRES REVISION

Important issues found.

Must be corrected before approval.

---

🔴 REJECTED

Major issues.

Do not continue.

Return to implementation.

---

# Reviewer Report Format

Always report using this structure.

Overall Score:

Requirements Coverage:

Strengths:

Weaknesses:

Required Changes:

Recommended Improvements:

Decision:

Next Action:

---

# Quality Target

Internal AI Review Target:

9/10 or higher

Human Approval Target:

Production Ready

Anything below 9/10 should normally be improved before reaching the engineer.

---

# Golden Rule

The purpose of review is not to criticize.

The purpose of review is to improve quality while reducing the engineer's workload.
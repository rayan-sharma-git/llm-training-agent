# CODING_STANDARDS.md

Version: 1.0

---

# Purpose

This document defines universal coding standards for every software project.

The objective is to produce code that is:

- Correct
- Readable
- Maintainable
- Testable
- Extensible
- Production Ready

These standards apply regardless of programming language or framework.

---

# Engineering Principles

Always optimize in this order:

1. Correctness
2. Simplicity
3. Readability
4. Maintainability
5. Testability
6. Reliability
7. Performance

Never sacrifice correctness for performance.

---

# File Organization

Each file should have one primary responsibility.

Avoid large files.

Split responsibilities into logical modules.

Avoid "God Classes" and "God Files."

---

# Naming Conventions

Names should clearly describe purpose.

Good examples:

BirdProfileService

MealRecommendationEngine

WeightAnalysisService

Bad examples:

Manager

Utils

Helper

Data2

Stuff

Temp

Avoid abbreviations unless they are industry standard.

---

# Functions

Every function should:

- Do one thing.
- Have one responsibility.
- Be easy to understand.
- Have descriptive names.

Avoid long functions.

Break complex logic into smaller functions.

---

# Parameters

Keep parameter lists short.

Prefer structured objects over many parameters.

Avoid boolean flags that change behavior.

---

# Variables

Use descriptive variable names.

Avoid single-letter variables except simple loops.

Avoid magic numbers.

Replace them with named constants.

---

# Comments

Write code that explains itself.

Use comments only when explaining:

- Why something exists.
- Complex business rules.
- Non-obvious decisions.

Never comment obvious code.

---

# Error Handling

Never silently ignore errors.

Return meaningful error messages.

Validate inputs.

Handle unexpected failures gracefully.

Never expose internal implementation details.

---

# Logging

Log:

- important events
- warnings
- failures
- unexpected conditions

Never log:

- passwords
- API keys
- secrets
- personal data

---

# Dependencies

Before adding a dependency ask:

Can existing code solve this?

Can the standard library solve this?

Is this dependency maintained?

Is it necessary?

Prefer fewer dependencies.

---

# Configuration

Never hardcode:

- API keys
- passwords
- URLs
- secrets
- environment-specific values

Use configuration files or environment variables.

---

# Code Duplication

Never duplicate business logic.

Extract reusable components.

Prefer composition over duplication.

---

# Architecture

Respect existing architecture.

Do not introduce new architectural patterns without justification.

Maintain consistency across the project.

---

# Readability

Code should read like English.

Prefer clarity over cleverness.

Another engineer should understand the code without explanation.

---

# Performance

Optimize only after correctness.

Avoid premature optimization.

Measure before optimizing.

---

# Security

Validate all external input.

Sanitize user input.

Never trust client-side validation.

Protect sensitive information.

Follow the principle of least privilege.

---

# Testing

Every new feature should include tests.

Test:

- expected behavior
- edge cases
- failure scenarios

Never merge untested functionality.

---

# Documentation

Public modules should be documented.

Keep documentation synchronized with implementation.

Outdated documentation is considered a defect.

---

# Code Review Checklist

Before considering code complete, verify:

✓ Requirements satisfied

✓ Naming is clear

✓ No duplicated logic

✓ Error handling exists

✓ Tests included

✓ Documentation updated

✓ No unused code

✓ No obvious performance issues

✓ No security concerns

✓ Readability maintained

---

# Definition of Production Ready

Production-ready code is:

- Correct
- Reviewed
- Tested
- Documented
- Maintainable
- Secure
- Consistent
- Free from known critical defects

Never declare code production-ready unless all conditions are satisfied.
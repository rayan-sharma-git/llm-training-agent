# PROMPT_LIBRARY.md

Version: 1.0

---

# Purpose

This document contains universal prompts that can be reused across software engineering projects.

These prompts are intentionally project-independent.

Always adapt them using the current project requirements.

---

# Universal Rule

Before executing any prompt:

1. Read the complete repository.
2. Read requirements.md.
3. Read all approved documentation.
4. Understand existing architecture.
5. Do not assume missing information.
6. Follow AGENTS.md.

---

# Prompt 1 — Start Project

Read the complete repository including requirements.md and all approved documentation.

Understand the project before making changes.

Follow AGENTS.md exactly.

Create a project execution plan.

Break the project into independent deliverables.

Present only the first deliverable.

Wait for approval before continuing.

---

# Prompt 2 — Continue Workflow

The previous deliverable has been approved.

Automatically continue to the next deliverable according to AGENTS.md.

Do not repeat completed work.

Do not skip steps.

---

# Prompt 3 — Improve Deliverable

Review the current deliverable.

Find weaknesses.

Improve correctness.

Improve readability.

Improve maintainability.

Improve documentation.

Perform another self-review.

Present the improved version.

---

# Prompt 4 — Architecture Review

Review the architecture.

Check:

- scalability
- modularity
- maintainability
- extensibility
- consistency

Identify weaknesses.

Recommend improvements.

Do not implement changes.

---

# Prompt 5 — Code Review

Review the entire codebase.

Check:

- bugs
- security
- readability
- maintainability
- duplication
- performance
- architecture consistency

Assign a quality score.

Recommend improvements.

---

# Prompt 6 — Documentation Review

Review every documentation file.

Verify:

- completeness
- consistency
- correctness
- formatting
- synchronization with implementation

List missing documentation.

---

# Prompt 7 — Test Review

Review all tests.

Identify:

- missing edge cases
- missing regression tests
- weak assertions
- duplicated tests

Recommend improvements.

---

# Prompt 8 — Refactor

Refactor the affected code.

Do not change behavior.

Improve:

- readability
- maintainability
- modularity

Run tests after refactoring.

---

# Prompt 9 — Bug Fix

Investigate the reported issue.

Identify the root cause.

Fix the issue.

Run all affected tests.

Confirm the issue is resolved.

Explain what changed.

---

# Prompt 10 — Feature Implementation

Implement the approved feature.

Follow the approved architecture.

Follow coding standards.

Update documentation.

Run tests.

Self-review before presenting.

---

# Prompt 11 — Final Validation

Perform a complete project audit.

Verify:

- requirements satisfied
- documentation complete
- architecture respected
- tests passing
- build successful
- coding standards followed

List any remaining issues.

---

# Prompt 12 — Release Readiness

Determine whether the project is production ready.

Evaluate:

- correctness
- maintainability
- security
- testing
- documentation
- reliability

Provide:

Overall Score

Remaining Risks

Blocking Issues

Recommendation

---

# Prompt 13 — Lessons Learned

Review the completed project.

Identify:

- engineering successes
- mistakes
- recurring problems
- automation opportunities
- workflow improvements

Recommend updates to AGENTS.md.

---

# Prompt 14 — Daily Progress Report

Generate a concise engineering status report.

Format:

Completed

Current

Next

Risks

Blockers

ETA

---

# Prompt 15 — Repository Audit

Review the repository structure.

Verify:

- organization
- naming consistency
- documentation
- unnecessary files
- duplicate code
- missing tests

Recommend improvements.

---

# Golden Rule

These prompts are starting points.

AGENTS.md remains the primary workflow document.

Whenever AGENTS.md conflicts with a prompt, AGENTS.md takes precedence.

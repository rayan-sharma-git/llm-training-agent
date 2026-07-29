# requirements.md

# LLM Training Agent

Version: 1.0

Author: Project Owner

Status: Draft

---

# 1. Purpose

This document defines the complete engineering requirements for the **LLM Training Agent** project.

This document serves as the single source of truth for development.

The implementation agent (Cline) must strictly follow this document.

If implementation decisions are required that are not explicitly defined here, prefer:

* clean architecture
* maintainability
* scalability
* extensibility
* production readiness

over shortcuts.

---

# 2. Terminology

To avoid ambiguity, the following definitions must always be used throughout development.

## Implementation Agent

The term **Implementation Agent** refers to **Cline**.

Whenever this document instructs the "Implementation Agent", it is referring to Cline.

The Implementation Agent is responsible for designing, implementing, testing, documenting and maintaining the codebase according to this specification.

---

## Product Agent

The term **Product Agent** refers to the software being built.

The Product Agent is the VS Code extension together with its backend services.

The Product Agent is the final software users interact with.

The Product Agent must never be confused with the Implementation Agent.

---

## User

A User is an ML Engineer, AI Engineer, Research Engineer or Developer using the Product Agent inside Visual Studio Code.

---

# 3. Product Vision

The Product Agent is an AI-powered engineering assistant for LLM fine-tuning.

Its purpose is to analyze an entire fine-tuning project before training begins.

Instead of acting as a chatbot, it functions as an experienced ML engineer capable of reviewing:

* datasets
* prompts
* model choices
* hyperparameters
* training pipeline
* project structure

The Product Agent identifies weaknesses, explains issues, recommends improvements and—with explicit user approval—can automatically modify the project.

The Product Agent should reduce:

* failed experiments
* wasted GPU time
* unnecessary retraining
* trial-and-error

while improving engineering productivity.

---

# 4. Product Goals

The Product Agent shall:

* understand an entire fine-tuning project
* provide actionable engineering recommendations
* estimate training cost
* estimate project readiness
* compare alternative models
* analyze datasets
* analyze prompts
* analyze hyperparameters
* predict likely training behaviour
* maintain experiment history
* improve developer productivity
* integrate naturally into Visual Studio Code

The Product Agent shall not attempt to replace the developer.

The developer always remains in control.

---

# 5. Design Philosophy

The Product Agent must follow these principles.

## Safety

Never silently modify user files.

Every modification requires explicit user approval.

---

## Explainability

Every recommendation must include:

* why
* expected benefit
* confidence
* possible drawbacks

Recommendations without explanations are unacceptable.

---

## Transparency

Whenever uncertainty exists, communicate confidence levels.

Do not present speculation as fact.

---

## Professional Engineering

The Product Agent must behave like a senior ML engineer reviewing a pull request.

It should never behave like a generic conversational chatbot.

---

## Modular Design

Every major capability must exist as an independent module.

Future contributors must be able to add modules without modifying unrelated components.

---

## Open Source First

The project is intended to become a long-term open-source project.

All architectural decisions must prioritize readability, extensibility and community contributions.

Avoid tightly coupled code.

Avoid hidden dependencies.

Favor interfaces over implementations.

---

# 6. Success Criteria

The project is considered successful only if it satisfies all of the following.

* Successfully builds on Windows, macOS and Linux.

* Can be packaged as a VS Code extension.

* Can be published to the VS Code Marketplace.

* Can be cloned and built by contributors.

* Contains automated testing.

* Contains documentation.

* Supports future contributors.

* Has a clean modular architecture.

* Produces useful recommendations for real LLM projects.

* Maintains production-level code quality.

Prototype-quality code is unacceptable.

---

# 7. Scope

Version 1 includes:

* VS Code Extension
* Python Backend
* Project Scanner
* Dataset Intelligence
* Prompt Intelligence
* Hyperparameter Advisor
* Base Model Advisor
* Prediction Engine
* Cost Estimator
* Experiment Tracker
* Recommendation Engine
* AI Chat Interface
* Safe Project Editing
* Report Generation

Future versions may introduce additional capabilities without breaking existing APIs.

---

# 8. Out of Scope

Version 1 shall not include:

* cloud-hosted training
* automatic model fine-tuning
* model serving
* inference hosting
* GPU orchestration
* distributed training
* remote cluster management

The Product Agent analyzes projects.

It does not perform model training itself.

---

# 9. Development Philosophy

The Implementation Agent (Cline) shall never attempt to generate the complete application in one step.

Development must be milestone driven.

Each milestone must:

* compile successfully
* pass tests
* remain deployable
* be documented

No milestone may leave the repository in a broken state.

The repository must remain functional after every completed milestone.

# 10. System Architecture

The Product Agent shall be developed using a modular client-server architecture.

The system shall consist of two independent applications:

1. VS Code Extension (Frontend)
2. Python Backend (Analysis Engine)

These components must remain loosely coupled and communicate only through well-defined APIs.

The VS Code Extension must never contain complex ML analysis logic.

The Python Backend must never depend on VS Code APIs.

---

# 11. High-Level Architecture

```
+---------------------------------------------------------+
|                    Visual Studio Code                   |
|                                                         |
|  +---------------------------------------------------+  |
|  |               Product Agent Extension             |  |
|  |                                                   |  |
|  | Sidebar                                           |  |
|  | Chat                                              |  |
|  | Commands                                          |  |
|  | Settings                                          |  |
|  | Report Viewer                                     |  |
|  | Diff Preview                                      |  |
|  +-----------------------+---------------------------+  |
|                          |                              |
+--------------------------|------------------------------+
                           |
                      HTTP / WebSocket
                           |
+--------------------------|------------------------------+
|                  Python Backend (FastAPI)              |
|                                                       |
| Project Scanner                                       |
| Dataset Intelligence                                  |
| Prompt Intelligence                                   |
| Hyperparameter Advisor                               |
| Base Model Advisor                                   |
| Prediction Engine                                    |
| Recommendation Engine                                |
| Experiment Tracker                                   |
| Cost Estimator                                       |
| Report Generator                                     |
+-------------------------------------------------------+
```

---

# 12. Technology Stack

The Implementation Agent shall use the following technologies unless there is a strong engineering justification to change them.

## VS Code Extension

Language

* TypeScript

Runtime

* Node.js

Package Manager

* npm

Framework

* Visual Studio Code Extension API

Testing

* Vitest or Jest

Linting

* ESLint

Formatting

* Prettier

---

## Backend

Language

* Python

Framework

* FastAPI

Data Validation

* Pydantic

Package Manager

* uv (preferred) or pip

Testing

* pytest

Formatting

* Ruff
* Black

Type Checking

* mypy (where practical)

---

## Storage

Initially:

SQLite

Later versions may support PostgreSQL without breaking the abstraction layer.

---

## AI Provider

The Product Agent shall support multiple providers.

The provider implementation must be abstracted.

Supported providers should include:

* OpenAI
* Anthropic
* Google Gemini
* OpenRouter
* Ollama (local)

The rest of the application must not depend on any single provider.

---

# 13. Project Structure

The repository shall follow a clean structure.

```
root/

backend/

extension/

shared/

docs/

examples/

tests/

.github/

scripts/
```

No unrelated files should exist in the repository root.

---

# 14. Backend Structure

The backend should follow feature-based organization.

Example:

```
backend/

api/

core/

config/

scanner/

analyzers/

dataset/

prompt/

hyperparameters/

models/

prediction/

recommendation/

experiments/

cost/

reports/

storage/

utils/

tests/
```

Every feature should be isolated.

Avoid large utility files containing unrelated functions.

---

# 15. Extension Structure

```
extension/

src/

commands/

sidebar/

chat/

views/

providers/

services/

settings/

state/

utils/

types/

tests/
```

Every folder should have a single responsibility.

---

# 16. Shared Module

Common data models should exist only once.

```
shared/

schemas/

types/

constants/

interfaces/
```

Avoid duplicating models between backend and extension whenever practical.

---

# 17. Communication

The extension shall communicate only through defined APIs.

The extension must never directly access backend internals.

Communication shall use:

REST for standard requests.

WebSocket for streaming responses where appropriate.

---

# 18. API Principles

Every endpoint must:

* return typed responses
* validate input
* validate output
* provide useful error messages
* support future versioning

Errors shall never expose internal stack traces to users.

---

# 19. Configuration

Configuration shall be separated from code.

Supported configuration sources:

* environment variables
* configuration files
* VS Code settings

No secrets may be hardcoded.

API keys shall never be committed.

---

# 20. Logging

The Product Agent shall implement structured logging.

Logs should support levels:

* Debug
* Info
* Warning
* Error
* Critical

Production logs should be concise.

Development logs may be verbose.

---

# 21. Error Handling

The Product Agent shall fail gracefully.

If one analyzer fails:

* remaining analyzers must continue when possible
* the user must receive a useful explanation
* partial reports should still be generated

The Product Agent must never crash because one module encounters an error.

---

# 22. Plugin Architecture

Every analyzer shall implement a common interface.

Examples:

* Dataset Analyzer
* Prompt Analyzer
* Hyperparameter Advisor
* Model Advisor
* Prediction Engine

The Recommendation Engine should interact only with interfaces, not concrete implementations.

Future contributors must be able to create new analyzers without modifying the existing core.

---

# 23. Dependency Injection

Avoid direct object construction where practical.

Major services should receive dependencies through constructors or dependency injection.

Avoid global state.

---

# 24. Performance

The Product Agent should remain responsive.

General targets:

* UI should remain interactive.
* Small projects should analyze in seconds.
* Long-running analysis should stream progress.
* Expensive operations should execute asynchronously.

The user should always know the current analysis status.

---

# 25. Scalability

The architecture should support future additions without requiring major rewrites.

Examples include:

* New fine-tuning frameworks
* Additional model providers
* New analyzers
* Enterprise integrations
* Cloud services
* Community-developed plugins

The initial architecture should anticipate long-term growth while keeping Version 1 simple.

# 26. Functional Requirements

This section defines the functional behavior of every major module.

Each module shall have a single responsibility.

Each module must expose a clear interface.

The Recommendation Engine shall combine outputs from all modules into a unified report.

---

# 27. Project Scanner

## Purpose

The Project Scanner is responsible for understanding the user's project before any analysis begins.

It acts as the entry point for the entire Product Agent.

---

## Responsibilities

The Project Scanner shall:

* Detect project type.
* Detect fine-tuning framework.
* Discover datasets.
* Discover configuration files.
* Discover prompt templates.
* Discover training scripts.
* Discover evaluation scripts.
* Detect base model.
* Detect LoRA or PEFT usage.
* Detect tokenizer configuration.
* Build an internal project representation.

---

## Supported Frameworks (Initial)

* Hugging Face Transformers
* PEFT
* TRL
* Unsloth
* Axolotl

The architecture must allow future framework support.

---

## Expected Output

The scanner should generate a structured project summary.

Example:

* Framework
* Base Model
* Dataset
* Tokenizer
* Training Script
* Prompt Template
* Configuration Files

The scanner should never modify files.

---

# 28. Dataset Intelligence

## Purpose

Evaluate the quality and consistency of training datasets.

---

## Responsibilities

Analyze:

* duplicates
* near duplicates
* empty records
* missing fields
* malformed records
* inconsistent formatting
* instruction consistency
* response consistency
* language consistency
* average response length
* token distribution
* response diversity
* dataset balance
* low-quality samples

---

## Output

The Dataset Intelligence module shall produce:

* Dataset Quality Score
* Identified Issues
* Severity Level
* Suggested Improvements

Every recommendation must include reasoning.

---

# 29. Prompt Intelligence

## Purpose

Evaluate prompt templates used for fine-tuning.

---

## Responsibilities

Analyze:

* clarity
* ambiguity
* consistency
* formatting
* instruction quality
* role definitions
* template correctness
* prompt complexity

Detect:

* conflicting instructions
* missing placeholders
* prompt leakage
* formatting mismatches

---

## Output

Return:

* Prompt Quality Score
* Identified Problems
* Suggested Improvements

---

# 30. Hyperparameter Advisor

## Purpose

Analyze training configuration and identify likely problems.

---

## Supported Configuration

Examples include:

* learning rate
* epochs
* batch size
* gradient accumulation
* warmup
* optimizer
* scheduler
* weight decay
* sequence length
* LoRA rank
* LoRA alpha
* LoRA dropout

---

## Responsibilities

Identify:

* overfitting risk
* underfitting risk
* unstable learning rate
* inefficient configuration
* excessive GPU usage
* likely convergence problems

Provide recommendations with explanations.

---

## Editing Support

The Product Agent may propose changes.

Actual file modifications require explicit user approval.

---

# 31. Base Model Advisor

## Purpose

Evaluate whether the selected base model matches the intended task.

---

## Responsibilities

Compare models based on:

* reasoning
* coding
* instruction following
* multilingual capability
* inference speed
* context length
* parameter count
* VRAM usage

Support comparison between multiple candidate models.

---

## Recommendations

Recommend alternatives where appropriate.

Explain trade-offs.

Never recommend a model without justification.

---

# 32. Fine-Tuning Outcome Prediction

## Purpose

Estimate likely training behavior before training begins.

---

## Important Limitation

The Product Agent shall NOT claim to predict exact model outputs.

Instead, estimate probabilities and expected behavior.

---

## Predictions

Estimate:

* instruction following
* hallucination risk
* reasoning quality
* response consistency
* response length
* creativity
* formatting consistency
* likely failure modes

Each prediction must include a confidence score.

---

# 33. Cost Estimator

## Purpose

Estimate required computational resources.

---

## Estimate

* estimated training time
* VRAM usage
* storage requirements
* checkpoint size
* hardware compatibility

If information is missing, clearly state assumptions.

---

# 34. Experiment Tracker

## Purpose

Maintain a history of previous experiments.

---

## Store

* dataset version
* model
* tokenizer
* hyperparameters
* metrics
* timestamps
* notes

Allow users to compare experiments.

Identify the best-performing runs.

---

# 35. Recommendation Engine

## Purpose

Produce one consolidated engineering report.

This module consumes outputs from all analyzers.

---

## Responsibilities

Prioritize recommendations.

Group related issues.

Estimate impact.

Provide confidence.

Explain every recommendation.

Avoid duplicate recommendations.

Rank recommendations by expected benefit.

---

# 36. AI Chat Interface

## Purpose

Allow users to interact naturally with the Product Agent.

---

## Examples

Users may ask:

* Why is my learning rate too high?
* Compare TinyLlama with Gemma.
* Why is my dataset quality low?
* Explain hallucination risk.
* Show all duplicate samples.

The Product Agent shall answer using project context.

Responses should reference analysis results whenever possible.

---

# 37. Safe Editing

The Product Agent may generate proposed modifications.

Examples:

* configuration updates
* prompt improvements
* dataset cleanup

The workflow shall always be:

Analyze

↓

Generate Changes

↓

Show Diff

↓

Request User Approval

↓

Apply Changes

↓

Support Undo

Automatic silent modification is prohibited.

---

# 38. Reports

Generate a comprehensive report containing:

* Executive Summary
* Project Health Score
* Training Readiness Score
* Confidence Level
* Dataset Findings
* Prompt Findings
* Hyperparameter Findings
* Model Findings
* Predictions
* Cost Estimates
* Recommended Actions

Reports should be exportable in future versions.

---

# 39. Acceptance Criteria

Every functional module is considered complete only when:

* Inputs are validated.
* Outputs are typed.
* Errors are handled gracefully.
* Unit tests exist.
* Documentation exists.
* Public interfaces are documented.
* The module integrates successfully with the Recommendation Engine.

# 40. User Experience Requirements

The Product Agent must provide a clean, professional experience suitable for software engineers.

The interface should prioritize clarity, speed, and discoverability.

The Product Agent must never overwhelm users with unnecessary information.

Advanced information should be expandable.

Important issues should be highlighted automatically.

---

# 41. VS Code Integration

The Product Agent shall integrate naturally with Visual Studio Code.

It shall support:

* Activity Bar Icon
* Sidebar View
* Command Palette
* Context Menus
* Notifications
* Progress Indicators
* Output Channel
* Settings Page

The extension should feel like a native VS Code feature.

---

# 42. Activity Bar

The extension shall create a dedicated Activity Bar icon.

Selecting the icon opens the Product Agent sidebar.

The icon should remain lightweight and recognizable.

---

# 43. Sidebar

The sidebar is the primary interface.

Sections should include:

Project Overview

Analysis

Recommendations

Experiments

Reports

Chat

Settings

Future sections may be added without redesigning the sidebar.

---

# 44. Project Overview

Display:

Current Project

Detected Framework

Detected Model

Dataset

Configuration

Training Framework

Project Health Score

Training Readiness Score

Last Analysis Time

Analysis Status

This information should update automatically after every successful analysis.

---

# 45. Analysis Panel

Allow users to start analyses.

Supported actions:

Analyze Entire Project

Analyze Dataset

Analyze Prompt

Analyze Hyperparameters

Analyze Base Model

Estimate Training Cost

Refresh Analysis

Cancel Running Analysis

Each action should display progress.

---

# 46. Recommendations Panel

Display prioritized recommendations.

Each recommendation shall include:

Title

Description

Reason

Expected Benefit

Confidence

Severity

Estimated Impact

Buttons:

Explain

Preview Changes

Apply

Dismiss

Recommendations should be grouped by category.

---

# 47. Report Viewer

Display a complete engineering report.

Sections:

Executive Summary

Project Health

Dataset

Prompt

Hyperparameters

Base Model

Predictions

Cost

Action Plan

The report should be searchable.

The report should support collapsing sections.

---

# 48. Experiment History

Display previous runs.

Each run should include:

Timestamp

Model

Dataset

Training Arguments

Metrics

Notes

Users should be able to compare experiments.

---

# 49. Chat Interface

Provide an engineering-focused conversational interface.

The Product Agent should answer questions about the current project.

Examples:

Explain this recommendation.

Compare TinyLlama with Gemma.

Why is this dataset quality low?

Show duplicate samples.

What happens if I increase LoRA rank?

The Product Agent should use analysis results before relying on general knowledge.

---

# 50. Diff Viewer

Before modifying files, display proposed changes.

The user must see exactly what will change.

The interface should resemble the native VS Code diff viewer.

Users must be able to:

Approve

Reject

Modify later

The Product Agent shall never bypass this step.

---

# 51. Notifications

Use notifications sparingly.

Examples:

Analysis Started

Analysis Complete

Analysis Failed

Changes Applied

Changes Cancelled

Experiment Saved

Notifications should never interrupt the user's workflow unnecessarily.

---

# 52. Progress Reporting

Long-running tasks must report progress.

Examples:

Scanning Project...

Analyzing Dataset...

Comparing Models...

Generating Recommendations...

Preparing Report...

If possible, display estimated remaining time.

---

# 53. Settings

The extension shall expose configurable settings.

Examples:

Preferred AI Provider

Model

Temperature

Backend URL

Automatic Analysis

Telemetry

Theme Preferences

Experimental Features

Every setting must include documentation.

---

# 54. Commands

Provide Command Palette commands.

Examples:

LLM Training Agent: Analyze Project

LLM Training Agent: Analyze Dataset

LLM Training Agent: Open Chat

LLM Training Agent: View Report

LLM Training Agent: View Experiments

LLM Training Agent: Settings

Commands should follow VS Code naming conventions.

---

# 55. Context Menus

Where appropriate, allow users to right-click:

Dataset files

Prompt templates

Training scripts

Configuration files

Available actions may include:

Analyze

Explain

Optimize

Compare

View Report

These actions should use the selected file as context.

---

# 56. Error Experience

Errors must be actionable.

Instead of:

"Analysis Failed"

Display:

What failed

Why it failed

Possible causes

Suggested fixes

Relevant log location

The user should never receive unexplained failures.

---

# 57. Accessibility

The interface should support:

Keyboard navigation

Screen readers where practical

High contrast themes

Light theme

Dark theme

Responsive layouts

Avoid color as the only indicator of status.

---

# 58. User Workflow

Typical workflow:

1. Open an LLM fine-tuning project.

2. Open the Product Agent.

3. Click "Analyze Project."

4. The Product Agent scans the repository.

5. Individual analyzers execute.

6. Results are merged into one report.

7. Recommendations are displayed.

8. The user explores findings.

9. The user asks follow-up questions through chat.

10. The user previews suggested changes.

11. The user approves selected changes.

12. The Product Agent applies approved modifications.

13. The user proceeds with training.

The Product Agent should reduce the number of manual engineering decisions while ensuring the user remains in complete control.

---

# 59. Acceptance Criteria

The UI is considered complete only if:

* Navigation is intuitive.
* Every feature is discoverable.
* Long operations display progress.
* File modifications require approval.
* Reports are readable.
* Chat understands project context.
* UI remains responsive during analysis.
* The extension follows VS Code design conventions.
* New features can be added without redesigning the interface.

# 60. AI Architecture

The Product Agent shall use a modular intelligence pipeline.

The Product Agent must not rely on a single LLM prompt to analyze an entire project.

Instead, every analysis shall be performed by specialized modules.

The Recommendation Engine shall combine their outputs into one final report.

---

# 61. Intelligence Pipeline

The Product Agent shall execute analysis in the following order:

Project Scanner

↓

Project Context Builder

↓

Dataset Intelligence

↓

Prompt Intelligence

↓

Hyperparameter Advisor

↓

Base Model Advisor

↓

Cost Estimator

↓

Prediction Engine

↓

Recommendation Engine

↓

Report Generator

↓

AI Chat Context

Each stage must receive structured input from previous stages.

Avoid passing raw text whenever structured data is available.

---

# 62. Context Builder

## Purpose

Create a single structured representation of the user's project.

The Context Builder should combine information discovered during scanning.

Examples include:

* detected framework
* detected model
* tokenizer
* dataset statistics
* prompt templates
* configuration
* training arguments
* project metadata

All downstream modules should consume this context rather than independently rescanning the project.

---

# 63. Analyzer Interface

Every analyzer shall implement a common interface.

Example responsibilities:

Input

* Project Context

Output

* Findings
* Warnings
* Recommendations
* Confidence
* Supporting Evidence

Every analyzer must be independently testable.

---

# 64. Recommendation Format

Every recommendation shall include:

Unique Identifier

Category

Severity

Confidence

Title

Description

Evidence

Expected Benefit

Possible Drawbacks

Suggested Actions

Files Affected

Estimated Impact

Recommendations without evidence are not acceptable.

---

# 65. Confidence Scoring

Every prediction or recommendation shall include a confidence score.

Possible values:

Very High

High

Medium

Low

Very Low

Confidence must be based on available evidence.

Never fabricate certainty.

If insufficient information exists, explicitly communicate uncertainty.

---

# 66. Evidence Collection

Every recommendation must reference supporting evidence.

Examples:

* Dataset statistics
* Hyperparameter values
* Prompt structure
* Model capabilities
* Project configuration

Evidence should be traceable.

The user should always understand why a recommendation was generated.

---

# 67. AI Provider Abstraction

The Product Agent shall not depend on a single LLM provider.

Implement a provider abstraction layer.

Supported providers should include:

* OpenAI
* Anthropic
* Google Gemini
* OpenRouter
* Ollama

Adding a new provider should require implementing only the provider interface.

Business logic must remain unchanged.

---

# 68. Prompt Management

All prompts used by the Product Agent shall be stored separately from application logic.

Do not hardcode prompts inside source files.

Requirements:

* Versioned
* Documented
* Reusable
* Easy to modify

Future prompt improvements should not require code changes.

---

# 69. Reasoning Strategy

The Product Agent should reason in stages.

Stage 1

Collect facts.

Stage 2

Generate observations.

Stage 3

Generate recommendations.

Stage 4

Prioritize recommendations.

Stage 5

Generate final report.

Avoid combining all reasoning into one LLM request.

---

# 70. Structured Outputs

Every analyzer should produce structured outputs.

Avoid returning free-form text whenever structured data is possible.

Examples:

Scores

Warnings

Recommendations

Evidence

Confidence

Affected Files

Structured outputs improve testing, reliability and future automation.

---

# 71. Recommendation Prioritization

The Recommendation Engine shall rank recommendations using factors including:

Severity

Confidence

Expected Impact

Engineering Effort

Estimated Training Savings

Potential Quality Improvement

Users should see the most valuable recommendations first.

---

# 72. Explainability

Every recommendation shall answer:

What is wrong?

Why is it wrong?

How was this determined?

How should it be fixed?

Why is this fix recommended?

What benefit is expected?

The Product Agent should educate users rather than simply issuing warnings.

---

# 73. AI Chat Context

The AI Chat shall have access to:

Project Context

Analysis Results

Reports

Recommendations

Experiment History

Approved Changes

The Product Agent should answer questions using project-specific context before relying on general LLM knowledge.

---

# 74. Hallucination Prevention

The Product Agent shall distinguish between:

Verified Facts

Reasonable Inferences

Speculation

Recommendations

If the Product Agent is uncertain, it must communicate uncertainty rather than invent information.

---

# 75. Failure Handling

If an analyzer fails:

* Record the failure.
* Continue remaining analyzers where possible.
* Notify the user.
* Mark affected recommendations with reduced confidence.

One module failing must not prevent the Product Agent from generating a useful report.

---

# 76. Future Intelligence

The architecture shall allow future additions including:

* ML-based prediction models
* Custom recommendation engines
* Retrieval-Augmented Generation (RAG)
* Organization-specific knowledge bases
* Community-developed analyzers
* Domain-specific plugins

These additions should require minimal changes to the existing architecture.

---

# 77. Acceptance Criteria

The AI architecture is considered complete only if:

* Every analyzer is independent.
* Recommendations include evidence.
* Confidence is communicated.
* AI providers are interchangeable.
* Prompts are externalized.
* Structured outputs are used.
* The Recommendation Engine combines analyzer outputs consistently.
* The Product Agent remains explainable and testable.

# 78. Development Standards

The Implementation Agent (Cline) shall develop this project as production software.

Prototype-quality code is unacceptable.

Every implementation decision should prioritize:

* readability
* maintainability
* scalability
* extensibility
* testability

The repository should resemble a mature open-source project rather than a personal project.

---

# 79. Coding Standards

All source code shall follow consistent conventions.

Requirements:

* meaningful naming
* small focused functions
* single responsibility
* minimal code duplication
* explicit typing
* descriptive comments where necessary

Avoid:

* magic numbers
* giant classes
* giant functions
* deeply nested logic
* hidden side effects

Code should be understandable by a contributor reading it for the first time.

---

# 80. Documentation Standards

Every major module shall contain documentation.

Documentation should explain:

Purpose

Responsibilities

Inputs

Outputs

Dependencies

Extension points

Limitations

Examples

Documentation should evolve together with the implementation.

---

# 81. Repository Documentation

The repository shall contain:

README.md

CONTRIBUTING.md

ARCHITECTURE.md

API.md

DEVELOPMENT.md

ROADMAP.md

CHANGELOG.md

CODE_OF_CONDUCT.md

SECURITY.md

LICENSE

Every document should remain updated.

---

# 82. Git Standards

The Implementation Agent shall use logical commits.

Each commit should implement one coherent change.

Commit messages should follow Conventional Commits.

Examples:

feat:

fix:

docs:

refactor:

test:

ci:

build:

style:

chore:

Avoid extremely large commits.

---

# 83. Branch Strategy

Recommended branches:

main

develop

feature/*

bugfix/*

release/*

hotfix/*

The main branch should always remain deployable.

---

# 84. Testing Strategy

Testing is mandatory.

Every major module shall include tests.

Testing levels:

Unit Tests

Integration Tests

End-to-End Tests

Regression Tests

The Product Agent should never rely solely on manual testing.

---

# 85. Test Coverage

The Implementation Agent should maximize meaningful coverage.

Priority:

Business logic

Analyzer outputs

Recommendation generation

Configuration parsing

API validation

Avoid testing trivial getters or boilerplate.

---

# 86. Continuous Integration

GitHub Actions shall automatically perform:

Install dependencies

Lint

Format verification

Run unit tests

Run integration tests

Build extension

Build backend

Verify packaging

The CI pipeline must fail if any required check fails.

---

# 87. Code Quality

Automatically enforce:

Formatting

Linting

Static analysis

Type checking

Import ordering

Dead code detection where practical

No pull request should reduce overall quality.

---

# 88. Security

The Product Agent shall follow secure development practices.

Requirements:

Never store API keys in source code.

Never log secrets.

Validate all external input.

Sanitize file operations.

Avoid arbitrary code execution.

Restrict filesystem modifications to approved actions.

Protect against path traversal attacks.

---

# 89. Privacy

User projects belong to the user.

The Product Agent shall not transmit project contents to external services without user consent.

If cloud AI providers are used, clearly indicate:

* what data is sent
* which provider receives it
* why it is required

Support local models where practical.

---

# 90. Telemetry

Telemetry shall be disabled by default.

If telemetry is implemented:

Users must explicitly opt in.

Document:

Collected data

Purpose

Retention

No source code or datasets may be collected without explicit permission.

---

# 91. Open Source Requirements

The project shall be designed for long-term community development.

Requirements:

Clear architecture

Contributor-friendly structure

Good documentation

Easy onboarding

Stable public interfaces

Meaningful issue labels

Template-based issues

Template-based pull requests

Contributor recognition

---

# 92. Extensibility

Contributors should be able to add:

New analyzers

New AI providers

New report generators

New recommendation strategies

New training framework support

New prediction engines

Without modifying existing core modules.

Favor interfaces over inheritance.

---

# 93. Versioning

Use Semantic Versioning.

Examples:

1.0.0

1.1.0

2.0.0

Breaking changes must be documented.

---

# 94. Releases

Each release shall include:

Release notes

Updated changelog

Migration notes (if needed)

Documentation updates

Version tags

Marketplace package

GitHub release

---

# 95. Deployment

The Product Agent shall support:

Development builds

Production builds

Marketplace publishing

Local backend execution

Cross-platform installation

Deployment should require minimal manual configuration.

---

# 96. Marketplace Readiness

Before the first public release, verify:

Extension metadata

Icons

Screenshots

Description

Keywords

License

Privacy policy (if required)

Repository links

Issue tracker

Documentation links

Version compatibility

The extension should meet Visual Studio Marketplace publishing requirements.

---

# 97. Community Management

Prepare the repository for open-source collaboration.

Include:

Good First Issues

Help Wanted labels

Feature Requests

Bug Reports

Discussions

Project Roadmap

Contributor Guide

Community members should understand how to contribute within minutes.

---

# 98. Definition of Done

A feature is considered complete only if:

Implementation is finished.

Tests pass.

Documentation exists.

Code review completed.

No known critical defects.

CI passes.

The project builds successfully.

The feature integrates with existing architecture.

No placeholder implementations remain.

---

# 99. Final Deliverables

The completed project shall include:

Production-ready VS Code Extension

Production-ready Python Backend

Complete documentation

Automated tests

GitHub Actions CI

Marketplace-ready package

Example projects

Developer documentation

Contribution documentation

Architecture documentation

Release process

Deployment guide

Open-source repository ready for public launch

The Product Agent should be suitable for real-world ML engineers and capable of growing into a mature community-driven open-source project.

# 100. Implementation Roadmap

The Implementation Agent (Cline) shall **NOT** attempt to build the entire Product Agent in a single implementation.

The project shall be implemented incrementally through milestones.

Each milestone must satisfy the following before proceeding:

* Successfully builds
* Successfully runs
* Successfully passes all tests
* Documentation updated
* No placeholder code
* No broken features
* CI passes

Every milestone must leave the repository in a production-ready state.

---

# Milestone 1 — Project Foundation

## Goal

Establish the repository, architecture and development environment.

## Deliverables

* Repository initialization
* Folder structure
* VS Code Extension scaffold
* FastAPI backend scaffold
* Shared interfaces
* Configuration system
* Logging system
* GitHub Actions
* Linting
* Formatting
* Testing frameworks
* Documentation skeleton

## Acceptance Criteria

* Extension launches successfully.
* Backend starts successfully.
* CI passes.
* Documentation exists.
* No analyzer implemented yet.

---

# Milestone 2 — Extension Shell

## Goal

Build the complete VS Code user interface.

## Deliverables

* Activity Bar
* Sidebar
* Command Palette integration
* Settings
* Status Bar
* Output Channel
* Progress Notifications
* Chat UI
* Report Viewer
* Placeholder pages

Backend integration is not required yet.

## Acceptance Criteria

The extension should look complete even if no intelligence exists yet.

---

# Milestone 3 — Backend Infrastructure

## Goal

Create backend services.

## Deliverables

* FastAPI
* API versioning
* Health endpoint
* Configuration
* Dependency injection
* Error handling
* Logging
* Request validation
* Response validation

## Acceptance Criteria

Backend is production ready.

---

# Milestone 4 — Project Scanner

## Goal

Teach the Product Agent to understand projects.

## Deliverables

Detect:

* framework
* datasets
* prompts
* configs
* tokenizer
* model
* LoRA
* training scripts

Produce ProjectContext.

## Acceptance Criteria

Scanner successfully analyzes multiple sample projects.

---

# Milestone 5 — Dataset Intelligence

## Goal

Analyze datasets.

Implement:

* duplicate detection
* near duplicate detection
* quality score
* token statistics
* consistency analysis
* formatting validation
* missing values
* dataset report

## Acceptance Criteria

Dataset reports are accurate.

---

# Milestone 6 — Prompt Intelligence

Implement:

* prompt quality
* ambiguity
* consistency
* formatting
* template validation

Acceptance:

Prompt analysis integrated with reports.

---

# Milestone 7 — Hyperparameter Advisor

Implement:

* learning rate analysis
* epoch analysis
* batch size
* scheduler
* optimizer
* LoRA analysis
* overfitting prediction
* underfitting prediction

Acceptance:

Generate engineering recommendations.

---

# Milestone 8 — Base Model Advisor

Implement support for:

* TinyLlama
* Llama
* Gemma
* Mistral
* Qwen

Compare:

* reasoning
* coding
* speed
* VRAM
* context
* multilingual

Acceptance:

Produce comparison reports.

---

# Milestone 9 — Cost Estimator

Estimate:

* training duration
* VRAM
* storage
* checkpoint size
* GPU compatibility

Acceptance:

Reports generated from project context.

---

# Milestone 10 — Prediction Engine

Implement prediction system.

Estimate:

* instruction following
* hallucination
* response consistency
* response quality
* reasoning ability
* likely failure modes

Every prediction must include:

* explanation
* confidence
* evidence

Do NOT claim certainty.

Acceptance:

Prediction integrates into reports.

---

# Milestone 11 — Recommendation Engine

Merge outputs from all analyzers.

Generate:

* Project Health Score
* Training Readiness Score
* Action Plan
* Prioritized Recommendations

Acceptance:

Single engineering report generated.

---

# Milestone 12 — AI Chat

Implement project-aware chat.

The Product Agent should answer questions using:

* ProjectContext
* Reports
* Recommendations
* Experiment history

Acceptance:

Context-aware conversations.

---

# Milestone 13 — Safe Editing

Implement:

* diff generation
* preview
* approval
* apply
* rollback

No automatic modification allowed.

Acceptance:

Every edit requires user approval.

---

# Milestone 14 — Experiment Tracker

Implement:

* history
* comparison
* metrics
* best runs
* notes

Acceptance:

Users can compare experiments.

---

# Milestone 15 — Polish

Improve:

performance

UX

error handling

documentation

logging

testing

code quality

Acceptance:

No major usability issues remain.

---

# Milestone 16 — Open Source Preparation

Create:

README

CONTRIBUTING

CODE_OF_CONDUCT

SECURITY

ROADMAP

Issue Templates

PR Templates

GitHub Labels

Architecture diagrams

Contribution guide

Acceptance:

Repository ready for community contributions.

---

# Milestone 17 — Marketplace Preparation

Prepare:

icons

branding

screenshots

description

keywords

license

privacy

versioning

packaging

publisher configuration

Acceptance:

Extension is publishable.

---

# Milestone 18 — Version 1.0 Release

Perform final verification.

Checklist:

✓ Build passes

✓ Tests pass

✓ CI passes

✓ Extension packaged

✓ Backend packaged

✓ Documentation complete

✓ Examples included

✓ Marketplace ready

✓ GitHub ready

✓ Repository public

The Product Agent is now considered Version 1.0.

---

# 101. Engineering Rules

Throughout development the Implementation Agent (Cline) shall follow these rules.

1. Never generate placeholder code.

2. Never leave TODO implementations.

3. Never duplicate logic.

4. Refactor when necessary.

5. Prefer composition over inheritance.

6. Keep modules independent.

7. Write tests with every feature.

8. Keep documentation synchronized.

9. Keep APIs stable.

10. Never silently modify user projects.

11. Never sacrifice architecture for speed.

12. Never claim unsupported ML capabilities.

13. Clearly distinguish:

* measured values,
* deterministic analysis,
* heuristic recommendations,
* AI-generated suggestions.

14. Every recommendation must be explainable.

15. Every file added to the repository should have a clear purpose.

---

# 102. Final Instruction to the Implementation Agent

Do not optimize for writing code quickly.

Optimize for building a production-quality, maintainable, extensible, open-source software project.

Treat this project as if it will eventually be maintained by hundreds of contributors and used by thousands of ML engineers.

Every architectural decision should reflect that expectation.

This document is the authoritative specification for the project. If implementation details are ambiguous, choose the solution that best aligns with the goals of maintainability, extensibility, correctness, transparency, and long-term sustainability.

# 103. Appendix A — Core Data Models

This appendix defines the canonical data structures used throughout the Product Agent.

These structures are conceptual specifications.

The Implementation Agent may choose the implementation language and serialization format while preserving the meaning of every field.

---

# ProjectContext

Represents the complete understanding of a user's project.

Fields:

* projectName
* projectPath
* detectedFramework
* frameworkVersion
* baseModel
* tokenizer
* datasetPaths
* promptTemplates
* configurationFiles
* trainingScripts
* evaluationScripts
* inferenceScripts
* hardwareInformation
* projectStatistics
* projectHealthScore
* trainingReadinessScore
* analysisTimestamp

---

# DatasetAnalysisResult

Fields:

* datasetName
* sampleCount
* tokenCount
* averagePromptLength
* averageResponseLength
* duplicatePercentage
* nearDuplicatePercentage
* missingFieldPercentage
* formattingConsistencyScore
* languageConsistencyScore
* instructionConsistencyScore
* responseConsistencyScore
* qualityScore
* findings
* warnings
* recommendations
* confidence

---

# PromptAnalysisResult

Fields:

* templateName
* promptComplexity
* ambiguityScore
* clarityScore
* formattingScore
* instructionQualityScore
* consistencyScore
* detectedIssues
* recommendations
* confidence

---

# HyperparameterAnalysisResult

Fields:

* learningRate
* batchSize
* epochs
* optimizer
* scheduler
* gradientAccumulation
* weightDecay
* warmupRatio
* sequenceLength
* loraRank
* loraAlpha
* loraDropout
* overfittingRisk
* underfittingRisk
* efficiencyScore
* recommendations
* confidence

---

# ModelAnalysisResult

Fields:

* selectedModel
* parameterCount
* contextLength
* estimatedVRAM
* reasoningCapability
* codingCapability
* multilingualCapability
* instructionFollowingCapability
* speedScore
* memoryEfficiency
* strengths
* weaknesses
* recommendedAlternatives
* confidence

---

# PredictionResult

Fields:

* instructionFollowingPrediction
* hallucinationRisk
* reasoningPrediction
* responseConsistencyPrediction
* creativityPrediction
* formattingPrediction
* likelyFailureModes
* expectedStrengths
* expectedWeaknesses
* confidence

Predictions shall never claim certainty.

---

# CostEstimate

Fields:

* estimatedTrainingTime
* estimatedGPUHours
* estimatedVRAMUsage
* estimatedCheckpointSize
* estimatedStorageRequirement
* compatibleHardware
* assumptions
* confidence

---

# Recommendation

Every recommendation shall follow the same schema.

Fields:

* recommendationId
* category
* title
* description
* reasoning
* evidence
* severity
* confidence
* estimatedBenefit
* implementationDifficulty
* estimatedEngineeringTime
* affectedFiles
* suggestedActions
* references

Recommendations must always contain evidence.

---

# EngineeringReport

Fields:

* executiveSummary
* projectHealthScore
* trainingReadinessScore
* datasetSummary
* promptSummary
* hyperparameterSummary
* modelSummary
* predictionSummary
* costSummary
* prioritizedRecommendations
* actionPlan

---

# Experiment

Fields:

* experimentId
* timestamp
* baseModel
* datasetVersion
* tokenizer
* hyperparameters
* metrics
* notes
* tags
* artifacts

---

# ChatSession

Fields:

* sessionId
* creationTime
* projectContextReference
* messageHistory
* referencedReports
* referencedRecommendations

---

# FileModification

Fields:

* filePath
* modificationType
* originalContent
* proposedContent
* diff
* approvalStatus
* appliedTimestamp
* rollbackAvailable

---

# Analyzer Interface

Every analyzer shall expose a consistent interface.

Input

* ProjectContext

Output

* AnalysisResult

Every analyzer shall be independently testable.

---

# AI Provider Interface

Every AI provider shall implement:

Initialize

Validate Credentials

Chat Completion

Streaming Completion

Embedding Generation (future)

Health Check

Model Listing

Provider implementations must remain interchangeable.

---

# Storage Interface

Storage implementations shall support:

Save

Load

Update

Delete

Search

Backup

Future storage systems must not require changes to business logic.

---

# Report Generator Interface

Input:

All Analysis Results

Output:

Engineering Report

The report generator shall remain independent from analyzer implementations.

---

# Plugin Interface

Every future plugin shall declare:

Plugin Name

Plugin Version

Author

Description

Supported Frameworks

Capabilities

Dependencies

Configuration

Entry Point

The Product Agent shall discover plugins automatically where practical.

---

# Version Compatibility

Every serialized object shall include a schema version.

Future schema changes must remain backward compatible whenever practical.

Breaking changes shall require explicit version increments.

---

# Data Validation

All incoming and outgoing data shall be validated.

Invalid data shall produce descriptive validation errors.

Silent failures are prohibited.

---

# Serialization

The Product Agent shall use structured serialization.

Supported formats may include:

* JSON
* YAML
* TOML

Binary serialization should be avoided unless there is a measurable performance benefit.

---

# Extensibility

Every data model should support future extension without requiring breaking changes.

Prefer optional fields over incompatible schema redesigns where appropriate.

# 104. Appendix B — API Specification

This appendix defines the public API contract between the VS Code Extension and the Backend.

The Product Agent shall communicate exclusively through these APIs.

Business logic shall never exist inside the VS Code extension.

---

# API Design Principles

Every endpoint shall:

* use versioning
* validate requests
* validate responses
* return typed objects
* return meaningful error messages
* avoid breaking changes whenever practical

Base URL

/api/v1

---

# Health

## GET

/health

Purpose

Verify backend availability.

Response

* status
* version
* uptime
* providerStatus

---

# Project Analysis

## POST

/project/analyze

Purpose

Analyze an entire project.

Request

* projectPath

Response

* ProjectContext
* EngineeringReport

---

## GET

/project/context

Purpose

Retrieve the latest ProjectContext.

---

## POST

/project/refresh

Purpose

Rebuild ProjectContext.

---

# Dataset Analysis

## POST

/dataset/analyze

Request

* datasetPath

Response

DatasetAnalysisResult

---

## POST

/dataset/duplicates

Purpose

Detect duplicate samples.

---

## POST

/dataset/statistics

Purpose

Return dataset statistics.

---

## POST

/dataset/clean

Purpose

Generate cleanup recommendations.

This endpoint must not modify files.

---

# Prompt Analysis

## POST

/prompt/analyze

Request

* promptTemplate

Response

PromptAnalysisResult

---

## POST

/prompt/improve

Purpose

Generate improved prompt suggestions.

Changes must remain proposals until user approval.

---

# Hyperparameter Analysis

## POST

/hyperparameters/analyze

Response

HyperparameterAnalysisResult

---

## POST

/hyperparameters/optimize

Purpose

Generate optimized training configuration.

No configuration files shall be modified automatically.

---

# Model Advisor

## POST

/model/analyze

Purpose

Analyze selected model.

---

## POST

/model/compare

Purpose

Compare multiple models.

Request

* models

Response

ComparisonReport

---

# Prediction Engine

## POST

/predict/training

Purpose

Estimate likely fine-tuning outcome.

Response

PredictionResult

Predictions are probabilistic.

---

# Cost Estimator

## POST

/cost/estimate

Purpose

Estimate training resources.

Response

CostEstimate

---

# Recommendations

## GET

/recommendations

Return current recommendations.

---

## POST

/recommendations/refresh

Regenerate recommendations.

---

# Reports

## GET

/report

Return EngineeringReport.

---

## POST

/report/export

Supported formats

JSON

Markdown

PDF (future)

HTML (future)

---

# Chat

## POST

/chat/message

Purpose

Interact with the Product Agent.

Request

* sessionId
* message

Response

assistantResponse

references

confidence

---

## GET

/chat/history

Return previous conversation.

---

## DELETE

/chat/history

Delete conversation history.

---

# Experiments

## GET

/experiments

Return experiments.

---

## POST

/experiments

Create experiment.

---

## GET

/experiments/{id}

Return experiment details.

---

## DELETE

/experiments/{id}

Delete experiment.

---

## POST

/experiments/compare

Compare multiple experiments.

---

# File Modifications

## POST

/files/propose

Generate proposed edits.

---

## POST

/files/apply

Apply approved edits.

Requires explicit user approval.

---

## POST

/files/rollback

Undo previous modifications.

---

# Providers

## GET

/providers

Return available AI providers.

---

## POST

/provider/select

Change active provider.

---

## GET

/provider/models

Return supported models.

---

# Plugins

## GET

/plugins

List installed plugins.

---

## POST

/plugins/install

Future feature.

---

## POST

/plugins/uninstall

Future feature.

---

## GET

/plugins/capabilities

Return plugin capabilities.

---

# Configuration

## GET

/config

Return current configuration.

---

## PUT

/config

Update configuration.

---

# Logging

## GET

/logs

Return recent logs.

Development mode only.

---

# Metrics

## GET

/metrics

Return:

* analysis duration
* analyzer timings
* memory usage
* cache statistics

---

# WebSocket

/ws/analysis

Purpose

Real-time analysis progress.

Events

Analysis Started

Scanner Progress

Analyzer Progress

Recommendation Generated

Report Ready

Completed

Failed

---

# Error Format

Every API error shall include:

* errorCode
* message
* details
* timestamp
* requestId

Internal stack traces shall never be exposed.

---

# Authentication

Version 1 requires no authentication.

The architecture shall support future authentication without breaking existing APIs.

---

# API Versioning

Breaking API changes shall require a new version.

Example

/api/v1

/api/v2

Older versions should remain supported for a reasonable deprecation period.

---

# Rate Limiting

Future cloud deployments should support configurable rate limiting.

Local deployments should not enforce unnecessary limits.

---

# Acceptance Criteria

The API layer is considered complete only if:

* Every endpoint validates requests.
* Every endpoint validates responses.
* Every endpoint is documented.
* API contracts remain stable.
* Unit and integration tests exist.
* OpenAPI documentation is automatically generated.

# 105. Appendix C — Database Design & Storage Architecture

This appendix defines the persistent storage architecture for the Product Agent.

The storage layer shall remain independent from business logic.

Business logic must never directly access database implementations.

Always use repository interfaces.

---

# Storage Goals

The storage layer shall provide:

* reliability
* consistency
* maintainability
* portability
* scalability

Version 1 shall use SQLite.

Future versions shall support PostgreSQL without requiring business logic changes.

---

# Database Engine

Version 1

SQLite

Future

PostgreSQL

The database implementation shall remain abstracted behind repository interfaces.

---

# Migration Strategy

Database schema changes shall be managed through migrations.

Manual schema modification is prohibited.

Every migration shall:

* have a unique identifier
* support rollback where practical
* preserve user data

---

# Core Tables

Version 1 shall contain the following logical tables.

---

## Projects

Purpose

Store project metadata.

Fields

* project_id
* project_name
* project_path
* framework
* framework_version
* base_model
* tokenizer
* created_at
* updated_at

---

## Analyses

Purpose

Store completed analysis sessions.

Fields

* analysis_id
* project_id
* started_at
* completed_at
* duration
* health_score
* readiness_score
* status

---

## Dataset Reports

Fields

* report_id
* analysis_id
* dataset_name
* quality_score
* duplicate_percentage
* token_count
* findings
* recommendations

---

## Prompt Reports

Fields

* report_id
* analysis_id
* template_name
* clarity_score
* ambiguity_score
* consistency_score
* findings
* recommendations

---

## Hyperparameter Reports

Fields

* report_id
* analysis_id
* learning_rate
* batch_size
* epochs
* optimizer
* scheduler
* lora_rank
* lora_alpha
* findings
* recommendations

---

## Model Reports

Fields

* report_id
* analysis_id
* model_name
* reasoning_score
* coding_score
* speed_score
* vram_estimate
* strengths
* weaknesses

---

## Predictions

Fields

* prediction_id
* analysis_id
* confidence
* hallucination_risk
* reasoning_prediction
* instruction_following_prediction
* response_consistency
* predicted_failure_modes

---

## Cost Estimates

Fields

* estimate_id
* analysis_id
* training_time
* gpu_hours
* vram
* storage
* checkpoint_size

---

## Recommendations

Fields

* recommendation_id
* analysis_id
* severity
* confidence
* title
* description
* evidence
* status

Status examples

Pending

Accepted

Dismissed

Applied

---

## Experiments

Fields

* experiment_id
* project_id
* dataset_version
* model
* tokenizer
* hyperparameters
* metrics
* notes
* created_at

---

## Chat Sessions

Fields

* session_id
* project_id
* created_at
* updated_at

---

## Chat Messages

Fields

* message_id
* session_id
* role
* content
* timestamp

---

## File Modifications

Fields

* modification_id
* project_id
* file_path
* change_summary
* approval_status
* rollback_available
* applied_at

---

## Settings

Fields

* key
* value
* updated_at

Settings shall be extensible.

---

# Relationships

Logical relationships include:

Project

↓

Many Analyses

Analysis

↓

Many Reports

Analysis

↓

Many Recommendations

Project

↓

Many Experiments

Project

↓

Many Chat Sessions

Chat Session

↓

Many Messages

Project

↓

Many File Modifications

---

# Repository Layer

Business logic shall communicate through repositories.

Examples

ProjectRepository

AnalysisRepository

DatasetRepository

RecommendationRepository

ExperimentRepository

SettingsRepository

ChatRepository

Repositories shall hide database implementation details.

---

# Transactions

Database transactions shall be used for operations that modify multiple related records.

Partial writes should be avoided.

---

# Indexing

Indexes should be created for frequently queried fields.

Examples

project_id

analysis_id

experiment_id

session_id

created_at

Avoid unnecessary indexes.

---

# Caching

Frequently accessed information may be cached.

Examples

Latest ProjectContext

Latest Engineering Report

Model Metadata

Dataset Statistics

Caches must be invalidated automatically after relevant changes.

---

# Backups

Future versions shall support:

Manual Backup

Automatic Backup

Restore

Export

Import

---

# Data Retention

Users should be able to:

Delete projects

Delete reports

Delete experiments

Delete chat history

Delete cached information

Deletion should remove associated records where appropriate.

---

# Search

The storage layer should support searching by:

Project

Experiment

Recommendation

Dataset

Model

Date

Tags

---

# Import & Export

Support structured export.

Preferred formats

JSON

Markdown

CSV (where appropriate)

Future versions may add additional formats.

---

# Performance

The storage layer should remain responsive.

Goals

Small projects should require negligible storage overhead.

Queries should avoid unnecessary table scans.

Large reports should be streamed where practical.

---

# Future Storage Extensions

The architecture should support future additions including:

Vector databases

Cloud databases

Distributed storage

Remote synchronization

Workspace sharing

None of these additions should require rewriting business logic.

---

# Acceptance Criteria

The storage layer is complete only if:

* Schema is versioned.
* Migrations are implemented.
* Repository abstraction exists.
* Transactions are used appropriately.
* Relationships are documented.
* Tests validate CRUD operations.
* Future database engines can be adopted with minimal changes.

# 106. Appendix D — Plugin & Extension Architecture

This appendix defines how the Product Agent shall be extended without modifying the core application.

The plugin architecture is a first-class feature.

Every major capability should be replaceable or extendable through plugins.

---

# Design Goals

The plugin system shall:

* encourage community contributions
* minimize core modifications
* isolate plugins
* simplify future expansion
* support version compatibility
* prevent plugins from breaking the core application

---

# Plugin Categories

Version 1 shall support internal plugins only.

Future versions may support third-party plugins.

Supported plugin categories include:

* Dataset Analyzer
* Prompt Analyzer
* Hyperparameter Advisor
* Base Model Advisor
* Prediction Engine
* Report Generator
* AI Provider
* Training Framework
* File Parser
* Exporter
* Visualization
* Experiment Tracker

---

# Plugin Discovery

The Product Agent shall automatically discover plugins during startup.

The discovery process should:

* validate metadata
* validate compatibility
* verify dependencies
* register capabilities

Invalid plugins shall be skipped without affecting the remaining system.

---

# Plugin Metadata

Every plugin shall define:

Plugin Name

Plugin ID

Version

Description

Author

License

Repository

Documentation

Supported Product Agent Version

Supported Frameworks

Dependencies

Capabilities

Entry Point

Configuration Schema

---

# Plugin Lifecycle

Every plugin shall support the following lifecycle:

Initialize

↓

Register

↓

Load Configuration

↓

Perform Health Check

↓

Ready

↓

Shutdown

Plugins must release resources during shutdown.

---

# Plugin Isolation

Plugins must never directly modify the internal state of the Product Agent.

Communication shall occur only through defined interfaces.

Plugins should not depend on private implementation details.

---

# Plugin Registration

The Product Agent shall maintain a Plugin Registry.

The registry is responsible for:

* loading plugins
* unloading plugins
* enabling plugins
* disabling plugins
* listing capabilities
* resolving conflicts

---

# Analyzer Plugins

Every analyzer plugin shall implement a common interface.

Input

ProjectContext

Output

AnalysisResult

The Recommendation Engine should treat built-in and external analyzers identically.

---

# AI Provider Plugins

AI providers shall be implemented as plugins.

Supported examples:

OpenAI

Anthropic

Google Gemini

OpenRouter

Ollama

Future providers

The rest of the application must remain provider-independent.

---

# Training Framework Plugins

Examples include:

Transformers

TRL

PEFT

Unsloth

Axolotl

Future frameworks

Adding a new framework should require only a new plugin.

---

# File Parser Plugins

Support parsing:

JSON

JSONL

CSV

YAML

TOML

TXT

Future datasets

Custom formats

---

# Report Generator Plugins

Support generating reports in:

Markdown

JSON

HTML

PDF

Future formats

---

# Visualization Plugins

Future visualizations may include:

Dataset statistics

Training curves

Token distributions

Recommendation graphs

Dependency graphs

Cost estimation charts

The core Product Agent should remain independent of visualization implementations.

---

# Plugin Configuration

Each plugin shall define its own configuration.

Configuration should be validated before plugin initialization.

Invalid configuration shall disable the plugin with an informative error.

---

# Plugin Dependencies

Plugins may depend on:

Other plugins

Shared services

AI providers

Storage interfaces

Dependency cycles are prohibited.

---

# Plugin Versioning

Every plugin shall declare:

Minimum supported Product Agent version.

Maximum tested Product Agent version.

Semantic Version.

Incompatible plugins shall not load.

---

# Plugin Security

Plugins shall not:

Execute arbitrary shell commands without user approval.

Access unrelated user files.

Transmit project data without user permission.

Modify files outside approved workflows.

Request excessive permissions.

---

# Plugin Permissions

Future versions may support permission declarations.

Examples:

Read Project

Read Dataset

Read Prompt

Write Files

Export Reports

Network Access

Users should be able to review granted permissions.

---

# Plugin Failure Handling

If a plugin fails:

* Log the error.
* Disable the failed plugin.
* Continue loading remaining plugins.
* Notify the user.

One faulty plugin must never crash the Product Agent.

---

# Community Plugins

Future community plugins should be installable without modifying the Product Agent.

Installation should include:

Validation

Compatibility Check

Dependency Resolution

Registration

Health Check

---

# Plugin Testing

Every plugin should include:

Unit Tests

Integration Tests

Documentation

Configuration Examples

Version Information

---

# Plugin Documentation

Every plugin repository should document:

Purpose

Features

Configuration

Installation

Examples

Limitations

Compatibility

---

# Acceptance Criteria

The plugin system is complete only if:

* Plugins are discoverable.
* Plugins are isolated.
* Plugin failures are contained.
* Version compatibility is enforced.
* New analyzers can be added without changing core modules.
* AI providers can be replaced without changing business logic.
* Community plugins can be supported in future versions.

# 107. Appendix E — Security Architecture

This appendix defines the security requirements of the Product Agent.

Security is a core engineering requirement.

The Product Agent shall be designed assuming it may eventually be used inside enterprise environments.

Security shall never be treated as an optional feature.

---

# Security Goals

The Product Agent shall protect:

* user source code
* datasets
* prompts
* API keys
* project configuration
* generated reports
* experiment history

The Product Agent shall minimize unnecessary risk.

---

# Security Principles

Follow the principle of:

Least Privilege

Every module should have only the permissions it requires.

Avoid unnecessary filesystem access.

Avoid unnecessary network communication.

---

# Trust Boundaries

The Product Agent interacts with:

VS Code

↓

Extension

↓

Backend

↓

AI Provider

↓

Local Storage

Each boundary should validate incoming data.

Never trust external input.

---

# Secret Management

Secrets include:

API Keys

Authentication Tokens

Provider Credentials

Future Enterprise Credentials

Requirements

Never hardcode secrets.

Never commit secrets.

Never print secrets in logs.

Never expose secrets in reports.

Never expose secrets in stack traces.

Secrets should be stored using secure platform mechanisms where practical.

---

# API Key Handling

Supported providers may require API keys.

The Product Agent shall:

Validate keys.

Store keys securely.

Avoid displaying complete keys.

Allow key rotation.

Allow key deletion.

Mask secrets whenever displayed.

---

# Filesystem Security

The Product Agent shall only access:

Current Workspace

User-approved files

Temporary directories

It shall never:

Scan unrelated folders.

Access operating system files.

Modify files without approval.

Delete files automatically.

Create files outside the project without approval.

---

# Safe File Editing

Every modification follows:

Analyze

↓

Generate Diff

↓

Display Preview

↓

User Approval

↓

Apply Changes

↓

Create Rollback Point

↓

Record History

Automatic modifications are prohibited.

---

# Rollback

Every file modification shall support rollback whenever practical.

Rollback metadata shall include:

Timestamp

Original Content

Modified Content

Reason

User Approval

---

# Network Security

The Product Agent shall minimize network communication.

If cloud providers are used:

Clearly identify:

Destination

Purpose

Data transmitted

Provider

Allow users to disable cloud communication.

---

# Offline Mode

The Product Agent should support local workflows whenever practical.

Examples

Ollama

Local models

Offline dataset analysis

Offline reports

Offline recommendations based on deterministic analyzers

---

# Input Validation

Validate:

API Requests

Configuration

Dataset Files

Prompt Templates

Plugin Metadata

User Commands

Configuration Files

Reject malformed input.

Never assume correctness.

---

# Output Validation

Every generated object shall be validated before use.

Examples

Reports

Recommendations

Configuration

Predictions

File modifications

---

# Path Traversal Protection

The Product Agent shall reject attempts to access files outside approved directories.

Examples include:

Relative path attacks

Symbolic link abuse

Unexpected workspace traversal

All filesystem operations shall use canonical paths.

---

# Command Execution

The Product Agent shall never execute arbitrary shell commands automatically.

Future command execution requires:

Explicit user approval

Visible command preview

Confirmation

Execution logging

---

# Dependency Security

Dependencies shall:

Be actively maintained.

Have permissive licenses.

Receive security updates.

Avoid unnecessary packages.

Prefer mature libraries.

---

# Dependency Auditing

Regularly perform:

Dependency scanning

Known vulnerability checks

License verification

Unused dependency detection

---

# Logging Security

Logs shall never contain:

API Keys

Tokens

Passwords

Private datasets

Prompt contents (unless explicitly enabled)

Personal information

Sensitive configuration

---

# Privacy

User data belongs to the user.

The Product Agent shall:

Avoid unnecessary collection.

Avoid unnecessary transmission.

Avoid unnecessary retention.

Users should control their own data.

---

# Telemetry

Telemetry shall be disabled by default.

If enabled:

Clearly explain:

Collected information

Purpose

Retention

Transmission

Users shall be able to disable telemetry at any time.

---

# AI Provider Privacy

Before sending project information to cloud providers:

Warn the user.

Explain:

What is transmitted.

Which provider receives it.

Why it is necessary.

Local providers should be preferred when practical.

---

# Plugin Security

Plugins shall be treated as untrusted components.

Plugins should not receive unrestricted access.

Plugins should only access approved interfaces.

Future versions may introduce sandboxing.

---

# Authentication

Version 1 requires no authentication.

Future enterprise versions may support:

OAuth

API Tokens

SSO

Enterprise Identity Providers

Authentication should remain modular.

---

# Authorization

Future versions should support role-based permissions.

Examples

Administrator

Developer

Reviewer

Read Only

Permissions shall be centrally managed.

---

# Denial of Service Protection

The Product Agent should prevent:

Infinite analysis loops

Recursive scanning

Unbounded memory allocation

Excessive file processing

Large prompt explosions

Resource limits should be configurable.

---

# Resource Limits

Configurable limits should include:

Maximum project size

Maximum dataset size

Maximum token count

Maximum file size

Maximum concurrent analyses

Maximum plugin execution time

---

# Secure Defaults

Default configuration shall prioritize security over convenience.

Unsafe features should require explicit opt-in.

---

# Security Reviews

Major releases should include:

Threat review

Dependency audit

Permission review

Privacy review

Plugin review

---

# Future Security Enhancements

Possible future additions:

Encrypted local storage

Plugin sandboxing

Workspace trust integration

Enterprise authentication

Cloud synchronization

Remote policy management

Security dashboards

These additions should not require major architectural changes.

---

# Acceptance Criteria

The security architecture is complete only if:

* Secrets are protected.
* User approval is required for modifications.
* Sensitive information is never logged.
* File access is restricted.
* Network communication is transparent.
* Plugins are isolated.
* Security defaults are conservative.
* Future enterprise security features can be added without redesigning the system.

# 108. Appendix F — Comprehensive Testing Strategy

This appendix defines the quality assurance strategy for the Product Agent.

Testing is a mandatory engineering activity.

No feature shall be considered complete without appropriate automated tests.

---

# Testing Goals

The testing strategy shall ensure:

* correctness
* reliability
* maintainability
* reproducibility
* scalability
* regression prevention

Testing shall be integrated throughout the development lifecycle.

---

# Testing Pyramid

The Product Agent shall follow the testing pyramid.

Priority:

1. Unit Tests
2. Integration Tests
3. End-to-End Tests

Avoid excessive dependence on manual testing.

---

# Test Categories

The Product Agent shall include:

* Unit Tests
* Integration Tests
* End-to-End Tests
* Regression Tests
* Performance Tests
* Stress Tests
* Security Tests
* Compatibility Tests
* AI Evaluation Tests
* User Acceptance Tests

---

# Unit Testing

Every business logic component shall have unit tests.

Examples:

Project Scanner

Dataset Analyzer

Prompt Analyzer

Recommendation Engine

Prediction Engine

Cost Estimator

Configuration Parser

Validation Utilities

Repository Layer

Utility Functions

Unit tests shall not depend on external services.

---

# Integration Testing

Integration tests shall verify communication between components.

Examples:

VS Code Extension ↔ Backend

Backend ↔ Database

Backend ↔ AI Provider

Scanner ↔ Analyzer

Analyzer ↔ Recommendation Engine

Repository ↔ Database

Plugin ↔ Core Application

---

# End-to-End Testing

End-to-End tests shall validate complete workflows.

Example workflows:

Open project

↓

Analyze project

↓

Generate recommendations

↓

Open report

↓

Approve modification

↓

Apply change

↓

Rollback change

Every critical workflow shall have at least one automated end-to-end test.

---

# Regression Testing

Every resolved defect should receive a regression test.

A previously fixed bug must never reappear unnoticed.

---

# AI Evaluation Testing

AI-generated outputs require additional evaluation.

Evaluate:

Recommendation Quality

Prediction Consistency

Prompt Improvement Quality

Model Comparison Accuracy

Engineering Report Quality

AI outputs should be reviewed using deterministic evaluation criteria whenever possible.

---

# Dataset Testing

Prepare multiple datasets for testing.

Examples:

Small Dataset

Medium Dataset

Large Dataset

Corrupted Dataset

Incomplete Dataset

Duplicate Dataset

Multilingual Dataset

Instruction Dataset

Conversation Dataset

Edge Case Dataset

Analyzers shall behave correctly for all supported datasets.

---

# Prompt Testing

Prepare prompt collections representing:

Good Prompts

Poor Prompts

Ambiguous Prompts

Very Long Prompts

Minimal Prompts

Role-Based Prompts

Conversation Prompts

Prompt analyzers shall generate meaningful recommendations.

---

# Hyperparameter Testing

Validate:

Learning Rate Analysis

Batch Size Analysis

Epoch Recommendations

Scheduler Detection

Optimizer Detection

LoRA Configuration

QLoRA Configuration

Edge cases shall be included.

---

# Prediction Testing

Predictions shall be evaluated against known benchmark projects whenever practical.

The Product Agent shall never fabricate confidence.

Prediction confidence shall remain calibrated.

---

# Recommendation Testing

Recommendations shall be evaluated for:

Correctness

Consistency

Explainability

Priority

Evidence

Conflicting recommendations should be detected.

---

# API Testing

Every endpoint shall include:

Success Tests

Validation Tests

Authorization Tests (future)

Failure Tests

Malformed Request Tests

Timeout Tests

Large Payload Tests

---

# Database Testing

Test:

CRUD Operations

Transactions

Rollback

Migration

Indexes

Relationships

Constraint Validation

Data Integrity

---

# File Modification Testing

Verify:

Diff Generation

Approval Workflow

Rollback

Conflict Detection

File Preservation

No unintended modifications should occur.

---

# Plugin Testing

Each plugin shall include:

Initialization Test

Registration Test

Configuration Test

Failure Test

Compatibility Test

Health Check

---

# Performance Testing

Measure:

Project Scan Time

Dataset Analysis Time

Prompt Analysis Time

Prediction Generation Time

Recommendation Generation Time

Report Generation Time

Startup Time

Memory Usage

CPU Usage

Performance regressions should be detected automatically.

---

# Load Testing

Future testing should include:

Large Projects

Large Datasets

Thousands of Files

Long Conversations

Large Reports

Many Experiments

System stability shall remain acceptable.

---

# Stress Testing

Evaluate behavior under extreme conditions.

Examples:

Extremely Large Dataset

Very Long Prompt

Massive Workspace

Invalid Configuration

Plugin Failures

Multiple Simultaneous Requests

The Product Agent should fail gracefully.

---

# Security Testing

Perform tests for:

Input Validation

Path Traversal

Secret Leakage

Unauthorized File Access

Plugin Isolation

Dependency Vulnerabilities

Malformed Requests

Unsafe Configurations

---

# Compatibility Testing

Verify compatibility across:

Windows

Linux

macOS

Multiple Python Versions

Multiple Node.js Versions

Multiple VS Code Versions

Supported AI Providers

---

# UI Testing

Validate:

Sidebar

Activity Bar

Commands

Status Bar

Notifications

Settings

Report Viewer

Chat Interface

Theme Compatibility

Accessibility

---

# Accessibility Testing

The extension should support:

Keyboard Navigation

Screen Readers

Readable Contrast

Scalable Fonts

Accessible Icons

Accessibility should be considered during UI design.

---

# Continuous Testing

Automated tests shall execute:

Every Commit

Every Pull Request

Every Release Candidate

Nightly Builds (future)

Manual testing should supplement, not replace, automation.

---

# Test Coverage

Meaningful coverage is preferred over artificial percentage goals.

Priority should be given to:

Business Logic

Recommendation Engine

Prediction Engine

API Contracts

Database Layer

Plugin System

Coverage metrics should guide improvement rather than become the primary objective.

---

# Test Data

Test data shall remain separate from production data.

Synthetic datasets should be preferred.

Sensitive user data shall never be committed to the repository.

---

# Mocking Strategy

External systems should be mocked when appropriate.

Examples:

AI Providers

Remote APIs

Network Calls

Cloud Storage

Mocks should accurately reflect expected behavior.

---

# Failure Reporting

Test failures should provide:

Clear Description

Expected Result

Actual Result

Relevant Logs

Affected Component

Suggested Investigation

Avoid vague failure messages.

---

# Acceptance Criteria

The testing strategy is complete only if:

* Every critical module has automated tests.
* Integration tests validate component interactions.
* End-to-end workflows are covered.
* Performance regressions are detectable.
* Security tests validate critical protections.
* Plugin functionality is tested.
* AI-specific behavior is evaluated.
* Continuous Integration executes automated test suites before every release.

# 109. Appendix G — Continuous Integration, Continuous Delivery & Release Engineering

This appendix defines the build, testing, release, and deployment pipeline for the Product Agent.

Every change to the project shall pass through automated quality gates before reaching the main branch.

Automation is preferred over manual processes whenever practical.

---

# CI/CD Goals

The CI/CD pipeline shall ensure:

* repeatable builds
* automated testing
* code quality enforcement
* reliable releases
* reproducible artifacts
* fast developer feedback

---

# Source Control

The Product Agent shall use Git.

Recommended branching strategy:

main

develop

feature/*

bugfix/*

release/*

hotfix/*

The main branch shall always remain deployable.

---

# Pull Request Workflow

Every Pull Request shall:

* pass all automated checks
* pass linting
* pass formatting
* pass unit tests
* pass integration tests
* receive code review
* update documentation if necessary

Direct commits to the main branch are discouraged.

---

# Continuous Integration

Every commit shall automatically execute:

Install dependencies

↓

Static analysis

↓

Formatting verification

↓

Linting

↓

Type checking

↓

Unit tests

↓

Integration tests

↓

Build backend

↓

Build VS Code extension

↓

Package extension

↓

Generate artifacts

↓

Publish test results

If any stage fails, the pipeline shall fail.

---

# Build Pipeline

The build pipeline shall verify:

Python dependencies

Node.js dependencies

Environment configuration

API contracts

Plugin compatibility

Version consistency

Generated artifacts

No release artifacts shall be produced if validation fails.

---

# Static Analysis

Automatically perform:

Type checking

Unused imports

Dead code detection

Dependency validation

Circular dependency detection

Security linting where practical

Static analysis should execute before tests.

---

# Code Formatting

Formatting shall be automatically verified.

Formatting should remain deterministic.

Formatting differences should fail CI.

---

# Dependency Validation

Automatically verify:

Dependency installation

Version conflicts

Unsupported versions

Duplicate dependencies

Missing dependencies

---

# Security Scanning

CI should automatically perform:

Dependency vulnerability scanning

License verification

Secret detection

Unsafe configuration detection

Known vulnerability detection

Potential security issues should block releases.

---

# Documentation Validation

Automatically verify:

Broken links

Missing documents

Missing examples

Missing API documentation

Documentation should remain synchronized with implementation.

---

# Test Pipeline

Automated test stages:

Unit Tests

↓

Integration Tests

↓

End-to-End Tests

↓

Regression Tests

↓

Performance Smoke Tests

Each stage shall publish results.

---

# Build Artifacts

Every successful build should produce:

VSIX Package

Backend Package

Documentation Artifacts

Test Reports

Coverage Reports

Release Notes (future)

Artifacts should remain reproducible.

---

# Version Management

The Product Agent shall use Semantic Versioning.

Examples:

1.0.0

1.1.0

1.2.3

2.0.0

Breaking changes require major version increments.

---

# Release Candidates

Before every stable release:

Freeze new features.

Run complete regression tests.

Verify documentation.

Verify changelog.

Verify version numbers.

Verify packaging.

Only then create a release candidate.

---

# Release Checklist

Every release shall verify:

All tests pass.

No critical defects remain.

Documentation updated.

README updated.

CHANGELOG updated.

Version incremented.

Marketplace package generated.

GitHub release prepared.

---

# GitHub Actions

The Product Agent shall automate:

Build

Test

Lint

Format Check

Type Check

Package Extension

Publish Artifacts

Future additions may include:

Automatic Releases

Nightly Builds

Scheduled Security Audits

Benchmark Execution

---

# Release Artifacts

Each release should contain:

VSIX Package

Release Notes

CHANGELOG

Documentation

Version Tag

Checksums (future)

Artifacts should be reproducible.

---

# Marketplace Deployment

Before publishing:

Validate extension metadata.

Validate icon.

Validate screenshots.

Validate description.

Validate keywords.

Validate repository links.

Validate licensing.

Validate compatibility.

The extension should satisfy Visual Studio Marketplace requirements.

---

# GitHub Releases

Every release should include:

Version

Summary

New Features

Bug Fixes

Breaking Changes

Migration Notes

Known Limitations

Future Work

---

# Rollback Strategy

Every release should support rollback.

Rollback should include:

Previous Release

Previous VSIX

Previous Documentation

Previous Tags

Previous Changelog

Users should be able to return to a previous stable version.

---

# Continuous Delivery

Successful builds should always produce deployable artifacts.

Deployment to production shall remain a deliberate decision.

---

# Continuous Deployment

Automatic deployment is not required for Version 1.

Future versions may support automatic deployment after all quality gates succeed.

---

# Build Performance

The CI pipeline should remain efficient.

Long-running tasks should be parallelized where practical.

Repeated work should be minimized through caching.

---

# Failure Handling

When CI fails:

Stop subsequent stages.

Publish logs.

Publish failing tests.

Provide actionable diagnostics.

Avoid vague failure messages.

---

# Acceptance Criteria

The CI/CD pipeline is complete only if:

* Every commit is automatically validated.
* Every Pull Request passes required quality gates.
* Builds are reproducible.
* Release artifacts are generated automatically.
* Documentation remains synchronized.
* Security scanning is integrated.
* Releases are versioned and traceable.
* Stable releases are publishable to the Visual Studio Marketplace with minimal manual effort.

# 110. Appendix H — Performance, Scalability & Reliability Architecture

This appendix defines the non-functional requirements of the Product Agent.

The Product Agent shall be engineered to remain responsive, reliable, and maintainable as projects grow in size and complexity.

Performance optimizations shall never compromise correctness.

---

# Performance Goals

The Product Agent shall prioritize:

* Fast startup
* Responsive UI
* Efficient analysis
* Low memory usage
* Predictable execution
* Incremental processing

Performance improvements should be measurable.

---

# Startup Performance

The VS Code Extension should initialize quickly.

Startup should include only essential initialization.

Heavy analyzers shall not execute during extension startup.

Background initialization is preferred.

---

# Lazy Loading

The Product Agent shall lazily load:

AI Providers

Analyzers

Plugin Modules

Report Generators

Visualization Components

Large Configuration Objects

Only load components when required.

---

# Incremental Analysis

The Product Agent should avoid reanalyzing unchanged content.

Possible optimization strategies include:

File timestamps

Content hashes

Dependency graphs

Workspace events

Cache validation

Only affected components should be reanalyzed whenever practical.

---

# Caching Strategy

Cache frequently reused information.

Examples include:

Project Context

Model Metadata

Dataset Statistics

Configuration

Analysis Results

Token Counts

Recommendations

Cache invalidation shall occur automatically when dependent data changes.

---

# Parallel Processing

Independent analyzers should execute concurrently where practical.

Examples:

Dataset Analysis

Prompt Analysis

Hyperparameter Analysis

Model Analysis

Cost Estimation

Execution order shall respect dependencies.

---

# Task Scheduling

Long-running work shall execute in background tasks.

The UI shall remain responsive during analysis.

Blocking operations on the UI thread are prohibited.

---

# Progress Reporting

Every long-running operation should report progress.

Examples:

Scanning Files

Loading Dataset

Generating Recommendations

Building Report

Prediction Analysis

Users should understand current progress.

---

# Cancellation

Long-running operations shall support cancellation.

Cancellation should:

Stop unnecessary computation.

Release allocated resources.

Preserve application stability.

Partial work may be retained if useful.

---

# Memory Management

The Product Agent should minimize memory usage.

Avoid:

Unnecessary object duplication

Loading large datasets entirely into memory

Long-lived unused objects

Memory leaks

Large temporary allocations

Prefer streaming where practical.

---

# Large Dataset Handling

Large datasets should be processed incrementally.

Avoid requiring complete dataset loading.

Chunk-based processing is preferred.

---

# Large Workspace Handling

The scanner should scale to projects containing:

Thousands of files

Multiple datasets

Large configuration directories

Nested repositories

Large prompt collections

Only relevant files should be analyzed.

---

# File Watching

Workspace changes should trigger intelligent updates.

Examples:

Configuration Changes

Dataset Changes

Prompt Changes

Training Script Changes

Model Configuration Changes

Avoid rescanning the entire project.

---

# Background Processing

Expensive operations should execute asynchronously.

Examples:

Prediction Engine

Recommendation Generation

Report Generation

Cost Estimation

The user interface should remain interactive.

---

# Timeouts

Long-running operations should have configurable timeouts.

Timeouts should produce descriptive error messages.

Operations should terminate gracefully.

---

# Retry Strategy

Transient failures may be retried.

Examples:

Temporary AI Provider Errors

Temporary File Locks

Network Interruptions

Retries should use exponential backoff where appropriate.

Permanent failures should not be retried indefinitely.

---

# Reliability

The Product Agent should remain operational when individual components fail.

Examples:

Plugin Failure

AI Provider Failure

Analyzer Failure

Visualization Failure

One component should not terminate the entire application.

---

# Graceful Degradation

When advanced functionality is unavailable:

Continue providing deterministic analysis.

Disable only affected features.

Inform the user.

Never terminate unexpectedly.

---

# Fault Isolation

Failures should remain isolated.

Examples:

One plugin failure

↓

Disable plugin

↓

Continue application

One analyzer failure

↓

Report failure

↓

Continue remaining analyzers

---

# Resource Management

Resources should always be released.

Examples:

Database Connections

File Handles

Network Connections

Background Workers

Caches

Failure to release resources is unacceptable.

---

# Logging Performance

Logging should be efficient.

Avoid excessive logging.

Verbose logging should be configurable.

Production logging should prioritize useful diagnostics.

---

# Scalability

The architecture should support future scaling.

Potential future improvements:

Distributed Analysis

Remote Workers

Cloud Execution

Shared Workspaces

Enterprise Deployments

These additions should require minimal architectural changes.

---

# Benchmarking

Benchmark important workflows.

Examples:

Startup Time

Project Scan Time

Dataset Analysis Time

Recommendation Generation Time

Report Generation Time

Memory Consumption

CPU Utilization

Benchmark results should be reproducible.

---

# Performance Monitoring

Future versions may monitor:

Execution Time

Memory Usage

CPU Usage

Cache Efficiency

Plugin Performance

Analyzer Performance

Monitoring should assist engineering decisions.

---

# Performance Budgets

Future versions may define performance budgets.

Examples:

Extension Startup

Project Scan

Dataset Analysis

Recommendation Generation

UI Response Time

Budgets should be measurable.

---

# Acceptance Criteria

The performance architecture is complete only if:

* Startup remains responsive.
* Heavy work executes asynchronously.
* Independent analyzers execute concurrently where appropriate.
* Large projects remain usable.
* Memory usage remains controlled.
* Long-running operations support cancellation.
* Failures degrade gracefully.
* Future scalability is achievable without redesigning the architecture.

# 111. Appendix I — Project-Specific Implementation Guidelines

This appendix defines how the Implementation Agent (Cline) shall implement this specific project.

These guidelines supplement the global engineering workflow defined in AGENTS.md.

If this appendix conflicts with AGENTS.md, AGENTS.md takes precedence.

---

# Primary Objective

The objective is to build a production-quality VS Code extension and backend for machine learning engineers.

The Implementation Agent shall optimize for:

* correctness
* maintainability
* extensibility
* readability
* reliability

Implementation speed is secondary.

---

# Scope Control

The Implementation Agent shall implement only the approved milestone.

Do not begin future milestones.

Do not partially implement future features.

Do not speculate about future implementations unless explicitly requested.

---

# Implementation Workflow

For every milestone:

Read requirements

↓

Read architecture

↓

Verify dependencies

↓

Design implementation

↓

Implement

↓

Write tests

↓

Run tests

↓

Run linting

↓

Run formatting

↓

Update documentation

↓

Self review

↓

Independent review

↓

Wait for approval

---

# File Creation Rules

Only create files that are required.

Avoid unnecessary files.

Avoid duplicate functionality.

Every file must have a clearly defined responsibility.

---

# Module Responsibilities

Every module shall have one primary responsibility.

Examples:

Scanner

Recommendation Engine

Prediction Engine

Report Generator

Configuration

API

Storage

Avoid combining unrelated responsibilities.

---

# Public Interfaces

Public interfaces should remain stable.

Avoid breaking changes unless explicitly approved.

Future extensibility should be considered before modifying interfaces.

---

# Internal APIs

Internal APIs shall:

Use explicit types

Return predictable objects

Avoid hidden side effects

Document expected behavior

---

# Error Handling

Every error shall:

Provide meaningful context

Be logged appropriately

Avoid exposing sensitive information

Support debugging

Silent failures are prohibited.

---

# Logging

Logs should include:

Timestamp

Component

Severity

Message

Relevant Context

Logs should never expose:

Secrets

Tokens

API Keys

Sensitive user information

---

# Configuration

Configuration values shall never be hardcoded unless they are true constants.

Support centralized configuration.

Future configuration expansion should require minimal changes.

---

# Dependencies

Before adding any dependency:

Verify necessity.

Prefer mature libraries.

Avoid unnecessary packages.

Avoid duplicate functionality.

Document why the dependency was added.

---

# Refactoring

Refactor when:

Readability improves.

Maintainability improves.

Complexity decreases.

Do not refactor simply for stylistic preferences.

Avoid unnecessary churn.

---

# Documentation Updates

Whenever implementation changes:

Update relevant documentation.

Avoid stale documentation.

Documentation should accurately reflect implementation.

---

# Comments

Comments should explain:

Why

Tradeoffs

Important assumptions

Avoid comments that merely restate code.

---

# AI Provider Integrations

AI provider implementations shall remain interchangeable.

Avoid provider-specific assumptions throughout the codebase.

Provider logic belongs only within provider modules.

---

# File Modifications

Never modify user files automatically.

Required workflow:

Generate Diff

↓

Display Preview

↓

Receive User Approval

↓

Apply Changes

↓

Record Modification

↓

Enable Rollback

---

# Performance

Avoid premature optimization.

Optimize only after correctness.

When optimizing:

Measure first.

Optimize second.

Measure again.

---

# Testing

Every implemented feature shall include appropriate tests.

Implementation without tests is incomplete.

Tests should remain deterministic.

---

# Security

Before merging new functionality verify:

Input validation

Output validation

File safety

Secret handling

Permission boundaries

Security regressions are unacceptable.

---

# Pull Request Readiness

Before considering work complete:

Implementation complete

Tests passing

Lint passing

Formatting passing

Documentation updated

Architecture preserved

No placeholder code

No TODO implementations

---

# Open Source Readiness

Assume every commit may become public.

Code should be understandable by external contributors.

Prefer clarity over cleverness.

---

# Breaking Changes

Avoid unnecessary breaking changes.

If unavoidable:

Document them.

Explain migration.

Update versioning.

---

# Technical Debt

Do not knowingly introduce technical debt without documentation.

If temporary workarounds are required:

Document:

Reason

Impact

Future resolution

Target milestone

---

# Code Review Mindset

Before completing work ask:

Is this understandable?

Can another engineer maintain it?

Can another contributor extend it?

Does it follow architecture?

Does it satisfy requirements?

If any answer is "No", revise the implementation.

---

# Completion Criteria

A milestone is complete only when:

Requirements satisfied

Architecture respected

Implementation complete

Tests complete

Documentation updated

Review completed

No critical defects known

CI passes

Repository builds successfully

---

# Final Engineering Principle

Every implementation decision should favor long-term maintainability over short-term convenience.

The Product Agent is intended to become a mature, community-driven, open-source engineering tool.

Implementation decisions should reflect that long-term vision.


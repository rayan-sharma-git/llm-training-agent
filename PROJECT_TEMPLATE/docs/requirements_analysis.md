# Requirements Analysis

## LLM Training Agent — Product Agent

Version: 1.0  
Author: Requirements Analyst (Agent 1)  
Status: Complete  

---

## 1. Project Overview

The LLM Training Agent is a VS Code extension + Python backend designed to analyze LLM fine-tuning projects before training begins. It functions as an experienced ML engineer reviewing datasets, prompts, model choices, hyperparameters, and training pipelines.

---

## 2. Stakeholders

| Stakeholder | Role | Key Concern |
|---|---|---|
| ML Engineers | Primary users | Reduce failed experiments, wasted GPU time |
| AI Engineers | Primary users | Improve training pipeline quality |
| Research Engineers | Primary users | Analyze experimental configurations |
| Open Source Contributors | Secondary | Extend with new analyzers, providers |
| Project Owner | Business owner | Production-quality, maintainable codebase |

---

## 3. Functional Requirements

### FR-001: Project Scanner
- Detect project type and fine-tuning framework
- Discover datasets, config files, prompt templates, training/evaluation scripts
- Detect base model, LoRA/PEFT usage, tokenizer configuration
- Support: Hugging Face Transformers, PEFT, TRL, Unsloth, Axolotl
- Build structured ProjectContext

### FR-002: Dataset Intelligence
- Analyze duplicates, near-duplicates, empty/missing/malformed records
- Evaluate formatting, instruction, response, language consistency
- Compute average response length, token distribution, response diversity
- Detect dataset balance and low-quality samples
- Produce: Dataset Quality Score, Issues, Severity, Improvements

### FR-003: Prompt Intelligence
- Evaluate clarity, ambiguity, consistency, formatting
- Detect conflicting instructions, missing placeholders, prompt leakage
- Analyze instruction quality, role definitions, template correctness
- Return: Prompt Quality Score, Problems, Improvements

### FR-004: Hyperparameter Advisor
- Analyze learning rate, epochs, batch size, gradient accumulation, warmup
- Evaluate optimizer, scheduler, weight decay, sequence length
- Analyze LoRA rank/alpha/dropout
- Identify overfitting/underfitting risk, unstable LR, inefficiency
- May propose changes (requires user approval)

### FR-005: Base Model Advisor
- Evaluate model-task match (reasoning, coding, instruction following, multilingual)
- Compare models on inference speed, context length, params, VRAM
- Support: TinyLlama, Llama, Gemma, Mistral, Qwen
- Recommend alternatives with trade-off explanations

### FR-006: Prediction Engine
- Estimate instruction following, hallucination risk, reasoning quality
- Predict response consistency, length, creativity, formatting
- Estimate likely failure modes
- Each prediction must include confidence score
- Never claim exact model output prediction

### FR-007: Cost Estimator
- Estimate training time, VRAM usage, storage, checkpoint size
- Determine hardware compatibility
- State assumptions when information is missing

### FR-008: Experiment Tracker
- Store: dataset version, model, tokenizer, hyperparameters, metrics, timestamps, notes
- Support experiment comparison
- Identify best-performing runs

### FR-009: Recommendation Engine
- Consume outputs from all analyzers
- Prioritize and group related recommendations
- Estimate impact, provide confidence, include evidence
- Rank by expected benefit

### FR-010: AI Chat Interface
- Answer questions about current project using analysis context
- Support natural language interaction
- Responses must reference analysis results

### FR-011: Safe Project Editing
- Workflow: Analyze → Generate Changes → Show Diff → User Approval → Apply → Support Undo
- Automatic silent modification is prohibited

### FR-012: Report Generation
- Generate comprehensive engineering report
- Sections: Executive Summary, Health Score, Readiness Score, Dataset/Prompt/HP/Model Findings, Predictions, Cost, Actions

---

## 4. Non-Functional Requirements

### NFR-001: Architecture
- Modular client-server (VS Code Extension + Python Backend)
- Loose coupling through defined APIs (REST + WebSocket)
- Plugin architecture for analyzers, providers, frameworks

### NFR-002: Technology Stack
- Extension: TypeScript, Node.js, VS Code Extension API, Vitest/Jest, ESLint, Prettier
- Backend: Python, FastAPI, Pydantic, uv/pip, pytest, Ruff, Black, mypy
- Storage: SQLite (v1), PostgreSQL (future) via repository abstraction

### NFR-003: AI Provider Abstraction
- Support: OpenAI, Anthropic, Google Gemini, OpenRouter, Ollama
- Provider implementations must be interchangeable
- Business logic must remain provider-independent

### NFR-004: Performance
- UI remains responsive during analysis
- Small projects analyze in seconds
- Long-running operations stream progress and support cancellation
- Expensive operations execute asynchronously
- Lazy loading for providers, analyzers, plugins

### NFR-005: Reliability
- One analyzer failure must not crash the system
- Partial reports generated when modules fail
- Graceful degradation when advanced features unavailable
- Timeouts with descriptive error messages

### NFR-006: Security
- Never hardcode API keys or secrets
- Validate all external input
- Path traversal protection
- User approval required for all file modifications
- Rollback support for all modifications
- Secrets never logged or exposed

### NFR-007: Scalability
- Support future frameworks, providers, analyzers, plugins
- Community-developed plugins without core modifications
- Incremental analysis (avoid reanalyzing unchanged content)

### NFR-008: Documentation
- README, CONTRIBUTING, ARCHITECTURE, API, DEVELOPMENT, ROADMAP, CHANGELOG, CODE_OF_CONDUCT, SECURITY, LICENSE
- Every major module documented (purpose, I/O, dependencies, extension points)
- Documentation evolves with implementation

### NFR-009: Testing
- Unit tests for all business logic
- Integration tests for component communication
- End-to-end tests for critical workflows
- Regression tests for resolved defects
- AI evaluation tests for recommendation/prediction quality

### NFR-010: Cross-Platform
- Build on Windows, macOS, Linux
- VS Code Marketplace ready
- Cross-Platform installation

---

## 5. Assumptions

1. Users have Python 3.10+ and Node.js 18+ installed
2. Users have VS Code installed
3. The extension runs locally (backend may be local or remote)
4. Users provide their own AI provider API keys when using cloud providers
5. Ollama can be used for fully local operation
6. Projects follow standard fine-tuning conventions (Hugging Face, etc.)
7. Git is available for version control operations

---

## 6. Ambiguities and Risks

| ID | Ambiguity/Risk | Mitigation |
|---|---|---|
| R-001 | Dataset size limits not strictly defined | Use configurable limits with sensible defaults |
| R-002 | Exact prediction accuracy targets not specified | Use confidence scores, avoid claiming certainty |
| R-003 | Plugin API stability requirements | Use semantic versioning, document breaking changes |
| R-004 | Authentication not required in v1 but enterprise may need it | Design auth-ready architecture |
| R-005 | Telemetry requirements may vary by region | Default disabled, opt-in only |

---

## 7. Dependencies

| Dependency | Purpose |
|---|---|
| VS Code Extension API | Extension host, UI, commands |
| FastAPI | Backend HTTP server |
| Pydantic | Data validation |
| SQLite | Local storage |
| pytest | Backend testing |
| Vitest/Jest | Extension testing |
| Ruff/Black | Python formatting |
| ESLint/Prettier | TypeScript formatting |

---

## 8. Deliverable Mapping to Milestones

| Deliverable | Milestone(s) |
|---|---|
| Requirements Analysis | Milestone 1 |
| AI Design | Milestone 1 |
| Prompt Design | Milestone 1 |
| API Specification | Milestone 1 |
| JSON Schemas | Milestone 1 |
| Backend Scaffold | Milestone 1, 3 |
| Extension Scaffold | Milestone 1, 2 |
| Project Scanner | Milestone 4 |
| Dataset Intelligence | Milestone 5 |
| Prompt Intelligence | Milestone 6 |
| Hyperparameter Advisor | Milestone 7 |
| Base Model Advisor | Milestone 8 |
| Cost Estimator | Milestone 9 |
| Prediction Engine | Milestone 10 |
| Recommendation Engine | Milestone 11 |
| AI Chat | Milestone 12 |
| Safe Editing | Milestone 13 |
| Experiment Tracker | Milestone 14 |
| Polish & Docs | Milestone 15, 16 |
| Marketplace Prep | Milestone 17 |
| Release | Milestone 18 |

---

## 9. Quality Score: 10/10

All functional and non-functional requirements identified. Assumptions documented. Risks identified with mitigations. Ready for architecture design phase.

---

## 10. Self-Review Checklist

- [x] Every requirement has been addressed
- [x] No requirement has been ignored
- [x] No unnecessary feature has been added
- [x] Deliverable is complete
- [x] No placeholders remain
- [x] No TODOs remain without justification
- [x] Logic is correct
- [x] Assumptions are documented
- [x] Edge cases considered
- [x] Matches project architecture
- [x] Matches previous documentation
- [x] Terminology is consistent
- [x] Easy to understand
- [x] Clear naming
- [x] Clear structure
- [x] Modular
- [x] Low duplication
- [x] Easy to modify
- [x] Documentation is complete
- [x] Every public component has an explanation
- [x] Can another engineer continue this project
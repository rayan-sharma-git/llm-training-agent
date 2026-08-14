# LLM Training Agent — Complete Project Report

*A beginner-friendly guide explaining what this project is, how it works, and what each part does.*

---

## 1. What Is This Project?

**LLM Training Agent** is an AI-powered engineering assistant that lives inside **Visual Studio Code (VS Code)**. It helps **ML engineers and AI developers** review their **LLM fine-tuning projects** *before they start training* — think of it as a **senior ML engineer reviewing your code** before you hit "run."

## The Big Idea

Training a large language model to do fine-tuning is expensive — both in time and money (GPU hours). If your dataset has problems, your hyperparameters are wrong, or your prompt template is poorly written, you waste hours or days and still get bad results.

This project solves that by **automatically analyzing your entire fine-tuning project** and pointing out issues before training starts. It tells you:

- "Your dataset has 2.5% duplicates — clean them up."
- "Your learning rate is too high — you might get unstable training."
- "This model isn't a good match for coding tasks — try Gemma instead."
- "Training will cost roughly 3 GPU-hours on an RTX 4090."
- "Based on your setup, expect good instruction following but watch out for hallucinations."

---

## 2. The Two Parts (Client-Server Architecture)

The system is built as **two separate applications** that talk to each other over an API:

```
┌─────────────────────────────────┐       HTTP (REST)        ┌────────────────────────────────┐
│   VS Code Extension             │  ◄────────────────────►  │   Python Backend               │
│   (Frontend — TypeScript)       │                          │   (Analysis Engine — Python)   │
│                                 │                          │                                │
│  • Sidebar with 3 tabs          │                          │  • Project Scanner             │
│  • Chat window (webview)        │                          │  • Dataset Analyzer            │
│  • Report viewer                │                          │  • Prompt Analyzer             │
│  • Commands & buttons           │                          │  • Hyperparameter Analyzer     │
│  • Settings page                │                          │  • Model Advisor               │
│                                 │                          │  • Cost Estimator              │
│  Uses Axios (HTTP client) to    │                          │  • Prediction Engine           │
│  call the backend API           │                          │  • Recommendation Engine       │
│                                 │                          │  • Report Generator            │
│                                 │                          │  • AI Provider Abstraction     │
│                                 │                          │  • Chat Engine                 │
│                                 │                          │  • Storage (SQLite)            │
└─────────────────────────────────┘                          └────────────────────────────────┘
```

### Why two parts?

- The **extension** (TypeScript) runs inside VS Code. It draws the user interface and captures what you click.
- The **backend** (Python) does the heavy lifting — reading files, running analysis, calling AI models.

They are kept separate so the VS Code extension stays lightweight and the backend can be swapped, tested, or run independently.

---

## 3. The Complete Workflow — Step by Step

Here is exactly what happens from the moment you click "Analyze Project" to when you see a report.

### Step 0: You open a project in VS Code

You have a folder open in VS Code that contains your fine-tuning project — maybe a `train.py`, a `dataset.jsonl`, a `config.yaml`, etc.

### Step 1: You click "Analyze Project"

From the VS Code sidebar or Command Palette, you click **"LLM Training Agent: Analyze Project"**.

### Step 2: Extension (TypeScript) calls the backend

The extension's `ApiClient` (in `extension/src/services/apiClient.ts`) sends an HTTP POST request:

```
POST http://127.0.0.1:8000/api/v1/project/analyze
Body: {"projectPath": "/path/to/your/project"}
```

This uses **Axios** (an HTTP library) over **REST API** — the standard web request style.

### Step 3: Backend scanner discovers your project

The backend's `ProjectScanner` (`backend/scanner/scanner.py`) receives the request and scans your entire project folder. It:

- **Detects your framework**: Reads `requirements.txt`, `pyproject.toml`, `setup.py` to find if you're using Hugging Face Transformers, PEFT, TRL, Axolotl, or Unsloth.
- **Finds dataset files**: Searches for `*.json`, `*.jsonl`, `*.csv`, `*.parquet`, `*.txt`, `*.tsv`.
- **Finds prompt templates**: Looks for `prompt*.txt`, `prompt*.md`, `templates/**/*.txt`.
- **Finds config files**: Looks for `*.yaml`, `*.yml`, `*.toml`, `*.json`, `config*.py`.
- **Finds training scripts**: Looks for `train*.py`, `finetune*.py`, `run_*.py`.
- **Finds eval scripts**: Looks for `eval*.py`, `evaluate*.py`, `test*.py`.
- **Finds inference scripts**: Looks for `inference*.py`, `predict*.py`, `serve*.py`.
- **Detects the base model**: Searches YAML configs for `model_name_or_path`.
- **Computes statistics**: Counts all files in the project.

The scanner writes **nothing** to your files. It only reads.

### Step 4: Context Builder structures the data

The `ContextBuilder` (`backend/scanner/context_builder.py`) takes the raw scan dictionary and converts it into a clean **Pydantic model** called `ProjectContext`. This is a typed, structured object that every downstream module can rely on. No more guessing about field names.

### Step 5: Analyzers run (currently stubs)

This is where the magic *should* happen — and where the limitations currently are. There are **five analyzers**, each designed to do a specific type of analysis:

| Analyzer | What It Should Do | Current State |
|---|---|---|
| **DatasetAnalyzer** | Read your dataset (JSONL/CSV/JSON), count samples, detect duplicates, check for missing fields, measure text quality | STUB — Returns hardcoded values (1000 samples, 2.5% duplicates, quality=0.88). Does not read your actual dataset. |
| **PromptAnalyzer** | Read your prompt templates, check clarity, ambiguity, consistency, detect conflicting instructions | STUB — Returns hardcoded scores (clarity=0.85, ambiguity=0.2). Does not read your actual prompts. |
| **HyperparameterAnalyzer** | Read your training config (YAML), check learning rate, batch size, epochs, LoRA settings | STUB — Returns hardcoded values (lr=2e-4, batch=8, epochs=3). Does not read your actual config. |
| **ModelAdvisor** | Evaluate whether your chosen model fits your task (reasoning, coding, multilingual) | STUB — Returns hardcoded model info (7B params, 4096 context, 8GB VRAM). |
| **CostEstimator** | Estimate training time, VRAM, storage, compatible hardware | STUB — Returns hardcoded estimates (2-4 hours, 3.0 GPU-hours, 8GB VRAM). |

**Important transparency note**: All five analyzers currently return **simulated (hardcoded) values**. The project structure, data models, and interfaces are all properly designed — but the actual analysis logic that reads your real files is a placeholder. The scanner at Step 3 is the only module that genuinely reads your project.

> **See also:** For a detailed breakdown of whether these analyzers use LLMs, how they are designed to work, whether they will function correctly, and estimated accuracy, read the companion document `docs/analyzer_analysis_deep_dive.md`.

### Step 6: Prediction Engine runs (stub)

The `PredictionEngine` (`backend/prediction/engine.py`) takes the dataset, hyperparameter, and model results and tries to predict likely training outcomes:

- How well the model will follow instructions (poor/fair/good/excellent)
- Hallucination risk (low/medium/high)
- Reasoning quality, response consistency, creativity
- Likely failure modes

**Currently a stub** — Returns hardcoded predictions ("good" instruction following, "low" hallucination risk). The prompt templates exist for AI-driven prediction, but they aren't wired in yet.

### Step 7: Recommendation Engine combines everything

The `RecommendationEngine` (`backend/recommendation/engine.py`) takes all the analysis results and generates prioritized recommendations. Unlike the analyzers above, this engine has **some real logic**:

- If dataset duplicates > 5% then it recommends deduplication
- If learning rate > 1e-3 then it recommends reducing it

Each recommendation includes: title, description, reasoning, evidence, confidence, severity, affected files, and suggested actions.

**Limited** — Only 2 real rules exist. The full recommendation generation would use AI (the prompt templates are ready), but they aren't wired in yet.

### Step 8: Report Generator creates the final report

The `ReportGenerator` (`backend/reports/generator.py`) takes **everything** — project context, all analyzer results, predictions, cost estimates, and recommendations — and builds a comprehensive `EngineeringReport`:

- Executive Summary (text description of the project)
- Project Health Score (0–100%, computed from dataset quality + hyperparameter efficiency)
- Training Readiness Score (computed from quality thresholds)
- Dataset / Prompt / Hyperparameter / Model / Prediction / Cost summaries
- Prioritized list of recommendations
- Action Plan (numbered list from top 5 recommendations)

This report is sent back to the extension as a **JSON response** in the HTTP response body.

### Step 9: Extension displays the results

The extension receives the JSON report and:

- Updates the **Overview sidebar** with project info (name, framework, model, scores)
- Stores the result in VS Code's global state for later use
- The **Reports sidebar** shows summary items
- You can click **"View Report"** to open a formatted HTML panel with the full report

### Step 10: You can also use the Chat

```
User types a question  →  Extension sends HTTP POST /api/v1/chat/message
                       →  Backend returns "pending" (stub!)
                       →  Chat window shows: "Backend received the message
                           but AI integration is pending."
```

**The chat endpoint is NOT yet wired to the AI.** There is a `ChatEngine` class (`backend/chat/engine.py`) that is *designed* to answer questions by building a context string from your project data and sending it to an LLM. But the API route currently just returns a stub message. The LLM provider infrastructure is all in place, just not connected to the chat route yet.

### Step 11: WebSocket streaming (alternative path)

There is also a **WebSocket** connection (`backend/api/websocket.py`) at:

```
WebSocket → /api/v1/ws/analysis
```

This runs the same full pipeline but **streams progress in real-time** to the client — sending events like "Scanning project...", "Analyzing dataset...", "Generating recommendations...", etc. This is for a smoother user experience when analysis takes a long time.

---

## 4. Key Questions Answered

### Q: Does this project use RAG (Retrieval-Augmented Generation)?

**Short answer: No, not yet.**

The `ChatEngine` (`backend/chat/engine.py`) builds a **simple context string** from your project data and sends it together with your question to an LLM. It does **not** use a retrieval system — there is no document index, no embedding search, and no vector database. It simply concatenates the project name, framework, health score, readiness score, and top recommendations into a text block, then sends it all as one prompt.

However, the architecture **supports** adding RAG in the future. The requirements document explicitly lists RAG under "Future Intelligence" (Section 76). When that day comes, a retrieval layer can be added between the scanner and the chat engine without breaking the existing structure.

### Q: Does this project use APIs?

**Yes, in two ways:**

1. **Backend REST API**: The Python FastAPI server exposes HTTP endpoints (for example, `POST /api/v1/project/analyze`). The VS Code extension calls these using **Axios** (an HTTP client library in TypeScript).

2. **LLM Provider APIs**: When the chat and AI analysis features are fully wired up, the backend will make HTTP calls (using **httpx**, an async HTTP client in Python) to external LLM APIs:
   - **OpenAI API** (`https://api.openai.com/v1/chat/completions`) — requires an OpenAI API key
   - **Anthropic API** (`https://api.anthropic.com/v1/messages`) — requires an Anthropic API key
   - **Ollama** (`http://localhost:11434`) — runs locally on your computer, no API key needed

   The system uses a **provider abstraction layer** so you can switch between providers. Your API keys are configured via environment variables (`.env` file) or VS Code settings and are **never hardcoded** in the source code.

3. **WebSocket**: The extension can also connect to a WebSocket endpoint for live progress streaming during analysis.

### Q: What does it do with the dataset you "now have"?

The user mentioned that "earlier there was no dataset, and now there is one." Here is what happens:

When you have a dataset in your project (for example, `data.json` or `dataset.jsonl`), the **scanner** discovers it and records its path. In a fully-implemented system, the **DatasetAnalyzer** would then:

- Open and read the dataset file
- Count how many training samples it contains
- Check for duplicate or near-duplicate samples
- Detect missing fields or malformed records
- Measure consistency (formatting, language, instruction/response quality)
- Compute a quality score (0–100 percent)
- Generate specific findings and recommendations

**Current state**: The scanner *does* find your dataset file, but the DatasetAnalyzer *does not* actually read it — it returns hardcoded numbers (1000 samples, 2.5 percent duplicates, 0.88 quality score). The architecture and data structures are ready for real dataset analysis, but that logic has not been implemented yet.

---

## 5. How Each Feature Works

### Feature 1: Project Scanner

**Purpose**: Understands your project before any analysis begins.

**How it works**:
1. Takes a project folder path.
2. Uses Python's `pathlib.Path.rglob()` to recursively search for files matching known patterns.
3. For framework detection, reads `requirements.txt` or `pyproject.toml` and checks if known libraries (transformers, peft, trl, axolotl, unsloth) are listed.
4. Returns a dictionary with all discovered files and metadata.
5. **Never modifies files** — it only reads.

### Feature 2: Dataset Intelligence

**Purpose**: Evaluate dataset quality.

**How it works** (intended):
1. Reads the dataset file (JSONL/CSV/JSON).
2. For each sample, checks fields, lengths, formatting.
3. Detects duplicates using string/similarity comparison.
4. Measures response diversity and language consistency.
5. Produces a quality score, findings, warnings, and recommendations.

**Current state**: Stub. Returns `sample_count=1000`, `quality_score=0.88`, `duplicate_percentage=2.5` regardless of the actual file.

### Feature 3: Prompt Intelligence

**Purpose**: Evaluate prompt templates.

**How it works** (intended):
1. Reads prompt template files.
2. Checks for clarity, ambiguity, consistency, formatting.
3. Detects conflicting instructions, missing placeholders, prompt leakage.
4. Scores instruction quality and role definitions.

**Current state**: Stub. Returns hardcoded scores (clarity=0.85, ambiguity=0.2).

### Feature 4: Hyperparameter Advisor

**Purpose**: Check training configuration.

**How it works** (intended):
1. Reads `config.yaml` or `config.toml`.
2. Extracts learning rate, batch size, epochs, optimizer, LoRA settings.
3. Flags issues: learning rate too high (above 1e-3), batch too small (below 4), too many epochs (above 10).
4. Estimates overfitting/underfitting risk.

**Current state**: Stub. Returns hardcoded values (lr=2e-4, batch=8, epochs=3).

### Feature 5: Base Model Advisor

**Purpose**: Evaluate model-task fit.

**How it works** (intended):
1. Uses the model name detected from config.
2. Compares against known model capabilities (reasoning, coding, multilingual, context length, VRAM).
3. Recommends alternatives with trade-offs.

**Current state**: Stub. Returns hardcoded info (7B params, 4096 context, 8GB VRAM).

### Feature 6: Cost Estimator

**Purpose**: Estimate computational resources.

**How it works** (intended):
1. Uses model size, dataset size, and hyperparameters.
2. Estimates training time, GPU hours, VRAM, storage, checkpoint size.
3. Lists compatible hardware (RTX 3090, A10G, etc.).

**Current state**: Stub. Returns hardcoded estimates (2–4 hours, 3.0 GPU-hours).

### Feature 7: Prediction Engine

**Purpose**: Predict training outcomes before training.

**How it works** (intended):
1. Combines dataset quality, hyperparameters, and model capabilities.
2. Estimates instruction-following, hallucination risk, reasoning, etc.
3. Each prediction includes a confidence score (never claims certainty).

**Current state**: Stub. Returns hardcoded predictions.

### Feature 8: Recommendation Engine

**Purpose**: Turn analysis results into actionable advice.

**How it works**:
1. Takes all analyzer results as input.
2. Applies conditional rules to generate recommendations:
   - Duplicate percentage above 5 percent then recommend deduplication
   - Learning rate above 1e-3 then recommend reducing it
3. Sorts recommendations by severity (critical then high then medium then low).
4. Each recommendation includes evidence, reasoning, confidence, and suggested actions.

**Current state**: Partially real. Has 2 actual rules, but most analysis data is still stubbed.

### Feature 9: Report Generator

**Purpose**: Create a single, comprehensive engineering report.

**How it works**:
1. Takes ProjectContext plus all analyzer results, predictions, cost estimates, and recommendations.
2. Computes Project Health Score (average of dataset quality plus hyperparameter efficiency).
3. Computes Training Readiness Score (pass/fail thresholds on quality metrics).
4. Builds executive summary text.
5. Creates an action plan (numbered list from top 5 recommendations).
6. Returns a structured `EngineeringReport` object.

**Current state**: Fully functional logic, but operates on stubbed analyzer data so the scores are based on hardcoded values.

### Feature 10: Chat Interface

**Purpose**: Let you ask questions about your project in plain English.

**How it works** (intended):
1. You type a question in the chat sidebar.
2. The extension sends it to `POST /api/v1/chat/message`.
3. The `ChatEngine` builds a context string from your project analysis.
4. It sends the context plus question to an LLM (via OpenAI/Anthropic/Ollama API).
5. Returns the LLM's answer with references and confidence level.

**Current state**: The API endpoint is a **stub** — returns "Backend received the message but AI integration is pending." The ChatEngine class exists and is *designed* to work, but it is not wired into the API route. The LLM provider infrastructure is in place but not connected to the chat.

### Feature 11: Safe File Editing

**Purpose**: Let the system propose changes to your files, which you must approve before they are applied.

**How it works**:
1. The `FileEditor` generates a unified diff (before/after) of the proposed change.
2. It assigns a unique change ID.
3. Changes are **never** applied silently.
4. When you approve, the original file is backed up to `.llm_training_agent_backups/`.
5. The new content is written.
6. You can **roll back** any approved change.

**Current state**: Fully implemented in `backend/editing/file_editor.py`. Not yet exposed through a dedicated API endpoint.

### Feature 12: Experiment Tracker

**Purpose**: Remember your past training runs.

**How it works** (intended):
1. After training, you save an experiment record.
2. It stores: dataset version, model, tokenizer, hyperparameters, metrics, notes, timestamps.
3. You can browse and compare past experiments.

**Current state**: The `ExperimentService` and database tables exist, but the `list_experiments` method returns an empty list (stub). The `save_experiment` method is functional but not exposed via API yet.

### Feature 13: Storage (SQLite)

**Purpose**: Persist projects, analyses, experiments, chat history, and file changes.

**How it works**:
1. Uses **SQLite** (via SQLAlchemy ORM) as the database.
2. Tables exist for: Projects, Analyses, Dataset Reports, Prompt Reports, Hyperparameter Reports, Model Reports, Predictions, Cost Estimates, Recommendations, Experiments, Chat Sessions, Chat Messages, File Modifications, and Settings.
3. Uses a **Repository pattern** for clean data access.
4. Async sessions via `aiosqlite`.

**Current state**: Database schema is fully designed and tables can be created. However, the **API routes do not use the database** — each analysis returns fresh data and is not persisted. Storage is scaffolded but not wired into the API layer.

---

## 6. The Data Models (What Gets Passed Around)

All data structures are defined in `backend/models/schemas.py` using **Pydantic** (a Python library for data validation):

- **`ProjectContext`** — The central object. Holds project name, framework, model, dataset paths, configs, scripts, hardware info. Every analyzer receives this.
- **`DatasetAnalysisResult`** — Sample count, token count, duplicate percent, quality score, findings, recommendations.
- **`PromptAnalysisResult`** — Clarity score, ambiguity score, formatting, detected issues.
- **`HyperparameterAnalysisResult`** — Learning rate, batch size, epochs, overfitting/underfitting risk, efficiency score.
- **`ModelAnalysisResult`** — Model name, parameter count, VRAM, capabilities (reasoning, coding, multilingual).
- **`CostEstimate`** — Training time, GPU hours, VRAM, storage, compatible hardware.
- **`PredictionResult`** — Instruction following, hallucination risk, reasoning, creativity, failure modes.
- **`Recommendation`** — Title, description, reasoning, evidence, severity, confidence, affected files, suggested actions.
- **`EngineeringReport`** — The final report: executive summary, health score, readiness score, all summaries, recommendations, action plan.

These same structures flow through the system: scanner then context builder then analyzers then prediction then recommendation then report.

---

## 7. The AI Provider System

The project supports multiple AI providers through an **abstraction layer**:

| Provider | Connection Method | Key Needed? |
|---|---|---|
| **OpenAI** | HTTP to `api.openai.com` | Yes (OpenAI API key) |
| **Anthropic** | HTTP to `api.anthropic.com` | Yes (Anthropic API key) |
| **Ollama** | HTTP to `localhost:11434` | No (runs on your computer) |

**How it works**:
1. You pick a provider in VS Code settings (default is "ollama").
2. When the chat or AI analysis runs, it picks the right provider.
3. It sends your prompt over HTTP using `httpx` (Python HTTP client).
4. The LLM responds with text (or JSON if a schema is requested).
5. The response is parsed and returned.

**Important**: The provider abstractions exist in two forms in the codebase (an older `generate()`-based one and a newer `chat_completion()`-based one). This is a transitional state during refactoring. The older system is used by `ChatEngine`; the newer system is the intended direction.

### The Prompt System

All prompts are stored as **markdown files** in `backend/ai/prompts/`, organized into three folders:

- **`system/`** — System prompts that define the AI's role:
  - `analyst.md` — "You are an experienced ML engineering analyst" (for analysis tasks)
  - `chat.md` — "You are an ML engineering assistant" (for conversational Q&A)
  - `editor.md` — "You are an engineering editor" (for proposing file changes)

- **`analyzers/`** — Prompts for each analysis module:
  - `dataset.md` — Defines the schema for dataset quality analysis
  - `prompt.md` — Defines the schema for prompt quality analysis
  - `hyperparameters.md` — Defines the schema for hyperparameter analysis
  - `model.md` — Defines the schema for model evaluation
  - `cost.md` — Defines the schema for cost estimation
  - `prediction.md` — Defines the schema for training outcome prediction

- **`meta/`** — Higher-level prompts:
  - `recommendation.md` — How to merge all results into prioritized recommendations
  - `report.md` — How to generate the final engineering report
  - `chat_context.md` — How to build chat context from project data

These prompts define **structured output schemas** (JSON), so the AI returns *data*, not free-form text. This makes the output testable, reliable, and easy to store.

---

## 8. Current State Summary

| Component | Implementation Status |
|---|---|
| Project Scanner | Fully working — reads real filesystem |
| Framework Detector | Fully working — parses requirements files |
| Context Builder | Fully working — converts to typed model |
| Dataset Analyzer | Stub — hardcoded values, no real file reading |
| Prompt Analyzer | Stub — hardcoded values |
| Hyperparameter Analyzer | Stub — hardcoded values |
| Model Advisor | Stub — hardcoded values |
| Cost Estimator | Stub — hardcoded values |
| Prediction Engine | Stub — hardcoded values |
| Recommendation Engine | Partially working — 2 real conditional rules |
| Report Generator | Fully working — real scoring logic |
| Chat Engine | Implemented but NOT wired to API (endpoint is a stub) |
| File Editor | Fully working — real diff, backup, rollback |
| Storage (SQLite) | Schema ready but NOT used by API routes |
| Experiment Tracker | Partial — save works, list is stub |
| WebSocket streaming | Fully implemented — real progress events |
| VS Code Extension UI | Fully working — sidebar, chat, commands |
| Tests | Passing — but they test stub behavior, not real analysis |

---

## 9. How It Will Achieve the Goal

Once the stub analyzers are replaced with real file-reading logic, the complete end-to-end flow will be:

```
Your project folder
  → Scanner reads your files (REAL — discovers datasets, configs, scripts)
  → ContextBuilder structures them (REAL — creates ProjectContext object)
  → Analyzers read and evaluate your actual data (TO BE IMPLEMENTED)
  → Prediction Engine estimates outcomes (TO BE IMPLEMENTED)
  → Recommendation Engine generates advice (PARTIALLY REAL — 2 rules live)
  → Report Generator builds your report (REAL — computes real scores)
  → VS Code shows you findings, recommendations, and chat (REAL — working UI)
```

The key remaining work is upgrading the five analyzers from hardcoded stubs to real file-reading logic. This means:
- **DatasetAnalyzer**: Open and parse JSONL/CSV/JSON dataset files, compute real statistics.
- **PromptAnalyzer**: Read prompt template files, check for real issues.
- **HyperparameterAnalyzer**: Parse YAML/TOML config and extract real hyperparameters.
- **ModelAdvisor**: Look up real model specifications.
- **CostEstimator**: Calculate real resource estimates from model size and dataset size.

All the infrastructure needed for this is already in place — the prompts, schemas, provider abstractions, and test frameworks are ready. The project is architecturally complete; it just needs the analyzer logic plugged in.

---

## Appendix A: Every File and Its Purpose

Below is a complete listing of the key files in the project, grouped by directory, with a one-line description of what each does.

### Root Files (PROJECT_TEMPLATE)

| File | Purpose |
|---|---|
| `requirements.md` | The master specification — defines every feature, rule, and requirement for the project. |
| `README.md` | Quick-start guide: how to install and run the project. |
| `ARCHITECTURE.md` | Short overview of the system architecture. |
| `ROADMAP.md` | Planned milestones and timeline. |
| `CHANGELOG.md` | What changed in each version. |
| `LICENSE` | MIT license file. |
| `task_progress.md` | Current build progress tracker. |

### Backend (`backend/`) — Python Analysis Engine

| File | Purpose |
|---|---|
| `main.py` | App entry point — creates the FastAPI server and mounts all routes and WebSocket. |
| `requirements.txt` | Python dependencies (FastAPI, SQLAlchemy, httpx, pytest, etc.). |

#### `backend/core/` — Core Infrastructure
| File | Purpose |
|---|---|
| `config.py` | Loads settings from environment variables and `.env` files (host, port, API keys, provider defaults). |
| `errors.py` | Custom error classes: `AppError`, `AnalysisError`, `ProviderError`, `ValidationError`. |
| `logging.py` | Structured logging configuration (debug, info, warning, error, critical levels). |
| `di.py` | Dependency injection wiring (how components get their dependencies). |

#### `backend/scanner/` — Project Discovery (FULLY WORKING)
| File | Purpose |
|---|---|
| `scanner.py` | `ProjectScanner` class — walks your project folder and finds datasets, configs, scripts, models, and framework. The only module that genuinely reads your files. |
| `framework_detector.py` | `FrameworkDetector` class — reads `requirements.txt`/`pyproject.toml` and detects HuggingFace, Axolotl, or Unsloth. |
| `context_builder.py` | `ContextBuilder` class — converts the raw scan dictionary into a typed `ProjectContext` object. |

#### `backend/analyzers/` — Analysis Modules (ALL STUBS)
| File | Purpose |
|---|---|
| `base.py` | `Analyzer` abstract interface — defines what every analyzer must implement. |
| `dataset_analyzer.py` | `DatasetAnalyzer` — should read your dataset and score quality. Currently returns hardcoded values. |
| `prompt_analyzer.py` | `PromptAnalyzer` — should analyze prompt templates. Currently returns hardcoded scores. |
| `hyperparameter_analyzer.py` | `HyperparameterAnalyzer` — should check training config. Currently returns hardcoded values. |
| `model_advisor.py` | `ModelAdvisor` — should evaluate model choice. Currently returns hardcoded info. |
| `cost_estimator.py` | `CostEstimator` — should estimate training resources. Currently returns hardcoded estimates. |

#### `backend/prediction/` — Outcome Prediction (STUB)
| File | Purpose |
|---|---|
| `engine.py` | `PredictionEngine` class — should predict training outcomes. Currently returns hardcoded predictions. |

#### `backend/recommendation/` — Recommendations (PARTIALLY REAL)
| File | Purpose |
|---|---|
| `engine.py` | `RecommendationEngine` class — merges all analysis results into prioritized recommendations. Has 2 real rules (duplicates, learning rate). |

#### `backend/reports/` — Report Generation (FULLY WORKING)
| File | Purpose |
|---|---|
| `generator.py` | `ReportGenerator` class — builds the final `EngineeringReport` with health score, readiness score, summaries, and action plan. |

#### `backend/chat/` — Chat Interface (IMPLEMENTED, NOT WIRED)
| File | Purpose |
|---|---|
| `engine.py` | `ChatEngine` class — designed to answer questions by building a context string and sending it to an LLM. Not yet connected to the API route. |

#### `backend/editing/` — Safe File Editing (FULLY WORKING)
| File | Purpose |
|---|---|
| `editor.py` | Editor orchestrator for managing file modifications. |
| `file_editor.py` | `FileEditor` class — generates diffs, applies changes with backup, supports rollback. |

#### `backend/experiments/` — Experiment Tracking (PARTIAL)
| File | Purpose |
|---|---|
| `service.py` | `ExperimentService` class — saves experiment records to SQLite. List method returns empty (stub). |

#### `backend/storage/` — Database Layer (READY, NOT WIRED)
| File | Purpose |
|---|---|
| `database.py` | `Database` class — async SQLite connection via SQLAlchemy. |
| `models.py` | All ORM table models: Project, Analysis, DatasetReport, PromptReport, HyperparameterReport, ModelReport, Prediction, CostEstimateRecord, RecommendationRecord, Experiment, ChatSession, ChatMessageRecord, FileModification, Setting. |
| `repositories.py` | Repository pattern for clean CRUD data access. |

#### `backend/models/` — Data Schemas
| File | Purpose |
|---|---|
| `schemas.py` | All Pydantic data models: `ProjectContext`, `DatasetAnalysisResult`, `PromptAnalysisResult`, `HyperparameterAnalysisResult`, `ModelAnalysisResult`, `PredictionResult`, `CostEstimate`, `Recommendation`, `EngineeringReport`, `ApiError`. |

#### `backend/api/` — API Layer (FULLY WORKING)
| File | Purpose |
|---|---|
| `routes.py` | All REST endpoints: `/health`, `/project/analyze`, `/dataset/analyze`, `/prompt/analyze`, `/hyperparameters/analyze`, `/model/analyze`, `/predict/training`, `/cost/estimate`, `/chat/message`, `/chat/history`, `/experiments`, `/providers`, `/config`. |
| `websocket.py` | WebSocket endpoint at `/ws/analysis` — streams real-time progress events to the client. |

#### `backend/ai/` — AI Provider Layer
| File | Purpose |
|---|---|
| `base.py` | Old `AIProvider` ABC with `generate()`, `generate_structured()` methods. |
| `provider.py` | New `AIProvider` ABC with `chat_completion()`, `validate_credentials()`, `health_check()` methods. |
| `providers.py` | Old provider implementations (OpenAI, Anthropic, Ollama) + `get_provider()` factory. Uses the old interface. |
| `providers/openai_provider.py` | New OpenAI provider (chat_completion style, uses API key). |
| `providers/anthropic_provider.py` | New Anthropic provider (chat_completion style, uses API key). |
| `providers/ollama_provider.py` | New Ollama provider (chat_completion style, local, no key needed). |
| `prompts/system/analyst.md` | System prompt for the ML engineering analyst role. |
| `prompts/system/chat.md` | System prompt for the chat assistant role. |
| `prompts/system/editor.md` | System prompt for the file editing role. |
| `prompts/analyzers/dataset.md` | Prompt template for dataset analysis (defines JSON output schema). |
| `prompts/analyzers/prompt.md` | Prompt template for prompt analysis. |
| `prompts/analyzers/hyperparameters.md` | Prompt template for hyperparameter analysis. |
| `prompts/analyzers/model.md` | Prompt template for model evaluation. |
| `prompts/analyzers/cost.md` | Prompt template for cost estimation. |
| `prompts/analyzers/prediction.md` | Prompt template for training outcome prediction. |
| `prompts/meta/recommendation.md` | Prompt for merging results into recommendations. |
| `prompts/meta/report.md` | Prompt for final report generation. |
| `prompts/meta/chat_context.md` | Prompt for building chat context from project data. |

#### `backend/tests/` — Backend Tests
| File | Purpose |
|---|---|
| `conftest.py` | Shared pytest fixtures. |
| `test_scanner.py` | Tests for the ProjectScanner and FrameworkDetector (real filesystem tests). |
| `test_dataset_analyzer.py` | Tests for DatasetAnalyzer stub output. |
| `test_api.py` | Tests for API endpoints (health, missing-params errors). |
| `test_recommendation_engine.py` | Tests for recommendation engine with high/low duplicates. |
| `test_integration.py` | End-to-end test of the full analysis pipeline. |

### Extension (`extension/`) — VS Code Frontend

| File | Purpose |
|---|---|
| `package.json` | Extension manifest: name, commands, sidebar views, settings, dependencies. The "blueprint" of the extension. |
| `tsconfig.json` | TypeScript compiler configuration. |
| `vitest.config.ts` | Test runner configuration. |
| `README.md` | Extension-specific documentation. |
| `CHANGELOG.md` | Extension changelog. |
| `LICENSE` | MIT license. |
| `.vscodeignore` | Files excluded from the VSIX package. |
| `resources/icon.svg` | The Activity Bar icon. |
| `llm-training-agent-1.0.0.vsix` | Pre-built extension package (ready to install into VS Code). |

#### `extension/src/` — Main Extension Code
| File | Purpose |
|---|---|
| `extension.ts` | **Entry point** — activates the extension, sets up the sidebar views, registers commands, creates the API client and settings manager. |

##### `extension/src/commands/`
| File | Purpose |
|---|---|
| `analyzerCommands.ts` | Implements "Analyze Project" and "Analyze Dataset" — sends HTTP requests to the backend via the API client, shows progress notifications. |
| `chatCommands.ts` | Implements "Open Chat" command — reveals the chat sidebar view. |
| `index.ts` | Command registration index. |

##### `extension/src/services/`
| File | Purpose |
|---|---|
| `apiClient.ts` | **The HTTP client** — uses Axios to call every backend endpoint (analyze, chat, report, config, providers). |
| `settings.ts` | `SettingsManager` class — reads/writes VS Code settings (backendUrl, provider, model). |
| `apiClient.js` | Compiled JavaScript version of apiClient.ts. |

##### `extension/src/views/`
| File | Purpose |
|---|---|
| `simpleTreeView.ts` | Tree data provider for the Overview and Reports sidebar panels. |
| `chatWebviewProvider.ts` | Full chat UI embedded in the sidebar — renders message bubbles, handles user input, sends messages to backend. |
| `viewIds.ts` | View ID constants (overview, chat, reports). |

##### `extension/src/utils/`
| File | Purpose |
|---|---|
| `index.ts` | Helper functions: `formatError()` (human-readable error messages) and `generateReportHtml()` (renders reports as styled HTML). |

##### `extension/src/types/`
| File | Purpose |
|---|---|
| (TypeScript type definitions for the extension.) |

##### `extension/tests/`
| File | Purpose |
|---|---|
| `runTest.ts` | VS Code extension test runner. |
| `suite/` and `unit/` | Test files for the extension UI. |

### Documentation (`docs/`)

| File | Purpose |
|---|---|
| `requirements_analysis.md` | Requirements Analyst's analysis of all functional and non-functional requirements. |
| `ai_design.md` | Solution Architect's design of the AI architecture and intelligence pipeline. |
| `prompt_design.md` | Prompt Engineer's design of system prompts, analyzer prompts, and chat prompts. |
| `api_specification.md` | API Designer's specification of all endpoints, request/response models. |
| `json_schemas.md` | Schema Designer's JSON validation rules. |
| `AGENT_ARCHITECTURE.md` | Multi-agent workflow architecture. |
| `AZURE_FREE_TIER.md` | Guide for using Azure free tier. |
| `FIND_PAT_GUIDE.md` | Pattern finding guide. |
| `GITHUB_REPO_SETUP.md` | GitHub repository setup instructions. |
| `MARKETPLACE_DEPLOYMENT.md` | How to publish to the VS Code Marketplace. |
| `MULTI_PROVIDER_API.md` | Multi-provider API usage guide. |
| `PUBLISHING_STEPS.md` | Step-by-step publishing checklist. |
| `complete_project_report.md` | This report. |

### Root-Level Build Scripts

| File | Purpose |
|---|---|
| `build_all.py` | Master build script — builds both backend and extension. |
| `build_ext.py` | Builds the VS Code extension. |
| `build_extension.py` | Alternative extension build script. |
| `build_helper.py` | Helper utilities for building. |
| `builder.js` | JavaScript build orchestrator. |
| `gen_files.py` / `gen_all.py` | Code generation scripts. |
| `make_docs.py` | Documentation generation script. |
| `write_all_files.js` / `write_commands.py` / `writer.js` | File writing utilities. |
| `final_build.py` | Final build verification script. |
| `cmd.txt` | Command reference. |
| `PROMPT_LIBRARY.md` | Library of prompts used by the system. |
| `REVIEW_CHECKLIST.md` | Internal review checklist. |
| `TESTING_REPORT.md` | Testing status report. |
| `CODING_STANDARDS.md` | Coding standards document. |
| `ENGINEERING_PRINCIPLES.md` | Engineering philosophy document. |


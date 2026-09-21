# 8 — Core Analyzer Functionality: Real Project Analysis

**Scope:** Dataset Analyzer, Prompt Analyzer, Hyperparameter Advisor, Model Advisor, Cost Estimator
(+ the downstream Prediction Engine, Recommendation Engine and Report Generator that consume their outputs).

---

## 1. What the components were before, and how they worked

### 1.1 Dataset Analyzer (`backend/analyzers/dataset_analyzer.py`)

**Before:** The analyzer already read real dataset files (via `cleaning/dataset_io.py`) and computed
real statistics: sample counts, character-length averages, exact/near duplicate percentages, missing-field
percentages, consistency scores and a composite quality score. However:

- It analyzed **only the first discovered dataset file** (`context.dataset_paths[0]`) and silently
  ignored every other dataset file in the project.
- It read entire files into memory with no bound (only the separate cleaning pipeline had a 200 MB cap).
- When a file was empty or fully unparseable, it returned `confidence="high"` with all-zero scores —
  an over-confident state that looked like a real measurement.
- Missing/extra dataset files were never reported.

### 1.2 Prompt Analyzer (`backend/analyzers/prompt_analyzer.py`)

**Before:** It read the first discovered prompt-template file and computed real deterministic scores
(placeholder extraction, ambiguity word lists, clarity, formatting, instruction quality). Problems:

- The `POST /prompt/analyze` endpoint puts **inline template text** into `context.prompt_templates`,
  but the analyzer unconditionally treated the entry as a file path and called `read_text` on it.
  Pasted templates always failed with "Template file not found" and returned neutral 0.5 filler scores.
- When no template was found it returned `clarity/formatting/…=0.5` with `confidence="low"` —
  neutral filler values that looked like measurements.

### 1.3 Hyperparameter Analyzer (`backend/analyzers/hyperparameter_analyzer.py`)

**Before:** It read real values from the project's YAML/TOML config files when present. But:

```python
# Apply defaults if still unknown
lr = lr or 2e-4
batch_size = batch_size or 8
epochs = epochs or 3
```

If no configuration existed, the analyzer **fabricated** `learning_rate=2e-4`, `batch_size=8`,
`epochs=3` and then assessed *those invented values* — returning "overfitting risk: medium" and an
efficiency score computed from numbers that were never in the user's project. There was also no way
to tell which values came from the user's config versus were invented.

### 1.4 Model Advisor (`backend/analyzers/model_advisor.py`)

**Before:** It maintained a static reference database of well-known models (Llama 3, Gemma, Mistral,
Qwen …) and produced a capability assessment from it. Problems:

- For **unknown models** it invented `"medium"` ratings for every capability and `context_length=4096`,
  presented like real data.
- The reference data was not labeled as reference data (risk of reading "estimated_vram" as measured).
- The actually detected GPU (`context.hardware_information`) was never consulted, so no feasibility
  check between the model's VRAM needs and the user's hardware was made.
- LLM enhancement output was merged without type validation.

### 1.5 Cost Estimator (`backend/analyzers/cost_estimator.py`)

**Before:** It used the correct FLOPs-based training-time formula (`6 × P × tokens`), but every input
was padded with placeholders:

| Input | Before |
|---|---|
| Model parameter count | Defaulted to **7.0B** when unknown |
| Dataset samples | Defaulted to **1000** when unknown |
| Batch size / epochs / seq length | Hardcoded defaults 8 / 3 / 512 |
| Tokens per sample | `max(seq_length, 20)` — a comment even said "assume 20 tokens" |
| Reference GPU | Always RTX 4090 (163 TFLOPS), regardless of the detected GPU |
| Training method | Always assumed QLoRA without labeling it as an assumption |

As a result the estimator produced a *specific-looking number* (e.g. "3.2 GPU-hours") even for
projects with no model, no dataset and no config — a fabricated estimate.

### 1.6 Downstream layers (leak multipliers)

- `prediction/engine.py` was a **fully hardcoded stub** — every prediction was literally `"good"/"low"`
  with a comment `# Stub implementation`, regardless of the analysis inputs.
- `reports/generator.py` `_compute_readiness_score` returned hardcoded **0.85 / 0.6** and
  `_compute_health_score` injected a hardcoded 0.8 for the model component.
- The scanner's `_detect_model` returned the **placeholder string `"detected_in_config"`** instead of
  the actual model name, which then could never be resolved by the Model Advisor or Cost Estimator.
- The Recommendation Engine only had two rules (duplicates, learning rate) and ignored the prompt,
  model, cost and prediction results it received.
- A stale copy of the whole backend existed under `extension/backend/` (packaged for the .vsix) and
  was **not synchronized**, so two diverging analyzer implementations existed in the repo.

---

## 2. Why this was a problem

1. **Fabricated results presented as facts.** Defaults such as `lr=2e-4 / batch 8 / epochs 3` and
   `param_count=7B / 1000 samples` flowed into risk assessments, cost estimates and the final report.
   A user with no config saw "overfitting risk: medium" and "3.2 GPU-hours" — pure invention.
2. **Violates the tool's core promise.** The product's purpose is to analyze *the user's actual
   project*. A hardcoded "everything is good" prediction and fixed readiness score of 0.85/0.6 made
   the report meaningless (identical for every project).
3. **Untrustworthy confidence signals.** Empty datasets returned `confidence="high"`; unknown models
   got confident-looking "medium" capability ratings. Users cannot calibrate trust when confidence is
   fabricated.
4. **Hidden information loss.** Only the first dataset file was analyzed; multi-file projects were
   silently under-analyzed. Unbounded reads risked memory exhaustion on large datasets.
5. **Broken entry point.** The `/prompt/analyze` endpoint was effectively non-functional for inline
   templates (its main use case).
6. **Duplicate implementations.** The stale `extension/backend` copy meant fixes to one copy did not
   reach users of the packaged extension.

---

## 3. What was fixed, and how

### 3.1 Dataset Analyzer
- **Multi-file analysis**: all discovered dataset files are analyzed and aggregated (directories are
  expanded deterministically, same suffix rules as the cleaning pipeline). Missing files, empty files
  and files beyond the file cap are reported in `warnings` instead of being silently ignored.
- **Bounded memory**: per-file cap (`50,000` records), total cap (`100,000` records) and file-count cap
  (`20`), with explicit truncation warnings. Read-only — nothing is ever written to the user's project.
- **Honest empty state**: zero readable records → all metrics 0, `confidence="very_low"`, findings
  explaining *which* files were empty/unparseable and why. No statistics are invented.
- **Small-dataset damping fixed**: the quality formula dampened tiny datasets by multiplying the whole
  score by `n/1000`, which zeroed out clean 60-sample datasets (`quality=0.0`). It now applies a gentle
  documented dampening (`0.7 + 0.3 × size_factor`) so small-but-clean data is never reported as 0.
- **Deterministic**: sorted file order, sequential reads, hash-based duplicate detection.

### 3.2 Prompt Analyzer
- Added `_resolve_template()`: an entry is treated as a **file path** if it resolves to a file,
  otherwise as **inline template content** when it looks like content (multi-line/long). This makes
  `POST /prompt/analyze` work for pasted templates for the first time.
- Missing templates / empty projects now return `confidence="very_low"` with 0 scores and an explicit
  issue ("No prompt templates found") instead of neutral 0.5 filler.
- LLM enhancement failures still degrade gracefully to the deterministic result (unchanged behavior).

### 3.3 Hyperparameter Analyzer
- **Removed all fabricated defaults.** Missing values stay `None` and are reported in a new
  `findings` list (`"learning rate: not found in the project configuration."`), plus a recommendation
  to add a config. Confidence is now data-driven: `high` when all core values exist, `medium` when
  some, `very_low` when none.
- **Provenance**: every core value is labeled as coming from the request or the project configuration.
- Risk assessment now only evaluates *provided* values; `overfitting_risk`/`underfitting_risk` become
  `"unknown"` when nothing can be assessed, and the efficiency score is computed only over assessed
  parameters. LLM enhancement runs only when real values exist.

### 3.4 Model Advisor
- **Unknown models are honest**: capabilities = `"unknown"`, `context_length = 0`, VRAM
  `"unknown (model not in the reference database)"`, `confidence="low"`, weaknesses explain how to fix
  it. No invented "medium" ratings.
- All outputs now carry the note that specs are **static reference data, not measured performance**.
- **Hardware-aware check**: the actually detected GPU (from `context.hardware_information`) is compared
  against the model's reference VRAM estimate and any gap is added to `weaknesses`.
- LLM enhancement output is **validated** (only string lists accepted) and can never overwrite the
  reference-derived numeric specifications.

### 3.5 Cost Estimator
- **Real inputs first**: sample count and measured average sample length (chars/4 → tokens) come from
  the DatasetAnalyzer result, batch/epochs/seq-length from the HyperparameterAnalyzer result; the
  reference GPU comes from the actually detected hardware (matched against the reference table; unknown
  detected GPUs are labeled as such). Config-regex extraction is kept as a fallback.
- **Every assumption is labeled** in `assumptions`: e.g. `"Sequence length: 512 tokens (assumed
  default — not found in the project configuration)"`, `"Training method: QLoRA (assumed …)"`,
  `"GPU utilization: ~70% (heuristic …)"`, and the model parameter count is labeled as name-derived
  reference data.
- **Explicit uncertainty states**: when the model or dataset is unknown, `estimated_training_time`
  becomes `"unknown — model size or dataset size could not be determined"`, GPU-hours are `0.0`,
  VRAM/checkpoint/storage become `"unknown …"`, and `confidence="very_low"`. No fake numbers.
- Formula audit: `FLOPs = 6 × P × tokens` (standard training-cost approximation), utilization 0.70 and
  the ±50% time range are documented heuristics; QLoRA VRAM ≈ 1 GB/B-params (4-bit) + 4 GB overhead;
  full fine-tune checkpoint ≈ 10 bytes/param (FP16 + Adam states). Time formatting now reports
  seconds/4-decimal GPU-hours so tiny jobs don't round to a fake `0.0`.
- The unused LLM "enhancement" was removed — cost estimation is deterministic by design.

### 3.6 Cross-component fixes
- **Scanner**: `_detect_model` now extracts and returns the **actual model name** from
  `model_name_or_path` (YAML/JSON), instead of the placeholder `"detected_in_config"`.
- **Prediction Engine**: the hardcoded stub was replaced with deterministic predictions derived from
  the real dataset/hyperparameter/model results (instruction following, hallucination risk, formatting,
  reasoning, creativity, failure modes). Confidence reflects how many of the three evidence sources
  actually existed (`very_low` … `high`); a project with no data and an unknown model can no longer be
  predicted "good".
- **Report Generator**: readiness score is now a documented weighted blend of the real data quality,
  configuration efficiency (discounted when the config was missing) and model verifiability; the
  health score uses a documented model-confidence weight instead of a constant 0.8.
- **Recommendation Engine**: now uses all five analyzer outputs — new rules for unreadable datasets,
  missing fields, prompt-template issues, missing training configuration, unrecognized models and
  high hallucination risk, each citing measured evidence.
- **Pipeline wiring**: `/project/analyze` now passes the real `DatasetAnalysisResult` and
  `HyperparameterAnalysisResult` objects into the Cost Estimator.
- **Schema**: `HyperparameterAnalysisResult` gained an additive `findings: List[str] = []` field so
  provenance/missing-value findings reach the API and report.
- **Packaged copy synchronized**: `extension/backend/` was regenerated from `backend/` via the
  existing `build_backend_into_extension.py` script — one authoritative implementation per analyzer.

### 3.7 Error handling
- Analyzer failures are still caught per-analyzer in `/project/analyze` (a failing analyzer produces a
  structured error entry; the rest of the analysis continues).
- Nothing fabricates results on failure: unavailable LLM → deterministic result only; unreadable
  dataset → explicit "cannot be analyzed" state; unknown model → `"unknown"`; unknown cost inputs →
  `"unknown"` outputs.
- Analysis remains strictly read-only.

---

## 4. How the components work now

### Execution path (verified end-to-end)

```
User project
  → ProjectScanner        (discovers datasets/prompts/configs; detects the real base model)
  → ContextBuilder        (ProjectContext)
  → DatasetAnalyzer       (reads every dataset file, bounded & deterministic → measured stats)
  → PromptAnalyzer        (reads template file or inline content → deterministic scores)
  → HyperparameterAnalyzer(real config values or explicit "missing", with provenance)
  → ModelAdvisor          (reference database or honest "unknown"; hardware-aware)
  → CostEstimator         (FLOPs formula fed by measured dataset + config + detected GPU;
                           explicit "unknown" states and labeled assumptions)
  → PredictionEngine      (derived from the real results above)
  → RecommendationEngine  (rules citing measured evidence from all five analyzers)
  → ReportGenerator       (health/readiness scores computed from the real results)
  → /api/v1/project/analyze → VS Code extension UI
```

**Example verified run** (temporary 60-sample project + `config.yaml` + `prompt.txt`):

```
model: meta-llama/llama-3-8b-instruct      ← real name from the user's config
dataset: sample_count=62, quality=0.39, confidence=medium
hp: efficiency=0.9, overfitting_risk=low, confidence=high
cost: real GPU-hour estimate from the measured dataset & config, assumptions labeled
prediction: instruction_following=good, hallucination_risk=high (small dataset), confidence=high
health: 0.70, readiness: 0.66                ← computed, previously constant 0.85/0.6
recs: ["Mitigate hallucination risk before training", "Improve prompt template quality"]
```

**Key invariants guaranteed now**

| Situation | Old behavior | New behavior |
|---|---|---|
| No training config | Fake lr/batch/epochs analyzed | `None` + explicit findings, `confidence=very_low` |
| Unknown model | Invented "medium" capabilities | `"unknown"` capabilities, `confidence=low` |
| Unknown model + no dataset | Fabricated "3.2 GPU-hours" | `"unknown"` time, `0.0` GPU-hours, `confidence=very_low` |
| Empty dataset | 0-scores with `confidence="high"` | 0-scores with `confidence="very_low"` + per-file findings |
| Multiple dataset files | Only first file | All files aggregated, caps + warnings |
| Inline prompt template | "file not found" + 0.5 filler | Template analyzed directly |
| Any analyzer failure | — | Structured partial result; pipeline continues |

### Verification

- **98 backend tests pass** (79 pre-existing + 19 new in `backend/tests/test_core_analyzers.py`)
  covering: real-record statistics, multi-file aggregation, empty datasets, malformed JSONL, missing
  files, config-driven vs missing hyperparameters, cost formula math against hand-computed values,
  assumed-default labeling, detected-GPU usage, unknown models, inline prompt templates, prediction
  derivation (good *and* bad projects), and non-constant report scores. The scanner test was
  strengthened to assert the real model name (not the old placeholder).
- `ruff` and `mypy` show no new issues in the touched modules (remaining findings are pre-existing in
  unrelated files).
- End-to-end `/project/analyze` smoke test verified the full data flow into the report.
- `extension/backend` packaged copy verified identical to `backend/` (hash comparison).

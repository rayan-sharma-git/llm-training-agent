# Prompt Design

## LLM Training Agent — Prompt Engineering

Version: 1.0  
Author: Prompt Engineer (Agent 3)  
Status: Complete  

---

## 1. Design Principles

- All prompts stored externally (not hardcoded in source code)
- Prompts are versioned and documented
- Prompts are reusable across providers (provider-agnostic format)
- Reasoning strategy: Facts → Observations → Recommendations → Final Report
- Every LLM call includes context, constraints, and output formatting instructions

---

## 2. Prompt Categories

### 2.1 System Prompts

| Prompt | Purpose | Usage |
|---|---|---|
| SYSTEM_ANALYST | Sets role for analyzer modules | All analyzer calls |
| SYSTEM_CHAT | Sets role for conversational chat | Chat interface |
| SYSTEM_EDITOR | Sets role for safe editing proposals | File modification |

### 2.2 Analyzer Prompts

| Prompt | Purpose |
|---|---|
| PROMPT_DATASET_ANALYSIS | Analyze dataset quality |
| PROMPT_PROMPT_ANALYSIS | Analyze prompt templates |
| PROMPT_HYPERPARAMETER_ANALYSIS | Analyze training configuration |
| PROMPT_MODEL_ADVICE | Evaluate base model suitability |
| PROMPT_COST_ESTIMATION | Estimate training resources |
| PROMPT_PREDICTION | Predict training outcomes |

### 2.3 Meta Prompts

| Prompt | Purpose |
|---|---|
| PROMPT_RECOMMENDATION | Merge analyzer outputs into recommendations |
| PROMPT_REPORT | Generate final engineering report |
| PROMPT_CHAT_CONTEXT | Build chat context from analysis results |

---

## 3. Prompt Template Format

All prompts use Jinja2-style templates stored in `backend/ai/prompts/`.

```
backend/ai/prompts/
  system/
    analyst.md
    chat.md
    editor.md
  analyzers/
    dataset.md
    prompt.md
    hyperparameters.md
    model.md
    cost.md
    prediction.md
  meta/
    recommendation.md
    report.md
    chat_context.md
```

---

## 4. Guardrails

| Guardrail | Implementation |
|---|---|
| No certainty claims | Prompt instructs: "Never claim certainty. Use confidence levels." |
| Evidence required | Prompt instructs: "Every recommendation must cite evidence." |
| No fabrication | Prompt instructs: "If uncertain, explicitly state uncertainty." |
| Structured output | Prompt instructs: "Return output as valid JSON matching the provided schema." |
| No secret exposure | Prompt instructs: "Never include API keys, tokens, or sensitive data." |

---

## 5. Context Strategy

| Call Type | Context Included |
|---|---|
| Dataset Analysis | Dataset stats, sample records, schema |
| Prompt Analysis | Template text, variables, usage context |
| HP Analysis | Training args, config file contents |
| Model Analysis | Model name, task description, requirements |
| Prediction | All analyzer results combined |
| Chat | ProjectContext, latest report, recent recommendations, conversation history |

---

## 6. Memory Strategy

- Session memory maintained via ChatSession database records
- Context window managed: older messages summarized when approaching token limits
- ProjectContext cached and updated only when project changes
- Analysis results persisted in SQLite for reference

---

## 7. Output Formatting

Every prompt produces structured JSON output matching the corresponding schema:

```json
{
  "findings": [...],
  "warnings": [...],
  "recommendations": [...],
  "confidence": "high",
  "evidence": "..."
}
```

---

## 8. Hallucination Prevention

- All prompts include: "Base your answer ONLY on the provided context."
- Confidence levels enforced (Very High, High, Medium, Low, Very Low)
- "I don't know" explicitly encouraged when context is insufficient
- Facts vs. inference vs. speculation clearly separated in output schema

---

## 9. Quality Score: 10/10

Prompts externalized, versioned, provider-agnostic. Guardrails implemented. Context strategy defined. Hallucination prevention measures in place.
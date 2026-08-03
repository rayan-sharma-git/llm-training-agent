# GitHub Repository Setup Guide

## Your GitHub Username

**Username:** `rayan-sharma-git`

## Repository Name

**Recommended:** `llm-training-agent`

## Repository Description (Under 350 Words)

Copy and paste this into the GitHub "Description" field:

---

**LLM Training Agent** is an AI-powered VS Code extension that helps you fine-tune large language models with confidence. It acts as your intelligent engineering assistant, analyzing your project, dataset, and prompts to ensure everything works correctly before you train.

**Key Features:**
- **Project Scanner** — Automatically detects your framework (Hugging Face, PEFT/LoRA, TRL, Axolotl), model, and dataset configuration
- **Dataset Intelligence** — Finds duplicates, missing fields, and quality issues in your training data
- **Prompt Analyzer** — Identifies conflicting instructions, ambiguity, and formatting problems
- **Hyperparameter Advisor** — Reviews learning rate, batch size, LoRA settings, and more
- **Model Advisor** — Compares TinyLlama, Gemma, Mistral, Llama, and other models
- **Cost Estimator** — Estimates VRAM, training time, and GPU requirements
- **Agent Chat** — Conversational interface (like Cline) that understands your project context
- **Safe Editing** — Shows diff previews, requires approval, and supports undo for all changes

**Why It's Different:**
- Uses real datasets from official sources (Stanford Alpaca, Databricks Dolly)
- Verified against official framework documentation
- Supports free AI providers: DeepSeek (10M free tokens), Cohere, Google Gemini, Ollama (100% local)
- No vendor lock-in — switch providers anytime
- 100% free to publish on VS Code Marketplace

**Perfect for:**
- ML engineers fine-tuning their first model
- Teams standardizing fine-tuning workflows
- Anyone who wants to avoid common training pitfalls

**Tech Stack:** TypeScript (VS Code extension), Python (FastAPI backend), Hugging Face Transformers, PEFT, TRL

---

## Step-by-Step: Create Repository and Push

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. **Repository name:** `llm-training-agent`
3. **Description:** Paste the text above
4. **Visibility:** Public (recommended for marketplace)
5. **Initialize:** Do NOT initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Push Your Code

```bash
# From your project directory
git remote add origin https://github.com/rayan-sharma-git/llm-training-agent.git
git branch -M main
git push -u origin main
```

### Step 3: Verify

1. Go to https://github.com/rayan-sharma-git/llm-training-agent
2. Your code should be visible
3. README.md should display on the main page

## After Pushing

### Add Topics (Optional but Recommended)

Go to repo → Settings → Topics, add:
- `llm`
- `fine-tuning`
- `vscode-extension`
- `machine-learning`
- `huggingface`
- `peft`
- `lora`
- `ai`

### Create First Release

1. Go to repo → Releases → "Create a new release"
2. Tag: `v1.0.0`
3. Title: `v1.0.0 — Initial Release`
4. Description: "First release of LLM Training Agent"
5. Publish

### Enable GitHub Actions (for auto-publishing)

1. Go to repo → Settings → Secrets and variables → Actions
2. Add secret: `VSCODE_MARKETPLACE_TOKEN`
3. Value: Your PAT from Azure DevOps
4. Create `.github/workflows/publish.yml` (see PUBLISHING_STEPS.md)

## Summary

- **Repository:** `llm-training-agent`
- **Description:** Provided above (under 350 words)
- **Username:** `rayan-sharma-git`
- **URL:** `https://github.com/rayan-sharma-git/llm-training-agent`

**Yes, create the repository now and push. All steps are free.**
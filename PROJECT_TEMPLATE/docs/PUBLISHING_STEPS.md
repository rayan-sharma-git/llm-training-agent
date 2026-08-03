# Publishing to VS Code Marketplace — Step-by-Step

## Overview

**Total Time:** 30-60 minutes
**Total Cost:** $0
**Difficulty:** Easy

## Prerequisites (All Free)

- [ ] GitHub account (free)
- [ ] Microsoft account (free)
- [ ] VS Code installed (free)
- [ ] Node.js 18+ installed (free)

---

## Step 1: Prepare Your Extension (10 minutes)

### 1.1 Ensure Required Files Exist

Check that these files are in `PROJECT_TEMPLATE/extension/`:

```
extension/
├── package.json          ✅ Extension manifest
├── README.md             ✅ Description for marketplace
├── CHANGELOG.md          ✅ Version history
├── LICENSE               ✅ MIT or Apache license
├── icon.png              ✅ 128x128 pixel icon
└── .vscodeignore         ✅ Files to exclude
```

### 1.2 Update package.json

Edit `extension/package.json`:

```json
{
  "name": "llm-training-agent",
  "publisher": "your-unique-publisher-name",
  "version": "1.0.0",
  "description": "AI-powered assistant for LLM fine-tuning projects",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Machine Learning", "Other"],
  "keywords": ["llm", "fine-tuning", "machine-learning", "ai", "peft", "lora"],
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/llm-training-agent"
  },
  "license": "MIT"
}
```

**Important:** Replace `your-unique-publisher-name` with your chosen publisher ID.

### 1.3 Create Extension Icon

Create a 128x128 pixel PNG icon:
- Use Canva (free), Figma (free), or any image editor
- Simple design: brain or robot icon with "LLM" text
- Save as `extension/icon.png`

**Free icon options:**
- Use Flaticon.com (free icons)
- Use Font Awesome + screenshot
- Use VS Code icon generator

### 1.4 Write README.md

This is your marketplace listing description:

```markdown
# LLM Training Agent

AI-powered engineering assistant for LLM fine-tuning projects.

## Features

- **Project Scanner** — Automatically detects framework, model, dataset
- **Dataset Intelligence** — Finds duplicates, missing fields, quality issues
- **Prompt Analyzer** — Identifies conflicting instructions, ambiguity
- **Hyperparameter Advisor** — Reviews learning rate, batch size, LoRA config
- **Model Advisor** — Compares TinyLlama, Gemma, Mistral, Llama
- **Cost Estimator** — Estimates VRAM, training time, GPU requirements
- **Agent Chat** — Conversational interface like Cline
- **Safe Editing** — Shows diff preview, requires approval, supports undo

## Supported Frameworks

- Hugging Face Transformers
- PEFT (LoRA, QLoRA)
- TRL (SFTTrainer)
- Axolotl
- Unsloth

## Usage

1. Open your LLM fine-tuning project in VS Code
2. Click the LLM Training Agent icon in sidebar
3. Click "Analyze Project"
4. Review recommendations
5. Apply fixes with one click

## Requirements

- Python 3.10+ (for backend)
- Node.js 18+ (for extension)
- AI provider API key (DeepSeek, Cohere, OpenAI, etc.) — free options available

## Free AI Providers Supported

- **DeepSeek** — 10M free tokens
- **Cohere** — 4,000 requests/month free
- **Google Gemini** — 15 requests/minute free
- **Ollama** — 100% free, runs locally

## Links

- [Documentation](https://github.com/yourusername/llm-training-agent)
- [Report Issues](https://github.com/yourusername/llm-training-agent/issues)
- [View Source](https://github.com/yourusername/llm-training-agent)
```

### 1.5 Create CHANGELOG.md

```markdown
# Changelog

## [1.0.0] - 2025-01-03

### Added
- Initial release
- Project scanner for Hugging Face, PEFT, TRL, Axolotl
- Dataset intelligence (duplicates, quality, missing fields)
- Prompt analysis (conflicts, clarity, formatting)
- Hyperparameter advisor (learning rate, batch size, LoRA)
- Model advisor (TinyLlama, Gemma, Mistral, Llama)
- Cost estimator (VRAM, time, hardware)
- Agent chat interface (Cline-style)
- Safe file editing with diff preview
- Support for DeepSeek, Cohere, OpenAI, Ollama
```

### 1.6 Add LICENSE File

```bash
# Create MIT LICENSE
echo "MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction..." > extension/LICENSE
```

Or copy from: https://opensource.org/licenses/MIT

---

## Step 2: Install Publishing Tools (5 minutes)

### 2.1 Install vsce

```bash
npm install -g @vscode/vsce
```

### 2.2 Verify Installation

```bash
vsce --version
# Should show version number
```

---

## Step 3: Create Publisher Account (5 minutes)

### 3.1 Sign Up

1. Go to: https://marketplace.visualstudio.com/manage
2. Click "Sign in with Microsoft"
3. Use any Microsoft account (Outlook, Hotmail, Live, etc.)
4. **Cost:** $0

### 3.2 Create Publisher

1. Click "Create Publisher"
2. Fill in:
   - **Publisher ID:** `your-unique-name` (e.g., `ml-engineer-tools`)
   - **Display Name:** `Your Name or Organization`
   - **Email:** Your email
   - **Description:** Brief description
3. Click "Create"
4. **Cost:** $0

**Note:** Publisher ID must be unique across all marketplace extensions.

### 3.3 Verify Email

- Check your email for verification link
- Click link to verify
- **Cost:** $0

---

## Step 4: Create Personal Access Token (PAT) (5 minutes)

### 4.1 Go to Azure DevOps

1. Go to: https://dev.azure.com/
2. Sign in with same Microsoft account
3. **Cost:** $0

### 4.2 Create PAT

1. Click "User Settings" (top right) → "Personal Access Tokens"
2. Click "+ New Token"
3. Fill in:
   - **Name:** `VS Code Marketplace Publishing`
   - **Expiration:** 1 year (or custom)
   - **Scopes:** Check "Marketplace" → Check both "Acquire" and "Manage"
4. Click "Create"
5. **COPY THE TOKEN** (shown only once!)

**Important:** Save this token securely. You'll need it for publishing.

**Cost:** $0

---

## Step 5: Package Your Extension (5 minutes)

### 5.1 Navigate to Extension Directory

```bash
cd PROJECT_TEMPLATE/extension
```

### 5.2 Package

```bash
vsce package
```

### 5.3 Verify Output

You should see:
```
✓ Extension packaged: llm-training-agent-1.0.0.vsix
```

The `.vsix` file is your extension package.

**Cost:** $0

---

## Step 6: Publish to Marketplace (5 minutes)

### Option A: Publish Directly (Recommended for First Time)

```bash
vsce publish --pat YOUR_PERSONAL_ACCESS_TOKEN
```

Replace `YOUR_PERSONAL_ACCESS_TOKEN` with the token from Step 4.

### Option B: Publish VSIX File

```bash
vsce publish --packagePath llm-training-agent-1.0.0.vsix --pat YOUR_PERSONAL_ACCESS_TOKEN
```

### 6.1 Verify Success

You should see:
```
✓ Extension published successfully!
✓ View at: https://marketplace.visualstudio.com/items?itemName=your-publisher.llm-training-agent
```

**Cost:** $0

---

## Step 7: Verify Publication (5 minutes)

### 7.1 Check Marketplace

1. Go to: https://marketplace.visualstudio.com/manage
2. Your extension should show as "Published"
3. Click on extension name to view details

### 7.2 View Live Listing

1. Go to: `https://marketplace.visualstudio.com/items?itemName=your-publisher.llm-training-agent`
2. Your extension is now live!
3. Users can install it by searching "LLM Training Agent"

### 7.3 Test Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "LLM Training Agent"
4. Click "Install"
5. **Cost:** $0

---

## Step 8: Automate Future Updates (Optional)

### 8.1 Add GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to VS Code Marketplace

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '18.x'
      
      - run: npm install
      
      - run: npm run compile
      
      - run: vsce package
      
      - uses: HaaLeo/publish-vscode-extension@v1
        with:
          pat: ${{ secrets.VSCODE_MARKETPLACE_TOKEN }}
          registryUrl: 'https://marketplace.visualstudio.com'
```

### 8.2 Add GitHub Secret

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `VSCODE_MARKETPLACE_TOKEN`
4. Value: Your PAT from Step 4
5. Click "Add secret"

### 8.3 Create Release

1. Go to GitHub repo → Releases → "Create a new release"
2. Choose tag: `v1.0.0`
3. Title: `v1.0.0 — Initial Release`
4. Click "Publish release"
5. Extension auto-publishes to marketplace!

**Cost:** $0 (GitHub Actions free for public repos)

---

## Step 9: Promote Your Extension (Optional)

### 9.1 Share on Social Media

- Twitter/X: "Just published LLM Training Agent for VS Code!"
- LinkedIn: Post about helping ML engineers
- Reddit: r/MachineLearning, r/vscode

### 9.2 Add to GitHub Profile

Update GitHub profile README:
```markdown
## My Extensions

- [LLM Training Agent](https://marketplace.visualstudio.com/items?itemName=your-publisher.llm-training-agent) — AI assistant for fine-tuning
```

### 9.3 Write Blog Post

- Dev.to
- Medium
- Personal blog

---

## Troubleshooting

### Error: "Publisher not found"

**Solution:** Create publisher at https://marketplace.visualstudio.com/manage first

### Error: "Invalid PAT"

**Solution:** 
- Ensure PAT has "Marketplace" scope
- Generate new PAT at https://dev.azure.com/

### Error: "Package validation failed"

**Solution:**
- Check package.json for errors
- Ensure icon.png exists and is 128x128
- Verify README.md exists

### Error: "Extension name already taken"

**Solution:** Choose different name or add publisher prefix

---

## Summary

**Total Steps:** 9
**Total Time:** 30-60 minutes
**Total Cost:** $0

**What you get:**
- ✅ Live extension on VS Code Marketplace
- ✅ Unlimited downloads
- ✅ Unlimited updates
- ✅ Professional listing
- ✅ Global distribution

**Next Steps After Publishing:**
1. Monitor downloads on marketplace dashboard
2. Respond to GitHub issues
3. Release updates with new features
4. Build community

---

## Quick Reference Card

```
Step 1: Prepare files (10 min)
  ├─ package.json
  ├─ README.md
  ├─ CHANGELOG.md
  ├─ LICENSE
  ├─ icon.png
  └─ .vscodeignore

Step 2: Install vsce (5 min)
  └─ npm install -g @vscode/vsce

Step 3: Create publisher (5 min)
  └─ https://marketplace.visualstudio.com/manage

Step 4: Create PAT (5 min)
  └─ https://dev.azure.com/ → Personal Access Tokens

Step 5: Package (5 min)
  └─ cd extension && vsce package

Step 6: Publish (5 min)
  └─ vsce publish --pat YOUR_TOKEN

Step 7: Verify (5 min)
  └─ Check marketplace listing

Step 8: Automate (optional)
  └─ GitHub Actions workflow

Step 9: Promote (optional)
  └─ Share on social media
```

---

**You're ready to publish. Start with Step 1.**
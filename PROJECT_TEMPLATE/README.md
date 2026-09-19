# LLM Training Agent

AI-powered engineering assistant for LLM fine-tuning in VS Code.

> **Repository**: https://github.com/rayan-sharma-git/llm-training-agent

## What is it?

The **LLM Training Agent** is a VS Code extension with a local Python backend that scans your fine-tuning project and provides analysis, recommendations, chat, and reports. It supports multiple AI providers — including **Ollama** (fully local, no API key) and various cloud APIs — all configurable from a Settings view inside VS Code.

## Repository Layout

```
PROJECT_TEMPLATE/
├── backend/       # Python FastAPI backend
│   ├── main.py    # Backend entry point
│   ├── scanner/   # Project scanner (scanner.py)
│   ├── analyzers/ # Dataset, prompt, hyperparameter, model, cost analysis
│   ├── ai/        # AI provider abstraction (Ollama, OpenAI, ...)
│   └── api/       # REST API routes (/api/v1)
├── extension/     # VS Code extension (TypeScript)
│   ├── src/       # Extension source (commands, services, views)
│   └── backend/   # Bundled copy of the Python backend for the .vsix
└── docs/          # Technical documentation & design deliverables
```

## Quick Start (end users)

1. **Install Python 3.10+** and **Node.js 18+**.
2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Install & run the extension**:
   - Install the `.vsix` from `extension/` (or build it — see below).
   - Run the extension (F5 in VS Code). It **automatically starts the Python backend** on `http://127.0.0.1:8000`.

   To start the backend manually instead:
   ```bash
   cd backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

## Getting the extension from GitHub

1. Clone the repo: `git clone https://github.com/rayan-sharma-git/llm-training-agent.git`
2. Build the VSIX (see **Development** below) and install it via `code --install-extension llm-training-agent-1.0.0.vsix` or the Extensions panel → `...` → Install from VSIX.
3. The **Python backend runs locally** on `127.0.0.1:8000` — it is packaged inside the `.vsix`, and the extension auto-starts it. No cloud/Azure account is required.

## How "Analyze Project" works

```
User clicks "Analyze Project"
        ↓
Extension sends POST /api/v1/project/analyze  {projectPath}
        ↓
Python route calls ProjectScanner(project_path)
        ↓
backend/scanner/scanner.py discovers project files & framework
        ↓
Backend builds context, runs analyzers (dataset, prompt, hyperparameters, model, cost)
        ↓
Backend generates predictions, recommendations, and a report
        ↓
Result is returned and shown in the Overview / Reports views
```

## AI Settings

The **Settings view** (Activity Bar → LLM Training Agent → Settings) lets you:

- **Select a provider**: Ollama (local), OpenAI, Anthropic, Google Gemini, DeepSeek, Cohere, OpenRouter, or an OpenAI-compatible endpoint.
- **Select a model** (static lists, or free-text / Refresh Models for dynamic providers like Ollama & OpenRouter).
- **Enter an API key** (stored securely via **VS Code SecretStorage** — never committed to GitHub).
- **Test the connection** before using a provider.
- **Configure a custom base URL** for Ollama or OpenAI-compatible servers.

## Local AI — Ollama (no cost, no key)

1. Install Ollama from https://ollama.com.
2. Run `ollama serve` (or the Ollama app).
3. Pull a model: `ollama pull llama3.2`.
4. In Settings, select `Ollama` as provider.

## Free / no-cost AI options

- **Ollama** — fully local & free (no API key).
- **Google Gemini** — Google AI Studio free tier (rate-limited) — https://aistudio.google.com.
- **DeepSeek** — free tier (subject to current terms) — https://platform.deepseek.com.
- **Cohere** — free trial tier — https://dashboard.cohere.com.
- **OpenRouter** — several free models (`*-instruct:free`) — https://openrouter.ai.

## Reviewing Agent File Changes ("View Changes")

When the agent proposes a file modification, it is **never applied silently**. Every change is stored as a pending proposal that you review before accepting:

1. Run **"LLM Training Agent: View Changes"** from the Command Palette (or the title-bar button).
2. A QuickPick lists all pending proposed changes.
3. Selecting one opens VS Code's **native diff editor** — original content on the left, the agent's proposal on the right.
4. Choose **Apply** (change is written, with an automatic backup), **Discard** (file untouched), or **Rollback** (restore the file from backup).

Pending proposals persist on disk (`.llm_training_agent/pending_changes/`), so you can review them even after a restart. Backups live in `.llm_training_agent_backups/`.

## Troubleshooting
> Free tiers change often — confirm current availability on the provider's official site.

## Troubleshooting

- **Backend unavailable / connection refused** — the extension auto-starts the backend on `127.0.0.1:8000`. Check the Output panel → **LLM Training Agent: Backend**. Start it manually: `cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000`.
- **Python or dependencies missing** — install Python 3.10+ and run `pip install -r backend/requirements.txt`.
- **Scanner failure** — the scanner skips `.git`, `venv`, `node_modules`, `__pycache__`, etc., and continues past individual file errors.
- **Ollama unavailable** — ensure Ollama is running (`ollama serve`) and the URL in Settings is correct (`http://localhost:11434`).
- **API key missing / invalid** — go to Settings, enter the key, click Save, and Test Connection.
- **No workspace open** — the "Analyze Project" command requires an open folder.

## Development

```bash
# Backend + tests
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v

# Extension (compile, test, package)
cd extension
npm install
npm run compile
npm test
npm run package   # produces llm-training-agent-1.0.0.vsix

# Re-sync backend into the extension before packaging (if backend changed)
cd ..
python build_backend_into_extension.py
cd extension && npm run package
```

## License

MIT
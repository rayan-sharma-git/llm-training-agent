# LLM Training Agent

AI-powered engineering assistant for LLM fine-tuning in VS Code.

## Features

- **Activity Bar icon** — click the LLM Training Agent icon in the Activity Bar to open the sidebar.
- **Overview view** — shows project, provider, and model status.
- **Chat view** — a functional chat interface in the sidebar for asking questions about your fine-tuning project.
- **Reports view** — view analysis reports and generate new ones.
- **Settings view** — configure AI provider, model, and API key (stored securely via VS Code SecretStorage).
- **Commands**:
  - `LLM Training Agent: Analyze Project` — scans the workspace and refreshes the Overview view.
  - `LLM Training Agent: Analyze Dataset` — analyzes a selected dataset directory.
  - `LLM Training Agent: Open Chat` — opens the Chat sidebar view.
  - `LLM Training Agent: View Report` — opens the latest analysis report.
  - `LLM Training Agent: Configure AI Provider` — opens the Settings view.

## Quick Start

1. **Install Python 3.10+** and **Node.js 18+**.
2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Install extension dependencies**:
   ```bash
   cd extension
   npm install
   ```
4. **Run the extension** (F5 in VS Code) — the extension **automatically starts the backend** on `http://127.0.0.1:8000`.

   If the backend fails to auto-start, you can run it manually:
   ```bash
   cd backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

## How Analyze Project Works

```
User clicks "Analyze Project"
        ↓
Extension sends POST /api/v1/project/analyze
        ↓
Python backend route calls ProjectScanner(project_path)
        ↓
backend/scanner/scanner.py discovers project files
        ↓
Backend builds context and runs analyzers (dataset, prompt, hyperparameters, model, cost)
        ↓
Backend generates predictions, recommendations, and a report
        ↓
Result is returned to the extension and displayed in the Overview/Reports views
```

## AI Settings

The **Settings** view (sidebar) lets you:

- **Select a provider**: Ollama (local), OpenAI, Anthropic, Google Gemini, DeepSeek, Cohere, OpenRouter, or an OpenAI-compatible endpoint.
- **Select a model** (static lists for known providers, free-text for dynamic providers). For Ollama/OpenRouter you can click **Refresh Models** to query the service for available models.
- **Enter an API key** (stored securely via VS Code SecretStorage — never committed to GitHub).
- **Test the connection** to verify your provider configuration works.
- **Configure a custom base URL** for Ollama or OpenAI-compatible endpoints.

Changes are applied to both VS Code settings and the backend's runtime configuration, so subsequent AI calls (chat, analyzers, etc.) use the selected provider and model.

## Local AI — Ollama

To use **Ollama** (fully local, no API key):

1. Install Ollama from https://ollama.com.
2. Run `ollama serve` (or start the Ollama app).
3. Pull a model: `ollama pull llama3.2`.
4. In the extension Settings view, select **Ollama** as the provider.

The extension queries Ollama's `/api/tags` endpoint to discover installed models.

## Free / No-Cost AI Options

- **Ollama** — 100% local, free, no API key required.
- **Google Gemini** — Google AI Studio offers a free tier with rate limits; obtain an API key at https://aistudio.google.com.
- **DeepSeek** — offers a free tier (subject to their current terms); see https://platform.deepseek.com.
- **Cohere** — offers a free trial tier; see https://dashboard.cohere.com.
- **OpenRouter** — aggregates many models, some of which are free (e.g. `meta-llama/llama-3.1-8b-instruct:free`); see https://openrouter.ai.

> **Note**: Free tiers and availability can change. Always check the provider's official website for current terms.

## Troubleshooting

### Backend unavailable
- The extension auto-starts the backend on `127.0.0.1:8000`. Check the Output panel → **LLM Training Agent: Backend** for logs.
- If the backend did not start, start it manually:
  ```bash
  cd backend
  python -m uvicorn main:app --host 127.0.0.1 --port 8000
  ```
- Verify the health endpoint: open http://127.0.0.1:8000/api/v1/health in a browser — should return `{"status":"ok","version":"1.0.0",...}`.

### Python or dependencies missing
- Install Python 3.10+.
- Install backend dependencies: `pip install -r backend/requirements.txt`.

### Scanner failure
- The scanner skips `.git`, `venv`, `node_modules`, `__pycache__`, etc.
- It scans Python, TypeScript, YAML, JSON, CSV, and other file types.
- If a single file causes an error, the scanner logs it and continues.

### Ollama unavailable
- Ensure Ollama is installed and running: `ollama serve`.
- Check URL in Settings (default `http://localhost:11434`).

### API key missing / invalid
- Open the **Settings** view, select the provider, enter the API key, and click **Save Configuration**.
- Click **Test Connection** to verify the key works.

### No workspace open
- The "Analyze Project" command requires an open workspace folder.
- Open a folder first (File → Open Folder) then run the command.

## Architecture

- **VS Code Extension** (TypeScript) — provides the Activity Bar icon, sidebar views, and commands.
- **Python Backend** (FastAPI) — provides analysis, chat, and report APIs.
- **SQLite storage** with repository abstraction.
- **AI provider abstraction** (Ollama, OpenAI, Anthropic, Gemini, DeepSeek, Cohere, OpenRouter, OpenAI-compatible).

## Development

```bash
cd extension
npm install
npm run compile
npm test
npm run package
```

## License

MIT
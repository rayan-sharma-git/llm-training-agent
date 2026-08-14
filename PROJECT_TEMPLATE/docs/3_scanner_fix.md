# 3 — Scanner / Analyze Project Fix Report

**Status**: Complete
**Date**: 2026-08-14

---

## 1. What it was before, and how it worked

### Analyze Project flow (as originally designed)

```
VS Code command: "LLM Training Agent: Analyze Project"
        ↓
extension/src/commands/analyzerCommands.ts
        ↓ registerAnalyzerCommands → llmTrainingAgent.analyzeProject
extension/src/services/apiClient.ts  → apiClient.analyzeProject(projectPath)
        ↓ POST /api/v1/project/analyze   { projectPath }
Python backend (FastAPI)  backend/main.py → api/routes.py
        ↓ analyze_project()
backend/scanner/scanner.py  → ProjectScanner(project_path).scan()
        ↓ discovers files + framework + model
backend/scanner/context_builder.py → builds ProjectContext
backend/analyzers/* → dataset / prompt / hyperparameter / model / cost
backend/prediction + recommendation + reports
        ↓
HTTP response { project, report } → extension → Overview/Reports views
```

### Was `backend/scanner/scanner.py` actually executing?

**Before** this fix, when the **backend was started manually**, `scanner.py` **was** executing correctly. I proved this two ways:

1. **Direct integration test** (Python) — `POST /api/v1/project/analyze` with the extension path returned HTTP 200 with `project` + `report`.
2. **Server log evidence** — when I started uvicorn and hit the endpoint, the log showed:
   ```
   api.routes | Starting project analysis: D:/.../extension
   scanner.scanner | Scanning project: D:\Documents\...\extension
   scanner.scanner | Project scan complete
   ```
   so `scanner.py` `scan()` ran, discovered **122 files**, and the pipeline completed.

**However**, from the **VS Code extension's perspective**, the flow often did **not reach** the backend at all. The practical failure ("Analyze Project fails immediately") was caused by **extension-side bugs** that broke the chain **before** `scanner.py` — not by `scanner.py` itself.

---

## 2. Why it was a problem (root causes)

I traced the full call chain and found several defects, in order of impact:

1. **`ApiClient` SecretStorage crash** — `apiClient.ts` used `(vscode as any).__extensionContext` to get SecretStorage, but **nothing ever sets `vscode.__extensionContext`**. Any call to `getApiKey / setApiKey / removeApiKey` (used by the Settings webview and AI-key handling) threw `SecretStorage is not available`. The constructor also did not receive the extension context.

2. **Settings webview had two conflicting `_getModelError` definitions** (one sync at line ~178, one async at line ~685) and a syntax error `onchange="updateProvider(this.value"` (missing `)`). It also referenced a non-existent `ollamaBaseUrl` element. This broke the Settings view and could break activation / command registration.

3. **`SettingsWebviewProvider` had no `reveal()` method**, but `extension.ts` called `settingsProvider.reveal()` for the `configureProvider` command → runtime error when that command runs.

4. **Model select replaced the DOM node** (`select.replaceWith(input)`) which broke subsequent UI re-renders; fixed by using a stable container.

5. **`package.json` provider enum** only listed `["ollama","openai","anthropic"]`, so the other providers (Gemini, DeepSeek, Cohere, OpenRouter, openai_compatible) could not be persisted cleanly through settings.

6. **Weak backend-start diagnostics** — `BackendManager` gave no output channel and its venv detection was limited, making auto-start failures hard to diagnose.

None of these blocked **`scanner.py`** when the backend ran manually, but they **blocked the extension→backend→scanner chain** in practice.

---

## 3. How I fixed it, and what I changed

### Extension fixes (TypeScript)

- **`src/services/apiClient.ts`**
  - Constructor now accepts the `vscode.ExtensionContext` and stores it.
  - `getSecretStorage()` returns `this.context?.secrets` (instead of the never-set `vscode.__extensionContext`).
  - `setApiKey` uses `secretStore.store(...)` (correct VS Code API).
  - Improved Axios error mapping to keep human-friendly messages.

- **`src/extension.ts`**
  - Passes `context` into `new ApiClient(...)` so SecretStorage works.

- **`src/views/settingsWebviewProvider.ts`** (rewritten)
  - Removed the duplicate `_getModelError`.
  - Added a working `reveal()` method.
  - Fixed HTML/JS: valid `onchange`, real `ollamaBaseUrl` element, stable `modelContainer` for the model select/input.
  - Wired provider/model/API-key save, test connection, remove key, refresh models, and secure API-key storage via SecretStorage.

- **`src/commands/analyzerCommands.ts`**
  - Better path existence check before hitting the backend.
  - Checks the backend-start promise result and surfaces a clear "Python backend could not be started" message.
  - Clearer progress messages ("Contacting backend" → "Scanning project").

- **`src/services/backendManager.ts`**
  - Added an **Output Channel** ("LLM Training Agent: Backend") so auto-start logs are visible.
  - Logs stdout/stderr from uvicorn.
  - Improved Python/venv discovery (searches more candidate locations incl. `..\..\..`).
  - Resolves the ready promise when uvicorn reports "running".

- **`package.json`**
  - Expanded the `llmTrainingAgent.provider` enum to all 8 providers.

- Removed stale compiled `.js` files inside `src/` that shadowed the `.ts` sources.

### Backend / documentation

- Re-synced the packaged backend inside `extension/backend` with the source backend (via `build_backend_into_extension.py`) so the `.vsix` ships the current scanner/analyzers/providers.
- Updated `README.md` (repo) and `extension/README.md` with install, GitHub distribution, backend, scanner flow, AI Settings, Ollama, free options, and troubleshooting.

---

## 4. How it works now

```
VS Code starts
   ↓ activation (extension.ts)
   ↓ BackendManager.ensureRunning() auto-starts uvicorn + waits for /api/v1/health
   ↓ Settings view works (provider/model/API key via SecretStorage)
User clicks "Analyze Project"
   ↓ (verifies workspace is open + path exists)
   ↓ ApiClient POST /api/v1/project/analyze  {projectPath}
   ↓ FastAPI route (api/routes.py)
   ↓ ProjectScanner(project_path).scan()   ← backend/scanner/scanner.py
   ↓ context build → analyzers → predictions → recommendations → report
   ↓ HTTP { project, report } → extension → Overview/Reports views
```

### Verification performed

- TypeScript compiles with **0 errors** (`npm run compile`).
- Backend Python test suite: **30/30 passed** (`pytest tests/ -v`), including all scanner tests.
- Started the real backend on `127.0.0.1:8000`:
  - `GET /api/v1/health` → `200 {"status":"ok","version":"1.0.0",...}`
  - `POST /api/v1/project/analyze` → `200`, scanned **122 files**, returned `project` + `report`.
  - Log proved `scanner.scanner | Scanning project` / `Project scan complete`.
- Providers endpoint returns all 8 providers (OpenAI, Anthropic, Gemini, DeepSeek, Cohere, OpenRouter, Ollama, openai_compatible).
- `.vsix` packaged successfully: `llm-training-agent-1.0.0.vsix` (86 files, ~101 KB) including bundled `backend/scanner/scanner.py`.

### Remaining notes

- Ollama itself is not installed/running on this machine, so real LLM calls return graceful `404` messages (`Client error '404 Not Found' for url 'http://localhost:11434/api/chat'`) — the backend logs that and continues, and analysis still succeeds. To enable live AI, install Ollama (`ollama serve`, `ollama pull llama3.2`) or configure a cloud provider key in Settings.
- The extension auto-starts the backend; if a user already runs one manually on port 8000, the auto-start detects it via `/health` and reuses it (no duplicate).
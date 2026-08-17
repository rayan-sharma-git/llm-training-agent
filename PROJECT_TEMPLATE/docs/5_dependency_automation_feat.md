# 5. Dependency Automation Feature

## 1. What Was There Before and How It Worked

Before this change, the extension had a **partial, hardcoded dependency check** that ran at **extension startup** (not when the user clicked "Analyze Project").

### Where it lived

The check lived inside `BackendManager.start()` in:

```
PROJECT_TEMPLATE/extension/src/services/backendManager.ts
```

### How it worked

When the extension activated, `BackendManager.ensureRunning()` was called in the background. Inside `start()`, before spawning the Uvicorn process, it ran a single synchronous Python command:

```ts
execFileSync(
  pythonExe,
  ['-c', 'import fastapi, uvicorn, pydantic, pydantic_settings'],
  { cwd, stdio: 'ignore', timeout: 15000 }
);
```

If that command threw (any of those four packages missing), it:

1. Logged the failure to the "LLM Training Agent: Backend" output channel.
2. Showed a generic VS Code notification:

   ```
   LLM Training Agent: Python backend dependencies are missing.
   Please run "pip install -r requirements.txt" using "<python>".
   ```

3. Cleaned up the process and returned `false` from `start()`.

### What it did NOT do

- It did **not** read `backend/requirements.txt`.
- It only checked **4 hardcoded packages** (`fastapi`, `uvicorn`, `pydantic`, `pydantic_settings`).
- It ran at **startup**, not when the user clicked **Analyze Project**.
- It offered **no Install / Cancel buttons**.
- It did **not** use the extension **chat window**.
- It did **not** provide a copyable manual command in the chat.
- It did **not** re-verify after any action.

---

## 2. Why It Was a Problem

### a) Incomplete coverage

`backend/requirements.txt` lists 16 packages, including:

- `sqlalchemy`
- `aiosqlite`
- `httpx`
- `google-generativeai`
- `cohere`
- `python-dotenv`
- `pytest`, `pytest-asyncio`, `ruff`, `black`, `mypy`

The old check only verified 4 of them. A backend could start with `fastapi`, `uvicorn`, `pydantic`, and `pydantic_settings` installed but still crash at runtime because `sqlalchemy` or `aiosqlite` was missing. The user would only discover the problem after the analysis had already started and failed.

### b) Wrong timing

The check ran at **extension startup**, not when the user clicked **Analyze Project**. This meant:

- The user could click "Analyze Project" and get a confusing runtime error even though the startup check had already passed (because the startup check was too shallow).
- Conversely, if the startup check failed, the user got a warning at startup but could still click "Analyze Project" and hit a broken backend.

### c) No permission-based flow

The old flow **never asked for permission** to install anything. It only showed a passive warning. There was no:

- `[Install Dependencies]` button
- `[Cancel]` button
- Chat-window message
- Manual command shown in the chat

This violated the requirement that the extension must **never install anything without explicit user approval**.

### d) No re-verification

Even if the user manually installed the missing packages, the extension never re-checked. The user had to reload the window or manually restart the backend.

---

## 3. How I Fixed It and What Fixes I Made

I implemented a **permission-based dependency-checking flow** that runs when the user clicks **Analyze Project**.

### New file: `PROJECT_TEMPLATE/extension/src/services/dependencyManager.ts`

This is a new service with three responsibilities:

1. **Parse `requirements.txt`** — `parseRequirements()` reads the file, strips version specifiers, extras (`[standard]`), and environment markers (`; python_version < "3.11"`), and maps pip package names to Python import specs (e.g. `python-dotenv` → `dotenv`, `google-generativeai` → `google.generativeai`).

2. **Check availability** — `checkDependencies()` runs a single Python subprocess that tries to import **all** requirements at once. If that fails, it falls back to checking each requirement individually to report exactly which ones are missing. This is a **read-only** check — it never installs or modifies anything.

3. **Install (permission-gated)** — `installDependencies()` runs `pip install -r requirements.txt` using the resolved Python interpreter. It streams output to a dedicated output channel. **This function is only ever called after the user has explicitly clicked "Install Dependencies".**

### Modified: `PROJECT_TEMPLATE/extension/src/services/backendManager.ts`

Added two public resolvers so the dependency check can reuse the same path-resolution logic as the backend startup:

- `getBackendPath()` — resolves `backend/main.py`.
- `getPythonExecutable()` — resolves the venv/system Python.

### Modified: `PROJECT_TEMPLATE/extension/src/views/chatWebviewProvider.ts`

Added support for **action cards** — interactive chat messages with clickable buttons:

- New `postActionCard()` method that posts a message with buttons and returns a promise resolving to the clicked action.
- New `showActionCard` webview message handler.
- New `actionButtonClicked` message handler that resolves the pending promise.
- New CSS for `.action-card`, `.card-buttons`, `.primary-btn`, `.secondary-btn`.

### Modified: `PROJECT_TEMPLATE/extension/src/commands/analyzerCommands.ts`

The "Analyze Project" command now:

1. **Checks dependencies first** (read-only) using `checkDependencies()`.
2. If dependencies are **available** → continues normally with the analysis.
3. If dependencies are **missing** → **STOPS** the analysis and asks for permission:
   - **Preferred**: posts an action card in the chat window with `[Install Dependencies]` and `[Cancel]` buttons, plus the manual command.
   - **Fallback**: if the chat view is not available, shows a modal VS Code dialog with the same options.
4. If the user clicks **Install Dependencies**:
   - Runs `installDependencies()` (the only place installation happens).
   - **Re-verifies** with `checkDependencies()`.
   - If still missing → shows an error and stops.
   - If now available → posts a success message and continues with the analysis.
5. If the user clicks **Cancel** (or dismisses):
   - Does **nothing** — no install, no download, no analysis.
   - Posts a clear message in the chat: *"Analyze Project was cancelled because the required backend dependencies are missing."* plus the manual command.
   - Shows a warning notification.

### Modified: `PROJECT_TEMPLATE/extension/src/extension.ts`

Passed the `backendManager` instance to `registerAnalyzerCommands()` so the command can resolve the backend path and Python executable.

### New test: `PROJECT_TEMPLATE/extension/tests/suite/dependencyManager.test.ts`

Added 9 unit tests covering:

- `parseRequirements()` — version stripping, extras, comments, environment markers, pip→import mapping.
- `buildManualCommand()` — quoting of paths and bare `python`.
- `checkDependencies()` — missing requirements file, all imports succeed, missing packages reported.

---

## 4. How It Works Now

### Flow diagram

```
User clicks "Analyze Project"
        ↓
Check dependencies (read-only, from backend/requirements.txt)
        ↓
Are they available?
       / \
     YES  NO
      ↓    ↓
 Continue  STOP
           ↓
      Explain problem in chat window
           ↓
      Ask permission
        /       \
     Approve    Cancel
       ↓          ↓
    Install      Do nothing
       ↓
   Verify again
       ↓
   Continue analysis
```

### Detailed behavior

1. **Check (always allowed, never modifies anything)**
   - The extension resolves the backend path and Python executable.
   - It reads `backend/requirements.txt` and tries to import every listed package.
   - This is a pure read-only operation.

2. **If all dependencies are available**
   - The analysis proceeds exactly as before — no interruption, no message.

3. **If dependencies are missing**
   - The analysis **stops immediately**.
   - The chat window shows a message like:

     ```
     ⚠️ Required backend dependencies are missing.

     Missing: sqlalchemy, aiosqlite

     Analyze Project cannot start until they are installed.

     Would you like me to install the required dependencies?

     Manual command:
     "C:\...\python.exe" -m pip install -r "C:\...\backend\requirements.txt"
     ```

   - Two buttons appear: **[Install Dependencies]** and **[Cancel]**.

4. **If the user clicks "Install Dependencies"**
   - The extension runs `pip install -r backend/requirements.txt` using the resolved Python interpreter.
   - Output streams to the "LLM Training Agent: Dependencies" output channel.
   - After installation, the extension **re-checks** the dependencies.
   - If still missing → error message, analysis stops.
   - If now available → success message, analysis continues.

5. **If the user clicks "Cancel"**
   - **Nothing is installed, downloaded, or modified.**
   - The chat shows: *"Analyze Project was cancelled because the required backend dependencies are missing."* plus the manual command.
   - A warning notification is shown.
   - The analysis does **not** start.

### Key guarantees

- **Checking is always allowed** — it never modifies the environment.
- **Installing requires explicit user permission** — the only code path that runs `pip install` is inside the `choice === 'install'` branch, which is only reached after the user clicks "Install Dependencies".
- **No silent actions** — the extension never downloads, installs, or fixes anything on its own.
- **Manual command always shown** — the user can always install manually if they prefer.
- **Re-verification after install** — the extension confirms the install actually worked before continuing.

### Files changed

| File | Change |
|------|--------|
| `PROJECT_TEMPLATE/extension/src/services/dependencyManager.ts` | **New** — parse/check/install logic |
| `PROJECT_TEMPLATE/extension/src/services/backendManager.ts` | Added `getBackendPath()` and `getPythonExecutable()` |
| `PROJECT_TEMPLATE/extension/src/views/chatWebviewProvider.ts` | Added action-card support |
| `PROJECT_TEMPLATE/extension/src/commands/analyzerCommands.ts` | Added dependency-check + permission flow |
| `PROJECT_TEMPLATE/extension/src/extension.ts` | Pass `backendManager` to analyzer commands |
| `PROJECT_TEMPLATE/extension/tests/suite/dependencyManager.test.ts` | **New** — 9 unit tests |

### Verification

- `npx tsc --noEmit -p ./` → **exit code 0** (no TypeScript errors).
- `npx vitest run` → **23 tests passed** (4 test files), including the 9 new dependency-manager tests.
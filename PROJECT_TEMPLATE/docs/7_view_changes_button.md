# View Changes Button

Feature: review the agent's proposed file modifications before accepting them (conceptually similar to Cline's "View Changes").

Status: Complete (implemented in this change set)

---

## 1. What was it before and how it worked

**The feature did not exist.** Inspection of the codebase showed:

- `backend/editing/file_editor.py` contained only a `FileEditor` with in-memory
  `propose_changes` / `apply_changes` / `rollback` methods that **were never wired to
  any API route or UI** — the module was dead code.
- `backend/editing/editor.py` had a second `FileEditor` (also unused) that could
  generate a unified diff string, but nothing ever surfaced that diff to the user.
- The extension (`extension/src/`) had no diff viewer, no "View Changes" command, no
  pending-change list, and no apply/discard/rollback flow. Searching all
  source files for `diff`, `propos`, `rollback`, `apply`, `View Changes` found no
  user-facing surface.
- When the agent modified a file, the change was applied silently. The user had no
  way to preview what would change before it happened.

**How the project handled file changes before:** it did not, in any user-visible way.
There was no proposal step, no approval gate, no diff display, and no rollback path.

## 2. Why it was a problem

- **No review gate.** A Cline-style agent must let the user inspect changes *before*
  they are applied. Without it, any backend modification to a file was immediate and
  irreversible.
- **Dead code risk.** Two untested `FileEditor` classes existed but were unreachable —
  misleading for maintainers and untestable against real behavior.
- **No recovery.** If a modification was wrong, there was no backup/rollback mechanism
  reachable from the UI.
- **Trust.** Users cannot adopt an agent that silently rewrites their files.

## 3. How it was fixed — changes made

The feature was integrated into the existing architecture (FastAPI backend +
VS Code extension) rather than redesigning anything.

### Backend

- `backend/editing/file_editor.py` — replaced the unused in-memory class with
  `PendingChangeStore`, which persists each proposal as JSON under
  `<project>/.llm_training_agent/pending_changes/<changeId>.json` (proposals survive
  backend restarts), tracks status (`pending → applied → rolled_back/rejected`),
  and resolves project files safely (path-traversal rejection via `editing/__init__.py::resolve_project_file`).
- `backend/api/routes.py` — new `/api/v1/files/*` endpoints:
  - `POST /files/propose` — stores original + proposed content and a unified diff
    **without touching the file**; returns `changeId` + diff.
  - `GET  /files/changes` — list pending proposals (metadata only).
  - `GET  /files/changes/{id}` — full proposal incl. original/proposed contents.
  - `POST /files/changes/{id}/apply` — backs up the current file to
    `.llm_training_agent_backups/`, then writes the proposed content.
  - `POST /files/changes/{id}/discard` — rejects the proposal; file untouched.
  - `POST /files/changes/{id}/rollback` — restores the file from the backup.
- `backend/editing/editor.py` and the old dead class were removed.
- New tests: `backend/tests/test_file_changes.py` (propose → list → get → apply →
  rollback, discard, 404/409 error paths).

### Extension (VS Code)

- `extension/src/commands/changeCommands.ts` — registers
  `llmTrainingAgent.viewChanges` ("View Changes"):
  1. Lists pending changes in a QuickPick (file path, status, timestamp).
  2. Fetches the selected proposal and opens it in **VS Code's native diff editor**
     (`vscode.diff`) via a `TextDocumentContentProvider` on the
     `llm-training-agent-changes:` virtual scheme — left side: original, right side:
     proposed.
  3. Shows **Apply / Discard / Rollback** actions after inspection.
- `extension/src/services/apiClient.ts` — added the six API client methods
  (`proposeFileChange`, `listFileChanges`, `getFileChange`, `applyFileChange`,
  `discardFileChange`, `rollbackFileChange`).
- `extension/package.json` — command + keybinding contribution.
- `extension/src/extension.ts` — wired `registerChangeCommands`.

No unrelated parts were redesigned; existing analyzer/chat/cleaning flows are untouched.

## 4. How it works now

```
Agent (or any backend flow) proposes a change
        ↓
POST /api/v1/files/propose  → changeId + unified diff stored on disk
        ↓
User clicks "View Changes" (Command Palette / UI button)
        ↓
GET /files/changes → QuickPick of pending proposals
        ↓
User selects one → GET /files/changes/{id}
        ↓
VS Code native diff editor: ORIGINAL vs PROPOSED (read-only, side by side)
        ↓
Apply            → backup made, file updated   (rollback possible)
Discard          → file untouched, proposal removed
Rollback         → file restored from backup
```

- **Before accepting:** the user always sees an exact line-level diff of what the
  agent proposes, in VS Code's built-in diff viewer.
- **Safety:** proposals never modify files; apply creates a backup first; rollback
  restores it; discard deletes the proposal; path traversal is rejected.
- **Persistence:** pending proposals are stored on disk in the project, so they
  survive backend restarts and can be reviewed later.

## Verification

- Backend: `python -m pytest tests/ -q` → **79 passed** (incl. 6 new file-change tests).
- Extension: `npx tsc --noEmit` → clean; `npx vitest run` → **23 passed**.
- Bundled backend re-synced into `extension/backend` for packaging.

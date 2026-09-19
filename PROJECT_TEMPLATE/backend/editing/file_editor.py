"""Manage pending (proposed but not yet applied) file changes with disk persistence."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from editing import resolve_project_file

logger = logging.getLogger(__name__)


class PendingChangeStore:
    """Persist proposed changes so a pending proposal survives backend restarts."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self._store_dir = self.project_root / ".llm_training_agent" / "pending_changes"
        self._memory: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _change_file(self, change_id: str) -> Path:
        return self._store_dir / f"{change_id}.json"

    def _load_from_disk(self, change_id: str) -> Optional[Dict[str, Any]]:
        path = self._change_file(change_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._memory[change_id] = data
            return data
        except Exception as exc:  # pragma: no cover - corrupt file guard
            logger.warning(f"Could not read pending change {change_id}: {exc}")
            return None

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def save(self, file_path: str, original_content: str, proposed_content: str, diff: str) -> Dict[str, Any]:
        """Persist a new pending change and return its metadata (incl. contents)."""
        self._store_dir.mkdir(parents=True, exist_ok=True)
        change_id = str(uuid.uuid4())
        record = {
            "changeId": change_id,
            "filePath": file_path,
            "originalContent": original_content,
            "proposedContent": proposed_content,
            "diff": diff,
            "status": "pending",
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        self._change_file(change_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
        self._memory[change_id] = record
        return record

    def get(self, change_id: str) -> Optional[Dict[str, Any]]:
        """Return a pending change by id (memory first, then disk)."""
        if change_id in self._memory:
            return self._memory[change_id]
        return self._load_from_disk(change_id)

    def list(self) -> List[Dict[str, Any]]:
        """List pending-change metadata (no file contents)."""
        if self._store_dir.exists():
            for path in sorted(self._store_dir.glob("*.json")):
                change_id = path.stem
                if change_id in self._memory:
                    continue
                self._load_from_disk(change_id)
        return [
            {k: v for k, v in record.items() if k not in ("originalContent", "proposedContent")}
            for record in self._memory.values()
        ]
    def set_status(self, change_id: str, status: str, backup_path: Optional[str] = None) -> None:
        """Update the persisted status of a change (pending → applied → rolled_back/rejected)."""
        record = self.get(change_id)
        if not record:
            return
        record["status"] = status
        if backup_path is not None:
            record["backupPath"] = backup_path
        self._memory[change_id] = record
        try:
            self._change_file(change_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
        except Exception as exc:  # pragma: no cover - best effort persistence
            logger.warning(f"Could not persist status for change {change_id}: {exc}")

    def remove(self, change_id: str) -> None:
        """Discard a pending change (after apply or explicit discard)."""
        self._memory.pop(change_id, None)
        try:
            self._change_file(change_id).unlink(missing_ok=True)
        except Exception as exc:  # pragma: no cover - best effort cleanup
            logger.warning(f"Could not delete pending change {change_id}: {exc}")

    def project_file(self, file_path: str) -> Path:
        """Resolve *file_path* inside the project, rejecting path traversal."""
        return resolve_project_file(self.project_root, file_path)

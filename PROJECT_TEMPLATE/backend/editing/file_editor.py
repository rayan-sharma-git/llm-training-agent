"""Safe file editing with change proposals and rollback."""
from __future__ import annotations

import difflib
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class FileEditor:
    """Manages safe file modifications."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self._backup_dir = self.project_root / ".llm_training_agent_backups"
        self._applied_changes: Dict[str, str] = {}  # change_id -> file_path
    
    async def propose_changes(self, file_path: str, new_content: str) -> Dict[str, Any]:
        """Propose file changes without applying them."""
        target_path = self.project_root / file_path
        
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        original_content = target_path.read_text(encoding="utf-8")
        diff = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
        )
        
        return {
            "changeId": str(uuid.uuid4()),
            "filePath": file_path,
            "originalContent": original_content,
            "proposedContent": new_content,
            "diff": "".join(diff),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def apply_changes(self, change_id: str, file_path: str, new_content: str) -> Dict[str, Any]:
        """Apply approved changes with rollback support."""
        target_path = self.project_root / file_path
        
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create backup
        self._backup_dir.mkdir(exist_ok=True)
        backup_path = self._backup_dir / f"{Path(file_path).name}.{change_id}.bak"
        backup_path.write_text(target_path.read_text(encoding="utf-8"))
        
        # Apply changes
        target_path.write_text(new_content, encoding="utf-8")
        self._applied_changes[change_id] = str(backup_path)
        
        return {
            "changeId": change_id,
            "status": "applied",
            "backupPath": str(backup_path),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def rollback(self, change_id: str) -> Dict[str, Any]:
        """Rollback a previously applied change."""
        if change_id not in self._applied_changes:
            raise ValueError(f"Change not found: {change_id}")
        
        backup_path = Path(self._applied_changes[change_id])
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Determine target file path
        original_name = backup_path.name.split(".")[0]
        target_path = self.project_root / original_name
        
        # Restore from backup
        target_path.write_text(backup_path.read_text(encoding="utf-8"))
        
        # Cleanup
        backup_path.unlink()
        del self._applied_changes[change_id]
        
        return {
            "changeId": change_id,
            "status": "rolled_back",
            "filePath": str(target_path),
            "timestamp": datetime.utcnow().isoformat(),
        }
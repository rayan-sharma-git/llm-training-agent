"""Safe file editing with diff generation and rollback."""
from __future__ import annotations

import difflib
import logging
from typing import Optional

from core.errors import ModificationError

logger = logging.getLogger(__name__)


class FileEditor:
    """Safe file editing with approval workflow."""

    def generate_diff(self, original: str, proposed: str, filepath: str) -> str:
        """Generate unified diff between original and proposed content."""
        original_lines = original.splitlines(keepends=True)
        proposed_lines = proposed.splitlines(keepends=True)
        diff = difflib.unified_diff(original_lines, proposed_lines, fromfile=filepath, tofile=filepath)
        return "".join(diff)

    def apply_changes(self, filepath: str, proposed_content: str) -> None:
        """Apply changes to file (this would be called after user approval)."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(proposed_content)
        except Exception as e:
            raise ModificationError(f"Failed to apply changes: {e}", filepath)

    def create_rollback_point(self, original_content: str) -> str:
        """Create rollback data (in production this would be persisted)."""
        return original_content
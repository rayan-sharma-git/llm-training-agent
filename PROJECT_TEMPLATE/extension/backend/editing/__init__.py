"""Utilities shared by the propose → view → apply → rollback file-change workflow."""
from __future__ import annotations

from pathlib import Path


def resolve_project_file(project_root: Path, file_path: str) -> Path:
    """Resolve a workspace-relative file path safely inside *project_root*."""
    candidate = (project_root / file_path).resolve()
    root = project_root.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"filePath escapes the project directory: {file_path}")
    return candidate

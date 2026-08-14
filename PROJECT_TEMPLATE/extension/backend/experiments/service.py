"""Experiment tracking service."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from models.schemas import ProjectContext
from storage.repositories import Repository, Experiment
from storage.database import get_session


class ExperimentService:
    """Tracks training experiments."""
    
    async def save_experiment(self, context: ProjectContext, metrics: Dict[str, Any], notes: Optional[str] = None) -> Dict[str, Any]:
        """Save experiment record."""
        logging.info("Saving experiment")
        
        experiment_id = str(uuid.uuid4())
        async with get_session() as session:
            repo = Repository(session, Experiment)
            record = {
                "id": experiment_id,
                "project_name": context.project_name,
                "dataset_version": context.dataset_paths[0] if context.dataset_paths else "unknown",
                "model": context.base_model or "unknown",
                "tokenizer": context.tokenizer or "unknown",
                "hyperparameters": str(context.project_statistics),
                "metrics": str(metrics),
                "timestamp": datetime.utcnow(),
                "notes": notes,
            }
            return await repo.create(record)
    
    async def list_experiments(self, project_name: str) -> List[Dict[str, Any]]:
        """List experiments for a project."""
        logging.info(f"Listing experiments for {project_name}")
        # Stub implementation
        return []
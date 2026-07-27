"""Experiment tracking service."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from models.schemas import Experiment

logger = logging.getLogger(__name__)


class ExperimentService:
    """Manages experiment tracking."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.experiments: List[Experiment] = []

    async def create_experiment(self, experiment: Experiment) -> Experiment:
        """Create a new experiment."""
        experiment.tags = experiment.tags or []
        experiment.artifacts = experiment.artifacts or []
        self.experiments.append(experiment)
        return experiment

    async def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments for this project."""
        return [exp.model_dump() for exp in self.experiments]

    async def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific experiment."""
        for exp in self.experiments:
            if exp.experiment_id == experiment_id:
                return exp.model_dump()
        return None

    async def delete_experiment(self, experiment_id: str) -> bool:
        """Delete an experiment."""
        self.experiments = [exp for exp in self.experiments if exp.experiment_id != experiment_id]
        return True

    async def compare_experiments(self, experiment_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple experiments."""
        comparison = {"experiments": [], "best_metrics": {}, "differences": []}
        for exp in self.experiments:
            if exp.experiment_id in experiment_ids:
                comparison["experiments"].append(exp.model_dump())
        return comparison
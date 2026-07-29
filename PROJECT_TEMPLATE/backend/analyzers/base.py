"""Abstract analyzer interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from models.schemas import ProjectContext


class Analyzer(ABC):
    """Base analyzer interface."""

    @abstractmethod
    async def analyze(self, context: ProjectContext, **kwargs) -> Dict[str, Any]:
        """Run analysis and return result."""
        pass
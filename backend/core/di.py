"""Simple dependency injection container."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type


class Container:
    """Lightweight dependency container."""

    def __init__(self) -> None:
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] {}

    def register(self, key: str, factory: Callable, singleton: bool = True) -> None:
        """Register a service."""
        self._factories[key] = factory
        if singleton:
            self._services[key] = factory()

    def get(self, key: str) -> Any:
        """Resolve a service."""
        if key not in self._services:
            if key not in self._factories:
                raise KeyError(f"Service not registered: {key}")
            self._services[key] = self._factories[key]()
        return self._services[key]

    def reset(self) -> None:
        """Clear all services (useful for tests)."""
        self._services.clear()


# Global container instance
container = Container()
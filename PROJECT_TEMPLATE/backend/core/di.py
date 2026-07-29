"""Dependency injection container."""
from __future__ import annotations

from typing import Any, Dict, Type

from core.config import get_settings


class Container:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, name: str, factory: Type[Any], singleton: bool = True) -> None:
        """Register a service."""
        if singleton:
            self._singletons[name] = factory
        else:
            self._services[name] = factory
    
    def get(self, name: str) -> Any:
        """Get a service instance."""
        if name in self._singletons:
            if name not in self._instances:
                self._instances[name] = self._singletons[name]()
            return self._instances[name]
        elif name in self._services:
            return self._services[name]()
        raise KeyError(f"Service '{name}' not registered")


container = Container()
container._instances: Dict[str, Any] = {}


def get_container() -> Container:
    """Get the global container instance."""
    return container
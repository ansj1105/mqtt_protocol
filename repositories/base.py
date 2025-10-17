"""
Base repository with common database operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository pattern implementation.
    For MVP, uses in-memory storage. Can be extended to use Redis, PostgreSQL, etc.
    """
    
    def __init__(self):
        self._storage: Dict[str, T] = {}
    
    def create(self, id: str, entity: T) -> T:
        """Create a new entity."""
        self._storage[id] = entity
        return entity
    
    def get(self, id: str) -> Optional[T]:
        """Get entity by ID."""
        return self._storage.get(id)
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        return list(self._storage.values())
    
    def update(self, id: str, entity: T) -> Optional[T]:
        """Update an entity."""
        if id in self._storage:
            self._storage[id] = entity
            return entity
        return None
    
    def delete(self, id: str) -> bool:
        """Delete an entity."""
        if id in self._storage:
            del self._storage[id]
            return True
        return False
    
    def exists(self, id: str) -> bool:
        """Check if entity exists."""
        return id in self._storage
    
    def count(self) -> int:
        """Count total entities."""
        return len(self._storage)
    
    def clear(self):
        """Clear all entities."""
        self._storage.clear()
    
    def find_by(self, **kwargs) -> List[T]:
        """
        Find entities by attributes.
        Simple implementation for MVP.
        """
        results = []
        for entity in self._storage.values():
            match = True
            for key, value in kwargs.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    break
            if match:
                results.append(entity)
        return results


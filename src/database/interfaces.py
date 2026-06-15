"""Abstract interfaces for database implementations."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class DatabaseInterface(ABC):
    """Abstract interface for all database implementations."""
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        """Create a new table."""
        pass
    
    @abstractmethod
    def insert(self, table_name: str, **kwargs) -> Dict[str, Any]:
        """Insert a new record."""
        pass
    
    @abstractmethod
    def get_by_id(self, table_name: str, record_id: int) -> Dict[str, Any]:
        """Get record by ID."""
        pass
    
    @abstractmethod
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all records."""
        pass
    
    @abstractmethod
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter records."""
        pass
    
    @abstractmethod
    def update(self, table_name: str, record_id: int, **updates) -> Dict[str, Any]:
        """Update a record."""
        pass
    
    @abstractmethod
    def delete(self, table_name: str, record_id: int) -> None:
        """Delete a record."""
        pass
    
    @abstractmethod
    def list_tables(self) -> List[str]:
        """List all tables."""
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str) -> None:
        """Drop a table."""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        pass
    
    @abstractmethod
    def sort(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort records by field."""
        pass
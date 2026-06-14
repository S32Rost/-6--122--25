"""Custom exceptions for database."""

class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a record is not found."""
    pass


class ValidationError(DatabaseError):
    """Raised when data validation fails."""
    pass
"""Predefined table schemas."""

SCHEMAS = {
    "students": {
        "name": str,
        "age": int,
        "major": str,
        "email": str
    },
    "books": {
        "title": str,
        "author": str,
        "year": int,
        "isbn": str
    },
    "employees": {
        "full_name": str,
        "position": str,
        "salary": float,
        "department": str
    }
}
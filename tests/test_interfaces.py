"""Tests for database interfaces."""

import unittest
from abc import ABC
from src.database.interfaces import DatabaseInterface


class TestInterfaces(unittest.TestCase):
    """Test that DatabaseInterface is abstract."""
    
    def test_interface_is_abstract(self):
        """DatabaseInterface should be an abstract class."""
        self.assertTrue(issubclass(DatabaseInterface, ABC))
    
    def test_interface_has_abstract_methods(self):
        """DatabaseInterface should have abstract methods."""
        abstract_methods = [
            'create_table', 'insert', 'get_by_id', 'get_all',
            'filter', 'update', 'delete', 'list_tables', 
            'drop_table', 'table_exists', 'sort'
        ]
        
        for method in abstract_methods:
            self.assertTrue(
                hasattr(DatabaseInterface, method),
                f"Method {method} not found"
            )


if __name__ == "__main__":
    unittest.main()
"""Tests for in-memory database."""

import unittest
from src.database.in_memory import InMemoryDatabase
from src.database.schemas import SCHEMAS
from src.database.errors import RecordNotFoundError, ValidationError, DatabaseError


class TestInMemoryDatabase(unittest.TestCase):
    """Test InMemoryDatabase class."""
    
    def setUp(self):
        self.db = InMemoryDatabase("test_db")
        self.db.create_table("students", SCHEMAS["students"])
    
    def test_create_table(self):
        self.assertTrue(self.db.table_exists("students"))
        self.assertIn("students", self.db.list_tables())
    
    def test_create_duplicate_table(self):
        with self.assertRaises(DatabaseError):
            self.db.create_table("students", SCHEMAS["students"])
    
    def test_insert(self):
        record = self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.assertEqual(record["name"], "Тест")
        self.assertEqual(record["age"], 20)
        self.assertEqual(record["id"], 1)
    
    def test_insert_missing_field(self):
        with self.assertRaises(ValidationError):
            self.db.insert("students", name="Тест", age=20)
    
    def test_get_by_id(self):
        self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        record = self.db.get_by_id("students", 1)
        self.assertEqual(record["name"], "Тест")
    
    def test_get_by_id_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.db.get_by_id("students", 999)
    
    def test_get_all(self):
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        records = self.db.get_all("students")
        self.assertEqual(len(records), 2)
    
    def test_update(self):
        self.db.insert("students", name="Старый", age=20, major="Тест", email="test@test.com")
        updated = self.db.update("students", 1, name="Новый", age=21)
        self.assertEqual(updated["name"], "Новый")
        self.assertEqual(updated["age"], 21)
    
    def test_update_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.db.update("students", 999, name="Новый")
    
    def test_delete(self):
        self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.db.delete("students", 1)
        with self.assertRaises(RecordNotFoundError):
            self.db.get_by_id("students", 1)
    
    def test_delete_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.db.delete("students", 999)
    
    def test_filter_eq(self):
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        results = self.db.filter("students", {"name": "Иван"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Иван")
    
    def test_filter_gt(self):
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        results = self.db.filter("students", {"age__gt": 22})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Петр")
    
    def test_filter_lt(self):
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        results = self.db.filter("students", {"age__lt": 22})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Иван")
    
    def test_filter_contains(self):
        self.db.insert("students", name="Иван Петров", age=20, major="Информатика", email="i@i.com")
        results = self.db.filter("students", {"name__contains": "Петр"})
        self.assertEqual(len(results), 1)
    
    def test_sort_ascending(self):
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Анна", age=22, major="Физика", email="a@a.com")
        self.db.insert("students", name="Борис", age=21, major="Мат", email="b@b.com")
        
        results = self.db.sort("students", "name", reverse=False)
        names = [r["name"] for r in results]
        self.assertEqual(names, ["Анна", "Борис", "Иван"])
    
    def test_sort_descending(self):
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Анна", age=22, major="Физика", email="a@a.com")
        self.db.insert("students", name="Борис", age=21, major="Мат", email="b@b.com")
        
        results = self.db.sort("students", "name", reverse=True)
        names = [r["name"] for r in results]
        self.assertEqual(names, ["Иван", "Борис", "Анна"])
    
    def test_drop_table(self):
        self.assertTrue(self.db.table_exists("students"))
        self.db.drop_table("students")
        self.assertFalse(self.db.table_exists("students"))

    def test_update_with_unknown_field(self):
        """Test update with unknown field should raise error."""
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="ivan@test.com")
        with self.assertRaises(ValidationError):
            self.db.update("students", 1, unknown_field="some_value")
if __name__ == "__main__":
    unittest.main()
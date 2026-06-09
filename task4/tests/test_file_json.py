import unittest
import os
import tempfile
import json
from database import FileDatabaseJSON, SCHEMAS
from errors import RecordNotFoundError, ValidationError, DatabaseError


class TestFileDatabaseJSON(unittest.TestCase):
    def setUp(self):
        """Создание временного файла для тестов."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()
        self.db = FileDatabaseJSON(self.temp_file.name)
    
    def tearDown(self):
        """Удаление временного файла после тестов."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_create_table(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.assertTrue(self.db.table_exists("students"))
        self.assertIn("students", self.db.list_tables())
    
    def test_insert_and_get(self):
        self.db.create_table("students", SCHEMAS["students"])
        record = self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.assertEqual(record["name"], "Тест")
        
        # Проверка сохранения в файл
        self.db2 = FileDatabaseJSON(self.temp_file.name)
        self.assertTrue(self.db2.table_exists("students"))
        loaded = self.db2.get_by_id("students", 1)
        self.assertEqual(loaded["name"], "Тест")
    
    def test_update(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.db.insert("students", name="Старое", age=20, major="Тест", email="test@test.com")
        updated = self.db.update("students", 1, name="Новое", age=21)
        self.assertEqual(updated["name"], "Новое")
        self.assertEqual(updated["age"], 21)
    
    def test_delete(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.db.delete("students", 1)
        with self.assertRaises(RecordNotFoundError):
            self.db.get_by_id("students", 1)
    
    def test_filter(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        
        results = self.db.filter("students", {"age__gt": 22})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Петр")
    
    def test_sort(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        self.db.insert("students", name="Анна", age=22, major="Мат", email="a@a.com")
        
        results = self.db.sort("students", "name", reverse=False)
        names = [r["name"] for r in results]
        self.assertEqual(names, ["Анна", "Иван", "Петр"])
    
    def test_drop_table(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.assertTrue(self.db.table_exists("students"))
        self.db.drop_table("students")
        self.assertFalse(self.db.table_exists("students"))


if __name__ == "__main__":
    unittest.main()
import unittest
import os
import tempfile
import shutil
from database import FileDatabaseCSV, SCHEMAS
from errors import RecordNotFoundError, ValidationError, DatabaseError


class TestFileDatabaseCSV(unittest.TestCase):
    def setUp(self):
        """Создание временной директории для тестов."""
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabaseCSV(self.temp_dir)
    
    def tearDown(self):
        """Удаление временной директории."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_table(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.assertTrue(self.db.table_exists("students"))
        self.assertIn("students", self.db.list_tables())
        
        # Проверка создания файлов
        csv_path = os.path.join(self.temp_dir, "students.csv")
        schema_path = os.path.join(self.temp_dir, "students_schema.json")
        self.assertTrue(os.path.exists(csv_path))
        self.assertTrue(os.path.exists(schema_path))
    
    def test_insert_and_get(self):
        self.db.create_table("students", SCHEMAS["students"])
        record = self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.assertEqual(record["name"], "Тест")
        
        # Проверка сохранения
        self.db2 = FileDatabaseCSV(self.temp_dir)
        loaded = self.db2.get_by_id("students", 1)
        self.assertEqual(loaded["name"], "Тест")
    
    def test_update(self):
        self.db.create_table("students", SCHEMAS["students"])
        self.db.insert("students", name="Старое", age=20, major="Тест", email="test@test.com")
        updated = self.db.update("students", 1, name="Новое", age=21)
        self.assertEqual(updated["name"], "Новое")
    
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
    
    def test_persistence_between_instances(self):
        """Проверка сохранения данных между разными экземплярами БД."""
        self.db.create_table("students", SCHEMAS["students"])
        self.db.insert("students", name="Сохраненный", age=20, major="Тест", email="test@test.com")
        
        # Новый экземпляр БД
        new_db = FileDatabaseCSV(self.temp_dir)
        self.assertTrue(new_db.table_exists("students"))
        records = new_db.get_all("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Сохраненный")


if __name__ == "__main__":
    unittest.main()
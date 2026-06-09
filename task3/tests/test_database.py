# Добавьте эти тесты в конец класса TestTable

class TestTableSort(unittest.TestCase):
    def setUp(self):
        self.schema = {"name": str, "age": int, "score": float}
        self.table = Table("test", self.schema)
        self.table.insert(name="Charlie", age=30, score=85.5)
        self.table.insert(name="Alice", age=25, score=95.0)
        self.table.insert(name="Bob", age=35, score=75.0)
        self.table.insert(name="David", age=20, score=88.5)
    
    def test_sort_by_age_ascending(self):
        """Сортировка по возрасту по возрастанию."""
        results = self.table.sort("age", reverse=False)
        ages = [r["age"] for r in results]
        self.assertEqual(ages, [20, 25, 30, 35])
    
    def test_sort_by_age_descending(self):
        """Сортировка по возрасту по убыванию."""
        results = self.table.sort("age", reverse=True)
        ages = [r["age"] for r in results]
        self.assertEqual(ages, [35, 30, 25, 20])
    
    def test_sort_by_name_ascending(self):
        """Сортировка по имени по возрастанию (A-Z)."""
        results = self.table.sort("name", reverse=False)
        names = [r["name"] for r in results]
        self.assertEqual(names, ["Alice", "Bob", "Charlie", "David"])
    
    def test_sort_by_name_descending(self):
        """Сортировка по имени по убыванию (Z-A)."""
        results = self.table.sort("name", reverse=True)
        names = [r["name"] for r in results]
        self.assertEqual(names, ["David", "Charlie", "Bob", "Alice"])
    
    def test_sort_by_score_ascending(self):
        """Сортировка по баллам по возрастанию."""
        results = self.table.sort("score", reverse=False)
        scores = [r["score"] for r in results]
        self.assertEqual(scores, [75.0, 85.5, 88.5, 95.0])
    
    def test_sort_by_score_descending(self):
        """Сортировка по баллам по убыванию."""
        results = self.table.sort("score", reverse=True)
        scores = [r["score"] for r in results]
        self.assertEqual(scores, [95.0, 88.5, 85.5, 75.0])
    
    def test_sort_invalid_field(self):
        """Сортировка по несуществующему полю."""
        with self.assertRaises(ValidationError):
            self.table.sort("nonexistent_field")
    
    def test_sort_case_insensitive(self):
        """Сортировка строк без учета регистра."""
        table = Table("test", {"name": str})
        table.insert(name="Zebra")
        table.insert(name="apple")
        table.insert(name="Banana")
        table.insert(name="cherry")
        
        results = table.sort("name", reverse=False)
        names = [r["name"] for r in results]
        # Должно быть case-insensitive: apple, Banana, cherry, Zebra
        self.assertEqual(names, ["apple", "Banana", "cherry", "Zebra"])
    
    def test_get_all_sorted(self):
        """Метод get_all_sorted должен работать корректно."""
        results = self.table.get_all_sorted("age", reverse=False)
        ages = [r["age"] for r in results]
        self.assertEqual(ages, [20, 25, 30, 35])
    
    def test_sort_empty_table(self):
        """Сортировка пустой таблицы."""
        empty_table = Table("empty", {"name": str})
        results = empty_table.sort("name")
        self.assertEqual(results, [])
    
    def test_sort_with_none_values(self):
        """Сортировка с None значениями (None должны быть в конце)."""
        table = Table("test", {"name": str, "age": int})
        table.insert(name="Alice", age=25)
        table.insert(name="Bob", age=None)  # None значение
        table.insert(name="Charlie", age=30)
        
        results = table.sort("age", reverse=False)
        # None должен быть в конце
        ages = [r["age"] for r in results]
        self.assertEqual(ages, [25, 30, None])
        
        results_desc = table.sort("age", reverse=True)
        ages_desc = [r["age"] for r in results_desc]
        # None всё равно в конце при reverse=True
        self.assertEqual(ages_desc, [30, 25, None])
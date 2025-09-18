import unittest
import os
import sys
sys.path.append('src')

from text_to_sql import TextToSQL
from sql_validator import SQLValidator
from database_utils import DatabaseUtils

class TestTextToSQL(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        self.test_db = "test.db"
        self.text_to_sql = TextToSQL(self.test_db)
        self.validator = SQLValidator(self.test_db)
        self.db_utils = DatabaseUtils(self.test_db)

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_database_initialization(self):
        """Test database is properly initialized"""
        tables = self.db_utils.get_table_info()
        self.assertEqual(len(tables), 2)
        table_names = [table['name'] for table in tables]
        self.assertIn('employees', table_names)
        self.assertIn('departments', table_names)

    def test_basic_sql_generation(self):
        """Test basic SQL generation"""
        question = "Show me all employees"
        result = self.text_to_sql.query(question)

        self.assertIsNotNone(result['sql_query'])
        self.assertIsNone(result['error'])
        self.assertTrue(len(result['results']) > 0)

    def test_sql_validation(self):
        """Test SQL validation"""
        # Valid query
        valid_sql = "SELECT * FROM employees"
        is_valid, errors = self.validator.validate_query(valid_sql)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid query
        invalid_sql = "SELECT * FROM nonexistent_table"
        is_valid, errors = self.validator.validate_query(invalid_sql)
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)

    def test_dangerous_query_detection(self):
        """Test detection of dangerous queries"""
        dangerous_query = "DROP TABLE employees"
        is_valid, errors = self.validator.validate_query(dangerous_query)
        self.assertFalse(is_valid)
        self.assertTrue("dangerous operations" in str(errors))

    def test_sample_queries(self):
        """Test various natural language queries"""
        test_cases = [
            ("Find employees older than 30", "age > 30"),
            ("Show employees in Engineering", "Engineering"),
            ("What is the average salary?", "AVG"),
            ("List all departments", "departments"),
            ("Show employees hired in 2020", "2020")
        ]

        for question, expected_keyword in test_cases:
            result = self.text_to_sql.query(question)
            self.assertIsNotNone(result['sql_query'], f"Failed to generate SQL for: {question}")
            if result['error'] is None:
                self.assertIn(expected_keyword, result['sql_query'].upper())

    def test_schema_extraction(self):
        """Test database schema extraction"""
        schema = self.db_utils.format_schema_for_llm()
        self.assertIn("Table: employees", schema)
        self.assertIn("Table: departments", schema)
        self.assertIn("Columns:", schema)

    def test_query_execution(self):
        """Test query execution with expected results"""
        result = self.text_to_sql.query("Count total number of employees")
        self.assertEqual(len(result['results']), 1)
        self.assertTrue(result['results'][0]['count(*)'] >= 5)

    def test_read_only_enforcement(self):
        """Test that only read-only queries are allowed"""
        read_only_query = "SELECT * FROM employees"
        self.assertTrue(self.validator.is_read_only_query(read_only_query))

        write_query = "INSERT INTO employees (name) VALUES ('Test')"
        self.assertFalse(self.validator.is_read_only_query(write_query))

if __name__ == '__main__':
    unittest.main()
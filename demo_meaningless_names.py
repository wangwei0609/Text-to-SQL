import os
import sqlite3
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, inspect
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class TextToSQLDemo:
    def __init__(self, db_path: str = "demo_meaningless_names.db"):
        self.db_path = db_path

        # Configure Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Initialize database with meaningless column names
        self._init_database()
        self._setup_prompts()

    def _init_database(self):
        """Initialize SQLite database with meaningless column names"""
        self.engine = create_engine(f"sqlite:///{self.db_path}")

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS t01 (
                    c001 INTEGER PRIMARY KEY,
                    c002 TEXT NOT NULL,
                    c003 INTEGER,
                    c004 INTEGER,
                    c005 REAL,
                    c006 DATE,
                    FOREIGN KEY (c004) REFERENCES t02(c001)
                );

                CREATE TABLE IF NOT EXISTS t02 (
                    c001 INTEGER PRIMARY KEY,
                    c002 TEXT NOT NULL,
                    c003 TEXT
                );

                INSERT OR IGNORE INTO t02 (c001, c002, c003) VALUES
                (1, 'Engineering', 'San Francisco'),
                (2, 'Sales', 'New York'),
                (3, 'Marketing', 'Los Angeles');

                INSERT OR IGNORE INTO t01 (c001, c002, c003, c004, c005, c006) VALUES
                (1, 'John Doe', 30, 1, 75000.0, '2020-01-15'),
                (2, 'Jane Smith', 28, 2, 65000.0, '2021-03-20'),
                (3, 'Bob Johnson', 35, 1, 85000.0, '2019-07-10'),
                (4, 'Alice Brown', 32, 3, 70000.0, '2020-11-05'),
                (5, 'Charlie Wilson', 29, 2, 68000.0, '2022-02-15');
            """)

    def _setup_prompts(self):
        """Setup prompt template for SQL generation"""
        self.prompt_template = """You are a SQL expert. Given the following database schema:

{schema}

Convert the user's natural language question into SQL.
Return only the SQL query without any explanation or formatting.

User question: {question}
SQL query:"""

    def get_database_schema(self) -> str:
        """Get the current database schema"""
        inspector = inspect(self.engine)
        schema = []

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)

            table_info = f"Table: {table_name}\n"
            table_info += "Columns:\n"

            for column in columns:
                col_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                primary_key = "PRIMARY KEY" if column['primary_key'] else ""
                table_info += f"  - {column['name']} {col_type} {nullable} {primary_key}\n"

            if foreign_keys:
                table_info += "Foreign Keys:\n"
                for fk in foreign_keys:
                    table_info += f"  - {fk['constrained_columns']} references {fk['referred_table']}({fk['referred_columns']})\n"

            schema.append(table_info)

        return "\n".join(schema)

    def generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question"""
        schema = self.get_database_schema()

        try:
            prompt = self.prompt_template.format(
                schema=schema,
                question=question
            )

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating SQL: {str(e)}"

    def show_schema_impact(self):
        """Demonstrate the impact of meaningless column names"""
        print("=== 数据库Schema (无意义列名) ===")
        print(self.get_database_schema())

        print("\n=== 测试查询 ===")

        # These queries will likely fail or be incorrect
        test_questions = [
            "Show me all employees",
            "Find employees older than 30",
            "Show employees in the Engineering department",
            "What is the average salary by department?"
        ]

        for question in test_questions:
            print(f"\n问题: {question}")
            sql_result = self.generate_sql(question)
            print(f"生成的SQL: {sql_result}")

if __name__ == "__main__":
    demo = TextToSQLDemo()
    demo.show_schema_impact()
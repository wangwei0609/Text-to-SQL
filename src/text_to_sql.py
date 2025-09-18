import os
import sqlite3
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, inspect
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

class TextToSQL:
    def __init__(self, db_path: str = "example.db"):
        self.db_path = db_path
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo",
            temperature=0
        )

        # Initialize database
        self._init_database()

        # Setup prompts
        self._setup_prompts()

    def _init_database(self):
        """Initialize SQLite database with sample data"""
        self.engine = create_engine(f"sqlite:///{self.db_path}")

        # Create tables if they don't exist
        self._create_sample_tables()

    def _create_sample_tables(self):
        """Create sample employee and department tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT
                );

                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    department_id INTEGER,
                    salary REAL,
                    hire_date DATE,
                    FOREIGN KEY (department_id) REFERENCES departments(id)
                );

                INSERT OR IGNORE INTO departments (id, name, location) VALUES
                (1, 'Engineering', 'San Francisco'),
                (2, 'Sales', 'New York'),
                (3, 'Marketing', 'Los Angeles');

                INSERT OR IGNORE INTO employees (id, name, age, department_id, salary, hire_date) VALUES
                (1, 'John Doe', 30, 1, 75000.0, '2020-01-15'),
                (2, 'Jane Smith', 28, 2, 65000.0, '2021-03-20'),
                (3, 'Bob Johnson', 35, 1, 85000.0, '2019-07-10'),
                (4, 'Alice Brown', 32, 3, 70000.0, '2020-11-05'),
                (5, 'Charlie Wilson', 29, 2, 68000.0, '2022-02-15');
            """)

    def _setup_prompts(self):
        """Setup LangChain prompts for SQL generation"""
        self.schema_prompt = PromptTemplate(
            input_variables=["schema"],
            template="""You are a SQL expert. Given the following database schema:

{schema}

Convert the user's natural language question into SQL.
Return only the SQL query without any explanation or formatting.

User question: {question}
SQL query:"""
        )

        self.sql_chain = LLMChain(
            llm=self.llm,
            prompt=self.schema_prompt
        )

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
            result = self.sql_chain.run(
                schema=schema,
                question=question
            )
            return result.strip()
        except Exception as e:
            return f"Error generating SQL: {str(e)}"

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql_query)
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            return [{"error": str(e)}]

    def query(self, question: str) -> Dict[str, Any]:
        """Main method: convert natural language to SQL and execute"""
        sql_query = self.generate_sql(question)

        if sql_query.startswith("Error"):
            return {
                "question": question,
                "sql_query": None,
                "results": [],
                "error": sql_query
            }

        results = self.execute_query(sql_query)

        return {
            "question": question,
            "sql_query": sql_query,
            "results": results,
            "error": None
        }

if __name__ == "__main__":
    # Example usage
    text_to_sql = TextToSQL()

    # Test questions
    questions = [
        "Show me all employees",
        "Find employees older than 30",
        "Show employees in the Engineering department",
        "What is the average salary by department?"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        result = text_to_sql.query(question)
        print(f"SQL: {result['sql_query']}")
        print(f"Results: {result['results']}")
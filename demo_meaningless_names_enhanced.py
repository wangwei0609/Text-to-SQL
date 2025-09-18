import os
import sqlite3
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, inspect
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class TextToSQLEnhanced:
    def __init__(self, db_path: str = "demo_meaningless_enhanced.db"):
        self.db_path = db_path

        # Configure Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Initialize database with meaningless column names
        self._init_database()
        self._setup_prompts()

    def _create_metadata_table(self):
        """Create column metadata table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS column_metadata (
                    table_name TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    business_name TEXT,
                    description TEXT,
                    data_type TEXT,
                    example_value TEXT,
                    is_sensitive BOOLEAN DEFAULT 0,
                    business_rules TEXT,
                    PRIMARY KEY (table_name, column_name)
                )
            """)

    def _insert_sample_metadata(self):
        """Insert sample metadata for meaningless columns"""
        metadata_data = [
            ('t01', 'c001', '员工ID', '员工的唯一标识符', 'INTEGER', '1, 2, 3', 0, '主键，自增'),
            ('t01', 'c002', '员工姓名', '员工的全名', 'TEXT', 'John Doe', 0, '不能为空'),
            ('t01', 'c003', '员工年龄', '员工的年龄', 'INTEGER', '30, 28, 35', 0, '必须大于18'),
            ('t01', 'c004', '部门ID', '员工所属部门ID', 'INTEGER', '1, 2, 3', 0, '外键，关联t02表'),
            ('t01', 'c005', '薪资', '员工的年薪', 'REAL', '75000.0, 65000.0', 1, '单位：美元'),
            ('t01', 'c006', '入职日期', '员工入职时间', 'DATE', '2020-01-15', 0, '格式：YYYY-MM-DD'),
            ('t02', 'c001', '部门ID', '部门的唯一标识符', 'INTEGER', '1, 2, 3', 0, '主键，自增'),
            ('t02', 'c002', '部门名称', '部门的中文名称', 'TEXT', 'Engineering, Sales', 0, '不能为空'),
            ('t02', 'c003', '办公地点', '部门所在城市', 'TEXT', 'San Francisco', 0, '可为空')
        ]

        with sqlite3.connect(self.db_path) as conn:
            conn.executemany("""
                INSERT OR IGNORE INTO column_metadata
                (table_name, column_name, business_name, description, data_type, example_value, is_sensitive, business_rules)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, metadata_data)

    def _init_database(self):
        """Initialize SQLite database with meaningless column names"""
        self.engine = create_engine(f"sqlite:///{self.db_path}")

        # Create metadata table
        self._create_metadata_table()

        # Create tables with meaningless names
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

        # Insert sample metadata
        self._insert_sample_metadata()

    def _setup_prompts(self):
        """Setup prompt template for SQL generation"""
        self.prompt_template = """You are a SQL expert. Given the following database schema:

{schema}

Convert the user's natural language question into SQL.
Return only the SQL query without any explanation or formatting.

User question: {question}
SQL query:"""

    def get_column_metadata(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Get column metadata from the metadata table"""
        metadata = {}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT table_name, column_name, business_name, description,
                       data_type, example_value, is_sensitive, business_rules
                FROM column_metadata
            """)

            for row in cursor.fetchall():
                table_name, column_name, business_name, description, data_type, example_value, is_sensitive, business_rules = row

                if table_name not in metadata:
                    metadata[table_name] = {}

                metadata[table_name][column_name] = {
                    'business_name': business_name,
                    'description': description,
                    'data_type': data_type,
                    'example_value': example_value,
                    'is_sensitive': bool(is_sensitive),
                    'business_rules': business_rules
                }

        return metadata

    def get_enhanced_schema(self) -> str:
        """Get enhanced database schema with metadata"""
        inspector = inspect(self.engine)
        metadata = self.get_column_metadata()
        schema = []

        for table_name in inspector.get_table_names():
            if table_name == 'column_metadata':
                continue  # Skip the metadata table itself

            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)

            table_info = f"Table: {table_name}\n"
            table_info += "Columns:\n"

            for column in columns:
                col_name = column['name']
                col_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                primary_key = "PRIMARY KEY" if column['primary_key'] else ""

                # Add metadata if available
                metadata_info = ""
                if table_name in metadata and col_name in metadata[table_name]:
                    meta = metadata[table_name][col_name]
                    metadata_info = f" (业务名称: {meta['business_name']}, 描述: {meta['description']}"
                    if meta['example_value']:
                        metadata_info += f", 示例: {meta['example_value']}"
                    if meta['business_rules']:
                        metadata_info += f", 规则: {meta['business_rules']}"
                    if meta['is_sensitive']:
                        metadata_info += ", 敏感字段"
                    metadata_info += ")"

                table_info += f"  - {col_name} {col_type} {nullable} {primary_key}{metadata_info}\n"

            if foreign_keys:
                table_info += "Foreign Keys:\n"
                for fk in foreign_keys:
                    table_info += f"  - {fk['constrained_columns']} references {fk['referred_table']}({fk['referred_columns']})\n"

            schema.append(table_info)

        return "\n".join(schema)

    def get_basic_schema(self) -> str:
        """Get basic schema without metadata (for comparison)"""
        inspector = inspect(self.engine)
        schema = []

        for table_name in inspector.get_table_names():
            if table_name == 'column_metadata':
                continue

            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)

            table_info = f"Table: {table_name}\n"
            table_info += "Columns:\n"

            for column in columns:
                col_name = column['name']
                col_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                primary_key = "PRIMARY KEY" if column['primary_key'] else ""
                table_info += f"  - {col_name} {col_type} {nullable} {primary_key}\n"

            if foreign_keys:
                table_info += "Foreign Keys:\n"
                for fk in foreign_keys:
                    table_info += f"  - {fk['constrained_columns']} references {fk['referred_table']}({fk['referred_columns']})\n"

            schema.append(table_info)

        return "\n".join(schema)

    def generate_sql(self, question: str, use_metadata: bool = True) -> str:
        """Generate SQL from natural language question"""
        if use_metadata:
            schema = self.get_enhanced_schema()
        else:
            schema = self.get_basic_schema()

        try:
            prompt = self.prompt_template.format(
                schema=schema,
                question=question
            )

            response = self.model.generate_content(prompt)
            return response.text.strip()
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

    def show_comparison(self):
        """Show comparison between basic and enhanced schema"""
        print("=== 基础Schema (无元数据) ===")
        print(self.get_basic_schema())

        print("\n=== 增强Schema (含元数据) ===")
        print(self.get_enhanced_schema())

        print("\n=== 对比测试 ===")

        test_questions = [
            "Show me all employees",
            "Find employees older than 30",
            "Show employees in the Engineering department",
            "What is the average salary by department?"
        ]

        for question in test_questions:
            print(f"\n问题: {question}")

            # Without metadata
            print("Without metadata:")
            sql_without = self.generate_sql(question, use_metadata=False)
            print(f"  SQL: {sql_without}")

            # With metadata
            print("With metadata:")
            sql_with = self.generate_sql(question, use_metadata=True)
            print(f"  SQL: {sql_with}")

            # Execute the better query
            if sql_with and not sql_with.startswith("Error"):
                results = self.execute_query(sql_with)
                print(f"  Results: {results}")

if __name__ == "__main__":
    demo = TextToSQLEnhanced()
    demo.show_comparison()
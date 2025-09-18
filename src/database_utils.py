import sqlite3
from typing import List, Dict, Any
from sqlalchemy import create_engine, inspect, text

class DatabaseUtils:
    def __init__(self, db_path: str = "example.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")

    def get_table_info(self) -> List[Dict[str, Any]]:
        """Get detailed information about all tables"""
        inspector = inspect(self.engine)
        tables_info = []

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)

            table_info = {
                "name": table_name,
                "columns": [],
                "primary_keys": primary_keys.get("constrained_columns", []),
                "foreign_keys": []
            }

            for column in columns:
                table_info["columns"].append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "primary_key": column["primary_key"],
                    "default": column.get("default")
                })

            for fk in foreign_keys:
                table_info["foreign_keys"].append({
                    "name": fk["name"],
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"]
                })

            tables_info.append(table_info)

        return tables_info

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            return [{"error": str(e)}]

    def validate_sql(self, sql_query: str) -> bool:
        """Validate if SQL query is syntactically correct"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"EXPLAIN {sql_query}")
                return True
        except:
            return False

    def format_schema_for_llm(self) -> str:
        """Format database schema in LLM-friendly format"""
        tables_info = self.get_table_info()
        schema_parts = []

        for table in tables_info:
            schema_part = f"Table: {table['name']}\n"
            schema_part += "Columns:\n"

            for col in table['columns']:
                constraints = []
                if not col['nullable']:
                    constraints.append("NOT NULL")
                if col['primary_key']:
                    constraints.append("PRIMARY KEY")
                constraint_str = " ".join(constraints) if constraints else ""

                schema_part += f"  - {col['name']} {col['type']} {constraint_str}\n"

            if table['foreign_keys']:
                schema_part += "Foreign Keys:\n"
                for fk in table['foreign_keys']:
                    schema_part += f"  - {fk['constrained_columns']} references {fk['referred_table']}({fk['referred_columns']})\n"

            # Add sample data
            sample_data = self.get_sample_data(table['name'], 3)
            if sample_data and not any("error" in row for row in sample_data):
                schema_part += f"Sample data (first 3 rows):\n"
                for row in sample_data:
                    schema_part += f"  - {row}\n"

            schema_parts.append(schema_part)

        return "\n".join(schema_parts)
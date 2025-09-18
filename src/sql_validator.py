import sqlite3
import re
from typing import List, Tuple

class SQLValidator:
    def __init__(self, db_path: str = "example.db"):
        self.db_path = db_path

    def validate_query(self, sql_query: str) -> Tuple[bool, List[str]]:
        """Validate SQL query and return (is_valid, error_messages)"""
        errors = []

        # Basic SQL injection prevention
        if self._is_potential_injection(sql_query):
            errors.append("Potential SQL injection detected")

        # Check for dangerous operations
        if self._contains_dangerous_operations(sql_query):
            errors.append("Query contains potentially dangerous operations")

        # Syntax validation
        if not self._validate_syntax(sql_query):
            errors.append("Invalid SQL syntax")

        return len(errors) == 0, errors

    def _is_potential_injection(self, sql_query: str) -> bool:
        """Check for potential SQL injection patterns"""
        dangerous_patterns = [
            r';\s*drop\s+',
            r';\s*delete\s+from\s+\w+\s*where\s+1\s*=\s*1',
            r';\s*truncate\s+',
            r';\s*exec\s*\(',
            r';\s*xp_cmdshell',
            r';\s*union\s+select',
            r'--\s*$',
            r'/\*\s*\*/',
            r'\bor\s+1\s*=\s*1\b',
            r'\bwaitfor\s+delay\b'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                return True
        return False

    def _contains_dangerous_operations(self, sql_query: str) -> bool:
        """Check for potentially dangerous SQL operations"""
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT',
            'UPDATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
        ]

        query_upper = sql_query.upper()

        # Allow SELECT and safe operations
        if query_upper.strip().startswith('SELECT'):
            return False

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return True

        return False

    def _validate_syntax(self, sql_query: str) -> bool:
        """Validate SQL syntax using database engine"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Use EXPLAIN to validate syntax without executing
                conn.execute(f"EXPLAIN {sql_query}")
                return True
        except sqlite3.Error:
            return False

    def sanitize_query(self, sql_query: str) -> str:
        """Basic query sanitization"""
        # Remove comments
        sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)

        # Remove extra whitespace
        sql_query = ' '.join(sql_query.split())

        return sql_query.strip()

    def is_read_only_query(self, sql_query: str) -> bool:
        """Check if query is read-only (SELECT)"""
        query_upper = sql_query.upper().strip()
        return query_upper.startswith('SELECT') or query_upper.startswith('WITH')
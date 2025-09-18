#!/usr/bin/env python3
"""
Example usage of the Text-to-SQL system
"""
import sys
import os
sys.path.append('src')

from text_to_sql import TextToSQL
from sql_validator import SQLValidator
from database_utils import DatabaseUtils

def main():
    print("=== Text-to-SQL PoC Demo ===\n")

    # Initialize components
    text_to_sql = TextToSQL()
    validator = SQLValidator()
    db_utils = DatabaseUtils()

    # Show database schema
    print("Database Schema:")
    print("-" * 50)
    print(db_utils.format_schema_for_llm())
    print()

    # Example queries
    examples = [
        "Show me all employees and their departments",
        "Find employees older than 30 with salary above 70000",
        "What is the average salary by department?",
        "Count employees in each department",
        "Show the highest paid employee in Engineering",
        "List employees hired in 2020"
    ]

    print("Example Queries:")
    print("=" * 50)

    for i, question in enumerate(examples, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 30)

        # Generate and execute query
        result = text_to_sql.query(question)

        if result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Generated SQL: {result['sql_query']}")
            print(f"📊 Results ({len(result['results'])} rows):")

            for j, row in enumerate(result['results'][:3], 1):  # Show first 3 results
                print(f"   {j}. {row}")

            if len(result['results']) > 3:
                print(f"   ... and {len(result['results']) - 3} more rows")

        print()

    # Interactive mode
    print("\n" + "=" * 50)
    print("Interactive Mode (type 'quit' to exit)")
    print("=" * 50)

    while True:
        user_question = input("\nAsk a question about the database: ").strip()

        if user_question.lower() in ['quit', 'exit', 'q']:
            break

        if not user_question:
            continue

        result = text_to_sql.query(user_question)

        if result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ SQL: {result['sql_query']}")
            if result['results']:
                print("📊 Results:")
                for i, row in enumerate(result['results'], 1):
                    print(f"   {i}. {row}")
            else:
                print("📊 No results found")

    print("\nThank you for using Text-to-SQL!")

if __name__ == "__main__":
    main()
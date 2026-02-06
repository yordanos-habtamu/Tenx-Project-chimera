import os
import sys

from sqlalchemy import inspect

from src.database.connection import get_engine, init_db


def verify_database():
    print("Verifying Database Persistence (SQLite)...")

    # 1. Initialize DB (Creates tables)
    try:
        init_db()
        print("PASS: Database initialization routine executed")
    except Exception as e:
        print(f"FAIL: Database initialization failed: {e}")
        sys.exit(1)

    # 2. Check File Existence
    if os.path.exists("chimera.db"):
        print("PASS: chimera.db file created")
    else:
        print("FAIL: chimera.db file NOT found")
        sys.exit(1)

    # 3. Inspect Tables
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"Tables found: {tables}")

    required_tables = ["agents", "tasks", "videos", "trends"]
    missing = [t for t in required_tables if t not in tables]

    if not missing:
        print("PASS: All required tables present")
    else:
        print(f"FAIL: Missing tables: {missing}")
        sys.exit(1)


if __name__ == "__main__":
    verify_database()

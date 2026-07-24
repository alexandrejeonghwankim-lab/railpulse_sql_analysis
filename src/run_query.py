import sqlite3 
from pathlib import path 

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "railpulse.db"
)

QUERY_PATH = (
    PROJECT_ROOT
    / "sql"
    / "analysis"
    / "01_peak_hour.sql"
)

if not DATABASE_PATH.is_file():
    raise FileNotFoundError(
        f"Database not found: {DATABASE_PATH}"
    )

if not QUERY_PATH.is_file():
    raise FileNotFoundError(
        f"SQL file not found: {QUERY_PATH}"
    )

query = QUERY_PATH.read_text(
    encoding="utf-8"
)

print("Executing SQL:")
print(query)
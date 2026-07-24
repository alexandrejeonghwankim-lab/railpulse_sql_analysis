import sqlite3
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCHEMA_PATH = PROJECT_ROOT / "docs" / "First_diagram.sql"

DATABASE_PATH = PROJECT_ROOT / "database" / "railpulse.db"




def create_database():
    """ Create the Railpulse tables from the SQL schema."""

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_PATH}"
        )
    schema_sql = SCHEMA_PATH.read_text(encoding = "utf-8")
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
        )
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_sql)

        tables = conn.execute(
        """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name

"""
    ).fetchall()

        print("Created tables:")
        for table in tables: 
            print(f"- {table[0]}")

    print(f"Database ready: {DATABASE_PATH}")

if __name__ == "__main__":
    create_database()
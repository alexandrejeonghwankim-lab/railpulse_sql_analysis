import csv
import sqlite3
from datetime import datetime
from pathlib import Path

from ingest_config import BATCH_SIZE, IMPORT_ORDER, TABLE_CONFIG


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = (
    PROJECT_ROOT
    / "SNCB_text_data"
    / "SNCB_GTFS"
)
DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "railpulse.db"
)


def expected_source_columns(config):
    """Return the source columns required by one table configuration."""

    return {
        config["source_columns"].get(database_column, database_column)
        for database_column in config["columns"]
    }


def validate_source_file(table_name):
    """Check that one GTFS file exists and contains the expected columns."""

    config = TABLE_CONFIG[table_name]
    source_path = DATA_DIRECTORY / config["source_file"]

    if not source_path.is_file():
        print(
            f"[MISSING] {table_name}: "
            f"{config['source_file']}"
        )
        return False

    with source_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as source_file:
        reader = csv.DictReader(source_file)
        actual_columns = set(reader.fieldnames or [])

    required_columns = expected_source_columns(config)
    missing_columns = required_columns - actual_columns

    if missing_columns:
        print(
            f"[INVALID] {table_name}: "
            f"missing columns {sorted(missing_columns)}"
        )
        return False

    print(
        f"[OK] {table_name}: "
        f"{config['source_file']} "
        f"({len(actual_columns)} columns)"
    )
    return True


def empty_to_none(value):
    """Convert an empty GTFS value into SQL NULL"""

    if value == "":
        return None
    return value

def convert_gtfs_date(value):
    """Convert a GTFS YYYYMMDD date into YYYY-MM-DD."""

    parsed_date = datetime.strptime(value, "%Y%m%d").date()
    return parsed_date.isoformat()

def convert_value(value, column, config):
    """Convert one GTFS value to its database data type."""

    value = empty_to_none(value)

    if value is None:
        return None

    if column in config.get("integer_columns", []):
        return int(value)

    if column in config.get("real_columns", []):
        return float(value)

    if column in config.get("date_columns", []):
        return convert_gtfs_date(value)

    return value 

def prepare_row(source_row, config):
    """Create a database-ready tuple from one GTFS record."""

    values = []

    for database_column in config["columns"]:
        source_column = config["source_columns"].get(
            database_column,
            database_column,
        )
        source_value = source_row[source_column]
        converted_value = convert_value(
            source_value,
            database_column,
            config)
        values.append(converted_value)

    return tuple(values)

def build_upsert_sql(table_name, config):
    """Build an INSERT/UPDATE statement for one configured table."""

    columns = config["columns"]
    conflict_columns = config["conflict_columns"]

    column_names = ", ".join(columns)
    placeholders = ", ".join(
        "?" for _ in columns
    )

    conflict_names = ", ".join(conflict_columns)
    update_columns = [
        column
        for column in columns
        if column not in conflict_columns
    ]

    update_assignments = ", ".join(
        f"{column} = excluded.{column}"
        for column in update_columns
    )

    return f"""
        INSERT INTO {table_name} (
            {column_names}
        )
        VALUES (
            {placeholders}
        )
        ON CONFLICT ({conflict_names}) DO UPDATE SET
            {update_assignments}
    """

def write_batch(connection, insert_sql, batch):
    """Insert one batch and empty the batch list."""

    connection.executemany(insert_sql, batch)
    batch.clear()


def import_table(connection, table_name):
    """Import one configured GTFS file into SQLite."""

    config = TABLE_CONFIG[table_name]
    source_path = DATA_DIRECTORY / config["source_file"]
    insert_sql = build_upsert_sql(table_name, config)

    batch = []
    processed_count = 0
    with source_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as source_file:
        reader = csv.DictReader(source_file)

        for source_row in reader:
            database_values = prepare_row(
                source_row,
                config
            )

            batch.append(database_values)

            if len(batch) >= BATCH_SIZE:
                processed_count += len(batch)
                write_batch(
                    connection,
                    insert_sql,
                    batch
                ) 
                print(
                    f"{table_name}: "
                    f"{processed_count:,} records processed."
                )
        if batch:
            processed_count += len(batch)
            write_batch(
                connection,
                insert_sql,
                batch
            )
    print(
        f"{table_name}: "
        f"{processed_count:,} records imported."
    )

def count_table_rows(connection, table_name):
    """Return the current number of rows in a database table."""

    result = connection.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()

    return result[0]

def check_foreign_keys(connection):
    """Return all foreign-key violations."""

    return connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()


def test_first_record(table_name):
    """Prepare and display the first record from one GTFS file."""

    config = TABLE_CONFIG[table_name]
    source_path = DATA_DIRECTORY / config["source_file"]

    with source_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as source_file:
        reader = csv.DictReader(source_file)
        source_row = next(reader, None)

    if source_row is None:
        raise ValueError(
            f"{config['source_file']} contains no records."
        )
    database_values = prepare_row(source_row, config)
    print(f"First prepared record for {table_name}:")
    for column, value in zip(
        config["columns"],
        database_values,
    ):
        print (
            f"-{column}: {value!r}"
            f"({type(value).__name__})"
        )


def test_generate_sql():
    """Display generated SQL for single and composite primary keys."""

    test_tables = (
        "agencies",
        "service_exceptions",
        "stop_times",
    )

    for table_name in test_tables:
        config = TABLE_CONFIG[table_name]
        generated_sql = build_upsert_sql(table_name, config)

        print(f"Generated SQL for {table_name}:")
        print(generated_sql)


def main():
    """Validate the sources and test conversion of one row per table."""

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data directory exists: {DATA_DIRECTORY.is_dir()}")
    print(f"Database exists: {DATABASE_PATH.is_file()}")
    print()

    validation_results = [
        validate_source_file(table_name)
        for table_name in IMPORT_ORDER
    ]

    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}. "
            "Run create_database.py first."
        )

    if not all(validation_results):
        raise ValueError(
            "One or more required GTFS source files failed validation."
        )

    print()
    print("All required GTFS files passed validation.")
    print()

    # Import all required tables in foreign-key-safe order.
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        for table_name in IMPORT_ORDER:
            print()
            print(f"Importing {table_name}...")

            connection.execute(
                "PRAGMA defer_foreign_keys = ON"
            )

            import_table(connection, table_name)
            connection.commit()

            row_count = count_table_rows(
                connection,
                table_name,
            )

            print(
                f"Rows in {table_name}: "
                f"{row_count:,}"
            )

        violations = check_foreign_keys(connection)

        if violations:
            raise ValueError(
                f"Foreign-key violations found: "
                f"{violations[:10]}"
            )
        print()
        print("Database import completed successfully.")
        print("Foreign-key check passed.")


if __name__ == "__main__":
    main()

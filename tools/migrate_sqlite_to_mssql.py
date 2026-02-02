#!/usr/bin/env python
"""
One-time migration script: Copy data from SQLite files to MSSQL.
Run before switching USE_MSSQL=1.

Usage:
  python tools/migrate_sqlite_to_mssql.py [location_dir]
  If location_dir omitted, uses current directory or scans for *.db files.
"""
import os
import sys
import sqlite3

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _is_duplicate_key_error(e):
    """Return True if exception is a duplicate/primary key violation (MSSQL or generic)."""
    msg = str(e).lower()
    return (
        "primary key" in msg
        or "duplicate" in msg
        or "unique" in msg
        or "violation" in msg
        or "2627" in msg  # MSSQL duplicate key
        or "2601" in msg  # MSSQL unique index
    )


def migrate_file(sqlite_path, project_id, engine):
    """Migrate one SQLite file to MSSQL. project_id = basename or identifier."""
    from sqlalchemy import text

    if not os.path.exists(sqlite_path):
        print(f"Skip (not found): {sqlite_path}")
        return 0

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    count = 0

    tables = ["backups_M", "backups", "restoreM", "restores", "node_jobs", "jobs_recordManager"]
    # SQLite column -> MSSQL column for tables where names differ (e.g. jobs_recordManager: id -> job_id)
    col_map = {"jobs_recordManager": {"id": "job_id"}}

    with engine.connect() as mssql_conn:
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                if not rows:
                    continue
                cols = [d[0] for d in cursor.description]
                if "project_id" not in cols:
                    cols = ["project_id"] + cols
                table_map = col_map.get(table, {})

                for row in rows:
                    row_dict = dict(zip([d[0] for d in cursor.description], row))
                    row_dict["project_id"] = project_id
                    # Apply column renames for MSSQL (e.g. SQLite "id" -> MSSQL "job_id")
                    for old_name, new_name in table_map.items():
                        if old_name in row_dict:
                            row_dict[new_name] = row_dict.pop(old_name)
                    col_names = ", ".join(row_dict.keys())
                    placeholders = ", ".join([":" + k for k in row_dict.keys()])
                    # MSSQL has no INSERT IGNORE; use INSERT and skip on duplicate key
                    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                    try:
                        mssql_conn.execute(text(sql), row_dict)
                        count += 1
                    except Exception as e:
                        if _is_duplicate_key_error(e):
                            pass  # skip duplicate
                        else:
                            print(f"  Warning: {table} insert: {e}")
                mssql_conn.commit()
            except sqlite3.OperationalError as e:
                if "no such table" in str(e).lower():
                    pass
                else:
                    print(f"  Error reading {table}: {e}")

    conn.close()
    return count


def main():
    location = None
    if len(sys.argv) > 1:
        location = sys.argv[1]
    else:
        try:
            from FlaskWebProject3 import app
            location = (app.config.get("location") if app.config else None) or os.getcwd()
        except Exception:
            location = os.getcwd()

    try:
        from FlaskWebProject3.db_config import DATABASE_URL, USE_MSSQL
        from sqlalchemy import create_engine
    except ImportError:
        print("Run from project root. FlaskWebProject3 must be importable.")
        sys.exit(1)

    engine = create_engine(DATABASE_URL)

    # Ensure tables exist
    from FlaskWebProject3.db import create_all_tables
    create_all_tables()

    # Find *.db files - SQLite files may not have .db extension in path
    db_files = []
    for root, _, files in os.walk(location):
        for f in files:
            if f.endswith(".db"):
                db_files.append(os.path.join(root, f))
            elif ".db" in f or (not f.endswith(".db") and "sqlite" in root.lower()):
                pass

    # Also check for db files without extension (path like location/epc)
    for item in os.listdir(location):
        path = os.path.join(location, item)
        if os.path.isfile(path) and not item.endswith(".db"):
            # Could be SQLite - try opening
            try:
                conn = sqlite3.connect(path)
                conn.execute("SELECT 1")
                conn.close()
                db_files.append(path)
            except Exception:
                pass

    total = 0
    for path in db_files:
        project_id = os.path.basename(path).replace(".db", "") or os.path.basename(os.path.dirname(path))
        n = migrate_file(path, project_id, engine)
        total += n
        print(f"Migrated {path} -> project_id={project_id}: {n} rows")

    print(f"Total rows migrated: {total}")


if __name__ == "__main__":
    main()

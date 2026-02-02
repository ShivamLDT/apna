"""
Auto-migrate SQLite data to MSSQL on server startup when USE_MSSQL=1.
Tracks migrated files in sqlite_migration_log to avoid re-migrating on restart.
"""
import os
import sqlite3
import logging

logger = logging.getLogger("flask_app")


def _is_duplicate_key_error(e):
    """Return True if exception is a duplicate/primary key violation."""
    msg = str(e).lower()
    return (
        "primary key" in msg
        or "duplicate" in msg
        or "unique" in msg
        or "violation" in msg
        or "2627" in msg
        or "2601" in msg
    )


def _migrate_single_file(engine, sqlite_path, project_id):
    """Migrate one SQLite file to MSSQL. Returns number of rows migrated."""
    from sqlalchemy import text

    if not os.path.exists(sqlite_path):
        return 0

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    count = 0

    tables = ["backups_M", "backups", "restoreM", "restores", "node_jobs", "jobs_recordManager"]
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
                    for old_name, new_name in table_map.items():
                        if old_name in row_dict:
                            row_dict[new_name] = row_dict.pop(old_name)
                    col_names = ", ".join(row_dict.keys())
                    placeholders = ", ".join([":" + k for k in row_dict.keys()])
                    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                    try:
                        mssql_conn.execute(text(sql), row_dict)
                        count += 1
                    except Exception as e:
                        if _is_duplicate_key_error(e):
                            pass
                        else:
                            logger.warning("Migration insert %s: %s", table, e)
                mssql_conn.commit()
            except sqlite3.OperationalError as e:
                if "no such table" not in str(e).lower():
                    logger.warning("Migration read %s from %s: %s", table, sqlite_path, e)

    conn.close()
    return count


def _find_sqlite_files(location):
    """Find SQLite .db files and files without extension that are SQLite databases."""
    if not location or not os.path.isdir(location):
        return []

    db_files = []
    for root, _, files in os.walk(location):
        for f in files:
            if f.endswith(".db"):
                db_files.append(os.path.join(root, f))

    for item in os.listdir(location):
        path = os.path.join(location, item)
        if os.path.isfile(path) and not item.endswith(".db"):
            try:
                conn = sqlite3.connect(path)
                conn.execute("SELECT 1")
                conn.close()
                db_files.append(path)
            except Exception:
                pass

    return db_files


def run_auto_migration(app):
    """
    On server startup, if USE_MSSQL=1, scan for SQLite files and migrate any
    that haven't been migrated before. Uses sqlite_migration_log to avoid
    re-migrating on restart.
    """
    try:
        from FlaskWebProject3.db_config import USE_MSSQL, DATABASE_URL
        from FlaskWebProject3.models import Base, SqliteMigrationLog
        from sqlalchemy import create_engine, text
    except ImportError as e:
        logger.debug("Auto-migration skipped (import error): %s", e)
        return

    if not USE_MSSQL:
        return

    location = app.config.get("location")
    if not location:
        logger.debug("Auto-migration skipped: no location config")
        return

    try:
        engine = create_engine(DATABASE_URL)

        # Ensure sqlite_migration_log table exists
        Base.metadata.create_all(bind=engine, tables=[SqliteMigrationLog.__table__])

        db_files = _find_sqlite_files(location)
        if not db_files:
            return

        migrated_this_run = 0
        with engine.connect() as conn:
            for path in db_files:
                project_id = (
                    os.path.basename(path).replace(".db", "")
                    or os.path.basename(os.path.dirname(path))
                )
                source_path = os.path.abspath(path)

                # Check if already migrated
                result = conn.execute(
                    text(
                        "SELECT 1 FROM sqlite_migration_log "
                        "WHERE project_id = :pid AND source_path = :path"
                    ),
                    {"pid": project_id, "path": source_path},
                )
                if result.fetchone():
                    continue

                # Migrate
                try:
                    n = _migrate_single_file(engine, path, project_id)
                    conn.execute(
                        text(
                            "INSERT INTO sqlite_migration_log (project_id, source_path) "
                            "VALUES (:pid, :path)"
                        ),
                        {"pid": project_id, "path": source_path},
                    )
                    conn.commit()
                    migrated_this_run += n
                    logger.info(
                        "Auto-migrated SQLite %s -> MSSQL project_id=%s: %d rows",
                        path, project_id, n,
                    )
                except Exception as e:
                    conn.rollback()
                    logger.warning("Auto-migration failed for %s: %s", path, e)

        if migrated_this_run > 0:
            logger.info("Auto-migration complete: %d total rows migrated", migrated_this_run)
    except Exception as e:
        logger.warning("Auto-migration error: %s", e)

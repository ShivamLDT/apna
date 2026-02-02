"""
Database helper functions for common operations.
Uses SQLAlchemy ORM; project_id is required for all tenant-scoped operations.
"""
from FlaskWebProject3.db import get_session_for_project
from module2 import BackupLogs, BackupMain


def _project_id_from_db_path(db_path):
    """Derive project_id from legacy db_path (can be full path or filename)."""
    import os
    if not db_path:
        return ""
    # db_path is often like "C:\...\location\epc" or "epc" - use basename or full path
    return os.path.basename(db_path.rstrip("/\\")) or db_path


def query_backup_by_id_name(project_id, backup_id, name):
    """Get BackupLogs row by id and name. Returns ORM object or None."""
    with get_session_for_project(project_id) as session:
        return session.query(BackupLogs).filter(
            BackupLogs.project_id == project_id,
            BackupLogs.id == float(backup_id),
            BackupLogs.name == float(name),
        ).first()


def query_backup_main_by_id(project_id, main_id):
    """Get BackupMain row by id. Returns ORM object or None."""
    with get_session_for_project(project_id) as session:
        return session.query(BackupMain).filter(
            BackupMain.project_id == project_id,
            BackupMain.id == float(main_id),
        ).first()


def upsert_backup_main(project_id, **kwargs):
    """Insert or update BackupMain. Uses merge for upsert."""
    from module2 import BackupMain
    with get_session_for_project(project_id) as session:
        row = BackupMain(project_id=project_id, **kwargs)
        session.merge(row)


def update_backup_main_sum_done(project_id, main_id, sum_done):
    """Update sum_done on BackupMain."""
    from sqlalchemy import update
    from module2 import BackupMain
    with get_session_for_project(project_id) as session:
        session.execute(
            update(BackupMain)
            .where(BackupMain.project_id == project_id, BackupMain.id == float(main_id))
            .values(sum_done=int(sum_done))
        )


def insert_or_replace_backup_log(project_id, **kwargs):
    """Insert or replace BackupLogs row."""
    from module2 import BackupLogs
    with get_session_for_project(project_id) as session:
        row = BackupLogs(project_id=project_id, **kwargs)
        session.merge(row)


def execute_raw_select(project_id, table_name, where_clause_parts, params=None):
    """
    Execute a raw SELECT - for complex queries during migration.
    Prefer using ORM query_backup_* methods when possible.
    """
    from sqlalchemy import text
    with get_session_for_project(project_id) as session:
        # Only for backward compat during migration - most should use ORM
        sql = f"SELECT * FROM {table_name} WHERE {where_clause_parts}"
        result = session.execute(text(sql), params or {})
        return result.fetchall()

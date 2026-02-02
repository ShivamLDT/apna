
import sqlite3
import os

# Array of strings to match against the family_name column
familyNames = ["pdf", "xlsx", "Williams", "Jones", "Brown"]

# Database path: use env or default (for SQLite); project_id for MSSQL
_db_path = os.getenv("MODULE13_DB_PATH", "D:\\PyRepos\\FlaskWebProject3\\FlaskWebProject3\\26d1bc626d2bdccc8874b7da3e914d9a4053f7975d83845aa70e74395ba3719c.db")
_project_id = os.path.splitext(os.path.basename(_db_path))[0]

try:
    from FlaskWebProject3.db_config import USE_MSSQL
    from FlaskWebProject3.db import get_session_for_project
    from FlaskWebProject3.models import BackupLogs
except ImportError:
    USE_MSSQL = False

if USE_MSSQL:
    with get_session_for_project(_project_id) as session:
        from sqlalchemy import or_
        q = session.query(BackupLogs).filter(
            BackupLogs.project_id == _project_id,
            BackupLogs.name == 1717235820.3287108,
            or_(*[BackupLogs.full_file_name.like(f"%{name}") for name in familyNames]),
        )
        results = q.all()
        for row in results:
            print(getattr(row, "mime_type", row[8] if hasattr(row, "__getitem__") else None))
else:
    conn = sqlite3.connect(_db_path)
    cursor = conn.cursor()
    query = "SELECT * FROM backups WHERE name = 1717235820.3287108 and (" + " OR ".join([f"full_file_name LIKE '%{name}'" for name in familyNames]) + ")"
    print("Constructed Query:", query)
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(row[8])
    conn.close()

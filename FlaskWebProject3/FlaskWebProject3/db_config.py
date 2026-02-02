"""
Database configuration for MSSQL migration.
Reads from environment variables; falls back to SQLite when MSSQL is not configured.
"""
import os

# Load .env file if python-dotenv is available (so you can set DATABASE_URL etc. in .env)
try:
    from dotenv import load_dotenv
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_this_dir)
    _repo_root = os.path.dirname(_project_root)
    for d in (_repo_root, _project_root, _this_dir, os.getcwd()):
        p = os.path.join(d, ".env")
        if os.path.isfile(p):
            load_dotenv(p)
            break
    else:
        load_dotenv()  # fallback to cwd
except ImportError:
    pass

# Set USE_MSSQL=1 to enable Microsoft SQL Server; set to 0 for SQLite fallback (default: 0 for backward compat)
USE_MSSQL = os.getenv("USE_MSSQL", "0").lower() in ("1", "true", "yes", "on")

# MSSQL connection URLs - set via env or provide defaults for local dev (requires ODBC Driver 17/18 for SQL Server)
_DEFAULT_SYNC = "mssql+pyodbc://user:password@localhost/apnabackup?driver=ODBC+Driver+17+for+SQL+Server"
_DEFAULT_ASYNC = "mssql+aioodbc://user:password@localhost/apnabackup?driver=ODBC+Driver+17+for+SQL+Server"
DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_SYNC)
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", _DEFAULT_ASYNC)

# Pool settings for sync engine
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))

# Async pool settings for SessionStore
ASYNC_POOL_SIZE = int(os.getenv("DB_ASYNC_POOL_SIZE", "10"))
ASYNC_MAX_OVERFLOW = int(os.getenv("DB_ASYNC_MAX_OVERFLOW", "5"))

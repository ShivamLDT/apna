"""Database config for fClient - reads from env. Use MSSQL when USE_MSSQL=1."""
import os
USE_MSSQL = os.getenv("USE_MSSQL", "0").lower() in ("1", "true", "yes", "on")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://user:password@localhost/apnabackup?driver=ODBC+Driver+17+for+SQL+Server",
)

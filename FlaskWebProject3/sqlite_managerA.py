# Phase 4: SQLiteManager deprecated. Use FlaskWebProject3.sqlite_legacy.execute_queries_sqlite when USE_MSSQL=0.
import warnings
warnings.warn(
    "sqlite_managerA is deprecated; use FlaskWebProject3.sqlite_legacy.execute_queries_sqlite",
    DeprecationWarning,
    stacklevel=2,
)
import sys
import os
# Allow import from FlaskWebProject3 package when run from project root
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, os.path.dirname(_here))
from FlaskWebProject3.sqlite_legacy import execute_queries_sqlite

class SQLiteManager:
    """Deprecated. Use execute_queries_sqlite() from FlaskWebProject3.sqlite_legacy instead."""
    def execute_queries(self, db_query_pairs, timeout=20):
        return execute_queries_sqlite(db_query_pairs, timeout=timeout)

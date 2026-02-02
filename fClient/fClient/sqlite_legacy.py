"""
Legacy SQLite execute_queries helper (Phase 4: replaces SQLiteManager).
Use when USE_MSSQL=0 for backward compatibility. Same return shape as former SQLiteManager.execute_queries.
"""
import sqlite3
import threading
import time


def execute_queries_sqlite(db_query_pairs, timeout=20):
    """
    Execute (db_path, [sql1, sql2, ...]) pairs using direct sqlite3.
    Returns: {db_path: [(result, records), ...]} where result is "Success" or "Failed: ...".
    """
    lock = threading.Lock()

    def execute_single_query(db_path, query):
        start_time = time.time()
        while True:
            try:
                conn = sqlite3.connect(db_path, timeout=15)
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA busy_timeout=30000")
                conn.execute("PRAGMA temp_store=MEMORY")
                conn.execute("PRAGMA cache_size=-64000")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                if query.strip().lower().startswith("select"):
                    records = cursor.fetchall()
                    conn.close()
                    return "Success", records
                else:
                    conn.commit()
                    conn.close()
                    return "Success", None
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    if time.time() - start_time >= timeout:
                        return f"Failed: Timeout after {timeout} seconds", None
                    time.sleep(0.1)
                else:
                    return f"Failed: {e}", None
            except Exception as e:
                return f"Failed: {e}", None

    results = {}
    for db_path, queries in db_query_pairs:
        db_results = []
        for query in queries:
            with lock:
                result, records = execute_single_query(db_path, query)
            db_results.append((result, records))
        results[db_path] = db_results
    return results

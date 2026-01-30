
# import sqlite3
# import threading
# import time

# class SQLiteManager:
#     def __init__(self):
#         self.connection_lock = threading.Lock()

#     def synchronized(self, lock):
#         def wrapper(f):
#             def wrapped(*args, **kwargs):
#                 with lock:
#                     return f(*args, **kwargs)
#             return wrapped
#         return wrapper

#     @synchronized(connection_lock)
#     def execute_queries(self, db_query_pairs, timeout=20):
#         results = {}
#         for db_path, queries in db_query_pairs:
#             start_time = time.time()
#             while True:
#                 try:
#                     conn = sqlite3.connect(db_path)
#                     cursor = conn.cursor()
#                     db_results = []
#                     for query in queries:
#                         try:
#                             cursor.execute(query)
#                             conn.commit()
#                             db_results.append("Success")
#                         except Exception as e:
#                             db_results.append(f"Failed: {e}")
#                     results[db_path] = db_results
#                     conn.close()
#                     break
#                 except sqlite3.OperationalError as e:
#                     if 'database is locked' in str(e):
#                         elapsed_time = time.time() - start_time
#                         if elapsed_time >= timeout:
#                             results[db_path] = [f"Failed: Timeout after {timeout} seconds"]
#                             break
#                         time.sleep(0.1)  # Small delay before retrying
#                     else:
#                         results[db_path] = [f"Failed: {e}"]
#                         break
#                 except Exception as e:
#                     results[db_path] = [f"Failed: {e}"]
#                     break
#         return results


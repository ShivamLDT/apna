# # sqlite_manager.py

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

#     def execute_queries(self, db_query_pairs, timeout=20):
#         @self.synchronized(self.connection_lock)
#         def execute_single_query(db_path, query):
#             start_time = time.time()
#             while True:
#                 try:
#                     conn = sqlite3.connect(db_path)
#                     ##kartik
#                     conn.execute('PRAGMA journal_mode=WAL')
#                     conn.execute('PRAGMA synchronous=NORMAL')
#                     conn.execute('PRAGMA busy_timeout=30000')  
#                     conn.execute('PRAGMA temp_store=MEMORY')
#                     conn.execute('PRAGMA cache_size=-64000')  
#                     ##kartik
#                     cursor = conn.cursor()
#                     cursor.execute(query)
#                     if query.strip().lower().startswith('select'):
#                         conn.execute("PRAGMA wal_checkpoint(FULL)")
#                         records = cursor.fetchall()
#                         conn.close()
#                         return "Success", records
#                     else:
#                         conn.commit() 
#                         conn.execute("PRAGMA wal_checkpoint(FULL)")
#                         conn.close()
#                         return "Success", None
#                 except sqlite3.OperationalError as e:
#                     if 'database is locked' in str(e):
#                         elapsed_time = time.time() - start_time
#                         if elapsed_time >= timeout:
#                             return f"Failed: Timeout after {timeout} seconds", None
#                         time.sleep(0.1)  # Small delay before retrying
#                     else:
#                         return f"Failed: {e}", None
#                 except Exception as e:
#                     return f"Failed: {e}", None

#         results = {}
#         for db_path, queries in db_query_pairs:
#             db_results = []
#             for query in queries:
#                 result, records = execute_single_query(db_path, query)
#                 db_results.append((result, records))
#             results[db_path] = db_results
#         return results



import sqlite3
import threading
import queue
import time
import logging
import os
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SQLiteManager:
    """
    Thread-safe SQLite connection manager with optimized concurrent access.
    
    Features:
    - Separate read/write connection pools
    - Batched writes for high throughput
    - WAL mode with automatic checkpointing
    - Zero data loss with unlimited queue
    - Retry logic for external database access conflicts
    """
    
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._init()
        self._initialized = True

    def _init(self):
        """Initialize connection pools and worker thread"""
        self._write_queue = queue.Queue(maxsize=0)
        self._write_conns = {}
        
        self._read_conns = {}
        self._read_lock = threading.Lock()
        
        self._checkpoint_interval = 60
        self._last_checkpoint = {}
        
        self._stop_event = threading.Event()
        self._worker = threading.Thread(
            target=self._write_worker,
            name="SQLite-Writer",
            daemon=True
        )
        self._worker.start()
        logger.info("SQLite manager initialized")

    def _get_write_conn(self, db_path: str) -> sqlite3.Connection:
        """
        Get or create write connection with retry logic.
        
        Args:
            db_path: Path to SQLite database file
            
        Returns:
            sqlite3.Connection: Connection configured for WAL mode
            
        Raises:
            sqlite3.OperationalError: If connection fails after retries
        """
        if db_path not in self._write_conns:
            max_retries = 3
            retry_delay = 0.1
            
            for attempt in range(max_retries):
                try:
                    conn = sqlite3.connect(
                        db_path,
                        check_same_thread=False,
                        timeout=30
                    )
                    conn.execute("PRAGMA journal_mode=WAL;")
                    conn.execute("PRAGMA synchronous=NORMAL;")
                    conn.execute("PRAGMA busy_timeout=30000;")
                    conn.execute("PRAGMA temp_store=MEMORY;")
                    conn.execute("PRAGMA cache_size=-64000;")
                    conn.isolation_level = None
                    self._write_conns[db_path] = conn
                    logger.info(f"Write connection established: {db_path}")
                    break
                except sqlite3.OperationalError as e:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Connection retry {attempt + 1}/{max_retries} for {db_path}: {e}"
                        )
                        time.sleep(retry_delay * (2 ** attempt))
                    else:
                        logger.error(f"Failed to connect to {db_path} after {max_retries} attempts")
                        raise
        
        return self._write_conns[db_path]

    def _get_read_conn(self, db_path: str) -> sqlite3.Connection:
        """
        Get or create read-only connection with retry logic.
        
        Args:
            db_path: Path to SQLite database file
            
        Returns:
            sqlite3.Connection: Read-only connection
            
        Raises:
            sqlite3.OperationalError: If connection fails after retries
        """
        uri = f"file:{os.path.abspath(db_path)}?mode=ro"

        with self._read_lock:
            if db_path not in self._read_conns:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        conn = sqlite3.connect(
                            uri,
                            uri=True,
                            check_same_thread=False,
                            timeout=10
                        )
                        conn.execute("PRAGMA query_only=ON;")
                        conn.execute("PRAGMA journal_mode=WAL;")
                        conn.execute("PRAGMA synchronous=NORMAL;")
                        self._read_conns[db_path] = conn
                        logger.info(f"Read connection established: {db_path}")
                        break
                    except sqlite3.OperationalError as e:
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Read connection retry {attempt + 1}/{max_retries} for {db_path}"
                            )
                            time.sleep(0.05 * (2 ** attempt))
                        else:
                            logger.error(f"Failed to create read connection for {db_path}")
                            raise
            return self._read_conns[db_path]

    def _checkpoint_wal(self, db_path: str):
        """
        Perform passive WAL checkpoint to prevent unbounded growth.
        
        Args:
            db_path: Path to database file
        """
        try:
            conn = self._get_write_conn(db_path)
            conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
            logger.debug(f"WAL checkpoint completed: {db_path}")
        except Exception as e:
            logger.warning(f"WAL checkpoint failed for {db_path}: {e}")

    def _flush_batch(self, batch: List[Tuple]):
        """
        Execute batched writes in single transaction per database.
        
        Args:
            batch: List of (db_path, sql, params, result_queue) tuples
        """
        if not batch:
            return
        
        db_batches = {}
        for task in batch:
            db_path = task[0]
            if db_path not in db_batches:
                db_batches[db_path] = []
            db_batches[db_path].append(task)
        
        for db_path, tasks in db_batches.items():
            conn = None
            try:
                conn = self._get_write_conn(db_path)
                conn.execute("BEGIN IMMEDIATE")
                
                for _, sql, params, result_q in tasks:
                    try:
                        cur = conn.cursor()
                        cur.execute(sql, params or ())
                        if result_q:
                            result_q.put(("Success", None))
                    except Exception as e:
                        logger.exception(f"Batch item failed: {sql[:100]}")
                        if result_q:
                            result_q.put(("Failed", str(e)))
                
                conn.commit()
                logger.debug(f"Batch committed: {len(tasks)} operations for {db_path}")
                
                if db_path not in self._last_checkpoint or \
                   (time.time() - self._last_checkpoint.get(db_path, 0)) > self._checkpoint_interval:
                    self._checkpoint_wal(db_path)
                    self._last_checkpoint[db_path] = time.time()
                
            except Exception as e:
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                logger.exception(f"Batch transaction failed for {db_path}")
                for _, _, _, result_q in tasks:
                    if result_q:
                        result_q.put(("Failed", str(e)))

    def _write_worker(self):
        """
        Background worker thread for batched write operations.
        Processes queued writes in batches for optimal performance.
        """
        batch = []
        batch_size = 50
        batch_timeout = 0.05
        last_flush = time.time()
        
        logger.info("Write worker started")
        
        while not self._stop_event.is_set():
            try:
                task = self._write_queue.get(timeout=batch_timeout)
            except queue.Empty:
                if batch and (time.time() - last_flush) >= batch_timeout:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
                continue

            if task is None:
                if batch:
                    self._flush_batch(batch)
                break

            batch.append(task)
            
            if len(batch) >= batch_size or (time.time() - last_flush) >= batch_timeout:
                self._flush_batch(batch)
                batch = []
                last_flush = time.time()
                
            self._write_queue.task_done()
        
        logger.info("Write worker stopped")

    def execute_queries(
        self, 
        db_query_pairs: List[Tuple[str, List[str]]]
    ) -> Dict[str, List[Tuple[str, Any]]]:
        """
        Execute queries with automatic routing to read/write connections.
        
        Args:
            db_query_pairs: List of (db_path, queries) tuples
            
        Returns:
            Dict mapping db_path to list of (status, result) tuples
            
        Example:
            results = manager.execute_queries([
                ('/path/db.sqlite', [
                    'SELECT * FROM users',
                    'INSERT INTO logs VALUES (?, ?)'
                ])
            ])
        """
        results = {}

        for db_path, queries in db_query_pairs:
            db_results = []

            for sql in queries:
                is_select = sql.lstrip().lower().startswith("select")

                if is_select:
                    try:
                        conn = self._get_read_conn(db_path)
                        cur = conn.cursor()
                        cur.execute(sql)
                        rows = cur.fetchall()
                        db_results.append(("Success", rows))
                    except Exception as e:
                        logger.exception(f"Read query failed: {sql[:100]}")
                        db_results.append(("Failed", str(e)))
                else:
                    result_q = queue.Queue()
                    self._write_queue.put((db_path, sql, None, result_q))
                    
                    try:
                        status, error = result_q.get(timeout=30)
                        if status != "Success":
                            logger.error(f"Write query failed: {error}")
                            raise RuntimeError(f"SQLite write failed: {error}")
                        db_results.append(("Success", None))
                    except queue.Empty:
                        logger.error(f"Write query timeout: {sql[:100]}")
                        raise RuntimeError("SQLite write timeout")

            results[db_path] = db_results

        return results

    def shutdown(self, timeout: int = 30):
        """
        Gracefully shutdown manager, ensuring all pending writes complete.
        
        Args:
            timeout: Maximum seconds to wait for queue drain
        """
        pending = self._write_queue.qsize()
        logger.info(f"Shutting down SQLite manager, pending writes: {pending}")
        
        self._stop_event.set()
        self._write_queue.put(None)
        
        start = time.time()
        while not self._write_queue.empty() and (time.time() - start) < timeout:
            time.sleep(0.1)
        
        self._worker.join(timeout=5)
        
        if self._worker.is_alive():
            logger.error("Write worker did not terminate gracefully")
        
        for db_path, conn in self._write_conns.items():
            try:
                conn.execute("PRAGMA optimize;")
                conn.close()
                logger.info(f"Write connection closed: {db_path}")
            except Exception as e:
                logger.error(f"Error closing write connection {db_path}: {e}")

        for db_path, conn in self._read_conns.items():
            try:
                conn.close()
                logger.info(f"Read connection closed: {db_path}")
            except Exception as e:
                logger.error(f"Error closing read connection {db_path}: {e}")
        
        logger.info("SQLite manager shutdown complete")

    def __del__(self):
        """Cleanup on garbage collection"""
        if hasattr(self, '_worker') and self._worker.is_alive():
            self.shutdown(timeout=5)

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


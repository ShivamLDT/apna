
# """
# crypto_middleware.py - Persistent session storage with SQLite
# COMPLETE FIX for hanging/deadlock issues
# """
# import json
# import base64
# import threading
# import sqlite3
# import os
# import queue
# from datetime import datetime, timedelta
# from flask import Request, g, jsonify, current_app, request
# from werkzeug.exceptions import Unauthorized, BadRequest

# from .crypto_utils import (
#     gen_rsa_keypair, rsa_decrypt, aes_encrypt, aes_decrypt,
#     make_key_id, now_ts, SESSION_TTL_SECONDS
# )


# class SessionStore:
#     """
#     Thread-safe persistent session storage using SQLite with WAL mode
#     Uses a dedicated worker thread to serialize all database operations
#     """
    
#     # def __init__(self, db_path='sessions.db'):
#     #     self.db_path = db_path
#     #     self.work_queue = queue.Queue()
#     #     self.stop_event = threading.Event()
#     #     self._init_db()
        
#     #     # Start dedicated worker thread for all DB operations
#     #     self.worker_thread = threading.Thread(target=self._worker, daemon=True)
#     #     self.worker_thread.start()
    
#     # def _init_db(self):
#     #     """Initialize database schema with WAL mode and optimizations"""
#     #     conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
#     #     conn.execute('PRAGMA journal_mode=WAL')
#     #     conn.execute('PRAGMA synchronous=NORMAL')
#     #     conn.execute('PRAGMA busy_timeout=30000')  
#     #     conn.execute('PRAGMA temp_store=MEMORY')
#     #     conn.execute('PRAGMA cache_size=-64000')  
        
#     #     cursor = conn.cursor()
#     #     cursor.execute('''
#     #         CREATE TABLE IF NOT EXISTS sessions (
#     #             key_id TEXT PRIMARY KEY,
#     #             aes_key BLOB NOT NULL,
#     #             expires_at REAL NOT NULL,
#     #             created_at REAL NOT NULL
#     #         )
#     #     ''')
#     #     cursor.execute('''
#     #         CREATE INDEX IF NOT EXISTS idx_expires 
#     #         ON sessions(expires_at)
#     #     ''')
#     #     conn.commit()
#     #     conn.close()
    
#     # def _worker(self):
#     #     """
#     #     Dedicated worker thread that processes all database operations sequentially.
#     #     This eliminates all locking issues by serializing operations.
#     #     """
#     #     # Create a dedicated connection for this worker thread only
#     #     conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None, 
#     #                           check_same_thread=True)
#     #     conn.execute('PRAGMA journal_mode=WAL')
#     #     conn.execute('PRAGMA synchronous=NORMAL')
#     #     conn.execute('PRAGMA busy_timeout=30000')
        
#     #     try:
#     #         while not self.stop_event.is_set():
#     #             try:
#     #                 # Get work item with timeout to allow checking stop_event
#     #                 work_item = self.work_queue.get(timeout=0.5)
#     #                 if work_item is None:  # Poison pill
#     #                     break
                    
#     #                 operation, args, result_queue = work_item
                    
#     #                 try:
#     #                     if operation == 'save':
#     #                         key_id, aes_key, expires_at = args
#     #                         cursor = conn.cursor()
#     #                         cursor.execute('''
#     #                             INSERT OR REPLACE INTO sessions 
#     #                             (key_id, aes_key, expires_at, created_at)
#     #                             VALUES (?, ?, ?, ?)
#     #                         ''', (key_id, aes_key, expires_at, now_ts()))
#     #                         conn.commit()
#     #                         result_queue.put(('success', None))
                        
#     #                     elif operation == 'get':
#     #                         key_id = args[0]
#     #                         cursor = conn.cursor()
#     #                         cursor.execute('''
#     #                             SELECT aes_key, expires_at FROM sessions 
#     #                             WHERE key_id = ?
#     #                         ''', (key_id,))
#     #                         row = cursor.fetchone()
                            
#     #                         if row:
#     #                             aes_key, expires_at = row
#     #                             if expires_at > now_ts():
#     #                                 result_queue.put(('success', {'aes_key': aes_key, 'expires': expires_at}))
#     #                             else:
#     #                                 result_queue.put(('success', None))
#     #                         else:
#     #                             result_queue.put(('success', None))
                        
#     #                     elif operation == 'delete':
#     #                         key_id = args[0]
#     #                         cursor = conn.cursor()
#     #                         cursor.execute('DELETE FROM sessions WHERE key_id = ?', (key_id,))
#     #                         conn.commit()
#     #                         result_queue.put(('success', None))
                        
#     #                     elif operation == 'cleanup':
#     #                         cursor = conn.cursor()
#     #                         deleted = cursor.execute(
#     #                             'DELETE FROM sessions WHERE expires_at < ?',
#     #                             (now_ts(),)
#     #                         ).rowcount
#     #                         conn.commit()
#     #                         result_queue.put(('success', deleted))
                        
#     #                     elif operation == 'count':
#     #                         cursor = conn.cursor()
#     #                         cursor.execute('SELECT COUNT(*) FROM sessions WHERE expires_at > ?', (now_ts(),))
#     #                         count = cursor.fetchone()[0]
#     #                         result_queue.put(('success', count))
                    
#     #                 except Exception as e:
#     #                     result_queue.put(('error', str(e)))
                    
#     #                 finally:
#     #                     self.work_queue.task_done()
                
#     #             except queue.Empty:
#     #                 continue
        
#     #     finally:
#     #         conn.close()
    
#     # def _execute(self, operation, *args, timeout=5.0):
#     #     """Execute database operation via worker thread"""
#     #     result_queue = queue.Queue()
#     #     self.work_queue.put((operation, args, result_queue))
        
#     #     try:
#     #         status, result = result_queue.get(timeout=timeout)
#     #         if status == 'error':
#     #             raise Exception(f"Database operation failed: {result}")
#     #         return result
#     #     except queue.Empty:
#     #         raise TimeoutError(f"Database operation '{operation}' timed out after {timeout}s")
    
#     # def save_session(self, key_id, aes_key, expires_at):
#     #     """Save session to database"""
#     #     return self._execute('save', key_id, aes_key, expires_at)
    
#     # def get_session(self, key_id):
#     #     """Retrieve session from database"""
#     #     return self._execute('get', key_id)
    
#     # def delete_session(self, key_id):
#     #     """Delete session from database"""
#     #     return self._execute('delete', key_id)
    
#     # def cleanup_expired(self):
#     #     """Remove expired sessions"""
#     #     return self._execute('cleanup', timeout=30.0)
    
#     # def get_session_count(self):
#     #     """Get total number of active sessions"""
#     #     return self._execute('count')
    
#     # def shutdown(self):
#     #     """Gracefully shutdown the worker thread"""
#     #     self.stop_event.set()
#     #     self.work_queue.put(None)  # Poison pill
#     #     self.worker_thread.join(timeout=5)


#     def __init__(self, db_path='sessions.db', read_pool_size=10):
#         self.db_path = db_path
#         self.read_pool_size = read_pool_size
#         self.write_queue = queue.Queue()
#         self.stop_event = threading.Event()
#         self.read_pool = queue.Queue(maxsize=read_pool_size)
        
#         self._init_db()
#         self._init_read_pool()
        
#         # Dedicated writer thread
#         self.writer_thread = threading.Thread(target=self._writer_worker, daemon=True)
#         self.writer_thread.start()
    
#     def _init_db(self):
#         """Initialize database schema with WAL mode"""
#         conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
#         conn.execute('PRAGMA journal_mode=WAL')
#         conn.execute('PRAGMA synchronous=NORMAL')
#         conn.execute('PRAGMA busy_timeout=30000')
#         conn.execute('PRAGMA temp_store=MEMORY')
#         conn.execute('PRAGMA cache_size=-64000')
        
#         cursor = conn.cursor()
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS sessions (
#                 key_id TEXT PRIMARY KEY,
#                 aes_key BLOB NOT NULL,
#                 expires_at REAL NOT NULL,
#                 created_at REAL NOT NULL
#             )
#         ''')
#         cursor.execute('''
#             CREATE INDEX IF NOT EXISTS idx_expires 
#             ON sessions(expires_at)
#         ''')
#         conn.commit()
#         conn.close()
    
#     def _init_read_pool(self):
#         """Create pool of read-only connections"""
#         for _ in range(self.read_pool_size):
#             conn = sqlite3.connect(
#                 f'file:{self.db_path}?mode=ro', 
#                 uri=True,
#                 timeout=5,
#                 check_same_thread=False
#             )
#             conn.execute('PRAGMA query_only=ON')
#             self.read_pool.put(conn)
    
#     def _get_read_conn(self, timeout=2.0):
#         """Get connection from pool"""
#         try:
#             return self.read_pool.get(timeout=timeout)
#         except queue.Empty:
#             raise TimeoutError("Read connection pool exhausted")
    
#     def _return_read_conn(self, conn):
#         """Return connection to pool"""
#         try:
#             self.read_pool.put_nowait(conn)
#         except queue.Full:
#             conn.close()
    
#     def _writer_worker(self):
#         """Dedicated writer thread for all write operations"""
#         conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
#         conn.execute('PRAGMA journal_mode=WAL')
#         conn.execute('PRAGMA synchronous=NORMAL')
        
#         try:
#             while not self.stop_event.is_set():
#                 try:
#                     work_item = self.write_queue.get(timeout=0.5)
#                     if work_item is None:
#                         break
                    
#                     operation, args, result_queue = work_item
                    
#                     try:
#                         if operation == 'save':
#                             key_id, aes_key, expires_at = args
#                             cursor = conn.cursor()
#                             cursor.execute('''
#                                 INSERT OR REPLACE INTO sessions 
#                                 (key_id, aes_key, expires_at, created_at)
#                                 VALUES (?, ?, ?, ?)
#                             ''', (key_id, aes_key, expires_at, now_ts()))
#                             conn.commit()
#                             conn.execute('PRAGMA wal_checkpoint(PASSIVE)')
#                             result_queue.put(('success', None))
                        
#                         elif operation == 'delete':
#                             key_id = args[0]
#                             cursor = conn.cursor()
#                             cursor.execute('DELETE FROM sessions WHERE key_id = ?', (key_id,))
#                             conn.commit()
#                             result_queue.put(('success', None))
                        
#                         elif operation == 'cleanup':
#                             cursor = conn.cursor()
#                             deleted = cursor.execute(
#                                 'DELETE FROM sessions WHERE expires_at < ?',
#                                 (now_ts(),)
#                             ).rowcount
#                             conn.commit()
#                             result_queue.put(('success', deleted))
                    
#                     except Exception as e:
#                         result_queue.put(('error', str(e)))
                    
#                     finally:
#                         self.write_queue.task_done()
                
#                 except queue.Empty:
#                     continue
        
#         finally:
#             conn.close()
    
#     def _execute_write(self, operation, *args, timeout=5.0):
#         """Execute write operation via writer thread"""
#         result_queue = queue.Queue()
#         self.write_queue.put((operation, args, result_queue))
        
#         try:
#             status, result = result_queue.get(timeout=timeout)
#             if status == 'error':
#                 raise Exception(f"Write operation failed: {result}")
#             return result
#         except queue.Empty:
#             raise TimeoutError(f"Write operation '{operation}' timed out")
    
#     def save_session(self, key_id, aes_key, expires_at):
#         """Save session (write operation)"""
#         return self._execute_write('save', key_id, aes_key, expires_at)
    
#     def get_session(self, key_id):
#         """Retrieve session (direct read from pool)"""
#         conn = self._get_read_conn()
#         try:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 SELECT aes_key, expires_at FROM sessions 
#                 WHERE key_id = ?
#             ''', (key_id,))
#             row = cursor.fetchone()
            
#             if row:
#                 aes_key, expires_at = row
#                 if expires_at > now_ts():
#                     return {'aes_key': aes_key, 'expires': expires_at}
#             return None
#         finally:
#             self._return_read_conn(conn)
    
#     def delete_session(self, key_id):
#         """Delete session (write operation)"""
#         return self._execute_write('delete', key_id)
    
#     def cleanup_expired(self):
#         """Remove expired sessions (write operation)"""
#         return self._execute_write('cleanup', timeout=30.0)
    
#     def get_session_count(self):
#         """Get active session count (direct read)"""
#         conn = self._get_read_conn()
#         try:
#             cursor = conn.cursor()
#             cursor.execute('SELECT COUNT(*) FROM sessions WHERE expires_at > ?', (now_ts(),))
#             return cursor.fetchone()[0]
#         finally:
#             self._return_read_conn(conn)
    
#     def shutdown(self):
#         """Gracefully shutdown"""
#         self.stop_event.set()
#         self.write_queue.put(None)
#         self.writer_thread.join(timeout=5)
        
#         # Close all pooled connections
#         while not self.read_pool.empty():
#             try:
#                 conn = self.read_pool.get_nowait()
#                 conn.close()
#             except queue.Empty:
#                 break


# class CryptoRequest(Request):
#     """Custom request class that decrypts body and headers on access."""

#     _decrypted_body = None
#     _decryption_attempted = False

#     def _ensure_decrypted(self):
#         """Decrypt request body and headers if needed."""
#         if self._decryption_attempted:
#             return

#         self._decryption_attempted = True

#         if (self.method == "OPTIONS" or
#             self.path.startswith("/handshake") or
#             self.path.startswith("/v1/") or 
#             self.path.startswith("/socket.io") or
#             "socket.io" in self.path.lower() or ":7777" in self.path.lower() or
#             self.headers.get("Upgrade") == "websocket"):
#             self._decrypted_body = super().get_data(cache=True)
#             try:
#                 self._cached_json = json.loads(self._decrypted_body.decode())
#             except Exception:
#                 self._cached_json = None
#             return

#         key_id = self.headers.get("X-Key-Id")
        
#         if not key_id:
#             self._decrypted_body = super().get_data(cache=True)
#             try:
#                 self._cached_json = json.loads(self._decrypted_body.decode())
#             except Exception:
#                 self._cached_json = None
#             return

#         session_store = current_app.config.get("SESSION_STORE")
#         session = session_store.get_session(key_id) if session_store else None

#         if not session:
#             self._decrypted_body = b""
#             g.crypto_error = "invalid_or_expired_key"
#             g.key_id = None
#             return

#         if session["expires"] < now_ts():
#             self._decrypted_body = b""
#             g.crypto_error = "session_expired"
#             g.key_id = None
#             return

#         aes_key = session["aes_key"]

#         raw = super().get_data(cache=True)
#         if raw:
#             try:
#                 payload = json.loads(raw)
#                 tag_b64 = payload.get("tag")
#                 plaintext = aes_decrypt(
#                     aes_key, 
#                     payload["iv"], 
#                     payload["ct"], 
#                     tag_b64
#                 )
#                 # self._decrypted_body = plaintext
#                 try:
#                     decrypted_data = json.loads(plaintext.decode())
#                     # import time
#                     # current_time_abs = time.time()
#                     # print("=====================.....................>>>>>>>>>>>",current_time_abs - decrypted_data['time'])
#                     # if decrypted_data.get('time',None):
                        
#                     #     # if not (decrypted_data['time'] < current_time_abs) or (abs(current_time_abs - decrypted_data['time']) > 60): 
#                     #     if  (abs(current_time_abs - decrypted_data['time']) > 5): 
#                     #         decrypted_data=None
#                     #         plaintext=None
#                     #         self._decrypted_body = None
#                     #         #return  jsonify({"error": "Tampering detected"}), 500
#                     # else:
#                     #         decrypted_data=None
#                     #         plaintext=None
#                     #         self._decrypted_body = None
#                     #         # #return  jsonify({"error": "Tampering detected"}), 500
#                     self._cached_json = decrypted_data
#                 except Exception:
#                     self._cached_json = None

#                 self._decrypted_body = plaintext

#             except Exception as e:
#                 current_app.logger.error(f"Body decryption failed: {e}")
#                 self._decrypted_body = b""
#                 g.crypto_error = "decryption_failed"
#                 g.key_id = None
#                 return
#         else:
#             self._decrypted_body = b""

#         g.key_id = key_id

#     @property
#     def json(self):
#         """Return decrypted JSON body if available."""
#         self._ensure_decrypted()
#         return getattr(self, "_cached_json", None)

#     def get_data(self, cache=True, as_text=False, parse_form_data=False):
#         """Get decrypted request data."""
#         self._ensure_decrypted()
#         if as_text:
#             return self._decrypted_body.decode("utf-8")
#         return self._decrypted_body


# def cleanup_task(app):
#     """Background task to cleanup expired sessions and handshakes"""
#     import time
#     while True:
#         time.sleep(60)
#         try:
#             # Clean RSA handshakes
#             with app.config["_CRYPTO_LOCK"]:
#                 rsa_handshakes = app.config.get("RSA_HANDSHAKES", {})
#                 current_time = now_ts()
#                 expired_rsa = [
#                     kid for kid, hs in rsa_handshakes.items()
#                     if current_time - hs["created"] > 120
#                 ]
#                 for kid in expired_rsa:
#                     del rsa_handshakes[kid]
            
#             # Clean expired sessions
#             session_store = app.config.get("SESSION_STORE")
#             if session_store:
#                 deleted = session_store.cleanup_expired()
#                 active = session_store.get_session_count()
#                 if deleted > 0:
#                     app.logger.info(
#                         f"Cleanup: removed {deleted} expired sessions, "
#                         f"{active} active sessions"
#                     )
#         except Exception as e:
#             app.logger.error(f"Cleanup task error: {e}")


# def init_crypto(app, db_path='sessions.db'):
#     """Install ephemeral crypto middleware and handshake endpoints."""
#     app.request_class = CryptoRequest

#     app.config.setdefault("RSA_HANDSHAKES", {})
#     app.config.setdefault("_CRYPTO_LOCK", threading.Lock())
#     app.config["SESSION_STORE"] = SessionStore(db_path)

#     cleanup_thread = threading.Thread(target=cleanup_task, args=(app,), daemon=True)
#     cleanup_thread.start()
#     app.logger.info(f"Persistent session storage initialized at {db_path} (WAL mode)")

#     @app.before_request
#     def check_crypto_errors():
#         """Check for crypto errors after decryption attempt."""
#         if hasattr(g, 'crypto_error'):
#             error = g.crypto_error
#             if error == "invalid_or_expired_key":
#                 return jsonify({"error": "invalid_or_expired_key"}), 401
#             elif error == "session_expired":
#                 return jsonify({"error": "session_expired"}), 401
#             elif error == "decryption_failed":
#                 return jsonify({"error": "decryption_failed"}), 400

#     @app.route("/handshake", methods=["GET"])
#     def handshake_get():
#         """Initiate handshake - return RSA public key."""
#         priv_pem, pub_pem = gen_rsa_keypair()
#         key_id = make_key_id()
#         with app.config["_CRYPTO_LOCK"]:
#             app.config["RSA_HANDSHAKES"][key_id] = {
#                 "priv_pem": priv_pem,
#                 "pub_pem": pub_pem,
#                 "created": now_ts(),
#             }
#         return jsonify({"key_id": key_id, "pub_pem": pub_pem.decode()})

#     @app.route("/handshake/confirm", methods=["POST"])
#     def handshake_confirm():
#         """Confirm handshake - establish AES session."""
#         app.logger.info("handshake_confirm called")
        
#         try:
#             data = request.get_json(force=True, silent=True)
#         except Exception as e:
#             app.logger.error(f"handshake_confirm: JSON parse error: {e}")
#             return jsonify({"error": "invalid json"}), 400

#         if not data:
#             app.logger.warning("handshake_confirm: missing JSON body")
#             return jsonify({"error": "missing json body"}), 400

#         key_id, enc_aes_b64 = data.get("key_id"), data.get("enc_aes_b64")
#         if not key_id or not enc_aes_b64:
#             app.logger.warning(f"handshake_confirm: missing fields (key_id={key_id})")
#             return jsonify({"error": "missing fields"}), 400

#         # Atomically fetch and remove handshake
#         with app.config["_CRYPTO_LOCK"]:
#             handshake = app.config["RSA_HANDSHAKES"].pop(key_id, None)

#         if not handshake:
#             app.logger.warning(f"handshake_confirm: invalid_or_expired_handshake for key_id={key_id}")
#             return jsonify({"error": "invalid_or_expired_handshake"}), 400

#         # Decrypt AES key (expensive operation done without any locks)
#         try:
#             aes_key = rsa_decrypt(handshake["priv_pem"], enc_aes_b64)
#             app.logger.info(f"handshake_confirm: AES key decrypted for key_id={key_id}")
#         except Exception as e:
#             app.logger.error(f"handshake_confirm: RSA decrypt error for key_id={key_id}: {e}")
#             return jsonify({"error": "decrypt_failed"}), 400

#         # Save AES session (worker thread handles DB operation)
#         try:
#             expires = now_ts() + SESSION_TTL_SECONDS
#             session_store = app.config["SESSION_STORE"]
#             session_store.save_session(key_id, aes_key, expires)
#             app.logger.info(f"handshake_confirm SUCCESS: session saved (key_id={key_id})")

#             return jsonify({
#                 "ok": True,
#                 "key_id": key_id,
#                 "ttl": SESSION_TTL_SECONDS
#             })
#         except TimeoutError as e:
#             app.logger.error(f"handshake_confirm: database timeout for key_id={key_id}: {e}")
#             return jsonify({"error": "database_timeout"}), 503
#         except Exception as e:
#             app.logger.error(f"handshake_confirm: failed to save session for key_id={key_id}: {e}")
#             return jsonify({"error": "session_save_failed"}), 500

#     @app.route("/handshake/check-key", methods=["POST"])
#     def check_key():
#         """Check if the key_id exists and is still valid."""
#         data = request.get_json(force=True, silent=True)
#         if not data or "key_id" not in data:
#             return jsonify({"error": "missing key_id"}), 400

#         key_id = data["key_id"]
#         try:
#             session_store = app.config["SESSION_STORE"]
#             sess = session_store.get_session(key_id)

#             if not sess:
#                 return jsonify({"error": "invalid_or_expired_key"}), 401

#             if sess["expires"] < now_ts():
#                 return jsonify({"error": "session_expired"}), 401

#             return jsonify({"ok": True, "ttl": sess["expires"] - now_ts()})
#         except Exception as e:
#             app.logger.error(f"check_key error: {e}")
#             return jsonify({"error": "database_error"}), 500

#     @app.route("/handshake/stats", methods=["GET"])
#     def session_stats():
#         """Get session statistics"""
#         try:
#             session_store = app.config["SESSION_STORE"]
#             active = session_store.get_session_count()
#             pending = len(app.config.get("RSA_HANDSHAKES", {}))
#             return jsonify({
#                 "active_sessions": active,
#                 "pending_handshakes": pending
#             })
#         except Exception as e:
#             app.logger.error(f"session_stats error: {e}")
#             return jsonify({"error": "database_error"}), 500

#     @app.after_request
#     def encrypt_outgoing(resp):
#         """Encrypt JSON responses for encrypted sessions."""
#         if (request.path in ['/handshake'] or
#             request.path.startswith('/handshake/') or 
#             request.path.startswith('/socket.io') or
#             request.method == 'OPTIONS'  or
#             'socket.io' in request.path.lower() or ":7777" in request.path.lower() or
#             request.headers.get('Upgrade') == 'websocket'):
#             return resp

#         key_id = getattr(g, "key_id", None) or request.headers.get("X-Key-Id")
        
#         if not key_id:
#             return resp

#         content_type = resp.headers.get("Content-Type", "")
#         # print(f"{request.path}and{content_type}")
#         # if "application/json" not in content_type.lower():
#         #     return resp

#         # if resp.status_code >= 400:
#         #     return resp

#         try:
#             session_store = app.config["SESSION_STORE"]
#             sess = session_store.get_session(key_id)

#             if not sess:
#                 return jsonify({"error": "session_expired"}), 401

#             enc = aes_encrypt(sess["aes_key"], resp.get_data())
#             new_body = json.dumps(enc).encode()
#             resp.set_data(new_body)
#             resp.headers["Content-Type"] = content_type #"application/json"
#             resp.headers["Content-Length"] = str(len(new_body))
#         except Exception as e:
#             app.logger.error(f"Response encryption failed: {e}")

#         return resp


"""
crypto_middleware.py - Persistent session storage with async SQLite
Complete implementation with proper async/sync bridge for Flask
"""
import json
import threading
import asyncio
from contextlib import asynccontextmanager
from flask import Request, g, jsonify, current_app, request
from werkzeug.exceptions import Unauthorized, BadRequest

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

from .crypto_utils import (
    gen_rsa_keypair, rsa_decrypt, aes_encrypt, aes_decrypt,
    make_key_id, now_ts, SESSION_TTL_SECONDS
)


def _use_mssql_session_store():
    """Check if MSSQL-based SessionStore should be used."""
    try:
        from FlaskWebProject3.db_config import USE_MSSQL
        return USE_MSSQL
    except ImportError:
        return False


class SessionStore:
    """
    Async persistent session storage.
    Uses MSSQL + SQLAlchemy async when USE_MSSQL is True, else aiosqlite.
    """
    
    def __init__(self, db_path='sessions.db', max_connections=20):
        """
        Initialize async session store.
        
        Args:
            db_path: Path to SQLite database file (used when USE_MSSQL=False)
            max_connections: Maximum concurrent database connections
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self._connection_semaphore = None
        self._initialized = False
        self._loop = None
        self._loop_thread = None
        self._use_mssql = _use_mssql_session_store()
        self._async_engine = None
        self._async_session_factory = None
        self._start_event_loop()
    
    def _start_event_loop(self):
        """Start dedicated event loop in background thread."""
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._run_event_loop,
            daemon=True,
            name="SessionStore-EventLoop"
        )
        self._loop_thread.start()
    
    def _run_event_loop(self):
        """Run the event loop in dedicated thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _run_async(self, coro, timeout=10.0):
        """
        Execute async coroutine from sync context.
        
        Args:
            coro: Coroutine to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Result of the coroutine
        """
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)
    
    async def _init_db_mssql(self):
        """Initialize MSSQL schema for sessions via SQLAlchemy async."""
        if self._async_engine is None:
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy.ext.asyncio import async_sessionmaker
            from FlaskWebProject3.db_config import ASYNC_DATABASE_URL, ASYNC_POOL_SIZE, ASYNC_MAX_OVERFLOW
            from FlaskWebProject3.models import Base, CryptoSession
            
            self._async_engine = create_async_engine(
                ASYNC_DATABASE_URL,
                pool_size=ASYNC_POOL_SIZE,
                max_overflow=ASYNC_MAX_OVERFLOW,
                pool_pre_ping=True,
            )
            self._async_session_factory = async_sessionmaker(
                self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            async with self._async_engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))
        self._initialized = True
    
    async def _init_db_sqlite(self):
        """Initialize SQLite schema with WAL mode."""
        if not aiosqlite:
            raise ImportError("aiosqlite is required when USE_MSSQL=False. pip install aiosqlite")
        if self._connection_semaphore is None:
            self._connection_semaphore = asyncio.Semaphore(self.max_connections)
            
        async with aiosqlite.connect(self.db_path, timeout=30.0) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            await conn.execute('PRAGMA synchronous=NORMAL')
            await conn.execute('PRAGMA busy_timeout=5000')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    key_id TEXT PRIMARY KEY,
                    aes_key BLOB NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL
                )
            ''')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_expires ON sessions(expires_at)')
            await conn.commit()
        self._initialized = True
    
    async def _init_db(self):
        """Initialize database schema."""
        if self._initialized:
            return
        if self._use_mssql:
            await self._init_db_mssql()
        else:
            await self._init_db_sqlite()
    
    @asynccontextmanager
    async def _get_mssql_session(self):
        """Context manager for MSSQL AsyncSession."""
        if self._connection_semaphore is None:
            self._connection_semaphore = asyncio.Semaphore(self.max_connections)
        async with self._connection_semaphore:
            async with self._async_session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get write connection (MSSQL or SQLite)."""
        if self._use_mssql:
            async with self._get_mssql_session() as session:
                yield session
        else:
            if self._connection_semaphore is None:
                self._connection_semaphore = asyncio.Semaphore(self.max_connections)
            async with self._connection_semaphore:
                async with aiosqlite.connect(
                    self.db_path, timeout=10.0, isolation_level=None
                ) as conn:
                    await conn.execute('PRAGMA journal_mode=WAL')
                    await conn.execute('PRAGMA synchronous=NORMAL')
                    yield conn
    
    @asynccontextmanager
    async def _get_read_connection(self):
        """Get read-only connection."""
        if self._use_mssql:
            async with self._get_mssql_session() as session:
                yield session
        else:
            async with aiosqlite.connect(
                f"file:{self.db_path}?mode=ro", uri=True, timeout=3.0
            ) as conn:
                await conn.execute('PRAGMA query_only=ON')
                yield conn

    async def save_session(self, key_id, aes_key, expires_at):
        """Save session to database asynchronously."""
        await self._init_db()
        created = now_ts()
        
        if self._use_mssql:
            from FlaskWebProject3.models import CryptoSession
            async with self._get_mssql_session() as session:
                sess = CryptoSession(
                    key_id=key_id,
                    aes_key=aes_key,
                    expires_at=expires_at,
                    created_at=created,
                )
                await session.merge(sess)
        else:
            async with self._get_connection() as conn:
                await conn.execute(
                    'INSERT OR REPLACE INTO sessions (key_id, aes_key, expires_at, created_at) VALUES (?, ?, ?, ?)',
                    (key_id, aes_key, expires_at, created)
                )
                await conn.commit()
    
    async def get_session(self, key_id):
        """Retrieve session from database."""
        await self._init_db()
        
        if self._use_mssql:
            from sqlalchemy import select
            from FlaskWebProject3.models import CryptoSession
            
            try:
                async with self._get_mssql_session() as session:
                    result = await session.execute(
                        select(CryptoSession.aes_key, CryptoSession.expires_at).where(
                            CryptoSession.key_id == key_id
                        )
                    )
                    row = result.first()
                    if row:
                        aes_key, expires_at = row
                        if expires_at > now_ts():
                            return {'aes_key': aes_key, 'expires': expires_at}
                    return None
            except Exception as e:
                if 'unable to open' in str(e).lower() or 'connect' in str(e).lower():
                    await self._init_db()
                    return await self.get_session(key_id)
                raise
        else:
            try:
                async with self._get_read_connection() as conn:
                    async with conn.execute(
                        'SELECT aes_key, expires_at FROM sessions WHERE key_id = ?',
                        (key_id,)
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            aes_key, expires_at = row[0], row[1]
                            if expires_at > now_ts():
                                return {'aes_key': aes_key, 'expires': expires_at}
                return None
            except Exception as e:
                if aiosqlite and isinstance(e, aiosqlite.OperationalError):
                    if 'unable to open database' in str(e).lower():
                        await self._init_db()
                        return await self.get_session(key_id)
                raise
    
    async def delete_session(self, key_id):
        """Delete session from database."""
        await self._init_db()
        
        if self._use_mssql:
            from sqlalchemy import delete
            from FlaskWebProject3.models import CryptoSession
            
            async with self._get_mssql_session() as session:
                await session.execute(delete(CryptoSession).where(CryptoSession.key_id == key_id))
        else:
            async with self._get_connection() as conn:
                await conn.execute('DELETE FROM sessions WHERE key_id = ?', (key_id,))
                await conn.commit()

    async def extend_session(self, key_id, new_expires_at):
        """Extend session expiration (sliding expiration)."""
        await self._init_db()
        
        if self._use_mssql:
            from sqlalchemy import update, and_
            from FlaskWebProject3.models import CryptoSession
            
            async with self._get_mssql_session() as session:
                await session.execute(
                    update(CryptoSession)
                    .where(and_(
                        CryptoSession.key_id == key_id,
                        CryptoSession.expires_at > now_ts()
                    ))
                    .values(expires_at=new_expires_at)
                )
        else:
            async with self._get_connection() as conn:
                await conn.execute(
                    'UPDATE sessions SET expires_at = ? WHERE key_id = ? AND expires_at > ?',
                    (new_expires_at, key_id, now_ts())
                )
                await conn.commit()
    
    async def cleanup_expired(self):
        """Remove expired sessions. Returns number deleted."""
        await self._init_db()
        
        if self._use_mssql:
            from sqlalchemy import delete, func
            from FlaskWebProject3.models import CryptoSession
            
            async with self._get_mssql_session() as session:
                result = await session.execute(delete(CryptoSession).where(CryptoSession.expires_at < now_ts()))
                return result.rowcount
        else:
            async with self._get_connection() as conn:
                cursor = await conn.execute(
                    'DELETE FROM sessions WHERE expires_at < ?', (now_ts(),)
                )
                deleted = cursor.rowcount
                await conn.commit()
                return deleted
    
    async def get_session_count(self):
        """Get count of active (non-expired) sessions."""
        await self._init_db()
        
        if self._use_mssql:
            from sqlalchemy import select, func
            from FlaskWebProject3.models import CryptoSession
            
            try:
                async with self._get_mssql_session() as session:
                    result = await session.execute(
                        select(func.count()).select_from(CryptoSession).where(
                            CryptoSession.expires_at > now_ts()
                        )
                    )
                    return result.scalar() or 0
            except Exception as e:
                if 'unable to open' in str(e).lower() or 'connect' in str(e).lower():
                    await self._init_db()
                    return await self.get_session_count()
                raise
        else:
            try:
                async with self._get_read_connection() as conn:
                    cursor = await conn.execute(
                        'SELECT COUNT(*) FROM sessions WHERE expires_at > ?',
                        (now_ts(),)
                    )
                    row = await cursor.fetchone()
                    return row[0] if row else 0
            except Exception as e:
                if aiosqlite and isinstance(e, aiosqlite.OperationalError):
                    if 'unable to open database' in str(e).lower():
                        await self._init_db()
                        return await self.get_session_count()
                raise
    
    def save_session_sync(self, key_id, aes_key, expires_at):
        """
        Synchronous wrapper for save_session.
        Safe to call from Flask routes.
        """
        return self._run_async(self.save_session(key_id, aes_key, expires_at))
    
    def get_session_sync(self, key_id):
        """
        Synchronous wrapper for get_session.
        Safe to call from Flask routes.
        
        Returns:
            dict with 'aes_key' and 'expires' keys, or None if not found/expired
        """
        return self._run_async(self.get_session(key_id))
    
    def delete_session_sync(self, key_id):
        """
        Synchronous wrapper for delete_session.
        Safe to call from Flask routes.
        """
        return self._run_async(self.delete_session(key_id))
    
    def extend_session_sync(self, key_id, new_expires_at):
        """Synchronous wrapper for extend_session. Extends session expiration (sliding)."""
        return self._run_async(self.extend_session(key_id, new_expires_at), timeout=5.0)

    def cleanup_expired_sync(self):
        """
        Synchronous wrapper for cleanup_expired.
        Safe to call from Flask routes.
        
        Returns:
            int: Number of deleted sessions
        """
        return self._run_async(self.cleanup_expired(), timeout=30.0)
    
    def get_session_count_sync(self):
        """
        Synchronous wrapper for get_session_count.
        Safe to call from Flask routes.
        
        Returns:
            int: Count of active sessions
        """
        return self._run_async(self.get_session_count())
    
    def shutdown(self):
        """Gracefully shutdown the event loop."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._loop_thread:
            self._loop_thread.join(timeout=5.0)


class CryptoRequest(Request):
    """Custom request class that decrypts body and headers on access."""

    _decrypted_body = None
    _decryption_attempted = False

    def _ensure_decrypted(self):
        """Decrypt request body and headers if needed."""
        if self._decryption_attempted:
            return

        self._decryption_attempted = True

        if (self.method == "OPTIONS" or
            self.path.startswith("/handshake") or
            self.path.startswith("/v1/") or 
            self.path.startswith("/socket.io") or
            "socket.io" in self.path.lower() or ":7777" in self.path.lower() or
            self.headers.get("Upgrade") == "websocket"):
            self._decrypted_body = super().get_data(cache=True)
            try:
                self._cached_json = json.loads(self._decrypted_body.decode())
            except Exception:
                self._cached_json = None
            return

        key_id = self.headers.get("X-Key-Id")
        
        if not key_id:
            self._decrypted_body = super().get_data(cache=True)
            try:
                self._cached_json = json.loads(self._decrypted_body.decode())
            except Exception:
                self._cached_json = None
            return

        # GET requests typically have no body, handle them gracefully
        raw = super().get_data(cache=True)
        if not raw:
            self._decrypted_body = b""
            self._cached_json = None
            g.key_id = key_id  # Still set key_id for response encryption
            return

        session_store = current_app.config.get("SESSION_STORE")
        session = session_store.get_session_sync(key_id) if session_store else None

        if not session:
            self._decrypted_body = b""
            g.crypto_error = "invalid_or_expired_key"
            g.key_id = None
            return

        if session["expires"] < now_ts():
            self._decrypted_body = b""
            g.crypto_error = "session_expired"
            g.key_id = None
            return

        aes_key = session["aes_key"]

        raw = super().get_data(cache=True)
        if raw:
            try:
                payload = json.loads(raw)
                tag_b64 = payload.get("tag")
                plaintext = aes_decrypt(
                    aes_key, 
                    payload["iv"], 
                    payload["ct"], 
                    tag_b64
                )
                try:
                    decrypted_data = json.loads(plaintext.decode())
                    self._cached_json = decrypted_data
                except Exception:
                    self._cached_json = None

                self._decrypted_body = plaintext
                # Sliding expiration: extend session on each successful decrypt so active users stay alive
                try:
                    new_expires = now_ts() + SESSION_TTL_SECONDS
                    session_store.extend_session_sync(key_id, new_expires)
                except Exception:
                    pass

            except Exception as e:
                current_app.logger.error(f"Body decryption failed: {e}")
                self._decrypted_body = b""
                g.crypto_error = "decryption_failed"
                g.key_id = None
                return
        else:
            self._decrypted_body = b""

        g.key_id = key_id

    @property
    def json(self):
        """Return decrypted JSON body if available."""
        self._ensure_decrypted()
        return getattr(self, "_cached_json", None)

    def get_data(self, cache=True, as_text=False, parse_form_data=False):
        """Get decrypted request data."""
        self._ensure_decrypted()
        if as_text:
            return self._decrypted_body.decode("utf-8")
        return self._decrypted_body


def cleanup_task(app):
    """Background task to cleanup expired sessions and handshakes"""
    import time
    while True:
        time.sleep(60)
        try:
            with app.config["_CRYPTO_LOCK"]:
                rsa_handshakes = app.config.get("RSA_HANDSHAKES", {})
                current_time = now_ts()
                expired_rsa = [
                    kid for kid, hs in rsa_handshakes.items()
                    if current_time - hs["created"] > 120
                ]
                for kid in expired_rsa:
                    del rsa_handshakes[kid]
            
            session_store = app.config.get("SESSION_STORE")
            if session_store:
                deleted = session_store.cleanup_expired_sync()
                active = session_store.get_session_count_sync()
                if deleted > 0:
                    app.logger.info(
                        f"Cleanup: removed {deleted} expired sessions, "
                        f"{active} active sessions"
                    )
        except Exception as e:
            app.logger.error(f"Cleanup task error: {e}")


def init_crypto(app, db_path='sessions.db'):
    """Install ephemeral crypto middleware and handshake endpoints."""
    app.request_class = CryptoRequest

    app.config.setdefault("RSA_HANDSHAKES", {})
    app.config.setdefault("_CRYPTO_LOCK", threading.Lock())
    app.config["SESSION_STORE"] = SessionStore(db_path)

    cleanup_thread = threading.Thread(target=cleanup_task, args=(app,), daemon=True)
    cleanup_thread.start()
    app.logger.info(f"Persistent session storage initialized at {db_path} (WAL mode)")

    @app.before_request
    def check_crypto_errors():
        """Trigger decryption for encrypted requests, then check for crypto errors."""
        # Force decryption before view runs so g.crypto_error is set (avoids 500 from request.json.get on None)
        key_id = request.headers.get("X-Key-Id")
        if key_id and request.method == "POST" and request.get_data():
            try:
                _ = request.json  # triggers _ensure_decrypted
            except Exception:
                pass
        if hasattr(g, 'crypto_error'):
            error = g.crypto_error
            if error == "invalid_or_expired_key":
                return jsonify({"error": "invalid_or_expired_key"}), 401
            elif error == "session_expired":
                return jsonify({"error": "session_expired"}), 401
            elif error == "decryption_failed":
                return jsonify({"error": "decryption_failed"}), 400

    @app.route("/handshake", methods=["GET"])
    def handshake_get():
        """Initiate handshake - return RSA public key."""
        priv_pem, pub_pem = gen_rsa_keypair()
        key_id = make_key_id()
        with app.config["_CRYPTO_LOCK"]:
            app.config["RSA_HANDSHAKES"][key_id] = {
                "priv_pem": priv_pem,
                "pub_pem": pub_pem,
                "created": now_ts(),
            }
        return jsonify({"key_id": key_id, "pub_pem": pub_pem.decode()})

    @app.route("/handshake/confirm", methods=["POST"])
    def handshake_confirm():
        """Confirm handshake - establish AES session."""
        app.logger.info("handshake_confirm called")
        
        try:
            data = request.get_json(force=True, silent=True)
        except Exception as e:
            app.logger.error(f"handshake_confirm: JSON parse error: {e}")
            return jsonify({"error": "invalid json"}), 400

        if not data:
            app.logger.warning("handshake_confirm: missing JSON body")
            return jsonify({"error": "missing json body"}), 400

        key_id, enc_aes_b64 = data.get("key_id"), data.get("enc_aes_b64")
        if not key_id or not enc_aes_b64:
            app.logger.warning(f"handshake_confirm: missing fields (key_id={key_id})")
            return jsonify({"error": "missing fields"}), 400

        with app.config["_CRYPTO_LOCK"]:
            handshake = app.config["RSA_HANDSHAKES"].pop(key_id, None)

        if not handshake:
            app.logger.warning(f"handshake_confirm: invalid_or_expired_handshake for key_id={key_id}")
            return jsonify({"error": "invalid_or_expired_handshake"}), 400

        try:
            aes_key = rsa_decrypt(handshake["priv_pem"], enc_aes_b64)
            app.logger.info(f"handshake_confirm: AES key decrypted for key_id={key_id}")
        except Exception as e:
            app.logger.error(f"handshake_confirm: RSA decrypt error for key_id={key_id}: {e}")
            return jsonify({"error": "decrypt_failed"}), 400

        try:
            expires = now_ts() + SESSION_TTL_SECONDS
            session_store = app.config["SESSION_STORE"]
            session_store.save_session_sync(key_id, aes_key, expires)
            app.logger.info(f"handshake_confirm SUCCESS: session saved (key_id={key_id})")

            return jsonify({
                "ok": True,
                "key_id": key_id,
                "ttl": SESSION_TTL_SECONDS
            })
        except TimeoutError as e:
            app.logger.error(f"handshake_confirm: database timeout for key_id={key_id}: {e}")
            return jsonify({"error": "database_timeout"}), 503
        except Exception as e:
            app.logger.error(f"handshake_confirm: failed to save session for key_id={key_id}: {e}")
            return jsonify({"error": "session_save_failed"}), 500

    @app.route("/handshake/check-key", methods=["POST"])
    def check_key():
        """Check if the key_id exists and is still valid."""
        data = request.get_json(force=True, silent=True)
        if not data or "key_id" not in data:
            return jsonify({"error": "missing key_id"}), 400

        key_id = data["key_id"]
        try:
            session_store = app.config["SESSION_STORE"]
            sess = session_store.get_session_sync(key_id)

            if not sess:
                return jsonify({"error": "invalid_or_expired_key"}), 401

            if sess["expires"] < now_ts():
                return jsonify({"error": "session_expired"}), 401

            return jsonify({"ok": True, "ttl": sess["expires"] - now_ts()})
        except Exception as e:
            app.logger.error(f"check_key error: {e}")
            return jsonify({"error": "database_error"}), 500

    @app.route("/handshake/stats", methods=["GET"])
    def session_stats():
        """Get session statistics"""
        try:
            session_store = app.config["SESSION_STORE"]
            active = session_store.get_session_count_sync()
            pending = len(app.config.get("RSA_HANDSHAKES", {}))
            return jsonify({
                "active_sessions": active,
                "pending_handshakes": pending
            })
        except Exception as e:
            app.logger.error(f"session_stats error: {e}")
            return jsonify({"error": "database_error"}), 500

    @app.after_request
    def encrypt_outgoing(resp):
        """Encrypt JSON responses for encrypted sessions."""
        if (request.path in ['/handshake'] or
            request.path.startswith('/handshake/') or 
            request.path.startswith('/socket.io') or
            request.method == 'OPTIONS' or
            'socket.io' in request.path.lower() or ":7777" in request.path.lower() or
            request.headers.get('Upgrade') == 'websocket'):
            return resp

        key_id = getattr(g, "key_id", None) or request.headers.get("X-Key-Id")
        
        if not key_id:
            return resp

        content_type = resp.headers.get("Content-Type", "")

        try:
            session_store = app.config["SESSION_STORE"]
            sess = session_store.get_session_sync(key_id)

            if not sess:
                return jsonify({"error": "session_expired"}), 401

            enc = aes_encrypt(sess["aes_key"], resp.get_data())
            new_body = json.dumps(enc).encode()
            resp.set_data(new_body)
            resp.headers["Content-Type"] = content_type
            resp.headers["Content-Length"] = str(len(new_body))
        except Exception as e:
            app.logger.error(f"Response encryption failed: {e}")

        return resp
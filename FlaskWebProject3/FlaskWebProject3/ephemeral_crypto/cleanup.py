# cleanup.py
import threading, time
from .crypto_utils import now_ts, RSA_HANDSHAKE_LIFETIME, SESSION_TTL_SECONDS

def start_cleanup_task(app, store_lock):
    def cleanup():
        while True:
            with store_lock:
                now = now_ts()
                # cleanup AES sessions
                for k in list(app.config['AES_SESSIONS'].keys()):
                    if app.config['AES_SESSIONS'][k]['expires'] < now:
                        app.logger.info(f"Expiring AES session {k}")
                        app.config['AES_SESSIONS'].pop(k, None)

                # cleanup RSA handshakes
                for k in list(app.config['RSA_HANDSHAKES'].keys()):
                    if app.config['RSA_HANDSHAKES'][k]['created'] + RSA_HANDSHAKE_LIFETIME < now:
                        app.logger.info(f"Removing expired RSA handshake {k}")
                        app.config['RSA_HANDSHAKES'].pop(k, None)
            time.sleep(30)
    t = threading.Thread(target=cleanup, daemon=True)
    t.start()

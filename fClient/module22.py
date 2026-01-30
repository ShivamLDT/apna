import os
import threading
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- CONFIG ----------
SFTP_HOST = '192.168.2.13'
SFTP_PORT = 22
SFTP_USERNAME = 'kuldeep'
SFTP_PASSWORD = 'Server@123'
REMOTE_ROOT = '/ApnaBackup/'
LOCAL_ROOT = 'D:/ApnaBackup'
MAX_PARALLEL = 8
RETRY_LIMIT = 3
CHUNK_SIZE = 32 * 1024 * 1024  # 32 MB
# ----------------------------

lock = threading.Lock()  # For thread-safe printing/logging

def create_sftp_client():
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

def sftp_upload_file(local_path, remote_path):
    attempts = 0
    while attempts < RETRY_LIMIT:
        try:
            sftp, transport = create_sftp_client()

            # Ensure remote dir exists
            ensure_remote_dirs(sftp, os.path.dirname(remote_path))

            # Resume logic
            try:
                remote_size = sftp.stat(remote_path).st_size
            except IOError:
                remote_size = 0

            file_size = os.path.getsize(local_path)
            if remote_size == file_size:
                log(f"SKIP {local_path} (already uploaded)")
                sftp.close()
                transport.close()
                return

            with open(local_path, "rb") as f:
                if remote_size:
                    f.seek(remote_size)
                    mode = 'ab'
                else:
                    mode = 'wb'

                with sftp.file(remote_path, mode) as remote_f:
                    remote_f.set_pipelined(True)
                    remote_f.seek(remote_size)
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        remote_f.write(chunk)

            sftp.close()
            transport.close()
            log(f" Uploaded: {local_path} -> {remote_path}")
            return
        except Exception as e:
            attempts += 1
            log(f" Error uploading {local_path} (attempt {attempts}): {e}")
    log(f" Failed to upload after {RETRY_LIMIT} attempts: {local_path}")

def ensure_remote_dirs(sftp, remote_dir):
    parts = remote_dir.strip('/').split('/')
    path = ''
    for part in parts:
        path += '/' + part
        try:
            sftp.stat(path)
        except FileNotFoundError:
            sftp.mkdir(path)

def list_files_recursive(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            local_path = os.path.join(dirpath, fname)
            remote_rel = os.path.relpath(local_path, root_dir).replace("\\", "/")
            remote_path = os.path.join(REMOTE_ROOT, remote_rel).replace("\\", "/")
            yield local_path, remote_path

def log(message):
    with lock:
        print(message)

def main():
    files = list(list_files_recursive(LOCAL_ROOT))
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
        futures = [executor.submit(sftp_upload_file, l, r) for l, r in files]
        for f in as_completed(futures):
            pass
        del futures
if __name__ == '__main__':
    main()


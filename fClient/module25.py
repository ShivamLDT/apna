
import os
import sys
import argparse
import hashlib
import logging
import threading
from time import sleep
import zstandard as zstd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from paramiko import Transport, SFTPClient

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

class ChunkCompressor:
    def __init__(self, chunk_size: int):
        self.chunk_size = chunk_size
        self.zstd_compressor = zstd.ZstdCompressor()

    def compress_stream(self, file_path: Path):
        """Yield compressed chunks."""
        with file_path.open("rb") as f:
            index = 0
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                compressed = self.zstd_compressor.compress(chunk)
                chunk_name = f"{file_path.name}.part{index}.zst"
                yield chunk_name, compressed
                index += 1

class SFTPUploader:
    def __init__(self, host, port, username, password, remote_path, max_workers=4, chunk_size=100*1024*1024):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self._lock = threading.Lock()
        self.total_files = 0
        self.total_uploaded = 0
        self._last_slept_at=0

    def _connect(self):
        transport = Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        return SFTPClient.from_transport(transport)

    def _upload_chunk(self, local_chunk: bytes, remote_filename: str, local_filename: str):
        try:
            with self._connect() as sftp:
                #remote_file_path = os.path.join(self.remote_path, remote_filename).replace("\\","/")
                self.remote_path="/D:/DDDDDDDDDDDDDD"
                remote_file_path = os.path.join(self.remote_path, remote_filename).replace("\\","/")
                parts = os.path.dirname(remote_file_path).split('/')
                current_path = ''
                for part in parts:
                    if part:  # Skip empty strings from leading/trailing slashes
                        current_path = f"{current_path}/{part}" if current_path else part
                        current_path=current_path.replace("//","/")
                        try:
                            sftp.stat(current_path)  # Check if directory exists
                        except FileNotFoundError:
                            sftp.mkdir(current_path) # Create if it doesn't exist
                with sftp.file(remote_file_path, 'wb') as f:
                    f.write(local_chunk)
                sftp.close()
            logging.info(f"Uploaded: {remote_filename}")
            with self._lock:
                self.total_uploaded += 1
                if self.total_uploaded and self.total_uploaded % 50 == 0 and self.total_uploaded != self._last_slept_at:
                    self._last_slept_at = self.total_uploaded

                logging.info(f"Progress: {self.total_uploaded}/{self.total_files}")
        except Exception as e:
            logging.error(f"Failed to upload {remote_filename}: {e}")
        print("asdfasdfasdf")
    def _process_file(self, file_path: Path):
        compressor = ChunkCompressor(self.chunk_size)
        futures = []
        for chunk_name, compressed_chunk in compressor.compress_stream(file_path):
            futures.append(self.executor.submit(self._upload_chunk, compressed_chunk, chunk_name))
        return futures

    def upload_directory(self, local_path):
        file_list = [p for p in Path(local_path).rglob('*') if p.is_file()]
        self.total_files = sum((os.path.getsize(f) - 1) // self.chunk_size + 1 for f in file_list)
        logging.info(f"Total chunks to upload: {self.total_files}")

        all_futures = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            self.executor = executor
            for file_path in file_list:
                futures = self._process_file(file_path)
                all_futures.extend(futures)

            for future in as_completed(all_futures):
                pass  # All logging is already done


# CLI Entry Point

def main():
    parser = argparse.ArgumentParser(description="Chunked, compressed SFTP uploader")
    parser.add_argument('--host', required=True, help='SFTP server host')
    parser.add_argument('--port', type=int, default=22, help='SFTP port')
    parser.add_argument('--username', required=True, help='SFTP username')
    parser.add_argument('--password', required=True, help='SFTP password')
    parser.add_argument('--remote-path', required=True, help='Remote directory to upload to')
    parser.add_argument('--local-path', required=True, help='Local directory containing files to upload')
    parser.add_argument('--chunk-size-mb', type=int, default=100, help='Chunk size in MB')
    parser.add_argument('--workers', type=int, default=4, help='Max parallel uploads')

    args = parser.parse_args()

    uploader = SFTPUploader(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        remote_path=args.remote_path,
        max_workers=args.workers,
        chunk_size=args.chunk_size_mb * 1024 * 1024
    )

    uploader.upload_directory(args.local_path)

if __name__ == "__main__":
    # main()

    #uploader = SFTPUploader(host="127.0.0.1",port=5050, username="owner", password="Server@123", remote_path="/sha2",chunk_size=256*1024*1024)
    #uploader.upload_directory(r"I:\Ronak Sharma 3Handshake\Source code")
    

    # uploader = SFTPUploader(host="127.0.0.1",port=5050, username="Administrator", password="123456", remote_path=".",chunk_size=256*1024*1024)
    # uploader.upload_directory(r"I:\Ronak Sharma 3Handshake\Source code")
    uploader = SFTPUploader(host="192.168.2.12",port=22, username="Administrator", password="123456", remote_path="Ronak Sharma 3Handshake/Source code/",chunk_size=256*1024*1024)
    uploader.upload_directory(r"I:\Ronak Sharma 3Handshake\Source code")
    # x = uploader._connect()
    # if x:
    #     x.chdir("/D:/DDDDDDDDDDDDDD")
    #     print("done " )
    #     x.close()

    print("thanks")

import os
import threading
import time
from tkinter import CURRENT
import paramiko
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

class SFTPUploader:
    def __init__(self, hostname, port, username, password, max_workers=4):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.max_workers = max_workers
        self._lock = threading.Lock()

    def _connect(self):
        try:
            client = paramiko.Transport((self.hostname, self.port))
            client.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(client)
            return client, sftp
        except Exception as eee:
            print(eee)

        

    def _upload_file(self, local_path, remote_path, chunk_size=32 * 1024 * 1024):
        file_size = os.path.getsize(local_path)
        sftp=None
        try:
            client, sftp = self._connect()
            
            # Resume support
            remote_size = 0
            try:
                remote_size = sftp.stat(remote_path).st_size
            except FileNotFoundError:
                pass

            parts = os.path.dirname(remote_path).split('/')
            current_path = ''
            for part in parts:
                if part:  # Skip empty strings from leading/trailing slashes
                    current_path = f"{current_path}/{part}" if current_path else part
                    current_path=current_path.replace("//","/")
                    try:
                        sftp.stat(current_path)  # Check if directory exists
                    except FileNotFoundError:
                        sftp.mkdir(current_path) # Create if it doesn't exist

            with open(local_path, "rb") as f:
                f.seek(remote_size)

                with tqdm(total=file_size, initial=remote_size, unit='B', unit_scale=True, desc=os.path.basename(local_path)) as pbar:
                    mode = 'ab' if remote_size > 0 else 'wb'
                    with sftp.file(remote_path, mode) as remote_file:
                        remote_file.set_pipelined(True)
                        while True:
                            data = f.read(chunk_size)
                            if not data:
                                break
                            remote_file.write(data)
                            pbar.update(len(data))
        finally:
            try:
                sftp.close()
            except Exception as ee:
                pass
            client.close()

    def _upload_file_Bytes(self, local_path, remote_path,encrypted_chunk, chunk_size=32 * 1024 * 1024):
        file_size = encrypted_chunk.seek(0,2) #os.path.getsize(local_path)
        sftp = None
        client=None
        try:
            client, sftp = self._connect()
            parts = os.path.dirname(remote_path).split('/')
            current_path = ''
            for part in parts:
                if part:  # Skip empty strings from leading/trailing slashes
                    current_path = f"{current_path}/{part}" if current_path else part
                    current_path=current_path.replace("//","/")
                    try:
                        sftp.stat(current_path)  # Check if directory exists
                    except FileNotFoundError:
                        sftp.mkdir(current_path) # Create if it doesn't exist
                


            encrypted_chunk.seek(0)
            # Resume support
            remote_size = 0
            try:
                remote_size = sftp.stat(remote_path).st_size
            except FileNotFoundError:
                pass
            
            
                 

            # with open(local_path, "rb") as f:
            #     f.seek(remote_size)
            encrypted_chunk.seek(remote_size)
            #with tqdm(total=file_size, initial=remote_size, unit='B', unit_scale=True, desc=local_path) as pbar:
            mode = 'ab' if remote_size > 0 else 'wb'
            sftp.putfo(encrypted_chunk,remote_path)
            # with sftp.file(remote_path, mode,bufsize=256*1024*1024) as remote_file:
            #     remote_file.set_pipelined(True)
            #     while True:
            #         data = encrypted_chunk.read()#chunk_size)
            #         if not data:
            #             break
                        
            #         remote_file.write(data)
            #             #pbar.update(len(data))
        finally:
            try:
                sftp.close()
            except:
                pass
            try:
                client.close()
            except:
                pass

    def _upload_worker(self, file_tuple):
        local_path, remote_path = file_tuple
        try:
            self._upload_file(local_path, remote_path)
        except Exception as e:
            print(f"[ERROR] Failed to upload {local_path}: {e}")

    def upload_directory(self, local_dir, remote_dir):
        local_dir = Path(local_dir).resolve()
        tasks = []

        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = Path(root) / file
                rel_path = local_path.relative_to(local_dir)
                remote_path = os.path.join(remote_dir, str(rel_path).replace("\\", "/"))
                tasks.append((str(local_path), remote_path))

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self._upload_worker, tasks)

# ----------------------------
# Example Usage
# ----------------------------
if __name__ == "__main__":
    # uploader = SFTPUploader(
    #     hostname="192.168.2.60",
    #     port=22,
    #     username="owner",
    #     password="Server@123",
    #     max_workers=8
    # )
    # uploader.upload_directory('I:/NF/BUG files', "/sha1e4r/")
    # uploader = SFTPUploader(
    #     hostname="127.0.0.1",
    #     port=5050,
    #     username="Administrator",
    #     password="123456",
    #     max_workers=1
    # )
    # uploader.upload_directory('I:\\NF\\Tanuu', "/DDDDDDDDDDDDDD/")
    
    uploader = SFTPUploader(
        hostname="192.168.2.12",
        port=22,
        username="user",
        password="Server@123",
        max_workers=16
    )
    t=time.time()
    uploader.upload_directory('I:\\NF\\Tanuu', "Test09/")
    print(f'Total time taken {str(time.time()-t)}') 


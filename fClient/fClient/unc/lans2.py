from ast import Try
from io import BytesIO
import math
import mmap
import os
import json
import hashlib
import logging
import os.path
from pydoc import ispath
import time
import zlib
import uuid
from appdirs import AppDirs
from apscheduler.schedulers.background import Thread
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import py7zr
import py7zr.exceptions
from pyzstd import ZstdError
from pydispatch import dispatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


from sqlalchemy import try_cast
from fClient import app
import fClient
from fClient import fingerprint
from fClient.fingerprint import getCode, getCodeHost, getKey
from fClient.p7zstd import p7zstd
from fClient.shad import OpenShFile
import tempfile
import traceback
# from fClient.sjbs.class1x import get_remote_file_stat

# import smb
# import smb.smb_constants
# from smb.base import SMBTimeout, NotReadyError, OperationFailure
# from smb.SMBConnection import SMBConnection
from fClient.unc.smbwrapper import (
    SMBConnection,
    SMBTimeout,
    NotReadyError,
    OperationFailure,
)
# Import UNC logger for unified logging to unc.log
from fClient.unc.unc_logger import (
    log_connection_attempt,
    log_connection_result,
    log_transfer_start,
    log_transfer_complete,
    log_error as unc_log_error,
    log_info as unc_log_info,
    log_debug as unc_log_debug,
)
import module23

##kartik
import logging
import logging.handlers
import sys
# Create a logs folder if it doesn't exist
os.makedirs("every_logs", exist_ok=True)

LOG_FILE = "every_logs/client_class2.log"

# Create the main logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define a detailed log format
detailed_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s:%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
)

# --- 1 File handler ---
file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_format)

# --- 2 Console handler ---
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(detailed_format)

# Add file + console handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --- 3 Windows Event Viewer handler ---
# try:
#     event_handler = logging.handlers.NTEventLogHandler(appname="ABS")
#     event_handler.setLevel(logging.DEBUG)
#     event_formatter = logging.Formatter(
#         "[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
#     )
#     event_handler.setFormatter(event_formatter)
#     logger.addHandler(event_handler)
#     logger.info("Windows Event Viewer handler attached successfully.")
# except Exception as e:
#     logger.warning(f"Could not attach Windows Event Viewer handler: {e}")


# Constants
# CHUNK_SIZE = 64 * 1021 * 1024  # 64KBM
# MASTER_METADATA_FILE = 'master_metadata.json'
app.config["AppFolders"] = AppDirs("ApnaBackup", roaming=True, multipath=True)
CHUNK_SIZE = 0  # 64 * 1024 * 1024  # 64KBM
RETRY_LIMIT = [
    4,5,6,    4,    5,    6,    4,    5,    6,    4,    5,    6,    4,    5,    
    6,4,5,    6,    4,    5,    6,    4,    5,    6,    4,    5,    6,    4,    
    5,6,4,    5,    6,    4,    5,    6,
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,
]
RETRY_BACKOFF_BASE = 2

MASTER_METADATA_FILE = os.path.join(
    app.config["AppFolders"].site_config_dir, "master_metadata.json"
)

# Setup logging
logging.basicConfig(
    level=logging.INFO, filename="LAN2.log", datefmt="yyyy_MMM_dd_HH_mm_ss"
)
logger = logging.getLogger(__name__)

# Thread lock for thread safety
lock = threading.Lock()

# Ensure master metadata file exists
if not os.path.exists(MASTER_METADATA_FILE):
    os.makedirs(os.path.dirname(MASTER_METADATA_FILE), exist_ok=True)
    with open(MASTER_METADATA_FILE, "w") as f:
        json.dump({}, f)


class EncryptedFileSystem:

    # def __new__(
    #     cls, server_name_address, server_user_name, server_password, share_location
    # ):

    #     server_conn = SMBConnection(
    #         server_user_name,
    #         server_password,
    #         "",
    #         server_name_address,
    #         use_ntlm_v2=True,
    #         is_direct_tcp=True,
    #     )
    #     try:
    #         turn = 0
    #         while turn < 10:
    #             try:
    #                 if not server_conn.connect(server_name_address, 445):
    #                     time.sleep(18)
    #                 else:
    #                     turn = 10
    #             except Exception as e:
    #                 print("===============================")
    #                 print(str(e))
    #                 time.sleep(18)
    #                 print("server not connected")
    #                 print("===============================")
    #             turn += 1

    #         # if not server_conn.connect(server_name_address, 445):
    #         #     return None
    #         return super().__new__(cls)
    #     except Exception as se:
    #         return None
    #     # finally:
    #     #     server_conn.session.disconnect()

    def __init__(
        self,
        server_name_address,
        server_user_name,
        server_password,
        share_location,
        job_id=None,
        keyx=None,
        iv=None,
        smb_conn=None,
        sFTP_uploader=None
    ):

        self.FILE_NOT_FOUND = "FileNotFound"
        self.ACCESS_ERROR = "AccessError"
        self.ERROR = "Error"
        self.UPLOADED = "Uploaded"
        self.UPLOADED_PART = "UploadedPart"
        self.UPLOADED_PART_FILE_HANDLER = "UploadedPartFile"
        self.UPLOADED_JOB = "UploadedJob"
        self.CONNECTION_REJECTED = "ConnectionRejected"
        self.job_id = job_id
        self.key = keyx
        self.iv = "00000000000000000000000000000000" if iv is None else iv
        
        self.server_name_address = server_name_address
        self.server_user_name = server_user_name
        self.server_password = server_password
        self.share_location=share_location
        self.server_conn = self.refresh_smb() if smb_conn is None else smb_conn
        self.executor = ThreadPoolExecutor(max_workers=16)
        self.sFTP_uploader=self.get_SFTP_uploader()
        self.sftp_client=None
        self.sftp_object=None
    def init_smb(self):

        if not self.server_conn:
            self.server_conn = SMBConnection(
                self.server_user_name,
                self.server_password,"",
                self.server_name_address,
                use_ntlm_v2=True,
                is_direct_tcp=True,
                ) 
        try:
            if not self.server_conn.connect(self.server_name_address, 445):
                logger.error("Failed to connect to server.")
                raise RuntimeError(ConnectionError("Failed to connect to server."))
            self.share_location = self.share_location
        except Exception as se:
            logger.error(f"Failed to connect to server.{se}")
            raise RuntimeError(ConnectionError("Failed to connect to server."))
    
    def get_SFTP_uploader(self):
        try:
            if not self.sFTP_uploader:
                self.sFTP_uploader = module23.SFTPUploader(
                    hostname=self.server_name_address,
                    port=22,
                    username=self.server_user_name,
                    password=self.server_password,
                    max_workers=40
                )
        except:
            self.sFTP_uploader =None
        return self.sFTP_uploader
                     
    def refresh_smb(self):

        try:
            self.server_conn.tree.disconnect()
            try:
                self.server_conn.session.disconnect()

            except:
                pass

        except:
            pass

        finally:

            self.server_conn=None
        

            
        # if not self.server_conn:
        #     self.server_conn

        server_conn = SMBConnection(
            self.server_user_name,
            self.server_password,"",
            self.server_name_address,
            use_ntlm_v2=True,
            is_direct_tcp=True,
            ) 
        
        try:
            if not server_conn.connect(self.server_name_address, 445):
                logger.error("Failed to connect to server.")
                raise RuntimeError(ConnectionError("Failed to connect to server."))
            self.share_location = self.share_location
            return server_conn
        except Exception as se:
            logger.error(f"Failed to connect to server.{se}")
            raise RuntimeError(ConnectionError("Failed to connect to server."))

    def is_prime(self, n):
        """Returns True if n is a prime number, else False."""
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False

        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def get_chunk_size(self, file_size):
        """
        Determines the optimal chunk size based on:
        1. No chunking for files <= 1MB.
        2. No chunking if file_size is prime.
        3. Otherwise, find the largest proper divisor for chunking.

        Returns:
            (chunk_size, total_chunks)
        """

        max_chunk_size = 1024**2  # 1MB
        min_chunk_size = 1 * 1024
        if file_size <= max_chunk_size * 256:  # 1MB threshold
            return file_size, 1  # No chunking

        # if self.is_prime(file_size):
        #     return file_size, 1  # Prime numbers cannot be chunked

        # Find the largest integer divisor for chunking
        for i in range(file_size // 1024, 0, -1):  # Start from half of file_size
            if file_size % i == 0:
                if i <= 256 * (1024**2):
                    return i, file_size // i  # (chunk size, total chunks)
            i = i // 2

        return file_size, 1  # This should never occur

    def compress_data(self, data, iv=None, file_name="data"):
        iv = self.iv if not iv else iv
        pZip = p7zstd(iv, preset=int("6"))
        compressed_data = pZip.compress(data=data, file_name=file_name, chunk_size=0)
        del pZip
        return compressed_data
        # return zlib.compress(data,zlib.Z_BEST_COMPRESSION)

    def decompress_data(self, data, iv=None, file_name="data"):
        iv = self.iv if not iv else iv
        pZip = p7zstd(iv)
        decompressed_data = pZip.decompress(encrypted_data=data, file_name=file_name)
        del pZip
        return decompressed_data
        # return zlib.decompress(data)

    def encrypt_and_chunk_file_old(self, file_path, key, guid, OpendedSh=None, **kwargs):
        chunks = []
        # iv = os.urandom(16)
        # secret = "your_strong_secret"
        # iv = hashlib.sha256(secret.encode()).hexdigest()[:16]
        # cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        # padder = padding.PKCS7(128).padder()
        import html
        from urllib.parse import unquote
        guid = html.unescape(unquote(guid))
        
        open_file_name = file_path
        if OpendedSh:
            open_file_name = OpendedSh.get_path(file_path)
            if not open_file_name:
                open_file_name = file_path
        dispatcher.send(
            signal=self.UPLOADED_PART_FILE_HANDLER,
            sender=self,
            metadata={},
            file_path=file_path,
            per=0,
            file_id=kwargs["kwargs"]["backup_status_template"],
        )
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.padding import PKCS7

        # Define your static IV
        iv = bytes.fromhex(self.iv)  # Replace with your desired static IV

        # Create the cipher object with the static IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

        padder = padding.PKCS7(128).padder()
        import asyncio

        file_size = 0
        size = 0
        CHUNK_SIZE = 0
        t_c_count = 0
        i = 0
        futures = []
        try:
            size = os.path.getsize(open_file_name)
            print(f"Size: {size} bytes")
        except OSError as e:
            print(f"Error: {e}")
            size = -1
        try:
            # with open(file_path, "rb") as f:
            # with OpenShFile(file_path, "rb") as f:
            # executor = ThreadPoolExecutor(max_workers=8)
            j = None
            with open(open_file_name, "rb") as f:
                if size < 0:
                    f.seek(0, 2)
                    size = f.tell()
                    f.seek(0)

                CHUNK_SIZE, total_chunks = self.get_chunk_size(size)
                CHUNK_SIZE = 128 * 1024 * 1024
                if size >= 1024 * 1024 * 1024:
                    CHUNK_SIZE = 128 * 1024 * 1024
                if size >= 512 * 1024 * 1024:
                    CHUNK_SIZE = 256 * 1024 * 1024
                if CHUNK_SIZE > size:
                    CHUNK_SIZE = size

                total_chunks = math.ceil(size / CHUNK_SIZE)

                #with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as file_obj:
                # compressed_data = file_obj.read() #f.read()
                # compressed_data = self.compress_data(data=compressed_data,iv=self.iv)#,file_name=f"{os.path.basename(file_path)}")

                chunk_num = 0
                encryptor = cipher.encryptor()
                # if CHUNK_SIZE<1:
                #     CHUNK_SIZE=len(compressed_data)
                # CHUNK_SIZE,_ = self.get_chunk_size(len(compressed_data))
                # CHUNK_SIZE=len(compressed_data)
                # for i in range(0, len(compressed_data), CHUNK_SIZE):
                chunk_data = f.read(CHUNK_SIZE)
                while chunk_data:
                    if self.job_id:
                        j = app.apscheduler.get_job(id=self.job_id)
                        if j:
                            while not j.next_run_time:
                                asyncio.sleep(10)
                                j = app.apscheduler.get_job(id=self.job_id)

                    i = i + 1
                    t_c_count = t_c_count - 1
                    encrypted_chunk = BytesIO()
                    # iv,preset=int(compression_level)
                    with py7zr.SevenZipFile(
                        encrypted_chunk,
                        "w",
                        password=self.iv,
                        filters=[
                            {"id": py7zr.FILTER_ZSTD},
                            {
                                "id": py7zr.FILTER_CRYPTO_AES256_SHA256,
                                "password": self.iv,
                            },
                        ],
                    ) as archive:
                        archive.writestr(
                            data=chunk_data, arcname=f"chunk_{i}.abzv2"
                        )

                    # with py7zr.SevenZipFile(encrypted_chunk, 'r', password=self.iv,
                    #                         filters=[{"id": py7zr.FILTER_ZSTD},
                    #                                  {"id": py7zr.FILTER_CRYPTO_AES256_SHA256, "password": self.iv}]) as archive:
                    #     extracted = archive.readall()
                    #     datdda=BytesIO()
                    #     if extracted:
                    #         for edata in extracted:# archive.readall().items: #extracted:
                    #             datdda.write(extracted[edata].getvalue())
                    #         print(datdda.getvalue())

                    # print(encrypted_chunk.getvalue()[:16])
                    encrypted_chunk_position = encrypted_chunk.tell()
                    print(f"pointer found at {encrypted_chunk_position}")
                    encrypted_chunk.seek(0)
                    chunk_data = f.read(CHUNK_SIZE)

                    # encrypted_chunk=encrypted_chunk.getvalue()

                    # chunk = compressed_data[i : i + CHUNK_SIZE]
                    # the following line has been commented to stop explicit encyption
                    # and the value of encrypted_chunk has been set from chunk
                    # padded_data = padder.update(chunk)
                    # try:
                    #     padded_data += padder.finalize()
                    # except:
                    #     print("")

                    # encrypted_chunk = (
                    #     encryptor.update(padded_data) + encryptor.finalize()
                    # )

                    # encrypted_chunk=chunk

                    # file_size+=len(encrypted_chunk)

                    # encrypted_chunk.seek(0,2)
                    # file_size+=encrypted_chunk.tell()
                    file_size = 10  # encrypted_chunk.tell()
                    # encrypted_chunk.seek(0)
                    chunk_folder = os.path.join(guid, f"abb{chunk_num}")
                    os.makedirs(chunk_folder, exist_ok=True)
                    file_path = html.unescape(unquote(file_path))
                    from urllib.parse import unquote
                    import html
                    chunk_path = os.path.join(
                        chunk_folder,
                        f"{os.path.basename(file_path)}.abb{chunk_num}",
                    )
                    self.server_conn.ensure_connected(self.share_location)
                    if not self.server_conn.tree:
                        self.server_conn.connectTree(self.share_location)

                    # self.create_folder_tree(
                    #     self.server_conn, os.path.dirname(chunk_path)
                    # )
                    self.server_conn.ensure_remote_folder(self.share_location,os.path.dirname(chunk_path))
                    #self.server_conn.disconnectTree()
                    
                    # Calculate expected hash BEFORE upload for verification
                    encrypted_chunk.seek(0)
                    expected_hash = hashlib.sha256(encrypted_chunk.getvalue()).hexdigest()
                    encrypted_chunk.seek(0)
                    upload_verified = False

                    for attempt in RETRY_LIMIT:
                        try:
                            encrypted_chunk.seek(0)
                            self.server_conn.storeFile(self.share_location, chunk_path, encrypted_chunk)
                            
                            # Verify upload by reading back and comparing checksum
                            verify_buffer = BytesIO()
                            try:
                                self.server_conn.retrieveFile(self.share_location, chunk_path, verify_buffer)
                                verify_buffer.seek(0)
                                actual_hash = hashlib.sha256(verify_buffer.read()).hexdigest()
                                if actual_hash == expected_hash:
                                    upload_verified = True
                                    logger.info(f"Uploaded and verified chunk {chunk_num}: {chunk_path}")
                                    break
                                else:
                                    logger.warning(f"Upload checksum mismatch for chunk {chunk_num}, retrying...")
                            except Exception as verify_err:
                                logger.warning(f"Failed to verify uploaded chunk {chunk_num}: {verify_err}")
                            finally:
                                verify_buffer.close()
                                
                        except (SMBTimeout, NotReadyError, OperationFailure, OSError) as e:
                            with open(chunk_path, "wb") as chunk_file:
                                chunk_file.write(encrypted_chunk.getvalue())
                                chunk_file.flush()

                            x = -1
                            try:
                                x = self.upload_to_server(chunk_path)
                                if x > 0:
                                    # Verify fallback upload
                                    verify_buffer = BytesIO()
                                    try:
                                        self.server_conn.retrieveFile(self.share_location, chunk_path, verify_buffer)
                                        verify_buffer.seek(0)
                                        actual_hash = hashlib.sha256(verify_buffer.read()).hexdigest()
                                        if actual_hash == expected_hash:
                                            upload_verified = True
                                    except:
                                        pass
                                    finally:
                                        verify_buffer.close()
                                    if upload_verified:
                                        break
                            except:
                                pass

                            if x < 1:
                                logging.error(
                                    f"Upload attempt {attempt + 1} failed: {e}"
                                )
                                backoff = RETRY_BACKOFF_BASE**attempt
                                print(
                                    f"Retrying to connect to NAS/File server...........{backoff}"
                                )
                                time.sleep(backoff)
                    
                    if not upload_verified:
                        logger.error(f"Failed to verify upload for chunk {chunk_num} after all retries")
                        raise RuntimeError(f"Upload verification failed for chunk {chunk_num}")

                    chunk_hash = expected_hash  # Use pre-calculated hash
                    chunk_json = {
                        "path": chunk_path,
                        "hash": chunk_hash,
                        "size": size,
                    }
                    chunks.append(chunk_json)

                    dispatcher.send(
                        signal=self.UPLOADED_PART_FILE_HANDLER,
                        sender=self,
                        metadata={},
                        file_path=file_path,
                        per=100 * ((chunk_num + 1) / total_chunks),
                        file_id=kwargs["kwargs"]["backup_status_template"],
                    )

                    del chunk_path
                    del chunk_hash

                    chunk_num += 1

                    # shifting  chunk_data to next block

                # Finalize padding is not required as the above encryption has been commented
                # # Finalize padding
                # try:
                #     final_padded_data = padder.finalize()
                #     if final_padded_data:
                #         encryptor = cipher.encryptor()
                #         encrypted_chunk = (
                #             encryptor.update(final_padded_data) + encryptor.finalize()
                #         )
                #         chunk_folder = os.path.join(guid, f"abb{chunk_num}")
                #         os.makedirs(chunk_folder, exist_ok=True)
                #         chunk_path = os.path.join(
                #             chunk_folder, f"{os.path.basename(file_path)}.abb{chunk_num}"
                #         )
                #         with open(chunk_path, "wb") as chunk_file:
                #             chunk_file.write(encrypted_chunk)
                #         chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()
                #         chunks.append({"path": chunk_path, "hash": chunk_hash})
                # except:
                #     print("")

        except Exception as e:
            logger.error(f"Error encrypting and chunking file: {e}")
            self.cleanup_files([chunk["path"] for chunk in chunks])
            try:
                os.removedirs(chunk_folder)
            except:
                pass
            raise RuntimeError(e)

        return chunks, iv

    #def encrypt_and_chunk_file(self, file_path, key, guid, OpendedSh=None, **kwargs):
    def encrypt_and_chunk_file(self, file_path, key, guid, OpendedSh=None, **kwargs):
        chunks = []
        import html
        from urllib.parse import unquote
        guid = html.unescape(unquote(guid))
        
        open_file_name = file_path
        if OpendedSh:
            open_file_name = OpendedSh.get_path(file_path)
            if not open_file_name:
                open_file_name = file_path
        dispatcher.send(
            signal=self.UPLOADED_PART_FILE_HANDLER,
            sender=self,
            metadata={},
            file_path=file_path,
            per=0,
            file_id=kwargs["kwargs"]["backup_status_template"],
        )
        # from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        # from cryptography.hazmat.backends import default_backend
        # from cryptography.hazmat.primitives.padding import PKCS7

        # Define your static IV
        iv = bytes.fromhex(self.iv)  # Replace with your desired static IV

        # # Create the cipher object with the static IV
        # cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

        # padder = padding.PKCS7(128).padder()
        # import asyncio

        file_size = 0
        size = 0
        CHUNK_SIZE = 0
        t_c_count = 0
        i = 0
        futures = []
        try:
            size = os.path.getsize(open_file_name)
            print(f"Size: {size} bytes")
        except OSError as e:
            print(f"Error: {e}")
            size = -1
        try:
        
            j = None
            with open(open_file_name, "rb") as f:
                if size < 0:
                    f.seek(0, 2)
                    size = f.tell()
                    f.seek(0)

                #CHUNK_SIZE, total_chunks = self.get_chunk_size(size)
                CHUNK_SIZE = 128 * 1024 * 1024
                if size >= 1024 * 1024 * 1024:
                    CHUNK_SIZE = 128 * 1024 * 1024
                elif size >= 512 * 1024 * 1024:
                    CHUNK_SIZE = 256 * 1024 * 1024
                elif size >= 128 * 1024 * 1024:
                    CHUNK_SIZE = 50 * 1024 * 1024
                elif CHUNK_SIZE > size:
                    CHUNK_SIZE = size

                total_chunks = math.ceil(size / CHUNK_SIZE)
                chunk_num = 0
                #encryptor = cipher.encryptor()
                
                chunk_data = f.read(CHUNK_SIZE)
                while chunk_data:
                    try:
                        if self.job_id:
                            j = app.apscheduler.get_job(id=self.job_id)
                            if j:
                                while not j.next_run_time:
                                    time.sleep(10)
                                    j = app.apscheduler.get_job(id=self.job_id)
                    except Exception as eeee:
                        pass
                    i = i + 1
                    t_c_count = t_c_count - 1
                    encrypted_chunk = BytesIO()
                    with py7zr.SevenZipFile(
                        encrypted_chunk,
                        "w",
                        password=self.iv,
                        filters=[
                            {"id": py7zr.FILTER_ZSTD},
                            {
                                "id": py7zr.FILTER_CRYPTO_AES256_SHA256,
                                "password": self.iv,
                            },
                        ],
                    ) as archive:
                        archive.writestr(
                            data=chunk_data, arcname=f"chunk_{i}.abzv2"
                        )

                    
                    encrypted_chunk_position = encrypted_chunk.tell()
                    print(f"pointer found at {encrypted_chunk_position}")
                    encrypted_chunk.seek(0)
                    chunk_data = f.read(CHUNK_SIZE)

                    
                    file_size = 10  # encrypted_chunk.tell()
                    chunk_folder = os.path.join(guid, f"abb{chunk_num}")
                    os.makedirs(chunk_folder, exist_ok=True)
                    file_path = html.unescape(unquote(file_path))
                    from urllib.parse import unquote
                    import html
                    chunk_path = os.path.join(
                        chunk_folder,
                        f"{os.path.basename(file_path)}.abb{chunk_num}",
                    )
                    # Ensure connection and create remote folder structure before upload
                    self.server_conn.ensure_connected(self.share_location)
                    
                    # Create folder structure on SMB share (required - SMB won't auto-create parent dirs)
                    chunk_folder_path = os.path.dirname(chunk_path)
                    if chunk_folder_path:
                        self.server_conn.ensure_remote_folder(self.share_location, chunk_folder_path)
                    
                    # Log transfer start to unc.log
                    chunk_size = encrypted_chunk.seek(0, 2)  # Get size
                    encrypted_chunk.seek(0)
                    # Calculate expected hash BEFORE upload for verification
                    expected_hash = hashlib.sha256(encrypted_chunk.getvalue()).hexdigest()
                    encrypted_chunk.seek(0)
                    
                    unc_log_info(f"CHUNK_UPLOAD_START | chunk={chunk_num}/{total_chunks} | path={chunk_path} | size={chunk_size} | hash={expected_hash[:16]}...")
                    upload_start_time = time.time()
                    upload_verified = False
                    
                    for attempt in RETRY_LIMIT:
                        try:
                            # Ensure BytesIO is at position 0 before each upload attempt
                            encrypted_chunk.seek(0)
                            
                            # Use SMB (storeFile) instead of SFTP for Windows UNC shares
                            # SFTP requires SSH server (port 22) which Windows doesn't have by default
                            # SMB uses port 445 which is native to Windows file sharing
                            self.server_conn.storeFile(self.share_location, chunk_path, encrypted_chunk)
                            
                            # Verify upload by reading back and comparing checksum
                            verify_buffer = BytesIO()
                            try:
                                self.server_conn.retrieveFile(self.share_location, chunk_path, verify_buffer)
                                verify_buffer.seek(0)
                                actual_hash = hashlib.sha256(verify_buffer.read()).hexdigest()
                                
                                if actual_hash == expected_hash:
                                    upload_verified = True
                                    upload_duration = time.time() - upload_start_time
                                    logger.info(f"Uploaded and verified chunk {chunk_num} to SMB share: {chunk_path}")
                                    unc_log_info(f"CHUNK_UPLOAD_VERIFIED | chunk={chunk_num}/{total_chunks} | path={chunk_path} | duration={upload_duration:.2f}s")
                                    break
                                else:
                                    # Checksum mismatch - data corrupted during transfer
                                    unc_log_error("upload_checksum_mismatch", 
                                        ValueError(f"Expected: {expected_hash[:16]}..., Got: {actual_hash[:16]}..."),
                                        context=f"chunk={chunk_num} attempt={attempt+1} path={chunk_path}")
                                    logger.warning(f"Upload verification failed for chunk {chunk_num}, retrying...")
                                    # Continue to retry
                            except Exception as verify_err:
                                # Verification read failed - treat as upload failure
                                unc_log_error("upload_verify_read", verify_err, context=f"chunk={chunk_num} attempt={attempt+1}")
                                logger.warning(f"Failed to verify uploaded chunk {chunk_num}: {verify_err}")
                            finally:
                                verify_buffer.close()
                                
                        except Exception as e:
                            logger.warning(f"SMB upload attempt {attempt + 1} failed: {e}")
                            # Log to unc.log for tracking
                            unc_log_error(f"smb_upload", e, context=f"chunk={chunk_num} attempt={attempt+1} path={chunk_path}")
                            
                            # Try to reconnect SMB before retry
                            try:
                                self.server_conn.ensure_connected(self.share_location)
                                unc_log_debug(f"SMB reconnect attempt after failure")
                            except Exception as reconn_err:
                                unc_log_error("smb_reconnect", reconn_err, context=f"chunk={chunk_num}")
                            
                            # Fallback: write chunk to local disk then upload via alternate method
                            try:
                                os.makedirs(os.path.dirname(chunk_path), exist_ok=True)
                                encrypted_chunk.seek(0)
                                with open(chunk_path, "wb") as chunk_file:
                                    chunk_file.write(encrypted_chunk.getvalue())
                                    chunk_file.flush()
                                
                                unc_log_info(f"FALLBACK_UPLOAD_ATTEMPT | chunk={chunk_num} | path={chunk_path}")
                                x = self.upload_to_server(chunk_path)
                                if x > 0:
                                    # Verify fallback upload
                                    verify_buffer = BytesIO()
                                    try:
                                        self.server_conn.retrieveFile(self.share_location, chunk_path, verify_buffer)
                                        verify_buffer.seek(0)
                                        actual_hash = hashlib.sha256(verify_buffer.read()).hexdigest()
                                        if actual_hash == expected_hash:
                                            upload_verified = True
                                            upload_duration = time.time() - upload_start_time
                                            logger.info(f"Uploaded and verified chunk {chunk_num} via fallback method")
                                            unc_log_info(f"FALLBACK_UPLOAD_VERIFIED | chunk={chunk_num} | duration={upload_duration:.2f}s")
                                    except Exception as fallback_verify_err:
                                        unc_log_error("fallback_verify", fallback_verify_err, context=f"chunk={chunk_num}")
                                    finally:
                                        verify_buffer.close()
                                    
                                    # Clean up local file after successful upload
                                    try:
                                        os.remove(chunk_path)
                                    except:
                                        pass
                                    if upload_verified:
                                        break
                            except Exception as fallback_err:
                                logger.warning(f"Fallback upload also failed: {fallback_err}")
                                unc_log_error("fallback_upload", fallback_err, context=f"chunk={chunk_num}")

                        backoff = RETRY_BACKOFF_BASE**attempt
                        unc_log_info(f"UPLOAD_RETRY | chunk={chunk_num} | attempt={attempt+1} | backoff={backoff}s")
                        print(f"Retrying to connect to NAS/File server...........{backoff}")
                        time.sleep(backoff)
                    
                    # Check if upload was verified after all retries
                    if not upload_verified:
                        unc_log_error("upload_failed", 
                            RuntimeError(f"Failed to upload and verify chunk after {len(RETRY_LIMIT)} attempts"),
                            context=f"chunk={chunk_num} path={chunk_path}")
                        raise RuntimeError(f"Upload verification failed for chunk {chunk_num} after all retries")

                    chunk_hash = expected_hash  # Use pre-calculated hash
                    chunk_json = {
                        "path": chunk_path,
                        "hash": chunk_hash,
                        "size": size,
                    }
                    chunks.append(chunk_json)

                    dispatcher.send(
                        signal=self.UPLOADED_PART_FILE_HANDLER,
                        sender=self,
                        metadata={},
                        file_path=file_path,
                        per=100 * ((chunk_num + 1) / total_chunks),
                        file_id=kwargs["kwargs"]["backup_status_template"],
                    )

                    del chunk_path
                    del chunk_hash

                    chunk_num += 1

                    # shifting  chunk_data to next block

                # Finalize padding is not required as the above encryption has been commented
                # # Finalize padding
                # try:
                #     final_padded_data = padder.finalize()
                #     if final_padded_data:
                #         encryptor = cipher.encryptor()
                #         encrypted_chunk = (
                #             encryptor.update(final_padded_data) + encryptor.finalize()
                #         )
                #         chunk_folder = os.path.join(guid, f"abb{chunk_num}")
                #         os.makedirs(chunk_folder, exist_ok=True)
                #         chunk_path = os.path.join(
                #             chunk_folder, f"{os.path.basename(file_path)}.abb{chunk_num}"
                #         )
                #         with open(chunk_path, "wb") as chunk_file:
                #             chunk_file.write(encrypted_chunk)
                #         chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()
                #         chunks.append({"path": chunk_path, "hash": chunk_hash})
                # except:
                #     print("")

        except Exception as e:
            logger.error(f"Error encrypting and chunking file: {e}")
            self.cleanup_files([chunk["path"] for chunk in chunks])
            try:
                os.removedirs(chunk_folder)
            except:
                pass
            
            raise RuntimeError(e)

        return chunks, iv

    def _upload_file_Bytes(self, local_path, remote_path,encrypted_chunk, chunk_size=1 * 1024 * 1024):
        file_size = encrypted_chunk.seek(0,2) #os.path.getsize(local_path)
            
        if not self.sftp_client:
            self.sFTP_uploader = self.get_SFTP_uploader()
            self.sftp_client,self.sftp_object= self.sFTP_uploader._connect()

        sftp = self.sftp_object
        client=self.sftp_client
            
        try: 
            parts = os.path.dirname(remote_path).split('/')
            current_path = ''
            for part in parts:
                if part:  # Skip empty strings from leading/trailing slashes
                    current_path = f"{current_path}/{part}" if current_path else part
                    current_path=current_path.replace("//","/")
                    try:
                        sftp.stat(current_path)  # Check if directory exists
                    except FileNotFoundError:
                        try:
                            sftp.mkdir(current_path) # Create if it doesn't exist
                        except Exception as eer:
                            pass
                
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
                #sftp.put
            #with sftp.file(remote_path, mode,bufsize=32768) as remote_file:
            with sftp.file(remote_path, mode) as remote_file:
                remote_file.set_pipelined(True)
                while True:
                    data = encrypted_chunk.read()#chunk_size)
                    if not data:
                        break
                    remote_file.write(data)
                        #pbar.update(len(data))
        finally:
            # try:
            #     sftp.close()
            # except:
            #     pass
            # try:
            #     client.close()
            # except:
                pass


    def decrypt_and_reassemble_file(self, file_path=None, key=None, metadata=None, progress_callback=None):
        """Restore file from UNC chunks. Optional progress_callback(chunk_idx, total_chunks, progress_pct)."""

        if not metadata:
            metadata = self.get_metadata_from_master(file_path)

        if self.key:
            key = self.key
        if not key:
            key = getKey()
        iv = bytes.fromhex(metadata["givn"])
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        unpadder = padding.PKCS7(128).unpadder()

        original_file_path = metadata["original_path"]
        restore_file_path = ""
        try:
            restore_file_path = metadata.get(
                "restore_path", metadata.get("original_path", "")
            )
            if "Testing" in restore_file_path:
                print("")
            # Ensure Windows path has drive letter (e.g. Users\... -> C:\Users\...)
            if restore_file_path and os.name == "nt":
                import re
                if not re.match(r'^[A-Za-z]:[\\/]', restore_file_path):
                    sys_drive = os.environ.get("SystemDrive", "C:")
                    restore_file_path = os.path.normpath(os.path.join(sys_drive + os.sep, restore_file_path.lstrip("\\/")))
            if os.path.exists(restore_file_path):
                if not os.path.isfile(restore_file_path):
                    file_path = metadata.get("original_path", "").split(os.sep)[-1]
                    restore_file_path = os.path.join(restore_file_path, file_path)

        except:
            pass

        guid_folder = metadata["guid"]

        try:

            if restore_file_path == "":
                raise RuntimeError("Destination location not supplied by the user.")

            unc_log_info(f"RESTORE_START | target={restore_file_path} | chunks={len(metadata.get('chunks', []))}")
            os.makedirs(guid_folder, exist_ok=True)

            decrypted_data = b""
            decompressed_data = None
            if os.path.exists(restore_file_path) and os.path.isfile(restore_file_path):
                os.remove(restore_file_path)
            for chunk_idx, chunk_info in enumerate(metadata["chunks"], 1):
                chunk_path = chunk_info["path"]
                os.makedirs(os.path.dirname(chunk_path), exist_ok=True)
                expected_hash = chunk_info["hash"]
                
                # Retry logic for chunk download with checksum validation
                max_checksum_retries = 3
                chunk_validated = False
                
                for checksum_attempt in range(max_checksum_retries):
                    self.download_from_server(chunk_path, chunk_path)
                    
                    with open(chunk_path, "rb") as chunk_file:
                        encrypted_chunk = chunk_file.read()
                        chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()
                        
                        if chunk_hash == expected_hash:
                            # Checksum validated successfully
                            unc_log_info(f"CHUNK_CHECKSUM_OK | chunk={chunk_idx}/{len(metadata['chunks'])} | path={chunk_path}")
                            chunk_validated = True
                            break
                        else:
                            # Checksum mismatch - log and retry
                            unc_log_error("checksum_mismatch", 
                                ValueError(f"Expected: {expected_hash[:16]}..., Got: {chunk_hash[:16]}..."),
                                context=f"chunk={chunk_idx} attempt={checksum_attempt+1} path={chunk_path}")
                            logger.warning(f"Checksum mismatch for chunk {chunk_path}, attempt {checksum_attempt + 1}/{max_checksum_retries}")
                            
                            if checksum_attempt < max_checksum_retries - 1:
                                # Delete corrupted chunk and retry download
                                try:
                                    os.remove(chunk_path)
                                except:
                                    pass
                                time.sleep(RETRY_BACKOFF_BASE ** checksum_attempt)
                
                if not chunk_validated:
                    # All retries failed - data corruption or tampering
                    logger.error(f"Tampering/corruption detected in chunk after {max_checksum_retries} retries: {chunk_path}")
                    unc_log_error("checksum_failed", 
                        ValueError(f"Chunk validation failed after {max_checksum_retries} attempts"),
                        context=f"chunk={chunk_idx} path={chunk_path} expected={expected_hash[:16]}...")
                    raise ValueError(f"Checksum validation failed for chunk {chunk_path} after {max_checksum_retries} retries")
                
                # Checksum validated - now decompress the chunk
                try:
                    decompressed_data = self.decompress_data(
                        data=encrypted_chunk, iv=metadata["givn"]
                    )
                except (
                    py7zr.exceptions.Bad7zFile,
                    ZstdError,
                    py7zr.exceptions.DecompressionError,
                    py7zr.exceptions.UnsupportedCompressionMethodError,
                ) as e:
                    decrypted_data += encrypted_chunk
                    try:
                        decompressed_data = self.decompress_data(
                            data=decrypted_data, iv=metadata["givn"]
                        )
                        decrypted_data = None
                    except (
                        py7zr.exceptions.Bad7zFile,
                        ZstdError,
                        py7zr.exceptions.DecompressionError,
                        py7zr.exceptions.UnsupportedCompressionMethodError,
                    ) as e:
                        pass

                del encrypted_chunk
                try:
                    if os.path.exists(chunk_path) and os.path.isfile(chunk_path):
                        os.remove(chunk_path)
                except:
                    pass

                try:
                    with open(restore_file_path, "ab") as original_file:
                        original_file.write(decompressed_data)
                        original_file.flush()
                except Exception as eee:
                    print("EEE" + str(eee))
                decompressed_data = None

                # Emit progress for UI: progress_number 0→100 as chunks complete (higher = more done)
                if progress_callback:
                    total_chunks = len(metadata["chunks"])
                    progress_pct = float(100 * chunk_idx) / float(total_chunks) if total_chunks else 0
                    try:
                        progress_callback(chunk_idx, total_chunks, progress_pct)
                    except Exception as cb_err:
                        logger.debug(f"Progress callback error: {cb_err}")

            #         decrypted_data+=encrypted_chunk
            # #         decryptor = cipher.decryptor()
            # #         padded_data = (
            # #             decryptor.update(encrypted_chunk) + decryptor.finalize()
            # #         )
            # #         decrypted_data += unpadder.update(padded_data)

            # # decrypted_data += unpadder.finalize()
            # #decompressed_data = self.decompress_data(data=decrypted_data,iv=metadata["givn"])
            if decrypted_data:
                if not decrypted_data == b"":
                    # if os.path.exists(restore_file_path)and os.path.isfile(restore_file_path):
                    #     os.remove(restore_file_path)
                    decompressed_data = self.decompress_data(
                        data=decrypted_data, iv=metadata["givn"]
                    )
                    with open(restore_file_path, "wb") as original_file:
                        original_file.write(decompressed_data)

            # with open(original_file_path, "wb") as original_file:
            #     decrypted_data = b""
            #     for chunk_info in metadata["chunks"]:
            #         chunk_path = chunk_info["path"]
            #         os.makedirs(os.path.dirname(chunk_path), exist_ok=True)
            #         expected_hash = chunk_info["hash"]
            #         self.download_from_server(chunk_path, chunk_path)
            #         # self.download_from_server(chunk_path, os.path.basename(chunk_path))
            #         with open(chunk_path, "rb") as chunk_file:
            #             encrypted_chunk = chunk_file.read()
            #             chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()

            #             if chunk_hash != expected_hash:
            #                 logger.error(f"Tampering detected in chunk: {chunk_path}")
            #                 raise ValueError("Tampering detected in chunk")

            #             decryptor = cipher.decryptor()
            #             padded_data = (
            #                 decryptor.update(encrypted_chunk) + decryptor.finalize()
            #             )
            #             decrypted_data += unpadder.update(padded_data)

            #     decrypted_data += unpadder.finalize()
            #     decompressed_data = self.decompress_data(decrypted_data)
            #     original_file.write(decompressed_data)

            # Verify file exists at target before declaring success
            if not os.path.isfile(restore_file_path):
                logger.error(f"Restore claimed success but file missing: {restore_file_path}")
                unc_log_error("restore_file_missing", 
                    FileNotFoundError(restore_file_path),
                    context=f"target={restore_file_path}")
                raise RuntimeError(f"File was not written to {restore_file_path}")
            file_size = os.path.getsize(restore_file_path)
            logger.info(f"File {original_file_path} successfully reassembled to {restore_file_path} ({file_size} bytes)")
            unc_log_info(f"RESTORE_SUCCESS | target={restore_file_path} | size={file_size}")
            try:
                self.cleanup_local_files(guid_folder)
            except:
                pass
            return True
        except Exception as e:
            logger.error(f"Error decrypting and reassembling file: {e}")
            self.cleanup_files(
                [chunk["path"] for chunk in metadata["chunks"]] + [restore_file_path]
            )
            raise RuntimeError(e)
        return False

    @staticmethod
    def get_remote_file_stat(backup_pid, file_name, bkpType=None):

        import requests
        import base64
        import urllib
        import urllib3

        try:
            file_url = f"http://{app.config['server_ip']}:{app.config['server_port']}/restore/file"
            payload = dict(
                backup_pid=backup_pid,
                file_name=file_name,
                obj=str(str(app.config.get("getCode", None))),
            )
            if bkpType:
                payload = dict(
                    backup_pid=backup_pid,
                    bType=bkpType,
                    file_name=file_name,
                    obj=str(str(app.config.get("getCode", None))),
                )

            response = requests.post(url=file_url, json=payload, timeout=3000)
            if response.status_code == 200:
                return response.json()

        except:
            return None
        return None

    def save_files(self, f_files, key, job_id, OpendedSh=None, **kwargs):
        self.job_id = job_id
        i = 0
        iNotDone = 0
        try:
            import asyncio

            for file in f_files:
                j = app.apscheduler.get_job(id=job_id)
                if j:
                    while not j.next_run_time:
                        time.sleep(10)
                        j = app.apscheduler.get_job(id=job_id)
                try:
                    i += 1
                    kwargs["kwargs"]["total_chunks"] = str(1)
                    kwargs["kwargs"]["totalfiles"] = str(len(f_files))
                    kwargs["kwargs"]["currentfile"] = str(i)
                    kwargs["kwargs"]["iNotDone"] = str(iNotDone)
                    self.save_file(file, key, job_id, OpendedSh=OpendedSh, **kwargs)
                    kwargs["kwargs"]["filesdone"] = str(i - iNotDone)
                    # dispatcher.send(signal=self.UPLOADED_JOB, sender=self, job_id=job_id,kwargs=kwargs)
                except Exception as ex:
                    iNotDone += 1
                    dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
                    print(str(ex))
        except Exception as ex:
            dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
            print(str(ex))
            logger.warning(f"Error backup nas {str(ex)}")
        # finally:
        #     if self.server_conn: 
        #         try:
        #            self.server_conn.tree.disconnect()
        #         except:
        #             pass
        #         try:
        #             self.server_conn.session.disconnect()
        #         except:
        #             pass
        #         try:
        #             self.server_conn.disconnectTree()
        #         except:
        #             pass

        metadata = {
            "original_path": "",
            "chunks": 0,
            "givn": "",
            "guid": "",
            # "juid": str(job_id),
            "juid": str(job_id),
            "scom": str(app.config.get("getCode", None)),
            "scon": str(app.config.get("getCodeHost", None)),
            "scombm": self.server_conn.remote_name,
            "scombs": self.share_location,
        }
        metadata.update({"mime_type_bkp": kwargs["kwargs"]["mime_type_bkp"]})
        kwargs["kwargs"]["filesdone"] = str(i - iNotDone)
        kwargs["kwargs"]["iNotDone"] = str(iNotDone)
        kwargs["kwargs"]["finished"] = True

        dispatcher.send(
            signal=self.UPLOADED_JOB,
            sender=self,
            job_id=job_id,
            metadata=metadata,
            kwargs=kwargs,
        )
    
    def save_files_SFTP(self, f_files, key, job_id, OpendedSh=None, **kwargs):
        self.job_id = job_id
        i = 0
        iNotDone = 0
        total_files = len(f_files)
        futures = []

        try:
            try:
                j = app.apscheduler.get_job(id=job_id)
                if j:
                    while not j.next_run_time:
                        time.sleep(10)
                        j = app.apscheduler.get_job(id=job_id)
            except:
                pass
            #for file in f_files:
            try:
                # SFTP initialization removed - using SMB (storeFile) for Windows UNC shares
                # SFTP requires SSH server (port 22) which Windows doesn't have by default
                # SMB uses port 445 which is native to Windows file sharing
                self.sftp_object = None  # Not used when storeFile (SMB) is active

                for i, file in enumerate(f_files, 1):
                    try:
                        job_kwargs = kwargs.copy()
                        job_kwargs["kwargs"] = dict(kwargs.get("kwargs", {}))  # deep copy
                        job_kwargs["kwargs"]["total_chunks"] = "1"
                        job_kwargs["kwargs"]["totalfiles"] = str(total_files)
                        job_kwargs["kwargs"]["currentfile"] = str(i)
                        job_kwargs["kwargs"]["iNotDone"] = str(iNotDone)
                        
                                
                        def worker(file_path=file, idx=i, job_kwargs=job_kwargs):
                            nonlocal iNotDone
                            try:
                                self.save_file(file_path, key, job_id, OpendedSh=OpendedSh,sFTP=self.sftp_object, **job_kwargs)
                                job_kwargs["kwargs"]["filesdone"] = str(idx - iNotDone)
                                # self.dispatcher.send(signal=self.UPLOADED_JOB, sender=self, job_id=job_id, kwargs=job_kwargs)
                                #dispatcher.send(signal=self.UPLOADED_JOB, sender=self,met job_id=job_id, kwargs=job_kwargs)
                            except Exception as ex:
                                iNotDone += 1
                                dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
                                print(f"[ERROR] {str(ex)}")
                                logger.warning(f"Error backup nas {str(ex)}")
                                traceback.print_exc()
                        
                        futures.append(self.executor.submit(worker))
                    except:
                        pass
            except:
                pass
            try:
                for future in as_completed(futures):
                    # Result fetch to surface exceptions, if any
                    try:
                        future.result()
                    except Exception as ex:
                        dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
                        print(f"[FUTURE ERROR] {str(ex)}")
                        logger.warning(f"Error backup nas {str(ex)}")
                        traceback.print_exc()   
                        kwargs["kwargs"]["filesdone"] = str(i - iNotDone)
                    #except Exception as ex:
                        iNotDone += 1
                        dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
                        print(str(ex))
            except:
                pass
        except Exception as ex:
            dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
            print(f"[MAIN ERROR] {str(ex)}")
            logger.warning(f"Error backup nas [MAIN ERROR] {str(ex)}")
            traceback.print_exc()

            # dispatcher.send(signal=self.ERROR, sender=self, __doc__=ex.__doc__)
            # print(str(ex))
        # finally:
        #     if self.server_conn: 
        #         try:
        #            self.server_conn.tree.disconnect()
        #         except:
        #             pass
        #         try:
        #             self.server_conn.session.disconnect()
        #         except:
        #             pass
        #         try:
        #             self.server_conn.disconnectTree()
        #         except:
        #             pass

        metadata = {
            "original_path": "",
            "chunks": 0,
            "givn": "",
            "guid": "",
            # "juid": str(job_id),
            "juid": str(job_id),
            "scom": str(app.config.get("getCode", None)),
            "scon": str(app.config.get("getCodeHost", None)),
            "scombm": self.server_conn.remote_name,
            "scombs": self.share_location,
        }
        metadata.update({"mime_type_bkp": kwargs["kwargs"]["mime_type_bkp"]})
        kwargs["kwargs"]["filesdone"] = str(i - iNotDone)
        kwargs["kwargs"]["iNotDone"] = str(iNotDone)
        kwargs["kwargs"]["finished"] = True

        dispatcher.send(
            signal=self.UPLOADED_JOB,
            sender=self,
            job_id=job_id,
            metadata=metadata,
            kwargs=kwargs,
        )

    def save_file(self, file_path, key, job_id=None, OpendedSh=None,sFTP=None, **kwargs):
        print(kwargs.get("asdf", "noval"))
        if not job_id:
            job_id = str(uuid.uuid4())
        bOpen = True
        bkupType = kwargs["kwargs"].get("bkupType", "full")
        ################################# WIP Start
        file_stat_remote = None
        file_stat_remote_data = None
        # bOpen = bkupType == "full"
        try:
            file_stat = os.stat(file_path)
            st_ino = file_stat.st_ino
            result = None
            file_stat_remote = self.get_remote_file_stat(
                backup_pid=str(job_id), file_name=file_path
            )
            file_stat_remote = file_stat_remote.get("result", None)

            compressed_data = None
            compressed_data = zlib.compress(
                b"{44A0C353-B685-4F9E-A3CF-08050440A814}", zlib.Z_BEST_COMPRESSION
            )
            compressed_data = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"

            remote_first_time = 0
            remote_last_time = 0
            if file_stat_remote:
                result = list(
                    filter(
                        lambda d: d.get("file_path_name").lower() == file_path.lower(),
                        file_stat_remote,
                    )
                )
                if result:
                    if bkupType == "full":
                        bOpen = True
                    if bkupType == "incremental":
                        result = result[0]
                        bOpen = False
                    if bkupType == "differential":
                        result = result[1]
                        bOpen = False
                else:
                    bOpen = True

            if bkupType == "full":
                bOpen = True
            elif bkupType == "incremental":
                print(f"perform incremental backup of this file : {file_path} ")
                if result:
                    if result.get("last_c", 0) <= file_stat.st_mtime:
                        bOpen = True

            elif bkupType == "differential":
                print(f"perform differential backup of this file : {file_path} ")
                if result:
                    if result.get("first_c", None) <= file_stat.st_mtime:
                        bOpen = True

        except:
            print("asdf")

        chunks = None
        iv = None
        metadata = None
        if not bOpen:
            file_stat_remote_data = self.get_remote_file_stat(
                backup_pid=str(job_id),
                file_name=file_path,
                bkpType=result.get("id", 234234),
            )
            if file_stat_remote_data:
                file_stat_remote_data = file_stat_remote_data.get("result", None)

            if file_stat_remote_data:
                chunks = file_stat_remote_data["incr"]["data"]["chunks"]
                iv = file_stat_remote_data["diff"]["data"]["givn"]
                metadata = file_stat_remote_data["diff"]["data"]
                x = float(kwargs["kwargs"]["currentfile"])
                nx = float(kwargs["kwargs"]["iNotDone"])
                kwargs["kwargs"]["filesdone"] = str(x - nx)
                dispatcher.send(
                    signal=self.UPLOADED,
                    sender=self,
                    file_path=file_path,
                    file_id=metadata["guid"],
                    metadata=metadata,
                    kwargs=kwargs,
                )
                return True
        ################################# WIP Ends
        guid = str(uuid.uuid4())
        


        chunks, iv = self.encrypt_and_chunk_file(
            file_path, key, guid, OpendedSh=OpendedSh,sFTP=sFTP, **kwargs
        )
        metadata = {
            "original_path": file_path,
            "chunks": chunks,
            "givn": iv.hex(),
            "guid": guid,
            "juid": str(job_id),
            "scom": str(app.config.get("getCode", None)),
            "scon": str(app.config.get("getCodeHost", None)),
            "scombm": self.server_conn.remote_name,
            "scombs": self.share_location,
        }

        metadata_path = os.path.join(guid, f"{os.path.basename(file_path)}.metadata")

        try:
            os.makedirs(guid, exist_ok=True)
            with open(metadata_path, "w") as metadata_file:
                json.dump(metadata, metadata_file)
            i = 1
            file_size = 0
            for chunk in chunks:
                kwargs["kwargs"]["total_chunks"] = str(len(chunks))
                kwargs["kwargs"]["quNu"] = str(i)
                # self.upload_to_server(chunk["path"])
                # file_stat = os.stat(chunk["path"])
                file_size += chunk["size"]  # file_stat.st_size
                kwargs["kwargs"]["file_size"] = file_size
                dispatcher.send(
                    signal=self.UPLOADED_PART,
                    sender=self,
                    file_path=file_path,
                    metadata=metadata["guid"],
                    per=(100 * i / len(chunks)),
                    kwargs=kwargs,
                )
                i = i + 1
            # m_metadata = [[]]
            # m_metadata[metadata["guid"]] = metadata
            try:
                self.update_master_metadata(file_path, metadata)
            except:
                pass

            self.cleanup_local_files(guid)
            x = float(kwargs["kwargs"]["currentfile"])
            nx = float(kwargs["kwargs"]["iNotDone"])
            kwargs["kwargs"]["filesdone"] = str(x - nx)
            dispatcher.send(
                signal=self.UPLOADED,
                sender=self,
                file_path=file_path,
                file_id=metadata["guid"],
                metadata=metadata,
                kwargs=kwargs,
            )
        except Exception as e:
            errr = e.__doc__
            logger.error(f"Error saving file: {errr}")
            self.cleanup_files([chunk["path"] for chunk in chunks] + [metadata_path])
            raise RuntimeError(errr)

    def update_master_metadata(self, file_path, metadata):
        with lock:
            try:
                with open(MASTER_METADATA_FILE, "r") as f:
                    master_metadata = json.load(f)

                # master_metadata[file_path] = metadata
                master_metadata[metadata["guid"]] = metadata

                with open(MASTER_METADATA_FILE, "w") as f:
                    json.dump(master_metadata, f)

                logger.info(f"Master metadata updated for {file_path}.")
            except Exception as e:
                errr = e.__doc__
                logger.error(f"Error updating master metadata: {errr}")
                raise RuntimeError(errr)

    def get_metadata_from_master(self, file_path):
        with lock:
            try:
                with open(MASTER_METADATA_FILE, "r") as f:
                    master_metadata = json.load(f)

                metadata = master_metadata.get(file_path)

                if not metadata:
                    raise FileNotFoundError(
                        f"Metadata for {file_path} not found in master metadata."
                    )

                return metadata
            except Exception as e:
                logger.error(f"Error retrieving metadata from master: {e}")
                # raise RuntimeError(e.__doc__)

    def upload_to_server(self, file_path):
        from urllib.parse import unquote
        import html
        # import mmap
        file_size = 0
        upload_start = time.time()
        try:
            file_path = html.unescape(unquote(file_path))
            local_file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            unc_log_info(f"UPLOAD_TO_SERVER_START | path={file_path} | size={local_file_size}")
            
            with open(file_path, "rb") as file_obj:
                # with OpenShFile(file_path, "rb") as f:
                # with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as file_obj:
                with lock:
                    # Create only the directory structure, NOT a folder with the filename
                    folder_path = os.path.dirname(file_path)
                    if folder_path:
                        self.server_conn.ensure_remote_folder(self.share_location, folder_path)

                    self.server_conn.storeFile(self.share_location, file_path, file_obj)

            upload_duration = time.time() - upload_start
            logger.info(f"Uploaded {file_path} to share.")
            unc_log_info(f"UPLOAD_TO_SERVER_SUCCESS | path={file_path} | duration={upload_duration:.2f}s")
            file_size = 1
        except Exception as e:
            upload_duration = time.time() - upload_start
            logger.error(f"Error uploading file to server: {e}")
            unc_log_error("upload_to_server", e, context=f"path={file_path} duration={upload_duration:.2f}s")
            # raise RuntimeError(e)
        return file_size

    def download_from_server(self, file_name, dest_path):
        download_start = time.time()
        unc_log_info(f"DOWNLOAD_START | remote={file_name} | local={dest_path}")
        
        try:
            for attempt in RETRY_LIMIT:
                try:
                    with open(dest_path, "wb") as file_obj:
                        with lock:
                            self.server_conn.retrieveFile(
                                self.share_location, file_name, file_obj
                            )
                    download_duration = time.time() - download_start
                    file_size = os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
                    logger.info(f"Downloaded {file_name} from share.")
                    unc_log_info(f"DOWNLOAD_SUCCESS | remote={file_name} | size={file_size} | duration={download_duration:.2f}s")
                    break
                except (SMBTimeout, NotReadyError, OperationFailure, OSError) as e:
                    logging.warning(f"Download attempt {attempt + 1} failed: {e}")
                    unc_log_error("download", e, context=f"attempt={attempt+1} remote={file_name}")
                    backoff = RETRY_BACKOFF_BASE**attempt
                    unc_log_info(f"DOWNLOAD_RETRY | attempt={attempt+1} | backoff={backoff}s")
                    print(f"Retrying to connect to NAS/File server...........{backoff}")
                    time.sleep(backoff)

        except Exception as e:
            download_duration = time.time() - download_start
            logger.error(f"Error downloading file from server: {e}")
            unc_log_error("download_from_server", e, context=f"remote={file_name} duration={download_duration:.2f}s")
            # raise RuntimeError(e)

    def cleanup_files(self, file_paths):
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {e}")

    def cleanup_local_files(self, folder_path):
        try:
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
            logger.info(f"Cleaned up files: {os.path.join(root, name)}")
        except Exception as e:
            logger.error(f"Error cleaning up folder {os.path.join(root, name)}: {e}")
            # raise RuntimeError(e)
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except Exception as e:
                    logger.error(
                        f"Error cleaning up children folders {os.path.join(root, name)}: {e}"
                    )
            logger.info(f"Cleaned up children folders: {os.path.join(root, name)}")
            # raise RuntimeError(e)
        try:
            os.rmdir(folder_path)
            logger.info(f"Cleaned up folder: {folder_path}")
        except Exception as e:
            logger.error(f"Error cleaning up folder {folder_path}: {e}")
            # raise RuntimeError(e)

    def create_folder_tree(self, conn, full_path):

        from smbprotocol.open import (
            Open as NASOpen,
            CreateDisposition,
            CreateOptions,
            DirectoryAccessMask,
            FileAttributes,
            FileInformationClass,
            FilePipePrinterAccessMask,
            ImpersonationLevel,
            ShareAccess,
        )
        from smbprotocol.exceptions import SMBException

        """
        Creates a folder tree on the SMB share. Optionally creates an empty file if a filename is at the end of the path.

        :param conn: An active SMBConnection instance
        :param full_path: Full path to a file or folder, e.g. '/folder1/folder2/file.txt'
        """
        import os

        # Normalize path
        full_path = full_path.strip("/")
        full_path = full_path.strip("\\")
        full_path = full_path.replace("/", os.sep)

        # folders =os.path.split(full_path)

        # Separate folder path and optional file
        # folder_path, file_name = os.path.split(full_path)
        #folders = os.path.split(full_path) if full_path else []
        folders = full_path.strip("/").split(os.sep) if full_path else []

        current_path = ""
        for folder in folders:
            current_path += (
                f"/{folder}" if current_path != "" else f"{folder}"
            )  # current_path += os.path.join(current_path, folder).replace("\\", "/")
            
            try:
                directory = NASOpen(conn.tree, current_path)
                # directory.create(
                #     disposition=CreateDisposition.FILE_OPEN,
                #     options=CreateOptions.FILE_DIRECTORY_FILE,
                #     desired_access=DirectoryAccessMask.FILE_LIST_DIRECTORY,
                # )

                directory.create(
                    ImpersonationLevel.Impersonation,
                    DirectoryAccessMask.GENERIC_READ
                    | DirectoryAccessMask.GENERIC_WRITE,
                    FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                    ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                    CreateDisposition.FILE_OPEN_IF,
                    CreateOptions.FILE_DIRECTORY_FILE,
                )

                directory.close()
                
            except Exception as e:
                # Folder probably doesn't exist, create it
                try:
                    directory = NASOpen(conn.tree, current_path)
                    directory.create(
                        ImpersonationLevel.Impersonation,
                        DirectoryAccessMask.GENERIC_READ
                        | DirectoryAccessMask.GENERIC_WRITE,
                        FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                        ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                        CreateDisposition.FILE_OPEN_IF,
                        CreateOptions.FILE_DIRECTORY_FILE,
                    )
                    directory.close()
                    print(f"Created folder: {current_path}")
                except SMBException as e:
                    print(f"Failed to create folder {current_path}: {e}")
                    raise

    def create_folder_tree_old(self, conn, full_path):

        # Separate the filename from the path
        # folder_path, file_name = os.path.split(full_path)
        file_name = None
        folder_path = os.path.split(full_path)

        # Create all folders in the path recursively
        # folders = folder_path.strip('/').split('/')
        folders = folder_path
        current_path = ""
        for folder in folders:
            current_path += f"/{folder}"
            try:
                print("")
                contents = conn.listPath(self.share_location, current_path)
            except:

                try:
                    conn.createDirectory(self.share_location, current_path)
                    print(f"Created folder: {current_path}")
                except Exception as e:
                    print(f"Failed to create folder {current_path}: {e}")
                    if "already exists" in str(e):
                        print(f"Directory '{folder}' already exists.")
                    else:
                        print(f"Failed to create directory '{folder}': {e}")
                        # raise RuntimeError(e)

        # Create the file at the end of the path
        if file_name:
            try:
                with conn.openFile(
                    f"{self.share_location}/{folder_path}/{file_name}", "w"
                ) as file:
                    file.write(b"")  # Empty content for now
                print(f"File '{file_name}' created successfully.")
            except Exception as e:
                print(f"Failed to create file '{file_name}': {e}")
                # raise RuntimeError(e)

    def disconnect(self):
        try:
            self.server_conn.close()
            print("Connection closed successfully")
        except:
            print("Connection close issue")


def handle_request(request_type, file_path, key, efs):
    try:
        if request_type == "save":
            efs.save_file(file_path, key)
        elif request_type == "retrieve":
            efs.decrypt_and_reassemble_file(file_path, key)
    except Exception as e:
        logger.error(f"Error handling {request_type} request for {file_path}: {e}")


def file_not_found_handler(sender, file_path, error):
    print(f"File not found error for file '{file_path}': {error}")


def access_error_handler(sender, file_path, error):
    print(f"Access error for file '{file_path}': {error}")


def uploaded_handler(sender, file_path, file_id, metadata, **kwargs):
    print(f"File '{file_path}' uploaded successfully.")
    print(f"metada : '{metadata}' uploaded successfully.")
    import requests
    import gzip
    import base64

    try:
        app.config["server_ip"]
    except:
        app.config["server_ip"] = "127.0.0.1"
        logger.error("Server IP is not set")
    try:
        app.config["server_port"]
    except:
        app.config["server_port"] = "53335"
    try:
        url = f"http://{app.config['server_ip']}:{app.config['server_port']}/uploadunc"
        headers = {
            "tcc": base64.b64encode(gzip.compress(json.dumps(metadata).encode())),
            "v": base64.b64encode(gzip.compress(json.dumps(kwargs).encode())),
        }
        response = requests.post(url, headers=headers, timeout=3000)
    except requests.ConnectionError as ce:
        logger.error(str(ce))
    except requests.HTTPError as he:
        logger.error(str(he))
    except requests.JSONDecodeError as je:
        logger.error(str(je))


def uploaded_handler_part(sender, file_path, file_id, per):
    print(f"File '{file_id} {file_path}' {per} uploaded successfully.")


def connection_rejected_handler(sender, file_path, error):
    print(f"Connection rejected for file '{file_path}': {error}")


# Example Usage
if __name__ == "__main__":
# keya = getCode() #os.urandom(32)  # AES-256 key from environment variable or secure key management
# key =  hashlib.sha256(keya.encode()).digest()
# for i in range(25):
#     print(key.hex())
#     key = hashlib.sha256(key).digest()
    key =getKey()
    efs = EncryptedFileSystem('192.168.2.50', 'danish2', 'Server@1234', 'D2')
    if efs:
        dispatcher.connect(file_not_found_handler, signal=efs.FILE_NOT_FOUND)
        dispatcher.connect(access_error_handler, signal=efs.ACCESS_ERROR)
        dispatcher.connect(uploaded_handler, signal=efs.UPLOADED)
        dispatcher.connect(uploaded_handler_part, signal=efs.UPLOADED_PART)
        dispatcher.connect(connection_rejected_handler, signal=efs.CONNECTION_REJECTED)

        # Example file paths
        save_file_path = "D:\\Users\\user\\Downloads\\cv's apex university\\MCA 2025\\Akansha Sharma-MCA-2025-Web developer.docx"
        retrieve_file_path = "D:\\Users\\user\\Downloads\\cv's apex university\\MCA 2025\\Akansha Sharma-MCA-2025-Web developer.docx"

        # Save file to server
        df={}
        df["asdf"]=213
        efs.save_file(save_file_path, key,None,kwargs=df)
        efs.save_file(save_file_path, key)
        logger.info("File saved to server.")

        # Retrieve and decrypt file from server
        # efs.decrypt_and_reassemble_file(retrieve_file_path, key)
        # logger.info("File retrieved and decrypted from server.")

        # # Simulate concurrent requests for stress testing
        # requests = [("save", f"path/to/local/file{i}.txt", key) for i in range(10)] + \
        #            [("retrieve", f"path/to/local/file{i}.txt", key) for i in range(10)]

        # with ThreadPoolExecutor(max_workers=20) as executor:
        #     futures = [executor.submit(handle_request, request_type, file_path, key, efs) for request_type, file_path, key in requests]
        #     for future in as_completed(futures):
        #         future.result()  # To raise exceptions, if any

        logger.info("All requests handled.")

from ast import Param, Pass, Try
import asyncio
from binascii import unhexlify
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor, as_completed
from datetime import date
import datetime
from email import header
from functools import partial
import gzip
import imp
from importlib.machinery import OPTIMIZED_BYTECODE_SUFFIXES
from io import BytesIO
import json
import lzma
import mmap
import multiprocessing
from multiprocessing.pool import Pool
import multiprocessing.shared_memory
import queue
from sre_constants import SUCCESS
import threading
import time
import uuid
from zipfile import ZipFile, ZipInfo
import zlib
from Crypto.Cipher.AES import block_size
#from appdirs import com
from appdirs import AppDirs
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from apscheduler.schedulers.background import BackgroundScheduler
from onedrive.OneDriveClient import OneDriveClient
from gd.GDClient import GDClient
from flask import url_for
from flask_apscheduler import APScheduler
from flask_apscheduler.utils import CronTrigger
import py7zr
from requests import request
import scheduler
import fClient

from fClient.fingerprint import get_miltiprocessing_cpu_count, getCode, getCodeHost, getCodea, getKey
from fClient import SIGNATURE_MAP_COMPRESSION_LEVEL, app
from fClient.module3 import FileSnapshotter
from fClient.shad import OpenShFile
from fClient.xxh import FileDig
import fClient.xxh
import os

import os, math, gzip, base64, requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import ctypes
from ctypes import wintypes

# 748 minutes and 48 seconds
RETRY_LIMIT =[
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,  
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
AUTO_RETRY_MAX = 3

def broadcast_ws_message(cl, task_queue,kill=False):
    
    while True:
        try:
            backup_status = task_queue.get()
            if backup_status is None:  # Exit signal
                break
            
            try:
                            
                # if cl.connected: cl.disconnect()
                if not cl.connected:
                    cl.connect(
                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                    )
                if cl.connected:
                    cl.emit(
                        "starting",
                        json.dumps(
                            backup_status
                        ),
                        #"/starting",
                    )
                    time.sleep(0.1)
            except Exception as s:
                print(str(s))
            finally:
                try:
                    if cl.connected: cl.disconnect()
                    print("")        
                except:
                    pass
                    time.sleep(0.1)  # Prevent flooding

        except Exception as e:
            print(f"Error in backup thread: {e}")
        # if kill:
        #     task_queue=None

    return

##kartik
import logging
import logging.handlers
import sys
from fClient.structured_logging import log_event, log_chunk_event, ensure_job_id

# Create a logs folder if it doesn't exist
os.makedirs("every_logs", exist_ok=True)

LOG_FILE = "every_logs/class1x.log"

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
try:
    event_handler = logging.handlers.NTEventLogHandler(appname="ABS")
    event_handler.setLevel(logging.DEBUG)
    event_formatter = logging.Formatter(
        "[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    event_handler.setFormatter(event_formatter)
    logger.addHandler(event_handler)
except Exception as e:
    logger.warning(f"Could not attach Windows Event Viewer handler: {e}")


##kartik
def get_file_size_locked(path):
    
    GENERIC_READ = 0x80000000
    FILE_SHARE_READ = 1
    FILE_SHARE_WRITE = 2
    FILE_SHARE_DELETE = 4
    OPEN_EXISTING = 3
    FILE_ATTRIBUTE_NORMAL = 0x80

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    CreateFileW = kernel32.CreateFileW
    CreateFileW.restype = wintypes.HANDLE
    CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
    ]

    GetFileSizeEx = kernel32.GetFileSizeEx
    GetFileSizeEx.restype = wintypes.BOOL
    GetFileSizeEx.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_longlong)]

    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = [wintypes.HANDLE]
    handle = CreateFileW(
        path,
        0,  # metadata only (no read/write)
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        None
    )
    if handle == wintypes.HANDLE(-1).value:  # INVALID_HANDLE_VALUE
        raise OSError(f"Cannot open file: {path}")

    size = ctypes.c_longlong()
    if not GetFileSizeEx(handle, ctypes.byref(size)):
        CloseHandle(handle)
        raise OSError(f"Failed to get size for: {path}")

    CloseHandle(handle)
    return size.value


def process_folder(folder, all_types, all_selected_types):
    """Function to process a single folder and return found files (>0 bytes only)"""
    ff_files = []
    stack = []
    
    walk_data = list(os.walk(folder))  

    for root, dirs, files in walk_data:
        for f in files:
            file_path = os.path.join(root, f)
            try:
                size = get_file_size_locked(file_path)
                if size > 0:
                    if all_types or any(f.endswith(ext) for ext in all_selected_types):
                        ff_files.append(file_path)
            except (OSError, FileNotFoundError):
                # Skip inaccessible/deleted files safely
                continue

        stack.extend(os.path.join(root, d) for d in dirs)
        break  # stack-based processing

    return ff_files, stack

def process_folder_old(folder,all_types,all_selected_types):
    """ Function to process a single folder and return found files """
    ff_files = []
    stack = []
    
    # Convert os.walk() generator to a list before processing
    walk_data = list(os.walk(folder))  

    for root, dirs, files in walk_data:
        if all_types:
            ff_files.extend(os.path.join(root, f) for f in files)
        else:
            ff_files.extend(os.path.join(root, f) for f in files if any(f.endswith(ext) for ext in all_selected_types))            
        
        # Collect directories for further processing
        stack.extend(os.path.join(root, d) for d in dirs)
        
        # Break to avoid deep recursion (stack-based processing)
        break

    return ff_files, stack

def get_optimal_chunk_size(file_size, base_chunk_size=256 * 1024 * 1024,isOnline=False):
        """
        Adjust chunk_size to ensure file_size % chunk_size == 0.
    
        :param file_size: Total size of the file in bytes.
        :param base_chunk_size: Starting chunk size (default 128MB).
        :return: Optimized chunk size.
        """
        # if file_size < base_chunk_size:  # Stop at 1MB minimum
        #     return file_size

        # while file_size % base_chunk_size != 0:
        #     base_chunk_size //= 2  # Reduce chunk size to find an exact divisor
        #     if base_chunk_size < 1 * 1024 * 1024:  # Stop at 1MB minimum
        #         base_chunk_size = 1 * 1024 * 1024
        #         break
        # return file_size
        min_chunk_size = 100 * 1024 * 1024  # 1MB
        if isOnline:
            min_chunk_size = 10 * 1024 * 1024  # 1MB

        while file_size % base_chunk_size != 0:
            #base_chunk_size //= 2
            base_chunk_size = base_chunk_size -(min_chunk_size)
            if base_chunk_size < min_chunk_size:
                base_chunk_size = min_chunk_size
                break

        return base_chunk_size


def cjb_Desktop(**params):
    print("job desktop started ")
    from win32com import client

    try:
        import pythoncom

        print(params["source"])
        pythoncom.CoInitialize()
        shell = client.Dispatch("WScript.Shell")
        desktop_path = shell.SpecialFolders("Desktop")
        print(desktop_path)
        zip_filename = ""
        # zip_filename = os.path.join(
        #     app.config["UPLOAD_FOLDER"], f"Desktop_{getCode()}_{str(time.time())}.zip"
        # )
        # # zip_filename = os.path.join("D:\\ApnaBackup", f"Desktop_{scheduler.host_name}_{str(time.time())}.zip")
        # with ZipFile(zip_filename, "w") as zipf:
        #     for root, dirs, files in os.walk(desktop_path):
        #         for file in files:
        #             zipf.write(
        #                 os.path.join(root, file),
        #                 os.path.relpath(os.path.join(root, file), desktop_path),
        #             )
        return zip_filename

    except Exception as er:
        print(str(er))
    print("######################################################### ")


def cjb_Download():
    print("job Downloads started ")
    from win32com import client
    import winreg
    import os

    cjb_Download_folder_name = ""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        ) as key:
            path, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
            cjb_Download_folder_name = path
            print(cjb_Download_folder_name)
    except FileNotFoundError as fne:
        print(str(fne))
        pass

    if cjb_Download_folder_name == "":
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                path, _ = winreg.QueryValueEx(
                    key, "{7D83EE9B-2244-4E70-B1F5-5393042AF1E4}"
                )
                cjb_Download_folder_name = path
                print(cjb_Download_folder_name)
        except FileNotFoundError as fne:
            print(str(fne))
            pass

    if cjb_Download_folder_name.startswith("%USERPROFILE%"):
        cjb_Download_folder_name = os.path.expanduser(
            os.path.expandvars(cjb_Download_folder_name)
        )

    try:

        zip_filename = os.path.join(
            app.config["UPLOAD_FOLDER"], f"Downloads_{getCode()}_{str(time.time())}.zip"
        )
        with ZipFile(zip_filename, "w") as zipf:
            for root, dirs, files in os.walk(cjb_Download_folder_name):
                for file in files:
                    zipf.NameToInfo("kkkkkkkkk", ZipInfo("file"))
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(
                            os.path.join(root, file), cjb_Download_folder_name
                        ),
                    )
        return zip_filename

    except Exception as er:
        print(str(er))
        pass
        # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)

    # scheduler.add_listener(send_to_server,EVENT_JOB_EXECUTED)
    print("######################################################### ")


def cjb_Documents():
    print("job Documents started ")
    from win32com import client
    import winreg
    import os

    cjb_Download_folder_name = ""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        ) as key:
            path, _ = winreg.QueryValueEx(key, "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}")
            cjb_Download_folder_name = path
            print(cjb_Download_folder_name)
    except FileNotFoundError as fne:
        print(str(fne))
        # raise Exception(FileNotFoundError)
        # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)
        # pass
    if cjb_Download_folder_name == "":
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                path, _ = winreg.QueryValueEx(key, "Personal")
                cjb_Download_folder_name = path
                print(cjb_Download_folder_name)
        except FileNotFoundError as fne:
            print(str(fne))
            # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)
            # pass

    if cjb_Download_folder_name == "":
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                path, _ = winreg.QueryValueEx(key, "Documents")
                cjb_Download_folder_name = path
                print(cjb_Download_folder_name)
        except FileNotFoundError as fne:
            print(str(fne))
            # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)
            # pass

    if cjb_Download_folder_name == "":
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                path, _ = winreg.QueryValueEx(key, "My Documents")
                cjb_Download_folder_name = path
                print(cjb_Download_folder_name)
        except FileNotFoundError as fne:
            print(str(fne))
            # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)
            # pass

    if cjb_Download_folder_name.startswith("%USERPROFILE%"):
        cjb_Download_folder_name = os.path.expanduser(
            os.path.expandvars(cjb_Download_folder_name)
        )

    try:

        # zip_filename = os.path.join(
        #     app.config["UPLOAD_FOLDER"], f"Documents_{getCode()}_{str(time.time())}.zip"
        # )
        # with ZipFile(zip_filename, "w") as zipf:
        #     for root, dirs, files in os.walk(cjb_Download_folder_name):
        #         for file in files:
        #             zipf.write(
        #                 os.path.join(root, file),
        #                 os.path.relpath(
        #                     os.path.join(root, file), cjb_Download_folder_name
        #                 ),
        #             )

        for root, dirs, files in os.walk(cjb_Download_folder_name):
            sgetcode =str(app.config.get("getCode",None))
            for file in files:
                zip_filename = os.path.join(
                    # app.config["UPLOAD_FOLDER"], f"Documents_{getCode()}_{str(time.time())}.zip"
                    app.config["UPLOAD_FOLDER"],
                    f"Documents_{sgetcode}_{str(file).replace(':','@').replace(os.pathsep,'#')}_{str(time.time())}.zip",
                )
                
                with ZipFile(zip_filename, "w") as zipf:
                    try:
                        print(
                            str(
                                os.path.relpath(
                                    os.path.join(root, file), cjb_Download_folder_name
                                )
                            )
                        )
                    except Exception as dfe:
                        print(str(dfe))
                    print(str(os.path.join(root, file)))
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(
                            os.path.join(root, file), cjb_Download_folder_name
                        ),
                    )

        return zip_filename

    except Exception as er:
        print(str(er))
        # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)

    # scheduler.add_listener(send_to_server,EVENT_JOB_EXECUTED)
    print("######################################################### ")


def cjb_Videos():
    print("job Videos started ")
    from win32com import client
    import winreg
    import os

    cjb_Download_folder_name = ""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        ) as key:
            path, _ = winreg.QueryValueEx(key, "{18989B1D-99B5-455B-841C-AB7C74E4DDFC}")
            cjb_Download_folder_name = path
            print(cjb_Download_folder_name)
    except FileNotFoundError as fne:
        print(str(fne))
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                path, _ = winreg.QueryValueEx(key, "My Video")
                cjb_Download_folder_name = path
                print(cjb_Download_folder_name)
        except FileNotFoundError as fne:
            print(str(fne))
            # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)
            # pass
    if cjb_Download_folder_name.startswith("%USERPROFILE%"):
        cjb_Download_folder_name = os.path.expanduser(
            os.path.expandvars(cjb_Download_folder_name)
        )

    try:
        import os
        import threading
        sgetcode =str(app.config.get("getCode",None))
        ffile = f"Videos_{sgetcode}_{str(time.time())}.zip"
        zip_filename = os.path.join(app.config["UPLOAD_FOLDER"], ffile)
        with ZipFile(zip_filename, "w", 9, compresslevel=9) as zipf:
            for root, dirs, files in os.walk(cjb_Download_folder_name):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(
                            os.path.join(root, file), cjb_Download_folder_name
                        ),
                    )
        # threading.Thread(
        #     target=start_file_streaming(zip_filename, ffile, cjb_Download_folder_name)
        # ).start()
        start_file_streaming(zip_filename, ffile, cjb_Download_folder_name)
        return zip_filename

    except Exception as er:
        print(str(er))
        # raise er
        # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)

    # scheduler.add_listener(send_to_server,EVENT_JOB_EXECUTED)
    print("######################################################### ")


def cjb_Pictures():
    print("job Pictures started ")
    from win32com import client
    import winreg
    import os

    cjb_Download_folder_name = ""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        ) as key:
            path, _ = winreg.QueryValueEx(key, "{33E28130-4E1E-4676-835A-98395C3BC3BB}")
            cjb_Download_folder_name = path
            print(cjb_Download_folder_name)
    except FileNotFoundError as fne:
        print(str(fne))
        # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)
        # pass

    if cjb_Download_folder_name == "":
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                rf"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                path, _ = winreg.QueryValueEx(key, "My Pictures")
                cjb_Download_folder_name = path
                print(cjb_Download_folder_name)
        except FileNotFoundError as fne:
            print(str(fne))
            # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)
            # pass

    if cjb_Download_folder_name.startswith("%USERPROFILE%"):
        cjb_Download_folder_name = os.path.expanduser(
            os.path.expandvars(cjb_Download_folder_name)
        )
    try:
        sgetcode =str(app.config.get("getCode",None))
        zip_filename = os.path.join(
            app.config["UPLOAD_FOLDER"], 
            f"Pictures_{sgetcode}_{str(time.time())}.zip"
        )
        with ZipFile(zip_filename, "w") as zipf:
            for root, dirs, files in os.walk(cjb_Download_folder_name):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(
                            os.path.join(root, file), cjb_Download_folder_name
                        ),
                    )
        return zip_filename

    except Exception as er:
        print(str(er))
        # scheduler.add_listener(send_to_server,EVENT_JOB_ERROR)

    # scheduler.add_listener(send_to_server,EVENT_JOB_EXECUTED)
    print("######################################################### ")


import os
import re
import sqlite3

try:
    from fClient.db_config import USE_MSSQL
    from fClient.db import get_session_for_project
except ImportError:
    USE_MSSQL = False


def _safe_table_name(name):
    """Allow only alphanumeric and underscore for table names (SQL injection safety)."""
    if not name or not re.match(r"^[a-zA-Z0-9_]+$", name):
        return None
    return name


def filter_files_by_last_modified(src_folder, db_path, table_name):
    safe_table = _safe_table_name(table_name)
    last_modified_dict = {}

    if USE_MSSQL and safe_table:
        from sqlalchemy import text
        project_id = os.path.splitext(os.path.basename(db_path))[0] or db_path
        try:
            with get_session_for_project(project_id) as session:
                result = session.execute(text(f"SELECT file, last_modified FROM {safe_table}"))
                rows = result.fetchall()
                last_modified_dict = {row[0]: row[1] for row in rows}
        except Exception:
            pass
    else:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=30000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA cache_size=-64000")
            cursor = conn.cursor()
            cursor.execute(f"SELECT file, last_modified FROM {table_name}")
            sqlite_data = cursor.fetchall()
            last_modified_dict = {file_name: last_modified for file_name, last_modified in sqlite_data}
        finally:
            conn.close()

    filtered_files = []
    for root, dirs, files in os.walk(src_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if (
                file_name not in last_modified_dict
                or os.stat(file_path).st_mtime > last_modified_dict[file_name]
            ):
                filtered_files.append(file_path)

    return filtered_files

    # # Example usage:
    # src_folder = "YOUR_SOURCE_FOLDER_PATH_HERE"
    # db_path = "your_database.db"
    # table_name = "your_table"

    # filtered_files = filter_files_by_last_modified(src_folder, db_path, table_name)

    # # Do whatever you want with the filtered files here
    # for file_path in filtered_files:
    #     print(file_path)
    
###parallel processing 
def process_file(file_info):
    (
        file, current_index, total_files,
        trg_folder, p_name, repo, authId, job_Start,
        p_NameText, p_IdText, bkupType,
        src_folder, OpendedSh, this_file_id
    ) = file_info

    try:
        #logger.info(f"[{current_index}/{total_files}] Processing {file}...")

        start_file_streaming(
            file,
            os.path.basename(file),
            os.path.dirname(file),
            trg_folder,
            p_name,
            repo,
            authId,
            job_Start,
            ftype="folder",
            p_NameText=p_NameText,
            p_IdText=p_IdText,
            bkupType=bkupType,
            currentfile=current_index,
            totalfiles=total_files,
            file_id=this_file_id,
            src_location=src_folder,
            OpendedSh=OpendedSh,
            tfi=this_file_id,
        )

        return (file, True, None)

    except Exception as e:
        #logger.exception(f"Error processing file: {file}")
        return (file, False, str(e))


def run_file_batch(
    file_list,
    trg_folder, p_name, repo, authId,
    p_NameText, p_IdText, bkupType,
    src_folder, OpendedSh, this_file_id
):
    total_files = len(file_list)
    job_Start = datetime.utcnow().isoformat()

    file_args = [
        (
            file_path, idx + 1, total_files,
            trg_folder, p_name, repo, authId, job_Start,
            p_NameText, p_IdText, bkupType,
            src_folder, OpendedSh, this_file_id
        )
        for idx, file_path in enumerate(file_list)
    ]

    #logger.info(f"Starting multiprocessing for {total_files} files...")

    with multiprocessing.Pool(processes=get_miltiprocessing_cpu_count()) as pool:
        results = pool.map(process_file, file_args)

    failed = [r for r in results if not r[1]]
    #logger.info(f"Processing complete. Success: {total_files - len(failed)}, Failed: {len(failed)}")

    return results

##kartik 301225

import os
import subprocess
import re
import tempfile

# ================= CONFIG =================
MAX_THREADS = 5        # Python threads (same as your code)
ROBO_MT = 8           # Robocopy internal threads
# =========================================

lock = threading.Lock()

def is_path_under(path, root):
    try:
        path = os.path.realpath(path)
        root = os.path.realpath(root)

        path = os.path.normcase(os.path.normpath(path))
        root = os.path.normcase(os.path.normpath(root))

        return os.path.commonpath([path, root]) == root
    except Exception:
        return False


def get_subfolders(path):
    try:
        return [
            os.path.join(path, d)
            for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))
        ]
    except PermissionError:
        return []


def run_robocopy(**src_path):
    data = []

    if not src_path['search_extensions']:
        file_masks  = ["*.*"]
    else:
        file_masks = []
        for ext in src_path['search_extensions']:
            if ext.startswith("*."):
                file_masks.append(ext)
            elif ext.startswith("."):
                file_masks.append(f"*{ext}")   
            else:
                file_masks.append(f"*.{ext}")
    dest_dir = tempfile.gettempdir()
    if src_path.get("recursive", True):
        depth_flags = ["/E"]
    else:
        depth_flags = ["/LEV:1"]
    cmd = [
        "robocopy",
        src_path["source_dir"],
        dest_dir,
        *file_masks,
        *depth_flags,
        "/L","/BYTES",
        "/FP",            # FULL PATH
        f"/MT:{ROBO_MT}",
        "/R:0", "/W:0",
        "/NJH", "/NJS","/XJ",
        "/NDL", "/NC","/NP"
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        # stderr=subprocess.DEVNULL
        stderr=subprocess.STDOUT

    )
    file_line_re = re.compile(r"\s*(\d+)\s+(.*)")
    for raw_line in proc.stdout:
        line = raw_line.decode("utf-8", errors="ignore").strip()
        # line = line.split("\r")[0].strip()

        m = file_line_re.match(line)
        if not m:
            continue

        size = int(m.group(1))
        path = m.group(2).strip()

        # EXACT LOGIC YOU ASKED FOR
        # print(line)
        if os.path.isabs(path) and is_path_under(path, src_path["source_dir"]):
            # with lock:
            d = {'id': unique_time_float(),'path':path,'size': size}
            data.append(d)

    proc.wait()

    # # final update
    # src_path["task_queue"].put({
    #     "backup_jobs": [
    #         {
    #             "status": "counted",
    #             "paused": False,
    #             "name": src_path["p_NameText"],
    #             "agent": str(app.config.get("getCodeHost")),
    #             "scheduled_time": time.strftime(
    #                 "%H:%M:%S",
    #                 time.localtime(float(src_path["job_Start"]))
    #             ),
    #             "progress_number": len(data),
    #             "id": src_path["job_Start"],
    #             "repo": src_path["repo"]
    #         }
    #     ]
    # })

    # src_path["task_queue"].put(None)
    return {'data':data,'meta_data':src_path['meta_data']}

def worker(queue,f_files_robocount):
    while True:
        with lock:
            if not queue:
                return
            src = queue.pop()
        data =  run_robocopy(**src)
        with lock:
            f_files_robocount.extend(data['data'])
        data['meta_data']['totalfiles'] = len(f_files_robocount)
        url = f"http://{app.config['server_ip']}:{app.config['server_port']}/saveinitlog"
        if not len(data['data']) == 0:
            r = requests.post(url,json=data) # , stream=True)     
            print(r)

def list_files_with_robocopy(
    source_dir,
    search_extensions,
    task_queue,
    p_NameText,
    job_Start,
    repo,
    metadata
    ):
    p_targets = {
        "source_dir": source_dir,
        "search_extensions": search_extensions,
        "task_queue":task_queue,
        "p_NameText": p_NameText,
        "job_Start": job_Start,
        "repo": repo,
        "meta_data":metadata
    }

    # level1 = get_subfolders(source_dir)

    # # Same logic as your original code
    # if len(level1) == 1:
    #     level2 = get_subfolders(level1[0])
    #     folders = level2 if level2 else level1
    # else:
    #     folders = level1

   
    # # targets = [{
    # #     "source_dir": folder,
    # #     "search_extensions": search_extensions,
    # #     "task_queue":task_queue,
    # #     "p_NameText": p_NameText,
    # #     "job_Start": job_Start,
    # #     "repo": repo,
    # #     "meta_data":metadata
    # # } for folder in folders]

    # targets = []

    # targets.append(p_targets)

    f_files_robocount = []

    level1 = get_subfolders(source_dir)

    targets = []

    
    if not level1:
        targets.append({
            "source_dir": source_dir,
            "search_extensions": search_extensions,
            "task_queue": task_queue,
            "p_NameText": p_NameText,
            "job_Start": job_Start,
            "repo": repo,
            "meta_data": metadata,
            "recursive": True
        })

    else:
      
        targets.append({
            "source_dir": source_dir,
            "search_extensions": search_extensions,
            "task_queue": task_queue,
            "p_NameText": p_NameText,
            "job_Start": job_Start,
            "repo": repo,
            "meta_data": metadata,
            "recursive": False   # root files only
        })

        
        for folder in level1:
            targets.append({
                "source_dir": folder,
                "search_extensions": search_extensions,
                "task_queue": task_queue,
                "p_NameText": p_NameText,
                "job_Start": job_Start,
                "repo": repo,
                "meta_data": metadata,
                "recursive": True
            })

    if not targets:
        print(0)
        return

    queue = targets.copy()
    threads = []

    for _ in range(min(get_miltiprocessing_cpu_count(), len(queue))):
        t = threading.Thread(target=worker, args=(queue,f_files_robocount,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return f_files_robocount
##kartik 301225

##030126
# def unique_time_float():
#     import time
#     base = time.time()
#     nano = time.time_ns() % 1_000_000_000
#     tid = threading.get_ident() % 1000
#     return base + ((nano + tid) / 1e18)



# global, process-safe counter
_last_ts = 0.0
_seq = 0
_lock = threading.Lock()

def unique_time_float():
    import time
    global _last_ts, _seq

    with _lock:

        ts = round(time.time(), 6)  # microsecond precision ONLY

        if ts == _last_ts:
            _seq += 1
            # add smallest representable increment
            ts += _seq * 1e-6
        else:
            _seq = 0
            _last_ts = ts
        return ts
##030126

def create_localbkp_job(
    src_folder,
    trg_folder,
    p_name,
    repo,
    authId,
    p_NameText,
    p_IdText,
    bkupType,
    file_pattern,
    repo_d,
    this_file_id_j,
    scheduler_dict,
    
    ):
    job_Start = unique_time_float()
    schedulerid=None
    schedulersrno=0
    shadow_id=None
    OpendedSh=None
    try:
        if not repo:
            repo="LAN"

        repo =str(repo).upper() 

        if repo in ['AWS','AWSS3','GDRIVE','ONEDRIVE','AZURE']:
            payload = {"action":"repo_check", "rep":repo}
            req_onserver = requests.post(f'http://{app.config["server_ip"]}:{app.config["server_port"]}/dststorage',json=payload)
            response_data = req_onserver.json()
            if req_onserver.status_code in [200,'200', 201,'201']:
                if 'valid' in response_data and response_data['valid'] == False:
                    raise RuntimeError(f'Destination storage not configured {repo}')
                else: 
                    payload = {"rep":repo, "key":app.config.get('getCode', None)}
                    with requests.post(f'http://{app.config["server_ip"]}:{app.config["server_port"]}/download_cred',json=payload, stream=True) as r:
                        r.raise_for_status()
                        if repo == 'ONEDRIVE':
                            enc_file_name = f"OneDrive_credentials.enc"
                        elif repo == 'AZURE':
                            enc_file_name = f"Azure_credentials.enc"
                        elif repo == 'GDRIVE':
                            enc_file_name = f"token.pickle"
                        elif repo == 'AWSS3':
                            enc_file_name = f"AWS_credentials.enc"

                        with open(enc_file_name, "wb") as f:
                            import shutil
                            # shutil.copyfileobj(r.cont, f)
                            f.write(r.content)
            elif req_onserver.status_code in [400,404,500]:
                raise RuntimeError(f'Unexpected problem {repo},Please reconfigure or Contact for help')

        if scheduler_dict:
            schedulerid = scheduler_dict.get("schedulerid",None)
            # if schedulerid:
            #     print("\nPPPPPPPPPPPP Scheduler id : " , schedulerid,'\n')
            # else:
            #     print("\nno scheluser id\n")

        if schedulerid: 
            if scheduler_dict.get("job_srno",None)>1:
                if not app.config.get(schedulerid,None):
                    t=time.time()
                    while not app.config.get(schedulerid,None):
                        print(f"waiting for schelueid job object to be created {app.config.get(schedulerid,None)}")
                        if time.time()-t>10:
                            break
            
            if app.config.get(schedulerid,None):
                shadow_data =app.config[schedulerid]
                if time.time() - float( shadow_data["datetime_start"])<=60*15:
                    shadow_id =shadow_data["shadow_id"]
                else:
                    shadow_id=None

        OpendedSh = OpenShFile(src_folder,shadow_scheduler_GUID=shadow_id)
        skip_vss = os.getenv("AB_SKIP_VSS", "0").lower() in {"1", "true", "yes", "on"}
        if skip_vss:
            logger.warning("AB_SKIP_VSS enabled; using direct file read")
            OpendedSh.OpenFlatFile()
        else:
            try:
                OpendedSh.OpenFileSha()
            except Exception as shadow_error:
                logger.warning(
                    "Shadow copy failed; falling back to direct read: %s",
                    shadow_error,
                )
                OpendedSh.OpenFlatFile()

        if schedulerid:
            shadow_data = {"datetime_start":time.time(),"shadow_id" : OpendedSh.shadow_id}
            app.config[schedulerid] =shadow_data
            shadow_id = OpendedSh.shadow_id

        create_localbkp_job_original(src_folder,trg_folder,p_name,repo,authId,p_NameText,p_IdText
                                     ,bkupType,job_Start,file_pattern,repo_d,this_file_id_j
                                     ,schedulerid=schedulerid
                                     ,o_OpendedSh=OpendedSh)
        
    except Exception as errr_bkp:
         ##kartik

        try:
            print("\n\n----- WEBSOCKET EMIT START -----")
            from fClient.cktio import cl_socketio_obj
            # Attempt connection
            if not cl_socketio_obj.connected:
                print(" Trying to connect to:",
                        f"ws://{app.config['server_ip']}:{app.config['server_port']}")
                try:
                    cl_socketio_obj.connect(
                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                    )
                except Exception as socket_conn_err:
                    print(" Connection attempt failed:", socket_conn_err)

            print(" Connected =", cl_socketio_obj.connected)

            if cl_socketio_obj.connected:
                print(" Connection successful  Emitting now...")

                try:
                    cl_socketio_obj.emit(
                        "backup_data",
                        json.dumps({
                            "backup_jobs": [{
                                "status": "failed",
                                "reason": str(errr_bkp),
                                "paused": False,
                                "name": p_NameText,
                                "agent": getCodeHost(),
                                "finished": True,
                                "id": job_Start,
                                "repo": repo
                            }]
                        })
                    )
                    print("EMIT SUCCESS")
                except Exception as emit_error:
                    print("EMIT FAILED:", emit_error)

            else:
                print(" Emit skipped  socket is NOT connected")

            # Always try to disconnect
            try:
                cl_socketio_obj.disconnect()
                print(" Disconnected successfully")
            except Exception as disc_err:
                print(" Disconnect failed:", disc_err)

            print("----- WEBSOCKET EMIT END -----\n\n")

        except Exception as websocket_err:
            print(" Fatal WebSocket error:", websocket_err)

        raise RuntimeError(errr_bkp)
        ##kartik
    finally:
         if scheduler_dict:
            if scheduler_dict.get("job_total", None) == 1:
                if OpendedSh and getattr(OpendedSh, "shadow_obj", None):
                    OpendedSh.shadow_obj.Delete_()

## 080126
# def create_uncbkp_job(
def log_to_file(log_file, data):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, default=str) + "\n")
## 080126

def create_localbkp_job_original(
    src_folder,
    trg_folder,
    p_name,
    repo,
    authId,
    p_NameText,
    p_IdText,
    bkupType,
    job_Start,
    file_pattern=["*.*"],
    repo_d={},
    this_file_id_j = {"adf":str(uuid.uuid4())},
    schedulerid="",
    o_OpendedSh =None
    
):
    shadow_data=None
    shadow_id=None
    
    import os
    import threading
    from fClient.cktio import cl_socketio_obj

    if not repo:
        repo = "LAN"
    
    if not file_pattern:
        file_pattern = ["*.*"]
    all_types = "*.*" in file_pattern
    all_selected_types = {ext for ext in file_pattern if ext != "*.*"}
    search_extensions = [ext for ext in file_pattern if ext != "*.*"]
    threads=[]
    f_files = []
    ff_files=[]
    ff_filesParams=[]
    stack=[]
    a_results=[]
    accuracy=0.00
    finished=False
    OpendedSh=o_OpendedSh
    this_file_id = str(uuid.uuid4())

    j = app.apscheduler.get_job(id=p_IdText)
    file=""
    ##kartik 15-11-2025
    task_queue = queue.Queue(maxsize=1000)
    thread = threading.Thread(target=broadcast_ws_message, args=(cl_socketio_obj, task_queue,False), daemon=True)
    thread.start()
    backup_status = {
        "backup_jobs": [
            {
                "status": "initiating",
                "paused": False,
                "name": p_NameText,
                "agent": str(app.config.get("getCodeHost", None)),
                "scheduled_time": time.strftime("%H:%M:%S", time.localtime(job_Start)),
                "progress_number": 0,
                "id": job_Start,
                "repo":repo

            }
        ]
    }
    task_queue.put(backup_status)
  
    ##kartik 15-11-2025
    if j:
        p_NameText=j.name
        p_name=j.name
        while not j.next_run_time:
            try:
                if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                if not cl_socketio_obj.connected:
                    cl_socketio_obj.connect(
                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                        ,wait_timeout=5
                        ,retry=True
                    )
                time.sleep(2)
                if cl_socketio_obj.connected:
                    cl_socketio_obj.emit(
                        "starting",
                        json.dumps(
                            {
                                "backup_jobs": [
                                    {
                                        "status":"counting",
                                        "paused":True,
                                        "name": p_NameText,
                                        "scheduled_time": datetime.datetime.fromtimestamp(
                                            float(job_Start)
                                        ).strftime(
                                            "%H:%M:%S"
                                        ),
                                        "agent": str(app.config.get("getCodeHost",None)),
                                        "progress_number": float(len(f_files)),
                                        "id": job_Start,
                                        "repo":repo
                                    }
                                ]
                            }
                        ),
                        "/backup_jobs",
                    )
            except:
                if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
            finally:
                if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                j = app.apscheduler.get_job(id=p_IdText)
    

    
    # if schedulerid:
    #     if app.config.get(schedulerid,None):
    #         shadow_data =app.config[schedulerid]
    #         if time.time() - float( shadow_data["datetime_start"])<=600:
    #             shadow_id =shadow_data["shadow_id"]
    #         else:
    #             shadow_id=None

    # OpendedSh = OpenShFile(src_folder,shadow_scheduler_GUID=shadow_id)
    # OpendedSh.OpenFileSha()

    # if schedulerid:
    #     shadow_data = {"datetime_start":time.time(),"shadow_id" : OpendedSh.shadow_id}
    #     app.config[schedulerid] =shadow_data
    #     shadow_id = OpendedSh.shadow_id
    
    print('\n',"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",'\n',app.config.get(schedulerid,"NO ID FOUND"),'\n',"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",'\n') 

    
    
    icurfile = 0
    if os.path.exists(src_folder):
        a_results=[]
        if os.path.isfile(src_folder):
            if j:
                while not j.next_run_time:
                    try:
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                        if not cl_socketio_obj.connected:
                            cl_socketio_obj.connect(
                                f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                ,wait_timeout=5
                                ,retry=True
                            )
                        time.sleep(2)
                        if cl_socketio_obj.connected:
                            cl_socketio_obj.emit(
                                "starting",
                                json.dumps(
                                    {
                                        "backup_jobs": [
                                            {
                                                "status":"counting",
                                                "paused":True,
                                                "name": p_NameText,
                                                "scheduled_time": datetime.datetime.fromtimestamp(
                                                    float(job_Start)
                                                ).strftime(
                                                    "%H:%M:%S"
                                                ),
                                                "agent": str(app.config.get("getCodeHost",None)),
                                                "progress_number": float(len(1)),
                                                "id": job_Start,
                                                "repo":repo
                                            }
                                        ]
                                    }
                                ),
                                "/backup_jobs",
                            )
                    except:
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    finally:
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                        j = app.apscheduler.get_job(id=p_IdText)
            try:
                start_file_streaming(
                    os.path.join(os.path.dirname(src_folder), src_folder),
                    os.path.basename(src_folder),
                    os.path.dirname(src_folder),
                    trg_folder,
                    p_name,
                    repo,
                    authId,
                    job_Start,
                    ftype="file",
                    p_NameText=p_NameText,
                    p_IdText=p_IdText,
                    bkupType=bkupType,
                    currentfile=1,
                    totalfiles=1,
                    file_id=this_file_id,
                    src_location=src_folder,
                    OpendedSh = OpendedSh,
                    tfi= this_file_id,

                )
                a_results.append({
                    "file":file, 
                    "basename":os.path.basename(file),  # file
                    "dirname":os.path.dirname(file),  # root),
                    "trg_folder":trg_folder,
                    "p_name":p_name,
                    "repo":repo,
                    "id":job_Start,
                    "ftype":"folder",
                    "p_NameText":p_NameText,
                    "p_IdText":p_IdText,
                    "bkupType":bkupType,
                    "currentfile":icurfile,
                    "totalfiles":len(f_files),
                    "src_location":src_folder,
                    "result":"SUCCESS",
                    "reason":"",
                    })
            except Exception as streamerror:
                s_error =str(streamerror)
                logger.warning(f'Error: {str(streamerror)}')
                a_results.append({
                    "file":file, 
                    "basename":os.path.basename(file),  # file
                    "dirname":os.path.dirname(file),  # root),
                    "trg_folder":trg_folder,
                    "p_name":p_name,
                    "repo":repo,
                    "id":job_Start,
                    "ftype":"folder",
                    "p_NameText":p_NameText,
                    "p_IdText":p_IdText,
                    "bkupType":bkupType,
                    "currentfile":icurfile,
                    "totalfiles":len(f_files),
                    "src_location":src_folder,
                    "result":"failed",
                    "reason":s_error ,
                    })
        else:
            # stack=[src_folder]
            try:
                # # task_queue = queue.Queue()
                # stack=[]
                # ixs=0
                # # for root, dirs, files in os.walk(src_folder):
                # #     stack.extend([os.path.join(root, d) for d in dirs])
                # #     f_files.extend([os.path.join(root, f) for f in files])                    
                # #     break

                # for root, dirs, files in os.walk(src_folder,):
                #     # Collect non-empty files using locked-safe size check
                #     for f in files:
                #         file_path = os.path.join(root, f)
                #         try:
                #             size = get_file_size_locked(file_path) 
                #             if size > 0:
                #                 if all_types or any(f.endswith(ext) for ext in all_selected_types):
                #                     f_files.append(file_path)
                #         except (OSError, FileNotFoundError) as e:
                #             # Skip inaccessible/deleted files safely
                #             logger.warning(f"IO operations error {str(e)}")
                #             continue

                #     # Collect directories
                #     stack.extend(os.path.join(root, d) for d in dirs)

                #     # Break to avoid deep recursion (stack-based processing)
                #     break
                # subdirs = []
                # root_files = []
                # # for root, dirs, files in os.walk(src_folder):
                # #     subdirs.extend([os.path.join(root, d) for d in dirs])
                # #     root_files.extend([os.path.join(root, f) for f in files])

                # # for root, dirs,files in os.walk(src_folder):
                # #     fc = FileSnapshotter(src_folder)
                # #     all_files_list = fc.collect_all_files(src_folder)
                # #     if all_types:
                # #         f_files=all_files_list
                # #     else:
                # #         f_files = [file_info for file_info in all_files_list if all_files_list and file_info.endswith(tuple(search_extensions))]
                
                
                
                # backup_status = {
                #             "backup_jobs": [
                #                 {
                #                     "status": "counting",
                #                     "paused": False,
                #                     "name": p_NameText,
                #                     "agent": str(app.config.get("getCodeHost",None)),
                #                     "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                #                     "progress_number": len(f_files),
                #                     "id": job_Start,
                #                     "repo":repo
                #                 }
                #             ]
                #         }
                # task_queue.put(backup_status)
                # multiprocessing.freeze_support() 
                # results=[]
                # with multiprocessing.Pool(processes=get_miltiprocessing_cpu_count()) as pool:
                #     while stack:
                #         dirs_to_process = [stack.pop() for _ in range(min(len(stack), get_miltiprocessing_cpu_count()))]
                #         results = pool.map(partial( process_folder,all_types=all_types,all_selected_types =search_extensions) , dirs_to_process)
                #         for files, new_dirs in results:
                #             f_files.extend(files)
                #             ff_filesParams.extend(())

                #             stack.extend(new_dirs)
                #         # Send update to the dedicated queue
                #         backup_status = {
                #             "backup_jobs": [
                #                 {
                #                     "status": "counting",
                #                     "paused": False,
                #                     "name": p_NameText,
                #                     "agent": str(app.config.get("getCodeHost",None)),
                #                     "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                #                     "progress_number": len(f_files),
                #                     "id": job_Start,
                #                     "repo":repo
                #                 }
                #             ]
                #         }
                #         task_queue.put(backup_status)
                #     try:
                #         while not task_queue.empty():
                #             try:
                #                 task_queue.get_nowait()  # Non-blocking removal
                #             except queue.Empty:
                #                 break
                #     except:
                #         print("x not found")
                
                

                # #thread.join(timeout= float(3.00))

                # # task_queue =None 
                
                # # task_queue = queue.Queue()   
                
                # backup_status = {
                #     "backup_jobs": [
                #         {
                #             "status": "counting",
                #             "paused": False,
                #             "name": p_NameText,
                #             "agent": str(app.config.get("getCodeHost",None)),
                #             "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                #             "progress_number": len(f_files),
                #             "id": job_Start,
                #             "repo":repo
                #         }
                #     ]
                # }
                # task_queue.put(backup_status)
                # task_queue.put(None)
                # thread.join(timeout= float(5.00))
                results=[]
                meta_data = {
                    "p_name":p_name,
                    "repo":repo,
                    "id":job_Start,
                    "ftype":"folder",
                    "p_NameText":p_NameText,
                    "p_IdText":p_IdText,
                    "bkupType":bkupType,
                    "currentfile":icurfile,
                    "totalfiles":len(f_files),
                    "src_location":src_folder,
                    "epc": base64.b64encode(
                        gzip.compress(
                            str(app.config.get("getCode", None)).encode("utf-8"),
                            9,
                        )
                    ).decode("utf-8"),

                    "epn": base64.b64encode(
                        gzip.compress(
                            str(app.config.get("getCodea", None)).encode("utf-8"),
                            9,
                        )
                    ).decode("utf-8"),

                    }
                f_files = list_files_with_robocopy(
                        source_dir=src_folder,
                        search_extensions=search_extensions,
                        task_queue=task_queue,
                        p_NameText=p_NameText,
                        job_Start=job_Start,
                        repo=repo,
                        metadata = meta_data
                    )

                # url = f"http://{app.config['server_ip']}:{app.config['server_port']}/saveinitlog"
                # requests.post(url,json={"data":f_files, 'meta_data':{
                #     "p_name":p_name,
                #     "repo":repo,
                #     "id":job_Start,
                #     "ftype":"folder",
                #     "p_NameText":p_NameText,
                #     "p_IdText":p_IdText,
                #     "bkupType":bkupType,
                #     "currentfile":icurfile,
                #     "totalfiles":len(f_files),
                #     "src_location":src_folder,
                #     "epc": base64.b64encode(
                #         gzip.compress(
                #             str(app.config.get("getCode", None)).encode("utf-8"),
                #             9,
                #         )
                #     ).decode("utf-8"),

                #     "epn": base64.b64encode(
                #         gzip.compress(
                #             str(app.config.get("getCodea", None)).encode("utf-8"),
                #             9,
                #         )
                #     ).decode("utf-8"),

                #     }}, stream=True)       
############################################################################################
            #     for root, dirs, files in os.walk(src_folder):

            #         j = app.apscheduler.get_job(id=p_IdText)
            #         if j:
            #             while not j.next_run_time:
            #                 try:
            #                     if cl.connected: cl.disconnect()
            #                     if not cl.connected:
            #                         cl.connect(
            #                             f"ws://{app.config['server_ip']}:{app.config['server_port']}"
            #                             ,wait_timeout=5
            #                             ,retry=True
            #                         )
            #                     time.sleep(2)
            #                     if cl.connected:
            #                         cl.emit(
            #                             "starting",
            #                             json.dumps(
            #                                 {
            #                                     "backup_jobs": [
            #                                         {
            #                                             "status":"counting",
            #                                             "paused":True,
            #                                             "name": p_NameText,
            #                                             "scheduled_time": datetime.datetime.fromtimestamp(
            #                                                 float(job_Start)
            #                                             ).strftime(
            #                                                 "%H:%M:%S"
            #                                             ),
            #                                             "agent": str(app.config.get("getCodeHost",None)),
            #                                             "progress_number": float(0),
            #                                         }
            #                                     ]
            #                                 }
            #                             ),
            #                             "/backup_jobs",
            #                         )
            #                 except:
            #                     if cl.connected: cl.disconnect()
            #                 finally:
            #                     if cl.connected: cl.disconnect()
            #                     j = app.apscheduler.get_job(id=p_IdText)

            #         if all_types:
            #             # ff_files = files
            #             ff_files = list(map(lambda i: os.path.join(root, i), files))
            #             ixs=ixs+len(ff_files) 
            #             #if any(ixs % prime == 0 for prime in [1,10,50,100,200, 300, 500, 700, 1100, 1300, 1700, 1900, 2300, 2900, 3100, 3700, 4100, 4300, 4700, 5300, 5900]):
            #             try:
            #                 if ixs % ixs == 0:
                            
            #                     if cl.connected: cl.disconnect()
            #                     if not cl.connected:
            #                         cl.connect(
            #                             f"ws://{app.config['server_ip']}:{app.config['server_port']}"
            #                         ) 
            #                         time.sleep(2)
            #                     if cl.connected:
            #                         cl.emit(
            #                             "starting",
            #                             json.dumps(
            #                                 {
            #                                     "backup_jobs": [
            #                                         {
            #                                             "status":"counting",
            #                                             "paused":False,
            #                                             "name": p_NameText,
            #                                             "scheduled_time": datetime.datetime.fromtimestamp(
            #                                                 float(job_Start)
            #                                             ).strftime(
            #                                                 "%H:%M:%S"
            #                                             ),
            #                                             "agent": str(app.config.get("getCodeHost",None)),
            #                                             "progress_number": float(ixs),
            #                                         }
            #                                     ]
            #                                 }
            #                             ),
            #                             #"/starting",
            #                         )
            #                         time.sleep(0.1)
            #             except Exception as s:
            #                 print(str(s))
            #             finally:
            #                 try:
            #                     if cl.connected: cl.disconnect()
                                
            #                 except:
            #                     pass
            #         else:
            #             # ff_files = [
            #             #     os.path.join(root, file)
            #             #     for file in files
            #             #     if any(file.endswith(ext) for ext in all_selected_types)
            #             # ]
            #             for file in files:
            #                 if any(file.endswith(ext) for ext in all_selected_types):
                                
            #                     ixs += 1  # Increment counter
            #                     ff_files.append(os.path.join(root, file))  # Add file to list
            #                     #if any(ixs % prime == 0 for prime in [200, 300, 500, 700, 1100, 1300, 1700, 1900, 2300, 2900, 3100, 3700, 4100, 4300, 4700, 5300, 5900]):
                                
            #                     try:
            #                         if ixs % ixs == 0:

            #                             if cl.connected: cl.disconnect()
            #                             if not cl.connected:
            #                                 cl.connect(
            #                                     f"ws://{app.config['server_ip']}:{app.config['server_port']}"
            #                                 ) 
            #                                 time.sleep(2)
            #                             if cl.connected:
            #                                 cl.emit(
            #                                     "starting",
            #                                     json.dumps(
            #                                         {
            #                                             "backup_jobs": [
            #                                                 {
            #                                                     "status":"counting",
            #                                                     "paused":False,
            #                                                     "name": p_NameText,
            #                                                     "scheduled_time": datetime.datetime.fromtimestamp(
            #                                                         float(job_Start)
            #                                                     ).strftime(
            #                                                         "%H:%M:%S"
            #                                                     ),
            #                                                     "agent": str(app.config.get("getCodeHost",None)),
            #                                                     "progress_number": float(ixs),
            #                                                 }
            #                                             ]
            #                                         }
            #                                     ),
            #                                     #"/starting",
            #                                 )
            #                                 time.sleep(0.1)
            #                     except:
            #                         pass
            #                     finally:
            #                         try:
            #                             if cl.connected: cl.disconnect()
            #                             time.sleep(1)
            #                         except:
            #                             pass

                    
            #         f_files = f_files + ff_files

            #     # from fClient.FilesUtil import FileCollector
            #     # print(time.time())
            #     # file_collector = FileCollector(src_folder, all_types, all_selected_types)
            #     # f_files = file_collector.collect_files()
            #     # print(time.time())

            #     j = app.apscheduler.get_job(id=p_IdText)
            #     if j:
            #         while not j.next_run_time:
            #             try:
            #                 if cl.connected: cl.disconnect()
            #                 if not cl.connected:
            #                     cl.connect(
            #                         f"ws://{app.config['server_ip']}:{app.config['server_port']}"
            #                         ,wait_timeout=5
            #                         ,retry=True
            #                     )
            #                 time.sleep(2)
            #                 if cl.connected:
            #                     cl.emit(
            #                         "starting",
            #                         json.dumps(
            #                             {
            #                                 "backup_jobs": [
            #                                     {
            #                                         "status":"counting",
            #                                         "paused":True,
            #                                         "name": p_NameText,
            #                                         "scheduled_time": datetime.datetime.fromtimestamp(
            #                                             float(job_Start)
            #                                         ).strftime(
            #                                             "%H:%M:%S"
            #                                         ),
            #                                         "agent": str(app.config.get("getCodeHost",None)),
            #                                         "progress_number": float(0),
            #                                     }
            #                                 ]
            #                             }
            #                         ),
            #                         "/backup_jobs",
            #                     )
            #             except:
            #                 if cl.connected: cl.disconnect()
            #             finally:
            #                 if cl.connected: cl.disconnect()
            #                 j = app.apscheduler.get_job(id=p_IdText)

            # ########### FileSnapshotter
            
            #     # fc = FileSnapshotter(src_folder)
            #     # all_files_list = fc.collect_all_files(src_folder)
            #     # if all_types:
            #     #     f_files=all_files_list
            #     # else:
            #     #     f_files = [file_info for file_info in all_files_list if all_files_list and file_info.endswith(tuple(search_extensions))]
            
            # ############### FileSnapshotter
############################################################################################
                j = app.apscheduler.get_job(id=p_IdText)
                if j:
                    while not j.next_run_time:
                        try:
                            if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                            if not cl_socketio_obj.connected:
                                cl_socketio_obj.connect(
                                    f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                    ,wait_timeout=5
                                    ,retry=True
                                )
                            time.sleep(2)
                            if cl_socketio_obj.connected:
                                cl_socketio_obj.emit(
                                    "starting",
                                    json.dumps(
                                        {
                                            "backup_jobs": [
                                                {
                                                    "status":"counting",
                                                    "paused":True,
                                                    "name": p_NameText,
                                                    "scheduled_time": datetime.datetime.fromtimestamp(
                                                        float(job_Start)
                                                    ).strftime(
                                                        "%H:%M:%S"
                                                    ),
                                                    "agent": str(app.config.get("getCodeHost",None)),
                                                    "progress_number": float(len(f_files)),
                                                    "accuracy": accuracy,
                                                    "finished": finished,
                                                    "id": job_Start,
                                                    "repo":repo
                                                }
                                            ]
                                        }
                                    ),
                                    "/backup_jobs",
                                )
                        except:
                            if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                        finally:
                            if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                            j = app.apscheduler.get_job(id=p_IdText)


                icurfile = 0
                a_results=[]#for holding values how many files have been backedup
                if f_files:
                    failed = 0

                    max_threads = min(32, (os.cpu_count() or 4) * 4)
                    for idx, file_data in enumerate(f_files):
                        file = file_data['path']
                        args = (
                            file,os.path.basename(file), os.path.dirname(file), trg_folder, p_name,
                            repo, authId, job_Start,
                            f"folder", p_NameText, p_IdText,
                           idx+1, len(f_files),file_data['id'],
                        )
                        kwargs = {
                            "bkupType": bkupType,
                            "chunk_size": 1024 * 1024 * 64,
                            "src_location": src_folder,
                            # "accuracy": 0.99,
                            # "finished": False,
                            "OpendedSh": OpendedSh,
                            "tfi": this_file_id
                        }
                        ff_filesParams.append((args, kwargs))

                        # with Pool(processes=multiprocessing.cpu_count()) as pool:
                        #     results = pool.imap_unordered(run_start_file_streaming, ff_filesParams)
                        #     for result in pool.imap_unordered(run_start_file_streaming, ff_filesParams):
                        #         if isinstance(result, dict) and "error" in result:
                        #             # Log the error, or add to a failure list
                        #             print(f"Error processing {result['args']}: {result['error']}")
                        #         else:
                        #             # Success
                        #             print(f"Success: {result}")
                    # run_start_file_streaming(ff_filesParams[0][0], **ff_filesParams[0][1])
                    # start_file_streaming(ff_filesParams[0][0], **ff_filesParams[0][1])
                    
                    with ThreadPoolExecutor(max_workers=get_miltiprocessing_cpu_count()) as executor:
                        future_to_file = {
                            executor.submit(run_start_file_streaming, _args): _args[0][0]
                            for _args in ff_filesParams
                        }
                    
                        if not os.path.exists('metadata'):
                            os.makedirs('metadata')
                        log_file = os.path.join('metadata',f"{p_NameText}_{job_Start}.json")
                        for future in as_completed(future_to_file):
                            file = future_to_file[future]
                            timestamp = datetime.datetime.utcnow().isoformat()
                            try:
                                result = future.result()
                                results.append(result)
                                accuracy= 100*(len(f_files)-failed)/len(f_files)
                                log_to_file(log_file, {
                                    "timestamp": timestamp,
                                    "file": file,
                                    "status": "SUCCESS",
                                    "response": result,
                                    "accuracy": accuracy
                                })
                                print(f"[SUCCESS] Processed: {file}")
                            except Exception as e:
                                failed+=1
                                accuracy= 100*(len(f_files)-failed)/len(f_files)
                                log_to_file(log_file, {
                                    "timestamp": timestamp,
                                    "file": file,
                                    "status": "FAILURE",
                                    "error": str(e),
                                    "accuracy": accuracy
                                })
                                print(f"[FAILURE] {file} raised: {e}")
                            finally:
                                # Remove the future to free memory
                                del future_to_file[future]

                    #25/07/2025        start
                    # for filez in f_files:
                    #     file=filez
                    #     try:
                    #         icurfile = icurfile + 1
                    #         # print("Sending.. " + os.path.join(root, file))
                    #         print("Sending.. " + file)
                    #         try:

                    #             # t=threading.Thread(
                    #             #     target=start_file_streaming(
                    #             #         file,  # os.path.join(root, file),
                    #             #         os.path.basename(file),  # file
                    #             #         os.path.dirname(file),  # root),
                    #             #         trg_folder,
                    #             #         p_name,
                    #             #         repo,
                    #             #         authId,
                    #             #         job_Start,
                    #             #         ftype="folder",
                    #             #         p_NameText=p_NameText,
                    #             #         p_IdText=p_IdText,
                    #             #         bkupType=bkupType,
                    #             #         currentfile=icurfile,
                    #             #         totalfiles=len(f_files),
                    #             #         src_location=src_folder,
                    #             #         OpendedSh = OpendedSh,
                    #             #         tfi= this_file_id,
                    #             #     ),
                    #             # )
                    #             # threads.append(t)
                    #             # t.start()
                    #             # t.join()

                    #         #try:
                    #             # start_file_streaming(
                    #             #     file,  # os.path.join(root, file),
                    #             #     os.path.basename(file),  # file
                    #             #     os.path.dirname(file),  # root),
                    #             #     trg_folder,
                    #             #     p_name,
                    #             #     repo,
                    #             #     authId,
                    #             #     job_Start,
                    #             #     ftype="folder",
                    #             #     p_NameText=p_NameText,
                    #             #     p_IdText=p_IdText,
                    #             #     bkupType=bkupType,
                    #             #     currentfile=icurfile,
                    #             #     totalfiles=len(f_files),
                    #             #     src_location=src_folder,
                    #             #     OpendedSh = OpendedSh,
                    #             #     tfi= this_file_id,
                    #             # )

                    #             accuracy= 100*(len(f_files)-failed)/len(f_files)
                    #             # a_results.append({
                    #             #     "file":file, 
                    #             #     "basename":os.path.basename(file),  # file
                    #             #     "dirname":os.path.dirname(file),  # root),
                    #             #     "trg_folder":trg_folder,
                    #             #     "p_name":p_name,
                    #             #     "repo":repo,
                    #             #     "id":job_Start,
                    #             #     "ftype":"folder",
                    #             #     "p_NameText":p_NameText,
                    #             #     "p_IdText":p_IdText,
                    #             #     "bkupType":bkupType,
                    #             #     "currentfile":icurfile,
                    #             #     "totalfiles":len(f_files),
                    #             #     "src_location":src_folder,
                    #             #     "result":"SUCCESS",
                    #             #     "reason":"",
                    #             #     })
                    #         except Exception as streamerror :
                    #             # s_error =str(streamerror)
                    #             failed+=1
                    #             accuracy= 100*(len(f_files)-failed)/len(f_files)
                    #             print("Send message to server : "  + str(streamerror))
                    #             # a_results.append({
                    #             #     "file":file, 
                    #             #     "basename":os.path.basename(file),  # file
                    #             #     "dirname":os.path.dirname(file),  # root),
                    #             #     "trg_folder":trg_folder,
                    #             #     "p_name":p_name,
                    #             #     "repo":repo,
                    #             #     "id":job_Start,
                    #             #     "ftype":"folder",
                    #             #     "p_NameText":p_NameText,
                    #             #     "p_IdText":p_IdText,
                    #             #     "bkupType":bkupType,
                    #             #     "currentfile":icurfile,
                    #             #     "totalfiles":len(f_files),
                    #             #     "src_location":src_folder,
                    #             #     "result":"failed",
                    #             #     "reason":s_error ,
                    #             #     })
                    #     except Exception as ex:
                    #         print(str(ex))
                    #         try:
                    #             if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    #             if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    #             if not cl_socketio_obj.connected:
                    #                 cl_socketio_obj.connect(
                    #                     f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                    #                     ,wait_timeout=5
                    #                     ,retry=True
                    #                 ) 
                    #         except:
                    #             pass
                    #         if (str(ex).lower()) == "failed":
                    #             failed += 1
                    #             if float((100 * failed) / len(f_files)) >= float(50):                                    
                    #                 try:                                    
                    #                     if cl_socketio_obj.connected:
                    #                         cl_socketio_obj.emit(
                    #                             "backup_data",
                    #                             json.dumps(
                    #                                 {
                    #                                     "backup_jobs": [
                    #                                         {
                    #                                             "status":"finished",
                    #                                             "reason":"failed",
                    #                                             "paused":False,
                    #                                             "name": p_NameText,
                    #                                             "scheduled_time": datetime.datetime.fromtimestamp(
                    #                                                 float(job_Start)
                    #                                             ).strftime(
                    #                                                 "%H:%M:%S"
                    #                                             ),
                    #                                             "agent": str(app.config.get("getCodeHost",None)),
                    #                                             "progress_number":  float((100 * icurfile) / float(len(f_files))),#100.00 -float((100 * failed) / len(f_files)),
                    #                                             "accuracy":accuracy,
                    #                                             "finished":True,
                    #                                             "id": job_Start,
                    #                                         }
                    #                                     ]
                    #                                 }
                    #                             ),
                    #                             "/",
                    #                         )
                    #                         if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                                    
                    #                 except:
                    #                     pass
                    #                 raise RuntimeError(
                    #                     "failure threshold(50%) crossed : "
                    #                     + str(float((failed)))
                    #                     + " of "
                    #                     + str(len(f_files))
                    #                     + " files"
                    #                 )
                    #         else:
                    #             try:
                    #                 if cl_socketio_obj.connected:
                    #                     cl_socketio_obj.emit(
                    #                         "backup_data",
                    #                         json.dumps(
                    #                             {
                    #                                 "backup_jobs": [
                    #                                     {
                    #                                         "status":"finished",
                    #                                         "reason":"failed",
                    #                                         "paused":False,
                    #                                         "name": p_NameText,
                    #                                         "scheduled_time": datetime.datetime.fromtimestamp(
                    #                                             float(job_Start)
                    #                                         ).strftime(
                    #                                             "%H:%M:%S"
                    #                                         ),
                    #                                         "agent": getCodeHost(),
                    #                                         #"progress_number": 100.00 -float((100 * failed) / len(f_files)),
                    #                                         "progress_number":  float((100 * icurfile) / float(len(f_files))),#100.00 -float((100 * failed) / len(f_files)),
                    #                                         "accuracy":accuracy,
                    #                                         "finished":True,
                    #                                         "id": job_Start,
                    #                                     }
                    #                                 ]
                    #                             }
                    #                         ),
                    #                         "/",
                    #                     )
                    #                     if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    #             except:
                    #                 pass
                    #             raise RuntimeError(str(ex))
                    #25/07/2025        end
            except Exception as ex:
                # s_error =str(ex)
                # a_results.append({
                #     "file":file, 
                #     "basename":os.path.basename(file),  # file
                #     "dirname":os.path.dirname(file),  # root),
                #     "trg_folder":trg_folder,
                #     "p_name":p_name,
                #     "repo":repo,
                #     "id":job_Start,
                #     "ftype":"folder",
                #     "p_NameText":p_NameText,
                #     "p_IdText":p_IdText,
                #     "bkupType":bkupType,
                #     "currentfile":icurfile,
                #     "totalfiles":len(f_files),
                #     "src_location":src_folder,
                #     "result":"failed",
                #     "reason":s_error ,
                #     })
                try:
                    # OpendedSh.shadow_obj.Delete_()
                    print("OpendedSh.shadow_obj.Delete_()")
                except Exception as ddd:
                    print("")
                raise RuntimeError(str(ex))
            return
    try:
        print("OpendedSh.shadow_obj.Delete_()")
    except Exception as ddd:
        print("")
    try:
        if cl_socketio_obj.connected:
            cl_socketio_obj.emit(
                "backup_data",
                json.dumps(
                    {
                        "backup_jobs": [
                            {
                                "status":"finished",
                                "reason":"success",
                                "paused":False,
                                "name": p_NameText,
                                "scheduled_time": datetime.datetime.fromtimestamp(
                                    float(job_Start)
                                ).strftime(
                                    "%H:%M:%S"
                                ),
                                "agent": getCodeHost(),
                                #"progress_number": 100.00 -float((100 * failed) / len(f_files)),
                                "progress_number":  float((100 * icurfile) / float(len(f_files))),#100.00 -float((100 * failed) / len(f_files)),
                                "accuracy":accuracy,
                                "finished":True,
                                "id": job_Start,
                                "repo":repo
                            }
                        ]
                    }
                ),
                "/",
            )
            if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
    except:
        pass
    try:                             
        task_queue.put(backup_status)
        task_queue.put(None)
        thread.join(timeout= float(5.00))
    except:
        pass

    for thread in threads:
        try:
            thread.join()
        except:
            pass



def get_remote_file_stat(backup_pid,file_name):

    import requests
    import base64
    import urllib
    import urllib3
    try:
        file_url = f"http://{app.config['server_ip']}:{app.config['server_port']}/restore/file"
        response = requests.post(url= file_url, json=dict(backup_pid = backup_pid ,file_name =file_name,obj=str(str(app.config.get("getCode",None)))),  timeout=3000)
        logger.info(f"Response by /restore/file {response.json()} and status code {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Logged the response given by /restore/file {response.json()}")
            return response.json()
        
    except:
        return None
    return None

def run_start_file_streaming(args_kwargs):
    args, kwargs = args_kwargs
    try:
        return start_file_streaming(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Error: {str(e)} args: {args} kwargs: {kwargs}")
        return {
            "error": str(e),
            "args": args,
            "kwargs": kwargs
        }

from email.utils import parsedate_to_datetime
def get_date(source: str = ""):

    if source == "" or source.lower() == "online":
        try:
            dt = parsedate_to_datetime(
                requests.get("https://www.google.com", timeout=5).headers["Date"]
            )
            date_obj = dt.strftime("%Y-%m-%d")
            return {
                "source": "online",
                "date": date_obj
            }

        except Exception:
            # Auto fallback to PC
            return {
                "source": "pc",
                "date": datetime.date.today().strftime("%Y-%m-%d")
            }

    # ---------- PC Only ----------
    elif source.lower() == "pc":
        return {
            "source": "pc",
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }

    else:
        raise ValueError("Invalid source! Use '', 'pc', 'online', or add more source in function 'def get_date()' .")

def start_file_streaming(
    file_name,
    file,
    root,
    trg_folder,
    p_name,
    repo,
    authId,
    job_Start,
    ftype,
    p_NameText,
    p_IdText,
    currentfile,
    totalfiles,
    file_id=None,
    bkupType="full",
    chunk_size=1024 * 1024 * 64,
    src_location="",
    accuracy=0.00,
    finished=False,
    OpendedSh = None,
    tfi= None,
):
    # import os, math, gzip, base64, requests
    # from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    # from cryptography.hazmat.backends import default_backend
    # from cryptography.hazmat.primitives import padding

    # from Crypto.Cipher import AES
    # from Crypto.Util.Padding import pad, unpad
    # from Crypto.Random import get_random_bytes



    from fClient.cktio import cl_socketio_obj
    import hashlib

    if file_id is None:
        file_id = file_name
    job_id = ensure_job_id(job_Start)
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        file_id=file_id,
        extra={"event": "job_start"},
    )
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        file_id=file_id,
        extra={"event": "file_start"},
    )
    
    from fClient.p7zstd import p7zstd
    t_c_count =0
    i=0
    num_chunks=0 
    ret_val ={"total_chunks":num_chunks, "uploaded_chunks" :i,"file":file_name}
    open_file_name = file_name
    if OpendedSh and getattr(OpendedSh, "shadow_obj", None):
        open_file_name = OpendedSh.get_path(file_name)
        if not open_file_name:
            open_file_name = file_name

    url = f"http://{app.config['server_ip']}:{app.config['server_port']}/upload"
    try:
        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
        if not cl_socketio_obj.connected:
            try:
                cl_socketio_obj.connect(f"http://{app.config['server_ip']}:{app.config['server_port']}"
                    ,wait_timeout=5
                    ,retry=True
                )
            except:
                print("")
    except:
        pass
    seq_num = 0
    headers = {}
    files_dict=[]
    try:
        file_stat = os.stat(file_name)
        stat_data= {
                    "size": file_stat.st_size,
                    "mtime": file_stat.st_mtime,
                    "mtime_ns": file_stat.st_mtime_ns,
                    "st_atime": file_stat.st_atime,
                    "st_atime_ns": file_stat.st_atime_ns,
                    "st_ctime": file_stat.st_ctime,
                    "st_ctime_ns": file_stat.st_ctime_ns,
                    "st_gid": file_stat.st_gid,
                    "st_ino": file_stat.st_ino,
                    "mode": file_stat.st_mode,
                }
        password = time.time()
        stat_data = base64.b64encode(
                gzip.compress(
                    json.dumps(stat_data).encode('utf-8'),
                    9,
                    mtime=password,
                )
            )
        st_ino =file_stat.st_ino
        result=None
        file_stat_remote = get_remote_file_stat(backup_pid =p_IdText,file_name=file_name)
        file_stat_remote = file_stat_remote.get('result',None)
        logger.debug(f"File stat at remote /restore/file {file_stat_remote}")
        #compressed_data = zlib.compress(b"{44A0C353-B685-4F9E-A3CF-08050440A814}", zlib.Z_BEST_COMPRESSION)
        #compressed_data = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
        compressed_data = None
        SENTINEL_NO_CHANGE = None
        
        bOpen= True #bkupType == "full"
        remote_first_time=0
        remote_last_time=0
        if file_stat_remote:
            result = list(filter(lambda d: d.get('file_path_name').lower() == file_name.lower(), file_stat_remote))
            if result:
                if bkupType == "full" :
                    bOpen=True
                if bkupType == "incremental":
                    result=result[0]
                    bOpen=False
                if bkupType == "differential":
                    result=result[1]
                    bOpen=False
            else:
                bOpen=True
        
        if bkupType == "full":
            bOpen=True
        elif bkupType == "incremental":
            print(f"perform incremental backup of this file : {file_name} ")
            if result:
                if result.get('last_c',0) <= file_stat.st_mtime :
                # if result.get('last_c',0) != file_stat.st_mtime :
                    bOpen=True
            
        elif bkupType == "differential":
            print(f"perform differential backup of this file : {file_name} ")
            if result:
                if result.get('first_c',None)<=file_stat.st_mtime:
                # if result.get('first_c',None)!=file_stat.st_mtime:
                    bOpen=True

        t_c = math.ceil(os.path.getsize(file_name) / chunk_size)
        chunks = []
        #iv = bytes.fromhex("00000000000000000000000000000000")#os.urandom(16)
        s_7z_iv = "00000000000000000000000000000000"
        #key = getKey()
        # cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        # padder = padding.PKCS7(128).padder()

        # from runserver import a_scheduler

        j = app.apscheduler.get_job(id=p_IdText)
        if j != None:
            while not j.next_run_time:
                try:
                    if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    if not cl_socketio_obj.connected:
                        cl_socketio_obj.connect(
                            f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                            ,wait_timeout=5
                            ,retry=True             
                        )
                    time.sleep(2)
                    if cl_socketio_obj.connected:
                        cl_socketio_obj.emit(
                            "backup_data",
                            json.dumps(
                                {
                                    "backup_jobs": [
                                        {
                                            "name": p_NameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(job_Start)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": str(app.config.get("getCodeHost",None)),
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),
                                            "accuracy": accuracy,
                                            "finished": finished,                                            
                                            "id": job_Start,
                                            "repo":repo
                                        }
                                    ]
                                }
                            ),
                            "/",
                        )
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                except Exception as ex:
                    print(str(ex))
                    try:
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    except:
                        pass
                time.sleep(10)
                j = app.apscheduler.get_job(id=p_IdText)
        #with open(file_name, "rb") as f:
        #if bOpen:
        compression_level=3
        digest=None
        shm=None
        num_chunks=0 
        file_size=0
        #with OpenShFile(file_name, "rb") as m_file:
        
        with open(open_file_name, "rb") as f: #m_file:
            #with mmap.mmap(m_file.fileno(), 0, access=mmap.ACCESS_COPY) as f:
            # cdigest=FileDig()
            # digest= "cdigest._hash_memory(f)"
            # del cdigest
            # file_size = f.seek(0, 2) 
            # file_size = f.tell() 
            # f.seek(0)
            file_size = os.path.getsize(open_file_name)
            j = app.apscheduler.get_job(id=p_IdText)
            if j != None:
                while not j.next_run_time:
                    try:
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                        if not cl_socketio_obj.connected:
                            cl_socketio_obj.connect(
                                f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                ,wait_timeout=5
                                ,retry=True
                            )
                        if cl_socketio_obj.connected:
                            cl_socketio_obj.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "status": "progress",
                                            "name": p_NameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(job_Start)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": str(app.config.get("getCodea",None)),
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),                                            
                                            "accuracy": accuracy,
                                            "finished": finished,
                                            "id": job_Start,
                                            "repo":repo
                                        }
                                    ]
                                },
                            )
                        time.sleep(10)
                    except:
                        pass 
                    j = app.apscheduler.get_job(id=p_IdText)
            f.seek(0)
            if bOpen:
                file_signature = f.read(16)
                # for signature, level in SIGNATURE_MAP_COMPRESSION_LEVEL.items():
                #     if file_signature.startswith(signature):
                #         if level is None:
                #             compression_level= 1
                #         else:
                #             compression_level= level
                compression_level = SIGNATURE_MAP_COMPRESSION_LEVEL.get(file_signature[:4], 3) or 1   
                if file_size < 1 * 1024 * 1024:   # < 1 MB ==> Max compression
                    compression_level = min(compression_level + 3, 9)
                elif file_size < 100 * 1024 * 1024: # < 100 MB ==> High compression
                    compression_level = min(compression_level + 2, 9)
                elif file_size < 1 * 1024 * 1024 * 1024: # < 1 GB ==> Medium compression
                    compression_level = compression_level
                else:  # > 1 GB ==> Fast compression
                    compression_level = max(compression_level - 2, 1)

                f.seek(0)
                ##compressed_data = f.read()
                #shm= multiprocessing.shared_memory.SharedMemory(create=True,size=file_size)
                #shm.buf[:file_size] = f[:]
                chunk_size = get_optimal_chunk_size(file_size=file_size)
                num_chunks=math.ceil( file_size/chunk_size)
                compressed_data =num_chunks !=0
                t_c = math.ceil(file_size / chunk_size)
            f.close()
        if not bOpen:
            num_chunks=1
            #compressed_data = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
            SENTINEL_NO_CHANGE = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
        if compressed_data!=None or SENTINEL_NO_CHANGE!=None:
            if repo in ["GDRIVE", "LAN", "LOCAL", "LOCAL STORAGE","AWSS3","AZURE","ONEDRIVE"]:
                if bOpen: #if there is a change in file
                    # #compressed_data = zlib.compress(compressed_data,level=int(compression_level))
                    # pZip= p7zstd(iv,preset=int(compression_level))
                    # compressed_data = pZip.compress_chunk_shared(shm_name= shm.name,chunk_size= chunk_size,num_chunks= num_chunks)
                    # #compressed_data= pZip.compress(data=compressed_data,file_name=file_name)
                    # del pZip
                    # shm.unlink()
                    # shm.close()

                    print("")
                else:
                    compressed_data = SENTINEL_NO_CHANGE #b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
                    
                # if isinstance(iv,(str)):
                #     #iv = bytes.fromhex(iv)
                #     iv = iv.encode()
########################################################
                # from Crypto.Cipher import AES as myAES
                # from Crypto.Util.Padding import pad as myPad

                #cipher = myAES.new(key, myAES.MODE_CBC, iv)
                #compressed_data = zlib.compress(chunk, zlib.Z_BEST_COMPRESSION)
#following statement using  "compressed_data" which holds the entire file
                # encrypted_chunk = cipher.encrypt(
                #     myPad(compressed_data, myAES.block_size)
                # )
 
                # compressed_data = cipher.encrypt(
                #     myPad(compressed_data, myAES.block_size)
                # )
#######################################################

            chunk_num = 0
            seq_num = 0

            
            # x = float(filesdone)
            # nx = float(totalfiles)
            #accuracy=100.00*(x/nx)
            #t_c = math.ceil(len(compressed_data) / chunk_size)

            # t_c_count = math.ceil(len(compressed_data) / chunk_size)+1
            # for i in range(0, len(compressed_data), chunk_size):
            t_c_count =num_chunks
            ret_val = {"total_chunks":num_chunks, "uploaded_chunks" :i,"file":file_name}
            i=0
            futures = []
            logger.info(f"Number of chunks {t_c_count} and file name or path {open_file_name}") ##kartik
            log_event(
                logger,
                logging.DEBUG,
                job_id,
                "backup",
                file_path=open_file_name,
                file_id=file_id,
                extra={"event": "chunking_start", "chunk_total": t_c_count},
            )
            # with open(open_file_name, "rb") as f:# , ThreadPoolExecutor(max_workers=8) as executor:
            # #with open(open_file_name, "rb") as f:
            #     chunk_data = f.read(chunk_size) if bOpen else b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
            f=None
            file_hasher = hashlib.sha256() if bOpen else None
            if bOpen:
                f= open(open_file_name, "rb")# , ThreadPoolExecutor(max_workers=8) as executor:
                chunk_data = f.read(chunk_size) if bOpen else b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
            else:
                chunk_data = SENTINEL_NO_CHANGE

            while chunk_data:
                i=i+1
                t_c_count=t_c_count-1
                chunk = BytesIO()
                chunk_hash = None
                if bOpen:
                    try:
                        file_hasher.update(chunk_data)
                    except Exception as hash_error:
                        log_event(
                            logger,
                            logging.ERROR,
                            job_id,
                            "backup",
                            file_path=open_file_name,
                            file_id=file_id,
                            chunk_index=seq_num,
                            error_code="CHECKSUM_GENERATION_FAILED",
                            error_message=str(hash_error),
                            extra={"event": "file_hash_update_failed"},
                        )
                    #iv,preset=int(compression_level)
                    # with py7zr.SevenZipFile(chunk, 'w', password=iv.decode(), 
                    #                         filters=[{"id": py7zr.FILTER_ZSTD},
                    #                                  {"id": py7zr.FILTER_CRYPTO_AES256_SHA256, "password": iv.decode()}]) as archive:
                    with py7zr.SevenZipFile(chunk, 'w', password=s_7z_iv, 
                                            filters=[{"id": py7zr.FILTER_ZSTD},
                                                     {"id": py7zr.FILTER_CRYPTO_AES256_SHA256, "password": s_7z_iv}]) as archive:
                        archive.writestr(data=chunk_data, arcname=f"chunk_{i}.abzv2")
                    
                    chunk_data = f.read(chunk_size) if bOpen else None
                    #chunk = compressed_data[i : i + chunk_size]



                    # isLast = (i + chunk_size) ==len(compressed_data)
                    # if isLast or t_c_count==1:
                    #     print("ppppppppppppppppppppppppppppppppppppppppppppppppppppppp")
                    # chunk = f.read(chunk_size)
                    # seq_num = 0
                    # while chunk:

                password = time.time()
                if bOpen :
                    #compressed_chunk = b"{44A0C353-B685-4F9E-A3CF-08050440A814}" #gzip.compress(chunk.getvalue(), 1, mtime=password)
                    compressed_chunk = chunk.getvalue()
                    try:
                        chunk_hash = hashlib.sha256(compressed_chunk).hexdigest()
                    except Exception as hash_error:
                        log_event(
                            logger,
                            logging.ERROR,
                            job_id,
                            "backup",
                            file_path=open_file_name,
                            file_id=file_id,
                            chunk_index=seq_num,
                            error_code="CHECKSUM_GENERATION_FAILED",
                            error_message=str(hash_error),
                            extra={"event": "chunk_hash_failed"},
                        )

                else:
                    compressed_chunk = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
                    chunk_data = None
                try:
                    del chunk
                except:
                    pass
                root_ = root
                seq_num = seq_num + 1
                log_chunk_event(
                    logger,
                    logging.DEBUG,
                    job_id,
                    "backup",
                    file_path=open_file_name,
                    file_id=file_id,
                    chunk_index=seq_num,
                    extra={"event": "chunk_start"},
                )
                
                if repo in ["LAN", "LOCAL", "LOCAL STORAGE"]:

                    # encryptor = cipher.encryptor()
                    # padded_data = padder.update(chunk)
                    # encrypted_chunk = encryptor.update(padded_data)
                    # encryptor.update(padder.finalize())
                    # +encryptor.finalize()
#                     from Crypto.Cipher import AES as myAES
#                     from Crypto.Util.Padding import pad as myPad

#                     cipher = myAES.new(key, myAES.MODE_CBC, iv)
#                     #compressed_data = zlib.compress(chunk, zlib.Z_BEST_COMPRESSION)
# #following statement using  "compressed_data" which holds the entire file
#                     # encrypted_chunk = cipher.encrypt(
#                     #     myPad(compressed_data, myAES.block_size)
#                     # )
# # it should be using "compressed_chunk"
#                     encrypted_chunk = cipher.encrypt(
#                         myPad(chunk, myAES.block_size)
#                     )
#                     compressed_chunk = gzip.compress(encrypted_chunk, 9, mtime=password)
                    

                    #compressed_chunk = gzip.compress(chunk.getvalue(), 9, mtime=password)
                    print("")
                elif str(repo).upper() in ["GDRIVE","AWSS3","AZURE","ONEDRIVE"]:
                    # compressed_chunk = gzip.compress(
                    #     compressed_chunk, 9, mtime=password
                    # )
                    # compressed_chunk = gzip.compress(
                    #     chunk, 1, mtime=password
                    # )
                    print("")
                
                
                
                today_date = get_date('pc')
                headers = {
                    "File-Name": file,
                    "fileid":str(file_id),
                    "fidi": digest,
                    "stat":stat_data,
                    "tfi": tfi, #str(uuid.uuid4())
                    "quNu": str(seq_num),
                    "tc": str(num_chunks ),#str(math.ceil(len(compressed_data) / chunk_size)), #str(t_c),
                    "abt": "False",
                    "chkh": str(chunk_hash or ""),
                    # "givn": base64.b64encode(
                    #     gzip.compress(
                    #         str(iv.hex()).encode("UTF-8"),
                    #         9,
                    #         mtime=password,
                    #     )
                    # ),
                    "givn": base64.b64encode(gzip.compress(s_7z_iv.encode("UTF-8"), 9, mtime=password)),
                    "epc": base64.b64encode(
                        gzip.compress(
                            str(str(app.config.get("getCode",None))).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "epn": base64.b64encode(
                        gzip.compress(
                            str(str(app.config.get("getCodea",None))).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "tcc": base64.b64encode(
                        gzip.compress(
                            os.path.join(
                                str(str(app.config.get("getCode",None))), str(root).replace(":", "{{DRIVE}}")
                            ).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "tccsrc": base64.b64encode(
                        gzip.compress(
                            os.path.join(
                                str(str(app.config.get("getCode",None))), str(src_location).replace(":", "{{DRIVE}}")
                            ).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    # , trg_folder, p_name, repo, authId
                    "tf": base64.b64encode(
                        gzip.compress(
                            str(trg_folder).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "pna": base64.b64encode(
                        gzip.compress(
                            str(p_name).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "rep": base64.b64encode(
                        gzip.compress(
                            str(repo).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "ahi": base64.b64encode(
                        gzip.compress(
                            str(authId).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "jsta": base64.b64encode(
                        gzip.compress(
                            str(job_Start).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "mimet": base64.b64encode(
                        gzip.compress(
                            str(ftype).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "pNameText": base64.b64encode(
                        gzip.compress(
                            str(p_NameText).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "pIdText": base64.b64encode(
                        gzip.compress(
                            str(p_IdText).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "bkupType": base64.b64encode(
                        gzip.compress(
                            str(bkupType).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "currentfile": base64.b64encode(
                        gzip.compress(
                            str(currentfile).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "totalfiles": base64.b64encode(
                        gzip.compress(
                            str(totalfiles).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                }
                if file_hasher and seq_num == num_chunks:
                    headers["filehash"] = file_hasher.hexdigest()

                try:
                    response=None
                    # response = requests.post(
                    #     url, data=compressed_chunk, headers=headers, timeout=3000
                    # )
                    # with open("d:\\extracted_data_chunks_upload"+str(time.time()), "wb") as fchunks:
                    #     fchunks.write(compressed_chunk)
                    # fchunks.close() 
                    if bOpen :
                        files = {'file': (f'chunk_{file}_{seq_num}.bin', compressed_chunk, 'application/octet-stream')}
                        if repo in ["GDRIVE", "GOOGLEDRIVE","ONEDRIVE"]:
                            files = {'file': (f"{file}_{seq_num}.gz_{str(job_Start)}", compressed_chunk, 'application/octet-stream')}
                    else: 
                        files = compressed_chunk
                    del compressed_chunk
                    from requests_file import FileAdapter
                    for attempt_index, attempt in enumerate(RETRY_LIMIT, start=1):
                        if attempt_index > AUTO_RETRY_MAX:
                            log_event(
                                logger,
                                logging.ERROR,
                                job_id,
                                "backup",
                                file_path=open_file_name,
                                file_id=file_id,
                                chunk_index=seq_num,
                                error_code="UPLOAD_RETRY_EXHAUSTED",
                                error_message="Auto retries exhausted; manual retry required",
                                extra={
                                    "event": "chunk_retry_exhausted",
                                    "retry_count": attempt_index - 1,
                                    "retry_max": AUTO_RETRY_MAX,
                                },
                            )
                            raise RuntimeError("manual_retry_required")
                            
                        try:
                            if bOpen :
                                if repo in ["GDRIVE", "GOOGLEDRIVE","ONEDRIVE"]:
                                    if seq_num == 1:
                                        try:
                                            if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                                            if not cl_socketio_obj.connected:
                                                cl_socketio_obj.connect(
                                                    f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                                    ,wait_timeout=5
                                                    ,retry=True
                                                )
                                            if cl_socketio_obj.connected:
                                                cl_socketio_obj.emit(
                                                        "backup_data",
                                                        {
                                                            "backup_jobs": [
                                                                {
                                                                    "cloud":repo,
                                                                    "name": p_NameText,
                                                                    "scheduled_time": datetime.datetime.fromtimestamp(
                                                                        float(job_Start)
                                                                    ).strftime(
                                                                        "%H:%M:%S"
                                                                    ),
                                                                    "agent": str(str(app.config.get("getCodea",None))),
                                                                    "progress_number_upload": float(
                                                                        0.0
                                                                    )
                                                                    ,
                                                                    "id": job_Start,
                                                                    "filename":file_name,
                                                                    "repo": repo
                                                                }
                                                            ]
                                                        },
                                                    )
                                        except Exception as clerror:
                                            pass
                                    if repo in ["GDRIVE", "GOOGLEDRIVE"]:
                                        gdc = GDClient()
                                        fidi = gdc.upload_file(files, "text/abgd", str(job_Start),today_date['date'])
                                        headers['gfidi'] = json.dumps(fidi).encode('utf-8')
                                    elif repo == "ONEDRIVE":
                                        onec = None
                                        try:
                                            onec = OneDriveClient()
                                        except FileNotFoundError as onedrive_config:
                                            raise RuntimeError("Onedrive config file not found")

                                        folder_path="ApnaBackup"
                                        backup_path_onedrive = os.path.join(str(str(app.config.get("getCode",None))), str(root).replace(":", "{{DRIVE}}"), files["file"][0]+".gz")
                                        s3_key = f"{folder_path}/{backup_path_onedrive.replace(os.sep,'/')}" if folder_path else backup_path_onedrive
                                        fid=onec.upload_file(local_path= files,remote_path=s3_key)
                                    try:
                                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                                        if not cl_socketio_obj.connected:
                                            cl_socketio_obj.connect(
                                                f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                                ,wait_timeout=5
                                                ,retry=True
                                            )
                                        if cl_socketio_obj.connected:
                                            cl_socketio_obj.emit(
                                                    "backup_data",
                                                    {
                                                        "backup_jobs": [
                                                            {
                                                                "cloud":repo,
                                                                "name": p_NameText,
                                                                "scheduled_time": datetime.datetime.fromtimestamp(
                                                                    float(job_Start)
                                                                ).strftime(
                                                                    "%H:%M:%S"
                                                                ),
                                                                "agent": str(str(app.config.get("getCodea",None))),
                                                                "progress_number_upload": float(
                                                                    100 * (float(seq_num))
                                                                )
                                                                / float(num_chunks),
                                                                "id": job_Start,
                                                                "filename":file_name,
                                                                "repo": repo
                                                            }
                                                        ]
                                                    },
                                                )
                                    except Exception as clerror:
                                        pass
                                    data="E241BD06-0A09-45BC-8D4D-222E364BC14A"
                                    response = requests.post(url,  data=data, headers=headers)#, timeout=(30000,30000))
                                    response.raise_for_status()
                                    result_json = response.json()
                                    if str(result_json.get("result", {}).get("status", "")).lower() == "failed":
                                        raise RuntimeError(f"server_failed:{result_json}")
                                else:
                                    response = requests.post(url, files=files, headers=headers)#, timeout=(30000,30000))
                                    response.raise_for_status()
                                    result_json = response.json()
                                    if str(result_json.get("result", {}).get("status", "")).lower() == "failed":
                                        raise RuntimeError(f"server_failed:{result_json}")
                                break
                            else:
                                response = requests.post(url,  data=files, headers=headers)#, timeout=(30000,30000))
                                response.raise_for_status()
                                result_json = response.json()
                                if str(result_json.get("result", {}).get("status", "")).lower() == "failed":
                                    raise RuntimeError(f"server_failed:{result_json}")
                                break
                        except Exception as e:
                            backoff = RETRY_BACKOFF_BASE ** attempt
                            log_event(
                                logger,
                                logging.WARNING,
                                job_id,
                                "backup",
                                file_path=open_file_name,
                                file_id=file_id,
                                chunk_index=seq_num,
                                error_code="UPLOAD_RETRY",
                                error_message=str(e),
                                extra={
                                    "event": "chunk_retry",
                                    "retry_backoff": backoff,
                                    "retry_count": attempt_index,
                                    "retry_max": AUTO_RETRY_MAX,
                                },
                            )
                            print(f"Retrying to connect to server...........{backoff}")
                            time.sleep(backoff)

                    # chunk = f.read(chunk_size)
                    if response is None:
                        raise RuntimeError("upload_failed_all_retries")
                    try:
                        ret_val = {"total_chunks":num_chunks, "uploaded_chunks" :i,"file":file_name,"upload_result":response.json(),"exception":None}
                    except Exception as ssss:
                        ret_val = {"total_chunks":num_chunks, "uploaded_chunks" :i,"file":file_name,"upload_result":response.json(),"exception":ssss}
                        

                    if response.status_code == 200:
                        try:
                            ret_val = {"total_chunks":num_chunks, "uploaded_chunks" :i,"file":file_name,"upload_result":response.json(),"exception":None}
                        except Exception as ssss:
                            pass
                        
                        print(
                            f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                        )
                            
                        if (
                            str((response.json())["result"]["status"]).lower()
                            == "failed"
                        ):
                            log_event(
                                logger,
                                logging.ERROR,
                                job_id,
                                "backup",
                                file_path=open_file_name,
                                file_id=file_id,
                                chunk_index=seq_num,
                                error_code="UPLOAD_FAILED",
                                error_message=str((response.json())["result"]),
                                extra={"event": "chunk_failed"},
                            )
                            logger.warning(f"print full error reason of failed backup /upload {response.json()}")
                            try:
                                if cl_socketio_obj.connected:
                                    cl_socketio_obj.emit(
                                        "backup_data",
                                        {
                                            "backup_jobs": [
                                                {
                                                    "cloud": repo,
                                                    "name": p_NameText,
                                                    "id": job_Start,
                                                    "agent": str(str(app.config.get("getCodea", None))),
                                                    "filename": file_name,
                                                    "repo": repo,
                                                    "status": "failed",
                                                    "progress_number_upload": 100,
                                                }
                                            ]
                                        },
                                    )
                            except Exception:
                                pass
                            raise RuntimeError(
                                str((response.json())["result"]["status"])
                            )
                            break
                        else:
                            log_chunk_event(
                                logger,
                                logging.DEBUG,
                                job_id,
                                "backup",
                                file_path=open_file_name,
                                file_id=file_id,
                                chunk_index=seq_num,
                                extra={"event": "chunk_end"},
                            )
                    else:
                        try:
                            ret_val = {"total_chunks":num_chunks, "uploaded_chunks" :i,"file":file_name,"upload_result":response.json(),"exception":ssss}
                        except Exception as ssss:
                            ret_val = {"total_chunks":num_chunks, "uploaded_chunks" :i,"file":file_name,"upload_result":None,"exception":ssss}

                        print(
                            f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                        )
                        if (
                            str((response.json())["result"]["status"]).lower()
                            == "failed"
                        ):
                            log_event(
                                logger,
                                logging.ERROR,
                                job_id,
                                "backup",
                                file_path=open_file_name,
                                file_id=file_id,
                                chunk_index=seq_num,
                                error_code="UPLOAD_FAILED",
                                error_message=str((response.json())["result"]),
                                extra={"event": "chunk_failed"},
                            )
                            logger.warning(f"print full error reason of failed backup /upload {response.json()}")
                            try:
                                if cl_socketio_obj.connected:
                                    cl_socketio_obj.emit(
                                        "backup_data",
                                        {
                                            "backup_jobs": [
                                                {
                                                    "cloud": repo,
                                                    "name": p_NameText,
                                                    "id": job_Start,
                                                    "agent": str(str(app.config.get("getCodea", None))),
                                                    "filename": file_name,
                                                    "repo": repo,
                                                    "status": "failed",
                                                    "progress_number_upload": 100,
                                                }
                                            ]
                                        },
                                    )
                            except Exception:
                                pass
                            raise RuntimeError(
                                str((response.json())["result"]["status"])
                            )
                            break

                except Exception as ser:
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "backup",
                        file_path=open_file_name,
                        file_id=file_id,
                        chunk_index=seq_num,
                        error_code="UPLOAD_EXCEPTION",
                        error_message=str(ser),
                        extra={"event": "chunk_exception"},
                    )
                    print(str(ser))
                    raise RuntimeError(str(ser))

        else:
            if cl_socketio_obj.connected:
                cl_socketio_obj.disconnect()
            print("11data not found in file")
            #raise RuntimeError(str("11data not found in file")) 
    except Exception as sere:
        # if shm:
        #     shm.unlink()
        #     shm.close()
        if cl_socketio_obj.connected:
            cl_socketio_obj.disconnect()
        log_event(
            logger,
            logging.ERROR,
            job_id,
            "backup",
            file_path=file_name,
            file_id=file_id,
            error_code="BACKUP_FAILED",
            error_message=str(sere),
            extra={"event": "file_failed"},
        )
        print(str(sere))
        raise RuntimeError(str(sere)) 
    
    # if shm:
    #     shm.unlink()
    #     shm.close()
    if cl_socketio_obj.connected:
        cl_socketio_obj.disconnect()
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        file_id=file_id,
        extra={"event": "file_end"},
    )
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        file_id=file_id,
        extra={"event": "job_end"},
    )
    return ret_val

def hash_file(file_path, chunk_size=128 * 1024):
    import hashlib
    hasher = hashlib.sha256()
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file '{file_path}': {e}")
        return None


def start_file_streaming_v2(
    file_name,
    file,
    root,
    trg_folder,
    p_name,
    repo,
    authId,
    job_Start,
    ftype,
    p_NameText,
    p_IdText,
    currentfile,
    totalfiles,
    bkupType="full",
    chunk_size=1024 * 1024 * 64,
    src_location="",
    accuracy=0.00,
    finished=False
):
    import requests
    import gzip
    import math
    import os

    # from Crypto.Cipher import AES
    # from Crypto.Util.Padding import pad, unpad
    # from Crypto.Random import get_random_bytes

    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend

    import requests
    import base64
    import urllib
    import urllib3
    from fClient.cktio import cl_socketio_obj
    
    from fClient.p7zstd import p7zstd
    
    
    url = f"http://{app.config['server_ip']}:{app.config['server_port']}/upload"
    try:
        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
        if not cl_socketio_obj.connected:
            try:
                cl_socketio_obj.connect(f"http://{app.config['server_ip']}:{app.config['server_port']}"
                    ,wait_timeout=5
                    ,retry=True
                )
            except:
                print("")
    except:
        pass
    seq_num = 0
    headers = {}
    files_dict=[]
    compressed_data=None
    try:
        file_stat = os.stat(file_name)
        st_ino =file_stat.st_ino
        result=None
        file_stat_remote = get_remote_file_stat(backup_pid =p_IdText,file_name=file_name)
        file_stat_remote = file_stat_remote.get('result',None)
        #compressed_data = zlib.compress(b"{44A0C353-B685-4F9E-A3CF-08050440A814}", zlib.Z_BEST_COMPRESSION)
        #compressed_data = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
        compressed_data=None
        
        bOpen= True #bkupType == "full"
        remote_first_time=0
        remote_last_time=0
        if file_stat_remote:
            result = list(filter(lambda d: d.get('file_path_name').lower() == file_name.lower(), file_stat_remote))
            if result:
                if bkupType == "full" :
                    bOpen=True
                if bkupType == "incremental":
                    result=result[0]
                    bOpen=False
                if bkupType == "differential":
                    result=result[1]
                    bOpen=False
            else:
                bOpen=True
        
        if bkupType == "full":
            bOpen=True
        elif bkupType == "incremental":
            print(f"perform incremental backup of this file : {file_name} ")
            if result:
                if result.get('last_c',0) <= file_stat.st_mtime :
                    bOpen=True
            
        elif bkupType == "differential":
            print(f"perform differential backup of this file : {file_name} ")
            if result:
                if result.get('first_c',None)<=file_stat.st_mtime:
                    bOpen=True

        t_c = math.ceil(os.path.getsize(file_name) / chunk_size)
        chunks = []
        iv = bytes.fromhex("00000000000000000000000000000000")#os.urandom(16)
        iv = "00000000000000000000000000000000"
        key = getKey()
        # cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        # padder = padding.PKCS7(128).padder()

        # from runserver import a_scheduler

        j = app.apscheduler.get_job(id=p_IdText)
        if j != None:
            while not j.next_run_time:
                try:
                    if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    if not cl_socketio_obj.connected:
                        cl_socketio_obj.connect(
                            f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                            ,wait_timeout=5
                            ,retry=True             
                        )
                    time.sleep(2)
                    if cl_socketio_obj.connected:
                        cl_socketio_obj.emit(
                            "backup_data",
                            json.dumps(
                                {
                                    "backup_jobs": [
                                        {
                                            "name": p_NameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(job_Start)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": str(app.config.get("getCodeHost",None)),
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),
                                            "accuracy": accuracy,
                                            "finished": finished,                                            
                                            "id": job_Start,
                                        }
                                    ]
                                }
                            ),
                            "/",
                        )
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                except Exception as ex:
                    print(str(ex))
                    try:
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                    except:
                        pass
                time.sleep(10)
                j = app.apscheduler.get_job(id=p_IdText)
        #with open(file_name, "rb") as f:
        #if bOpen:
        compression_level=3
        digest=None
        shm=None
        num_chunks=0 
        file_size=0

        file_name = os.path.basename(file_name)
        file_size = os.path.getsize(file_name)
        file_hash = hash_file(file_name)
        chunk_number = 0
        import zstandard as myzstd 
        compression_level=3
        compressor = myzstd.ZstdCompressor(level=compression_level)
        compressor.chunker
        if bOpen:
            with OpenShFile(file_name, 'rb') as source_file, compressor.stream_reader(source_file) as compressed_stream:
                
                while True:
                   chunk = compressed_stream.read(chunk_size)
                   if not chunk:
                       break
                   
                   headers={
                       "File-Name": file,
                       "fidi": digest,
                       "quNu": str(seq_num),
                       "tc": str(math.ceil(len(compressed_data) / chunk_size)), #str(t_c),
                       "abt": "False",
                       "givn": base64.b64encode(
                           gzip.compress(
                               str(iv.hex()).encode("UTF-8"),
                               9,
                               mtime=password,
                               )
                           ),
                       "epc": base64.b64encode(
                            gzip.compress(
                                str(str(app.config.get("getCode",None))).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "epn": base64.b64encode(
                            gzip.compress(
                                str(str(app.config.get("getCodea",None))).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "tcc": base64.b64encode(
                            gzip.compress(
                                os.path.join(
                                    str(str(app.config.get("getCode",None))), str(root).replace(":", "{{DRIVE}}")
                                ).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "tccsrc": base64.b64encode(
                            gzip.compress(
                                os.path.join(
                                    str(str(app.config.get("getCode",None))), str(src_location).replace(":", "{{DRIVE}}")
                                ).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        
                        "tf": base64.b64encode(
                            gzip.compress(
                                str(trg_folder).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "pna": base64.b64encode(
                            gzip.compress(
                                str(p_name).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "rep": base64.b64encode(
                            gzip.compress(
                                str(repo).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "ahi": base64.b64encode(
                            gzip.compress(
                                str(authId).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "jsta": base64.b64encode(
                            gzip.compress(
                                str(job_Start).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "mimet": base64.b64encode(
                            gzip.compress(
                                str(ftype).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "pNameText": base64.b64encode(
                            gzip.compress(
                                str(p_NameText).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "pIdText": base64.b64encode(
                            gzip.compress(
                                str(p_IdText).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "bkupType": base64.b64encode(
                            gzip.compress(
                                str(bkupType).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "currentfile": base64.b64encode(
                            gzip.compress(
                                str(currentfile).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            ),
                        "totalfiles": base64.b64encode(
                            gzip.compress(
                                str(totalfiles).encode("UTF-8"),
                                9,
                                mtime=password,
                                )
                            )
                        }

                   try:
                        # files = {'file': (f'chunk_{file}_{seq_num}.bin', compressed_chunk, 'application/octet-stream')}
                        # files = {'file': (f"{file_name}.part{chunk_number + 1}", chunk, 'application/octet-stream')}
                        files = {'file': (f'chunk_{file}_{seq_num}.bin', chunk, 'application/octet-stream')}
                        from requests_file import FileAdapter
                        response = requests.post(url, files=files, headers=headers, timeout=(3000,3000))
                        #del compressed_chunk
                        del chunk
                    

                        if response.status_code == 200:
                            print(
                                f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                            )
                        if (
                            str((response.json())["result"]["status"]).lower()
                            == "failed"
                        ):
                            raise RuntimeError(
                                str((response.json())["result"]["status"])
                            )
                            break
                        else:
                            print(
                                f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                            )
                    
                        if (
                            str((response.json())["result"]["status"]).lower()
                            == "failed"
                        ):
                            raise RuntimeError(
                                str((response.json())["result"]["status"])
                            )
                            break

                   except Exception as ser:
                       print(str(ser))
                       raise RuntimeError(str(ser))
        
        with OpenShFile(file_name, "rb") as f:
            #with mmap.mmap(m_file.fileno(), 0, access=mmap.ACCESS_COPY) as f:
            cdigest=FileDig()
            digest= cdigest._hash_memory(f)
            file_size = f.seek(0, 2) 
            f.seek(0)
            del cdigest
            j = app.apscheduler.get_job(id=p_IdText)
            if j != None:
                while not j.next_run_time:
                    try:
                        if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                        if not cl_socketio_obj.connected:
                            cl_socketio_obj.connect(
                                f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                ,wait_timeout=5
                                ,retry=True
                            )
                        if cl_socketio_obj.connected:
                            cl_socketio_obj.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "status": "progress",
                                            "name": p_NameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(job_Start)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": str(app.config.get("getCodea",None)),
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),                                            
                                            "accuracy": accuracy,
                                            "finished": finished,
                                            "id": job_Start,
                                        }
                                    ]
                                },
                            )
                        time.sleep(10)
                    except:
                        pass 
                    j = app.apscheduler.get_job(id=p_IdText)
            f.seek(0)
            if bOpen:
                file_signature = f.read(16)
                for signature, level in SIGNATURE_MAP_COMPRESSION_LEVEL.items():
                    if file_signature.startswith(signature):
                        if level is None:
                            compression_level= 1
                        else:
                            compression_level= level
                    
                if file_size < 1 * 1024 * 1024:   # < 1 MB ==> Max compression
                    compression_level = min(compression_level + 3, 9)
                elif file_size < 100 * 1024 * 1024: # < 100 MB ==> High compression
                    compression_level = min(compression_level + 2, 9)
                elif file_size < 1 * 1024 * 1024 * 1024: # < 1 GB ==> Medium compression
                    compression_level = compression_level
                else:  # > 1 GB ==> Fast compression
                    compression_level = max(compression_level - 2, 1)

                f.seek(0)
                #compressed_data = f.read()
                shm= multiprocessing.shared_memory.SharedMemory(create=True,size=file_size)
                shm.buf[:file_size] = f[:]
                chunk_size = get_optimal_chunk_size(file_size=file_size)
                num_chunks=file_size//chunk_size
                compressed_data =num_chunks !=0
                t_c = math.ceil(file_size / chunk_size)
            f.close()
            if not bOpen:
                compressed_data = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
            if compressed_data:
                if repo in ["GDRIVE", "LAN", "LOCAL", "LOCAL STORAGE","AWSS3","AZURE","ONEDRIVE"]:
                    if bOpen: #if there is a change in file
                        #compressed_data = zlib.compress(compressed_data,level=int(compression_level))
                        pZip= p7zstd(iv,preset=int(compression_level))
                        compressed_data = pZip.compress_chunk_shared(shm_name= shm.name,chunk_size= chunk_size,num_chunks= num_chunks)
                        #compressed_data= pZip.compress(data=compressed_data,file_name=file_name)
                        del pZip
                        shm.unlink()
                        shm.close()

                        print("")
                    else:
                        compressed_data = b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
                    if isinstance(iv,(str)):
                        #iv = bytes.fromhex(iv)
                        iv = iv.encode()


                chunk_num = 0
                seq_num = 0

                t_c_count = math.ceil(len(compressed_data) / chunk_size)+1
                for i in range(0, len(compressed_data), chunk_size):
                    t_c_count=t_c_count-1
                    chunk = compressed_data[i : i + chunk_size]
                    isLast = (i + chunk_size) ==len(compressed_data)
                    if isLast or t_c_count==1:
                        print("ppppppppppppppppppppppppppppppppppppppppppppppppppppppp")


                    password = time.time()
                    # compressed_chunk = gzip.compress(chunk, 9, mtime=password)

                    root_ = root
                    seq_num = seq_num + 1
                    compressed_chunk = chunk
                    # if repo in ["LAN", "LOCAL", "LOCAL STORAGE"]:
                    #     compressed_chunk = gzip.compress(chunk, 9, mtime=password)
                    #     print("")
                    # elif str(repo).upper() in ["GDRIVE","AWSS3","AZURE","ONEDRIVE"]:
                    #     compressed_chunk = gzip.compress(
                    #         chunk, 9, mtime=password
                    #     )

                    headers = {
                        "File-Name": file,
                        "fidi": digest,
                        "quNu": str(seq_num),
                        "tc": str(math.ceil(len(compressed_data) / chunk_size)), #str(t_c),
                        "abt": "False",
                        "givn": base64.b64encode(
                            gzip.compress(
                                str(iv.hex()).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "epc": base64.b64encode(
                            gzip.compress(
                                str(str(app.config.get("getCode",None))).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "epn": base64.b64encode(
                            gzip.compress(
                                str(str(app.config.get("getCodea",None))).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "tcc": base64.b64encode(
                            gzip.compress(
                                os.path.join(
                                    str(str(app.config.get("getCode",None))), str(root).replace(":", "{{DRIVE}}")
                                ).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "tccsrc": base64.b64encode(
                            gzip.compress(
                                os.path.join(
                                    str(str(app.config.get("getCode",None))), str(src_location).replace(":", "{{DRIVE}}")
                                ).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        # , trg_folder, p_name, repo, authId
                        "tf": base64.b64encode(
                            gzip.compress(
                                str(trg_folder).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "pna": base64.b64encode(
                            gzip.compress(
                                str(p_name).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "rep": base64.b64encode(
                            gzip.compress(
                                str(repo).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "ahi": base64.b64encode(
                            gzip.compress(
                                str(authId).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "jsta": base64.b64encode(
                            gzip.compress(
                                str(job_Start).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "mimet": base64.b64encode(
                            gzip.compress(
                                str(ftype).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "pNameText": base64.b64encode(
                            gzip.compress(
                                str(p_NameText).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "pIdText": base64.b64encode(
                            gzip.compress(
                                str(p_IdText).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "bkupType": base64.b64encode(
                            gzip.compress(
                                str(bkupType).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "currentfile": base64.b64encode(
                            gzip.compress(
                                str(currentfile).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                        "totalfiles": base64.b64encode(
                            gzip.compress(
                                str(totalfiles).encode("UTF-8"),
                                9,
                                mtime=password,
                            )
                        ),
                    }

                    try:

                        files = {'file': (f'chunk_{file}_{seq_num}.bin', compressed_chunk, 'application/octet-stream')}
                        from requests_file import FileAdapter
                        response = requests.post(
                            url, files=files, headers=headers, timeout=3000
                        )
                        del compressed_chunk
                        # chunk = f.read(chunk_size)

                        if response.status_code == 200:
                            print(
                                f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                            )
                            if (
                                str((response.json())["result"]["status"]).lower()
                                == "failed"
                            ):
                                raise RuntimeError(
                                    str((response.json())["result"]["status"])
                                )
                                break
                        else:
                            print(
                                f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                            )
                            if (
                                str((response.json())["result"]["status"]).lower()
                                == "failed"
                            ):
                                raise RuntimeError(
                                    str((response.json())["result"]["status"])
                                )
                                break

                    except Exception as ser:
                        print(str(ser))
                        raise RuntimeError(str(ser))
            else:
                if cl_socketio_obj.connected:
                    cl_socketio_obj.disconnect
                print(str(ser))
                #raise RuntimeError(str("2data not found in file")) 
    except Exception as ser:
        if shm:
            shm.unlink()
            shm.close()
        if cl_socketio_obj.connected:
            cl_socketio_obj.disconnect
        print(str(ser))
        raise RuntimeError(str(ser))

    
    if shm:
        shm.unlink()
        shm.close()
    if cl_socketio_obj.connected:
        cl_socketio_obj.disconnect


def create_custom_job(scheduler: APScheduler, json):
    hasjob = scheduler.get_job(cjb_Desktop())
    if hasjob is None:
        try:
            trigger = CronTrigger(
                day_of_week="sun,mon,tue,wed,thu,fri,sat",
                hour="13",
                minute="30",
                second="0",
            )
            scheduler.add_job(
                func=cjb_Desktop(),
                trigger=trigger,
                id="Desktop_" + str(app.config.get("getCode",None)),
                name="Dektop Backup " + scheduler.host_name,
                misfire_grace_time=3600 * 50,
            )
        except Exception as e:
            print(str(e))
            print("error creating scheduler for desktop")


def create_default_jobs(scheduler: APScheduler, succ_listener, err_listener):
    return
    hasjob = scheduler.get_job("Desktop_" + str(app.config.get("getCode",None)))
    if hasjob is None:
        try:
            trigger = CronTrigger(
                day_of_week="sun,mon,tue,wed,thu,fri,sat",
                hour="13",
                minute="30",
                second="0",
            )
            scheduler.add_job(
                func="fClient.sjbs.class1:cjb_Desktop",
                trigger=trigger,
                id="Desktop_" + str(app.config.get("getCode",None)),
                name="Dektop Backup " + scheduler.host_name,
                misfire_grace_time=3600 * 50,
            )

        except Exception as e:
            print(str(e))
            print("error creating scheduler for desktop")

    hasjob = scheduler.get_job("Videos_" + str(app.config.get("getCode",None)))
    if hasjob is None:
        try:
            trigger = CronTrigger(
                day_of_week="sun,mon,tue,wed,thu,fri,sat",
                hour="13",
                minute="35",
                second="0",
            )
            scheduler.add_job(
                func=cjb_Videos,
                trigger=trigger,
                id="Videos_" + str(app.config.get("getCode",None)),
                name="Videos Backup " + scheduler.host_name,
                misfire_grace_time=3600 * 50,
            )
        except Exception as e:
            print(str(e))
            print("error creating scheduler for Videos")

    hasjob = scheduler.get_job("Pictures_" + str(app.config.get("getCode",None)))
    if hasjob is None:
        try:
            trigger = CronTrigger(
                day_of_week="sun,mon,tue,wed,thu,fri,sat",
                hour="13",
                minute="40",
                second="0",
            )
            scheduler.add_job(
                func=cjb_Pictures,
                trigger=trigger,
                id="Pictures_" + str(app.config.get("getCode",None)),
                name="Pictures Backup " + scheduler.host_name,
                misfire_grace_time=3600 * 50,
            )
        except Exception as e:
            print(str(e))
            print("error creating scheduler for desktop")

    hasjob = scheduler.get_job("Documents_" + str(app.config.get("getCode",None)))
    if hasjob is None:
        try:
            trigger = CronTrigger(
                day_of_week="sun,mon,tue,wed,thu,fri,sat",
                hour="13",
                minute="45",
                second="0",
            )
            scheduler.add_job(
                func=cjb_Documents,
                trigger=trigger,
                id="Documents_" + str(app.config.get("getCode",None)),
                name="Documents Backup of " + scheduler.host_name,
                misfire_grace_time=3600 * 50,
            )
        except Exception as e:
            print(str(e))
            print("error creating scheduler for Documents")

    hasjob = scheduler.get_job("Downloads_" + str(app.config.get("getCode",None)))
    if hasjob is None:
        try:
            trigger = CronTrigger(
                day_of_week="sun,mon,tue,wed,thu,fri,sat",
                hour="13",
                minute="50",
                second="0",
            )
            scheduler.add_job(
                func=cjb_Download,
                trigger=trigger,
                id="Downloads_" + str(app.config.get("getCode",None)),
                name="Downloads Backup of " + scheduler.host_name,
                misfire_grace_time=3600 * 50,
            )
        except Exception as e:
            print(str(e))
            print("error creating scheduler for Downloads")

    scheduler.add_listener(err_listener, EVENT_JOB_MISSED | EVENT_JOB_ERROR)
    scheduler.add_listener(succ_listener, EVENT_JOB_EXECUTED)

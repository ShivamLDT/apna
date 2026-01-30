# import os
# import json
# import datetime
# import time
# from ctypes import *
# from websocket import create_connection

# # Constants and WinAPI function declarations
# MAX_PATH = 260
# INVALID_HANDLE_VALUE = c_void_p(-1).value
# FILE_ATTRIBUTE_DIRECTORY = 0x10

# kernel32 = windll.kernel32

# FindFirstFileW = kernel32.FindFirstFileW
# FindNextFileW = kernel32.FindNextFileW
# FindClose = kernel32.FindClose

# # Structure for WIN32_FIND_DATA
# class WIN32_FIND_DATAW(Structure):
#     _fields_ = [
#         ("dwFileAttributes", c_uint),
#         ("cCreationTime", c_uint * 2),
#         ("cLastAccessTime", c_uint * 2),
#         ("cLastWriteTime", c_uint * 2),
#         ("nFileSizeHigh", c_uint),
#         ("nFileSizeLow", c_uint),
#         ("dwReserved0", c_uint),
#         ("dwReserved1", c_uint),
#         ("cFileName", c_wchar * MAX_PATH),
#         ("cAlternateFileName", c_wchar * 14)
#     ]

# def traverse_directory_winapi(directory):
#     find_data = WIN32_FIND_DATAW()
#     handle = FindFirstFileW(f"{directory}\\*", byref(find_data))
    
#     if handle == INVALID_HANDLE_VALUE:
#         raise Exception("Error opening directory")

#     while True:
#         file_name = find_data.cFileName
#         if file_name not in (".", ".."):
#             yield os.path.join(directory, file_name)
#             if find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY:
#                 yield from traverse_directory_winapi(os.path.join(directory, file_name))

#         if not FindNextFileW(handle, byref(find_data)):
#             break

#     FindClose(handle)

# def connect_and_emit(cl, app, p_IdText, p_NameText, job_Start, progress):
#     try:
#         if not cl.connected:
#             cl.connect(f"ws://{app.config['server_ip']}:{app.config['server_port']}")
#         time.sleep(2)

#         if cl.connected:
#             cl.emit(
#                 "starting",
#                 json.dumps({
#                     "backup_jobs": [
#                         {
#                             "status": "counting",
#                             "paused": False,
#                             "name": p_NameText,
#                             "scheduled_time": datetime.datetime.fromtimestamp(float(job_Start)).strftime("%H:%M:%S"),
#                             "agent": str(app.config.get("getCodeHost", None)),
#                             "progress_number": float(progress),
#                         }
#                     ]
#                 }),
#                 "/backup_jobs"
#             )
#     except Exception as e:
#         print(f"Exception: {str(e)}")
#     finally:
#         if cl.connected:
#             cl.disconnect()

# def process_files(src_folder, app, cl, p_IdText, p_NameText, job_Start, all_types, all_selected_types):
#     ixs = 0
#     f_files = []

#     for file_path in traverse_directory_winapi(src_folder):
#         root, file_name = os.path.split(file_path)
#         j = app.apscheduler.get_job(id=p_IdText)
        
#         if j:
#             while not j.next_run_time:
#                 connect_and_emit(cl, app, p_IdText, p_NameText, job_Start, 0)
#                 time.sleep(2)
#                 if cl.connected:
#                     cl.disconnect()
#                 j = app.apscheduler.get_job(id=p_IdText)

#         if all_types:
#             ff_files = [file_path]
#             ixs += len(ff_files)
#             if ixs % 1000 == 0:  # Example condition for progress update
#                 connect_and_emit(cl, app, p_IdText, p_NameText, job_Start, ixs)
#         else:
#             if any(file_name.endswith(ext) for ext in all_selected_types):
#                 ff_files = [file_path]
#                 ixs += 1
#                 if ixs % 1000 == 0:  # Example condition for progress update
#                     connect_and_emit(cl, app, p_IdText, p_NameText, job_Start, ixs)
#                 time.sleep(0.1)

#         f_files.extend(ff_files)

#     return f_files

# # Example usage
# # Define your variables here, e.g.:
# # src_folder, app, cl, p_IdText, p_NameText, job_Start, all_types, all_selected_types

# # result = process_files(src_folder, app, cl, p_IdText, p_NameText, job_Start, all_types, all_selected_types)
###################################################################################

import os
from ctypes import *
from ctypes.wintypes import *

# Constants
MAX_PATH = 260
INVALID_HANDLE_VALUE = c_void_p(-1).value
FILE_ATTRIBUTE_DIRECTORY = 0x10
ERROR_NO_MORE_FILES = 18
ERROR_ACCESS_DENIED = 5

kernel32 = windll.kernel32

FindFirstFileW = kernel32.FindFirstFileW
FindNextFileW = kernel32.FindNextFileW
FindClose = kernel32.FindClose
GetLastError = kernel32.GetLastError

# Define WIN32_FIND_DATAW structure
class WIN32_FIND_DATAW(Structure):
    _fields_ = [
        ("dwFileAttributes", DWORD),
        ("ftCreationTime", FILETIME),
        ("ftLastAccessTime", FILETIME),
        ("ftLastWriteTime", FILETIME),
        ("nFileSizeHigh", DWORD),
        ("nFileSizeLow", DWORD),
        ("dwReserved0", DWORD),
        ("dwReserved1", DWORD),
        ("cFileName", WCHAR * MAX_PATH),
        ("cAlternateFileName", WCHAR * 14)
    ]

def traverse_directory_winapi(directory):
    """ Iteratively traverse a directory using the C-style approach """

    if not os.path.exists(directory):
        print(f"[ERROR] Directory '{directory}' does not exist.")
        return

    # Use \\?\ prefix to handle long paths correctly in Windows
    directory = f"\\\\?\\{directory}"

    stack = [directory]  # Stack-based traversal
    visited_dirs = set()

    while stack:
        current_dir = stack.pop()

        if current_dir in visited_dirs:
            continue  # Prevent infinite loops in case of symlinks
        visited_dirs.add(current_dir)

        find_data = WIN32_FIND_DATAW()
        search_path = f"{current_dir}\\*"

        handle = FindFirstFileW(c_wchar_p(search_path), byref(find_data))

        if handle == INVALID_HANDLE_VALUE:
            error_code = GetLastError()
            if error_code == ERROR_ACCESS_DENIED:
                print(f"[WARNING] Access denied: {current_dir}")
            else:
                print(f"[ERROR] Cannot access {current_dir}, Error code: {error_code}")
            continue

        print(f"[INFO] Opened handle for: {current_dir}")

        try:
            while True:
                file_name = find_data.cFileName
                if file_name not in (".", ".."):  # Ignore special entries
                    file_path = os.path.join(current_dir, file_name)

                    yield file_path  # Yield file/folder name

                    if find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY:
                        stack.append(file_path)  # Push directory for later traversal

                if not FindNextFileW(handle, byref(find_data)):
                    if GetLastError() == ERROR_NO_MORE_FILES:
                        break  # No more files, exit loop
                    else:
                        print(f"[ERROR] FindNextFileW failed in '{current_dir}', Error code: {GetLastError()}")
                        break

        finally:
            FindClose(handle)  # Ensure handle is always closed
            print(f"[INFO] Closed handle for: {current_dir}")

    print(f"[INFO] Traversal completed: {directory}")

def process_files(src_folder):
    """ Processes files in the given folder """
    try:
        for file_path in traverse_directory_winapi(src_folder):
            print(file_path)
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")

# Example usage
src_folder = "D:\\253 data files"
process_files(src_folder)

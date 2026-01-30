
import ctypes
import win32security
import win32file
import win32api
from shadowcopy import shadow, shadow_copy
# Constants
SE_BACKUP_NAME = "SeBackupPrivilege"
TOKEN_ADJUST_PRIVILEGES = 0x20
TOKEN_QUERY = 0x8
SE_PRIVILEGE_ENABLED = 0x2
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x1
OPEN_EXISTING = 0x3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000  # Important for reading system files

# Define INVALID_HANDLE_VALUE correctly
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

# Enable backup privilege
def enable_backup_privilege():
    hToken = win32security.OpenProcessToken(
        win32api.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
    )
    privilege_id = win32security.LookupPrivilegeValue(None, SE_BACKUP_NAME)
    new_privilege = [(privilege_id, SE_PRIVILEGE_ENABLED)]
    win32security.AdjustTokenPrivileges(hToken, 0, new_privilege)

# Read file using BackupRead
def backup_read_file(file_path):
    enable_backup_privilege()
    
    # Open file with FILE_FLAG_BACKUP_SEMANTICS
    hFile = win32file.CreateFile(
        file_path, GENERIC_READ, FILE_SHARE_READ, None, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, None
    )

    if hFile.handle == INVALID_HANDLE_VALUE:
        print(f"Failed to open {file_path} (Handle is INVALID)")
        return

    buffer_size = 4096*1024
    buffer = ctypes.create_string_buffer(buffer_size)
    bytes_read = ctypes.c_ulong(0)
    context = ctypes.c_void_p(0)

    data = b""
    from time import time
    t1 = time()
    while True:
        success = ctypes.windll.kernel32.BackupRead(
            hFile.handle, buffer, buffer_size, ctypes.byref(bytes_read), False, False, ctypes.byref(context)
        )
        if not success or bytes_read.value == 0:
            break
        data += buffer.raw[:bytes_read.value]
    print (time()-t1)
    print("File Content:\n", data.decode(errors="ignore"))
    
    # Close handle
    win32file.CloseHandle(hFile)

# Example usage
# file_path = "C:\\Windows\\System32\\config\\SAM"  # Example protected file
# try:
#     backup_read_file(file_path)
# except Exception as e:
#     print("Error:", e)
file_path = "C:\\Users\\user\\Documents\\Outlook Files\\hod.software@3handshake.in.pst"
try:
    shadow_copy(file_path,file_path+"ASDF")
    #backup_read_file(file_path)
    exit()
except Exception as e:
    print("Error:", e)

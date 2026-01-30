#filecopy
import ctypes
from ctypes import wintypes

kernel32 = ctypes.windll.kernel32

# Define constants
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_FLAG_OVERLAPPED = 0x40000000
INVALID_HANDLE_VALUE = -1
CREATE_ALWAYS = 2
ERROR_IO_PENDING = 997
INFINITE = 0xFFFFFFFF

class OVERLAPPED(ctypes.Structure):
    _fields_ = [
        ("Internal", ctypes.c_void_p),
        ("InternalHigh", ctypes.c_void_p),
        ("Offset", ctypes.c_ulong),
        ("OffsetHigh", ctypes.c_ulong),
        ("hEvent", wintypes.HANDLE)
    ]


def copy_file_in_use(source, destination):
    try:
        # Open the source file
        source_handle = kernel32.CreateFileW(
            source,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_OVERLAPPED,
            None
        )
        if source_handle == INVALID_HANDLE_VALUE:
            raise Exception(f"Failed to open source file: {source} (Error: {kernel32.GetLastError()})")

        # Create the destination file
        destination_handle = kernel32.CreateFileW(
            destination,
            GENERIC_WRITE,
            0,
            None,
            CREATE_ALWAYS,
            FILE_FLAG_OVERLAPPED,
            None
        )
        if destination_handle == INVALID_HANDLE_VALUE:
            kernel32.CloseHandle(source_handle)
            raise Exception(f"Failed to create destination file: {destination} (Error: {kernel32.GetLastError()})")

        # Buffer size and overlapped structure
        buffer_size = 65536  # 64 KB
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = wintypes.DWORD(0)
        bytes_written = wintypes.DWORD(0)

        overlapped = OVERLAPPED()
        overlapped.hEvent = kernel32.CreateEventW(None, True, False, None)

        if not overlapped.hEvent:
            kernel32.CloseHandle(source_handle)
            kernel32.CloseHandle(destination_handle)
            raise Exception(f"Failed to create overlapped event (Error: {kernel32.GetLastError()})")

        offset = 0
        izi=1
        while True:
            print(izi)
            izi+=1
            overlapped.Offset = offset & 0xFFFFFFFF
            overlapped.OffsetHigh = (offset >> 32) & 0xFFFFFFFF

            success = kernel32.ReadFile(source_handle, buffer, buffer_size, None, ctypes.byref(overlapped))

            if not success and kernel32.GetLastError() != ERROR_IO_PENDING:
                raise Exception(f"Error reading file: {kernel32.GetLastError()}")

            # Wait for the read operation to complete
            kernel32.WaitForSingleObject(overlapped.hEvent, INFINITE)
            success = kernel32.GetOverlappedResult(source_handle, ctypes.byref(overlapped), ctypes.byref(bytes_read), True)

            if not success or bytes_read.value == 0:
                break  # End of file or error

            # Write to the destination file
            success = kernel32.WriteFile(destination_handle, buffer, bytes_read, None, ctypes.byref(overlapped))

            if not success and kernel32.GetLastError() != ERROR_IO_PENDING:
                raise Exception(f"Error writing file: {kernel32.GetLastError()}")

            # Wait for the write operation to complete
            kernel32.WaitForSingleObject(overlapped.hEvent, INFINITE)
            success = kernel32.GetOverlappedResult(destination_handle, ctypes.byref(overlapped), ctypes.byref(bytes_written), True)

            if not success or bytes_written.value != bytes_read.value:
                raise Exception("Failed to write all bytes to destination file")

            offset += bytes_read.value  # Update the offset

        # Clean up handles
        kernel32.CloseHandle(source_handle)
        kernel32.CloseHandle(destination_handle)
        kernel32.CloseHandle(overlapped.hEvent)

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


# Example usage
if __name__ == "__main__":
    import time
    source_file = "D:\\PyRepos\\FlaskWebProject3\\fClient\\e67bd65687a3391c20bf93c3b587901b9c82050f4c86b465d0a5ec8f776d11e2 .db"
    source_file = "C:\\Users\\user\\Documents\\Outlook Files\\hod.software@3handshake.in.pst"

    destination_file = f"C:\\Users\\user\\Documents\\of\\{time.time()}.software@3handshake.in.pst"

    if copy_file_in_use(source_file, destination_file):
        print(f"File '{source_file}' copied successfully to '{destination_file}'")
    else:
        print(f"Failed to copy file '{source_file}'.")
  
# if __name__ == "__main__":
#     source_file = "C:\\Users\\user\\Documents\\Outlook Files\\hod.software@3handshake.in.pst"
#     destination_file = "C:\\Users\\user\\Documents\\of\\hod.software@3handshake.in.pst"

#     if copy_file_in_use(source_file, destination_file):
#         print(f"File '{source_file}' copied successfully to '{destination_file}'")
#     else:
#         print(f"Failed to copy file '{source_file}'.")

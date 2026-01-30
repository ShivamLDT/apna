 
# class OVERLAPPED(ctypes.Structure):
#     _fields_ = [
#         ("Internal", ctypes.c_void_p),
#         ("InternalHigh", ctypes.c_void_p),
#         ("Offset", ctypes.c_ulong),
#         ("OffsetHigh", ctypes.c_ulong),
#         ("hEvent", wintypes.HANDLE)
#     ]
#     
import ctypes
from ctypes import wintypes

kernel32 = ctypes.windll.kernel32

# Define constants
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
GENERIC_READ = 0x80000000
FILE_FLAG_OVERLAPPED = 0x40000000
INVALID_HANDLE_VALUE = -1
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


class LockedFileReader2:
    """
    A context manager for reading locked or in-use files in chunks using asynchronous I/O.
    """
    def __init__(self, filepath, chunk_size=1024):  # Default chunk size: 1 MB
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.handle = None
        self.overlapped = None

    def __enter__(self):
        try:
            # Open the file in shared mode with overlapped I/O
            self.handle = kernel32.CreateFileW(
                self.filepath,
                GENERIC_READ,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                FILE_FLAG_OVERLAPPED,
                None
            )
            if self.handle == INVALID_HANDLE_VALUE:
                raise ctypes.WinError(kernel32.GetLastError())

            # Initialize OVERLAPPED structure
            self.overlapped = OVERLAPPED()
            self.overlapped.hEvent = kernel32.CreateEventW(None, True, False, None)
            if not self.overlapped.hEvent:
                kernel32.CloseHandle(self.handle)
                raise ctypes.WinError(kernel32.GetLastError())

            return self
        except Exception as e:
            raise RuntimeError(f"Failed to open file for reading: {e}")

    def read_chunks(self):
        """
        A generator to read the file in chunks using asynchronous I/O.
        """
        if not self.handle:
            raise RuntimeError("File handle is not open.")

        offset = 0
        buffer = ctypes.create_string_buffer(self.chunk_size)
        bytes_read = wintypes.DWORD()

        while True:
            # Set the offset in the OVERLAPPED structure
            self.overlapped.Offset = offset & 0xFFFFFFFF
            self.overlapped.OffsetHigh = (offset >> 32) & 0xFFFFFFFF

            # Asynchronous read
            success = kernel32.ReadFile(
                self.handle,
                buffer,
                self.chunk_size,
                None,
                ctypes.byref(self.overlapped)
            )
            if not success and kernel32.GetLastError() != ERROR_IO_PENDING:
                raise ctypes.WinError(kernel32.GetLastError())

            # Wait for the read operation to complete
            kernel32.WaitForSingleObject(self.overlapped.hEvent, INFINITE)
            success = kernel32.GetOverlappedResult(self.handle, ctypes.byref(self.overlapped), ctypes.byref(bytes_read), True)
            if not success or bytes_read.value == 0:
                break  # End of file or error

            # Yield the data read from the file
            yield buffer[:bytes_read.value]

            # Update the offset for the next read
            offset += bytes_read.value

    def __exit__(self, exc_type, exc_value, traceback):
        # Clean up handles
        if self.handle:
            kernel32.CloseHandle(self.handle)
        if self.overlapped and self.overlapped.hEvent:
            kernel32.CloseHandle(self.overlapped.hEvent)


def open_locked_file(filepath, chunk_size=1024 * 1024):
    """
    Mimics the `open` function for locked files, supporting binary read modes only.
    """
    return LockedFileReader2(filepath, chunk_size)


# Example Usage
if __name__ == "__main__":
    filepath = f"C:\\Users\\user\\Documents\\Outlook Files\\hod.software@3handshake.in.pst"

    try:
        i=1
        with open_locked_file(filepath, chunk_size=1) as locked_file:  # 64 KB chunks
            for chunk in locked_file.read_chunks():
                # Process the chunk (e.g., save, decode, etc.)
                print(f"{i}Read {len(chunk)}bytes {chunk.decode('UTF-8', errors='replace')}")
                i+=1
    except Exception as e:
        print(f"Error: {e}")

    print("Done reading locked file.")

# # Usage Example
# if __name__ == "__main__":
#     import time
#     d = "large_locked_file.txt"  # Path to your locked or in-use file
#     d = f"C:\\Users\\user\\Documents\\Outlook Files\\hod.software@3handshake.in.pst"
#     destination_file = f"C:\\Users\\user\\Documents\\of\\hod.software{time.time()}@3handshake.in.pst"

#     try:
#         with open_locked_file(d, "rb", chunk_size=1024 * 1024) as locked_file:  # 1 MB chunks
#             for chunk in locked_file.read_chunks():
#                 # Process each chunk (e.g., decode, save, etc.)
#                 print(chunk.decode("UTF-8", errors="replace"))
#     except Exception as e:
#         print(f"Error: {e}")

#     print("Done reading locked file.")


import ctypes
from ctypes import wintypes

# Load kernel32.dll
kernel32 = ctypes.windll.kernel32

# Define constants
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = -1

class LockedFileReaderBackupRead:
    """
    A class for reading locked or in-use files using the BackupRead API.
    """
    def __init__(self, filepath, buffer_size=64 * 1024):
        self.filepath = filepath
        self.handle = None
        self.buffer_size = buffer_size

    def open_file(self):
        """
        Opens the file with shared read/write and backup semantics.
        """
        self.handle = kernel32.CreateFileW(
            self.filepath,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
        if self.handle == INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())
        print(f"Opened file handle: {self.handle}")

    def read_file(self):
        """
        Reads the file in chunks using BackupRead.
        """
        if self.handle is None:
            raise RuntimeError("File handle is not open.")

        buffer = ctypes.create_string_buffer(self.buffer_size)
        bytes_read = wintypes.DWORD()
        context = ctypes.c_void_p()  # Backup context handle

        try:
            while True:
                success = kernel32.BackupRead(
                    self.handle,
                    buffer,
                    self.buffer_size,
                    ctypes.byref(bytes_read),
                    False,  # Abort flag
                    False,  # Process security
                    ctypes.byref(context)
                )
                if not success:
                    error_code = kernel32.GetLastError()
                    if error_code == 0:  # End of file
                        break
                    else:
                        raise ctypes.WinError(error_code)

                # Process the data (e.g., write to another file or print)
                print(buffer.raw[:bytes_read.value].decode("utf-8", errors="replace"))

                # If no more data is read, break
                if bytes_read.value == 0:
                    break
        finally:
            # End BackupRead session
            if context:
                kernel32.BackupRead(self.handle, None, 0, None, True, False, ctypes.byref(context))

    def close_file(self):
        """
        Closes the file handle.
        """
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None
            print("Closed file handle.")

    def __enter__(self):
        self.open_file()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_file()


# Usage Example
if __name__ == "__main__":
    locked_file_path = r"C:\Users\user\Documents\Outlook Files\example_locked_file.pst"
    locked_file_path = "C:\\Users\\user\\Documents\\Outlook Files\\hod.software@3handshake.in.pst"


    try:
        # Use the LockedFileReaderBackupRead context manager
        with LockedFileReaderBackupRead(locked_file_path) as reader:
            reader.read_file()
    except Exception as e:
        print(f"Error: {e}")

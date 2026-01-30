
import win32file




class LockedFileReader:
    # Define constants if they are not available

    """
    A context manager for reading locked or in-use files in chunks.
    """
    def __init__(self, filepath, chunk_size=1024 * 1024):  # Default chunk size: 1 MB
        self.filepath = filepath
        self.handle = None
        self.chunk_size = chunk_size

        self.CREATE_ALWAYS = getattr(win32file, "CREATE_ALWAYS", 2)
        self.OPEN_EXISTING = getattr(win32file, "OPEN_EXISTING", 3)
        self.FILE_SHARE_READ = getattr(win32file, "FILE_SHARE_READ", 1)
        self.FILE_SHARE_WRITE = getattr(win32file, "FILE_SHARE_WRITE", 2)
        self.FILE_SHARE_DELETE = getattr(win32file, "FILE_SHARE_DELETE", 4)
    def __enter__(self):
        try:
            # Open the file in shared read mode
            self.handle = win32file.CreateFile(
                self.filepath,
                win32file.GENERIC_READ,
                self.FILE_SHARE_READ | self.FILE_SHARE_WRITE | self.FILE_SHARE_DELETE,
                None,
                self.OPEN_EXISTING,
                0,
                None
            )
            return self
        except Exception as e:
            raise RuntimeError(f"Failed to open locked file for reading: {e}")

    def read_chunks(self):
        """
        A generator to read the file in chunks while handling locked portions gracefully.
        """
        if self.handle is None:
            raise RuntimeError("File handle is not open.")
        
        position = 0
        while True:
            try:
                # Move the file pointer to the current position
                win32file.SetFilePointer(self.handle, position, win32file.FILE_BEGIN)
                _, data = win32file.ReadFile(self.handle, self.chunk_size)
                if not data:  # End of file
                    break
                yield data
                position += len(data)  # Update position for the next read
            except win32file.error as e:
                # Handle specific error for locked portions
                if e.winerror == 33:  # ERROR_LOCK_VIOLATION
                    print(f"Warning: Skipping locked portion at position {position}.")
                    position += self.chunk_size  # Skip locked portion
                else:
                    raise RuntimeError(f"Failed to read from file: {e}")

    def __exit__(self, exc_type, exc_value, traceback):
        if self.handle:
            try:
                win32file.CloseHandle(self.handle)
            except Exception as e:
                print(f"Warning: Failed to close file handle: {e}")


def open_locked_file(filepath, mode, chunk_size=1024 * 1024):
    """
    Mimics the `open` function for locked files, supporting binary read modes only.
    """
    if "r" not in mode or "b" not in mode:
        raise ValueError("Only binary read modes (e.g., 'rb') are supported for locked files.")
    return LockedFileReader(filepath, chunk_size)


# Usage Example
if __name__ == "__main__":
    d = "large_locked_file.txt"  # Path to your locked or in-use file
    d = "C:\\Users\\user\\Documents\\Outlook Files\\hod.software@3handshake.in.pst"
    destination_file = "C:\\Users\\user\\Documents\\of\\hod.software@3handshake.in.pst"

    try:
        with open_locked_file(d, "rb", chunk_size=1024 * 1024) as locked_file:  # 1 MB chunks
            for chunk in locked_file.read_chunks():
                # Process each chunk (e.g., decode, save, etc.)
                print(chunk.decode("UTF-8", errors="replace"))
    except Exception as e:
        print(f"Error: {e}")

    print("ddddddddddddddddddddddddddd")



import os
import time
import hashlib
import blake3
import xxhash
import threading
import mmap

class FileDig:
    def __init__(self, algo="xxhash", chunk_size=100 * 1024* 1024):
        """
        Initialize the hasher.
        :param algo: Choose 'xxhash' (default) or 'blake3'.
        :param chunk_size: Read file in chunks of this size (default 1MB).
        """
        self.chunk_size = chunk_size
        self.algo = algo.lower()
        if self.algo not in ["xxhash", "blake3"]:
            raise ValueError("Algorithm must be 'xxhash' or 'blake3'.")
    def _get_hasher(self):
        """Returns the appropriate hash object based on the algorithm."""
        if self.algo == "xxhash":
            return xxhash.xxh3_128()
        else:
            return blake3.blake3()
    
    def _hash_memory(self, data):
        """
        Compute hash for in-memory data.
        :param data: A bytes-like object (e.g., memory buffer, bytearray).
        :return: Hex digest of the data.
        """
        if not isinstance(data, mmap.mmap):
            raise TypeError("Data must be bytes, bytearray, or memoryview.")
        
        hasher = self._get_hasher()
        try:
            while chunk := data.read(self.chunk_size):
                    hasher.update(chunk)
        except Exception as e:
                print(f"Error reading data: {e}")
                return None
        return hasher.hexdigest()

    def hash_memory(self, data):
        """Public method to compute file hash."""
        start = time.time()
        result = self._hash_file(data)
        elapsed = time.time() - start
        return {"file": "data", "hash": result, "time": elapsed}

    def _hash_file(self, file_path):
        """Compute the hash of a single file."""
        hasher = self._get_hasher()
        try:
            with open(file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped:
                    #hasher.update(mmapped)
                    while chunk := mmapped.read(self.chunk_size):
                        hasher.update(chunk)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
        return hasher.hexdigest()
    
    
    def hash_file(self, file_path):
        """Public method to compute file hash."""
        start = time.time()
        result = self._hash_file(file_path)
        elapsed = time.time() - start
        return {"file": file_path, "hash": result, "time": elapsed}

    def hash_folder(self, folder_path):
        """Compute a single hash for an entire folder (based on file contents and paths)."""
        start = time.time()
        folder_hasher = self._get_hasher()
        lock = threading.Lock()
        threads = []

        def process_file(file_path):
            """Thread-safe file hashing."""
            file_hash = self._hash_file(file_path)
            if file_hash:
                relative_path = os.path.relpath(file_path, folder_path).encode()
                with lock:
                    folder_hasher.update(relative_path)  # Include file path in hash
                    folder_hasher.update(file_hash.encode())

        for root, _, files in os.walk(folder_path):
            for file in sorted(files):  # Sorting ensures consistency
                file_path = os.path.join(root, file)
                thread = threading.Thread(target=process_file, args=(file_path,))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()  # Wait for all threads to finish

        elapsed = time.time() - start
        return {"folder": folder_path, "hash": folder_hasher.hexdigest(), "time": elapsed}
    
#if __name__ == "__main__":
    
    # hasher = FileDig(algo="xxhash")  # Use 'blake3' for BLAKE3
    # print(time.time())
    # # Hash a single file
    # #file_result = hasher.hash_file(r"I:\NF\BUG files\ubuntu-24.04.1-desktop-amd64.iso")
    # #print(file_result)
    # print(time.time())
    # # Hash an entire folder
    # folder_result = hasher.hash_folder(r"I:\NF\BUG files")
    # print(folder_result)
import multiprocessing
import datetime
import os
import hashlib
import time
import stat
import errno
import json
from multiprocessing import Pool, cpu_count, Manager
from functools import partial
from pydispatch import dispatcher

from fClient.fingerprint import get_miltiprocessing_cpu_count

# Define the event signal name
FILE_PROCESSED_EVENT = "file_processed_event"
FILE_COUNT_EVENT = "file_count_event"

class FileSnapshotter2:
    def __init__(self, source_dir, snapshot_file=None):
        self.source_dir = source_dir
        self.snapshot_file = snapshot_file
        self.total_size = 0
        self.manager = Manager()
        self.manager2 = Manager()
        self.processed_count = self.manager.Value('i', 0)  # Shared counter
        self.files_count = self.manager2.Value('ii', 0)  # Shared counter

    def process_file(self, file_path, processed_count):
        """Processes a single file, calculating its hash and metadata."""
        try:
            with open(file_path, "rb") as f_in:
                file_data = f_in.read()
                file_hash = hashlib.sha256(file_data).hexdigest()

            file_stat = os.stat(file_path)
            self.total_size += file_stat.st_size

            # Increment shared counter
            with processed_count.get_lock():
                processed_count.value += 1

            # Dispatch event with updated count
            dispatcher.send(signal=FILE_PROCESSED_EVENT, sender=self, count=processed_count.value)

            return {
                'path': file_path,
                'size': file_stat.st_size,
                'mtime': file_stat.st_mtime,
                'mode': oct(file_stat.st_mode),
                'hash': file_hash
            }

        except (IOError, OSError) as e:
            if e.errno == errno.EACCES:
                print(f"Warning: Cannot access {file_path}: {e}")
            else:
                print(f"Error processing {file_path}: {e}")
            return None  # Indicate error for this file

    def create_snapshot(self):
        """Creates a file snapshot using multiprocessing."""
        try:
            all_files = self.collect_all_files(self.source_dir)
            results = []
            
            # Use Pool with shared counter
            with Pool(processes=get_miltiprocessing_cpu_count()) as pool:
                process_func = partial(self.process_file, processed_count=self.processed_count)
                results = pool.map(process_func, all_files)

            snapshot_data = {
                'timestamp': time.strftime("%Y%m%d_%H%M%S"),
                'total_size': sum(file_info["size"] for file_info in results if file_info),
                'files': [file_info for file_info in results if file_info]
            }
            
            if self.snapshot_file:
                with open(self.snapshot_file, 'w') as f:
                    json.dump(snapshot_data, f, indent=4)
                print(f"Snapshot saved at: {self.snapshot_file}")

            return True, [], snapshot_data

        except Exception as e:
            print(f"Error creating snapshot: {e}")
            return False, [str(e)]

    def collect_all_files(self, source_dir):
        """Recursively collects all files from a directory."""
        all_files = []
        try:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    all_files.append(os.path.join(root, file))
                # Increment shared counter
                with self.manager2.Lock():
                    self.files_count.value += len(files)

                # Dispatch event with updated count
                dispatcher.send(signal=FILE_COUNT_EVENT, sender=self, count=self.files_count.value)

        except PermissionError as e:
            print(f"Access denied: {source_dir} - {e}")
        return all_files


def handle_file_processed(sender, count):
    """Handles file processed event and prints progress."""
    print(f"Files processed so far: {count}")
def handle_file_count(sender, count):
    """Handles file processed event and prints progress."""
    print(f"Files found so far: {count}")

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()

    # Register the event handler
    dispatcher.connect(handle_file_processed, signal=FILE_PROCESSED_EVENT)
    dispatcher.connect(handle_file_count, signal=FILE_COUNT_EVENT)

    # Run the snapshotter
    snapshotter = FileSnapshotter2(source_dir="C:\\Windows", snapshot_file="snapshot.json")
    snapshotter.create_snapshot()


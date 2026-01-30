# import multiprocessing
# import os
# import hashlib
# import time
# import json
# import errno
# from multiprocessing import Pool, cpu_count, Value, get_context
# from pydispatch import dispatcher
# from functools import partial

# from fClient.fingerprint import get_miltiprocessing_cpu_count

# # Define event signal names
# FILE_COUNTED_EVENT = "file_counted_event"
# FILE_PROCESSED_EVENT = "file_processed_event"

# class FileSnapshotter:
#     def __init__(self, source_dir, snapshot_file=None, counted_files=None, processed_files=None):
#         self.source_dir = source_dir
#         self.snapshot_file = snapshot_file
#         self.total_size = 0
#         self.counted_files = counted_files  # Shared counter for counted files
#         self.processed_files = processed_files  # Shared counter for processed files

#     def list_files_in_directory(self, root):
#         """Recursively lists all files in a given directory."""
#         file_list = []
#         try:
#             for dirpath, _, filenames in os.walk(root):
#                 for file in filenames:
#                     file_list.append(os.path.join(dirpath, file))
#         except PermissionError as e:
#             print(f"Access denied: {root} - {e}")
#         return file_list

#     def collect_all_files(self):
#         """Use multiprocessing to count all files and dispatch events."""
#         subdirs = []
#         root_files = []

#         try:
#             # Get top-level directories and root files
#             for root, dirs, files in os.walk(self.source_dir):
#                 subdirs.extend([os.path.join(root, d) for d in dirs])
#                 root_files.extend([os.path.join(root, f) for f in files])
#                 break  # Process only the top level

#         except PermissionError as e:
#             print(f"Access denied: {self.source_dir} - {e}")
#             return []

#         # Use multiprocessing to count files in subdirectories
#         with get_context("fork").Pool(processes=get_miltiprocessing_cpu_count()) as pool:
#             subdir_files = pool.map(self.list_files_in_directory, subdirs)

#         # Combine all file paths
#         all_files = root_files
#         for sublist in subdir_files:
#             all_files.extend(sublist)

#         # Update the counted files counter
#         with self.counted_files.get_lock():
#             self.counted_files.value = len(all_files)
        
#         # Dispatch event with counted files
#         dispatcher.send(signal=FILE_COUNTED_EVENT, sender=self, count=self.counted_files.value)

#         return all_files

#     def process_file(self, file_path):
#         """Processes a single file, calculating its hash and metadata."""
#         try:
#             with open(file_path, "rb") as f_in:
#                 file_data = f_in.read()
#                 file_hash = hashlib.sha256(file_data).hexdigest()

#             file_stat = os.stat(file_path)
#             self.total_size += file_stat.st_size

#             # Increment shared counter safely
#             with self.processed_files.get_lock():
#                 self.processed_files.value += 1
#                 processed_count = self.processed_files.value  # Get the updated value
            
#             # Dispatch event with updated count
#             dispatcher.send(signal=FILE_PROCESSED_EVENT, sender=self, count=processed_count)

#             return {
#                 'path': file_path,
#                 'size': file_stat.st_size,
#                 'mtime': file_stat.st_mtime,
#                 'mode': oct(file_stat.st_mode),
#                 'hash': file_hash
#             }

#         except (IOError, OSError) as e:
#             if e.errno == errno.EACCES:
#                 print(f"Warning: Cannot access {file_path}: {e}")
#             else:
#                 print(f"Error processing {file_path}: {e}")
#             return None  # Indicate error for this file

#     def create_snapshot(self):
#         """Creates a file snapshot using multiprocessing."""
#         try:
#             print("[Snapshotter] Counting all files...")
#             all_files = self.collect_all_files()
#             print(f"[Snapshotter] Total files found: {self.counted_files.value}")

#             results = []
            
#             # Use Pool with shared counter
#             with get_context("fork").Pool(processes=get_miltiprocessing_cpu_count())) as pool:
#                 process_func = partial(self.process_file)
#                 results = pool.map(process_func, all_files)

#             snapshot_data = {
#                 'timestamp': time.strftime("%Y%m%d_%H%M%S"),
#                 'total_size': sum(file_info["size"] for file_info in results if file_info),
#                 'files': [file_info for file_info in results if file_info]
#             }
            
#             if self.snapshot_file:
#                 with open(self.snapshot_file, 'w') as f:
#                     json.dump(snapshot_data, f, indent=4)
#                 print(f"Snapshot saved at: {self.snapshot_file}")

#             return True, [], snapshot_data

#         except Exception as e:
#             print(f"Error creating snapshot: {e}")
#             return False, [str(e)]


# # Event Handlers
# def handle_file_counted(sender, count):
#     """Handles the file counting event and prints progress."""
#     print(f"[Event] Total files counted: {count}")

# def handle_file_processed(sender, count):
#     """Handles the file processed event and prints progress."""
#     print(f"[Event] Files processed so far: {count}")


# if __name__ == '__main__':
#     from multiprocessing import freeze_support
#     freeze_support()

#     # Register event handlers
#     dispatcher.connect(handle_file_counted, signal=FILE_COUNTED_EVENT)
#     dispatcher.connect(handle_file_processed, signal=FILE_PROCESSED_EVENT)

#     # Initialize shared counters using multiprocessing.Value
#     counted_files = Value('i', 0)  # Shared counter for file counting
#     processed_files = Value('i', 0)  # Shared counter for file processing

#     # Run the snapshotter
#     snapshotter = FileSnapshotter(
#         source_dir="C:\\windows", 
#         snapshot_file="snapshot.json", 
#         counted_files=counted_files,
#         processed_files=processed_files
#     )

#     snapshotter.create_snapshot()

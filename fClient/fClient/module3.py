from asyncore import dispatcher
import datetime
import os
import hashlib
import time
import stat
import errno
import json
from multiprocessing import Pool, cpu_count, Manager
from functools import partial
from typing import Any

from pydispatch import dispatcher

from fClient.fingerprint import get_miltiprocessing_cpu_count
FILE_COUNT_EVENT = "file_count_event"


class FileSnapshotter:
    def __init__(self, source_dir, snapshot_file=None,cl=None):
        self.source_dir = source_dir
        self.snapshot_file = snapshot_file
        self.errors = []
        self.total_size =0
        self.total_files =0
        self.cl=cl
        # self.manager2 =Manager()
        # self.file_count =Manager().Value("i",1)
        
    def process_file(self,file_path):
        """Processes a single file, calculating its hash and metadata."""
        try:
            t1=time.time()
            file_hash=""
            try:
                with open(file_path, "rb") as f_in:
                    file_data = f_in.read()
                    file_hash = hashlib.sha256(file_data).hexdigest()
            except Exception as e:
                print(f"++++++++++++++++++++++ Error in file hash {str(e)}")
                pass
            file_stat = os.stat(file_path)
            self.total_size += file_stat.st_size
            # print(f"\t\t{file_path} has {file_stat.st_size} bytes and hash created in {time.time()-t1}" )
            print(f"\t\t{self.total_size} 444444444444444bytes collected")
            
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


    def create_single_file_snapshot_multiprocessing(self,source_dir, snapshot_file):
        """
        Creates a single file snapshot of the source directory using multiprocessing.

        Args:
            source_dir: Path to the source directory.
            snapshot_file: Path to the output snapshot file.

        Returns:
            A tuple containing:
                - True if the snapshot was created successfully, False otherwise.
                - A list of any errors encountered during the snapshot creation.
        """
        try:
            all_files = []
            # for root, _, files in os.walk(source_dir):
            #     for file in files:
            #         all_files.append(os.path.join(root, file))
            t1=time.time()
            all_files= self.collect_all_files(self.source_dir)
            # extensions=[".exe",".ocx",".dll"]
            # print(f"time taken {time.time()-t1} files {len(all_files)}")
            # x= [file_info for file_info in all_files if all_files and file_info.endswith(tuple(extensions))]
            
            results = []
            with Pool(processes=get_miltiprocessing_cpu_count()) as pool:
                results = pool.map(self.process_file, all_files)

            snapshot_data = {
                'timestamp': time.strftime("%Y%m%d_%H%M%S"),
                'total_size': sum(file_info["size"] for file_info in results if file_info),
                'files': [file_info for file_info in results if file_info]
            }
            
            if snapshot_file:
                with open(snapshot_file, 'w') as f:
                    json.dump(snapshot_data, f, indent=4)

                print(f"Snapshot created at: {snapshot_file}")
            return True, [],snapshot_data

        except Exception as e:
            print(f"Error creating snapshot: {e}")
            return False, [str(e)],None

    def list_files_in_directory(self,root_directory,mgr=None,data=None):
        """Traverse the directory using os.walk and return a list of all file paths."""
        all_files = []
        all_dirs=[]
        try:
            for root, _, files in os.walk(root_directory):
                
                self.total_files+=len(files)
                dispatcher.send(signal=FILE_COUNT_EVENT, sender=self, count=self.total_files)
                for file in files:
                    all_files.append(os.path.join(root, file))
                all_dirs.extend([os.path.join(root, d) for d in _])

        except PermissionError as e:
            print(f"Access denied: {root_directory} - {e}")
        except Exception as e:
            print(f"Error accessing {root_directory}: {e}")
        return all_files

    def collect_all_files(self,source_dir):
        """Use multiprocessing to collect all files from a directory."""
        # Get the list of top-level directories and files
        try:
            subdirs = []
            root_files = []
            for root, dirs, files in os.walk(source_dir):
                subdirs.extend([os.path.join(root, d) for d in dirs])
                root_files.extend([os.path.join(root, f) for f in files])
                break  # Only process the top-level directory
        except PermissionError as e:
            print(f"Access denied: {source_dir} - {e}")
            return []
        except Exception as e:
            print(f"Error accessing {source_dir}: {e}")
            return []
        self.total_files+=len(root_files)
        dispatcher.send(signal=FILE_COUNT_EVENT, sender=self, count=self.total_files)
        # Use multiprocessing to process subdirectories
        with Pool(processes=get_miltiprocessing_cpu_count()) as pool:
            subdir_list_files = partial(self.list_files_in_directory)#, mgr="mg",data="data")
            subdir_files = pool.map(self.list_files_in_directory, subdirs)

        # Combine files from root and all subdirectories
        all_files = root_files

        for sublist in subdir_files:
            all_files.extend(sublist)

        return all_files

    # def list_files_in_directory(self,directory):
    #     """List all files in the given directory and its subdirectories."""
    #     all_files = []
    #     try:
    #         for entry in os.scandir(directory):
    #             if entry.is_file():
    #                 all_files.append(entry.path)
    #             elif entry.is_dir():
    #                 # Recursively list files in subdirectories
    #                 all_files.extend(self.list_files_in_directory(entry.path))
    #     except PermissionError as e:
    #         print(f"Access denied: {directory} - {e}")
    #     except Exception as e:
    #         print(f"Error accessing {directory}: {e}")
    #     return all_files

    # def collect_all_files(self,source_dir=None):
    #     """Use multiprocessing to collect all files from a directory."""
    #     # Get top-level directories
    #     if not source_dir:
    #         source_dir=self.source_dir
    #     with os.scandir(source_dir) as entries:
    #         subdirs = [entry.path for entry in entries if entry.is_dir()]
    #         files_in_root = [entry.path for entry in entries if entry.is_file()]

    #     # Use multiprocessing to process subdirectories
    #     with Pool(processes=cpu_count()) as pool:
    #         subdir_files = pool.map(self.list_files_in_directory, subdirs)

    #     # Combine files from root and all subdirectories
    #     all_files = files_in_root
    #     for sublist in subdir_files:
    #         all_files.extend(sublist)

    #     return all_files
def handle_file_count(sender, count):
        """Handles file processed event and prints progress."""
        print(f"Files found so far: {count}")

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    dispatcher.connect(handle_file_count, signal=FILE_COUNT_EVENT)


    import time
    source_dir = "C:\\windows"
    source_dir = "C:\\Program Files (x86)"
    snapshot_file = os.path.expanduser(f"C_Program_Files_(x86)_directory_snapshot{time.time()}.json")
    source_dir = "C:\jjj_546"#"C:\\Program Files (x86)"
    #source_dir = "C:\\Program Files (x86)"
    print(datetime.datetime.fromtimestamp(time.time()))
    fs = FileSnapshotter (source_dir=source_dir,snapshot_file=snapshot_file)
    success, errors,jsdata = fs.create_single_file_snapshot_multiprocessing(source_dir, snapshot_file)
    print(datetime.datetime.fromtimestamp(time.time()))
    if jsdata:
        print(len(jsdata["files"]))

    if success:
        print("Snapshot created successfully.")
    else:
        print("Errors encountered during snapshot creation:")
        for error in errors:
            print(f" - {error}")

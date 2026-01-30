import os
import time
import multiprocessing

from fClient.fingerprint import get_miltiprocessing_cpu_count

class FileScanner:
    def __init__(self, directory, all_types=True, selected_types=None):
        self.directory = directory
        self.all_types = all_types
        self.selected_types = selected_types if selected_types else [".txt"]
        
        self.on_progress = None
        self.on_complete = None

    def process_directory(self, queue, directory):
        """ Worker function to process a directory and send results to the queue """
        ff_files = []
        subdirs = []

        for root, dirs, files in os.walk(directory):
            if self.all_types:
                ff_files.extend(os.path.join(root, f) for f in files)
            else:
                ff_files.extend(os.path.join(root, f) for f in files if any(f.endswith(ext) for ext in self.selected_types))

            subdirs.extend(os.path.join(root, d) for d in dirs)
            break  # Avoid deep recursion

        queue.put((ff_files, subdirs))  # Send results to the queue
        if self.on_progress:
                self.on_progress(len(ff_files))  # Emit progress event

    def scan(self):
        """ Main function to scan files using multiprocessing """
        t1 = time.time()
        stack = [self.directory]
        file_list = []  
        process_count = min(get_miltiprocessing_cpu_count(), len(stack))

        queue = multiprocessing.Queue()
        processes = []

        while stack:
            #process_count = min(multiprocessing.cpu_count(), len(stack))
            while stack and len(processes) < process_count:
                dir_to_scan = stack.pop()
                p = multiprocessing.Process(target=self.process_directory, args=(queue, dir_to_scan))
                p.start()
                processes.append(p)

            for p in processes:
                p.join()  # Wait for all processes to complete

            while not queue.empty():
                ff_files, new_dirs = queue.get()
                file_list.extend(ff_files)
                stack.extend(new_dirs)

                if self.on_progress:
                    self.on_progress(len(file_list))  # Emit progress event

            processes.clear()  # Reset process list
            


        if self.on_complete:
            self.on_complete(file_list)  # Emit completion event

        print(f"Total Files: {len(file_list)}")
        print(f"Time Taken: {time.time() - t1:.2f} seconds")

    def set_progress_callback(self, callback):
        """ Set a callback for progress updates """
        self.on_progress = callback

    def set_complete_callback(self, callback):
        """ Set a callback for when scanning is complete """
        self.on_complete = callback

#####################################################
def progress_update(count):
    print(f"Files processed: {count}")

def scan_complete(files):
    print(f"Scanning complete. Total files found: {len(files)}")

if __name__ == "__main__":
    scanner = FileScanner(r"D:\AutoShop", all_types=True)

    # Set event listeners
    scanner.set_progress_callback(progress_update)
    scanner.set_complete_callback(scan_complete)

    # Start scanning
    scanner.scan()

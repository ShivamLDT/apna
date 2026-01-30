import os
import multiprocessing

class FileCollector:
    def __init__(self, src_folder, all_types, all_selected_types, num_processes=4):
        self.src_folder = src_folder
        self.all_types = all_types
        self.all_selected_types = set(all_selected_types) if not all_types else None
        self.num_processes = num_processes

    def process_files(self, args):
        root, files = args
        if self.all_types:
            return [os.path.join(root, file) for file in files]
        else:
            return [os.path.join(root, file) for file in files if any(file.endswith(ext) for ext in self.all_selected_types)]

    def collect_files(self):
        pool = multiprocessing.Pool(processes=self.num_processes)
        results = []

        for root, _, files in os.walk(self.src_folder):
            results.append(pool.apply_async(self.process_files, ((root, files),)))

        pool.close()
        pool.join()

        collected_files = []
        for result in results:
            collected_files.extend(result.get())

        return collected_files

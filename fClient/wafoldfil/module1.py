from functools import partial
import os
import time
import multiprocessing

from fClient.fingerprint import get_miltiprocessing_cpu_count

# Directory to search
current_dird = r"C:\Program Files (x86)"

# File filters (modify if needed)



def process_directory(directory,all_types,all_selected_types):
    """ Function to process a single directory and return found files """
    ff_files = []
    stack = []
    
    # Convert os.walk() generator to a list before processing
    walk_data = list(os.walk(directory))  

    for root, dirs, files in walk_data:
        if all_types:
            ff_files.extend(os.path.join(root, f) for f in files)
        else:
            ff_files.extend(os.path.join(root, f) for f in files if any(f.endswith(ext) for ext in all_selected_types))
        
        # Collect directories for further processing
        stack.extend(os.path.join(root, d) for d in dirs)
        
        # Break to avoid deep recursion (stack-based processing)
        break

    return ff_files, stack

if __name__ == "__main__":
    all_types = True
    all_selected_types = [".jpg",".zip"]
    multiprocessing.freeze_support()  # ✅ Required for Windows executables

    t1 = time.time()

    # Shared lists (not needed now since we aggregate results)
    stack = [current_dird]
    f_files = []

    # Create a process pool
    with multiprocessing.Pool(processes=get_miltiprocessing_cpu_count()) as pool:
        while stack:
            # Get a batch of directories to process in parallel
            dirs_to_process = [stack.pop() for _ in range(min(len(stack), get_miltiprocessing_cpu_count()))]

            # Run multiprocessing
            results = pool.map(partial( process_directory,all_types=all_types,all_selected_types =all_selected_types) , dirs_to_process)

            # Aggregate results
            for files, new_dirs in results:
                f_files.extend(files)
                stack.extend(new_dirs)
            
            print(f"Total Files: {len(f_files)} Time Taken: {time.time() - t1:.2f} seconds")

    print(f"Total Files: {len(f_files)}")
    print(f"Time Taken: {time.time() - t1:.2f} seconds")

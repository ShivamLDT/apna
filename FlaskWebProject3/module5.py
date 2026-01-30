import os
import time

def get_file_info(dir_entry):
    file_info = {}
    file_stat = dir_entry.stat()
    file_info['fileMode'] = file_stat.st_mode
    file_info['creationTime'] = file_stat.st_ctime
    file_info['lastAccessed'] = time.ctime(file_stat.st_atime)
    file_info['lastModified'] = time.ctime(file_stat.st_mtime)
    file_info['file'] = dir_entry.path
    file_info['size'] = file_stat.st_size
    return file_info

def get_directory_info(start_path):
    total_size = 0
    directory_info = []

    stack = [os.scandir(start_path)]
    while stack:
        entries = stack.pop()
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                try:
                    stack.append(os.scandir(entry.path))
                except:
                    print("")
            else:
                total_size += entry.stat().st_size
                directory_info.append(get_file_info(entry))

    return directory_info, total_size

start_path = "C:\\"
t1 = time.time()
result, total_size = get_directory_info(start_path)
t2 = time.time()
print("Total size of", start_path, ":", total_size)
print(f"time taken {t2-t1}")
print(result)


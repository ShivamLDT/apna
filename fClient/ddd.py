import os

src_folder = "D:\\New folder (2)"

for root, dirs, files in os.walk(src_folder):
    for file in files:
        file_path = os.path.join(root, file)
        #print(f"|--{file_path}")   # This will always be the original path of the file


def print_paths(src_folder):
    for root, dirs, files in os.walk(src_folder):
        # Print the current directory
        #print(f"|+-{root}")
        
        # Print files in the current directory
        for file in files:
            file_path = os.path.join(root, file)
            print(f"|--{file_path}") 
        
        #Print empty subdirectories
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            print(f"|++{subdir_path}")

print_paths(src_folder)
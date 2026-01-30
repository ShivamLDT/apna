import pytsk3
import os

# Path to the disk (replace with your actual disk)
disk_path = "\\\\.\\D:" #linux

# Open the disk image
img = pytsk3.Img_Info(disk_path)

output_dir="D:\\demmmo"

# Open the file system
fs = pytsk3.FS_Info(img)

#scan for deleted files
def recover_file(file, output_dir):
    try:
        file_name = file.info.name.name.decode(errors='replace') if file.info.name.name else "unknown_file"
        file_size = file.info.meta.size
        recovered_path = os.path.join(output_dir, file_name)

        os.makedirs(output_dir, exist_ok=True)

        with open(recovered_path, "wb") as recovered_file:
            offset = 0
            chunk_size = 1024 * 1024  # 1 MB chunks
            while offset < file_size:
                file_data = file.read_random(offset, min(chunk_size, file_size - offset))
                recovered_file.write(file_data)
                offset += chunk_size

        print(f"Recovered file saved to: {recovered_path}")

    except Exception as e:
        print(f"Error recovering file: {e}")

# Function to list and recover deleted files
def list_files(fs, directory="/", output_dir="D:\\demmmo"):
    try:
        dir = fs.open_dir(directory)
        for file in dir:
            filename = "unknown_file"  # Default value for filename
            
            try:
                # Safely decode filename
                raw_name = file.info.name.name
                filename = raw_name.decode(errors='replace') if raw_name else "unknown_file"
                
                # Print raw and decoded filename for debugging
                print(f"Raw filename bytes: {raw_name}")
                print(f"Decoded filename: {filename}")
                print(f"File Meta flags: {file.info.meta and file.info.meta.flags}")

                # Skip . and .. directories
                if filename in [".", ".."]:
                    continue

                # Check if the file is deleted (unallocated)
                if file.info.meta and file.info.meta.flags == pytsk3.TSK_FS_META_FLAG_UNALLOC:
                    print(f"Deleted file detected: {filename}")
                    # Optionally recover the file
                    recover_file(file, output_dir)

                # Recursively search in directories
                if file.info.meta and file.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                    new_directory = os.path.join(directory, filename)
                    list_files(fs, new_directory, output_dir)

            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    except Exception as e:
        print(f"Error accessing directory {directory}: {e}")

# Start listing files from the root directory
list_files(fs, output_dir="D:\\demmmo")
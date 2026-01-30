# import re
# import ctypes

# # Constants for raw disk access
# GENERIC_READ = 0x80000000
# OPEN_EXISTING = 3
# FILE_SHARE_READ = 0x00000001
# FILE_SHARE_WRITE = 0x00000002
# CHUNK_SIZE = 4096*1024*100  # 4 KB for better alignment with clusters

# # PDF signature
# PDF_HEADER = b'%PDF-'
# PDF_FOOTER = b'%%EOF'

# def carve_pdf_from_disk(disk_path):
#     handle = ctypes.windll.kernel32.CreateFileW(
#         disk_path,
#         GENERIC_READ,
#         FILE_SHARE_READ | FILE_SHARE_WRITE,
#         None,
#         OPEN_EXISTING,
#         0,
#         None
#     )

#     if handle == -1:
#         print(f"[ERROR] Failed to open {disk_path}. Run as Administrator.")
#         return
    
#     buffer = b""
#     recovered_count = 0
    
#     try:
#         while True:
#             chunk = ctypes.create_string_buffer(CHUNK_SIZE)
#             bytes_read = ctypes.c_ulong(0)

#             success = ctypes.windll.kernel32.ReadFile(
#                 handle,
#                 chunk,
#                 CHUNK_SIZE,
#                 ctypes.byref(bytes_read),
#                 None
#             )

#             if not success or bytes_read.value == 0:
#                 break
            
#             # Add new chunk to rolling buffer
#             buffer += chunk.raw[:bytes_read.value]

#             # Search for PDF headers and footers
#             start = buffer.find(PDF_HEADER)
#             end = buffer.find(PDF_FOOTER)
#             print(len(buffer))
#             if start != -1 and end != -1 and end > start:
#                 # Found complete PDF
#                 pdf_data = buffer[start:end + len(PDF_FOOTER)]
                
#                 filename = f"recovered_{recovered_count}.pdf"
#                 with open(filename, 'wb') as f:
#                     f.write(pdf_data)
                
#                 print(f"[SUCCESS] Recovered PDF: {filename}")
#                 recovered_count += 1
                
#                 # Remove recovered section from buffer
#                 buffer = buffer[end + len(PDF_FOOTER):]
#             else:
#                 # Keep last 8 KB in the buffer to handle split boundaries
#                 buffer = buffer[-8192:]

#     except Exception as e:
#         print(f"[ERROR] {e}")

#     finally:
#         ctypes.windll.kernel32.CloseHandle(handle)

# # Try PDF recovery from PhysicalDrive0
# carve_pdf_from_disk(r"\\.\PhysicalDrive1")
import pytsk3
import os

# Output directory for recovered files
OUTPUT_DIR = "./recovered_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def recover_deleted_from_ntfs(disk_path, target_path):
    img = pytsk3.Img_Info(disk_path)
    fs = pytsk3.FS_Info(img)

    recovered_count = 0

    def process_directory(directory):
        nonlocal recovered_count
        
        for entry in directory:
            if not hasattr(entry, 'info') or not hasattr(entry.info, 'name'):
                continue

            # Skip active files; only process deleted files
            if entry.info.name.flags != pytsk3.TSK_FS_NAME_FLAG_UNALLOC:
                continue
            
            try:
                # Recover filename
                filename = entry.info.name.name.decode('utf-8', errors='ignore')

                # Open the file if possible
                file_obj = entry.open()
                if file_obj is None:
                    continue
                
                # Read file content
                file_data = file_obj.read_random(0, file_obj.info.meta.size)
                
                # Save file with original name
                recovered_path = os.path.join(OUTPUT_DIR, filename)
                with open(recovered_path, 'wb') as f:
                    f.write(file_data)

                print(f"[SUCCESS] Recovered: {filename} ({len(file_data)} bytes)")
                recovered_count += 1

            except Exception as e:
                print(f"[ERROR] Failed to recover file: {e}")

    try:
        # Open target folder directly
        target_dir = fs.open_dir(path=target_path)
        process_directory(target_dir)
    except Exception as e:
        print(f"[ERROR] Failed to open target folder: {e}")

    print(f"[INFO] Total recovered files: {recovered_count}")

if __name__ == "__main__":
    disk = r"\\.\D:"  # Target drive
    target_folder = r"\Users\user\Downloads\s"  # Target folder in NTFS path format
    print(f"[INFO] Scanning {disk} → {target_folder} for deleted files...")
    recover_deleted_from_ntfs(disk, target_folder)

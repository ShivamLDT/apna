
import zipfile
import os
import subprocess
import sys

def extract_and_run(archive_offset, executable_name, extract_to='.'):
    with open(sys.argv[0], 'rb') as f:
        f.seek(archive_offset)
        archive_data = f.read()
    
    temp_zip_path = os.path.join(extract_to, 'temp_archive.zip')
    with open(temp_zip_path, 'wb') as temp_zip:
        temp_zip.write(archive_data)

    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(temp_zip_path)

    executable_path = os.path.join(extract_to, executable_name)
    if os.path.exists(executable_path):
        print(f"Running {executable_path}...")
        subprocess.run([executable_path])
    else:
        print(f"{executable_name} not found in the extracted files!")

if __name__ == "__main__":
    extract_and_run(archive_offset={archive_offset}, executable_name="ABEndpointSetup.exe")

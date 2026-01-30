import gzip
from pathlib import Path
import shutil
import os
import zlib
import struct

class ZLibFileHandler:
    def __init__(self, zlib_file_path):
        self.zlib_file_path = zlib_file_path
    
    def isValidZlib(self):
        try:
            with open(self.zlib_file_path, 'rb') as f:
                x=f.read()
                x=zlib.decompress(x)
            return True
        except:
            return False

    def decompress_straeam(self, target_file_name, output_directory=None):
        output_file_path = target_file_name
        if output_directory:
            output_file_path = os.path.join(output_directory, target_file_name)

        with open(output_file_path, 'wb') as output_file:
            output_file.write(zlib.decompress(self.zlib_file_path))
            
        print(f"File '{target_file_name}' decompressed to '{output_file_path}'.")

    def decompress_file(self, target_file_name, output_directory):
        # Check if the gzip file exists
        if not os.path.exists(self.zlib_file_path):
            print(f"zlib file '{self.zlib_file_path}' not found.")
            return
        
        if not(self.isValidZlib()):
            gz= GzipFileHandler(self.zlib_file_path)
            gz.decompress_file(target_file_name,output_directory)
            os.replace(target_file_name,self.zlib_file_path)

        # Open the gzip file in binary mode
        with open(self.zlib_file_path, 'rb') as f:
            x=f.read()
            # Decompress the target file to the specified output directory
            output_file_path = os.path.join(output_directory, target_file_name)
            with open(output_file_path, 'wb') as output_file:
                output_file.write(zlib.decompress(x))
            
            print(f"File '{target_file_name}' decompressed to '{output_file_path}'.")

# # Example usage
# gzip_file_handler = GzipFileHandler('example_data.gz')
# output_directory = 'output'
# target_file_name = 'example.txt'

# gzip_file_handler.decompress_file(target_file_name, output_directory)

class GzipFileHandler:
    def __init__(self, gzip_file_path):
        self.gzip_file_path = gzip_file_path

    def decompress_file(self, target_file_name, output_directory):
        # Check if the gzip file exists
        if not os.path.exists(self.gzip_file_path):
            print(f"Gzip file '{self.gzip_file_path}' not found.")
            return
        
        # Open the gzip file in binary mode
        with gzip.open(self.gzip_file_path, 'rb') as f:
            # Check if the target file exists within the gzip file
            if target_file_name not in f.name:
                print(f"File '{target_file_name}' not found within '{self.gzip_file_path}'.")
                return
            
            # Decompress the target file to the specified output directory
            output_file_path = os.path.join(output_directory, target_file_name)
            with open(output_file_path, 'wb') as output_file:
                shutil.copyfileobj(f, output_file)
            
            print(f"File '{target_file_name}' decompressed to '{output_file_path}'.")

# # Example usage
# gzip_file_handler = GzipFileHandler('example_data.gz')
# output_directory = 'output'
# target_file_name = 'example.txt'

# gzip_file_handler.decompress_file(target_file_name, output_directory)



from ast import With
import chunk
import mmap
from multiprocessing import shared_memory
import os
from queue import Queue
import stat
from time import time
import py7zr
import io
import shutil
import tempfile
from fClient.shad import OpenShFile

class p7zstd:
    def __init__(self, password: str, compression_method="ZSTD", preset: int = 3,chunk_size=None):
        """
        Initialize SecureCompressor with AES-256 encryption and compression settings.
        
        :param password: Password for AES-256 encryption
        :param compression_method: Compression algorithm ("LZMA2" or "ZSTD")
        :param preset: Compression level (0=Fastest, 3=Balanced, 9=Max compression)
        """
        iv = "00000000000000000000000000000000" #bytes.fromhex("00000000000000000000000000000000")
        if password is None: password="00000000000000000000000000000000"
        if isinstance(password,(bytes)):
             password =password.decode()
        self.password = password 
        self.compression_method = compression_method
        self.preset = preset
    
    @staticmethod
    def get_optimal_chunk_size(file_size, base_chunk_size=1 * 1024 * 1024):
        """
        Adjust chunk_size to ensure file_size % chunk_size == 0.
    
        :param file_size: Total size of the file in bytes.
        :param base_chunk_size: Starting chunk size (default 128MB).
        :return: Optimized chunk size.
        """
        if base_chunk_size < 50 * 1024 * 1024:  # Stop at 1MB minimum
            return base_chunk_size

        while file_size % base_chunk_size != 0:
            base_chunk_size //= 2  # Reduce chunk size to find an exact divisor
            if base_chunk_size < 1 * 1024 * 1024:  # Stop at 1MB minimum
                base_chunk_size = 1 * 1024 * 1024
                break
        return base_chunk_size


    def _get_filter(self):
        """Returns the appropriate filter for the chosen compression method."""
        if self.compression_method.upper() == "LZMA2":
            return [{"id": py7zr.FILTER_LZMA2, "preset": self.preset}]
        elif self.compression_method.upper() == "ZSTD":
            # return [{"id": py7zr.FILTER_ZSTD, "level": self.preset}]
            return [
                {"id": py7zr.FILTER_ZSTD},  # Apply Zstandard compression
                {"id": py7zr.FILTER_CRYPTO_AES256_SHA256, "password": self.password}  # Apply AES-256 encryption
            ]
        else:
            raise ValueError("Unsupported compression method. Use 'LZMA2' or 'ZSTD'.")

    def compress(self, data: bytes,file_name:str,chunk_size:int) -> bytes:
        """
        Compress and encrypt data using py7zr.
        
        :param data: Raw bytes to compress and encrypt
        :return: Compressed and encrypted bytes
        """
        compressed_stream = io.BytesIO()
        filters = self._get_filter()
        file_name=file_name.split("\\")[:-1]

        with py7zr.SevenZipFile(compressed_stream, 'w', password=self.password, filters=filters) as archive:
            archive.writestr(data=data,arcname="file_name")  
            
        ret = compressed_stream.getvalue()
        del compressed_stream
        return ret

    def compress_chunk_shared(self,shm_name,  chunk_size, num_chunks,output_path=None):
        """
        Compress a chunk of data from shared memory.
        """
        start=0
        try:
            # Attach to the existing shared memory
            shm = shared_memory.SharedMemory(name=shm_name)
            compressed_stream = io.BytesIO()
            with py7zr.SevenZipFile(compressed_stream, 'w', password=self.password, filters=self._get_filter()) as archive:
                for i in range(num_chunks):
                    start = i * chunk_size
                    chunk_data = bytes(shm.buf[start: start + chunk_size])  # Read from shared memory
                    archive.writestr(data=chunk_data, arcname=f"chunk_{i}.abz")
                # archive._write_flush()
                # archive._fpclose()
            archive.close()
            if output_path:
                with open(output_path, "ab") as f_out:
                    f_out.write(compressed_stream.getvalue())
            
        finally:
            shm.close()  
        
            return compressed_stream.getvalue()

    
    def compress_and_stream_chunks(self, shm_name, chunk_size, num_chunks):
        """
        Generator that yields (chunk_index, compressed_stream) for each chunk.
        """
        shm = shared_memory.SharedMemory(name=shm_name)
        try:
            for i in range(num_chunks):
                start = i * chunk_size
                end = start + chunk_size
                chunk_data = bytes(shm.buf[start:end])

                compressed_stream = io.BytesIO()
                with py7zr.SevenZipFile(compressed_stream, 'w', password=self.password, filters=self._get_filter()) as archive:
                    archive.writestr(data=chunk_data, arcname=f"chunk_{i}.bin")

                compressed_stream.seek(0)
                yield i, compressed_stream
        finally:
            shm.close()


    def compress_mmap(self, mm_in: mmap.mmap,file_name:str,chunk_size:int) -> bytes:
        """
        Compress and encrypt data using py7zr.
        
        :param data: Raw bytes to compress and encrypt
        :return: Compressed and encrypted bytes
        """
        compressed_stream = io.BytesIO()
        filters = self._get_filter()
        file_name=file_name.split("\\")[:-1]

        file_size = os.path.getsize(file_name)

        queue = Queue()
        processes = []

         # Process file in chunks
        for i in range(0, file_size, chunk_size):
            chunk = mm_in[i: i + chunk_size]

            # Start a separate process for compression
            p = os.Process(target=self.compress, args=(chunk, queue, f"chunk_{i}.7z", filters, password))
            p.start()
            processes.append(p)

        # Collect compressed results and write to file
        for p in processes:
            compressed_chunk = queue.get()
            f_out.write(compressed_chunk)
            p.join()

        with py7zr.SevenZipFile(compressed_stream, 'w', password=self.password, filters=filters) as archive:
            archive.writestr(data=data,arcname="file_name")  
            
        ret = compressed_stream.getvalue()
        del compressed_stream
        return ret

    def decompress(self, encrypted_data: bytes,file_name:str="NonFile",b_write_file=False) -> bytes:
        """
        Decrypt and decompress data using py7zr.
        
        :param encrypted_data: Encrypted and compressed bytes
        :return: Original decompressed bytes
        """
        if isinstance(encrypted_data, bytes):
            encrypted_data = io.BytesIO(encrypted_data)        

        #file_name=file_name.split("\\")[:-1]
        #file_name=file_name[-1]
        try:
            with py7zr.SevenZipFile(encrypted_data, 'r', password=self.password,filters=self._get_filter()) as archive:
                print("Archive files:", archive.getnames())
                print("Get filter",self._get_filter())
                extracted = None
                names = archive.getnames() or []
                if hasattr(archive, "readall"):
                    extracted = archive.readall()
                elif hasattr(archive, "read"):
                    extracted = archive.read(names) if names else {}
                else:
                    extracted = {}
                    temp_dir = tempfile.mkdtemp(prefix="apna_restore_")
                    try:
                        archive.extractall(path=temp_dir)
                        if names:
                            for name in names:
                                path = os.path.normpath(os.path.join(temp_dir, name))
                                if os.path.isfile(path):
                                    with open(path, "rb") as chunk_file:
                                        extracted[name] = io.BytesIO(chunk_file.read())
                        else:
                            for root, _, files in os.walk(temp_dir):
                                for file in files:
                                    path = os.path.join(root, file)
                                    rel_path = os.path.relpath(path, temp_dir)
                                    with open(path, "rb") as chunk_file:
                                        extracted[rel_path] = io.BytesIO(chunk_file.read())
                    finally:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                print("Files extracted:", list(extracted.keys()) if hasattr(extracted, "keys") else [])
                data=io.BytesIO()
                if extracted:
                    for edata in extracted:# archive.readall().items: #extracted:
                        data.write(extracted[edata].getvalue())
                    if not file_name =="NonFile" and b_write_file:
                        with open(file_name, "wb") as chunk_file:
                            chunk_file.write(data.getvalue())
                            chunk_file.flush()
                    return data.getvalue()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Error reading archive:", e)
        #return extracted["data.bin"]
        #return extracted["file_name"]
        #return extracted["file_name"].getvalue()

    def is_aes256_encrypted(self,compressed_bytes):
        """Verify if the 7z archive is encrypted with AES-256."""
        try:
            input_stream = io.BytesIO(compressed_bytes)
            with py7zr.SevenZipFile(input_stream, mode='r') as archive:
                metadata = archive.archive_metadata()  # Get archive metadata
                encrypted_files = any(f.encrypted for f in archive.list())  # Check if files inside are encrypted
            
                return metadata.get("encrypted", False) and encrypted_files  # Both conditions must be met
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

if __name__ == "__main__":
    password = "SuperSecure123"
    compressor = p7zstd(password=None,compression_method="ZSTD", preset=9)  # Use LZMA2 (default)
    


    data = b"Highly confidential data!" * 1000  # Example Data
    t = time()
    encrypted_compressed_data=b''
    #with open( r"I:\support@3handshake.com.pst",'rb') as m_file:
    #with open( r"I:\support@3handshake.com.pst",'rb') as m_file:
    #with OpenShFile(r"I:\NF\BUG files\ubuntu-24.04.1-desktop-amd64.iso", "rb") as m_file:
    with OpenShFile(r"I:\NF\BUG files\kushalbairwa1989@gmail.com.pst", "rb") as m_file:
        with mmap.mmap(m_file.fileno(), 0, access=mmap.ACCESS_READ) as encrypted_file:
            data = encrypted_file.read()
            encrypted_compressed_data = compressor.compress(data=data,file_name="file_name")
    print (time()-t)
    t = time()
    #compressor = p7zstd(password="password", preset=1)  # Use LZMA2 (default)
    decrypted_decompressed_data = compressor.uncompress(encrypted_compressed_data,file_name="file_name")
    print (time()-t)

    # Verification
    assert  decrypted_decompressed_data.getvalue() == data, "Decompression failed!"
    print(compressor.is_aes256_encrypted(encrypted_compressed_data))
    print(f"Original Size: {len(data)/1024**2} Mbytes")
    print(f"Compressed & Encrypted Size: {len(encrypted_compressed_data)/1024**2} Mbytes")

# import py7zr
# import os


# class SecureSevenZipHandler:
#     def __init__(self, password, chunk_size=512 * 1024 * 1024):
#         """
#         Initialize the handler with encryption.

#         :param password: Encryption password
#         :param chunk_size: Chunk size in bytes (default: 512MB)
#         """
#         self.password = password
#         self.chunk_size = chunk_size  # Default 512MB chunks

#     def compress(self, input_file, output_archive):
#         """
#         Compress and encrypt a large file in chunks.
        
#         :param input_file: Path to the input file
#         :param output_archive: Path to the output .7z archive
#         """
#         filters = [{'id': py7zr.FILTER_ZSTD}, {'id': py7zr.FILTER_CRYPTO_AES256_SHA256}]
#         t= time()
#         x=1
#         with py7zr.SevenZipFile(output_archive, 'w', password=self.password, filters=filters) as archive:
#             with open(input_file, 'rb') as f:
#                 print( f"file opend in {time()-t} seconds")
#                 while chunk := f.read(self.chunk_size):  # Read in chunks
#                     temp_chunk_name = input_file + ".chunk"  # Temporary file
#                     with open(temp_chunk_name, 'wb') as temp_chunk:
#                         temp_chunk.write(chunk)
#                         print( f"chunk {x} written in {time()-t} seconds")
                    
#                     archive.write(temp_chunk_name, os.path.basename(temp_chunk_name))  # Add to archive
#                     os.remove(temp_chunk_name)  # Clean up chunk file
       
#         print(f"Compression & encryption completed: {output_archive} in {time()-t} seconds")

#     def decompress(self, input_archive, output_folder):
#         """
#         Decrypt and decompress a large .7z archive in chunks.

#         :param input_archive: Path to the input .7z archive
#         :param output_folder: Path where the extracted file should be stored
#         """
#         try:
#             with py7zr.SevenZipFile(input_archive, 'r', password=self.password) as archive:
#                 archive.extractall(path=output_folder)
#             print(f"Decompression & decryption completed: {output_folder}")
#         except py7zr.Bad7zFile:
#             print(" Error: Incorrect password or corrupted file!")

            
# # Example Usage
# password = "strongpassword"
# handler = SecureSevenZipHandler(password=password, chunk_size=512 * 1024 * 1024)  # 512MB chunks


# # Compression
# handler.compress( r"I:\support@3handshake.com.pst", r"I:\support@3handshake.com.pst.7z")
# # handler.compress( r"I:\DropBox_Package.rars", r"I:\DropBox_Package65432.rar.7z")

# # Decompression
# handler.decompress( r"I:\support@3handshake.com.pst.7z", r"I:\NewFolder\support@3handshake.com.pstrestored_large_file.bin")
# #handler.decompress( r"I:\DropBox_Package65432.rar.7z", r"I:\NewFolder\DropBox_Package.rar.7z.data")

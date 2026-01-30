
from bz2 import compress
import chunk
from gzip import GzipFile
import gzip
import io
import mmap
from time import time
import py7zr
import py7zr.compressor
import py7zr.compressor
import py7zr.exceptions
import os
import threading  # For potential future multi-threading
from concurrent.futures import ThreadPoolExecutor

from fClient.shad import OpenShFile  # For potential future concurrency

class YourClassOptimized:
    def __init__(self, password, compression_filters=None, compression_level=6):
        self.password = password
        # Default to LZMA2 with a reasonable compression level
        self.compression_filters = compression_filters if compression_filters else [{'id': py7zr.FILTER_ZSTD, 'level': compression_level}] #,{"id": py7zr.FILTER_CRYPTO_AES256_SHA256, "password": self.password}]
        self.decompression_lock = threading.Lock() # To potentially handle concurrent decompression safely

    def _get_filter(self):
        return self.compression_filters

    #65536

    def compress_streamed_new(self, data: io.BytesIO, file_name: str, chunk_size: int = 65536):
        
        try:
            i=1
            filters = self._get_filter()
            archive_name = os.path.basename(file_name)  # Use base name for archive entry

            # compressor =py7zr.compressor.SevenZipCompressor(filters=self. _get_filter(),password= self.password)            
            # while True:
            #     chunk = data.read(chunk_size)
            #     if not chunk:
            #         break
            #     indata = io.BytesIO(chunk)
            #     outdata = io.BytesIO()
            #     insize, outsize, crc = compressor.compress(indata, outdata)

            #     outsize += compressor.flush(outdata)

            #     yield outdata.getvalue()
            #     del outdata
            #     del indata
            #     del chunk
            #     i+=1
            # Dynamically decide properties
            properties = {
                "key_size": 256,  # Use AES-256 encryption
                "iv": os.urandom(16),  # Generate a random 16-byte IV
                "cipher_mode": "CBC",  # Use Cipher Block Chaining mode
                "salt": os.urandom(16),  # Generate a random 16-byte salt for key derivation
            }

            # Initialize AESCompressor with the dynamically generated properties
            compressor = py7zr.compressor.AESCompressor(password=password,_iv=bytes.fromhex("00000000000000000000000000000000"))
            properties= compressor.encode_filter_properties()
            print(properties)
            #compressor =py7zr.compressor.AESCompressor(password= self.password)
            while True:
                chunk = data.read(chunk_size)
                if not chunk:
                    break
                # indata = io.BytesIO(chunk)
                # outdata = io.BytesIO()
                outdata = compressor.compress(chunk)
                outdata += compressor.flush()

                yield outdata
                del outdata
                #del indata
                del chunk
                i+=1
            
        except Exception as e:
            raise Exception(f"Compression error: {e}")

    def decompress_streamed(self, data: io.BytesIO, file_name: str, chunk_size: int = 65536):
        """
        Compresses data incrementally and streams compressed chunks.

        :param data: Input file or data (as a file-like object) to compress.
        :param file_name: Name of the file to be compressed (for archive entry).
        :param chunk_size: Size of chunks (in bytes) to process at a time.
        :yield: Compressed chunks of data as bytes.
        """
        import sys
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        try:
            chunk_size
            i=1
            filters = self._get_filter()
            archive_name = os.path.basename(file_name)  # Use base name for archive entry

            with py7zr.SevenZipFile(data, filters=self._get_filter(), mode="r", password=password) as archive:
                archive.extractall(path=r"I:\NF\BUG files\asdf")
            coders=[]
            
            for filter in self._get_filter():
                 coders.insert(0, py7zr.compressor.SupportedMethods.get_coder(filter))
            decompressor =py7zr.compressor.SevenZipDecompressor(coders, password= self.password)
            while True:
                
                chunk = data.read(chunk_size)
                if not chunk:
                    break
                
                #compressed_stream.seek(0)
                indata = io.BytesIO(chunk)
                outdata= decompressor.decompress(indata)

                yield outdata.getvalue()
                del outdata
                del indata
                del chunk
                i+=1
            
        except Exception as e:
            raise Exception(f"Compression error: {e}")

    def compress_streamed(self, data: io.BytesIO, file_name: str, chunk_size: int = 65536):
        """
        Compresses data incrementally and streams compressed chunks.

        :param data: Input file or data (as a file-like object) to compress.
        :param file_name: Name of the file to be compressed (for archive entry).
        :param chunk_size: Size of chunks (in bytes) to process at a time.
        :yield: Compressed chunks of data as bytes.
        """
        try:
            i=1
            compressed_stream = io.BytesIO()
            filters = self._get_filter()
            archive_name = os.path.basename(file_name)  # Use base name for archive entry
           
            with py7zr.SevenZipFile(compressed_stream, 'w', password=self.password, filters=filters) as archive:
                if isinstance(data, bytes):
                    archive.writestr(data=data, arcname=archive_name)
                elif hasattr(data, 'read'):
                    # Use archive.write() for file-like objects, reading in chunks
                    #with archive.open(archive_name, 'w') as entry:
                    #with io.BytesIO() as temp_stream:
                    while True:
                        chunk = data.read(chunk_size)
                        if not chunk:
                            break
                        archive.writestr(chunk,archive_name+"_"+str(i))
                        archive._write_flush()
                        #archive._fpclose()
                        #archive._var_release()
                        #compressed_stream.seek(0)
                        yield compressed_stream.getvalue()
                        del chunk
                        compressed_stream.truncate(0)
                        i+=1
                else:
                    raise TypeError("data must be bytes or a file-like object")
            
            return compressed_stream.getvalue()
        except Exception as e:
            raise Exception(f"Compression error: {e}")

    def compress(self, data: bytes, file_name: str, chunk_size: int = 65536*1024) -> bytes: #
        """
        Compresses and encrypts data using py7zr.  Handles both bytes and file-like objects.

        :param data: Raw bytes or a file-like object to compress.
        :param file_name: The name to use for the entry within the archive.
        :param chunk_size: Chunk size for reading from file-like objects.
        :return: Compressed and encrypted bytes.
        """
        i=1
        compressed_stream = io.BytesIO()
        filters = self._get_filter()
        archive_name = os.path.basename(file_name)  # Use base name for archive entry

        try:
            with py7zr.SevenZipFile(compressed_stream, 'w', password=self.password, filters=filters) as archive:
                if isinstance(data, bytes):
                    archive.writestr(data=data, arcname=archive_name)
                elif hasattr(data, 'read'):
                    # Use archive.write() for file-like objects, reading in chunks
                    #with archive.open(archive_name, 'w') as entry:
                    #with io.BytesIO() as temp_stream:
                    while True:
                        chunk = data.read(chunk_size)
                        if not chunk:
                            break
                        #temp_stream.write(chunk)
                        #archive.writestr(temp_stream.getvalue(),str(i))
                        archive.writestr(chunk,archive_name+"_"+str(i))
                        del chunk
                        i+=1
                else:
                    raise TypeError("data must be bytes or a file-like object")
            return compressed_stream.getvalue()
        except Exception as e:
            raise Exception(f"Compression error: {e}")

    def decompress_streamed_old2(self, encrypted_data: bytes, chunk_size: int = 65536):
        """
        Decompresses large files using zstd and AES256 and streams chunks without storing the entire output.

        :param encrypted_data: Encrypted and compressed bytes.
        :param chunk_size: Size of chunks (in bytes) to process at a time.
        :yield: Decompressed chunks as bytes.
        """
        if isinstance(encrypted_data, bytes):
             encrypted_stream = io.BytesIO(encrypted_data)
        else:
            encrypted_stream = encrypted_data
        try:
            filters = self._get_filter()
            archive_name = os.path.basename(file_name)  # Use base name for archive entry
            decompressor=py7zr.compressor.SevenZipDecompressor(filters=self. _get_filter(),password= self.password)
            
            revert_data = decompressor.decompress(chunk)
            yield revert_data
            del revert_data
            raise ValueError("Incorrect password provided for the 7z archive.")
        except Exception as e:
            raise Exception(f"Decompression error: {e}")

    def decompress(self, encrypted_data: bytes, file_name: str) -> bytes:
        """
        Decrypt and decompress data using py7zr.

        :param encrypted_data: Encrypted and compressed bytes
        :param file_name: The name of the file expected within the archive
        :return: Original decompressed bytes
        """
        encrypted_stream = io.BytesIO(encrypted_data)
        expected_name = os.path.basename(file_name)
        try:
            with py7zr.SevenZipFile(encrypted_stream, 'r', password=self.password) as archive:
                extracted = archive.readall()  # Read all files
                
                data=io.BytesIO()
                if extracted:
                    for edata in extracted:# archive.readall().items: #extracted:
                        data.write(extracted[edata].getvalue())
                        print(len(data.getvalue()))
                    return data.getvalue()
                # if expected_name in extracted:
                #     return extracted[expected_name].getvalue()
                else:
                    raise ValueError(f"File '{expected_name}' not found in the archive.")
        except py7zr.exceptions.PasswordRequired:
            raise ValueError("Incorrect password for the 7z archive.")
        except py7zr.exceptions.Bad7zFile as sef :
            raise ValueError("The provided data is not a valid 7z archive.")
        except Exception as e:
            raise Exception(f"Decompression error: {e}")

    def decompreaaaaaass(self, encrypted_data: bytes, file_name: str) -> bytes:
        """
        Decrypt and decompress data using py7zr.

        :param encrypted_data: Encrypted and compressed bytes
        :param file_name: The name of the file expected within the archive
        :return: Original decompressed bytes
        """
        encrypted_stream = io.BytesIO(encrypted_data)
        expected_name = os.path.basename(file_name)
        try:
            with py7zr.SevenZipFile(encrypted_stream, 'r', password=self.password) as archive:
                if expected_name in archive.getnames():
                    with archive.open(expected_name, 'r') as entry:
                        return entry.read()
                else:
                    raise ValueError(f"File '{expected_name}' not found in the archive.")
        except py7zr.exceptions.PasswordRequired:
            raise ValueError("Incorrect password for the 7z archive.")
        except py7zr.exceptions.Bad7zFile:
            raise ValueError("The provided data is not a valid 7z archive.")
        except Exception as e:
            raise Exception(f"Decompression error: {e}")

    # Example of concurrent decompression (if you need to decompress multiple archives)
    def decompress_concurrent(self, encrypted_data_list: list, file_name_list: list, max_workers=4):
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.decompress, data, name) for data, name in zip(encrypted_data_list, file_name_list)]
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append(e)  # Or handle errors as needed
        return results

# Example Usage:
if __name__ == "__main__":
    password = "mysecretpassword"
    compressor = YourClassOptimized(password=password, compression_level=1) # Experiment with compression_level
    file_name=r"I:\azure-blob-storage-utility-documentation.docx"
    file_name=r"I:\support@3handshake.com.pst"
    file_name=r"I:\NF\BUG files\ubuntu-24.04.1-desktop-amd64.iso"
    file_name=r"I:\NF\BUG files\4_5825835975510596804.mkv"
    file_name=r"I:\NF\BUG files\Class_12th_Math_Exercise_7.5_in_hindi.ttml"
    file_name=r"I:\NF\BUG files\4k_Thetestdata.mp4"
    print("Compression")
    original_data = b"This is a large amount of data to compress and encrypt. " * 10000
    file_to_compress = "my_large_file.txt"
    t=time()
    # compressed_data = None

    with OpenShFile(file_name, "rb") as m_file:
            with mmap.mmap(m_file.fileno(), 0, access=mmap.ACCESS_READ) as f:                
                #compressed_data = compressor.compress(f, file_to_compress)
                with open(file_name+".7zs", "wb") as f_file:
                    for compressed_chunk in compressor.compress_streamed(f, file_name, chunk_size=1024*65536):
                        # Process compressed chunks (e.g., save to file or send over a network)
                        # if not compressed_data:
                        #     compressed_data = compressed_chunk
                        # else:
                        #     compressed_data =compressed_data +compressed_chunk
                        f_file.write(compressed_chunk)
                        #f_file.write(b'------EOC--------')
                        #f_file.flush()
                        print(f"Compressed chunk size: {len(compressed_chunk)} bytes")
    #print(f"Compressed data size: {len(compressed_data)}")
    print(str(time()-t))
    print("Decompression")
     
    t=time()
    decompressor = YourClassOptimized(password=password)
    with open(file_name+".7zs", "rb") as m_file: 
        for d_data in decompressor.decompress_streamed(m_file, file_to_compress):            
            for decompressed_data in decompressor.decompress_streamed(d_data, file_to_compress):
                with open(file_name + ".data", "wb") as f_data:        
                    f_data.write(decompressed_data)

    # with open(file_name+".7zs", "rb") as m_file: 
    #     m_file.seek(0)
    #     #decompressor = py7zr.compressor.AESDecompressor(aes_properties = b'S\x07|&\xae\x94do\x8a4', password=password)
    #     decompressor = py7zr.compressor.AESDecompressor(aes_properties = b'S\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', password=password)
    #     x = decompressor.decompress(m_file.read())

    #     with open(file_name+".7zs.txt", "wb") as d_file: 
    #         d_file.write(x)
    #         d_file.flush()
     

    print(str(time()-t))
    # with OpenShFile(file_name, "rb") as m_file:
    #         with mmap.mmap(m_file.fileno(), 0, access=mmap.ACCESS_COPY) as f:
    #             compressed_data=f.read()
    # # #print(f"Decompressed data matches original: {decompressed_data == compressed_data}")

    # # # Example Compression from a file-like object
    # # with io.BytesIO(original_data) as file_like:
    # #     compressed_from_stream = compressor.compress(file_like, "my_large_file_from_stream.txt")
    # #     print(f"Compressed from stream size: {len(compressed_from_stream)}")

    # # # Example Decompression (assuming the compressed data from stream)
    # # decompressed_from_stream = decompressor.decompress(compressed_from_stream, "my_large_file_from_stream.txt")
    # # print(f"Decompressed from stream matches original: {decompressed_from_stream == original_data}")

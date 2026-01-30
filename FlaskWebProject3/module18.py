import os
import json
import hashlib
import logging
import zlib
import uuid
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from smb.SMBConnection import SMBConnection
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Constants
CHUNK_SIZE = 64* 1024  # 64KB
MASTER_METADATA_FILE = 'master_metadata.json'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread lock for thread safety
lock = threading.Lock()

# Ensure master metadata file exists
if not os.path.exists(MASTER_METADATA_FILE):
    with open(MASTER_METADATA_FILE, 'w') as f:
        json.dump({}, f)

class EncryptedFileSystem:
    def __init__(self, server_name_address, server_user_name, server_password, share_location):
        self.server_conn = SMBConnection(server_user_name, server_password, "", server_name_address, use_ntlm_v2=True,is_direct_tcp=True)
        if not self.server_conn.connect(server_name_address, 445):
            logger.error("Failed to connect to server.")
            raise ConnectionError("Failed to connect to server.")
        self.share_location = share_location
    
    def compress_data(self, data):
        return zlib.compress(data)
    
    def decompress_data(self, data):
        return zlib.decompress(data)
    
    def encrypt_and_chunk_file(self, file_path, key, guid):
        chunks = []
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        padder = padding.PKCS7(128).padder()
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                compressed_data = self.compress_data(file_data)
                chunk_num = 0
                for i in range(0, len(compressed_data), CHUNK_SIZE):
                    chunk = compressed_data[i:i + CHUNK_SIZE]
                    padded_data = padder.update(chunk)
                    encryptor = cipher.encryptor()
                    encrypted_chunk = encryptor.update(padded_data) + encryptor.finalize()
                    chunk_folder = os.path.join(guid, f"abb{chunk_num}")
                    os.makedirs(chunk_folder, exist_ok=True)
                    chunk_path = os.path.join(chunk_folder, f"{os.path.basename(file_path)}.abb{chunk_num}")
                    with open(chunk_path, 'wb') as chunk_file:
                        chunk_file.write(encrypted_chunk)
                    chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()
                    chunks.append({"path": chunk_path, "hash": chunk_hash})
                    chunk_num += 1
                
                # Finalize padding
                final_padded_data = padder.finalize()
                if final_padded_data:
                    encryptor = cipher.encryptor()
                    encrypted_chunk = encryptor.update(final_padded_data) + encryptor.finalize()
                    chunk_folder = os.path.join(guid, f"abb{chunk_num}")
                    os.makedirs(chunk_folder, exist_ok=True)
                    chunk_path = os.path.join(chunk_folder, f"{os.path.basename(file_path)}.abb{chunk_num}")
                    with open(chunk_path, 'wb') as chunk_file:
                        chunk_file.write(encrypted_chunk)
                    chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()
                    chunks.append({"path": chunk_path, "hash": chunk_hash})
        
        except Exception as e:
            logger.error(f"Error encrypting and chunking file: {e}")
            self.cleanup_files([chunk["path"] for chunk in chunks])
            raise e
        
        return chunks, iv

    def save_file(self, file_path, key):
        guid = str(uuid.uuid4())
        chunks, iv = self.encrypt_and_chunk_file(file_path, key, guid)
        metadata = {
            "original_path": file_path,
            "chunks": chunks,
            "iv": iv.hex(),
            "guid": guid
        }
        
        metadata_path = os.path.join(guid, f"{os.path.basename(file_path)}.metadata")
        
        try:
            os.makedirs(guid, exist_ok=True)
            with open(metadata_path, 'w') as metadata_file:
                json.dump(metadata, metadata_file)
            
            for chunk in chunks:
                self.upload_to_server(chunk["path"])
            
            self.update_master_metadata(file_path, metadata)
            self.cleanup_local_files(guid)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            self.cleanup_files([chunk["path"] for chunk in chunks] + [metadata_path])
            raise e

    def update_master_metadata(self, file_path, metadata):
        with lock:
            try:
                with open(MASTER_METADATA_FILE, 'r') as f:
                    master_metadata = json.load(f)
                
                master_metadata[file_path] = metadata
                
                with open(MASTER_METADATA_FILE, 'w') as f:
                    json.dump(master_metadata, f)
                
                logger.info(f"Master metadata updated for {file_path}.")
            except Exception as e:
                logger.error(f"Error updating master metadata: {e}")
                raise e

    def get_metadata_from_master(self, file_path):
        with lock:
            try:
                with open(MASTER_METADATA_FILE, 'r') as f:
                    master_metadata = json.load(f)
                
                metadata = master_metadata.get(file_path)
                
                if not metadata:
                    raise FileNotFoundError(f"Metadata for {file_path} not found in master metadata.")
                
                return metadata
            except Exception as e:
                logger.error(f"Error retrieving metadata from master: {e}")
                raise e
    
    def upload_to_server(self, file_path):
        try:
            with open(file_path, 'rb') as file_obj:
                with lock:
                    self.create_folder_tree(self.server_conn,os.path.dirname(file_path))
                    self.create_folder_tree(self.server_conn,file_path)
                    self.server_conn.storeFile(self.share_location, file_path, file_obj)
                    #self.server_conn.storeFile(self.share_location, os.path.basename(file_path), file_obj)
                    # self.server_conn.storeFile(os.path.join(self.share_location,os.path.basename(file_path)), os.path.basename(file_path), file_obj)
            logger.info(f"Uploaded {file_path} to share.")
        except Exception as e:
            logger.error(f"Error uploading file to server: {e}")
            raise e
    
    def download_from_server(self, file_name, dest_path):
        try:
            with open(dest_path, 'wb') as file_obj:
                with lock:
                    self.server_conn.retrieveFile(self.share_location, file_name, file_obj)
            logger.info(f"Downloaded {file_name} from share.")
        except Exception as e:
            logger.error(f"Error downloading file from server: {e}")
            raise e

    def decrypt_and_reassemble_file(self, file_path, key):
        metadata = self.get_metadata_from_master(file_path)
        
        iv = bytes.fromhex(metadata['iv'])
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        unpadder = padding.PKCS7(128).unpadder()
        
        original_file_path = metadata['original_path']
        guid_folder = metadata['guid']
        
        try:
            os.makedirs(guid_folder, exist_ok=True)
            with open(original_file_path, 'wb') as original_file:
                decrypted_data = b""
                for chunk_info in metadata['chunks']:
                    chunk_path = chunk_info["path"]
                    os.makedirs(os.path.dirname( chunk_path), exist_ok=True)
                    expected_hash = chunk_info["hash"]
                    self.download_from_server(chunk_path, chunk_path)
                    #self.download_from_server(chunk_path, os.path.basename(chunk_path))
                    with open(chunk_path, 'rb') as chunk_file:
                        encrypted_chunk = chunk_file.read()
                        chunk_hash = hashlib.sha256(encrypted_chunk).hexdigest()
                        
                        if chunk_hash != expected_hash:
                            logger.error(f"Tampering detected in chunk: {chunk_path}")
                            raise ValueError("Tampering detected in chunk")
                        
                        decryptor = cipher.decryptor()
                        padded_data = decryptor.update(encrypted_chunk) + decryptor.finalize()
                        decrypted_data += unpadder.update(padded_data)
                
                decrypted_data += unpadder.finalize()
                decompressed_data = self.decompress_data(decrypted_data)
                original_file.write(decompressed_data)
            
            logger.info(f"File {original_file_path} successfully reassembled.")
            self.cleanup_local_files(guid_folder)
        except Exception as e:
            logger.error(f"Error decrypting and reassembling file: {e}")
            self.cleanup_files([chunk["path"] for chunk in metadata['chunks']] + [original_file_path])
            raise e

    def cleanup_files(self, file_paths):
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {e}")

    def cleanup_local_files(self, folder_path):
        try:
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder_path)
            logger.info(f"Cleaned up folder: {folder_path}")
        except Exception as e:
            logger.error(f"Error cleaning up folder {folder_path}: {e}")
 
    def create_folder_tree(self,conn, full_path):
        # Separate the filename from the path
        folder_path, file_name = os.path.split(full_path)

        # Create all folders in the path recursively
        folders = folder_path.strip('/').split('/')
        current_path = ''
        for folder in folders:
            current_path += f'/{folder}'
            try:
                conn.createDirectory(self.share_location, current_path)
                print(f"Created folder: {current_path}")
            except Exception as e:
                print(f"Failed to create folder {current_path}: {e}")

        # Create the file at the end of the path
        if file_name:
            try:
                with conn.openFile(f'{self.share_location}/{folder_path}/{file_name}', 'w') as file:
                    file.write(b'')  # Empty content for now
                print(f"File '{file_name}' created successfully.")
            except Exception as e:
                print(f"Failed to create file '{file_name}': {e}")

def handle_request(request_type, file_path, key, efs):
    try:
        if request_type == "save":
            efs.save_file(file_path, key)
        elif request_type == "retrieve":
            efs.decrypt_and_reassemble_file(file_path, key)
    except Exception as e:
        logger.error(f"Error handling {request_type} request for {file_path}: {e}")

# Example Usage
# if __name__ == "__main__":
#     key = os.urandom(32)  # AES-256 key from environment variable or secure key management
#     #efs = EncryptedFileSystem('192.168.2.201', 'user', 'Server@123', 'shared2')
#     efs = EncryptedFileSystem('192.168.2.15', 'admin', 'Server123', 'NAS Drive')

#     # Example file paths
#     save_file_path = "D:\\Users\\user\\Downloads\\cv's apex university\\MCA 2025\\Akansha Sharma-MCA-2025-Web developer.docx"
#     retrieve_file_path = "D:\\Users\\user\\Downloads\\cv's apex university\\MCA 2025\\Akansha Sharma-MCA-2025-Web developer.docx"

#     # Save file to server
#     efs.save_file(save_file_path, key)
#     logger.info("File saved to server.")

#     # Retrieve and decrypt file from server
#     efs.decrypt_and_reassemble_file(retrieve_file_path, key)
#     logger.info("File retrieved and decrypted from server.")

#     # # Simulate concurrent requests for stress testing
#     # requests = [("save", f"path/to/local/file{i}.txt", key) for i in range(10)] + \
#     #            [("retrieve", f"path/to/local/file{i}.txt", key) for i in range(10)]

#     # with ThreadPoolExecutor(max_workers=20) as executor:
#     #     futures = [executor.submit(handle_request, request_type, file_path, key, efs) for request_type, file_path, key in requests]
#     #     for future in as_completed(futures):
#     #         future.result()  # To raise exceptions, if any

#     logger.info("All requests handled.")

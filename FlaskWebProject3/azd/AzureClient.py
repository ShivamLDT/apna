
import mimetypes
#import os
import hashlib
import logging
import socket
import time
from azure.storage.blob import BlobServiceClient, ContentSettings

from azure.core.exceptions import (
    ResourceNotFoundError,ResourceExistsError,
    ServiceRequestError, ServiceResponseError,
    HttpResponseError, AzureError
)
from cryptography.fernet import Fernet
import json

from fingerprint import get_encryption_key_storage
# account_name = "cloudbackupapna"
# account_key = "WQ/S0bDskUvPhhvSevsi1zL1tXGdvxxJnVjfAnXtSu2lks4+n5PFv1GSt+H/lnwCWfQO3+d7sVqX+AStDzniLg=="

RETRY_LIMIT =[
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,  
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,  
    
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4, 
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4, 

    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,  
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,  
    
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4, 
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4, 

    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,  
    4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,     4,5,6, 4,5,6, 4,5,6, 4,5,6,  
    
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4, 
    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4,    4,7,4, 4,8,4, 4,9,4, 4,10,4, 


]
RETRY_BACKOFF_BASE = 2

def encrypt_data(enc_key,data):
        from cryptography.fernet import Fernet
        import base64
        import hashlib
        hash_key = hashlib.sha256(enc_key.encode()).digest()
        key = base64.urlsafe_b64encode(hash_key[:32])
        cipher = Fernet(key)
        return cipher.encrypt(data.encode()).decode()

class AzureBlobClient:
    def __init__(self, container_name=None, account_key=None,account_name=None):
        creds = self.load_credentials()
        
        if creds:
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={creds['access_key']};AccountKey={creds['secret_key']};EndpointSuffix=core.windows.net"
            container_name = creds['container_name']
        else:
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        try:
        # Create a new container (Blob Store)
            self.container_client = self.blob_service_client.create_container(self.container_name)
            print(f"Container '{container_name}' created successfully.")
        except ResourceExistsError:
            print(f"Container '{container_name}' already exists.")

        self.container_client = self.blob_service_client.get_container_client(container_name)

        # Create the container if it doesn't exist
        try:
            self.container_client.create_container()
            self.valid=True
        except Exception:
            self.valid=False

    def upload_data(self, file_name, data, content_type=None):
        """Uploads data directly to a blob. Sets Content-MD5 so Azure verifies integrity at cloud (chunk complete)."""
        try:
            if content_type == None:
                content_type="application/octet-stream"
            blob_client = self.container_client.get_blob_client(file_name)
            # Integrity at cloud: Azure validates upload against this MD5; reject if mismatch
            content_md5 = bytearray(hashlib.md5(data).digest())
            content_settings = ContentSettings(content_type=content_type, content_md5=content_md5)
            for attempt in RETRY_LIMIT:
                try: 
                    response =blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
                    file_id = response.get('etag', '').strip('"')
                    logging.info(f"File {file_name} uploaded successfully with ETag: {file_id}")
                    return {"file_key": file_name, "file_id": file_id} 
                    break
                except (ServiceRequestError, ServiceResponseError, socket.timeout) as e:
                    print(f"[Network error] Retrying chunk {e}")
                except HttpResponseError as e:
                    print(f"[HTTP error] Chunk failed with status {e.status_code}")
                    if e.status_code not in [500, 503]:  # not retryable
                        raise
                except AzureError as e:
                    print(f"[AzureError] Chunk failed: {e}")

                backoff = RETRY_BACKOFF_BASE ** attempt                                
                time.sleep(backoff)
            else:
                raise Exception(f"Chunk failed after  retries")
        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            return {"error": str(e)}

    def upload_file(self, file_path, file_name):
        """Uploads a file to Azure Blob Storage. Sets Content-MD5 so Azure verifies integrity at cloud (chunk complete)."""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            blob_client = self.container_client.get_blob_client(file_name)
            content_type, _ = mimetypes.guess_type(file_path)
            content_md5 = bytearray(hashlib.md5(data).digest())
            content_settings = ContentSettings(content_type=content_type, content_md5=content_md5)
            for attempt in RETRY_LIMIT:
                try: 
                    blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
                    break
                    except (ServiceRequestError, ServiceResponseError, socket.timeout) as e:
                        print(f"[Network error] Retrying {e}")
                    except HttpResponseError as e:
                        print(f"[HTTP error] Chunk failed with status {e.status_code}")
                        if e.status_code not in [500, 503]:  # not retryable
                            raise
                    except AzureError as e:
                        print(f"[AzureError] Chunk failed: {e}")
                        
                    backoff = RETRY_BACKOFF_BASE ** attempt
                    time.sleep(backoff)
                else:
                    raise Exception(f"Chunk failed after  retries")

            logging.info(f"File '{file_name}' uploaded successfully")
            return file_name
        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            return str(e)

    def upload_large_file(self, file_path, file_name):
        """Uploads a large file to Azure Blob Storage using chunking."""
        try:
            blob_client = self.container_client.get_blob_client(file_name)
            with open(file_path, "rb") as data:
                for attempt in RETRY_LIMIT:
                    try:
                        blob_client.upload_blob(data, overwrite=True)
                        break
                    except (ServiceRequestError, ServiceResponseError, socket.timeout) as e:
                        print(f"[Network error] Retrying chunk : {e}")
                    except HttpResponseError as e:
                        print(f"[HTTP error] Chunk failed with status {e.status_code}")
                        if e.status_code not in [500, 503]:  # not retryable
                            raise
                    except AzureError as e:
                        print(f"[AzureError] Chunk failed: {e}")
                        
                    backoff = RETRY_BACKOFF_BASE ** attempt
                    time.sleep(backoff)
                else:
                    raise Exception(f"Chunk failed after  retries")

            logging.info(f"Large file '{file_name}' uploaded successfully")
            return file_name
        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            return str(e)

    def download_file(self, file_name, local_path):
        """Downloads a file from Azure Blob Storage."""
        try:
            
            blob_client = self.container_client.get_blob_client(file_name)
            with open(local_path, "wb") as file:
                file.write(blob_client.download_blob().readall())
            logging.info(f"File '{file_name}' downloaded successfully to '{local_path}'")
            return f"File '{file_name}' downloaded successfully"
        except ResourceNotFoundError:
            logging.error(f"Blob '{file_name}' not found")
            return f"Blob '{file_name}' not found"
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return str(e)

    def download_data(self, file_name):
        """Downloads a file from Azure Blob Storage."""
        try:
            blob_client = self.container_client.get_blob_client(file_name)
            #blob_client.download_blob().readall()
            logging.info(f"sending File '{file_name}' to be downloaded.")
            return blob_client.download_blob().readall()
        except ResourceNotFoundError:
            logging.error(f"Blob '{file_name}' not found")
            return f"Blob '{file_name}' not found"
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return str(e)

    def delete_file(self, blob_name):
        """Deletes a file from Azure Blob Storage."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            logging.info(f"Blob '{blob_name}' deleted successfully")
            return f"Blob '{blob_name}' deleted successfully"
        except ResourceNotFoundError:
            logging.error(f"Blob '{blob_name}' not found")
            return f"Blob '{blob_name}' not found"
        except Exception as e:
            logging.error(f"Delete failed: {str(e)}")
            return str(e)

    def list_files(self):
        """Lists files in the container."""
        try:
            blobs = [blob.name for blob in self.container_client.list_blobs()]
            logging.info(f"Files in container: {blobs}")
            return blobs
        except Exception as e:
            logging.error(f"List files failed: {str(e)}")
            return str(e)

    def generate_presigned_url(self, blob_name, expiration=3600):
        """Generates a presigned URL for a blob."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            url = blob_client.url
            logging.info(f"Generated presigned URL for '{blob_name}'")
            return url
        except Exception as e:
            logging.error(f"Presigned URL generation failed: {str(e)}")
            return str(e)

    def create_folder(self, folder_name):
        """Creates a 'folder' in Azure Blob Storage (by creating an empty blob)."""
        try:
            if not folder_name.endswith('/'):
                folder_name += '/'
            blob_client = self.container_client.get_blob_client(folder_name)
            blob_client.upload_blob(b"", overwrite=True)
            logging.info(f"Folder '{folder_name}' created successfully")
            return folder_name
        except Exception as e:
            logging.error(f"Create folder failed: {str(e)}")
            return str(e)

    def delete_folder(self, folder_name):
        """Deletes a folder and its contents from Azure Blob Storage."""
        try:
            if not folder_name.endswith('/'):
                folder_name += '/'
            blobs = self.container_client.list_blobs(name_starts_with=folder_name)
            for blob in blobs:
                self.container_client.delete_blob(blob.name)
            logging.info(f"Folder '{folder_name}' deleted successfully")
            return folder_name
        except Exception as e:
            logging.error(f"Delete folder failed: {str(e)}")
            return str(e)

    @staticmethod
    def load_credentials(file_path='azure_credentials.enc'):
        try:
            key = get_encryption_key_storage()        
            cipher = Fernet(key)
            with open(file_path, "r") as file:
                json_data = file.read()
                json_data =cipher.decrypt(json_data.encode()).decode()
                return json.loads(json_data)
        except:
            return None

    @staticmethod
    def send_endpoint_credentials(file_path='azure_credentials.enc',encrypt_key=None):
        from flask import send_file
        agent_path=file_path.replace(".enc",f"_{encrypt_key}.enc")
        json_data={}
        try:
            key = get_encryption_key_storage()        
            cipher = Fernet(key)
            with open(file_path, "r") as file:
                json_data = file.read()
                json_data =cipher.decrypt(json_data.encode()).decode()
                json_data= encrypt_data(encrypt_key,json_data)
            
            with open(agent_path,"w") as file:
                file.write(json_data)
            # return send_file(
            #         agent_path,
            #         as_attachment=True,
            #         conditional=True  
            #     )
            return agent_path
        except:
            return None

    @staticmethod
    def validate_azure_credentials(access_key=None, secret_key=None, container_name=None):#,user_id):
        try:
            if access_key==None or secret_key==None or container_name==None:
                credentials = AzureBlobClient.load_credentials()
                access_key = credentials["access_key"]
                secret_key = credentials["secret_key"]
                container_name = credentials["container_name"]
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={access_key};AccountKey={secret_key};EndpointSuffix=core.windows.net"
            client = BlobServiceClient.from_connection_string(connection_string)
            container_client = client.get_container_client(container_name)
            container_client.get_container_properties()
            return True
        except Exception as e:
            return False

# if __name__ == '__main__':
#     s= AzureBlobClient()
#     fn=r"D:\ApnaBackup\7c3eb001aa90c597e790f0468db1e0416a89089266e5d1dbc018bac5aa8a306a\I{{DRIVE}}\okkihihihijijij\ClientReport.css_1742913676.7563128.gz"
#     with open (fn,"rb") as dd:
#         sd = s.upload_data(fn, dd.read(), "text/plain")
#     print (sd)
#     s.download_file(fn,fn+".zip")


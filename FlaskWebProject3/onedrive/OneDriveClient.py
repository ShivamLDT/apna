
import os
import io
import json
import time
import socket
import logging
import mimetypes
import requests
from cryptography.fernet import Fernet
from requests.exceptions import Timeout, ConnectionError, RequestException

from fingerprint import get_encryption_key_storage

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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def encrypt_data(enc_key,data):
        from cryptography.fernet import Fernet
        import base64
        import hashlib
        hash_key = hashlib.sha256(enc_key.encode()).digest()
        key = base64.urlsafe_b64encode(hash_key[:32])
        cipher = Fernet(key)
        return cipher.encrypt(data.encode()).decode()

class OneDriveClient:
    def __init__(self, creds_file="OneDrive_credentials.enc"):
        self.session = requests.Session()
        creds = self.load_credentials(creds_file)
        self.creds =creds
        self.client_id = creds.get("client_id")
        self.client_secret = creds.get("client_secret")
        self.tenant_id = creds.get("tenant_id")
        self.user_id = creds.get("user_id")  # can be user id or "me"

        self.base_url = f"https://graph.microsoft.com/v1.0/users/{self.user_id}/drive"
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        self.access_token =None
        self.refresh_token = None
        self.token_expires=0
        
        self.fetch_onedrive_token()

    def fetch_onedrive_token(self):
        
        client_id =self.client_id
        client_secret =self.client_secret

        token_url = self.token_url
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "offline_access https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        response = self.session.post(token_url, data=data,verify=False)
        response.raise_for_status()
        token_data = response.json()
        
        self.access_token= token_data["access_token"]
        self.token_expires = int(time.time()) + int(token_data.get("expires_in", 3600))
        self.refresh_token= token_data.get("refresh_token")  
        
        return {
            "access_token": token_data["access_token"],
            "token_expires": int(time.time()) + int(token_data.get("expires_in", 3600)),
            "refresh_token": token_data.get("refresh_token")  # May be None with client_credentials grant
        }


    def get_valid_onedrive_token(self):
        if "access_token" not in self.creds or time.time() >= self.creds.get("token_expires", 0):
            new_tokens = self.fetch_onedrive_token()
            self.creds.update(new_tokens)
        return self.creds["access_token"]

  
    def headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def refresh_access_token(self):
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
            'scope': 'https://graph.microsoft.com/.default offline_access'
        }
        response = self.session.post(self.token_url, data=payload,verify=False)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            logging.info("Access token refreshed")
        else:
            logging.error(f"Token refresh failed: {response.text}")
            raise Exception("Token refresh failed")

    def upload_file(self, local_path, remote_path):
        """Uploads file to OneDrive (simple upload for small files)"""
        try:
            url = f"{self.base_url}/root:/{remote_path}:/content"
            content_type, _ = mimetypes.guess_type(local_path)
            with open(local_path, 'rb') as f:
                file_data = f.read()

            for attempt in RETRY_LIMIT:
                try:
                    response = self.session.put(url, headers=self.headers(), data=file_data,verify=False)
                    if response.status_code in [200, 201]:
                        return response.json()
                    elif response.status_code == 401:
                        self.refresh_access_token()
                        continue
                    else:
                        logging.warning(f"Upload failed (attempt {attempt}): {response.text}")
                except (Timeout, ConnectionError, socket.timeout) as e:
                    logging.warning(f"Network retry {attempt}: {e}")

                time.sleep(RETRY_BACKOFF_BASE ** attempt)
        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            return {"error": str(e)}

    def download_file(self, remote_path, local_path):
        try:
            metadata_url = f"{self.base_url}/root:/{remote_path}"
            metadata = self.session.get(metadata_url, headers=self.headers(),verify=False).json()
            download_url = metadata["@microsoft.graph.downloadUrl"]

            # response = self.session.get(download_url, stream=True,verify=False)
            # with open(local_path, 'wb') as f:
            #     for chunk in response.iter_content(4096):
            #         f.write(chunk)
            # logging.info(f"Downloaded {remote_path} to {local_path}")
            # return local_path
            return download_url
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return str(e)

    def create_folder(self, folder_name, parent_path=None):
        try:
            parent_url = f"{self.base_url}/root" if not parent_path else f"{self.base_url}/root:/{parent_path}:/children"
            url = f"{parent_url}/children"
            payload = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail"
            }
            response = self.session.post(url, headers=self.headers(), json=payload,verify=False)
            return response.json()
        except Exception as e:
            logging.error(f"Create folder failed: {str(e)}")
            return str(e)

    def delete_file_or_folder(self, remote_path):
        try:
            url = f"{self.base_url}/root:/{remote_path}"
            response = self.session.delete(url, headers=self.headers(),verify=False)
            if response.status_code == 204:
                logging.info(f"Deleted: {remote_path}")
                return f"Deleted: {remote_path}"
            else:
                return response.text
        except Exception as e:
            logging.error(f"Delete failed: {str(e)}")
            return str(e)

    def list_files(self, folder_path=None):
        try:
            path = folder_path or ""
            url = f"{self.base_url}/root:/{path}:/children"
            response = self.session.get(url, headers=self.headers(),verify=False)
            return [item["name"] for item in response.json().get("value", [])]
        except Exception as e:
            logging.error(f"List failed: {str(e)}")
            return str(e)

    @staticmethod
    def load_credentials(file_path='OneDrive_credentials.enc'):
        try:
            key = get_encryption_key_storage()
            cipher = Fernet(key)
            with open(file_path, "r") as file:
                json_data = file.read()
                json_data = cipher.decrypt(json_data.encode()).decode()
                return json.loads(json_data)
        except Exception as e:
            logging.error(f"Credential load failed: {str(e)}")
            raise
    
    @staticmethod
    def send_endpoint_credentials(file_path='OneDrive_credentials.enc',encrypt_key=None):
        from flask import send_file
        agent_path=file_path.replace(".enc",f"_{encrypt_key}.enc")
        json_data={}
        try:
        
            key = get_encryption_key_storage()        
            cipher = Fernet(key)
            with open(file_path, "r") as file:
                json_data = file.read()
                json_data =cipher.decrypt(json_data.encode()).decode()
                
            json_data =encrypt_data(encrypt_key,json_data)
            
            with open(agent_path,"w") as file:
                file.write(json_data)
                file.flush()

            return agent_path

        except Exception as exc:
            return None
    @staticmethod
    def validate_onedrive_credentials(client_id=None, client_secret=None, tenant_id=None):
        try:
            if client_id==None or client_secret==None or tenant_id==None:
                credentials = OneDriveClient.load_credentials()
                client_id = credentials["client_id"]
                client_secret = credentials["client_secret"]
                tenant_id = credentials["tenant_id"]

            token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            }

            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return True
        except Exception as e:
            return False

if __name__ == '__main__':
    client = OneDriveClient("OneDrive_credentials.enc")

    # 1. Create a folder
    folder_result = client.create_folder("TestBackupFolder")
    print("Folder Creation Result:", folder_result)

    # 2. Upload a small file to the new folder
    upload_result = client.upload_file("local_sample.txt", "TestBackupFolder/local_sample.txt")
    print("Upload Result:", upload_result)

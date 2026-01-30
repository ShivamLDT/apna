import os
import io
import pathlib
import pickle
import socket
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.errors import *
from pydispatch import dispatcher
from googleapiclient.errors import (
    InvalidJsonError, UnknownFileType, UnknownLinkType,
    UnknownApiNameOrVersion, UnacceptableMimeTypeError,
    MediaUploadSizeError, ResumableUploadError,
    InvalidChunkSizeError, InvalidNotificationError,
    UnexpectedMethodError, UnexpectedBodyError
)
import requests
from google.auth.exceptions import TransportError #google.auth.exceptions.TransportError,
import datetime

SCOPES = ["https://www.googleapis.com/auth/drive"]
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email']
#SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/drive.appdata']
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.appdata']
    
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

###271225
import threading
from functools import wraps

def synchronized(lock):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator

shared_lock = threading.Lock()
###271225

class GDClient:
    def __init__(
        self, credentials_path="client_secret.json", token_path="token.pickle",is_reset=False
    ):
        
        self.root_folder_metadata = {
            "name": "ApnaBackup",
            "mimeType": "application/vnd.google-apps.folder",
        }

        ###########
        self.FILE_NOT_FOUND = "FileNotFound"
        self.ACCESS_ERROR = "AccessError"
        self.ERROR = "Error"
        self.UPLOADED = "Uploaded"
        self.UPLOADED_PART_FILE = "UploadedPartFile"
        self.UPLOADED_JOB = "UploadedJob"

        self.DOWNLOADED = "Downloaded"
        self.DOWNLOADED_PART = "DownloadedPart"
        self.DOWNLOADED_PART_FILE = "DownloadedPartFile"
        self.DOWNLOADED_JOB = "DownloadedJob"

        self.CONNECTION_REJECTED = "ConnectionRejected"
        ###########

        self.credentials_path = credentials_path
        self.token_path = token_path
        if is_reset:
            self.delete_token_file()
        self.service = self.authenticate()
        self.ApnaBackupFolder =self.CreateApnaBackupFolder()
    
    @synchronized(shared_lock)    
    def CreateApnaBackupFolder(self):
        folder_name=get_date("pc")
        
        self.get_or_create_drive_path(f"ApnaBackup/{folder_name['date']}")  ## duplicate folder resolutions
        
        ApnaBackup = self.list_folders(q_name= "ApnaBackup",page_size=5)
        if not ApnaBackup:
            ApnaBackup=self.create_folder("ApnaBackup")
            if isinstance(ApnaBackup,list):
                return ApnaBackup[0].get("id",None)
            return ApnaBackup

        return ApnaBackup[0].get("id",None)

    def CreateFolder(self, folder_name):
        ApnaBackup_parent = self.CreateApnaBackupFolder()
        self.get_or_create_drive_path(f"ApnaBackup/{folder_name}")  ## duplicate folder resolutions
        ApnaBackup = self.list_folders(q_name= folder_name,q_parents=ApnaBackup_parent,page_size=5)
        if not ApnaBackup:
            ApnaBackup=self.create_folder(folder_name, ApnaBackup_parent)
            return ApnaBackup

        return ApnaBackup[0].get("id",None)

    def token_file_exists(self):
        return os.path.exists(self.token_path)
    def delete_token_file(self):
        if self.token_file_exists():
            os.remove(self.token_path)
        return os.path.exists(self.token_path)
    
    def config_file_exists(self):
        return os.path.exists(self.credentials_path)
    
    def authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)
        if os.path.exists(self.credentials_path):
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    #flow.redirect_uri("http://localhost:53335/login")
                    #creds = flow.run_local_server(port=53335)
                    try:
                        creds = flow.run_local_server(port=0)
                        with open(self.token_path, "wb") as token:
                            pickle.dump(creds, token)
                    except Exception as ere:
                        print(f"Google Authentication failed error occured {ere}")
        try:
            return build("drive", "v3", credentials=creds)
        except Exception as dfs:
            return None
    def craeteTokenFile(self):
        creds = None
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                #flow.redirect_uri = "http://localhost:53335/login"
                #creds = flow.run_local_server(port=53335)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "wb") as token:
                pickle.dump(creds, token)
        return build("drive", "v3", credentials=creds)

    def list_files(
        self,
        page_size=1000,
        q_name=None,
        q_modifiedTimeFrom=None,
        q_modifiedTimeTo=None,
        q_parents=None,
        q_fields="nextPageToken, files(id, name, modifiedTime)"
    ):
        # search_query = (
        #     "name contains 'example_name' and "
        #     "modifiedTime > '" + q_modifiedTimeFrom + "' and "
        #     "modifiedTime < '" + q_modifiedTimeTo + "' and "
        #     "'"+q_parents+"' in  + parents"
        # )
        try:
            results = (
                self.service.files()
                .list(pageSize=page_size, fields="nextPageToken, files(id,mimeType, name)")
                .execute()
            )
            items = results.get("files", [])
            if not items:
                print("No files found.")
            else:
                print("Files:")
                for item in items:
                    print("{0}\t\t{1}\t\t({2})".format(item["name"], item["mimeType"], item["id"]))
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
            print(f"Google Drive is not reachable an error occurred : {error}")
    def list_folders(
        self,
        page_size=1000,
        q_name=None,
        q_modifiedTimeFrom=None,
        q_modifiedTimeTo=None,
        q_parents=None,
        q_fields="nextPageToken, files(id, name, modifiedTime)"
    ):
        # search_query = (
        #     "name contains 'example_name' and "
        #     "modifiedTime > '" + q_modifiedTimeFrom + "' and "
        #     "modifiedTime < '" + q_modifiedTimeTo + "' and "
        #     "'"+q_parents+"' in  + parents"
        # )
        try:
            if not q_name:
                q_name="*"

            query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
            if q_name:
                query += f" and name='{q_name}'"
            if q_parents:
                query += f" and '{q_parents}' in parents"

            page_token=None
            # results = (
            #     self.service.files()
            #     #.list(pageSize=page_size, fields="nextPageToken, files(id,mimeType, name)")
            #     #.list(q="mimeType = 'application/vnd.google-apps.folder'",
            #     .list(q=query,
            #           spaces="drive",
            #           fields="nextPageToken, files(id, mimeType, name)",
            #           pageToken = page_token)
          
            #     .execute()
            # )
            # items = results.get("files", [])

            items = []
            page_token = None

            while True:
                response = self.service.files().list(
                    q=query,
                    pageSize=page_size,
                    fields="nextPageToken, files(id, name, mimeType)",
                    spaces="drive",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    pageToken=page_token
                ).execute()

                items.extend(response.get("files", []))
                page_token = response.get("nextPageToken")

                if not page_token:
                    break

            if not items:
                print("No files found.")
                return None
            else:
                print("Files:")
                for item in items:
                    print("{0}\t\t{1}\t\t({2})".format(item["name"], item["mimeType"], item["id"]))
                return items
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
            print(f"Google Drive is not reachable an error occurred : {error}")
            
            return None
    
    def upload_file(self, file_path, mime_type,file_jid,parent_folder=None):
        
        ##kartik
        folder_id = None
        if parent_folder:
            folder_id=self.CreateFolder(parent_folder)
        if not folder_id:
            folder_id=self.ApnaBackupFolder
        ##kartik
        file_gid = None
        
        for attempt in RETRY_LIMIT: 

            
            try:
                if isinstance(file_path, dict):
                    file_stream=io.BytesIO(file_path["file"][1])
                    file_path=file_path["file"][0]
                    file_metadata = {"name": file_path + ".abgd","parents": [folder_id]}
                    media = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True)
                    file = self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id, name, mimeType, webViewLink, sha256Checksum'
                    ).execute()
                    print(file)
                    return file
                else:
                    file_metadata = {"name": pathlib.Path(file_path).stem + ".abgd","parents": [folder_id]}
                    media = MediaFileUpload(file_path, mimetype=mime_type)
                    media = MediaFileUpload(file_path,chunksize=5*1024*1024*1024 ,resumable=True)

                    file = (
                        self.service.files()
                        .create(
                            body=file_metadata,
                            keepRevisionForever=True,
                            media_body=media,
                            fields="id,name, mimeType, webViewLink",
                        )
                        .execute()
                    )
                    print("File ID: %s" % file.get("id"))
                    file_gid = file.get("id")
                    # dispatcher.dispatcher.send(
                    #     signal=self.UPLOADED,
                    #     sender=self,
                    #     file_path=file_path,
                    #     file_jid=file_jid,
                    #     file_gid=file_gid,
                    # )
                    break
            except (
                socket.timeout,
                requests.exceptions.Timeout,requests.exceptions.ConnectionError,TransportError,
                ResumableUploadError,
            ) as net_err:
                backoff = RETRY_BACKOFF_BASE ** attempt
                time.sleep(backoff)
            except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:          
                print(f"An error occurred: {error}")
                # dispatcher.dispatcher.send(
                #     signal=self.ERROR,
                #     sender=self,
                #     file_path=file_path,
                #     file_jid=file_jid,
                #     file_gid=file_gid,
                # )
        else:
            raise Exception(f"Chunk failed after  retries")
        return file_gid

    def download_file(self, file_id, file_path):
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_path, "wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
         
            print(f"An error occurred: {error}")

    def download_file_bytesio(self, file_id):
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
            fh.seek(0)
            return fh
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
            print(f"An error occurred: {error}")

    def create_folder(self, name,parent_folder=None):
        try:
            file_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            ##kartik
            if parent_folder:
                file_metadata['parents'] = [parent_folder]
            ##kartik
            folder = (
                self.service.files().create(body=file_metadata, fields="id").execute()
            )
            print("Folder ID: %s" % folder.get("id"))
            return folder.get("id")
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
            print(f"An error occurred: {error}")

    def share_file(self, file_id, user_email, role="reader"):
        try:
            batch = self.service.new_batch_http_request()
            user_permission = {"type": "user", "role": role, "emailAddress": user_email}
            batch.add(
                self.service.permissions().create(
                    fileId=file_id,
                    body=user_permission,
                    fields="id",
                )
            )
            batch.execute()
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:         
            print(f"An error occurred: {error}")

    def search_files(self, query, page_size=1000):
        try:
            results = (
                self.service.files()
                .list(
                    q=query, pageSize=page_size, fields="nextPageToken, files(id, name)"
                )
                .execute()
            )
            items = results.get("files", [])
            if not items:
                print("No files found.")
            else:
                print("Files:")
                for item in items:
                    print("{0} ({1})".format(item["name"], item["id"]))
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
            print(f"An error occurred: {error}")

    def search_folders(self, query, page_size=1000):
        try:
            results = (
                self.service.files()
                .list(
                    q=query, pageSize=page_size, fields="nextPageToken, files(id, name)"
                )
                .execute()
            )
            items = results.get("files", [])
            if not items:
                print("No files found.")
            else:
                print("Files:")
                for item in items:
                    print("{0} ({1})".format(item["name"], item["id"]))
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
            print(f"An error occurred: {error}")

    def update_file_metadata(self, file_id, new_name=None, new_mime_type=None):
        try:
            file_metadata = {}
            if new_name:
                file_metadata["name"] = new_name
            if new_mime_type:
                file_metadata["mimeType"] = new_mime_type
            updated_file = (
                self.service.files()
                .update(fileId=file_id, body=file_metadata, fields="id, name, mimeType")
                .execute()
            )
            print(
                f'Updated File ID: {updated_file.get("id")}, Name: {updated_file.get("name")}, MimeType: {updated_file.get("mimeType")}'
            )
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
         
            print(f"An error occurred: {error}")

    def delete_file(self, file_id):
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"File ID: {file_id} deleted successfully.")
        except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
         
            print(f"An error occurred: {error}")

    def upload_to_app_folder(self, filename, content, metadata=None):
        service= self.service
        file_metadata = {
            'name': filename,
            'parents': ['appDataFolder']
        }
        if metadata:
            file_metadata.update(metadata)

        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain')
        file = service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()
        print(f'Uploaded file: {filename} with ID: {file["id"]}')

    def list_app_folder_files(self):
        service = self.service
        results = service.files().list(
            spaces='appDataFolder',
            fields='files(id, name)'
        ).execute()
        files = results.get('files', [])
        for file in files:
            print(f'Found file: {file["name"]} ({file["id"]})')
    
    ##  duplicate resolution
    def get_or_create_drive_path(self, path, parent_id='root'):
        """
        Traverses a folder path and creates missing directories.
        :param service: Authorized Drive API service instance.
        :param path: String path like "Project/2025/Data"
        :param parent_id: Starting folder ID (defaults to 'root')
        :return: The ID of the final folder in the path.
        """
        # Clean the path and split into parts
        service=self.service
        parts = [p for p in path.split('/') if p]
    
        current_parent_id = parent_id
    
        for part in parts:
            # 1. Search for this folder name specifically within the current parent
            query = (f"name = '{part}' and '{current_parent_id}' in parents "
                     f"and mimeType = 'application/vnd.google-apps.folder' "
                     f"and trashed = false")
        
            results = service.files().list(
                q=query, 
                fields="files(id, name)",
                spaces='drive'
            ).execute()
        
            files = results.get('files', [])
        
            if files:
                # 2. Folder exists: use its ID as the parent for the next step
                current_parent_id = files[0]['id']
            else:
                # 3. Folder does not exist: create it
                file_metadata = {
                    'name': part,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [current_parent_id]
                }
                folder = service.files().create(
                    body=file_metadata, 
                    fields='id'
                ).execute()
                current_parent_id = folder.get('id')
            
        return current_parent_id

from email.utils import parsedate_to_datetime
def get_date(source: str = ""):


    # ---------- Try Online if source is "" or "online" ----------
    if source == "" or source.lower() == "online":
        try:
            dt = parsedate_to_datetime(
                requests.get("https://www.google.com", timeout=5).headers["Date"]
            )
            date_obj = dt.strftime("%Y-%m-%d")
            return {
                "source": "online",
                "date": date_obj
            }

        except Exception:
            # Auto fallback to PC
            return {
                "source": "pc",
                "date": datetime.date.today().strftime("%Y-%m-%d")
            }

    # ---------- PC Only ----------
    elif source.lower() == "pc":
        return {
            "source": "pc",
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }

    else:
        raise ValueError("Invalid source! Use '', 'pc', 'online', or add more source in function 'def get_date()' .")


def gd_test(is_reset=False):    
    client = None
    ret=False
    try:
        client = GDClient(is_reset=is_reset)
        if client:
            if client.config_file_exists():
                if client.config_file_exists():
                    if client.service:
                        #client.list_files()
                        ret =True
                    else:
                        print("Google Service is not reachable. Retry")
                else:
                    print("Google Authentication is missing. Retry")
            else:
                print("Google config file is missing contact Administrator")
        else:
            print("Google Drive cannot be setup contact Administrator")
    except Exception as dd:
        print(f"Google Drive cannot be setup an error occured {dd}" )
    
    return ret
    
# if __name__ == "__main__":
#     gd_test()


# import os
# import io
# import pathlib
# import pickle
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload
# from googleapiclient.errors import *
# from pydispatch import dispatcher

# SCOPES = ["https://www.googleapis.com/auth/drive"]
# SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email']
# #SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/drive.appdata']
# SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.appdata']
    


# class GDClient:
#     def __init__(
#         self, credentials_path="client_secret.json", token_path="token.pickle"
#     ):
#         self.root_folder_metadata = {
#             "name": "ApnaBackup",
#             "mimeType": "application/vnd.google-apps.folder",
#         }

#         ###########
#         self.FILE_NOT_FOUND = "FileNotFound"
#         self.ACCESS_ERROR = "AccessError"
#         self.ERROR = "Error"
#         self.UPLOADED = "Uploaded"
#         self.UPLOADED_PART_FILE = "UploadedPartFile"
#         self.UPLOADED_JOB = "UploadedJob"

#         self.DOWNLOADED = "Downloaded"
#         self.DOWNLOADED_PART = "DownloadedPart"
#         self.DOWNLOADED_PART_FILE = "DownloadedPartFile"
#         self.DOWNLOADED_JOB = "DownloadedJob"

#         self.CONNECTION_REJECTED = "ConnectionRejected"
#         ###########

#         self.credentials_path = credentials_path
#         self.token_path = token_path
#         self.service = self.authenticate()
#         self.ApnaBackupFolder =self.CreateApnaBackupFolder()
        
#     def CreateApnaBackupFolder(self):
#         ApnaBackup=    self.list_folders(q_name= "ApnaBackup",page_size=5)
#         if not ApnaBackup:
#             ApnaBackup=self.create_folder("ApnaBackup")
#             return ApnaBackup

#         return ApnaBackup[0].get("id",None)

    
#     def authenticate(self):
#         creds = None
#         if os.path.exists(self.token_path):
#             with open(self.token_path, "rb") as token:
#                 creds = pickle.load(token)
#         if os.path.exists(self.credentials_path):
#             if not creds or not creds.valid:
#                 if creds and creds.expired and creds.refresh_token:
#                     creds.refresh(Request())
#                 else:
#                     flow = InstalledAppFlow.from_client_secrets_file(
#                         self.credentials_path, SCOPES
#                     )
#                     #flow.redirect_uri("http://localhost:53335/login")
#                     #creds = flow.run_local_server(port=53335)
#                     creds = flow.run_local_server(port=0)
#                 with open(self.token_path, "wb") as token:
#                     pickle.dump(creds, token)
#         try:
#             return build("drive", "v3", credentials=creds)
#         except Exception as dfs:
#             return None
#     def craeteTokenFile(self):
#         creds = None
#         if os.path.exists(self.token_path):
#             with open(self.token_path, "rb") as token:
#                 creds = pickle.load(token)
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     self.credentials_path, SCOPES
#                 )
#                 #flow.redirect_uri = "http://localhost:53335/login"
#                 #creds = flow.run_local_server(port=53335)
#                 creds = flow.run_local_server(port=0)
#             with open(self.token_path, "wb") as token:
#                 pickle.dump(creds, token)
#         return build("drive", "v3", credentials=creds)

#     def list_files(
#         self,
#         page_size=1000,
#         q_name=None,
#         q_modifiedTimeFrom=None,
#         q_modifiedTimeTo=None,
#         q_parents=None,
#         q_fields="nextPageToken, files(id, name, modifiedTime)"
#     ):
#         # search_query = (
#         #     "name contains 'example_name' and "
#         #     "modifiedTime > '" + q_modifiedTimeFrom + "' and "
#         #     "modifiedTime < '" + q_modifiedTimeTo + "' and "
#         #     "'"+q_parents+"' in  + parents"
#         # )
#         try:
#             results = (
#                 self.service.files()
#                 .list(pageSize=page_size, fields="nextPageToken, files(id,mimeType, name)")
#                 .execute()
#             )
#             items = results.get("files", [])
#             if not items:
#                 print("No files found.")
#             else:
#                 print("Files:")
#                 for item in items:
#                     print("{0}\t\t{1}\t\t({2})".format(item["name"], item["mimeType"], item["id"]))
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
#             print(f"An error occurred: {error}")
#     def list_folders(
#         self,
#         page_size=1000,
#         q_name=None,
#         q_modifiedTimeFrom=None,
#         q_modifiedTimeTo=None,
#         q_parents=None,
#         q_fields="nextPageToken, files(id, name, modifiedTime)"
#     ):
#         # search_query = (
#         #     "name contains 'example_name' and "
#         #     "modifiedTime > '" + q_modifiedTimeFrom + "' and "
#         #     "modifiedTime < '" + q_modifiedTimeTo + "' and "
#         #     "'"+q_parents+"' in  + parents"
#         # )
#         try:
#             if not q_name:
#                 q_name="*"
#             page_token=None
#             results = (
#                 self.service.files()
#                 #.list(pageSize=page_size, fields="nextPageToken, files(id,mimeType, name)")
#                 #.list(q="mimeType = 'application/vnd.google-apps.folder'",
#                 .list(q="name  = '"+q_name+"'",
#                       spaces="drive",
#                       fields="nextPageToken, files(id, mimeType, name)",
#                       pageToken = page_token)
          
#                 .execute()
#             )
#             items = results.get("files", [])
#             if not items:
#                 print("No files found.")
#                 return None
#             else:
#                 print("Files:")
#                 for item in items:
#                     print("{0}\t\t{1}\t\t({2})".format(item["name"], item["mimeType"], item["id"]))
#                 return items
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
#             print(f"An error occurred: {error}")
            
#             return None
    
#     def upload_file(self, file_path, mime_type,file_jid):
#         folder_id=self.ApnaBackupFolder
#         file_gid = None
#         try:
#             file_metadata = {"name": pathlib.Path(file_path).stem + ".abgd","parents": [folder_id]}
#             media = MediaFileUpload(file_path, mimetype=mime_type)
#             media = MediaFileUpload(file_path)

#             file = (
#                 self.service.files()
#                 .create(
#                     body=file_metadata,
#                     keepRevisionForever=True,
#                     media_body=media,
#                     fields="id",
#                 )
#                 .execute()
#             )
#             print("File ID: %s" % file.get("id"))
#             file_gid = file.get("id")
#             # dispatcher.dispatcher.send(
#             #     signal=self.UPLOADED,
#             #     sender=self,
#             #     file_path=file_path,
#             #     file_jid=file_jid,
#             #     file_gid=file_gid,
#             # )
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
          
#             print(f"An error occurred: {error}")
#             # dispatcher.dispatcher.send(
#             #     signal=self.ERROR,
#             #     sender=self,
#             #     file_path=file_path,
#             #     file_jid=file_jid,
#             #     file_gid=file_gid,
#             # )
#         return file_gid

#     def download_file(self, file_id, file_path):
#         try:
#             request = self.service.files().get_media(fileId=file_id)
#             fh = io.FileIO(file_path, "wb")
#             downloader = MediaIoBaseDownload(fh, request)
#             done = False
#             while not done:
#                 status, done = downloader.next_chunk()
#                 print("Download %d%%." % int(status.progress() * 100))
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
         
#             print(f"An error occurred: {error}")

#     def download_file_bytesio(self, file_id):
#         try:
#             request = self.service.files().get_media(fileId=file_id)
#             fh = io.BytesIO()
#             downloader = MediaIoBaseDownload(fh, request)
#             done = False
#             while not done:
#                 status, done = downloader.next_chunk()
#                 print("Download %d%%." % int(status.progress() * 100))
#             fh.seek(0)
#             return fh
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
#             print(f"An error occurred: {error}")

#     def create_folder(self, name):
#         try:
#             file_metadata = {
#                 "name": name,
#                 "mimeType": "application/vnd.google-apps.folder",
#             }
#             folder = (
#                 self.service.files().create(body=file_metadata, fields="id").execute()
#             )
#             print("Folder ID: %s" % folder.get("id"))
#             return folder.get("id")
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
#             print(f"An error occurred: {error}")

#     def share_file(self, file_id, user_email, role="reader"):
#         try:
#             batch = self.service.new_batch_http_request()
#             user_permission = {"type": "user", "role": role, "emailAddress": user_email}
#             batch.add(
#                 self.service.permissions().create(
#                     fileId=file_id,
#                     body=user_permission,
#                     fields="id",
#                 )
#             )
#             batch.execute()
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:         
#             print(f"An error occurred: {error}")

#     def search_files(self, query, page_size=1000):
#         try:
#             results = (
#                 self.service.files()
#                 .list(
#                     q=query, pageSize=page_size, fields="nextPageToken, files(id, name)"
#                 )
#                 .execute()
#             )
#             items = results.get("files", [])
#             if not items:
#                 print("No files found.")
#             else:
#                 print("Files:")
#                 for item in items:
#                     print("{0} ({1})".format(item["name"], item["id"]))
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
#             print(f"An error occurred: {error}")

#     def search_folders(self, query, page_size=1000):
#         try:
#             results = (
#                 self.service.files()
#                 .list(
#                     q=query, pageSize=page_size, fields="nextPageToken, files(id, name)"
#                 )
#                 .execute()
#             )
#             items = results.get("files", [])
#             if not items:
#                 print("No files found.")
#             else:
#                 print("Files:")
#                 for item in items:
#                     print("{0} ({1})".format(item["name"], item["id"]))
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
#             print(f"An error occurred: {error}")

#     def update_file_metadata(self, file_id, new_name=None, new_mime_type=None):
#         try:
#             file_metadata = {}
#             if new_name:
#                 file_metadata["name"] = new_name
#             if new_mime_type:
#                 file_metadata["mimeType"] = new_mime_type
#             updated_file = (
#                 self.service.files()
#                 .update(fileId=file_id, body=file_metadata, fields="id, name, mimeType")
#                 .execute()
#             )
#             print(
#                 f'Updated File ID: {updated_file.get("id")}, Name: {updated_file.get("name")}, MimeType: {updated_file.get("mimeType")}'
#             )
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
         
#             print(f"An error occurred: {error}")

#     def delete_file(self, file_id):
#         try:
#             self.service.files().delete(fileId=file_id).execute()
#             print(f"File ID: {file_id} deleted successfully.")
#         except (Exception,Error,HttpError,InvalidJsonError,UnknownFileType,UnknownLinkType,UnknownApiNameOrVersion,UnacceptableMimeTypeError,MediaUploadSizeError,ResumableUploadError,InvalidChunkSizeError,InvalidNotificationError,HttpError,UnexpectedMethodError,UnexpectedBodyError,Error ) as error:
         
#             print(f"An error occurred: {error}")

#     def upload_to_app_folder(self, filename, content, metadata=None):
#         service= self.service
#         file_metadata = {
#             'name': filename,
#             'parents': ['appDataFolder']
#         }
#         if metadata:
#             file_metadata.update(metadata)

#         media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain')
#         file = service.files().create(
#             body=file_metadata, media_body=media, fields='id'
#         ).execute()
#         print(f'Uploaded file: {filename} with ID: {file["id"]}')

#     def list_app_folder_files(self):
#         service = self.service
#         results = service.files().list(
#             spaces='appDataFolder',
#             fields='files(id, name)'
#         ).execute()
#         files = results.get('files', [])
#         for file in files:
#             print(f'Found file: {file["name"]} ({file["id"]})')

if __name__ == "__main__":
    client = GDClient()
    ApnaBackup=    client.list_folders(q_name= "ApnaBackup",page_size=5)
    
    from concurrent.futures import ThreadPoolExecutor

    def create_folder_task():
        return client.CreateApnaBackupFolder()

    # Run in 4 parallel threads
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(create_folder_task) for _ in range(4)]

        for f in futures:
            try:
                result = f.result()  # wait & catch exceptions
                print("Folder result:", result)
            except Exception as e:
                print("Error:", e)

    if not ApnaBackup:
        ApnaBackup=client.create_folder("ApnaBackup")
#     # client.list_files()
#     # client.upload_file("C:\\7\\tttt.txt", "text/plain","s")
#     # file_name = 'config.kuldeep'
#     # file_content = '{"setting1": "value1", "setting2": "value2"}'
#     # file_metadata = {'properties': {'project_id': '12345', 'environment': 'production'}}
#     # client.upload_to_app_folder( file_name, file_content, metadata=file_metadata)
#     client.list_app_folder_files()
#     buffer=client.download_file_bytesio("1726ssiy85UU4c_XIqo7OXn5spMobPZKEH7mBfcfi9cU4nPKVZg")
#     print (buffer.read().decode('utf-8'))
#     # Example usage:
#     # client.upload_file('path_to_your_file.txt', 'text/plain')
#     # client.download_file('your_file_id', 'path_to_save_file.txt')
#     # client.create_folder('New Folder')
#     # client.share_file('your_file_id', 'user@example.com')
#     # client.search_files("name contains 'report'")
#     # client.update_file_metadata('your_file_id', new_name='New Report', new_mime_type='application/pdf')
#     # client.delete_file('your_file_id')

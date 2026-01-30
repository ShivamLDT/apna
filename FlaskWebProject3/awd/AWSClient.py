
import json
#import os
import io
#import pathlib
#import pickle
import socket
import time
#from pydispatch import dispatcher
import boto3
import mimetypes
import logging
from botocore.exceptions import(
    EndpointConnectionError, ConnectionClosedError,
    ReadTimeoutError, IncompleteReadError, BotoCoreError,  
    NoCredentialsError, PartialCredentialsError, ClientError
)

#from flask import jsonify
from cryptography.fernet import Fernet

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
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def encrypt_data(enc_key,data):
        from cryptography.fernet import Fernet
        import base64
        import hashlib
        hash_key = hashlib.sha256(enc_key.encode()).digest()
        key = base64.urlsafe_b64encode(hash_key[:32])
        cipher = Fernet(key)
        return cipher.encrypt(data.encode()).decode()

class S3Client:
    #def __init__(self, bucket_name=BUCKET_NAME, aws_access_key_id =ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name='ap-south-1'): # us-east-1'):
    def __init__(self, bucket_name=None, aws_access_key_id =None, aws_secret_access_key=None, region_name='ap-south-1'): # us-east-1'):

        self.s3=None
        
        creds = self.load_credentials()
        try:
            self.s3 = boto3.client(
                's3',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id or creds["access_key"],
                aws_secret_access_key=aws_secret_access_key or creds["secret_key"]
            )
            self.bucket_name = bucket_name or creds["bucket_name"]
            
        except:
            self.s3=None

    def upload_data(self, file_path,file_data, s3_key):
        """Uploads a file using put_object and returns the file ETag (unique ID)."""
        try:
            content_type, _ = mimetypes.guess_type(file_path)
            extra_args = {'ContentType': content_type} if content_type else {}
            for attempt in RETRY_LIMIT:
                try:
                    response = self.s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=file_data, **extra_args)            
                    file_id = response.get('ETag', '').strip('"')
                    logging.info(f"File {s3_key} uploaded successfully with ETag: {file_id}")
                    return {"file_key": s3_key, "file_id": file_id}
                except (EndpointConnectionError, ConnectionClosedError,ReadTimeoutError, IncompleteReadError, socket.timeout) as e:
                    print(f"[Network error] Part  retry {attempt}: {e}")
                except ClientError as e:
                    code = e.response.get("Error", {}).get("Code")
                    print(f"[ClientError {code}] Part retry {attempt}")
                    if code not in ['RequestTimeout', 'Throttling', '500', '503']:
                        raise
                except (NoCredentialsError, PartialCredentialsError) as e:
                    logging.error(f"Upload error: {str(e)}")
                    return str(e)
                except BotoCoreError as e:
                    print(f"[BotoCoreError] Part  retry {attempt}: {e}")

                backoff = RETRY_BACKOFF_BASE ** attempt
                time.sleep(backoff)
            else:
                raise Exception(f"Unload failed after Max retries")

        except Exception as e:
            logging.error(f"Upload with put_object failed: {str(e)}")
            return {"error": str(e)}

    def upload_file(self, file_path, s3_key, callback=None):
        """Uploads a small file to S3"""
        try:
            for attempt in RETRY_LIMIT:
                try:
                    content_type, _ = mimetypes.guess_type(file_path)
                    extra_args = {'ContentType': content_type} if content_type else {}
                    self.s3.upload_file(file_path, self.bucket_name, s3_key, ExtraArgs=extra_args, Callback=callback)
                    logging.info(f"File {s3_key} uploaded successfully")
                    return s3_key
                except (EndpointConnectionError, ConnectionClosedError,ReadTimeoutError, IncompleteReadError, socket.timeout) as e:
                    print(f"[Network error] Part  retry {attempt}: {e}")
                except ClientError as e:
                    code = e.response.get("Error", {}).get("Code")
                    print(f"[ClientError {code}] Part retry {attempt}")
                    if code not in ['RequestTimeout', 'Throttling', '500', '503']:
                        raise
                except (NoCredentialsError, PartialCredentialsError) as e:
                    logging.error(f"Upload error: {str(e)}")
                    return str(e)
                except BotoCoreError as e:
                    print(f"[BotoCoreError] Part retry {attempt}: {e}")
                    return str(e)

                backoff = RETRY_BACKOFF_BASE ** attempt
                time.sleep(backoff)
                #else:
                #    raise Exception(f"Part {part_number} failed after {MAX_RETRIES} retries")
        except ClientError as e:
            logging.error(f"Upload failed: {e.response['Error']['Message']}")
            return e.response['Error']['Message']
        except Exception as e:
            logging.error(f"Upload with put_object failed: {str(e)}")
            return {"error": str(e)}

    def upload_large_file(self, file_path, s3_key, callback=None):
        """Uploads a large file to S3 using multipart upload"""
        try:
            for attempt in RETRY_LIMIT:
                try:
                    content_type, _ = mimetypes.guess_type(file_path)
                    extra_args = {'ContentType': content_type} if content_type else {}
                    transfer_config = boto3.s3.transfer.TransferConfig(multipart_threshold=5 * 1024 * 1024)
                    self.s3.upload_file(file_path, self.bucket_name, s3_key, ExtraArgs=extra_args, Config=transfer_config, Callback=callback)
                    logging.info(f"Large file {s3_key} uploaded successfully")
                    return s3_key
                except (EndpointConnectionError, ConnectionClosedError,ReadTimeoutError, IncompleteReadError, socket.timeout) as e:
                    print(f"[Network error] Part  retry {attempt}: {e}")
                except ClientError as e:
                    code = e.response.get("Error", {}).get("Code")
                    print(f"[ClientError {code}] Part  retry {attempt}")
                    if code not in ['RequestTimeout', 'Throttling', '500', '503']:
                        raise
                except (NoCredentialsError, PartialCredentialsError) as e:
                    logging.error(f"Upload error: {str(e)}")
                    return str(e)
                except BotoCoreError as e:
                    print(f"[BotoCoreError] Part  retry {attempt}: {e}")
                    return str(e)

                backoff = RETRY_BACKOFF_BASE ** attempt
                time.sleep(backoff)
        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            return str(e)
    def download_file(self, s3_key, local_path):
        """Downloads a file from S3"""
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_path)
            logging.info(f"File {s3_key} downloaded successfully")
            return f"File {s3_key} downloaded successfully"
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return str(e)

    def download_data(self, s3_key):
        """Downloads a file from S3"""
        try:
            if not str(s3_key).lower().startswith("apnabackup/"):
                s3_key= "ApnaBackup/"+s3_key
            response = self.s3.get_object (Bucket=self.bucket_name, Key=s3_key)
            buffer  = response['Body'].read()
            logging.info(f"File {s3_key} downloaded successfully")
            return buffer #"File {s3_key} downloaded successfully"
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return str(e)

    def download_data_BytesIO(self, s3_key):
        """Downloads a file from S3"""
        try:
            buffer = io.BytesIO()
            response = self.s3.download_fileobj (self.bucket_name, s3_key,Fileobj=buffer)
            buffer.seek(0)
            logging.info(f"File {s3_key} downloaded successfully")
            return buffer #"File {s3_key} downloaded successfully"
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            return str(e)

    def delete_file(self, s3_key):
        """Deletes a file from S3"""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logging.info(f"File {s3_key} deleted successfully")
            return f"File {s3_key} deleted successfully"
        except Exception as e:
            logging.error(f"Delete failed: {str(e)}")
            return str(e)

    def list_files(self):
        """Lists files in the S3 bucket"""
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            logging.info(f"Listed files: {files}")
            return files
        except Exception as e:
            logging.error(f"List failed: {str(e)}")
            return str(e)

    def generate_presigned_url(self, s3_key, expiration=3600):
        """Generates a presigned URL for a file"""
        try:
            url = self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket_name, 'Key': s3_key}, ExpiresIn=expiration)
            logging.info(f"Generated presigned URL for {s3_key}")
            return url
        except Exception as e:
            logging.error(f"Presigned URL generation failed: {str(e)}")
            return str(e)

    def create_folder(self, folder_name):
        """Creates a folder in S3"""
        try:
            if not folder_name.endswith('/'):
                folder_name += '/'
            self.s3.put_object(Bucket=self.bucket_name, Key=folder_name)
            logging.info(f"Folder {folder_name} created successfully")
            return folder_name
        except Exception as e:
            logging.error(f"Create folder failed: {str(e)}")
            return str(e)

    def delete_folder(self, folder_name):
        """Deletes a folder and its contents from S3"""
        try:
            if not folder_name.endswith('/'):
                folder_name += '/'
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_name)
            if 'Contents' in response:
                for obj in response['Contents']:
                    self.s3.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
            logging.info(f"Folder {folder_name} deleted successfully")
            return folder_name
        except Exception as e:
            logging.error(f"Delete folder failed: {str(e)}")
            return str(e)
    @staticmethod
    def load_credentials(file_path='aws_credentials.enc'):
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
    def send_endpoint_credentials(file_path='aws_credentials.enc',encrypt_key=None):
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

            # return send_file(
            #         agent_path,
            #         as_attachment=True,
            #         conditional=True  )

        except Exception as exc:
            return None

    @staticmethod
    def validate_aws_credentials(access_key=None, secret_key=None, bucket_name=None):
        try:
            if access_key==None or secret_key==None or bucket_name==None:
                credentials = S3Client.load_credentials()
                access_key = credentials["access_key"]
                secret_key = credentials["secret_key"]
                bucket_name = credentials["bucket_name"]
            s3 = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key)
            s3.head_bucket(Bucket=bucket_name)
            return True
        except Exception as e:
            return False



# # Flask API
# app = Flask(__name__)

# @app.route('/upload', methods=['POST'])
# def upload():
#     """Handles file uploads to S3"""
#     file = request.files['file']
#     folder_path = request.form.get('folder_path', '')
#     aws_access_key = request.form.get('aws_access_key')
#     aws_secret_key = request.form.get('aws_secret_key')
#     bucket_name = request.form.get('bucket_name')

#     if not aws_access_key or not aws_secret_key or not bucket_name:
#         return jsonify({'error': 'AWS credentials and bucket name are required'}), 400

#     s3_client = S3Client(bucket_name=bucket_name, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

#     # Generate S3 key for nested folders
#     s3_key = f"{folder_path}/{file.filename}".lstrip('/') if folder_path else file.filename
#     file_path = f"/tmp/{file.filename}"
#     file.save(file_path)

#     # Upload progress callback
#     def progress_callback(bytes_transferred):
#         logging.info(f"Uploaded {bytes_transferred} bytes")

#     # Upload file
#     s3_key_response = s3_client.upload_large_file(file_path, s3_key, callback=progress_callback)

#     os.remove(file_path)
#     return jsonify({'message': 'File uploaded successfully', 's3_key': s3_key_response})

# @app.route('/create_folder', methods=['POST'])
# def create_folder():
#     """Creates a folder in S3"""
#     folder_name = request.form.get('folder_name', '')
#     aws_access_key = request.form.get('aws_access_key')
#     aws_secret_key = request.form.get('aws_secret_key')
#     bucket_name = request.form.get('bucket_name')

#     if not aws_access_key or not aws_secret_key or not bucket_name:
#         return jsonify({'error': 'AWS credentials and bucket name are required'}), 400

#     s3_client = S3Client(bucket_name=bucket_name, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    
#     response = s3_client.create_folder(folder_name)
#     return jsonify({'message': 'Folder created successfully', 'folder_name': response})

# @app.route('/delete_folder', methods=['POST'])
# def delete_folder():
#     """Deletes a folder and its contents from S3"""
#     folder_name = request.form.get('folder_name', '')
#     aws_access_key = request.form.get('aws_access_key')
#     aws_secret_key = request.form.get('aws_secret_key')
#     bucket_name = request.form.get('bucket_name')

#     if not aws_access_key or not aws_secret_key or not bucket_name:
#         return jsonify({'error': 'AWS credentials and bucket name are required'}), 400

#     s3_client = S3Client(bucket_name=bucket_name, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

#     response = s3_client.delete_folder(folder_name)
#     return jsonify({'message': 'Folder deleted successfully', 'folder_name': response})

# if __name__ == '__main__':
#     app.run(debug=True)


# # Flask API
# app = Flask(__name__)
# s3_client = S3Client(bucket_name='your-bucket-name')

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     folder_path = request.form.get('folder_path', '')
#     s3_key = f"{folder_path}/{file.filename}" if folder_path else file.filename
#     file_path = f"/tmp/{file.filename}"
#     file.save(file_path)
    
#     def progress_callback(bytes_transferred):
#         logging.info(f"Uploaded {bytes_transferred} bytes")
    
#     s3_key_response = s3_client.upload_large_file(file_path, s3_key, callback=progress_callback)
#     os.remove(file_path)
#     return jsonify({'message': 'File uploaded successfully', 's3_key': s3_key_response})

# if __name__ == '__main__':
#     s3 = S3Client()
#     file_list=s3.list_files()
#     print(len(file_list))
    
#     #app.run(debug=True)

"""
Routes and views for the flask application.
"""

from ast import Str, Try, dump
import base64
from bz2 import decompress
import datetime
from decimal import Decimal
import decimal
from doctest import debug
from fileinput import filename
import gzip
from http import client
import ipaddress
import json
from logging import raiseExceptions
import mmap
from msilib import UuidCreate
from operator import itemgetter
import os
import os.path
from pathlib import Path
import signal
import mimetypes
import hashlib
import secrets
import socket
import sqlite3
from sys import exception
import threading
from token import STAR
from traceback import print_tb
from urllib.parse import urlparse
import http.client


from uuid import UUID
import uuid
from wsgiref import headers
from wsgiref.simple_server import server_version
from click import DateTime
from cryptography.hazmat.primitives.asymmetric import padding

from flask.sansio.scaffold import F
from flask_socketio import SocketIO, emit, send
import requests
import psutil
from smb.SMBConnection import SMBConnection
from sqlalchemy import false, try_cast,func
# from zeroconf import ServiceBrowser, ServiceListener, ServiceInfo, Zeroconf
from asyncio.windows_events import NULL
from pickle import FALSE, GET
from sqlite3 import DateFromTicks, Timestamp
from ssl import ALERT_DESCRIPTION_BAD_CERTIFICATE_STATUS_RESPONSE
from types import MethodType
from urllib import response
from urllib.request import HTTPBasicAuthHandler
from warnings import catch_warnings
from flask import (
    Response,
    config,
    flash,
    make_response,
    redirect,
    render_template,
    send_from_directory,
    session,
    sessions,
    url_for,
)

from FlaskWebProject3 import app, notifications
from flask import abort
from time import sleep, time
from flask import Request, jsonify, request, render_template, send_file
from flask_cors import CORS
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from functools import wraps
from flask import Flask, stream_with_context
import sys
import subprocess
import asyncio
# import aiohttp

# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import MEDIA_MIME_TYPE_PARAMETER_DEFAULT_VALUE, build
# from googleapiclient.errors import HttpError

#from threading import Thread
from FlaskWebProject3.cm.cm import CredentialManager
#import WinNTP
from WinNTP.sync_time import set_time_zone_and_enable_windows_time_sync
import awd
import azd
from gd.GDClient import GDClient
#from module2 import create_database
from module2 import restore_child, restore_parent
import onedrive
from runserver import check_license_runserver

from sqlite_managerA import SQLiteManager #, RowWrapper

# from .socketio import sktio
from FlaskWebProject3 import sktio

GD_DATA_BLOCK=b"E241BD06-0A09-45BC-8D4D-222E364BC14A"

# from flask_session import Session
# app.secret_key = "quickbrownfox"
# # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
active_sessions = {}
# user = {
#     "user@gmail.com": {"loginemail": "user@gmail.com", "password": "123456"},
#     "user1@gmail.com": {"loginemail": "user1@gmail.com", "password": "123456"},
# }

# user = {'loginemail': 'user1@gmail.com', 'password': '123456'}
backupprofilescoll = []
client_backups = {}
client_backups_data_lock = threading.Lock()
CLIENT_BACKUPS_DATA_FILE = "backupdata.json"
clientnodes_x = {
    # "250.250.250.250": {
    #     "ipAddress": "250.250.250.250:7777",
    #     "lastConnected": 1709709502.23656,
    #     "ksey": "",
    # },
}
# clientnodes = [{"ipAddress": "250.250.250.250:7777"}]
clientnodes = []
clientnodes2x = []
# cors = CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True)
cors = CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

TARGET="http://127.0.0.1:5000"
HOP_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'transfer-encoding', 'upgrade',"content-length",
}

blicfound =False

from decimal import Decimal

def D(value):
    if isinstance(value, Decimal):
        return value
    elif isinstance(value, (int, str)):
        return Decimal(value)
    elif isinstance(value, float):
        return Decimal(str(value))
    else:
        raise TypeError(f"Unsupported type: {type(value)}")

from functools import lru_cache
@lru_cache(maxsize=1)
def get_current_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 7777))
        ip_address = s.getsockname()[0]
        #hostname = socket.gethostname()
        s.close()

        return ip_address
    except socket.gaierror as e:
        print(f"Error getting IP address: {e}")
        return None
##kartik
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
import sys
def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = json.loads(get_jwt_identity())
            print("JWT Identity:", identity, file=sys.stdout, flush=True)
            user_role = str(identity.get("role", "")).lower()

            if user_role not in [r.lower() for r in allowed_roles]:
                return jsonify({"error": "Access denied. Invalid role."}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def permission_required(*required_permissions):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = json.loads(get_jwt_identity())
            print("JWT Identity:", identity, file=sys.stdout, flush=True)
            role = str(identity.get("role", "")).lower()

            # Admins bypass permission checks
            if role == "admin":
                return fn(*args, **kwargs)

            privileges = identity.get("privileges", {}) or {}

            for perm in required_permissions:
                if privileges.get(perm) is True:
                    return fn(*args, **kwargs)

            return jsonify({
                "error": f"Permission denied. Required one of: {', '.join(required_permissions)}"
            }), 403

        return wrapper
    return decorator
##kartik
##kartik
import logging
import logging.handlers
import sys
from FlaskWebProject3.structured_logging import log_event, log_chunk_event, ensure_job_id

# Create a logs folder if it doesn't exist
os.makedirs("every_logs", exist_ok=True)

LOG_FILE = "every_logs/server_view.log"

# Create the main logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define a detailed log format
detailed_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s:%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
)

# --- 1 File handler ---
file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_format)

# --- 2 Console handler ---
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(detailed_format)

# Add file + console handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --- 3 Windows Event Viewer handler ---
try:
    event_handler = logging.handlers.NTEventLogHandler(appname="ABS")
    event_handler.setLevel(logging.DEBUG)
    event_formatter = logging.Formatter(
        "[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    event_handler.setFormatter(event_formatter)
    logger.addHandler(event_handler)
except Exception as e:
    logger.warning(f"Could not attach Windows Event Viewer handler: {e}")

##kartik
@app.before_request
def check_and_redirect():
    # Check if the requested endpoint is 'home' (or any other endpoint)

    #app.config["blicfound"]= True
    blicfound = app.config.get("blicfound",False)
    # app.config["blicfound"]= True
    # blicfound = app.config.get("blicfound",False)
    from flask import Request, jsonify, request, render_template, send_file,url_for
    
    print(f"ENDPOiNT CALLED {request.endpoint} lic {blicfound} URL: {request.host_url}")        
    
    if False: #request.endpoint in['handshake_get','handshake_confirm']:
        pass
    else:
    
        if not blicfound:
            if not request.endpoint in['register','v1234','l1234','login','static','stats','serve_static','serve_react_app', 'handshake','handshake_get','handshake_confirm','forward','assets']:
                # Redirect to a different route if the endpoint matches
                # return url_for("serve_react_app", _anchor='team', _external=True)
                return url_for("serve_react_app")#,  _external=True)
            else:
                pass
                #return url_for("serve_react_app",path='324asdfewr')
            
        # else:
        #     print(request.endpoint)
        
    

# # @app.before_request
# # def check_and_redirect():
# #     # Check if the requested endpoint is 'home' (or any other endpoint)
     
# #     if not request.endpoint in['v1234','l1234','login','serve_static','serve_react_app']:
# #         # Redirect to a different route if the endpoint matches
# #         return serve_react_app("/")

def getConn(repo_d={},keyx=None):
    from .unc import EncryptedFileSystem, NetworkShare
    from .cm import CredentialManager
    ns =NetworkShare(repo_d["ipc"], "", repo_d["uid"], repo_d["idn"])
    if ns.test_connection():
        try:
            ns.disconnect()
        except:
            pass

        try:
            return EncryptedFileSystem(
                repo_d["ipc"], repo_d["uid"], repo_d["idn"], repo_d["loc"]
            )
        except:
            return None
    else:
        u, p = CredentialManager(repo_d["ipc"],keyx=keyx).retrieve_credentials(repo_d["ipc"])
        if not u or not p:
            return None
        else:
            try:
                if not (NetworkShare(repo_d["ipc"], "", u, p).test_connection()):
                    return None

                return EncryptedFileSystem(repo_d["ipc"], u, p, repo_d["loc"])

            except Exception as de:
                return None


@app.route('/key', methods=['POST', 'GET'])
@app.route('/sync', methods=['POST', 'GET'])
@app.route('/savewidget', methods=['POST', 'GET'])
@app.route('/logout', methods=['POST', 'GET'])
@app.route('/planupgrade', methods=['POST', 'GET'])
@app.route('/requestotpwmail', methods=['POST', 'GET'])
@app.route('/otpverifywemail', methods=['POST', 'GET'])
@app.route('/otp-verify', methods=['POST'])
@app.route('/support', methods=['POST', 'GET'])
@app.route('/adduser', methods=['POST', 'GET'])
@app.route('/pair', methods=['POST'])
@app.route('/get-records', methods=['POST', 'GET'])
@app.route('/dststorage', methods=['POST', 'GET'])
@app.route('/notification', methods=['POST', 'GET'])
@app.route('/change-password', methods=['POST', 'GET'])
@app.route('/mailsmtp', methods=['POST', 'GET'])
@app.route('/tokencheck', methods=['POST', 'GET'])
@app.route('/reset-password', methods=['POST', 'GET'])
@app.route('/requestotp', methods=['POST', 'GET'])
@app.route('/updateuser', methods=['POST', 'GET'])
@app.route('/deleteuser', methods=['POST', 'GET'])
@app.route('/reset-password', methods=['POST', 'GET'])
@app.route('/keys/<key_id>', methods=['POST', 'GET'])
@app.route('/eventnotifications/clear', methods=['DELETE'])
@app.route('/eventnotifications/<int:notification_id>', methods=['DELETE'])
@app.route('/eventnotifications/<int:notification_id>/read', methods=['PATCH'])
@app.route('/eventnotifications', methods=['GET'])
@app.route('/eventnotifications', methods=['POST'])
@app.route('/eventlogs', methods=['GET'])
@app.route('/eventlogs', methods=['POST'])
@app.route('/refresh', methods=['POST'])
def forward(key_id=None , notification_id=None , token=None):
    path = request.path
    parsed = urlparse(f"{TARGET}{path}")
    if parsed.path in ["/pair","/sync"]:
        print(key_id)

    output_result = []
    if parsed.path in ["/dststorage"]:
        data = request.json or {}
        if 'action' in data and data['action'] == 'repo_check':
            return validate_credentials_clouds() 
        elif 'action' in data and data['action'] == 'list_repo_check':
            for repos in data['rep']:
                res_data = validate_credentials_clouds(repos)
                json_output = res_data[0].json
                output_result.append({repos:json_output['valid']})
            return jsonify({"repo_list":output_result}),200

    if parsed.path in ["/tokencheck"]:
        print(f"{key_id},{notification_id}, {token}")
    path = parsed.path or '/'
    if request.query_string:
        path += '?' + request.query_string.decode()

    conn_cls = http.client.HTTPSConnection if parsed.scheme == 'https' else http.client.HTTPConnection
    conn = conn_cls(parsed.hostname, parsed.port or 5000)


    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_HEADERS and k.lower() != 'host'
    }
    print(headers)

    try:
        request_data = request.get_data(cache=False)
        conn.request(
            method=request.method,
            url=f"{TARGET}{path}",
            body=request_data,  # raw streaming
            headers=headers
        )
        resp = conn.getresponse()


        response_data = resp.read()

        response_headers = {
            k: v for k, v in resp.getheaders()
            if k.lower() not in HOP_HEADERS
        }
        print("==============================================================================================")
        print(request_data)
        print("==============================================================================================")
        print (response_data)
        print("==============================================================================================")
        if parsed.path in ["/pair","/sync"]:
            print("key_id")
        return Response(response=response_data,status=resp.status,headers=response_headers)
    except Exception as e:
        print('Error in view', str(e))
    finally:
        conn.close()
##kartik
def search_endpoint_bykey():
    key = []
    fetched_online_ids = set()
    for e in app.config["agent_activation_keys"]:
        x= search_clientnodes_x_nodes(e)
        if x:
            key.append(x["key"])
            fetched_online_ids.add(x["key"])

    from .jobdata import JobsRecordManager
    m=JobsRecordManager("records.db", "records.json",app=app) 
    try:
        endp = m.fetch_nodes_as_json()
        m.close()
        for e in json.loads(endp):
            node_id = e["idx"]
            if node_id in  app.config["agent_activation_keys"]:
                if node_id in fetched_online_ids:
                    continue
                key.append(e["idx"])
    except:
        pass
    return key


@app.route('/validate_cred', methods=['POST'])
def validate_credentials_clouds(repos=None):
    data = request.json or {}
    
    if repos:
        data['rep'] = repos

    # Validate required field
    if 'rep' not in data:
        return jsonify({"error": "key not found"}), 400

    key = str(data['rep']).upper()

    if key in ['AWSS3', 'AWS']:
        from awd.AWSClient import S3Client
        check_result = S3Client.validate_aws_credentials()

    elif key == 'AZURE':
        from azd.AzureClient import AzureBlobClient
        check_result = AzureBlobClient.validate_azure_credentials()  
    
    elif key == 'ONEDRIVE':
        from onedrive.OneDriveClient import OneDriveClient
        check_result = OneDriveClient.validate_onedrive_credentials()

    elif key == 'GDRIVE':
        from gd.GDClient import gd_test
        check_result = gd_test()
        
    #send email and whatsApp 
    if check_result:
        return jsonify({"valid": bool(check_result)}), 200
    else:
        try:
            request_notification = requests.post('http://127.0.0.1:53335/api/sendtoserver', json={"event": "cred_failed", "rep":key})  
        except: 
            pass
        return jsonify({"valid": bool(check_result)}), 200
    return jsonify({"error": "unsupported key"}), 400

import base64
import hashlib
from flask import send_file
def encrypt_data(enc_key,data):
    from cryptography.fernet import Fernet
    hash_key = hashlib.sha256(enc_key.encode()).digest()
    key = base64.urlsafe_b64encode(hash_key[:32])
    cipher = Fernet(key)
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(enc_key,data):
    from cryptography.fernet import Fernet
    hash_key = hashlib.sha256(enc_key.encode()).digest()
    key = base64.urlsafe_b64encode(hash_key[:32])
    cipher = Fernet(key)
    return cipher.decrypt(data.encode()).decode()

def save_credentials(service,enc_key, credentials):
    encrypted = encrypt_data(enc_key,json.dumps(credentials))
    if not os.path.exists("keys"):
        os.makedirs("keys")
    file_path = os.path.join("keys", f"{service}_{enc_key}_credentials.enc")
    with open(file_path, "w") as file:
        file.write(encrypted)
        file.flush()
    with open(file_path, "r") as file:
        file.seek(0)
        print(decrypt_data(enc_key,file.read()))

@app.route('/download_cred', methods=['POST'])
def download_cred():
    data = request.json or {}
    if 'rep' not in data:
        return jsonify({"error": "key not found"}), 400

    key = str(data['rep']).upper()
    enc_key = str(data['key'])
    
    if key == 'AWSS3':
        from awd.AWSClient import S3Client
        res= S3Client.send_endpoint_credentials(encrypt_key=enc_key)
        return send_file(
            os.path.join(app.config['location'],res),
            as_attachment=True,
            conditional=True  )

    elif key == 'AZURE':
        from azd.AzureClient import AzureBlobClient
        res= AzureBlobClient.send_endpoint_credentials(encrypt_key=enc_key)  
        return send_file(
                os.path.join(app.config['location'],res),
                as_attachment=True,
                conditional=True  )
    
    elif key == 'ONEDRIVE':
        from onedrive.OneDriveClient import OneDriveClient
        res= OneDriveClient.send_endpoint_credentials(encrypt_key=enc_key)
        return send_file(
                    os.path.join(app.config['location'],res),
                    as_attachment=True,
                    conditional=True  )

    elif key == 'GDRIVE':
        from gd.GDClient import GDClient
        res = GDClient.send_endpoint_credentials()
        # file_path = "token.pickle"
        # return send_file(
        #     file_path,
        #     as_attachment=True,
        #     conditional=True  
        # )
        return send_file(
                os.path.join(app.config['location'],res),
                as_attachment=True,
                conditional=True  )

    # save_credentials(key,enc_key, check_result)
    # file_path = os.path.join("keys", f"{key}_{enc_key}_credentials.enc")
    # return send_file(
    #     file_path,
    #     as_attachment=True,
    #     conditional=True  
    # )

def run_backup_files():
    from .jobdata import JobsRecordManager
    m=JobsRecordManager("records.db", "records.json",app=app)
    # m.create_backup()
    # m.get_data_bkp_file()
    # m.close()

    resj=None
    try:
        resj = app.config.get("getRequestKey")
        b =  resj.get('application',None)==None
        b = b or resj.get('activationkey',None)==None
        if b : 
            return {"status":"failed", "reason":"Unknown endpoint"}, 500
    except:
        return {"status":"failed", "reason":"Unknown endpoint"}, 500

    if not resj:
        return {"status":"failed", "reason":"Unknown endpoint"}, 500

    
    headers = {
        "Accepted-Encoding": "gzip,deflate,br",
        "Content-Type": "application/json",
        "application": "",
        "server": "",
    }
    try:
        headers["application"]= resj['application']
    except:
        return {"status":"failed", "reason":"Unknown endpoint"}, 500

    try:
        headers["server"]= resj['activationkey']
    except:
        return {"status":"failed", "reason":"Unknown endpoint"}, 500

    import glob
    data = ['tokenSpecs.db', 'AWS_credentials.enc','Azure_credentials.enc']
    x = search_endpoint_bykey()
    print(x)
    for key in x:
        pattern = glob.glob(f"*{key}*.*")
        for add_data in pattern:
            data.append(add_data)
    
    print(f"check is there anything in database and data {data}")
    m.get_data_bkp_file(source_db=data)
    m.close()
    backup_dir = "backup_dir"
    matched_files = glob.glob(f'{backup_dir}/*')  
    full_paths = [os.path.abspath(f) for f in matched_files]  
    file_path = {"file_path": full_paths}
    # data.append(file_path)
    zip_name = f'{str(app.config.get("getCode"))}.zip'
    zip_path = os.path.abspath(zip_name)
    file_name = {"file_name": zip_path, **file_path}
    data = json.dumps(file_name)
    # print(f"data is passing now {data}")
    print(f"path {file_path}")

    upload_zip_parallel(full_paths, zip_name)

    try: 
        request = requests.post('http://127.0.0.1:5000/upload', data=data, headers=headers)
    except Exception as e:
        print(f"There is an error {str(e)}")

    if request.status_code == 200:
        print("logs are uploading")
        return {"status":"success"}, 200
    else:
        return {"status":"failed"}, 500

@app.route('/backupfiles', methods=['POST'])
def backup_files():
    result, status_code = run_backup_files()
    return jsonify(result), status_code

def backup_files_job():
    with app.app_context():
        result, status_code = run_backup_files()
        return result, status_code

def read_file(file_path):
    print(f"file_path {file_path}")
    with open(file_path, "rb") as f:
        return file_path, f.read();

import zipfile
from concurrent.futures import ThreadPoolExecutor
def upload_zip_parallel(file_paths, zip_name = "latest_agent_files.zip"):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(read_file, file_paths))
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file_path, data in results:
            arcname = os.path.basename(file_path)
            zipf.writestr(arcname, data)

from apscheduler.schedulers.background import BackgroundScheduler
import atexit
scheduler = BackgroundScheduler()
scheduler.add_job(backup_files_job, 'interval', hours=2, id='logs_backups')
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def extract_zip(zip_path):
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"{zip_path} is not a valid zip file.")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(".")
        print(f"Extracted {zip_path} to current directory.")
        return zip_ref.namelist()

@app.route('/download_file',methods=['POST'])
def download_log_files():
    import glob
    import shutil
    resj=None
    try:
        resj = app.config.get("getRequestKey")
        b =  resj.get('application',None)==None
        b = b or resj.get('activationkey',None)==None
        if b : 
            return jsonify({"status":"failed", "reason":"Unknown endpoint"}), 500
    except:
        return jsonify({"status":"failed", "reason":"Unknown endpoint"}), 500

    if not resj:
        return jsonify({"status":"failed", "reason":"Unknown endpoint"}), 500

    
    headers = {
        "Accepted-Encoding": "gzip,deflate,br",
        "Content-Type": "application/json",
        "application": "",
        "server": "",
    }
    try:
        headers["application"]= resj['application']
    except:
        return jsonify({"status":"failed", "reason":"Unknown endpoint"}), 500

    try:
        headers["server"]= resj['activationkey']
    except:
        return jsonify({"status":"failed", "reason":"Unknown endpoint"}), 500

    try: 
        request = requests.post('http://127.0.0.1:5000/getdata', data={}, headers=headers)
    except Exception as e:
        print(f"There is an error {str(e)}")
    response_Data = request.json()
    print(f"response data {response_Data}")
    main_file = Path(response_Data['file_name'])
    x = search_endpoint_bykey()
    # data = [r"7c3eb001aa90c597e790f0468db1e0416a89089266e5d1dbc018bac5aa8a306a.db_1758608125.9655383.kdb",
    #         r"1bb9ca3b9c0093e804a65018258e426910943e6050bda554a6ba404ec63eb998.db_1758608125.9655383.kdb",
    #         ]
    extract_zip(response_Data['file_name'])
    # os.remove(response_Data['file_name'])
    data = None
    # for key in x:
    #     pattern = glob.glob(f"*{key}*.kdb")
    #     data = pattern
    pattern = glob.glob(f"*.kdb")
    data = pattern
    for pattern in data:
        print(pattern)
        p = Path(pattern)
        while p.suffix:
            p = p.with_suffix('')
        base_name = str(p)
        print(f"print base name {base_name}")
        # if "_" in base_name:
        #     base_name = base_name.rsplit("_", 1)[0]
        if os.path.exists(pattern):
            if base_name in ['AWS_credentials','Azure_credentials']:
                decompressed_file =f"{base_name}.enc"
                # decompressed_file = f'{key}.db'
                with gzip.open(pattern, 'rb') as f_in:
                    with open(decompressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                if not str(main_file.with_suffix('')) == str(app.config.get("getCode")):
                    if base_name == str(main_file.with_suffix('')):
                        decompressed_file =f'{str(app.config.get("getCode"))}.db'
                        # decompressed_file = f'{key}.db'
                        with gzip.open(pattern, 'rb') as f_in:
                            with open(decompressed_file, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    else:
                        decompressed_file =f"{base_name}.db"
                        # decompressed_file = f'{key}.db'
                        with gzip.open(pattern, 'rb') as f_in:
                            with open(decompressed_file, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                else:
                    decompressed_file =f"{base_name}.db"
                    # decompressed_file = f'{key}.db'
                    with gzip.open(pattern, 'rb') as f_in:
                        with open(decompressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
        os.remove(pattern)

    if request.status_code == 200:
        print("logs are uploading")
        return jsonify({"status":"success"}),200
    else:
        return jsonify({"status":"failed"}),500
##kartik

@app.route('/eventnotifications/stream', methods=['GET'])
def forward_sse():
    path = request.path
    parsed = urlparse(f"{TARGET}{path}")
    path = parsed.path or '/'
    if request.query_string:
        path += '?' + request.query_string.decode()

    conn_cls = http.client.HTTPSConnection if parsed.scheme == 'https' else http.client.HTTPConnection
    conn = conn_cls(parsed.hostname, parsed.port or 5000)


    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_HEADERS and k.lower() != 'host'
    }
    
    request_data = request.get_data(cache=False)
    conn.request(
        method=request.method,
        url=f"{TARGET}{path}",
        body=request_data,  # raw streaming
        headers=headers
    )
    resp = conn.getresponse()

    def generate():
        while True:
            chunk = resp.readline()
            if not chunk:
                break
            yield f"{chunk.decode('utf-8')}\n"

    response_headers = {
        k: v for k, v in resp.getheaders()
        if k.lower() not in HOP_HEADERS
    }

    return Response(stream_with_context(generate()),status=resp.status,headers=response_headers,content_type='text/event-stream')


def redirect_all(): 
    # import logging
    # logging.basicConfig(
    #     level=logging.DEBUG,format='%(asctime)s [%(levelname)s] %(message)s'
    #     )
    # logger = logging.getLogger("REDR")

    try:

        path = request.path
        query = request.query_string.decode()
        target_url = f"{TARGET}{path}"
        print(f'print target url {target_url}')
        if query:
            target_url += f"?{query}"
        #logger.info(f"Redirecting {request.method} to: {target_url}")
        print(f"Redirecting {request.method} to: {target_url}")
        return redirect(target_url, code=307)
    except Exception as e:
        #logger.error(f'printing error in redirect {str(e)}')
        print(f'printing error in redirect {str(e)}')
        return {"error": "Internal Server Error"}, 500

@app.route('/keysssssssssssssssssss/<key_id>', methods=['POST', 'GET'])
def redirect_keyid(key_id):
    try:
        path = request.path
        query = request.query_string.decode()
        target_url = f"{TARGET}{path}"
        print(f'print target url {target_url}')
        if query:
            target_url += f"?{query}"
        #logger.info(f"Redirecting {request.method} to: {target_url}")
        print(f"Redirecting {request.method} to: {target_url}")

        return redirect(target_url, code=307)
    except Exception as e:
        #logger.error(f'printing error in redirect {str(e)}')
        print(f'printing error in redirect {str(e)}')
        return {"error": "Internal Server Error"}, 500


@app.route("/v1234", methods=["POST"])
def v1234():
    # from flask import make_response

    # from runserver import check_license_runserver, brdcst,save_response
    # print("====dddddddddddddd============================")
    # print(request.headers.get("allagents","missing all agents" ))
    # print("=====ddddddddddddddd===========================")
    # blicfound=false
    # if request.headers.get("allagents",None):
    #     resp = make_response()
    #     resp.headers["allagents"]=request.headers.get("allagents",[])
    #     #save_response(resp)
    #     blicfound=check_license_runserver(None,0)
    # app.config["blicfound"]=blicfound
    # if blicfound: brdcst(app.config["port"])        
    return {"status":blicfound},200

def search_client_nodes(search_value):
    for i, obj in enumerate(clientnodes):
        if (
            str(obj.get("ipAddress")).lower() == str(search_value).lower()
            or str(obj.get("agent")).lower() == str(search_value).lower()
        ):
            return obj
    return {"ipAddress": "", "agent": ""}  # Return -1 if not found

def search_clientnodes_x_nodes(search_value):
    for i, obj in enumerate(clientnodes_x):
        obj= clientnodes_x[str(obj)]
        if (
            obj.get("agent").lower() == str(search_value).lower()
            or str(obj.get("ipAddress")).lower() == str(search_value).lower()
            or str(obj.get("key")).lower() == str(search_value).lower()
        ):
            # clientnodes_x[obj.get('ipAddress')].get("key")
            return obj
    return None
def search_clientnodes_x_nodeList(search_value,search_value1,search_value2,):
    nodes=[]
    for i, obj in enumerate(clientnodes_x):
        obj= clientnodes_x[str(obj)]
        if (
            obj.get("agent").lower() == str(search_value).lower()
            or str(obj.get("ipAddress")).lower() == str(search_value).lower()
            or str(obj.get("key")).lower() == str(search_value).lower()
            
            or obj.get("agent").lower() == str(search_value1).lower()
            or str(obj.get("ipAddress")).lower() == str(search_value1).lower()
            or str(obj.get("key")).lower() == str(search_value1).lower()
            
            or obj.get("agent").lower() == str(search_value2).lower()
            or str(obj.get("ipAddress")).lower() == str(search_value2).lower()
            or str(obj.get("key")).lower() == str(search_value2).lower()
        ):
            # clientnodes_x[obj.get('ipAddress')].get("key")
            if obj not in nodes:
                nodes.append( obj)

    try:
        nodes = list(set(nodes))
    except:
        print("")
    return nodes

def search_clientX_nodes(search_value):
    for i, obj in enumerate(clientnodes):
        if (
            obj.get("ipAddress").lower() == str(search_value).lower()
            or str(obj.get("agent")).lower() == str(search_value).lower()
        ):
            # clientnodes_x[obj.get('ipAddress')].get("key")
            return clientnodes_x[obj.get("ipAddress")]
    return {"ipAddress": "", "agent": ""}  # Return -1 if not found


def load_backup_data(file):
    try:
        with open(CLIENT_BACKUPS_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_backup_data(data, file=None):
    with open(CLIENT_BACKUPS_DATA_FILE, "w") as file:
        json.dump(data, file)


def lic_required(f):
    @wraps(f)
    def fns(*args, **kwargs):
        from datetime import datetime
        try:
            session_id = request.authorization.token
            if session_id in active_sessions:
                jsd = active_sessions[session_id]
                try:
                    x = datetime.now().timestamp() - jsd["validtill"]
                except:
                    x = time() - jsd["validtill"]

                if x > (60 * 10):
                    active_sessions.pop(session_id)
                    return jsonify({"error": "Unauthorized"}), 401
                else:
                    return f(*args, **kwargs)
            else:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": "invalid Request"}), 500
        # return f(*args, **kwargs)

    return fns

def auth_required(f):
    @wraps(f)
    def fns(*args, **kwargs):
        from datetime import datetime 
        try:
            session_id = request.authorization.token
            if session_id in active_sessions:
                jsd = active_sessions[session_id]
                try:
                    x = datetime.now().timestamp() - jsd["validtill"]
                except:
                    x = time() - jsd["validtill"]

                if x > (60 * 10):
                    active_sessions.pop(session_id)
                    return jsonify({"error": "Unauthorized"}), 401
                else:
                    return f(*args, **kwargs)
            else:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": "invalid Request"}), 500
        # return f(*args, **kwargs)

    return fns

####################
import json
import os
import tempfile

CLIENTNODES_FILE = "clientnodes.json"


def load_clientnodes_x():
    if not os.path.exists(CLIENTNODES_FILE):
        return {}
    with open(CLIENTNODES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_clientnodes_x(clientnodes_x):
    directory = os.path.dirname(CLIENTNODES_FILE) or "."

    fd, tmp_path = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(clientnodes_x, f, indent=2)

        os.replace(tmp_path, CLIENTNODES_FILE)

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def update_clientnodes(clientnodes_x, clientnodes, clientnodes2x, new_node):
    if not clientnodes_x:
        clientnodes_x.update(load_clientnodes_x())
    new_client_node_key = new_node["key"]
    new_client_node = new_node["ipAddress"]
    new_client_node_Agent = new_node["agent"]
    new_input_password = new_node['lastConnected']
    new_client_node_ip = new_node["ip"]
    new_client_node_data = new_node["data"]
    new_input_password_time = new_node['lastConnectedTime']

    ##kartik
    old_ip = None
    for ip, node in clientnodes_x.items():
        if node["key"] == new_client_node_key:
            old_ip = ip
            break

    # remove old IP if key is same but IP changed
    if old_ip and old_ip != new_client_node:
        del clientnodes_x[old_ip]
    ##kartik

    existing_node = clientnodes_x.get(new_client_node)
    # existing_node = search_clientnodes_x_nodes(new_client_node_key)

    #if not existing_node:
        # existing_node = search_clientnodes_x_nodes(new_client_node)
        # while existing_node:
        #     try:
        #         del clientnodes_x[existing_node['ipAddress']]
        #     except Exception as dw:
        #             print(str(dw))
        #     existing_node = search_clientnodes_x_nodes(new_client_node)
        
        # existing_node = search_clientnodes_x_nodes(new_client_node_Agent)
        # while existing_node:
        #     try:
        #         del clientnodes_x[existing_node['ipAddress']]
        #     except Exception as dw:
        #             print(str(dw))
        #     existing_node = search_clientnodes_x_nodes(new_client_node_Agent)

    if existing_node:
        # If node exists, check if the key is the same and update if necessary
        if existing_node["key"] == new_client_node_key:
            clientnodes_x[new_client_node] = {
                "key": new_client_node_key,
                "ipAddress": new_client_node,
                "agent": new_client_node_Agent,
                "lastConnected": new_input_password,
                "ip":new_client_node_ip ,
                "data":new_client_node_data,
                "lastConnectedTime":new_input_password_time,
            }
        else:
            # Remove old node since we have conflicting keys (the new node's key is different)
            del clientnodes_x[new_client_node]
            # Add the new node
            clientnodes_x[new_client_node] = {
                "key": new_client_node_key,
                "ipAddress": new_client_node,
                "agent": new_client_node_Agent,
                "lastConnected": new_input_password,
                "ip":new_client_node_ip ,
                "data":new_client_node_data,
                "lastConnectedTime":new_input_password_time,
            }
    else:
        # If no existing node, add the new node
        clientnodes_x[new_client_node] = {
            "key": new_client_node_key,
            "ipAddress": new_client_node,
            "agent": new_client_node_Agent,
            "lastConnected": new_input_password,
            "ip":new_client_node_ip ,
            "data":new_client_node_data,
            "lastConnectedTime":new_input_password_time,
        }


    # Update clientnodes and clientnodes2x
    try:
        clientnodes_x=clientnodes_x
    except:
        print("")
    save_clientnodes_x(clientnodes_x)
    update_clientnodes_list(clientnodes_x, clientnodes, clientnodes2x)

def update_clientnodes_list(clientnodes_x, clientnodes, clientnodes2x):
    clientnodes[:] = [{"ipAddress": value["ipAddress"], "agent": value["agent"]} for value in clientnodes_x.values()]
    clientnodes2x[:] = [
            {"ipAddress": value["ipAddress"], 
             "agent": value["agent"], 
             "lastConnected": value["lastConnected"],
             "lastConnectedTime": value["lastConnectedTime"],
             "ip": value["ip"] ,
             "data": value["data"]} 
        for value in clientnodes_x.values()]
    try:
        clientnodes2x=list(set(clientnodes2x))
    except:
        print("Asdf")


@app.route("/tellme", methods=["GET", "POST"])
def tellme_handler(): 
    x =tellme()
    try:
        return x
    except:
        print("")

def tellme():
    request_json=None
    try:
        request_json= request.json
    except:
        try:
            request_json= request.event['args'][1]
        except:
            print("")
    if not request_json:
        try:
            request_json= request.event['args'][1]
        except:
            print("")
    if not request_json:
        return

    isRoaming=False
    ipstring =request.remote_addr
    clientnodes2X=None
    if request.method == "POST" or request.full_path.startswith(r"/socket.io"):
        client_report={}
        try:
            client_report=json.loads(request.headers.get("tccrep","{}"))
            if client_report.get('ip_addresses',None):
                isRoaming=ipstring !=client_report.get('ip_addresses',ipstring)
                ipstring = f"{ipstring}/{client_report.get('ip_addresses',None)}"
        except:
            client_report={}
        file_path=""
        if file_path == "":
            file_path = os.path.join(
                os.path.dirname(app.root_path), "downloads", "Client20032020_1751.exe"
            )

        if not os.path.exists(file_path) or client_report=={}:
            print(jsonify({"reason":"update file doesnot exist"}))
            return(jsonify({"reason":"update file doesnot exist"}),500)

        try:
            import win32api
            info = win32api.GetFileVersionInfo(file_path, "\\")
            version = f"{info['FileVersionMS'] >> 16}.{info['FileVersionMS'] & 0xffff}.{info['FileVersionLS'] >> 16}.{info['FileVersionLS'] & 0xffff}"
            version_s = (
                info["FileVersionMS"]
                + info["FileVersionMS"]
                + info["FileVersionLS"]
                + info["FileVersionLS"]
            )
            versionrequest = request_json.get("version",version)
            # if version_s > req_data["version_s"]:
            bUpdateProceed = 0!=compare_versions(version1=version,version2=versionrequest)
            if bUpdateProceed:
                print(jsonify({"reason":"Endpoint is not updated"}))
                return(jsonify({"reason":"Endpoint is not updated"}),500)

        except:
            print("")

        client_node = request.remote_addr + ":7777"
        #client_node = "http://" + (request.json)["IP"] + ":7777"
        client_node = "http://" + request.remote_addr + ":7777"
        client_node_key = request_json["key"]
        client_node_Agent = request_json["IP"]
        if  (client_node_key  in app.config["agent_activation_keys"]):
            print("found")
        else:
            #delete it from  collection
            return "400", 400
        # try:
        #     from FlaskWebProject3 import notifications

        #     notifications.put(client_node)
        # except Exception as ere:
        #     print(str(ere))
        
        try:
            print(clientnodes_x)
        except:
            pass
        input_password = time()
        import pytz
        ist_timezone = pytz.timezone("Asia/Kolkata")
        input_password_time = datetime.datetime.fromtimestamp(input_password, ist_timezone).strftime("%d/%m/%Y, %I:%M:%S %p")

        input_password = str(input_password)

        # try:
        #     requests.post(
        #         request.url_root + "create_database",
        #         json={"database_name": client_node_key},
        #     )
        # except:
        #     print("")

        # if client_node in clientnodes_x:
        #     clientnodes_x.__setitem__(
        #         client_node,
        #         {
        #             "ipAddress": client_node,
        #             "agent": client_node_Agent,
        #             "lastConnected": input_password,
        #             "key": client_node_key,
        #         },
        #     )
        # else:
        #     clientnodes_x.__setitem__(
        #         client_node,
                # {
                #     "ipAddress": client_node,
                #     "agent": client_node_Agent,
                #     "lastConnected": input_password,
                #     "key": client_node_key,
                # },
        #     )
        
        update_clientnodes(clientnodes_x
            ,clientnodes
            ,clientnodes2x, 
            {"ipAddress": client_node,
            "agent": client_node_Agent,
            "lastConnected": input_password,
            "lastConnectedTime": input_password_time,
            "key": client_node_key,
            "ip":ipstring,#"ip":request.remote_addr
            "isRoaming":isRoaming,
            "data":client_report
            }
        )
        # if {"ipAddress": client_node, "agent": client_node_Agent} in clientnodes:
        #     print("")
        # else:
        #     clientnodes.append({"ipAddress": client_node, "agent": client_node_Agent})
        #     clientnodes2x.append(
        #         {
        #             "ipAddress": client_node,
        #             "agent": client_node_Agent,
        #             "lastConnected": input_password,
        #         }
        #     )

        condition = {
            "ipAddress": client_node,
            "agent": client_node_Agent,
            "lastConnected": input_password,
            "lastConnectedTime": input_password_time,
            "key": client_node_key,
            "ip":request.remote_addr,
            "data":client_report
        }

        clientnodes2X_ = [
            (
                {
                    **item,
                    "lastConnected": condition["lastConnected"],
                    "lastConnectedTime": input_password_time,
                }
                if (
                    (condition["ipAddress"] is None
                    or item["ipAddress"] == condition["ipAddress"]
                    ) and client_node in app.config["agent_activation_keys"]
                )
                and (condition["agent"] is None or item["agent"] == condition["agent"])
                else item
            )
            for item in clientnodes2x
        ]
        try:
            clientnodes2X_ = list(set(clientnodes2X_))
        except:
            print ("")
        clientnodes2X = clientnodes2X_
    
    data=None
    try:
        data = clientnodes2X
    except:
        print("ASDF")
    if data:
        return (jsonify(result=data), 200)
    else:
        return (jsonify(result={}), 500)

def save_loging_response():
    blicfound=False
    import json,base64,gzip
    
    dagent=app.config.get("admin_login",{})
    d = app.config.get("AppFolders", None).site_config_dir
    if type(dagent) is dict:
        dagent=json.dumps(dagent)
        dagent = base64.b64encode(dagent.encode("UTF-8")).hex("-", 4)
        
    if not Path(d).exists():
        try:
            os.makedirs(d, exist_ok=True)
        except:
            print("")
            d = ""

    from builtins import open as fileopen
    d = os.path.join(d, f"lapo.opal")
    with fileopen(d, "wb") as encrypted_file:
        encrypted_file.write(dagent.encode("UTF-8"))
        encrypted_file.close()
   
def load_login_response():
    import json,base64,gzip
    d = app.config.get("AppFolders", None).site_config_dir
    if not d:
        print("0000000000===  Invalid site_config_dir  ========0000000000000000000")
        return None

    file_path = os.path.join(d, "lapo.opal")

    if Path(file_path).exists():
        file_lock = threading.Lock()
        with file_lock:
            with open(file_path, "rb") as encrypted_file:
                encoded_data = encrypted_file.read().decode("UTF-8")
                
                # Decode hex and base64
                try:
                    decoded_data = bytes.fromhex(encoded_data.replace("-", "")).decode("UTF-8")
                    dagent = json.loads(base64.b64decode(decoded_data).decode("UTF-8"))
                    app.config["admin_login"] = dagent
                    return True
                except Exception as e:
                    print(f"Error decoding data: {e}")
                    app.config["admin_login"] =None
                    return False
    else:
        print("0000000000===  Data file not found  ========0000000000000000000")
        return False


@app.route("/login", methods=["POST", "GET"])
def login():
    
    payload={"email":"","password":""}
    resj=""
    # if app.config.get("resj",None):
    #     resj = app.config.get("resj")["server"]
    if app.config.get("getRequestKey",None):
        resj = app.config.get("getRequestKey")
    
    if request.method == "POST":
        if request.mimetype == "application/json":
            #payload=request.get_json()
            payload["email"]= request.json.get("email","")
            payload["password"]= request.json.get("password","")
            payload["'"]= payload.get("password","") ##kartik
            headers = {
                "Accepted-Encoding": "gzip,deflate,br",
                "Content-Type": "application/json",
                "loginipname": request.remote_addr,
                "loginipusername": "",
                "IPname": "",
                "application": "",
                "server": "",
            }
            try:
                headers["IPname"]= resj['IPname']
            except:
                pass

            try:
                headers["application"]= resj['application']
            except:
                pass

            try:
                headers["server"]= resj['activationkey']
            except:
                pass
            try:
                headers["loginipname"]= request.remote_addr
            except:
                pass
            # try:
            #     headers["loginipname"]= request.remote_user
            # except:
            #     pass

            from flask import jsonify, Response,make_response
            res=requests.post("http://"+str(get_current_ip())+":5000/login",json=payload,headers=headers)
            #res= jsonify({"t":"Tr"},200)
            print(str(res))
            sanitized_headers = {k: v for k, v in res.headers.items() if k.lower() not in ["content-length", "transfer-encoding", "connection"]}
            if res.status_code ==200:
                if not app.config.get("admin_login",None):
                    a_j= res.json()
                    if type(a_j) is dict:
                        if a_j.get("data",None):
                            if a_j.get("data").get("role",None):
                                if str(a_j.get("data").get("role")).lower()=="admin":
                                    a_j["creds"]=payload
                                    app.config["admin_login"]= a_j
                                    save_loging_response()
                                    #keep admin creds for later use 
                                    #if any of the users is not able to login actively 
            try:
                # return Response(res.content, status=res.status_code, headers=sanitized_headers)
                return Response(res.content, status=res.status_code, headers=dict(res.headers))
            except:
                return "A"
            
        
    #return 
    #     # if request.mimetype == "application/json":
    #     #     # jsond = jsonify( request.data)
    #     #     # input_username = jsond['loginemail']
    #     #     # input_password = jsond['password']
    #     #     print("errr")
    #     # else:
    #     input_username = request.form["loginemail"]
    #     input_password = request.form["password"]

    #     # if input_username == user['username'] and input_password == user['password']:
    #     #     session['username'] = input_username
    #     #     flash('Logged in successfully!', 'success')
    #     #     return #redirect(url_for('dashboard'))
    #     # else:
    #     #     flash('Invalid username or password', 'error')
    #     # return #render_template('login.html')
    #     if input_username in user:
    #         if (
    #             input_username == user[input_username]["loginemail"]
    #             and input_password == user[input_username]["password"]
    #         ):
    #             # session['username'] = input_username
    #             # session.permanent = True
    #             # session.modified = True
    #             # Generate a secure session ID
    #             session_id = secrets.token_hex(16)

    #             # Store the session ID in the active_sessions dictionary
    #             active_sessions[session_id] = {
    #                 "user": input_username,
    #                 "validtill": datetime.datetime.now().timestamp(),
    #             }

    #             # Set the session cookie
    #             response = make_response(
    #                 jsonify({"Authorization": "Bearer " + session_id})
    #             )
    #             # response.set_cookie('session_id', session_id)
    #             # response.headers.add("Authorization",session_id)
    #             response.headers.add(
    #                 "Set-Cookie",
    #                 f"session_id={session_id}; Secure, SameSite=None; Path=/;",
    #             )
    #             response.headers.add(
    #                 "Set-Cookie",
    #                 f"Authorization={session_id}; Secure, SameSite=None; Path=/;",
    #             )

    #             return response  # jsonify({'status': 'success', 'message': 'Logged in successfully'})
    #         else:
    #             return (
    #                 jsonify(
    #                     {"status": "error", "message": "Invalid username or password"}
    #                 ),
    #                 401,
    #             )
    #     else:
    #         return (
    #             jsonify({"status": "error", "message": "Invalid username or password"}),
    #             401,
    #         )

    # else:
    #     try:
    #         redirect(location="/", code=307)
    #     except Exception as des:
    #         print(str(des))

    #     # if request.method == "GET":
    #     #     return render_template(
    #     #         "Login.html",
    #     #         title="Home Page",
    #     #         year=datetime.now().year,
    #     #     )
    #     # else:
    #     #     return (
    #     #         jsonify({"status": "error", "message": "Invalid username or password"}),
    #     #         401,
    #     #     )

    #     # return (
    #     #     jsonify({"status": "error", "message": "Invalid username or password"}),
    #     #     401,
    #     # )

@app.route("/restister", methods=["POST"])
def register():
    dagent=app.config.get("agent_activation_keys",[])
    if request.method == "POST":
        j=None
        try:
            import base64,gzip
            import fingerprint
            
            tcc = request.headers.get("tcc",None)
            if tcc:
                # tcc = [tcc[i : i + 9][:8] for i in range(0, len(tcc), 9)]
                # tcc = "".join(tcc)
                # tcc = bytes.fromhex(tcc)
                # tcc = base64.b64decode(tcc) 
                # tcc = tcc.decode("UTF-8")
                #tcc2 =tcc.hex("-", 8)
                tcc = base64.b64decode(tcc)
                #tcc = gzip.decompress(tcc)
                tcc = tcc.decode("UTF-8")
                tcc = base64.b64encode(tcc.encode("UTF-8"),).hex("-", 8)
                j= request.json.get("activationkey",None)
                if not j==tcc: return ({"res":"invalid request"},500)
                if j:
                    j = base64.b64decode(bytes.fromhex(j.replace('-', ''))).decode("UTF-8")
                    from runserver import check_license_runserver
                    x= check_license_runserver(None,2)
                    if True: #not (j in app.config.get("agent_activation_keys",[])):
                        headers = {
                            "Accepted-Encoding": "gzip,deflate,br",
                            "Content-Type": "application/json",
                            "tcc": base64.b64encode(
                                gzip.compress(
                                    str(app.config.get("getCode",None)).encode("UTF-8"),
                                    9,
                                )
                            ),
                        }
                        server_act_key = app.config.get('getRequestKey',None)
                        app.config['getRequestKey']['activationkey']
                        json_data=request.json 
                        if server_act_key:
                            server_act_key = server_act_key.get('activationkey',None)
                            if server_act_key:
                                json_data.update({'sak': server_act_key})
                        res = requests.post(
                            "http://127.0.0.1:5000/activationrequest", #"http://192.168.2.23:8000/api/v1/agent-activation/",  # "http://192.168.2.25:8000/activationrequest/",
                            json=json_data,
                            headers=headers,
                            timeout=5000,
                        )
                        if res.ok or res.status_code == 429:
                            from runserver import check_license_runserver
                            import re
                            from pathlib import Path
                            d=""
                            if res.json().get("status",None):
                                print("Hold here")
                            if app.config.get("AppFolders", None):     
                                d = app.config.get("AppFolders", None).site_config_dir
                            if not Path(d).exists():
                                try:
                                    os.makedirs(d, exist_ok=True)
                                except:
                                    print("")
                                    d = ""
            
                            resj =  json.dumps(res.headers["allagents"]) #res.text
                            resj = re.sub(r"'(?P<key>\w+?)':", r'\"\g<key>\":', resj)  # For keys
                            resj = re.sub(r":\s*'(?P<value>[^']*?)'", r':\"\g<value>\"', resj)  # For values
                            resj = re.sub(r',\s*([\]}])', r'\1', resj)
                            resj= json.loads(resj)
                                                           
                            if type(resj) is str:
                                resj= json.loads(resj)
                            if type(resj) is dict:
                                #app.config["agent_activation_keys"]= resj.get("Endpoints",[]) 
                                for dd in resj.get("Endpoints", []):
                                    try:
                                        dagent.append(base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8"))
                                    except Exception as dwdw:
                                        print(str(dwdw))
                                 
                                resj= json.dumps(resj)

                            dagent=list(set(dagent))
                            app.config["agent_activation_keys"] = dagent
                    
                            resj = base64.b64encode(resj.encode("UTF-8")).hex("-", 4)
                            d = os.path.join(d, f"{d}.lic")
                            file_lock = threading.Lock()
                            from builtins import open as fileopen
                            with file_lock:
                                with fileopen(d, "wb") as encrypted_file:
                                    encrypted_file.write(resj.encode("UTF-8"))
                                    encrypted_file.close()
                            blicfound= check_license_runserver(None,2)
                            app.config["blicfound"]=blicfound
                            print("")

                        if res.headers.get("allagents",None):
                            sres = make_response(res.json())
                            sres.headers["XServer"]=json_data.get("activationkey","")
                            sres.headers["allagents"]=res.headers.get("allagents","")

                            sktio.emit(
                                "message",
                                {
                                    #"message": str(app.config.get("getCodeHost",None)) +" has been paired with server" 
                                    "message": str(json_data.get("iPname","an endpoint")) +" is paired with server" 
                                },
                            )
                            return sres

                        m_j = {
                            "agent": str(app.config.get("getCodeHost",None)),
                            "idx":str(app.config.get("getCode",None)),
                            "event":"pairingrequest",
                            "job_id":str(""),
                            "job_name":str(""),
                            "error_desc":str(""),
                            "missed_time":str("")
                        }
                        res = requests.post(
                            "http://127.0.0.1:53335/api/sendtoserver",  # "http://192.168.2.25:5000/activationrequest", #"http://192.168.2.23:8000/api/v1/agent-activation/",  # "http://192.168.2.25:8000/activationrequest/",
                            json=m_j,
                            #headers=headers,
                            timeout=5000,
                        )
                        sktio.emit(
                            "message",
                            {
                                #"message": "pairing requested by " +str(app.config.get("getCodeHost",None))
                                "message": "pairing has been requested to " +str(app.config.get("getCodeHost",None)) +" by " + str(json_data.get("iPname","an endpoint")) +" is paired with server" 
                            },
                        )

                        return jsonify({"reason":"paired waiting"},500)

                        
        except Exception  as see:
            print(str(see))
            return jsonify({"reason":str(see)},500)
    else:
        try:
            redirect(location="/", code=307)
        except Exception as des:
            print(str(des))
# Serve static assets directly by Flask
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder + "/static", filename)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>",methods=["GET","POST"])
def serve_react_app(path):

    state = request.args.get("state")
    code = request.args.get("code")
    scope = request.args.get("scope")
    authuser = request.args.get("authuser")
    prompt = request.args.get("prompt")

    if state:
        # Process the state parameter as needed
        return jsonify({"state": state})

    if path != "" and (path.startswith("static") or path.startswith("assets")):
        return send_from_directory(app.static_folder, path)
    elif path == "":
        return send_from_directory(app.static_folder, "index.html")
    else:
        # Root-level assets (e.g. /logo192.png, /Abl.ico) or SPA client routes
        full_path = os.path.join(app.static_folder, path)
        if os.path.isfile(full_path) and os.path.realpath(full_path).startswith(os.path.realpath(app.static_folder)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")


@app.route("/authen")
@auth_required
def authen():
    return "200", 200


@app.route("/serverreport")
def serverreport():
    server_act_date =""
    server_version = app.config.get("Version","n/a")
    server_id = app.config.get("getCode","n/a")
    connected_client_node_data= None
    try:
        connected_client_node_data = client_nodes().get_json()
    except:
        connected_client_node_data= None
        print("")
    try:
        import pytz
        server_act_date= float(app.config['resj']['server']['activationDate3'])
        date_format = "%d/%m/%Y, %I:%M:%S %p"
        p = pytz.timezone("Asia/Kolkata")
        import datetime;
        server_act_date = datetime.datetime.fromtimestamp(server_act_date).replace(tzinfo=p).strftime(date_format)

    except:
        server_act_date ="n/a"
    from FlaskWebProject3 import ServerSystemReportGenerator
    report_generator = ServerSystemReportGenerator(app=app,computer_id=server_id, server_version=server_version, server_activation_date=server_act_date,server_connected_nodes=connected_client_node_data)
    report_generator.generate_report()
    print(json.dumps( report_generator.get_report_data(),indent=10))
    return jsonify(report_generator.get_report_data()), 200


@app.route("/echo")
def echo():
    return "200", 200


@app.route("/restart", methods=["POST"])
def restart_server():
    import os
    import sys
    import subprocess
    try:
        exe_path = sys.executable
        subprocess.Popen([exe_path] + sys.argv)
        return jsonify({"status": "success", "message": "Server restart initiated."}), 200
        os._exit(0)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/terminate", methods=["POST"])
def terminate_server():
    try:
        os.kill(os.getpid(), signal.SIGTERM)
        return (
            jsonify({"status": "success", "message": "Server termination initiated."}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



def search_idin_backupprofilescoll(coll, searchdata):
    # coll[:] = [obj for obj in coll if not any(str(searchdata).lower() in str(value).lower() for value in obj.values())]
    coll[:] = [
        obj
        for obj in coll
        if str(searchdata).lower() not in obj.get("backupProfileId", "").lower()
    ]


@app.route("/scheduler/action/reschedule", methods=["POST"])
@role_required('admin','employee') ##kartik
@permission_required('agentUpdate')
def Schedulers_Actions_Reschedule():

    rdata = request.json
    if not rdata: return (jsonify({"result":"payload error" }),500)
    
    next_time=None
    allowed_days=None
    action_info = rdata.get("action",None)
    jobid=action_info.get("jobId",None)
    action=action_info.get("action",None)
    agentName = action_info.get("agent",None)
    runEveryUnit = rdata.get("runEveryUnit",None)
    runAgainEvery = rdata.get("runAgainEvery",None)

    obj = search_client_nodes(str(agentName))
    selected_agent_ip = obj.get("ipAddress")
    c = clientnodes_x[obj.get("ipAddress")].get("key")

    ip = None
    if action: action = str(action).lower()
    if jobid: jobid = str(jobid).lower()
    if agentName: agentName = str(agentName).lower()
    if selected_agent_ip: 
        ip = str(selected_agent_ip).lower()
    selected_agent_ip = str(selected_agent_ip).lower()
    if c: c = str(c).lower()

    if action =="reschedule":
        try:  
            #ip="http://192.192.192.192:7777"
            if ip and jobid:
                url = str(f'{ip}/scheduler/jobreschedule')
                response = requests.post(url,json=rdata, timeout=200)
                if response.status_code == 200 or response.status_code == 204:
                    return (jsonify(response.json()),200)
        except Exception as exs:
            print(exs)

            sid = app.config["WSClients"].get(c,None)
            if not sid:
                return #(
                    #jsonify(
                    #    {"allowed_hosts": ["*"],"current_host": "None","running": False,}),200,
                    #)
            request_id = str(uuid.uuid4())
            event = threading.Event()
            result_holder = {}

            app.config["pending_requests"][request_id] = (event, result_holder)

            sktio.emit('scheduler_action_reschedule_response', {
                "key": c,
                "request_id": request_id,
                # "jobid":jobid,
                # "agentName" :agentName,
                # #"action" :action,
                # "next_time":None,
                # "allowed_days":None,
                # "action_info":action_info ,
                # "jobid":jobid,
                # #"action":action,
                # "agentName":agentName,
                # "runEveryUnit":runEveryUnit,
                # "runAgainEvery": runAgainEvery ,
                "rdata":rdata
            }, to=sid)

            if event.wait(timeout=300):
                data = result_holder.get("scheduler_action_reschedule_response", {})
                combined_response=data.get("combined_response",None)
                return jsonify(combined_response.get("response_content","nodata"),combined_response.get("response_code",500))
            else:
                print(f"[Fallback Timeout] No response for request_id: {request_id}")
    
    return 500
       



@app.route("/scheduler/action", methods=["POST","DELETE"])
@role_required('admin','employee') ##kartik
@permission_required('agentDelete','agentDelete','agentPause')
def Schedulers_Actions():
    rdata = request.json
    if not rdata: return (jsonify({"result":"payload error" }),500)

    jobid=rdata.get("jobId",None)
    agentName = rdata.get("agentName",None)
    action = rdata.get("action",None)
    jobNewName = rdata.get("jobNewName",None)

    obj = search_client_nodes(str(agentName))
    selected_agent_ip = obj.get("ipAddress")
    c = clientnodes_x[obj.get("ipAddress")].get("key")

    ip = None
    if action: action = str(action).lower()
    if jobid: jobid = str(jobid).lower()
    if agentName: agentName = str(agentName).lower()
    if selected_agent_ip: 
        ip = str(selected_agent_ip).lower()
    selected_agent_ip = str(selected_agent_ip).lower()
    if c: c = str(c).lower()

    ip="http://127.0.0.1:7777"
    bTry=True
    # if action =="delete":
    #     if request.method in ["DELETE"]:
    #         try:  
    #             if ip and jobid:
    #                 url = str(f'{ip}/scheduler/{c}/jobs/{jobid}')
    #                 print("ip")
    #                 response = requests.delete(url, timeout=20)
    #                 if response.status_code == 200 or response.status_code == 204:
    #                     print("Job has been deleted")
    #                     return (response.content,200)
    #         except Exception as exs:
    #             print(exs)
    #             bTry=True

    # elif action =="play":
    #     try:  
    #         if ip and jobid:
    #             url = str(f'{ip}/scheduler/{c}/jobs/{jobid}/resume')
    #             print("ip")
    #             response = requests.post(url, timeout=20)
    #             if response.status_code == 200 or response.status_code == 204:
    #                 return (response.content,200)
    #     except Exception as exs:
    #         print(exs)
    #         bTry=True
    # elif action =="pause":
    #     try:  
    #         if ip and jobid:
    #             url = str(f'{ip}/scheduler/{c}/jobs/{jobid}/pause')
    #             print("ip")
    #             response = requests.post(url, timeout=20)
    #             if response.status_code == 200 or response.status_code == 204:
    #                 return (response.content,200)
    #     except Exception as exs:
    #         print(exs)
    #         bTry=True
    # elif action =="rename":
    #     try:  
    #         if ip and jobid:
    #             url = str(f'{ip}/scheduler/jobrename')
    #             print("ip")
    #             response = requests.post(url,json={"job_id":jobid,"new_job_name":jobNewName}, timeout=20)
    #             if response.status_code == 200 or response.status_code == 204:
    #                 return (response.content,200)
    #     except Exception as exs:
    #         print(exs)
    #         bTry=True
    # elif action =="reschedule":
    #     pass
    response_content={"success":"Error"}
    response_code=500 
    if bTry:
        sid = app.config["WSClients"].get(c,None)
        if not sid:
            return #(
                #jsonify(
                #    {"allowed_hosts": ["*"],"current_host": "None","running": False,}),200,
                #)
        request_id = str(uuid.uuid4())
        event = threading.Event()
        result_holder = {}

        app.config["pending_requests"][request_id] = (event, result_holder)

        sktio.emit('scheduler_action_response', {
            "key": c,
            "request_id": request_id,
            "jobid":jobid,
            "agentName" :agentName,
            "action" :action,
            "jobNewName":jobNewName,
        }, to=sid)
        response_content={"success":"Error"}
        response_code=500 
        if event.wait(timeout=60):
            data = result_holder.get("scheduler_action_response", {})
            combined_response=data.get("combined_response",None)
            if data.get("combined_response",None):
                response_content=combined_response.get("response_content",{"success":"Error"})
                response_code=combined_response.get("response_code",500) 
        else:
            print(f"[Fallback Timeout] No response for request_id: {request_id}")
    if isinstance(response_content, bytes):
        response_content = response_content.decode('utf-8').strip()
        if response_content:  # not empty
            try:
                response_content = json.loads(response_content)
            except json.JSONDecodeError:
                # Not valid JSON; return as plain text
                response_content = {'raw': response_content}
    return jsonify(response_content),response_code #(response_content,response_code)

# @app.route("/scheduler", methods=["GET", "POST","DELETE"])
# # @auth_required
# @role_required('admin','employee') ##kartik
# @permission_required('agentRead')
# def GetSchedulers_Jobs():
#     ip = ""    
#     fields_to_extract = ['src_location','repo','day_of_week', 'hour', 'id', 'minute', 'name', 'next_run_time', 'second']
#     combined_response=None
#     if request.method in ["GET","POST"]:

#         try:
#             rdata = request.json
#             if rdata:
#                 try:
#                     if rdata["ip"]:
#                         ip = rdata["ip"]
#                         rdata["ip"]=str(rdata["ip"]).replace("http","jiii")
#                         url = str(
#                             f'{rdata["ip"]}/scheduler/{clientnodes_x[rdata["ip"]].get("key")}'
#                         )
#                         url2 = str(
#                             f'{rdata["ip"]}/scheduler/{clientnodes_x[rdata["ip"]].get("key")}/jobs'
#                         )
#                         print(rdata["ip"])
#                         response = requests.get(url, timeout=20)
#                         response2 = requests.get(url2, timeout=20)
#                         data=response2.json()
#                         # Function to filter data based on the selected fields
#                         filtered_data = [
#                             {key: entry[key] for key in fields_to_extract if key in entry}
#                             for entry in data
#                         ]
#                         if response.status_code == 200 and response2.status_code == 200:
#                             # Combine responses into a third variable
#                             combined_response = {
#                                 "scheduler": response.json(),
#                                 "jobs": filtered_data ,
#                             }
#                         #else:

                            

#                         print(combined_response)
#                         return (combined_response, 200)
#                 except Exception as eas:
#                     print(str(eas))
#                     rdata["ip"]=str(rdata["ip"]).replace("jiii","http")
#                     sid = app.config["WSClients"].get(clientnodes_x[rdata["ip"]].get("key"),None)
#                     if not sid:
#                         return (
#                             jsonify(
#                                 {"allowed_hosts": ["*"],"current_host": "None","running": False,}),200,
#                             )
#                     request_id = str(uuid.uuid4())
#                     event = threading.Event()
#                     result_holder = {}

#                     app.config["pending_requests"][request_id] = (event, result_holder)

#                     sktio.emit('scheduler_response', {
#                         "key": clientnodes_x[rdata["ip"]].get("key"),
#                         "request_id": request_id
#                     }, to=sid)

#                     if event.wait(timeout=300):
#                         data = result_holder.get("scheduler_response", {})
#                         combined_response=data.get("combined_response",{
#                             "allowed_hosts": ["*"],
#                             "current_host": "None",
#                             "running": False,
#                         })
#                     else:
#                         print(f"[Fallback Timeout] No response for request_id: {request_id}")

#                     return combined_response

#                     # return (
#                     #     jsonify(
#                     #         {
#                     #             "allowed_hosts": ["*"],
#                     #             "current_host": "None",
#                     #             "running": False,
#                     #         }
#                     #     ),
#                     #     200,
#                     #)
#         except Exception as exs:
#             print(exs)

#         return (
#             jsonify({"allowed_hosts": ["*"], "current_host": "None", "running": False}),
#             200,
#         )
    
@app.route("/scheduler", methods=["GET", "POST","DELETE"])
# @auth_required
@role_required('admin','employee') ##kartik
@permission_required('agentRead')
def GetSchedulers_Jobs():
    try:
        rdata = request.json
        rdata["ip"]=rdata["ip"]
        sid = app.config["WSClients"].get(clientnodes_x[rdata["ip"]].get("key"),None)
        if not sid:
            return (
                jsonify(
                    {"allowed_hosts": ["*"],"current_host": "None","running": False,}),200,
                )
        request_id = str(uuid.uuid4())
        event = threading.Event()
        result_holder = {}

        app.config["pending_requests"][request_id] = (event, result_holder)
        a = clientnodes_x[rdata["ip"]].get("key")
        print(f"Dddddddddddddddddddddddddddddddddddddddd {a}  dddd {request_id}")
        sktio.emit('scheduler_response', {
            "key": clientnodes_x[rdata["ip"]].get("key"),
            "request_id": request_id
        }, to=sid)

        if event.wait(timeout=300):
            data = result_holder.get("scheduler_response", {})
            combined_response=data.get("combined_response",{
                "allowed_hosts": ["*"],
                "current_host": "None",
                "running": False,
            })
        else:
            print(f"[Fallback Timeout] No response for request_id: {request_id}")

        return jsonify(combined_response)
    except Exception as exs:
            print(exs)

    return (
        jsonify({"allowed_hosts": ["*"], "current_host": "None", "running": False}),
        200,
    )
 

@app.route("/schedulera", methods=["GET", "POST"])
# @auth_required
def GetSchedulers():
    ip = ""
    
    try:
        rdata = request.json
        if rdata:
            try:
                if rdata["ip"]:
                    ip = rdata["ip"]
                    url = str(
                        f'{rdata["ip"]}/scheduler/{clientnodes_x[rdata["ip"]].get("key")}'
                    )
                    print(rdata["ip"])
                    response = requests.get(url, timeout=20)

                    print(response.content)
                    return (response.content, 200)
            except Exception as eas:
                print(str(eas))
                return (
                    jsonify(
                        {
                            "allowed_hosts": ["*"],
                            "current_host": "None",
                            "running": False,
                        }
                    ),
                    200,
                )
    except Exception as exs:
        print(exs)

    return (
        jsonify({"allowed_hosts": ["*"], "current_host": "None", "running": False}),
        200,
    )


@app.route("/scheduler/jobs", methods=["GET", "POST"])
# @auth_required
def GetScheduledJobonNodes():
    try:
        rdata = request.json
        if rdata:
            try:
                if rdata["ip"]:
                    ip = rdata["ip"]
                    url = str(
                        f'{rdata["ip"]}/scheduler/{clientnodes_x[rdata["ip"]].get("key")}/jobs'
                    )
                    print(rdata["ip"])
                    response = requests.get(url, timeout=20)
                    # return (jsonify(response.text), 200)
                    fields_to_extract = ['src_location','repo','day_of_week', 'hour', 'id', 'minute', 'name', 'next_run_time', 'second']
                    data=response.json()
                    # Function to filter data based on the selected fields
                    filtered_data = [
                        {key: entry[key] for key in fields_to_extract if key in entry}
                        for entry in data
                    ]
                    return ((filtered_data), 200)
            except Exception as eas:
                print(str(eas))
    except Exception as exs:
        print(exs)

    return (jsonify({}), 500)


@app.route("/backupprofilescreate", methods=["POST"])
# @auth_required
@role_required('admin', 'employee')  ##kartik
@permission_required('backupReadWrite')
def backupprofilescreate():

    try:
        set_time_zone_and_enable_windows_time_sync()
    except:
        pass

    requestData = request.json

    print("========8333===========================================")
    print(str(request.json))
    print("========8333===========================================")
    selectedStorageTYP =""
    selectedStorageIPC =""
    selectedStorageUID = ""
    selectedStorageIDN = ""
    selectedStorageLOC = ""
    try:
        selectedStorageType = request.json.get("storageType", "LAN")
        selectedStorageTypeJSON = request.json.get(
            "deststorageType",
            {"typ": "LAN", "ipc": "", "uid": "", "idn": "", "loc": ""},
        )
        if not selectedStorageTypeJSON:
           selectedStorageTypeJSON ={"typ": "LAN", "ipc": "", "uid": "", "idn": "", "loc": ""}
        selectedStorageTYP = selectedStorageTypeJSON.get("typ", "LAN")
        selectedStorageIPC = selectedStorageTypeJSON.get("ipc", "")
        selectedStorageUID = selectedStorageTypeJSON.get("uid", "")
        selectedStorageIDN = selectedStorageTypeJSON.get("idn", "")
        selectedStorageLOC = selectedStorageTypeJSON.get("loc", "")
    except:
        print("")

    try:
        from FlaskWebProject3.cm import CredentialManager
        from FlaskWebProject3.unc import NetworkShare

        # if NetworkShare(
        #     selectedStorageIPC, "", selectedStorageUID, selectedStorageIDN
        # ).test_connection():
        #     u, p = CredentialManager(selectedStorageIPC).retrieve_credentials(
        #         selectedStorageIPC
        #     )
        #     if not u or not p:
        #         CredentialManager(selectedStorageIPC).store_credentials(
        #             selectedStorageIPC, selectedStorageUID, selectedStorageIDN
        #         )
        #     else:
        #         try:
        #             if not (
        #                 NetworkShare(selectedStorageIPC, "", u, p).test_connection()
        #             ):
        #                 CredentialManager(selectedStorageIPC).delete_credentials(
        #                     selectedStorageIPC
        #                 )
        #                 CredentialManager(selectedStorageIPC).store_credentials(
        #                     selectedStorageIPC, selectedStorageUID, selectedStorageIDN
        #                 )
        #         except Exception as de:
        #             print(str(de))

        CredentialManager(selectedStorageIPC).delete_credentials(
            selectedStorageIPC
        )
        CredentialManager(selectedStorageIPC).store_credentials(
            selectedStorageIPC, selectedStorageUID, selectedStorageIDN
        )
    except Exception as dfe:
        print(str(dfe))
    res =None
    try:
        if requestData.get("backupProfileId",None):
            # search_idin_backupprofilescoll(
            #     backupprofilescoll, requestData["backupProfileId"]
            # )
            backupprofilescoll.append(requestData)
            if requestData.get("selectedSystems",None):
                # if requestData["schedulenow"]== True:
                for kk in requestData["selectedSystems"]:
                    try:

                        obj = search_client_nodes(kk)
                        selectedAgent = obj.get("ipAddress")
                        c = clientnodes_x[obj.get("ipAddress")].get("key")

                        try:

                            # if not os.path.exists(
                            #     os.path.join(app.config["location"], f"{c}.db")
                            # ):
                            # Capture values before thread (request context is lost in thread)
                            url_root = request.url_root
                            db_path = os.path.join(
                                app.config["location"], f"{c}.db"
                            )
                            def create_db_task():
                                requests.post(
                                    url_root + "create_database",
                                    json={"database_name": db_path},
                                )
                            threading.Thread(
                                target=create_db_task,
                                daemon=True,
                            ).start()

                        except Exception:
                            print("")
                            pass

                        # c =  clientnodes_x[str(kk.replace('http://','')).replace('https://','').replace(':7777','')].get('key')
                        # c = clientnodes_x[str(kk)].get("key")

                        data = {
                            # "id": f"{c}_{requestData['backupProfileId']}_{str(time())}",
                            "id": f"{c}_{requestData['backupProfileId']}",
                            "func": "__main__:show_me",
                            "trigger": "interval",
                            "seconds": 600,
                            "misfire_grace_time": 2 * 24 * 60 * 60,
                            "next_run_time": "1924-03-16T15:58:49.271128+05:30",
                            "start_date": "1924-03-14T17:40:34.271128+05:30",
                        }
                        # res = requests.post(
                        #     f"{selectedAgent}/backupprofilescreate",
                        #     json=requestData,
                        #     timeout=200,
                        # )
                        request_id = str(uuid.uuid4())
                        event = threading.Event()
                        result_holder = {}
                        app.config["pending_requests"][request_id] = (event, result_holder)
                        requestData["request_id"]=request_id
                        requestData["key"]=c #clientnodes_x[c].get("key"),                        
                        sktio.emit("backupprofilescreate",requestData,to= app.config['WSClients'].get(c))

                        if event.wait(timeout=300):
                            data = result_holder.get("backupprofilescreate_response", {})
                            combined_response=data.get("combined_response",None)

                            from .jobdata import JobsRecordManager
                            # m=JobsRecordManager("records.db", "records.json",app=app )
                            # try:
                                    
                            #     #m.add_records(res.json().get('data'))
                            #     m.add_records(combined_response[0])
                            #     n = 5  # Change this value as needed
                            #     top_n_grouped_records = m.get_top_n_grouped_records(n)
                            #     print(f"Top {n} grouped records:", top_n_grouped_records)
                            # except Exception as da:
                            #     print(str(da))
                            # finally:
                            #     m.close()
                            x=c
                            m=JobsRecordManager(f"{x}.db", "records.json",app=app)
                            try:
                                #m.add_records(res.json().get('data'))
                                m.add_records(combined_response[0])
                                n = 5  # Change this value as needed
                                top_n_grouped_records = m.get_top_n_grouped_records(n)
                                print(f"Top {n} grouped records:", top_n_grouped_records)
                            except Exception as da:
                                print(str(da))
                            finally:
                                m.close()

                            #return jsonify(combined_response.get("response_content","nodata"),combined_response.get("response_code",500))
                        else:
                            print(f"[Fallback Timeout] No response for request_id: {request_id}")
    

                        #sktio.emit("show_me",requestData,to= app.config['WSClients'].get(c))

                        #if not res.ok:
                            #send_websocket_createbackup_here
                        '''
                        if res.ok:
                            if res.status_code == 200:
                                from .jobdata import JobsRecordManager
                                m=JobsRecordManager("records.db", "records.json",app=app )
                                try:
                                    
                                    m.add_records(res.json().get('data'))
                                    n = 5  # Change this value as needed
                                    top_n_grouped_records = m.get_top_n_grouped_records(n)
                                    print(f"Top {n} grouped records:", top_n_grouped_records)
                                except Exception as da:
                                    print(str(da))
                                finally:
                                    m.close()
                                x=clientnodes_x[obj.get("ipAddress")].get("key")
                                m=JobsRecordManager(f"{x}.db", "records.json",app=app)
                                try:
                                    m.add_records(res.json().get('data'))
                                    n = 5  # Change this value as needed
                                    top_n_grouped_records = m.get_top_n_grouped_records(n)
                                    print(f"Top {n} grouped records:", top_n_grouped_records)
                                except Exception as da:
                                    print(str(da))
                                finally:
                                    m.close()
                        '''        
                        # requests.post(f"{kk}/scheduler/{c}/jobs", json=data)
                    except Exception as e:
                        print(str(e))
                        #return ("500", 500)
            
            # try:
            #     threading.Thread(
            #         target=app.add_url_rule(
            #             f"{c}/upload",
            #             f"{c}/upload",
            #             upload_file,
            #         )
            #     ).start()
            # except:
            #     print("")
            # try:
            #     threading.Thread(
            #         target=app.add_url_rule(
            #             f"{c}/uploadunc",
            #             f"{c}/uploadunc",
            #             upload_file_unc,
            #         )
            #     ).start()
            # except:
            #     print("")

            return ("200", 200)
        else:
            requestData["backupProfileId"] = UuidCreate()
            backupprofilescoll.append(requestData)
            return (request.json, 200)
    except:
        # return "Invalid Data",500
        return request.json, 500


@app.route("/backupprofiles", methods=["POST", "GET"])
# @auth_required
def backupprofiles():
    data = backupprofilescoll
    return jsonify(result=data)
    # return jsonify({'result': [{'backupProfileId': p.title, 'author': p.author} for p in profies]})


# @app.route('/backupjobs',methods=['GET', 'POST'])
@app.route("/backupjobs", methods=["GET"])
@auth_required
def backup_jobs():
    session_id = request.cookies.get("session_id")
    """Renders the contact page."""
    data = [
        {
            "computer": "192.268.22.54",
            "date": "21//10//2023",
            "id": "1",
            "profile": "Backup1",
            "time": "13:30",
        },
        {
            "computer": "192.268.2.54",
            "date": "22//10//2023",
            "id": "2",
            "profile": "Backup1",
            "time": "13:30",
        },
        {
            "computer": "192.168.78.123",
            "date": "22//10//2023",
            "id": "3",
            "profile": "Backup4",
            "time": "15:30",
        },
        {
            "computer": "192.168.12.54",
            "date": "21//10//2023",
            "id": "4",
            "profile": "Backup6",
            "time": "13:30",
        },
        {
            "computer": "192.168.25.154",
            "date": "22//10//2023",
            "id": "5",
            "profile": "Backup13",
            "time": "13:30",
        },
        {
            "computer": "192.168.45.223",
            "date": "26//10//2023",
            "id": "6",
            "profile": "Backup34",
            "time": "15:30",
        },
        {
            "computer": "192.268.25.154",
            "date": "26//10//2023",
            "id": "7",
            "profile": "Backup13",
            "time": "13:30",
        },
        {
            "computer": "192.168.45.223",
            "date": "27//10//2023",
            "id": "8",
            "profile": "Backup34",
            "time": "15:30",
        },
        {
            "computer": "192.168.2.54",
            "date": "21//10//2023",
            "id": "9",
            "profile": "Backup1",
            "time": "13:30",
        },
        {
            "computer": "192.168.2.154",
            "date": "22//10//2023",
            "id": "10",
            "profile": "Backup1",
            "time": "13:30",
        },
        {
            "computer": "192.268.78.123",
            "date": "22//10//2023",
            "id": "11",
            "profile": "Backup4",
            "time": "15:30",
        },
        {
            "computer": "192.168.12.254",
            "date": "25//11//2023",
            "id": "12",
            "profile": "Backup6",
            "time": "13:30",
        },
        {
            "computer": "192.168.25.154",
            "date": "12//11//2023",
            "id": "13",
            "profile": "Backup13",
            "time": "13:30",
        },
        {
            "computer": "192.168.45.223",
            "date": "26//11//2023",
            "id": "14",
            "profile": "Backup34",
            "time": "15:30",
        },
        {
            "computer": "192.268.25.154",
            "date": "26//11//2023",
            "id": "15",
            "profile": "Backup13",
            "time": "13:30",
        },
        {
            "computer": "192.168.45.223",
            "date": "27//11//2023",
            "id": "16",
            "profile": "Backup34",
            "time": "15:30",
        },
        {
            "computer": "192.268.25.154",
            "date": "22//10//2023",
            "id": "17",
            "profile": "Backup13",
            "time": "13:30",
        },
        {
            "computer": "192.168.45.223",
            "date": "26//10//2023",
            "id": "18",
            "profile": "Backup34",
            "time": "15:30",
        },
        {
            "computer": "192.168.209.154",
            "date": "26//10//2023",
            "id": "19",
            "profile": "Backup13",
            "time": "13:30",
        },
        {
            "computer": "192.268.145.223",
            "date": "27//10//2023",
            "id": "20",
            "profile": "Backup34",
            "time": "15:30",
        },
        {
            "computer": "192.168.201.254",
            "date": "21//10//2023",
            "id": "21",
            "profile": "Backup1",
            "time": "13:30",
        },
        {
            "computer": "192.168.2.154",
            "date": "22//10//2023",
            "id": "22",
            "profile": "Backup1",
            "time": "13:30",
        },
        {
            "computer": "192.168.178.123",
            "date": "22//10//2023",
            "id": "23",
            "profile": "Backup4",
            "time": "15:30",
        },
        {
            "computer": "192.168.312.54",
            "date": "25//11//2023",
            "id": "24",
            "profile": "Backup6",
            "time": "13:30",
        },
        {
            "computer": "192.168.25.154",
            "date": "22//10//2023",
            "id": "25",
            "profile": "Backup13",
            "time": "13:30",
        },
    ]

    return jsonify(result=data)
    # return jsonify({'result': [{'backupProfileId': p.title, 'author': p.author} for p in profies]})


########################
def get_db_connection(dbname):
    conn = sqlite3.connect(dbname)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/node_jobs', methods=['POST'])
def get_node_jobs():
    content = request.get_json() or {}
    action = content.get("action", "data") 
    node_filter = content.get("node", None)   

    fetch_all_failed_jobs()
    fetch_all_success_jobs()

    dbname = f'{str(app.config.get("getCode"))}.db'
    with get_db_connection(dbname) as conn:
        cursor = conn.cursor()
        if node_filter:
            cursor.execute("SELECT * FROM node_jobs WHERE node = ?", (node_filter,))
        else:
            cursor.execute("SELECT * FROM node_jobs")
        rows = cursor.fetchall()

    if action == "count":
        total_success = 0
        total_failed = 0

        for row in rows:
            row_dict = dict(row)
            total_success += row_dict.get("total_success", 0)
            total_failed += row_dict.get("total_failed", 0)
        return jsonify({"success":total_success, "failed":total_failed})
    else:  
        all_data = []
        all_failed_data = []

        for row in rows:
            data = json.loads(row["data"]) if row["data"] else {}
            failed_data = json.loads(row["failed_data"]) if row["failed_data"] else []

            all_data.append(data)
            all_failed_data.append(failed_data)

        return jsonify({'success':all_data, 'failed':all_failed_data})

async def fetch_failed_jobs_async(session, url, metadata):
    async with session.get(url) as response:
        return url, metadata, await response.text()


# def fetch_failed_jobs(url, metadata):
#     try:
#         response = requests.get(f"{url}/api/getfailedjobs", timeout=2)
#         if response.status_code == 200:
#             return url, response.json()
#     except:
#         print("")
#     return url, ""

import socket

def is_client_online(url, timeout=2):
    """
    Quick check if client is reachable using TCP socket.
    Returns True if online, False if offline.
    Much faster than HTTP request on offline clients.
    Accepts URL with or without scheme (e.g. http://ip:7777 or ip:7777).
    """
    try:
        from urllib.parse import urlparse
        url = str(url or "").strip()
        if not url:
            return False
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 7777
        if not host and url:
            # No scheme: treat as host:port (e.g. 10.109.164.78:7777)
            if ":" in url:
                parts = url.rsplit(":", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    host = parts[0]
                    port = int(parts[1])
                else:
                    host = url
            else:
                host = url

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        return result == 0  # 0 means connection successful
    except Exception:
        return False


# import re
# def get_total_from_cache(cache_file):
#     """
#     Fast extraction of total count from cached JSON without loading entire file.
#     Reads only first 200 bytes.
#     """
#     try:
#         with open(cache_file, "r", encoding="utf-8") as f:
#             chunk = f.read(200)
#             match = re.search(r'"total(?:_failed)?"\s*:\s*(\d+)', chunk)
#             if match:
#                 return int(match.group(1))
#     except (FileNotFoundError, IOError):
#         pass
#     return None

import json
import re

def get_total_from_cache(cache_file, read_size=4096):
    """
    Fast and portable extraction of the first dictionary from a JSON list in a file.
    Reads only the first few KB and uses regex for shallow JSON objects.
    Returns the dictionary if it contains 'total' or 'total_failed'.
    """
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data_chunk = f.read(read_size)
            
            # Skip any whitespace before the list
            data_chunk = data_chunk.lstrip()
            
            # Ensure it starts with '['
            if not data_chunk.startswith('['):
                return None

            # Regex to match first shallow JSON object in the list
            # Matches from first '{' to first '}'
            # Works for typical cache objects that are not deeply nested
            match = re.search(r'\{[^{}]*\}', data_chunk)
            if match:
                json_str = match.group(0)
                try:
                    obj = json.loads(json_str)
                    if "total" in obj or "total_failed" in obj:
                        return obj
                except json.JSONDecodeError:
                    return None
    except (FileNotFoundError, IOError):
        return None

    return None


def fetch_failed_jobs(url, metadata, offline=False):
    cache_dir = "client_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    node_key = metadata.get("key")
    if not node_key:
        return url, ""
    
    cache_file = os.path.join(cache_dir, f"{node_key}_failed.json")

    if "action" in metadata and metadata['action']=='count':
        if os.path.exists(cache_file):
            total = get_total_from_cache(cache_file)
            return url, [{"total_failed": total}]


    if offline or not is_client_online(url, timeout=5):
        print(f"Client offline: {url} (key={node_key})")
        
        # Use cached data immediately
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    print(f"Using cached data for offline client: key={node_key}")
                    if cached_data and "total_failed" in cached_data[0]:
                         cached_data.pop(0)
                    return url, cached_data
            except (json.JSONDecodeError, IOError):
                pass
        
        return url, ""
    
    try:
        response = requests.get(f"{url}/api/getfailedjobs", timeout=20)
        if response.status_code == 200:
            data = response.json()

            job_repo_count = {}

            for job in data:
                repo = job.get("job_repo")
                if repo:
                    job_repo_count[repo] = job_repo_count.get(repo, 0) + 1
            data[0] = data[0] | job_repo_count
            # Save to cache file using stable key
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            if data and "total_failed" in data[0]:
                data.pop(0)
            return url, data
    except Exception as e:
        print(f"Fetch failed for {url}: {str(e)}")
    
    # Fallback: Use cached file if fetch failed
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                print(f"Using cached failed jobs for key={node_key}")
                if cached_data and "total_failed" in cached_data[0]:
                    cached_data.pop(0)
                return url, cached_data
        except (json.JSONDecodeError, IOError):
            pass
    
    return url, ""

@app.route("/api/getfailedsuccessjobs", methods=["GET", "POST"])
def fetch_all_failed_success_jobs():
    request_data = {}
    if request.method == 'POST':
        request_data = request.json

    action = request_data.get('action', None)

    ar=[]
    failed_jobs=fetch_all_failed_jobs(action)
    for item in failed_jobs.get("failedjobs",None):
        for it in item.get("data",None):
            it.update({"status": "failed"})
            it.update({"nodeName":item.get("nodeName",None) })
            ar.append(it)
            ar = sorted(ar, key=itemgetter("nodeName", "status"))

    success_jobs=fetch_all_success_jobs(action)
    for item in success_jobs.get("successjobs",None):
        for it in item.get("data",None):
            it.update({"status": "success"})
            it.update({"nodeName":item.get("nodeName",None) })
            ar.append(it)
            ar = sorted(ar, key=itemgetter("nodeName", "status"))

    resp={"data":ar}
    return jsonify(resp,200)

def fetch_all_failed_jobs(action=None):
    urls = clientnodes_x
    import concurrent.futures

    res = []
    fetched_online_ids = set()
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(fetch_failed_jobs, url, {**metadata, "action": action} if action is not None else metadata): (url, metadata)
                for url, metadata in urls.items() 
            }

            # responses = []
            responses = {}
            total_count = 0 
            from sqlite_managerA import SQLiteManager
            session = SQLiteManager()
            for future in concurrent.futures.as_completed(futures):
                url, metadata = futures[future]
                try:
                    response = future.result()
                    # responses[url] = {'url': url, 'response': response}
                    responses[url] = {"response": response[1]}
                    data = response[1]
                    # save_jobs_only = [item for item in data if "total_failed" not in item]
                    res.append({"node": url,"nodeName": metadata.get("agent",""), "data": data})
                    fetched_online_ids.add(metadata.get("key"))
                    # responses.__add__(response[1])
                    # if (isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "total_failed" in data[0]):
                    #     total_count += data[0]["total_failed"]
                    # # responses.__add__(response[1])
                    # node = metadata.get("key")
                    # total_success = 0
                    # total_failed = total_count
                    # data_json = None
                    # failed_data = json.dumps(res)
                    # updated_at = datetime.datetime.utcnow().isoformat()

                    # dbname = f'{str(app.config.get("getCode"))}.db'
                    # create_table_sql = """
                    # CREATE TABLE IF NOT EXISTS node_jobs (
                    #     node TEXT PRIMARY KEY,
                    #     total_success INTEGER DEFAULT 0,
                    #     total_failed INTEGER DEFAULT 0,
                    #     data JSON,
                    #     failed_data JSON,
                    #     updated_at TEXT
                    # );
                    # """

                    # sql_upsert = f"""
                    # INSERT INTO node_jobs (node, total_success, total_failed, data, failed_data, updated_at)
                    # VALUES ('{node}', {total_success}, {total_failed}, '{data_json}','{failed_data.replace("'", "''")}', '{updated_at}')
                    # ON CONFLICT(node) DO UPDATE SET
                    #     total_failed = excluded.total_failed,
                    #     failed_data = excluded.failed_data,
                    #     updated_at = excluded.updated_at;
                    # """
                    # session.execute_queries([(dbname, [create_table_sql])])
                    # session.execute_queries([(dbname, [sql_upsert])])
                except Exception as exc:
                    print(
                        str(exc)
                    )  # responses[url] = {'url': url[0], 'response': str(exc)}
        # return (responses,res,200)
        # return (responses,res,200)
        # return (responses,res,200)
            executor.shutdown()
    except:
        pass
    from .jobdata import JobsRecordManager
    m=JobsRecordManager("records.db", "records.json",app=app)
    endp =[] 
    endpoints_statistics = [] 
    try:
        endp = m.fetch_nodes_as_json()
        m.close()
        for e in json.loads(endp):
            node_id = e["idx"]
            if node_id in  app.config["agent_activation_keys"]:
                if node_id in fetched_online_ids:
                    continue
                metadata = {
                    "key":e["idx"],
                    "action": action,
                    }
                url, data = fetch_failed_jobs(None, metadata, offline=True)
                res.append({"node": url,"nodeName": e.get("agent",""), "data": data})
    except:
        pass
    return {"failedjobs": res}#, "total_failed":total_count}


@app.route("/api/getfailedjobs", methods=["GET", "POST"])
def failed_jobs():
    request_data = {}
    if request.method == 'POST':
        request_data = request.json

    action = request_data.get('action', None)
    combined_response = fetch_all_failed_jobs(action)
    return jsonify(combined_response)


########################
def data_compile_success(data):
    import json
    from collections import defaultdict
    from datetime import datetime

    # # Load the JSON data
    # with open('data.json', 'r') as f:
    #     data = json.load(f)

    # Initialize counters
    node_job_counts = defaultdict(int)  # To count jobs per node
    hourly_timeline = defaultdict(int)  # To count jobs per hour

    # Extract data and perform analysis
    for item in data["successjobs"]:
        node = item["node"]
        jobs = item["data"]

        # Count jobs per node
        node_job_counts[node] += len(jobs)

        # Analyze hourly timeline
        for job in jobs:
            done_time = datetime.strptime(job["done_time"], "%Y-%m-%d %H:%M:%S")
            hour = done_time.strftime("%Y-%m-%d %H")
            hourly_timeline[hour] += 1

    # Sort the hourly timeline by hour
    sorted_timeline = sorted(hourly_timeline.items(), key=lambda x: x[0])

    # Print analysis results
    print("Jobs count per node:")
    for node, count in node_job_counts.items():
        print(f"{node}: {count} jobs")

    print("\nHourly timeline of jobs:")
    for hour, count in sorted_timeline:
        print(f"{hour}: {count} jobs")


async def fetch_success_jobs_async(session, url, metadata):
    async with session.get(url) as response:
        return url, metadata, await response.text()


# def fetch_success_jobs(url, metadata):
#     # if request:
#     #     port = request.environ.get('SERVER_PORT')
#     #     if port:
#     #         print(f'port=========>{port}')
#     # print("Port information not available")
#     try:
#         response = requests.get(f"{url}/api/getsuccessjobs", timeout=20)
#         if response.status_code == 200:
#             # data_compile_success(json.dumps(response.json()))
#             return url, response.json()
#     except:
#         print("")
#     return url, ""

def fetch_success_jobs(url, metadata, offline=False):
    cache_dir = "client_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    node_key = metadata.get("key")
    if not node_key:
        return url, ""

    cache_file = os.path.join(cache_dir, f"{node_key}.json")

    if "action" in metadata and metadata['action']=='count':
        if os.path.exists(cache_file):
            total = get_total_from_cache(cache_file)
            return url, [{"total_success": total}]

    if offline or not is_client_online(url, timeout=2):
        print(f"Client offline: {url} (key={node_key})")
        
        # Use cached data immediately
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    print(f"Using cached data for offline client: key={node_key}")
                    if cached_data and "total" in cached_data[0]:
                        cached_data.pop(0)
                    return url, cached_data
            except (json.JSONDecodeError, IOError):
                pass
        
        return url, ""

    try:
        response = requests.get(f"{url}/api/getsuccessjobs", timeout=20)
        if response.status_code == 200:
            data = response.json()
            job_repo_count = {}

            for job in data:
                repo = job.get("job_repo")
                if repo:
                    job_repo_count[repo] = job_repo_count.get(repo, 0) + 1
            data[0] = data[0] | job_repo_count
            # Save to cache file
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            if data and "total" in data[0]:
                data.pop(0)
            return url, data
    except Exception as e:
        print(f"Fetch failed for {url}: {str(e)}")
    
    # Fallback: Load from cache if fetch failed
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                print(f"Using cached data for {url}")
                if cached_data and "total" in cached_data[0]:
                    cached_data.pop(0)
                return url, cached_data
        except (json.JSONDecodeError, IOError):
            pass
    
    return url, ""


def fetch_all_10createdjobs_jobs():
    urls = clientnodes_x
    import concurrent.futures

    res = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_success_jobs, url, metadata): (url, metadata)
            for url, metadata in urls.items()
        }

        # responses = []
        responses = {}
        for future in concurrent.futures.as_completed(futures):
            url, metadata = futures[future]
            try:
                response = future.result()
                # responses[url] = {'url': url, 'response': response}
                responses[url] = {"response": response[1]}
                res.append({"node": url,"nodeName": metadata.get("agent",""), "data": response[1]})
                # responses.__add__(response[1])
            except Exception as exc:
                print(
                    str(exc)
                )  # responses[url] = {'url': url[0], 'response': str(exc)}
        executor.shutdown()
    # return (responses,res,200)
    # return (responses,res,200)
    # return (responses,res,200)
    return {"successjobs": res}


@app.route("/api/get10createdjobs", methods=["GET", "POST"])
def created10_jobs():
    combined_response = fetch_all_10createdjobs_jobs()
    return jsonify(combined_response)


def fetch_all_success_jobs(action=None):
    urls = clientnodes_x
    import concurrent.futures

    res = []
    fetched_online_ids = set()
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(fetch_success_jobs, url, {**metadata, "action": action} if action is not None else metadata): (url, metadata)
                for url, metadata in urls.items()
            }

            # responses = []
            responses = {}
            total_count = 0
            from sqlite_managerA import SQLiteManager
            session = SQLiteManager()
            for future in concurrent.futures.as_completed(futures):
                url, metadata = futures[future]
                try:
                    response = future.result()
                    # responses[url] = {'url': url, 'response': response}
                    responses[url] = {"response": response[1]}
                    data = response[1]
                    # save_jobs_only = [item for item in data if "total" not in item]
                    res.append({"node": url,"nodeName": metadata.get("agent",""), "data": data})
                    fetched_online_ids.add(metadata.get("key"))
                    # if (isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "total" in data[0]):
                    #     total_count += data[0]["total"]
                    # # responses.__add__(response[1])
                    # node = metadata.get("key")
                    # total_success = total_count
                    # total_failed = 0
                    # data_json = json.dumps(res)
                    # failed_data = None
                    # updated_at = datetime.datetime.utcnow().isoformat()

                    # dbname = f'{str(app.config.get("getCode"))}.db'
                    # create_table_sql = """
                    # CREATE TABLE IF NOT EXISTS node_jobs (
                    #     node TEXT PRIMARY KEY,
                    #     total_success INTEGER DEFAULT 0,
                    #     total_failed INTEGER DEFAULT 0,
                    #     data JSON,
                    #     failed_data JSON,
                    #     updated_at TEXT
                    # );
                    # """

                    # sql_upsert = f"""
                    # INSERT INTO node_jobs (node, total_success, total_failed, data, failed_data, updated_at)
                    # VALUES ('{node}', {total_success}, {total_failed}, '{data_json}','{failed_data}', '{updated_at}')
                    # ON CONFLICT(node) DO UPDATE SET
                    #     total_success = excluded.total_success,
                    #     data = excluded.data,
                    #     updated_at = excluded.updated_at;
                    # """
                    # session.execute_queries([(dbname, [create_table_sql])])
                    # session.execute_queries([(dbname, [sql_upsert])])
                except Exception as exc:
                    print(
                        str(exc)
                    )  # responses[url] = {'url': url[0], 'response': str(exc)}
        # return (responses,res,200)
        # return (responses,res,200)
        # return (responses,res,200)
            executor.shutdown()
    except:
        pass

    from .jobdata import JobsRecordManager
    m=JobsRecordManager("records.db", "records.json",app=app)
    endp =[] 
    endpoints_statistics = [] 
    try:
        endp = m.fetch_nodes_as_json()
        m.close()
        for e in json.loads(endp):
            node_id = e["idx"]
            if node_id in  app.config["agent_activation_keys"]:
                if node_id in fetched_online_ids:
                    continue
                metadata = {
                    "key":e["idx"],
                    "action": action,
                    }
                url, data = fetch_success_jobs(None, metadata, offline=True)
                res.append({"node": url,"nodeName": e.get("agent",""), "data": data})
    except:
        pass
    return {"successjobs": res} #, 'total':total_count}


@app.route("/api/getsuccessjobs", methods=["GET", "POST"])
def success_jobs():
    request_data = {}
    if request.method == 'POST':
        request_data = request.json

    action = request_data.get('action', None)
    combined_response = fetch_all_success_jobs(action)
    return jsonify(combined_response)


# async def failed_jobs_async():

#     ip = ""
#     try:
#         async with aiohttp.ClientSession() as session:
#             tasks = [
#                 fetch_failed_jobs(session, url, metadata)
#                 for url, metadata in clientnodes_x.items()
#             ]
#             responses = await asyncio.gather(*tasks)
#             return {
#                 url: {"metadata": metadata, "response": response}
#                 for url, metadata, response in responses
#             }

#     except Exception as exs:
#         print(str(exs))


@app.route("/agent/download", methods=["GET", "POST"])
def agent_download():
    from flask import send_file 
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "downloads",
        "Client20032020_1751.exe",
    )
    file_path = os.path.join(
        os.path.dirname(app.root_path), "downloads", "Client20032020_1751.exe"
    )

    archive_name= file_path+".zip"
    archive_name= file_path+".zip"
    filename = "Client20032020_1751.exe"
    filename="ABEndpointSetup.zip"
    return send_file(archive_name, as_attachment=True, download_name=filename)




@app.route("/data/download/file", methods=["POST"])
def data_download_file():
    from flask import send_file
    encryptionkey = request.headers.get("fe","ApnaBackup")
    filename=request.headers.get("source")
    rep=request.headers.get("rep")
    mime_type = request.headers.get("mime")
    pro=request.headers.get("pro")
    pro=json.loads(pro)
    job_id = ensure_job_id(pro.get("tccnstamp"))
    log_chunk_event(
        logger,
        logging.DEBUG,
        job_id,
        "restore",
        file_path=pro.get("tccn"),
        file_id=pro.get("name"),
        chunk_index=filename,
        extra={"event": "chunk_download_start", "repo": rep},
    )
    
    repd = request.headers.get("repd")
    repd = base64.b64decode(repd)
    repd = gzip.decompress(repd)
    repd = repd.decode("UTF-8")
    jsrepd = json.loads(repd)

    from io import BytesIO
    if mime_type == 'file':
        sktio.emit(
                "backup_data",
                {
                    "restore_flag":True,
                    "backup_jobs": [
                        {
                            "restore_flag":True,
                            "name":pro['name'],
                            "scheduled_time": datetime.datetime.fromtimestamp(
                                float(pro['tccnstamp'])
                            ).strftime("%H:%M:%S"),
                            "agent":  pro['agent'] ,
                            "progress_number": float(100-pro['pro']), # float(100 * (float(pendingfiles)))/ float(ftotal),
                            "id": float(pro['tccnstamp']),
                            "repo":rep,
                            # "restore_location":res_json["RestoreLocation"], ##kartik
                        }
                    ]
                },
            )
    sktio.emit(
            "backup_data",
            {
                    "restore_flag":True,
                    "backup_jobs": [
                        {
                            "status": "counting",
                            "restore_flag":True,
                            "name": pro['name'],
                            "agent": pro['agent'],
                            "scheduled_time": datetime.datetime.fromtimestamp(
                            float(pro['tccnstamp'])
                        ).strftime("%H:%M:%S"),
                            "progress_number": float(pro['pro']),
                            "id": float(pro['tccnstamp']),
                            "repo":rep,
                            "filename": pro['tccn'],

                        }
                    ]
                })

    try:
        if str(rep).upper() == "GDRIVE":
            gd = GDClient()
            # fh = gd.download_file_bytesio(jsrepd["gidn"])
            gfid = jsrepd["gidn_list"][int(filename)]
            if isinstance(gfid,dict):
                gfid = gfid['id']
            fh = gd.download_file_bytesio(gfid)
            if not fh:
                log_event(
                    logger,
                    logging.ERROR,
                    job_id,
                    "restore",
                    file_path=pro.get("tccn"),
                    file_id=pro.get("name"),
                    chunk_index=filename,
                    error_code="CHUNK_NOT_FOUND",
                    error_message="GDRIVE chunk not found",
                    extra={"event": "chunk_failed"},
                )
                return (str(filename) +" Not found on fileserver" , 404)
            return_send_file = send_file(fh, as_attachment=True, download_name=jsrepd["file_name"])
            return_send_file.headers.add("filename",filename)
            return_send_file.headers.add("folder","file")
            log_chunk_event(
                logger,
                logging.DEBUG,
                job_id,
                "restore",
                file_path=pro.get("tccn"),
                file_id=pro.get("name"),
                chunk_index=filename,
                extra={"event": "chunk_download_end", "repo": rep},
            )
            return return_send_file
        if str(rep).upper() == "AWSS3":
            gd = awd.S3Client()
            fh = gd.download_data(str(filename).replace(os.sep,"/"))
            if not fh:
                return (str(filename) +" Not found on fileserver" , 404)
            fh=BytesIO(fh)
            return_send_file = send_file(fh, as_attachment=True, download_name=filename)
            return_send_file.headers.add("filename",filename)
            return_send_file.headers.add("folder","file")
            log_chunk_event(
                logger,
                logging.DEBUG,
                job_id,
                "restore",
                file_path=pro.get("tccn"),
                file_id=pro.get("name"),
                chunk_index=filename,
                extra={"event": "chunk_download_end", "repo": rep},
            )
            return return_send_file

        if str(rep).upper() == "AZURE":
            gd = azd.AzureBlobClient("apnabackup")
            fh = gd.download_data(filename)
            if not fh:
                return (str(filename) +" Not found on fileserver" , 404)
            fh=BytesIO(fh)
            return_send_file = send_file(fh,mimetype='application/octet-stream', as_attachment=True, download_name=filename)
            return_send_file.headers.add("filename",filename)
            return_send_file.headers.add("folder","file")
            log_chunk_event(
                logger,
                logging.DEBUG,
                job_id,
                "restore",
                file_path=pro.get("tccn"),
                file_id=pro.get("name"),
                chunk_index=filename,
                extra={"event": "chunk_download_end", "repo": rep},
            )
            return return_send_file
        if str(rep).upper() == "ONEDRIVE":
            gd = onedrive.OneDriveClient()
            fh=""
            onedrive_filename = os.path.join("ApnaBackup", filename)
            onedrive_filename = str(onedrive_filename).replace(os.sep,os.sep).replace(os.sep,"/")
            try:
                fh = gd.download_file(str(onedrive_filename),"")
            except Exception as es:
                print(str(es))
            return fh

        filename = os.path.join(app.config["UPLOAD_FOLDER"],filename)
        return_send_file = send_file(
            filename, as_attachment=True, download_name=filename
        )
        return_send_file.headers.add("filename",filename)
        return_send_file.headers.add("folder","file")
        log_chunk_event(
            logger,
            logging.DEBUG,
            job_id,
            "restore",
            file_path=pro.get("tccn"),
            file_id=pro.get("name"),
            chunk_index=filename,
            extra={"event": "chunk_download_end", "repo": rep},
        )
        return return_send_file
    except FileNotFoundError as esd:
        log_event(
            logger,
            logging.ERROR,
            job_id,
            "restore",
            file_path=pro.get("tccn"),
            file_id=pro.get("name"),
            chunk_index=filename,
            error_code="CHUNK_NOT_FOUND",
            error_message=str(esd),
            extra={"event": "chunk_failed"},
        )
        return (str(filename) +" Not found on fileserver" , 404)
    except Exception as es:
        log_event(
            logger,
            logging.ERROR,
            job_id,
            "restore",
            file_path=pro.get("tccn"),
            file_id=pro.get("name"),
            chunk_index=filename,
            error_code="CHUNK_DOWNLOAD_FAILED",
            error_message=str(es),
            extra={"event": "chunk_failed"},
        )
        return (str(es), 500)
    
    


@app.route("/data/download/", methods=["GET", "POST"])
def data_download():
    from flask import send_file

    id = request.headers.get("id")
    pid = request.headers.get("pid")
    obj = request.headers.get("obj")

    # conn = sqlite3.connect(f"{obj}.db")
    s_manager = SQLiteManager()
    dbname = os.path.join(app.config["location"], obj)
    qrs = [
        (
            dbname,
            [
                "SELECT * FROM backups where "
                + "id = "
                + str(id)
                + " and name = "
                + str(pid)
            ],
        )
    ]
    results = s_manager.execute_queries(qrs)
    file_paths=None
    for db_path, db_results in results.items():
        print(f"Results for {db_path}:")
        for i, (result, records) in enumerate(db_results):
            print(f"  Query {i+1}: {result}")
            if result == "Success":
                if records is not None:
                    file_paths = records
                    print(f"    Records: {records}")

    # conn = sqlite3.connect(dbname)
    # cursor = conn.cursor()
    # cursor.execute(
    #     "SELECT * FROM backups where " + "id = " + str(id) + " and name = " + str(pid)
    # )
    # file_paths = cursor.fetchall()
    # cursor.close()
    # conn.close()
    file_or_folder = None
    jd = None
    if file_paths and len(file_paths) > 0:
        file_or_folder = file_paths[0][8]
        if file_or_folder == "" or file_or_folder is None:
            file_or_folder = "folder"
        try:
            log_val = file_paths[0][10]
            jd = json.loads(log_val) if isinstance(log_val, str) else log_val
            if isinstance(jd, str):
                jd = json.loads(jd)
        except Exception:
            jd = None
    # GDrive/cloud fallback: when backups is empty, query backups_M (data_repod has metadata)
    if jd is None and id and pid and obj:
        q_backups_m = (
            "SELECT from_path, file_name, data_repo, data_repod FROM backups_M WHERE "
            f"id = {float(pid)}"
        )
        try:
            qrs_m = [(dbname, [q_backups_m])]
            results_m = s_manager.execute_queries(qrs_m)
            db_results = results_m.get(dbname, [])
            if db_results and db_results[0][0] == "Success" and db_results[0][1]:
                row = db_results[0][1][0]
                from_path, file_name_m, data_repo_m, data_repod = (row[0] or ""), (row[1] or ""), (row[2] or ""), (row[3] or "{}")
                file_or_folder = "file" if file_name_m else "folder"
                if data_repod:
                    jd = json.loads(data_repod) if isinstance(data_repod, str) else data_repod
                    jd = jd or {}
                    jd.setdefault("rep", data_repo_m)
                    jd.setdefault("file_name", os.path.basename(file_name_m) if file_name_m else "")
                    jd.setdefault("file_name_x", (from_path + os.sep + file_name_m) if file_name_m else from_path)
        except Exception:
            pass
    if jd is None:
        return ("No backup record found for id=%s pid=%s" % (id, pid), 404)
    # file_path = os.path.join(
    #     os.path.dirname(os.path.realpath(__file__)),
    #     "downloads",
    #     "Client20032020_1751.exe",
    # )
    # file_path = os.path.join(
    #     os.path.dirname(app.root_path), "downloads", "Client20032020_1751.exe"
    # )
    
    isMetaFile = jd.get("isMetaFile",False)
    # isMetaFile = False

    from io import BytesIO
    filename = "Client20032020_1751.exea"
    if str(jd["rep"]).upper() == "GDRIVE":
        gd = GDClient()
        fh = gd.download_file_bytesio(jd["gidn"])
        if not fh:
            return (str(jd["file_name_x"]) +" Not found on fileserver" , 404)
        return_send_file = send_file(fh, as_attachment=True, download_name=jd["file_name"])
        return_send_file.headers.add("filename",jd["file_name_x"])
        return_send_file.headers.add("folder",file_or_folder)
        return return_send_file
    # print(file_path)
    if str(jd["rep"]).upper() == "AWSS3":
        gd = awd.S3Client()
        #fh = gd.download_data_BytesIO(jd["gidn"].get('file_key',""))
        #fh = gd.download_data(jd["gidn"].get('file_key',""))
        fh = gd.download_data(str(jd.get("file_name_x","")).replace(os.sep,"/"))
        if not fh:
            return (str(jd["file_name_x"]) +" Not found on fileserver" , 404)
        fh=BytesIO(fh)
        return_send_file = send_file(fh, as_attachment=True, download_name=jd["file_name"])
        return_send_file.headers.add("filename",jd["file_name_x"])
        return_send_file.headers.add("folder",file_or_folder)
        return return_send_file
    # print(file_path)
    if str(jd["rep"]).upper() == "AZURE":
        gd = azd.AzureBlobClient("apnabackup")
        fh = gd.download_data(jd["file_name_x"])
        if not fh:
            return (str(jd["file_name_x"]) +" Not found on fileserver" , 404)
        fh=BytesIO(fh)
        return_send_file = send_file(fh,mimetype='application/octet-stream', as_attachment=True, download_name=jd["file_name"])
        return_send_file.headers.add("filename",jd["file_name_x"])
        return_send_file.headers.add("folder",file_or_folder)
        return return_send_file
    # print(file_path)
    if str(jd["rep"]).upper() == "ONEDRIVE":
        gd = onedrive.OneDriveClient()
        jd["file_name_x"] = os.path.join("ApnaBackup",jd["path"],jd["file_name"]+"_"+str(jd["j_sta"])+".gz")
        jd["file_name_x"] =str(jd["file_name_x"]).replace(os.sep,os.sep).replace(os.sep,"/")
        fh=""
        #fh = gd.download_data(jd["file_name_x"])
        try:
            # fh = gd.download_file( 
            #     str(jd["file_name_x"]).replace(app.config['UPLOAD_FOLDER'],'ApnaBackup')
            #         .replace(os.sep,os.sep)
            #         .replace(os.sep,"/"),
            #         "")
            fh = gd.download_file(str(jd["file_name_x"]),"")
        except Exception as es:
            print(str(es))
        return fh
    # print(file_path)
    
    jd["file_name_x"] = os.path.join(app.config["UPLOAD_FOLDER"],jd["path"],jd["file_name"]+"_"+str(jd["j_sta"])+".gz")
    if isMetaFile:
        #send file as streaming data so that the client can get the data as streamed bytes without timeouts
        #read the metadata file 
        #start a loop for determining the files to be sent
        #send the header name of index of the next file so that the endpoint now download the next file
        
        try:
            return_send_file = send_file(
                jd["file_name_x"], as_attachment=True, download_name=jd["file_name"]
            )
            return_send_file.headers.add("filename",jd["file_name_x"])
            return_send_file.headers.add("folder",file_or_folder)
            return return_send_file
        except FileNotFoundError as esd:
            return (str(jd["file_name_x"]) +" Not found on fileserver" , 404)
        except Exception as es:
            return (str(es), 500)
    
    else:
        try:
            return_send_file = send_file(
                jd["file_name_x"], as_attachment=True, download_name=jd["file_name"]
            )
            return_send_file.headers.add("filename",jd["file_name_x"])
            return_send_file.headers.add("folder",file_or_folder)
            return return_send_file
        except FileNotFoundError as esd:
            return (str(jd["file_name_x"]) +" Not found on fileserver" , 404)
        except Exception as es:
            return (str(es), 500)

def compare_versions(version1, version2):
    # Compare each version component
    for v1, v2 in zip(version1, version2):
        if v1 < v2:
            return -1  # version1 is older
        elif v1 > v2:
            return 1   # version1 is newer
    return 0  # versions are equal

@app.route("/agent/checkdownload", methods=["GET", "POST"])
def check_download(file_path=""):
    import os
    import win32api
    from flask import send_file

    req_data = request.json
    if file_path == "":
        file_path = os.path.join(
            os.path.dirname(app.root_path), "downloads", "Client20032020_1751.exe"
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    try:
        info = win32api.GetFileVersionInfo(file_path, "\\")
        version = f"{info['FileVersionMS'] >> 16}.{info['FileVersionMS'] & 0xffff}.{info['FileVersionLS'] >> 16}.{info['FileVersionLS'] & 0xffff}"
        version_s = (
            info["FileVersionMS"]
            + info["FileVersionMS"]
            + info["FileVersionLS"]
            + info["FileVersionLS"]
        )
        versionrequest = req_data["Version"]
        # if version_s > req_data["version_s"]:
        bUpdateProceed = 0!=compare_versions(version1=version,version2=versionrequest)

        if bUpdateProceed :

            #######

            file_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "downloads",
                "Client20032020_1751.exe",
            )
            file_path = os.path.join(
                os.path.dirname(app.root_path), "downloads", "Client20032020_1751.exe"
            )

            filename = "Client20032020_1751.exea"
            print(file_path)
            return send_file(file_path, as_attachment=True, download_name=filename)
            #######
            # return (jsonify({'version':version,'version_s':version_s}))
    except Exception as e:
        print(f"Error: {e}")
        return None

    return None

@app.route("/uploadunc", methods=["POST"])
def upload_file_unc():
    import gzip

    bdone = True
    abort = "True" == request.headers.get("abt", "False")

    headers = request.headers.get("headers")
    seq_num = int(request.headers.get("quNu", -1))
    total_chunks = int(request.headers.get("tc", 0))
    init_msg = int(request.headers.get("init", False ))
    job_id = ensure_job_id(
        request.headers.get("job_id")
        or request.headers.get("jsta")
        or request.headers.get("tfi")
    )
    log_chunk_event(
        logger,
        logging.DEBUG,
        job_id,
        "backup",
        file_path=request.headers.get("File-Name"),
        chunk_index=seq_num,
        extra={"event": "chunk_received", "total_chunks": total_chunks},
    )

    compressed_chunk = request.data
    try:
        decompressed_chunk = gzip.decompress(compressed_chunk)
    except Exception as decompress_error:
        log_event(
            logger,
            logging.WARNING,
            job_id,
            "backup",
            file_path=request.headers.get("File-Name"),
            chunk_index=seq_num,
            error_code="DECOMPRESS_FALLBACK",
            error_message=str(decompress_error),
            extra={"event": "chunk_decompress_fallback"},
        )
        decompressed_chunk = compressed_chunk

    import base64
    jsv=None
    jsvkrgs = None
    tcc=None
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from module2 import BackupLogs, BackupMain
        from datetime import date

        s_manager = SQLiteManager()        
        v = request.headers.get("v",None)
       
        if v:
            v = base64.b64decode(v)
            v = gzip.decompress(v)
            v = v.decode("UTF-8")
            try:
                jsv = json.loads(v)
            except:
                jsv=None

        j_sta = time()
        src_folder = ""
        trg_folder = ""
        p_name = ""
        repo = ""
        authId = ""
        p_NameText = ""
        p_IdText = ""
        bkupType = ""
        file_pattern = ""
        finished=False

        if jsv:
            if jsv["kwargs"]:
                jsvkrgs = jsv["kwargs"].get("kwargs",None)
                if not jsvkrgs: jsvkrgs = jsv.get("kwargs",None)
                if jsvkrgs:
                    src_folder = jsvkrgs.get("src_folder", "")
                    trg_folder = jsvkrgs.get("trg_folder", "")
                    p_name = jsvkrgs.get("p_name", "")
                    repo = jsvkrgs.get("repo", "")
                    authId = jsvkrgs.get("authId", "")
                    p_NameText = jsvkrgs.get("p_NameText", "")
                    p_IdText = jsvkrgs.get("p_IdText", "")
                    bkupType = jsvkrgs.get("bkupType", "")
                    file_pattern = jsvkrgs.get("file_pattern", "")
                    seq_num = jsvkrgs.get("quNu", -1)
                    j_sta = jsvkrgs.get("jsta", time())
                    finished = jsvkrgs.get("finished", False)
                    mime_type_bkp = jsvkrgs.get("mime_type_bkp", "folder")
                    file_size = jsvkrgs.get("file_size", 0)
        
        file_path = None
        chunks = None
        ivhex = None
        guid = None
        job_id = None
        scom = None
        scon = None
        scombm = None
        scombs = None
        
        tcc = request.headers.get("tcc",None)
        if tcc:
            tcc = base64.b64decode(tcc)
            tcc = gzip.decompress(tcc)
            tcc = tcc.decode("UTF-8")
            jsdat = json.loads(tcc)
            print(jsdat)
            file_path = jsdat["original_path"]
            chunks = jsdat["chunks"]
            ivhex = jsdat["givn"]
            guid = jsdat["guid"]
            job_id = jsdat["juid"]
            scom = jsdat["scom"]
            scon = jsdat["scon"]
            scombm = jsdat["scombm"]
            scombs = jsdat["scombs"]
        chunk_hash = request.headers.get("chkh")
        file_hash = request.headers.get("filehash")
        chunk_hash = request.headers.get("chkh")
        file_hash = request.headers.get("filehash")

        from_path = os.path.join(
            scom, os.path.dirname(file_path).replace(":", "{{DRIVE}}")
        )
        full_file_name = os.path.join(scom, file_path.replace(":", "{{DRIVE}}"))
        mime_type="folder"
        if os.path.isfile(src_folder):
            mime_type = "file"
        mime_type = mime_type_bkp
        # else:
        #     mime_type = "file" if os.path.isfile(file_path) else "folder"
        file_name = ""
        x = float(jsvkrgs.get("filesdone",0))
        nx = float(jsvkrgs.get("totalfiles",0))
        accuracy=100.00*(x/nx)
        sktio.emit(
            "backup_data",
            {
                "backup_jobs": [
                    {
                        "name": p_NameText,
                        "scheduled_time": datetime.datetime.fromtimestamp(
                            float(j_sta)
                        ).strftime("%H:%M:%S"),
                        "agent": jsvkrgs["epn"],
                        "progress_number": float(
                            100
                            * (
                                float(jsvkrgs["currentfile"])
                                - 1
                                + float(seq_num) / float(jsvkrgs["total_chunks"])
                            )
                        )
                        / float(jsvkrgs["totalfiles"]),
                        "accuracy": accuracy,
                        "finished": finished,
                        "id": j_sta,
                        "repo": repo  ##kartik
                    }
                ]
            },
        )

        if mime_type == "file":
            file_name = os.path.basename(file_path)
        if file_name:
            manifest_folder = _manifest_folder(tcc)
            temp_manifest_dir = os.path.join(add_unc_temppath(), manifest_folder)
            os.makedirs(temp_manifest_dir, exist_ok=True)
            manifest = _load_manifest(temp_manifest_dir, file_name, j_sta)
            manifest["total_chunks"] = int(total_chunks or manifest.get("total_chunks") or 0)
            if file_hash:
                manifest["file_hash"] = str(file_hash)
            if chunk_hash:
                manifest.setdefault("chunks", {})
                manifest["chunks"][str(seq_num)] = str(chunk_hash)
            _save_manifest(temp_manifest_dir, file_name, j_sta, manifest)
            log_event(
                logger,
                logging.INFO,
                ensure_job_id(j_sta),
                "backup",
                file_path=file_name,
                error_code="",
                error_message="",
                extra={"event": "manifest_update", "manifest_path": _manifest_path(temp_manifest_dir, file_name, j_sta)},
            )
        if file_name:
            manifest_folder = _manifest_folder(tcc)
            temp_manifest_dir = os.path.join(add_unc_temppath(), manifest_folder)
            os.makedirs(temp_manifest_dir, exist_ok=True)
            manifest = _load_manifest(temp_manifest_dir, file_name, j_sta)
            manifest["total_chunks"] = int(total_chunks or manifest.get("total_chunks") or 0)
            if file_hash:
                manifest["file_hash"] = str(file_hash)
            if chunk_hash:
                manifest.setdefault("chunks", {})
                manifest["chunks"][str(seq_num)] = str(chunk_hash)
            _save_manifest(temp_manifest_dir, file_name, j_sta, manifest)
            log_event(
                logger,
                logging.INFO,
                ensure_job_id(j_sta),
                "backup",
                file_path=file_name,
                error_code="",
                error_message="",
                extra={"event": "manifest_update", "manifest_path": _manifest_path(temp_manifest_dir, file_name, j_sta)},
            )
        done_all = 1 if jsvkrgs["totalfiles"] == jsvkrgs["currentfile"] else 0
        dbname = os.path.join(app.config["location"], scom)
        qrs = [
            (
                dbname,
                [
                    "INSERT or IGNORE INTO backups_M ("
                    + " id,date_time,from_computer,from_path,"
                    + " data_repo,mime_type,file_name,size,"
                    + " pNameText,pIdText,bkupType,sum_all,"
                    + " sum_done,done_all,status,mode,data_repod) "
                    + "VALUES("
                    + str(j_sta)#str(job_id)
                    + ","
                    + str(time())
                    + ","
                    + "'"
                    + scon
                    + "',"
                    + "'"
                    + src_folder  #from_path
                    + "',"
                    + "'UNC',"
                    + "'"
                    + mime_type
                    + "',"
                    + "'',"
                    + "0,"
                    + "'"
                    + p_NameText
                    + "',"
                    + "'"
                    + p_IdText
                    + "',"
                    + "'"
                    + bkupType
                    + "',"
                    + ""
                    + str(jsvkrgs["totalfiles"])
                    + ","
                    + ""
                    + str(jsvkrgs["filesdone"])# str(jsvkrgs["currentfile"])
                    + ","
                    + ""
                    + str(done_all)
                    + ","
                    + "'',"
                    + "'',"
                    + "''"
                    + ") "
                    # + ") ON conflict(id) DO UPDATE SET"
                    + " ON CONFLICT(id) DO UPDATE SET date_time = excluded.date_time, "
                    + " from_computer = excluded.from_computer, from_path = excluded.from_path, "
                    + " data_repo = excluded.data_repo, mime_type = excluded.mime_type, file_name = excluded.file_name, "
                    + " size = excluded.size, "
                    + " pNameText = excluded.pNameText, " 
                    + " pIdText = excluded.pIdText, " 
                    + " bkupType = excluded.bkupType, " 
                    + " sum_all = excluded.sum_all, " 
                    + " sum_done = excluded.sum_done, " 
                    + " done_all = excluded.done_all, " 
                    + " status = excluded.status, " 
                    + " mode = excluded.mode, " 
                    + " data_repod = excluded.data_repod"
                    
                ],
            ),
            (
                dbname,
                [
                    "update backups_M  "
                    + " set sum_done = " + str(jsvkrgs["filesdone"])  
                    + " where id = " + str(job_id)  
                ],
            )
        ]
        results = s_manager.execute_queries(qrs)
        if (str(results[dbname][0]).capitalize()).__contains__("success"):
            qrs = [
                (
                    dbname,
                    [
                        # id,name,date_time,from_computer,from_path,
                        # data_repo,mime_type,size,file_name,full_file_name,
                        # log,pNameText,pIdText,bkupType,sum_all,sum_done,done_all,status,mode,data_repod
                        " INSERT or IGNORE INTO backups("
                        + " id,name,date_time,from_computer,from_path,"
                        + " data_repo,mime_type,file_name,full_file_name,size,"
                        + " log, pNameText,pIdText,bkupType,sum_all,"
                        + " sum_done,done_all,status,mode,data_repod) "
                        + "VALUES("
                        + str(unique_time_float())
                        + ","
                        + str(j_sta)#str(job_id)
                        + ","
                        + str(int(time()))
                        + ","
                        + "'"
                        + scon
                        + "',"
                        + "'"
                        + from_path
                        + "',"
                        + "'UNC',"
                        + "'"
                        + mime_type
                        + "',"
                        + "'"
                        + file_name
                        + "',"
                        + "'"
                        + full_file_name
                        + "',"
                        + str(file_size) +"," #"0,"
                        + "'"
                        + tcc
                        + "',"
                        + "'"
                        + p_NameText
                        + "',"
                        + "'"
                        + p_IdText
                        + "',"
                        + "'"
                        + bkupType
                        + "',"
                        + "1,"
                        + "1,"
                        + "1,"
                        + "'',"
                        + "'',"
                        + "''"
                        + ") "
                        + ""

                    ],
                )
            ]
        results = s_manager.execute_queries(qrs)
        if file_name and not abort and seq_num == total_chunks:
            final_manifest_path = _final_manifest_path(tcc, file_name, j_sta)
            temp_manifest_path = _manifest_path(temp_manifest_dir, file_name, j_sta)
            if os.path.exists(temp_manifest_path):
                try:
                    os.makedirs(os.path.dirname(final_manifest_path), exist_ok=True)
                    shutil.move(temp_manifest_path, final_manifest_path)
                    log_event(
                        logger,
                        logging.INFO,
                        ensure_job_id(j_sta),
                        "backup",
                        file_path=file_name,
                        extra={"event": "manifest_finalized", "manifest_path": final_manifest_path},
                    )
                except Exception as manifest_error:
                    log_event(
                        logger,
                        logging.ERROR,
                        ensure_job_id(j_sta),
                        "backup",
                        file_path=file_name,
                        error_code="MANIFEST_SAVE_FAILED",
                        error_message=str(manifest_error),
                        extra={"event": "manifest_failed"},
                    )

        # for x in jsdat["chunks"]:
        #     print("")
        #     print("===========================================")
        #     print(x)
        #     print("===========================================")
        #     print("")
        return "ok",200
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print("")
        bdone = False
        return "failed",500

@app.route("/uploadnas", methods=["POST"])
def upload_file_nas():
    import gzip

    bdone = True
    abort = "True" == request.headers.get("abt", "False")

    headers = request.headers.get("headers")
    seq_num = int(request.headers.get("quNu", -1))
    total_chunks = int(request.headers.get("tc", 0))
    init_msg = int(request.headers.get("init", False ))
    job_id = ensure_job_id(
        request.headers.get("job_id")
        or request.headers.get("jsta")
        or request.headers.get("tfi")
    )
    log_chunk_event(
        logger,
        logging.DEBUG,
        job_id,
        "backup",
        file_path=request.headers.get("File-Name"),
        chunk_index=seq_num,
        extra={"event": "chunk_received", "total_chunks": total_chunks},
    )

    compressed_chunk = request.data
    try:
        decompressed_chunk = gzip.decompress(compressed_chunk)
    except Exception as decompress_error:
        log_event(
            logger,
            logging.WARNING,
            job_id,
            "backup",
            file_path=request.headers.get("File-Name"),
            chunk_index=seq_num,
            error_code="DECOMPRESS_FALLBACK",
            error_message=str(decompress_error),
            extra={"event": "chunk_decompress_fallback"},
        )
        decompressed_chunk = compressed_chunk
    del compressed_chunk

    import base64
    jsv=None
    jsvkrgs = None
    tcc=None
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from module2 import BackupLogs, BackupMain
        from datetime import date

        s_manager = SQLiteManager()        
        v = request.headers.get("v",None)
       
        if v:
            v = base64.b64decode(v)
            v = gzip.decompress(v)
            v = v.decode("UTF-8")
            try:
                jsv = json.loads(v)
            except:
                jsv=None
        j_sta = time()
        src_folder = ""
        trg_folder = ""
        p_name = ""
        repo = ""
        authId = ""
        p_NameText = ""
        p_IdText = ""
        bkupType = ""
        file_pattern = ""
        finished=False

        if jsv:
            if jsv["kwargs"]:
                jsvkrgs = jsv["kwargs"].get("kwargs",None)
                if not jsvkrgs: jsvkrgs = jsv.get("kwargs",None)
                if jsvkrgs:
                    src_folder = jsvkrgs.get("src_folder", "")
                    trg_folder = jsvkrgs.get("trg_folder", "")
                    p_name = jsvkrgs.get("p_name", "")
                    repo = jsvkrgs.get("repo", "")
                    authId = jsvkrgs.get("authId", "")
                    p_NameText = jsvkrgs.get("p_NameText", "")
                    p_IdText = jsvkrgs.get("p_IdText", "")
                    bkupType = jsvkrgs.get("bkupType", "")
                    file_pattern = jsvkrgs.get("file_pattern", "")
                    seq_num = jsvkrgs.get("quNu", -1)
                    j_sta = jsvkrgs.get("jsta", time())
                    finished = jsvkrgs.get("finished", False)
        
        file_path = None
        chunks = None
        ivhex = None
        guid = None
        job_id = None
        scom = None
        scon = None
        scombm = None
        scombs = None
        
        tcc = request.headers.get("tcc",None)
        if tcc:
            tcc = base64.b64decode(tcc)
            tcc = gzip.decompress(tcc)
            tcc = tcc.decode("UTF-8")
            jsdat = json.loads(tcc)
            print(jsdat)
            file_path = jsdat["original_path"]
            chunks = jsdat["chunks"]
            ivhex = jsdat["givn"]
            guid = jsdat["guid"]
            job_id = jsdat["juid"]
            scom = jsdat["scom"]
            scon = jsdat["scon"]
            scombm = jsdat["scombm"]
            scombs = jsdat["scombs"]

        from_path = os.path.join(
            scom, os.path.dirname(file_path).replace(":", "{{DRIVE}}")
        )
        full_file_name = os.path.join(scom, file_path.replace(":", "{{DRIVE}}"))
        mime_type="folder"
        if os.path.isfile(src_folder):
            mime_type = "file"
        # else:
        #     mime_type = "file" if os.path.isfile(file_path) else "folder"
        file_name = ""
        x = float(jsvkrgs.get("filesdone",0))
        nx = float(jsvkrgs.get("totalfiles",0))
        accuracy=100.00*(x/nx)
        sktio.emit(
            "backup_data",
            {
                "backup_jobs": [
                    {
                        "name": p_NameText,
                        "scheduled_time": datetime.datetime.fromtimestamp(
                            float(j_sta)
                        ).strftime("%H:%M:%S"),
                        "agent": jsvkrgs["epn"],
                        "progress_number": float(
                            100
                            * (
                                float(jsvkrgs["currentfile"])
                                - 1
                                + float(seq_num) / float(jsvkrgs["total_chunks"])
                            )
                        )
                        / float(jsvkrgs["totalfiles"]),
                        "accuracy": accuracy,
                        "finished": finished,                        
                        "id": j_sta,
                        "repo": repo
                    }
                ]
            },
        )

        if mime_type == "file":
            file_name = os.path.basename(file_path)
        done_all = 1 if jsvkrgs["totalfiles"] == jsvkrgs["currentfile"] else 0
        dbname = os.path.join(app.config["location"], scom)
        qrs = [
            (
                dbname,
                [
                    "INSERT or IGNORE INTO backups_M ("
                    + " id,date_time,from_computer,from_path,"
                    + " data_repo,mime_type,file_name,size,"
                    + " pNameText,pIdText,bkupType,sum_all,"
                    + " sum_done,done_all,status,mode,data_repod) "
                    + "VALUES("
                    + str(job_id)
                    + ","
                    + str(time())
                    + ","
                    + "'"
                    + scon
                    + "',"
                    + "'"
                    + src_folder  #from_path
                    + "',"
                    + "'NAS',"
                    + "'"
                    + mime_type
                    + "',"
                    + "'',"
                    + "0,"
                    + "'"
                    + p_NameText
                    + "',"
                    + "'"
                    + p_IdText
                    + "',"
                    + "'"
                    + bkupType
                    + "',"
                    + ""
                    + str(jsvkrgs["totalfiles"])
                    + ","
                    + ""
                    + str(jsvkrgs["filesdone"])# str(jsvkrgs["currentfile"])
                    + ","
                    + ""
                    + str(done_all)
                    + ","
                    + "'',"
                    + "'',"
                    + "''"
                    + ") "
                    # + ") ON conflict(id) DO UPDATE SET"
                    
                ],
            ),
            (
                dbname,
                [
                    "update backups_M  "
                    + " set sum_done = " + str(jsvkrgs["filesdone"])  
                    + " where id = " + str(job_id)  
                ],
            )
        ]
        results = s_manager.execute_queries(qrs)
        if (str(results[dbname][0]).capitalize()).__contains__("success"):
            qrs = [
                (
                    dbname,
                    [
                        # id,name,date_time,from_computer,from_path,
                        # data_repo,mime_type,size,file_name,full_file_name,
                        # log,pNameText,pIdText,bkupType,sum_all,sum_done,done_all,status,mode,data_repod
                        " INSERT or IGNORE INTO backups("
                        + " id,name,date_time,from_computer,from_path,"
                        + " data_repo,mime_type,file_name,full_file_name,size,"
                        + " log, pNameText,pIdText,bkupType,sum_all,"
                        + " sum_done,done_all,status,mode,data_repod) "
                        + "VALUES("
                        + str(time())
                        + ","
                        + str(job_id)
                        + ","
                        + str(int(time()))
                        + ","
                        + "'"
                        + scon
                        + "',"
                        + "'"
                        + from_path
                        + "',"
                        + "'NAS',"
                        + "'"
                        + mime_type
                        + "',"
                        + "'"
                        + file_name
                        + "',"
                        + "'"
                        + full_file_name
                        + "',"
                        + "0,"
                        + "'"
                        + tcc
                        + "',"
                        + "'"
                        + p_NameText
                        + "',"
                        + "'"
                        + p_IdText
                        + "',"
                        + "'"
                        + bkupType
                        + "',"
                        + "0,"
                        + "0,"
                        + "0,"
                        + "'',"
                        + "'',"
                        + "''"
                        + ") "
                        # + " ON conflict(id) DO UPDATE SET"
                    ],
                )
            ]
        results = s_manager.execute_queries(qrs)
        if file_name and not abort and seq_num == total_chunks:
            final_manifest_path = _final_manifest_path(tcc, file_name, j_sta)
            temp_manifest_path = _manifest_path(temp_manifest_dir, file_name, j_sta)
            if os.path.exists(temp_manifest_path):
                try:
                    os.makedirs(os.path.dirname(final_manifest_path), exist_ok=True)
                    shutil.move(temp_manifest_path, final_manifest_path)
                    log_event(
                        logger,
                        logging.INFO,
                        ensure_job_id(j_sta),
                        "backup",
                        file_path=file_name,
                        extra={"event": "manifest_finalized", "manifest_path": final_manifest_path},
                    )
                except Exception as manifest_error:
                    log_event(
                        logger,
                        logging.ERROR,
                        ensure_job_id(j_sta),
                        "backup",
                        file_path=file_name,
                        error_code="MANIFEST_SAVE_FAILED",
                        error_message=str(manifest_error),
                        extra={"event": "manifest_failed"},
                    )

        # for x in jsdat["chunks"]:
        #     print("")
        #     print("===========================================")
        #     print(x)
        #     print("===========================================")
        #     print("")
        return 200
    except:
        print("")
        bdone = False
        return 500




@app.route("/uploaddddd", methods=["POST"])
@app.route("/upload", methods=["POST"])
def upload_file():
    import gzip

    bdone = True
    sql_logs = None
    abort = "True" == request.headers.get("abt", "False")

    file_name = request.headers.get("File-Name")
    seq_num = int(request.headers.get("quNu", -1))
    total_chunks = int(request.headers.get("tc", 0))
    bop = int(request.headers.get("bop", False))
    chunk_hash = request.headers.get("chkh")
    file_hash = request.headers.get("filehash")
    currentfile = request.headers.get("currentfile")
    job_id = ensure_job_id(
        request.headers.get("job_id")
        or request.headers.get("jsta")
        or request.headers.get("tfi")
    )
    log_chunk_event(
        logger,
        logging.DEBUG,
        job_id,
        "backup",
        file_path=file_name,
        file_id=request.headers.get("fileid"),
        chunk_index=seq_num,
        extra={"event": "chunk_received", "total_chunks": total_chunks},
    )

    
    decompressed_chunk = None
    if request.data:
        compressed_chunk = request.data
        try:
            decompressed_chunk = gzip.decompress(compressed_chunk)
        except:
            log_event(
                logger,
                logging.WARNING,
                job_id,
                "backup",
                file_path=file_name,
                file_id=request.headers.get("fileid"),
                chunk_index=seq_num,
                error_code="DECOMPRESS_FALLBACK",
                error_message="gzip.decompress failed; using raw chunk",
                extra={"event": "chunk_decompress_fallback"},
            )
            decompressed_chunk = compressed_chunk

    
    if request.files:
        if 'file' not in request.files:
            log_event(
                logger,
                logging.ERROR,
                job_id,
                "backup",
                file_path=file_name,
                file_id=request.headers.get("fileid"),
                chunk_index=seq_num,
                error_code="UPLOAD_NO_FILE_PART",
                error_message="No file part in request",
                extra={"event": "chunk_failed"},
            )
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            log_event(
                logger,
                logging.ERROR,
                job_id,
                "backup",
                file_path=file_name,
                file_id=request.headers.get("fileid"),
                chunk_index=seq_num,
                error_code="UPLOAD_EMPTY_FILENAME",
                error_message="Empty filename in upload",
                extra={"event": "chunk_failed"},
            )
            return 'No selected file', 400
        if file:
            filename = file.filename
            compressed_chunk = file.read()  # Write bytes directly.
            decompressed_chunk = compressed_chunk

    checksum_mismatch = False
    checksum_error = None
    computed_hash = None
    if chunk_hash and decompressed_chunk is not None and decompressed_chunk != GD_DATA_BLOCK:
        try:
            computed_hash = hashlib.sha256(decompressed_chunk).hexdigest()
            if computed_hash != str(chunk_hash):
                checksum_mismatch = True
            log_event(
                logger,
                logging.INFO,
                job_id,
                "backup",
                file_path=file_name,
                file_id=request.headers.get("fileid"),
                chunk_index=seq_num,
                extra={"event": "chunk_checksum_ok"},
            )
        except Exception as hash_error:
            checksum_mismatch = True
            checksum_error = str(hash_error)
            try:
                decompressed_chunk = gzip.decompress(compressed_chunk)
            except:
                log_event(
                    logger,
                    logging.WARNING,
                    job_id,
                    "backup",
                    file_path=file_name,
                    file_id=request.headers.get("fileid"),
                    chunk_index=seq_num,
                    error_code="DECOMPRESS_FALLBACK",
                    error_message="gzip.decompress failed; using raw chunk",
                    extra={"event": "chunk_decompress_fallback"},
                )
                decompressed_chunk = compressed_chunk
    elif chunk_hash and decompressed_chunk == GD_DATA_BLOCK:
        # GDrive: verify using Drive's sha256Checksum from gfidi when present
        gfidi_raw = request.headers.get("gfidi", "")
        drive_sha256 = None
        if gfidi_raw:
            try:
                raw = gfidi_raw.decode("utf-8") if isinstance(gfidi_raw, bytes) else gfidi_raw
                gfidi_obj = json.loads(raw) if raw else {}
                drive_sha256 = (gfidi_obj.get("sha256Checksum") or "").strip()
            except Exception:
                pass
        if drive_sha256:
            client_chkh = (str(chunk_hash) or "").strip()
            if client_chkh and (drive_sha256.lower() == client_chkh.lower()):
                log_event(
                    logger,
                    logging.INFO,
                    job_id,
                    "backup",
                    file_path=file_name,
                    file_id=request.headers.get("fileid"),
                    chunk_index=seq_num,
                    extra={"event": "chunk_checksum_ok", "reason": "gdrive_sha256_match"},
                )
            else:
                checksum_mismatch = True
                checksum_error = "gdrive_sha256_mismatch"
                log_event(
                    logger,
                    logging.WARNING,
                    job_id,
                    "backup",
                    file_path=file_name,
                    file_id=request.headers.get("fileid"),
                    chunk_index=seq_num,
                    extra={
                        "event": "chunk_checksum_failed",
                        "reason": "gdrive_sha256_mismatch",
                        "client_chkh": client_chkh[:16] + "..." if len(client_chkh) > 16 else client_chkh,
                        "drive_sha256": drive_sha256[:16] + "..." if len(drive_sha256) > 16 else drive_sha256,
                    },
                )
        else:
            log_event(
                logger,
                logging.INFO,
                job_id,
                "backup",
                file_path=file_name,
                file_id=request.headers.get("fileid"),
                chunk_index=seq_num,
                extra={"event": "chunk_checksum_skipped", "reason": "gdrive_metadata_only"},
            )
    try:
        del compressed_chunk
    except:
        pass
    
    import base64
    block= b'\x08\x1ed\x1e\xc8\x98s^I\x92Slk\xe6\\!\xc7KuL\x83!^\x1d\xf2w\xd4$\xa1\xcehI\t\x00\x0f?yU\x7f\xb8\x10\xfazN6\xb3\xe5\x9f\x14\xc7ca\x7fMG\xff\x98\x1b\xc8\xd1~/\xa3_'
    #block= b'\xf4\x0b\x1c\x18\x8ce\xc2M\xed\xb2\xb0\x12\xc7\xa4\xe4,\x14\x85\x92\x9b\x0e\x07\xc2\x8e\xee\x8b\xf6\xa3\xabD\x1bC3\xeba$\xad\x82\xf1\xeb\xa8\xee\xd0\xe4\xdd\xe4qQ\xb3\xa9>\xfcA\x8d\xcc\xe97-\xf2\xf6\x00\xff\x15)'
    block =b"{44A0C353-B685-4F9E-A3CF-08050440A814}"
    bNoBackup=False
    # if not app.config.get(tfi,None):
    #     app.config[tfi]=Decimal(0)
    if (decompressed_chunk) == block:
        print("this entry should be copied from the repo to repo")
        bNoBackup=True
    try:

        tfi= request.headers.get("tfi",None)
        file_id = request.headers.get("fileid")
        chunk_hash = request.headers.get("chkh")
        file_hash = request.headers.get("filehash")
        decimal.getcontext().prec = 28
        #app.config.setdefault(tfi, 0.0)
        app.config.setdefault(tfi, Decimal(0))
        
        tccsrc = request.headers.get("tccsrc")
        tccsrc = base64.b64decode(tccsrc)
        tccsrc = gzip.decompress(tccsrc)
        tccsrc = tccsrc.decode("UTF-8") 

        tcc = request.headers.get("tcc")
        tcc = base64.b64decode(tcc)
        tcc = gzip.decompress(tcc)
        tcc = tcc.decode("UTF-8")
        # os.makedirs(tcc, exist_ok=True)

        epc = request.headers.get("epc")
        epc = base64.b64decode(epc)
        epc = gzip.decompress(epc)
        epc = epc.decode("UTF-8")

        epn = request.headers.get("epn")
        epn = base64.b64decode(epn)
        epn = gzip.decompress(epn)
        epn = epn.decode("UTF-8")

        tf = request.headers.get("tf")
        tf = base64.b64decode(tf)
        tf = gzip.decompress(tf)
        tf = tf.decode("UTF-8")

        pna = request.headers.get("pna")
        pna = base64.b64decode(pna)
        pna = gzip.decompress(pna)
        pna = pna.decode("UTF-8")

        ahi = request.headers.get("ahi")
        ahi = base64.b64decode(ahi)
        ahi = gzip.decompress(ahi)
        ahi = ahi.decode("UTF-8")

        rep = request.headers.get("rep")
        rep = base64.b64decode(rep)
        rep = gzip.decompress(rep)
        rep = rep.decode("UTF-8")

        mimet = request.headers.get("mimet")
        mimet = base64.b64decode(mimet)
        mimet = gzip.decompress(mimet)
        mimet = mimet.decode("UTF-8")

        pNameText = request.headers.get("pNameText")
        pNameText = base64.b64decode(pNameText)
        pNameText = gzip.decompress(pNameText)
        pNameText = pNameText.decode("UTF-8")

        pIdText = request.headers.get("pIdText")
        pIdText = base64.b64decode(pIdText)
        pIdText = gzip.decompress(pIdText)
        pIdText = pIdText.decode("UTF-8")

        bkupType = request.headers.get("bkupType")
        bkupType = base64.b64decode(bkupType)
        bkupType = gzip.decompress(bkupType)
        bkupType = bkupType.decode("UTF-8")

        currentfile = request.headers.get("currentfile")
        currentfile = base64.b64decode(currentfile)
        currentfile = gzip.decompress(currentfile)
        currentfile = currentfile.decode("UTF-8")

        totalfiles = request.headers.get("totalfiles")
        totalfiles = base64.b64decode(totalfiles)
        totalfiles = gzip.decompress(totalfiles)
        totalfiles = totalfiles.decode("UTF-8")

        stat = request.headers.get("stat")
        stat = base64.b64decode(stat)
        stat = gzip.decompress(stat)
        stat = stat.decode("UTF-8")
        stat = json.loads(stat)

        if total_chunks>0:
            #app.config[tfi] = app.config.get(tfi,0.0)+ float( Decimal(100.0)*Decimal(seq_num)/Decimal(total_chunks)/Decimal(totalfiles))
            #app.config[tfi] = app.config.get(tfi,0.0)+ float( Decimal(100.0)*Decimal(1)/Decimal(total_chunks)/Decimal(totalfiles))
            
            #app.config[tfi] = Decimal(app.config.get(tfi,0))+ Decimal( Decimal(100)*Decimal(1)/Decimal(total_chunks)/Decimal(totalfiles))
            app.config[tfi] = D(app.config.get(tfi, 0)) + (D(100) / D(total_chunks) / D(totalfiles))
            #print(f"==================================================================")
            #print(f"===========>                              ======================")
            #print(f"===========>                              ======================")
            #print(f"===========>                              ======================")
            #print(f"===========>app.config[{tfi}] = {app.config[tfi]}")
            #print(f"===========>                              ======================")
            #print(f"===========>                              ======================")
            #print(f"===========>                              ======================")
            #print(f"===========>                              ===========================")

    except Exception as header_error:
        log_event(
            logger,
            logging.ERROR,
            job_id,
            "backup",
            file_path=file_name,
            file_id=request.headers.get("fileid"),
            chunk_index=seq_num,
            error_code="HEADER_DECODE_FAILED",
            error_message=str(header_error),
            extra={"event": "chunk_failed"},
        )
        print("")
        bdone = False
        return 500

    try:
        givn = request.headers.get("givn")
        givn = base64.b64decode(givn)
        givn = gzip.decompress(givn)
        givn = givn.decode("UTF-8")
    except:
        print("")

    try:
        j_sta = request.headers.get("jsta", float(1.0))
        j_sta = base64.b64decode(j_sta)
        j_sta = gzip.decompress(j_sta)
        j_sta = j_sta.decode("UTF-8")
        j_sta = float(j_sta)

    except:
        print("")

    try:
        repod = request.headers.get("repod", None)
        if repod:
            repod = base64.b64decode(str(repod))
            repod = gzip.decompress(repod)
            repod = repod.decode("UTF-8")

        repod = float(1.0)

    except:
        repod = float(1.0)
        print("")
        
    try:
        fidi = request.headers.get("fidi", "")
        # fidi = base64.b64decode(str(fidi))
        # fidi = gzip.decompress(fidi)
        # fidi = fidi.decode("UTF-8")
    except:
        repod = float(1.0)
        print("")

    try:
        gfidi = request.headers.get("gfidi", "")
    except:
        pass

    bGDBackup=False
    bOneDrive_backup = False
    bAWS_backup = False
    bAZURE_backup = False

    if (decompressed_chunk) == GD_DATA_BLOCK:
        print("this entry should save cloud metadata")
        rep_upper = str(rep).upper().replace(" ", "")
        if rep_upper in ["GOOGLEDRIVE", "GDRIVE"]:
            bGDBackup = True
        elif rep_upper == "ONEDRIVE":
            bOneDrive_backup = True
        elif rep_upper == "AWSS3":
            bAWS_backup = True
        elif rep_upper == "AZURE":
            bAZURE_backup = True


    # try:

    #     #if not os.path.exists(os.path.join(app.config["location"], f"{epc}.db")):
    #     x = requests.post(
    #         request.url_root + "create_database", json={"database_name": os.path.join(app.config["location"], f"{epc}.db")}
    #     )
    #     print(x.text)
    # except:
    #     print("")

    try:
        if not os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], tcc)):
            os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], tcc), exist_ok=True)
    except:
        print("")
    if str(rep).upper() == "UNC":
        job_id = ensure_job_id(j_sta)
        log_event(
            logger,
            logging.INFO,
            job_id,
            "backup",
            file_path=file_name,
            file_id=file_id,
            chunk_index=seq_num,
            extra={"event": "file_assembly_start"},
        )
        bdone,sql_logs = save_final(
            file_name,
            total_chunks,
            tcc,
            abort,
            epc=epc,
            epn=epn,
            tf=tf,
            pna=pna,
            rep=rep,
            ahi=ahi,
            j_sta=j_sta,
            mimet=mimet,
            pNameText=pNameText,
            pIdText=pIdText,
            bkupType=bkupType,
            currentfile=currentfile,
            totalfiles=totalfiles,
            givn=givn,bNoBackup=bNoBackup
            ,fidi=fidi,tfi=tfi
        )
        log_event(
            logger,
            logging.INFO if bdone else logging.ERROR,
            job_id,
            "backup",
            file_path=file_name,
            file_id=file_id,
            chunk_index=seq_num,
            error_code="" if bdone else "FILE_ASSEMBLY_FAILED",
            error_message="" if bdone else "save_final returned failure",
            extra={"event": "file_assembly_end"},
        )
        thiscurrentfile = currentfile if bdone else float(currentfile) - 1
        if currentfile>0:
            if thiscurrentfile ==0:
                thiscurrentfile=1

        sktio.emit(
            "backup_data",
            {
                "backup_jobs": [
                    {
                        "name": pNameText,
                        "scheduled_time": datetime.datetime.fromtimestamp(
                            float(j_sta)
                        ).strftime("%H:%M:%S"),
                        "agent": epn,
                        # "progress_number": float(100 * (float(thiscurrentfile)))
                        # / float(totalfiles), 
                        "progress_number": float(str(app.config[tfi])),
                        "id": j_sta,
                        "repo": rep
                    }
                ]
            },
        )
        if bdone:
            # return (
            #     #f"file_name {seq_num} of {total_chunks} uploaded successfully"
            # )

            return (
                jsonify(
                    result={
                        "currentfile": currentfile,
                        "seq_num": seq_num,
                        "query":sql_logs,
                        "status": "success",
                    }
                ),
                200,
            )
        else:
            # return ("500", 500)
            return (
                jsonify(
                    result={
                        "currentfile": currentfile,
                        "seq_num": seq_num,
                        "query":sql_logs,
                        "status": "failed",
                    }
                ),
                200,
            )

    if bdone:
        if not abort:
            if save_temp(
                file_name,
                seq_num,
                decompressed_chunk,
                tcc,
                abort,
                total_chunks,
                epc,
                epn=epn,
                tf=tf,
                pna=pna,
                rep=rep,
                ahi=ahi,
                j_sta=j_sta,
                mimet=mimet,
                pNameText=pNameText,
                pIdText=pIdText,
                bkupType=bkupType,
                currentfile=currentfile,
                totalfiles=totalfiles,
                givn=givn,bNoBackup=bNoBackup,fidi=fidi,tfi=tfi,gfidi=gfidi,
                chunk_hash=chunk_hash,file_hash=file_hash,
                bGD_backup=bGDBackup, bOneDrive_backup=bOneDrive_backup
            ):
                print(f"{seq_num}/{total_chunks} saved")
                
                # sktio.emit("backup_data",f"{file_name} {float(100*(float(currentfile)+seq_num/total_chunks))/float(totalfiles)} saved")

                # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": "14:00:00", "agent": epn , "progress_number": float(100*(float(currentfile)-1+seq_num/total_chunks))/float(totalfiles)}]})
                print(f"===========>app.config[{tfi}] = {float(str(app.config[tfi]))}")
                if total_chunks>0:
                    sktio.emit(
                        "backup_data",
                        {
                            "backup_jobs": [
                                {
                                    "name": pNameText,
                                    "scheduled_time": datetime.datetime.fromtimestamp(
                                        float(j_sta)
                                    ).strftime("%H:%M:%S"),
                                    "agent": epn,     #float(100*  (float(currentfile)+      seq_num/       total_chunks))/float(totalfiles)
                                    # "progress_number": float(100 * (float(currentfile)-1+float(seq_num)/float(total_chunks)))
                                    # / float(totalfiles),
                                    "progress_number": float(str(app.config[tfi])),
                                    "id": j_sta,
                                    "repo": rep
                                }
                            ]
                        },
                    )

                if save_all(
                    file_name, total_chunks, tcc, abort, epc, currentfile, totalfiles,bNoBackup=bNoBackup,tfi=tfi,
                    bGD_backup=bGDBackup, bOneDrive_backup=bOneDrive_backup,
                    bAWS_backup=bAWS_backup, bAZURE_backup=bAZURE_backup
                ):
                    job_id = ensure_job_id(j_sta)
                    log_event(
                        logger,
                        logging.INFO,
                        job_id,
                        "backup",
                        file_path=file_name,
                        file_id=file_id,
                        chunk_index=seq_num,
                        extra={"event": "file_assembly_start"},
                    )
                    bdone,sql_logs = save_final(
                        file_name,
                        total_chunks,
                        tcc,
                        abort,
                        epc=epc,
                        epn=epn,
                        tf=tf,
                        pna=pna,
                        rep=rep,
                        ahi=ahi,
                        j_sta=j_sta,
                        mimet=mimet,
                        pNameText=pNameText,
                        pIdText=pIdText,
                        bkupType=bkupType,
                        currentfile=currentfile,
                        totalfiles=totalfiles,
                        givn=givn,
                        tccsrc=tccsrc,bNoBackup=bNoBackup,fidi=fidi,tfi=tfi,bGD_backup=bGDBackup,bOneDrive_backup=bOneDrive_backup,bAWS_backup=bAWS_backup,bAZURE_backup=bAZURE_backup, stat=stat, file_id=file_id,
                        gfidi_from_headers=request.headers.get("gfidi") if bGDBackup else None,
                        chunk_index=seq_num,
                    )
                    log_event(
                        logger,
                        logging.INFO if bdone else logging.ERROR,
                        job_id,
                        "backup",
                        file_path=file_name,
                        file_id=file_id,
                        chunk_index=seq_num,
                        error_code="" if bdone else "FILE_ASSEMBLY_FAILED",
                        error_message="" if bdone else "save_final returned failure",
                        extra={"event": "file_assembly_end"},
                    )
                    thiscurrentfile = currentfile if bdone else float(currentfile) - 1
                    try:
                        sktio.emit(
                            "backup_data",
                            {
                                "backup_jobs": [
                                    {
                                        "name": pNameText,
                                        "scheduled_time": datetime.datetime.fromtimestamp(
                                            float(j_sta)
                                        ).strftime("%H:%M:%S"),
                                        "agent": epn,
                                        # "progress_number": float(
                                        #     100 * (float(thiscurrentfile)+float(seq_num)/float(total_chunks))
                                        # )
                                        # / float(totalfiles),
                                        "progress_number": float(str(app.config[tfi])),
                                        "id": j_sta,
                                        "repo": rep
                                    }
                                ]
                            },
                        )
                    except Exception as exs:
                        print(exs)

                    if bdone:
                        # return (
                        #     #f"file_name {seq_num} of {total_chunks} uploaded successfully"
                        # )
                        return (
                            jsonify(
                                result={
                                    "currentfile": currentfile,
                                    "seq_num": seq_num,
                                    "query":sql_logs,
                                    "status": "success",
                                }
                            ),
                            200,
                        )
                    else:
                        # return ("500", 500)
                        logger.warning("this goes in else when bdone not true, this is failed")
                        return (
                            jsonify(
                                result={
                                    "currentfile": currentfile,
                                    "seq_num": seq_num,
                                    "query":sql_logs,
                                    "status": "failed",
                                }
                            ),
                            200,
                        )
                else:
                    return (
                        jsonify(
                            result={
                                "currentfile": currentfile,
                                "seq_num": seq_num,
                                "query":sql_logs,
                                "status": "success",
                            }
                        ),
                        200,
                    )
            else:
                logger.warning(f"This goes in else condition when temp not create, this is failed")
                return (
                    jsonify(
                        result={
                            "currentfile": currentfile,
                            "seq_num": seq_num,
                            "query":sql_logs,
                            "status": "failed",
                        }
                    ),
                    200,
                )
        else:
            bdone,sql_logs = save_final(
                file_name,
                total_chunks,
                tcc,
                abort,
                epc=epc,
                epn=epn,
                tf=tf,
                pna=pna,
                rep=rep,
                ahi=ahi,
                j_sta=j_sta,
                mimet=mimet,
                pNameText=pNameText,
                pIdText=pIdText,
                bkupType=bkupType,
                currentfile=currentfile,
                totalfiles=totalfiles,
                givn=givn,bNoBackup=bNoBackup,fidi=fidi
            )
            thiscurrentfile = currentfile if bdone else float(currentfile) - 1
            sktio.emit(
                "backup_data",
                {
                    "backup_jobs": [
                        {
                            "name": pNameText,
                            "scheduled_time": datetime.datetime.fromtimestamp(
                                float(j_sta)
                            ).strftime("%H:%M:%S"),
                            "agent": epn,
                            # "progress_number": float(100 * (float(thiscurrentfile)+float(seq_num)/float(total_chunks)))
                            # / float(totalfiles),
                            "progress_number": float(str(app.config[tfi])),
                            "id": j_sta,
                            "repo": rep
                        }
                    ]
                },
            )
            if bdone:
                # with client_backups_data_lock:
                #     data = load_backup_data()
                #     new_item = {
                #         "ip_address": epc,
                #         "agent_name": epn,
                #         "path": tcc,
                #         "file_name": file_name,
                #         "size":0
                #     }
                #     data.append(new_item)
                #     save_backup_data(data)
                # return (
                #     f"file_name {seq_num} of {total_chunks} upload aborted successfully"
                # )
                return (
                    jsonify(
                        result={
                            "currentfile": currentfile,
                            "seq_num": seq_num,
                            "query":sql_logs,
                            "status": "success",
                        }
                    ),
                    200,
                )
            else:
                logger.warning(f"This goes in else in else when bdone is not true, this is failed")
                return (
                    jsonify(
                        result={
                            "currentfile": currentfile,
                            "seq_num": seq_num,
                            "query":sql_logs,
                            "status": "failed",
                        }
                    ),
                    200,
                )

########################################################################
def _manifest_name(file_name, tfi):
    safe_tfi = str(tfi or "default")
    return f"{file_name}_{safe_tfi}.manifest.json"


def _manifest_path(temp_dir, file_name, tfi):
    return os.path.join(temp_dir, _manifest_name(file_name, tfi))


def _load_manifest(temp_dir, file_name, tfi):
    manifest_path = _manifest_path(temp_dir, file_name, tfi)
    if not os.path.exists(manifest_path):
        return {"total_chunks": 0, "file_hash": "", "chunks": {}}
    with open(manifest_path, "r", encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def _save_manifest(temp_dir, file_name, tfi, manifest):
    manifest_path = _manifest_path(temp_dir, file_name, tfi)
    with open(manifest_path, "w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file)


def _manifest_folder(tcc_value):
    value = str(tcc_value or "")
    trimmed = value.strip()
    if trimmed.startswith("{") and trimmed.endswith("}"):
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
    return value


def _final_manifest_path(tcc, file_name, j_sta):
    return os.path.join(
        app.config["UPLOAD_FOLDER"],
        _manifest_folder(tcc),
        f"{file_name}_{str(j_sta)}.manifest.json",
    )


def save_temp(
    file_name,
    seq_num,
    chunk,
    tcc,
    abort,
    total_chunks,
    obj,
    epn,
    tf,
    pna,
    rep,
    ahi,
    j_sta,
    mimet,
    pNameText,
    pIdText,
    bkupType,
    currentfile,
    totalfiles,
    givn="",bNoBackup=False,fidi="",tfi=None,gfidi=None,
    chunk_hash=None,file_hash=None,
    bsame_backup=False,
    bGD_backup=False,
    bAWS_backup=False,
    bAZURE_backup=False,
    bOneDrive_backup=False,
):
    import gzip
    import os
    import tempfile

    job_id = ensure_job_id(j_sta)
    log_chunk_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        chunk_index=seq_num,
        extra={"event": "chunk_write_start"},
    )
    try:
        temp_dir = os.path.join(add_unc_temppath(), tcc)
        if tfi:
            temp_dir = os.path.join(add_unc_temppath(), tcc,tfi)  
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, f"{file_name}_{seq_num}")
        temp_file_path = os.path.join(temp_dir, f"{file_name}_{seq_num}.gz")
        delimiter = b"---CHUNK-END---"  # Define a unique delimiter
        # with open(temp_file_path, "wb") as temp_file:  # Open file with gzip compression
        #     temp_file.write(chunk)
        

        with gzip.open(
            temp_file_path, "wb", 9
        ) as temp_file:  # Open file with gzip compression
            if bGD_backup: # or bAWS_backup or bAZURE_backup or bOneDrive_backup :
                if isinstance(gfidi, bytes):
                    temp_file.write(gfidi)
                elif isinstance(gfidi, str):
                    temp_file.write(gfidi.encode("utf-8"))
                else:
                    temp_file.write(json.dumps(gfidi).encode("utf-8"))
            elif bOneDrive_backup :
                pass
            else:
                temp_file.write(chunk)

            #temp_file.write(delimiter)
            # s_manager = SQLiteManager()
            # dbname = os.path.join(app.config["location"], obj)
            # qrs = [
            #     (
            #         dbname,
            #         [
            #             "insert * FROM backups where "
            #             + "id = "
            #             + str(id)
            #             + " and name = "
            #             + str(pid)
            #         ],
            #     )
            # ]
            # results = s_manager.execute_queries(qrs)
        manifest = _load_manifest(temp_dir, file_name, tfi)
        manifest["total_chunks"] = int(total_chunks or manifest.get("total_chunks") or 0)
        if file_hash:
            manifest["file_hash"] = str(file_hash)
        if chunk_hash:
            manifest.setdefault("chunks", {})
            manifest["chunks"][str(seq_num)] = str(chunk_hash)
        _save_manifest(temp_dir, file_name, tfi, manifest)

        chunk_files = [f for f in os.listdir(temp_dir) if f.startswith(file_name + "_")]
        sktio.emit(
                "backup_data",
                {
                    "backup_jobs": [
                        {
                            "name": pNameText,
                            "scheduled_time": datetime.datetime.fromtimestamp(
                                float(j_sta)
                            ).strftime(
                                "%H:%M:%S"
                            ),
                            "agent": epn,
                            "progress_number_file": float(100 * (float(len(chunk_files))))/float(total_chunks),
                            "id": j_sta,
                            "repo": rep,
                            "filename":file_name
                        }
                    ]
                },
            )
        log_chunk_event(
            logger,
            logging.INFO,
            job_id,
            "backup",
            file_path=file_name,
            chunk_index=seq_num,
            extra={"event": "chunk_write_end"},
        )
    except Exception as deee:
        log_event(
            logger,
            logging.ERROR,
            job_id,
            "backup",
            file_path=file_name,
            chunk_index=seq_num,
            error_code="CHUNK_WRITE_FAILED",
            error_message=str(deee),
            extra={"event": "chunk_failed"},
        )
        print(str(deee))
        logger.warning(f"Error comes when save temp data Error: {str(deee)}")
        return False  # raise

    return True


def save_all(file_name, total_chunks, tcc, abort, 
             epn, currentfile, totalfiles,bNoBackup=False,tfi=None,
             bGD_backup =False, 
             bAWS_backup  =False, 
             bAZURE_backup =False, 
             bOneDrive_backup =False):
    import gzip
    import os
    import tempfile
    if bNoBackup:
        return bNoBackup
    if bGD_backup or bOneDrive_backup or bAWS_backup or bAZURE_backup:
        return True
    try:
        temp_dir = os.path.join(add_unc_temppath(), tcc)
        if tfi:
            temp_dir = os.path.join(add_unc_temppath(), tcc,tfi)
        chunk_files = [f for f in os.listdir(temp_dir) if f.startswith(file_name + "_")]
        return len(chunk_files) == total_chunks
    except Exception as deee:
        print(str(deee))
        raise

    return False


def get_save_stats(file_name, total_chunks, tcc, abort, epn,tccsrc,tfi=None):
    import gzip
    import os
    import tempfile

    try:
        temp_dir = os.path.join(add_unc_temppath(), tcc,tfi)
        if tfi:
            temp_dir = os.path.join(add_unc_temppath(), tcc,tfi)
        chunk_files = [f for f in os.listdir(temp_dir) if f.startswith(file_name + "_")]
        return len(chunk_files), (len(chunk_files) * 100) / total_chunks
    except Exception as deee:
        print(str(deee))
        return 0, 0
    # raise

from email.utils import parsedate_to_datetime
def get_date(source: str = ""):
    """
    Wrapper function to fetch date from multiple sources.
    
    Parameters:
        source (str): "online", "pc", or "other".
                      Default ("") → try online first, else fallback to PC.
    
    Returns:
        dict { "source": string, "date": datetime.date }
    """

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

##030126
# def unique_time_float():
#     import time
#     base = time.time()
#     nano = time.time_ns() % 1_000_000_000
#     tid = threading.get_ident() % 1000
#     return base + ((nano + tid) / 1e18)

# global, process-safe counter
_last_ts = 0.0
_seq = 0
_lock = threading.Lock()

def unique_time_float():
    import time
    global _last_ts, _seq

    with _lock:

        ts = round(time.time(), 6)  # microsecond precision ONLY

        if ts == _last_ts:
            _seq += 1
            # add smallest representable increment
            ts += _seq * 1e-6
        else:
            _seq = 0
            _last_ts = ts
        return ts

##030126

import base64
def save_final(
    file_name,
    total_chunks,
    tcc,
    abort,
    epc,
    epn,
    tf,
    pna,
    rep,
    ahi,
    j_sta,
    mimet,
    pNameText,
    pIdText,
    bkupType,
    currentfile,
    totalfiles,
    givn="",
    tccsrc="",bNoBackup=False,fidi="",tfi=None,
    bGD_backup=False,
    bAWS_backup=False,
    bAZURE_backup=False,
    bOneDrive_backup=False,
    stat = None,
    backup_logs_id=0.0, file_id = None,
    gfidi_from_headers=None,
    chunk_index=None,
):
    import gzip
    import os
    import tempfile
    import hashlib
    # if not bNoBackup: 
    #     bNoBackup ="full"
    thiscurrentfile = currentfile
    sql_logs = None
    sql_main = None
    fid = ""
    fid_list = []
    if backup_logs_id == 0.0:
        backup_logs_id = unique_time_float()
    bdone = True
    isMetaFile=False
    xsum_chunks =0
    output_file_pathgd = os.path.join(tcc, f"{file_name}_{str(j_sta)}.gz")
    output_file_path = os.path.join(
        app.config["UPLOAD_FOLDER"], tcc, f"{file_name}_{str(j_sta)}.gz"
    )
    if not abort:
        # GDrive/OneDrive/AWS/Azure: client uploads to cloud directly; no chunk files on server.
        # Skip temp_dir/chunk_files/manifest checks and only persist metadata to backups_M.
        if bGD_backup or bOneDrive_backup or bAWS_backup or bAZURE_backup:
            try:
                h = hashlib.md5()
                h.update(b"")
                gidn = None
                if gfidi_from_headers:
                    try:
                        raw = gfidi_from_headers.decode("utf-8") if isinstance(gfidi_from_headers, bytes) else gfidi_from_headers
                        gidn = json.loads(raw) if isinstance(raw, str) and raw.strip().startswith("{") else raw
                    except Exception:
                        gidn = gfidi_from_headers
                size_val = (stat.get("size", 0) if stat else 0) or 0
                save_savelogdata(
                    file_name, total_chunks, tcc, abort, epc, epn, tf, pna, rep, ahi, j_sta,
                    mimet, pNameText, pIdText, bkupType, currentfile, totalfiles,
                    hash_function=h, output_file_path=output_file_pathgd,
                    mode_m="uploading", status_m="pending", mode_t="saving",
                    givn=givn, gidn=gidn, backup_logs_id=backup_logs_id, bdone=True,
                    tccsrc=tccsrc, fidi=fidi, size_data=size_val, file_id=file_id,
                    chunk_index=chunk_index,
                )
                return True, None
            except Exception as e:
                log_event(
                    logger, logging.ERROR, ensure_job_id(j_sta), "backup",
                    file_path=file_name, file_id=file_id,
                    error_code="GDRIVE_SAVE_METADATA_FAILED", error_message=str(e),
                    extra={"event": "save_savelogdata_failed"},
                )
                return False, None

        temp_dir = os.path.join(add_unc_temppath(), tcc)
        if tfi:
            temp_dir = os.path.join(add_unc_temppath(), tcc,tfi)
        chunk_files = [f for f in os.listdir(temp_dir) if f.startswith(file_name + "_")]
        manifest = _load_manifest(temp_dir, file_name, tfi)
        manifest_total = int(manifest.get("total_chunks") or 0)
        manifest_chunks = manifest.get("chunks") or {}
        if manifest_total != int(total_chunks):
            log_event(
                logger,
                logging.ERROR,
                ensure_job_id(j_sta),
                "backup",
                file_path=file_name,
                file_id=file_id,
                error_code="CHUNK_SEQUENCE_ERROR",
                error_message="Manifest total_chunks mismatch",
                extra={"event": "sequence_error", "expected": total_chunks, "manifest_total": manifest_total},
            )
            return False, None
        expected_indexes = {str(i) for i in range(1, int(total_chunks) + 1)}
        missing_indexes = sorted(expected_indexes - set(manifest_chunks.keys()))
        if missing_indexes:
            log_event(
                logger,
                logging.ERROR,
                ensure_job_id(j_sta),
                "backup",
                file_path=file_name,
                file_id=file_id,
                error_code="MISSING_CHUNKS",
                error_message="Missing chunk hashes in manifest",
                extra={"event": "missing_chunks", "missing": missing_indexes},
            )
            return False, None
        if len(chunk_files) != int(total_chunks):
            log_event(
                logger,
                logging.ERROR,
                ensure_job_id(j_sta),
                "backup",
                file_path=file_name,
                file_id=file_id,
                error_code="MISSING_CHUNKS",
                error_message="Missing chunk files on disk",
                extra={"event": "missing_chunks", "expected": total_chunks, "actual": len(chunk_files)},
            )
            return False, None
        chunk_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

        # output_file_path = os.path.join(tcc, f"{file_name}_{str(time())}.gz")
        l_file_data=b''
        input_file=None
        batch_size=5
        batch_file_count=1
        s_fileName=[]
        s_fileName_store=[]
        data_file_path=None
        if (str(rep).upper().replace(" ", "") in ["LAN","AWSS3","AZURE","ONEDRIVE","GOOGLEDRIVE","GDRIVE"]):
            isMetaFile=True
        
        try:
            # with open(
            #     output_file_path,
            #     "wb",
            # ) as output_file:
            if True:
                hash_function = hashlib.new("md5")
                if not bNoBackup:
                    processed_size = 0
                    # Create a temp merged file (fast append using Windows 'type')
                    merged_temp = os.path.join(temp_dir, f"{file_name}_{str(j_sta)}.gztmp")
                    if os.path.exists(merged_temp):
                        os.remove(merged_temp)

                    # chunk_no=0 ## uncomment for one-by-one file merge logic 

                

                    
                    
                    
                    if (str(rep).upper().replace(" ", "") in ["LAN","AWSS3","AZURE","ONEDRIVE","GOOGLEDRIVE","GDRIVE"]):

                        isMetaFile=True
                        ## following code is commented on 19/11/2025 it used for merging files using windows 
                        ## the logic merges file multiple chunk files once basis
                        # if len(chunk_files)==1:
                        for chunk_file in chunk_files:
                            chunk_file_path = os.path.join(temp_dir, chunk_file)
                            if bGD_backup:
                                with gzip.open(chunk_file_path, "rb") as f:
                                    data = f.read()
                                    f.close()
                                fid_list.append(json.loads(data.decode("utf-8")))
                            
                            data_file_path = os.path.join(
                                tcc, f"{chunk_file}_{str(j_sta)}.gz"
                            )
                            s_fileName_store.append(data_file_path)
                            
                            data_file_path = os.path.join(
                                app.config["UPLOAD_FOLDER"], tcc, f"{chunk_file}_{str(j_sta)}.gz"
                            )
                            
                            if (str(rep).upper().replace(" ", "") == "LAN" or True==True):
                                try:
                                    startupinfo = subprocess.STARTUPINFO()
                                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                                    startupinfo.wShowWindow = subprocess.SW_HIDE

                                    cmd = f'move /Y "{chunk_file_path}" "{data_file_path}"'
                                    subprocess.run(
                                        cmd,  # Command as string
                                        shell=True,  
                                        check=True,  # Must be boolean True, not string
                                        startupinfo=startupinfo,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        creationflags=subprocess.CREATE_NO_WINDOW  # Additional flag to prevent window
                                    )

                                    xsum_chunks +=1
                                except Exception as move_error1:
                                    print(str(move_error1))

                        with open(merged_temp, "w") as f:
                            json.dump(s_fileName_store, f)                              
                        
 
                    else:
                        ## following code is commented on 19/11/2025 it used for merging files using windows 
                        ## the logic merges file multiple chunk files once basis
                        if len(chunk_files)==1:
                            for chunk_file in chunk_files:
                                merged_temp = os.path.join(temp_dir, chunk_file)
                                xsum_chunks +=1
                        else:
                        
                            for chunk_file in chunk_files:
                                chunk_file_path = os.path.join(temp_dir, chunk_file)
                                s_fileName.append(chunk_file_path)
                                if batch_file_count % batch_size ==0:
                                    #now we have an array or a list that contains 10 files' name
                                    # we have to just merge that list with "+" character
                                    print ("+".join(s_fileName))
                                    if os.path.exists(merged_temp):
                                        subprocess.run(
                                            ["cmd.exe", "/c", "copy", "/b"] + [merged_temp,"+"] + "*+*".join(s_fileName).split("*") +[merged_temp],
                                            shell=False,
                                            check=True
                                        )
                                        xsum_chunks +=len(s_fileName)
                                    else:
                                    
                                        subprocess.run(
                                        ["cmd.exe", "/c", "copy", "/b"] + "*+*".join(s_fileName).split("*") +[merged_temp],
                                        shell=False,
                                        check=True
                                        )
                                        xsum_chunks +=len(s_fileName)
                                    sleep(.1)
                                    try:
                                        subprocess.run(
                                        ["cmd.exe", "/c", "del"  ] +"*,*".join(s_fileName).split("*"),
                                        shell=False,
                                        check=True
                                        )
                                    except Exception as e:
                                        pass

                                    s_fileName=[]
                            
                                batch_file_count+=1

                            if len(s_fileName)>0:
                                if os.path.exists(merged_temp):
                                    subprocess.run(
                                        ["cmd.exe", "/c", "copy", "/b"] + [merged_temp,"+"] + "*+*".join(s_fileName).split("*") +[merged_temp],
                                        shell=False,
                                        check=True
                                    )
                                    xsum_chunks +=len(s_fileName)
                                else:
                                    subprocess.run(
                                    ["cmd.exe", "/c", "copy", "/b"] + "*+*".join(s_fileName).split("*") +[merged_temp],
                                    shell=False,
                                    check=True
                                    )
                                    xsum_chunks +=len(s_fileName)
                                    
                                sleep(.1)
                                try:
                                    subprocess.run(
                                    ["cmd.exe", "/c", "del"  ] +"*,*".join(s_fileName).split("*"),
                                    shell=False,
                                    check=True
                                    )
                                except Exception as e:
                                    pass


            
                        ## following code is commented on 19/11/2025 it used for merging files using windows 
                        ## the logic merges chunk file one-by-one basis
                        # for chunk_file in chunk_files:
                        #     chunk_file_path = os.path.join(temp_dir, chunk_file)
                        #     sleep(.1)

                        #     # Append chunk using Windows fast native IO
                        #     if chunk_no==0 :
                        #         #["copy" ,"/b" ,f'"{chunk_file_path}"', f'"{merged_temp}"'],
                        #         subprocess.run(
                        #             ["cmd.exe", "/c", "copy", "/b", chunk_file_path , merged_temp],
                        #             shell=False,
                        #             check=True
                        #         )
                        #     else:
                        #         subprocess.run(
                        #         ["cmd.exe", "/c", "copy", "/b", merged_temp,"+", chunk_file_path , merged_temp],
                        #         shell=False,
                        #         check=True
                        #     )
                        #     #processed_size += os.path.getsize(merged_temp)
                            
                        #     if os.path.exists(chunk_file_path):
                        #         sleep(.1)
                        #         os.remove(chunk_file_path)


                        #     chunk_no+=1

                    # Calculate checksum of merged file
                    # with open(merged_temp, "rb") as f:
                    #     for block in iter(lambda: f.read(1024 * 1024), b""):
                    #         hash_function.update(block)
                    # Move merged file to final output
                    # ["cmd", "/c", f'move /Y "{merged_temp}" "{output_file_path}"'],
                    try:
                        # subprocess.run(
                        #     ["cmd", "/c", "move", "/Y", merged_temp, output_file_path],
                        #     shell=False,
                        #     check=True
                        # )

                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE

                        cmd = f'move /Y "{merged_temp}" "{output_file_path}"'
                        subprocess.run(
                            cmd,  # Command as string
                            shell=True,  
                            check=True,  # Must be boolean True, not string
                            startupinfo=startupinfo,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW  # Additional flag to prevent window
                        )
                        s_fileName_store.append(output_file_pathgd)
                    except Exception as move_error2:
                        print(str(move_error2))
                
                size_data = 0
                if s_fileName_store:
                    for sizeFile in s_fileName_store:
                        if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"],sizeFile)):
                            size_data = size_data + os.path.getsize(os.path.join(app.config["UPLOAD_FOLDER"],sizeFile))

                # output_file.flush()
                # os.fsync(output_file.fileno())
                l_file_data=None
                input_file=None
                # with open(output_file_path, "rb") as input_file:
                #     file_data =mmap.mmap(input_file.fileno(), 0, access=mmap.ACCESS_COPY)
                #     file_data.seek(0)
                #     file_data=file_data.read()
                if not bNoBackup:
                    input_file= open(output_file_path, "rb") 
                    l_file_data =mmap.mmap(input_file.fileno(), 0, access=mmap.ACCESS_READ)
                if (
                    str(rep).upper().replace(" ", "") == "AZURE"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from azd.AzureClient import AzureBlobClient
                        
                        client = AzureBlobClient("apnabackup")
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        if not bNoBackup:
                            folder_path="ApnaBackup"
                            # s3_key = f"{folder_path}/{output_file_pathgd.replace(os.sep,'/')}" if folder_path else output_file_pathgd
                            # #fid=client.upload_file(file_path=output_file_path,s3_key=s3_key)
                            # fid=client.upload_data(file_name=output_file_pathgd,data=l_file_data)#,content_type="apnabackup/data")                           
                            # fid =fid.get("file_id",None)
                            for index,backup_path_azure in enumerate(s_fileName_store):
                                print(f"sfilenamestore data ======================")
                                print(f"index data=================== {index} and ==== {s_fileName_store[-1]}")
                                print(f"sfilenamestore data ======================")
                                s3_key = f"{backup_path_azure.replace(os.sep,'/')}" if folder_path else backup_path_azure
                                fid=client.upload_file(file_path= os.path.join(app.config["UPLOAD_FOLDER"],backup_path_azure),file_name=s3_key)
                                subprocess.run(
                                        ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],backup_path_azure)],
                                        shell=False,
                                        check=True
                                    )
                                sktio.emit(
                                    "backup_data",
                                    {
                                        "backup_jobs": [
                                            {
                                                "cloud":"AZURE",
                                                "name": pNameText,
                                                "scheduled_time": datetime.datetime.fromtimestamp(
                                                    float(j_sta)
                                                ).strftime(
                                                    "%H:%M:%S"
                                                ),
                                                "agent": epn,
                                                "progress_number_upload": float(
                                                    100 * (float(index+1))
                                                )
                                                / float(len(s_fileName_store)),
                                                "id": j_sta,
                                                "filename":file_name,
                                                "repo": rep
                                            }
                                        ]
                                    },
                                )
                                sleep(.2)
                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 "progress_number": float(
                            #                     100 * (float(currentfile))
                            #                 )
                            #                 / float(totalfiles),
                            #                 "id": j_sta,
                            #                 "repo": rep
                            #             }
                            #         ]
                            #     },
                            # )
                            pass
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 "progress_number": float(
                            #                     100 * (float(thiscurrentfile) - 1)
                            #                 )
                            #                 / float(totalfiles),
                            #                 "id": j_sta,
                            #                 "repo": rep
                            #             }
                            #         ]
                            #     },
                            # )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        try:
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass
                        if not len(s_fileName_store)==0:
                            for f_filename in s_fileName_store:
                                try:
                                    subprocess.run(
                                        ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],f_filename)],
                                        shell=False,
                                        check=True
                                    )
                                except:
                                    pass
                if (
                    str(rep).upper().replace(" ", "") == "ONEDRIVE"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from onedrive.OneDriveClient import OneDriveClient , ConnectionError
                        
                        client = OneDriveClient()
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        if not bNoBackup:
                            folder_path="ApnaBackup"
                            client.create_folder(folder_name=folder_path)
                            # s3_key = f"{folder_path}/{output_file_path.replace(app.config['UPLOAD_FOLDER'],'').replace(os.sep,'/')}" if folder_path else output_file_path
                            # #fid=client.upload_file(file_path=output_file_path,s3_key=s3_key)
                            # fid =client.upload_file(local_path=output_file_path, remote_path= s3_key)
                            # #fid=client.upload_data(file_name=output_file_path,data=l_file_data)#,content_type="apnabackup/data")                           
                            # fid =fid.get("id",None)
                            for index,backup_path_onedrive in enumerate(s_fileName_store):
                                print(f"sfilenamestore data ======================")
                                print(f"index data=================== {index} and ==== {s_fileName_store[-1]}")
                                print(f"sfilenamestore data ======================")
                                s3_key = f"{folder_path}/{backup_path_onedrive.replace(os.sep,'/')}" if folder_path else backup_path_onedrive
                                if not bOneDrive_backup:
                                    fid=client.upload_file(local_path= os.path.join(app.config["UPLOAD_FOLDER"],backup_path_onedrive),remote_path=s3_key)
                                else: 
                                    if len(s_fileName_store) -1== index:
                                        fid=client.upload_file(local_path= os.path.join(app.config["UPLOAD_FOLDER"],backup_path_onedrive),remote_path=s3_key)
                                        
                                subprocess.run(
                                        ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],backup_path_onedrive)],
                                        shell=False,
                                        check=True
                                    )
                                sktio.emit(
                                    "backup_data",
                                    {
                                        "backup_jobs": [
                                            {
                                                "cloud":"ONEDRIVE",
                                                "name": pNameText,
                                                "scheduled_time": datetime.datetime.fromtimestamp(
                                                    float(j_sta)
                                                ).strftime(
                                                    "%H:%M:%S"
                                                ),
                                                "agent": epn,
                                                "progress_number_upload": float(
                                                    100 * (float(index+1))
                                                )
                                                / float(len(s_fileName_store)),
                                                "id": j_sta,
                                                "filename":file_name,
                                                "repo": rep
                                            }
                                        ]
                                    },
                                )
                                sleep(.2)
                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 "progress_number": app.config.get(tfi,float(
                            #                     100 * (float(currentfile))
                            #                 )
                            #                 / float(totalfiles)),
                            #                 "id": j_sta,
                            #                 "repo": rep
                            #             }
                            #         ]
                            #     },
                            # )
                            pass
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 "progress_number":app.config.get(tfi, float(
                            #                     100 * (float(thiscurrentfile) - 1)
                            #                 )
                            #                 / float(totalfiles)),
                            #                 "id": j_sta,
                            #                 "repo": rep
                            #             }
                            #         ]
                            #     },
                            # )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        
                        try:
                            fid = base64.b64encode(json.dumps(fid).encode()).decode()
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass
                        if not len(s_fileName_store)==0:
                            for f_filename in s_fileName_store:
                                try:
                                    subprocess.run(
                                        ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],f_filename)],
                                        shell=False,
                                        check=True
                                    )
                                except:
                                    pass


                if (
                    str(rep).upper().replace(" ", "") == "AWSS3"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from awd.AWSClient import S3Client
                        

                        client = S3Client()
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        if not bNoBackup:
                            folder_path="ApnaBackup"

                            # donot delete this comment s3_key = f"{folder_path}/{output_file_pathgd.replace(os.sep,'/')}" if folder_path else output_file_pathgd
                            # donot delete this comment fid=client.upload_data(output_file_pathgd,l_file_data, s3_key)

                            for index,backup_path_aws in enumerate(s_fileName_store):
                                print(f"sfilenamestore data ======================")
                                print(f"index data=================== {index} and ==== {s_fileName_store[-1]}")
                                print(f"sfilenamestore data ======================")
                                s3_key = f"{folder_path}/{backup_path_aws.replace(os.sep,'/')}" if folder_path else backup_path_aws
                                fid=client.upload_file(file_path= os.path.join(app.config["UPLOAD_FOLDER"],backup_path_aws),s3_key=s3_key)
                                subprocess.run(
                                    ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],backup_path_aws)],
                                    shell=False,
                                    check=True
                                )
                                sktio.emit(
                                    "backup_data",
                                    {
                                        "backup_jobs": [
                                            {
                                                "cloud":"AWS",
                                                "name": pNameText,
                                                "scheduled_time": datetime.datetime.fromtimestamp(
                                                    float(j_sta)
                                                ).strftime(
                                                    "%H:%M:%S"
                                                ),
                                                "agent": epn,
                                                "progress_number_upload": float(
                                                    100 * (float(index+1))
                                                )
                                                / float(len(s_fileName_store)),
                                                "id": j_sta,
                                                "filename":file_name,
                                                "repo": rep
                                            }
                                        ]
                                    },
                                )
                                sleep(.2)
                                
                                #fid=client.upload_data(file_name,l_file_data, s3_key)

                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 #"cloud":"AWS",
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 # "progress_number": float(
                            #                 #     100 * (float(currentfile))
                            #                 # )
                            #                 # / float(totalfiles),
                            #                 "progress_number": float(str(app.config[tfi])),
                            #                 "id": j_sta,
                            #                 "repo": rep
                            #             }
                            #         ]
                            #     },
                            # )
                            pass
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 # "progress_number": float(
                            #                 #     100 * (float(thiscurrentfile) - 1)
                            #                 # )
                            #                 # / float(totalfiles),
                            #                 "progress_number": float(str(app.config[tfi])),
                            #                 "id": j_sta,
                            #                 "repo": rep
                            #             }
                            #         ]
                            #     },
                            # )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        
                        try:
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass
                        if not len(s_fileName_store)==0:
                            for f_filename in s_fileName_store:
                                try:
                                    subprocess.run(
                                            ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],f_filename)],
                                            shell=False,
                                            check=True
                                        )
                                except:
                                    pass

                if (
                    str(rep).upper().replace(" ", "") == "GDRIVE"
                    or str(rep).upper().replace(" ", "") == "GOOGLE DRIVE"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from gd.GDClient import GDClient

                        client = GDClient()
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        today_date = get_date('pc')
                        if not bNoBackup:
                            # fid = client.upload_file(
                            #     output_file_path, "text/abgd", j_sta
                            # )
                            for index,backup_path_gdrive in enumerate(s_fileName_store):
                                print(f"sfilenamestore data ======================")
                                print(f"index data=================== {index} and ==== {s_fileName_store[-1]}")
                                print(f"sfilenamestore data ======================")
                                # s3_key = f"{folder_path}/{backup_path_aws.replace(os.sep,'/')}" if folder_path else backup_path_aws
                                # fid=client.upload_file(file_path= os.path.join(app.config["UPLOAD_FOLDER"],backup_path_aws),s3_key=s3_key)
                                if not bGD_backup:
                                    print("continue with upload files other than the last")
                                    fid = client.upload_file(
                                        os.path.join(app.config["UPLOAD_FOLDER"],backup_path_gdrive), "text/abgd", j_sta,today_date['date']
                                    )
                                else:
                                    print("donot upload files other than the last")
                                    if len(s_fileName_store) -1== index:
                                        fid = client.upload_file(
                                            os.path.join(app.config["UPLOAD_FOLDER"],backup_path_gdrive), "text/abgd", j_sta,today_date['date']
                                        )

                                subprocess.run(
                                    ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],backup_path_gdrive)],
                                    shell=False,
                                    check=True
                                )
                                if index < len(s_fileName_store)-1:
                                    fid_list.append(fid)
                                sktio.emit(
                                    "backup_data",
                                    {
                                        "backup_jobs": [
                                            {
                                                "cloud":"GDRIVE",
                                                "name": pNameText,
                                                "scheduled_time": datetime.datetime.fromtimestamp(
                                                    float(j_sta)
                                                ).strftime(
                                                    "%H:%M:%S"
                                                ),
                                                "agent": epn,
                                                "progress_number_upload": float(
                                                    100 * (float(index+1))
                                                )
                                                / float(len(s_fileName_store)),
                                                "id": j_sta,
                                                "filename":file_name,
                                                "repo": rep
                                            }
                                        ]
                                    },
                                )
                                sleep(.2)
                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 "progress_number":app.config.get(tfi, float(
                            #                     100 * (float(currentfile))
                            #                 )
                            #                 / float(totalfiles)),
                            #                 "id": j_sta,
                            #                 "repo": rep
                            #             }
                            #         ]
                            #     },
                            # )
                            pass
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            # sktio.emit(
                            #     "backup_data",
                            #     {
                            #         "backup_jobs": [
                            #             {
                            #                 "name": pNameText,
                            #                 "scheduled_time": datetime.datetime.fromtimestamp(
                            #                     float(j_sta)
                            #                 ).strftime(
                            #                     "%H:%M:%S"
                            #                 ),
                            #                 "agent": epn,
                            #                 "progress_number": app.config.get(tfi,float(
                            #                     100 * (float(thiscurrentfile) - 1)
                            #                 )
                            #                 / float(totalfiles)),
                            #                 "id": j_sta,
                            #             }
                            #         ]
                            #     },
                            # )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        
                        try:
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass
                        if not len(s_fileName_store)==0:
                            for f_filename in s_fileName_store:
                                try:
                                    subprocess.run(
                                        ["cmd.exe", "/c", "del","/F","/Q",  os.path.join(app.config["UPLOAD_FOLDER"],f_filename)],
                                        shell=False,
                                        check=True
                                    )
                                except:
                                    pass

                if (
                    str(rep).upper().replace(" ", "") == "UNC"
                ):
                        print("Waiting for unc")
                
                thiscurrentfile = currentfile if bdone else float(currentfile) - 1
                print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
                try:
                    save_savelogdata(
                        file_name,
                        total_chunks,
                        tcc,
                        abort,
                        epc,
                        epn,
                        tf,
                        pna,
                        rep,
                        ahi,
                        j_sta,
                        mimet,
                        pNameText,
                        pIdText,
                        bkupType,
                        thiscurrentfile,
                        totalfiles,
                        hash_function,
                        output_file_path,
                        mode_t="saving",
                        givn=givn,
                        gidn=fid,
                        backup_logs_id=backup_logs_id,
                        bdone=bdone,
                        tccsrc=tccsrc,
                        fidi=fidi,xsum_done=xsum_chunks,isMetaFile=isMetaFile, size_data=size_data, file_id=file_id
                    )
                except Exception as save_err:
                    print("########################################################save_log_err")
                # with client_backups_data_lock:
                data = load_backup_data(CLIENT_BACKUPS_DATA_FILE)
                new_item = {
                    "version":app.config["Version"],
                    "ip_address": epc,
                    "agent_name": epn,
                    "path": tcc,
                    "file_name": file_name,
                    "file_name_x_old": output_file_path,
                    "file_name_x": output_file_pathgd,
                    "file_time": time(),
                    "file_code": hash_function.hexdigest(),  # calculate_file_digest(output_file_path),
                    "size": size_data,
                    "tf": tf,
                    "pna": pna,
                    "rep": rep,
                    "ahi": ahi,
                    "j_sta": j_sta,
                    "pNameText": pNameText,
                    "pIdText": pIdText,
                    "bkupType": bkupType,
                    "givn": givn,
                    "gidn": fid,  # drive
                    "gidn_list": fid_list,  # drive

                    "fidi": fidi,  # drive
                    "metafile": isMetaFile,
                    "isMetaFile": isMetaFile
                }
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                from module2 import BackupLogs, BackupMain
                from datetime import date

                var = BackupLogs()

                # engine = create_engine(f"sqlite:///{epc}.db")
                # Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
                # xession = Session()
                from sqlite_managerA import SQLiteManager
                xession = SQLiteManager()
                dbname = os.path.join(app.config["location"], epc)
                from sqlalchemy import func
                thiscurrentfile = currentfile if bdone else float(currentfile) - 1
                try:
                    size_data = 0
                    sum_all=0
                    sum_done=0
                    done_all=0
                    try:
                        if bNoBackup:
                            # q = xession.query(BackupLogs).filter(
                            #         BackupLogs.sum_all == BackupLogs.sum_done,
                            #         BackupLogs.pIdText == pIdText,
                            #         BackupLogs.full_file_name==os.path.join(tcc, file_name),
                            #         BackupLogs.size>0,
                            #         #BackupLogs.fidi==fidi,
                            #     ) 
                            q_logs = (
                                    "SELECT log, fidi, date_time,size,sum_all,sum_done,done_all FROM backups "
                                    "WHERE done_all=100 " #(100*sum_all/ sum_done)=100 "
                                    "AND pIdText = '" + str(pIdText) + "' "
                                    "AND full_file_name = '" + str(os.path.join(tcc, file_name)) + "' "
                                    "AND size > 0 "
                                    "ORDER BY date_time ASC"
                                )
                            qrs = [(dbname, [q_logs])]
                            results = xession.execute_queries(qrs)


                            if bkupType == "incremental":
                                try:
                                    rows = results[dbname][0][1]
                                    if rows:
                                        last = rows[-1]
                                        r = json.loads(last[0])  # log JSON
                                        fidi = last[1]           # fidi column
                                        size_data = last[3]
                                        sum_all = last[4]
                                        sum_done = last[5]
                                        done_all = last[6]
                                        new_item["file_name_x"] = r["file_name_x"]
                                        new_item["file_name_x_old"] = r["file_name_x_old"]
                                        new_item["file_time"] = r["file_time"]
                                        new_item["file_code"] = r["file_code"]
                                        new_item["size"] = r["size"]
                                        new_item["fidi"] = r["fidi"]
                                        try:
                                            new_item["metafile"] = r["metafile"]
                                        except:
                                            pass
                                        try:
                                            new_item["isMetaFile"] = r["isMetaFile"]
                                        except:
                                            pass
                                        try:
                                            new_item["j_sta"] = r["j_sta"]
                                        except:
                                            pass
                                        try:
                                            new_item["gidn_list"] = r["gidn_list"]
                                        except:
                                            pass
                                        fidi = r["fidi"]

                                        # cloud repo extra fields
                                        if rep.upper().replace(" ", "") in ["GDRIVE", "GOOGLEDRIVE", "AWSS3", "AZURE"]:
                                            for k in [
                                                "ip_address","agent_name","path","file_name","tf","pna",
                                                "rep","ahi","pNameText","pIdText","bkupType","givn","gidn","size","gidn_list"
                                            ]:
                                                new_item[k] = r[k]

                                except:
                                    print("patching not done incremental file")

                             
                            if bkupType == "differential":
                                try:
                                    rows = results[dbname][0][1]
                                    if rows:
                                        first = rows[0]
                                        r = json.loads(first[0])
                                        fidi = first[1]
                                        size_data = first[3]
                                        sum_all = first[4]
                                        sum_done = first[5]
                                        done_all = first[6]
                                        new_item["file_name_x"] = r["file_name_x"]
                                        new_item["file_name_x_old"] = r["file_name_x_old"]
                                        new_item["file_time"] = r["file_time"]
                                        new_item["file_code"] = r["file_code"]
                                        new_item["size"] = r["size"]
                                        new_item["fidi"] = r["fidi"]
                                        try:
                                            new_item["metafile"] = r["metafile"]
                                        except:
                                            pass
                                        try:
                                            new_item["isMetaFile"] = r["isMetaFile"]
                                        except:
                                            pass
                                        try:
                                            new_item["j_sta"] = r["j_sta"]
                                        except:
                                            pass
                                        try:
                                            new_item["gidn_list"] = r["gidn_list"]
                                        except:
                                            pass

                                        if rep.upper().replace(" ", "") in ["GDRIVE", "GOOGLEDRIVE", "AWSS3", "AZURE"]:
                                            for k in [
                                                "ip_address","agent_name","path","file_name","tf","pna",
                                                "rep","ahi","pNameText","pIdText","bkupType","givn","gidn","size","gidn_list"
                                            ]:
                                                new_item[k] = r[k]

                                except:
                                    print("patching not done differential file")

     
                        sql_main = (
                            "INSERT INTO backups_M ("
                            "id, date_time, from_computer, from_path, file_name, "
                            "data_repo, mime_type, size, pNameText, pIdText, "
                            "bkupType, sum_all, sum_done, done_all, status, "
                            "mode, data_repod"
                            ") VALUES ("
                            f"{float(j_sta)}, {time()}, '{epn}', '{tccsrc}', '{file_name if (mimet=='file') else ''}', "
                            f"'{rep}', '{mimet}', {stat.get('size', 1) if bNoBackup else stat.get('size', 1)}, "
                            f"'{pNameText}', '{pIdText}', '{bkupType}', {totalfiles}, {thiscurrentfile}, "
                            "'xdone_all', 'xdone_all', 'xdone_all', 'xdone_all'"
                            ") ON CONFLICT(id) DO UPDATE SET "
                            "date_time=excluded.date_time, "
                            "from_computer=excluded.from_computer, "
                            "from_path=excluded.from_path, "
                            "file_name=excluded.file_name, "
                            "data_repo=excluded.data_repo, "
                            "mime_type=excluded.mime_type, "
                            "size=excluded.size, "
                            "pNameText=excluded.pNameText, "
                            "pIdText=excluded.pIdText, "
                            "bkupType=excluded.bkupType, "
                            "sum_all=excluded.sum_all, "
                            "sum_done=excluded.sum_done, "
                            "done_all=excluded.done_all, "
                            "status=excluded.status, "
                            "mode=excluded.mode, "
                            "data_repod=excluded.data_repod"
                        )
                        xession.execute_queries([(dbname, [sql_main])])

                    except Exception as ssees:
                        print(str("#### ssees ####################"))
                        print(str(ssees))
                        logger.error(f"Unhandled error in save_savelogdata ({pNameText}): {str(ssees)}")
                        print(str("#### ssees ####################"))
                        # xession.rollback()
                        # from sqlalchemy import update

                        # try:
                        #     xession.execute(
                        #         update(BackupMain)
                        #         .where(BackupMain.id == float(j_sta))
                        #         .values(
                        #             size=BackupMain.size
                        #             + os.path.getsize(output_file_path)
                        #         )
                        #     )
                        # except Exception as dw:
                        #     print("ERRRR updating: " + str(dw))

                    try:
                        if bNoBackup:
                            xsum_all = sum_all
                            xsum_done = sum_done
                            xdone_all = done_all
                        else:
                            xsum_all = total_chunks
                            # xsum_done, xdone_all = get_save_stats(
                            #     file_name, total_chunks, tcc, abort, epc,tccsrc=tccsrc,tfi=tfi
                            # )
                            xsum_done=xsum_chunks
                            xdone_all = (xsum_done*100)/total_chunks
                            if file_id:
                                backup_logs_id=file_id

                        sql_logs = (
    "INSERT OR REPLACE INTO backups ("
    "id, name, date_time, from_computer, from_path, data_repo, "
    "mime_type, file_name, full_file_name, size, log, pNameText, "
    "pIdText, bkupType, sum_all, sum_done, done_all, status, "
    "mode, data_repod, repid, fidi"
    ") VALUES ("
    f"{backup_logs_id}, {float(j_sta)}, {int(time())}, '{epn}', '{tcc}', '{rep}', "
    f"'{mimet}', '{file_name}', '{os.path.join(tcc, file_name)}', "
    f"{stat.get('size', 1)}, "
    f"'{json.dumps(new_item)}', "
    f"'{pNameText}', '{pIdText}', '{bkupType}', "
    f"{xsum_all}, {xsum_done}, '{xdone_all}', 'xdone_all', "
    "'xdone_all', 'xdone_all', '', '{fidi}'"
    ")"
)                       
                        iretry=3
                        while iretry>0:
                            iretry-=1
                            r = xession.execute_queries([(dbname, [sql_logs])])
                            if not "success" in str(r).lower():
                                sleep(2.0)
                                bdone=False
                            else:
                                iretry=0
                                sql_logs=None   
                                bdone=True

                    except Exception as ssees:
                        print(str("########################"))
                        print(str(ssees))
                        print(str("########################"))
                        # xession.rollback()

                except Exception as ser:
                    logger.error(f"Error: {str(ser)}")
                    print(str(ser))
                    bdone = False
                # xession.close()

                # data.append(new_item)
                # save_backup_data(data)

        except Exception as desd:
            logger.warning(f"error comes in save_final data error: {str(desd)}")
            bdone = False
            thiscurrentfile = currentfile if bdone else float(currentfile) - 1
            sktio.emit(
                "backup_data",
                {
                    "backup_jobs": [
                        {
                            "name": pNameText,
                            "scheduled_time": datetime.datetime.fromtimestamp(
                                float(j_sta)
                            ).strftime("%H:%M:%S"),
                            "agent": epn,
                            "progress_number": float(app.config.get(tfi,float(100 * (float(thiscurrentfile)))
                            / float(totalfiles))),
                            "id": float(j_sta),
                            "repo": rep
                        }
                    ]
                },
            )
            print(str(desd))
            for chunk_file in chunk_files:
                try:
                    if os.path.exists(os.remove(os.path.join(temp_dir, chunk_file))):
                        os.remove(os.path.join(temp_dir, chunk_file))
                except Exception as fdel:
                    logger.error(f"Error: {str(fdel)}")
                    print(str(fdel))
                    asyncio.sleep(10)
                    try:
                        if os.path.exists(
                            os.remove(os.path.join(temp_dir, chunk_file))
                        ):
                            os.remove(os.path.join(temp_dir, chunk_file))
                    except Exception as fdel:
                        logger.error(f"Error: {str(fdel)}")
                        print(str(fdel))
            return (False, sql_logs)
        finally:
            try:
                input_file.close()
            except:
                pass
            try:
                l_file_data.close()
            except:
                pass
        if bNoBackup:
            try:
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)
            except Exception as dw:
                logger.error(f"Error: {str(dw)}")
                print(str(dw))
    else:
        bdone = False
        try:
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
        except Exception as dw:
            logger.error(f"Error: {str(dw)}")
            print(str(dw))

    if bdone:
        try:
            manifest_path = _manifest_path(temp_dir, file_name, tfi)
            final_manifest_path = _final_manifest_path(tcc, file_name, j_sta)
            if os.path.exists(manifest_path):
                os.makedirs(os.path.dirname(final_manifest_path), exist_ok=True)
                shutil.move(manifest_path, final_manifest_path)
        except Exception as manifest_error:
            log_event(
                logger,
                logging.ERROR,
                ensure_job_id(j_sta),
                "backup",
                file_path=file_name,
                file_id=file_id,
                error_code="MANIFEST_SAVE_FAILED",
                error_message=str(manifest_error),
                extra={"event": "manifest_failed"},
            )

    # Clean up temporary chunk files
    for chunk_file in chunk_files:
        try:
            if os.path.exists(os.path.join(temp_dir, chunk_file)):
                os.remove(os.path.join(temp_dir, chunk_file))
        except:
            asyncio.sleep(10)
            try:
                if os.path.exists(os.path.join(temp_dir, chunk_file)):
                    os.remove(os.path.join(temp_dir, chunk_file))
            except:
                print("")

    print(f"File '{output_file_path}' assembled successfully")
    return bdone,sql_logs


def save_final_old(
    file_name,
    total_chunks,
    tcc,
    abort,
    epc,
    epn,
    tf,
    pna,
    rep,
    ahi,
    j_sta,
    mimet,
    pNameText,
    pIdText,
    bkupType,
    currentfile,
    totalfiles,
    givn="",
    tccsrc="",bNoBackup=False,fidi="",tfi=None,
):
    import gzip
    import os
    import tempfile
    # if not bNoBackup: 
    #     bNoBackup ="full"
    thiscurrentfile = currentfile
    fid = ""
    backup_logs_id = time()
    bdone = True
    output_file_pathgd = os.path.join(tcc, f"{file_name}_{str(j_sta)}.gz")
    output_file_path = os.path.join(
        app.config["UPLOAD_FOLDER"], tcc, f"{file_name}_{str(j_sta)}.gz"
    )
    if not abort:
        temp_dir = os.path.join(add_unc_temppath(), tcc)
        if tfi:
            temp_dir = os.path.join(add_unc_temppath(), tcc,tfi)
        chunk_files = [f for f in os.listdir(temp_dir) if f.startswith(file_name + "_")]
        chunk_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

        # output_file_path = os.path.join(tcc, f"{file_name}_{str(time())}.gz")
        l_file_data=b''
        input_file=None
        try:
            with open(
                output_file_path,
                "wb",
            ) as output_file:
                
                hash_function = hashlib.new("md5")
                if not bNoBackup:
                    processed_size = 0
                    for chunk_file in chunk_files:
                        chunk_file_path = os.path.join(temp_dir, chunk_file)
                        with open(chunk_file_path, "rb") as input_file:
                            local_file_data = input_file.read()
                            hash_function.update(local_file_data)
                            l_file_data = l_file_data+local_file_data
                    output_file.write(l_file_data)
                    output_file.flush()
                    os.fsync(output_file.fileno())    
                    l_file_data=None
                    # with open(output_file_path, "rb") as input_file:
                    #     file_data =mmap.mmap(input_file.fileno(), 0, access=mmap.ACCESS_COPY)
                    #     file_data.seek(0)
                    #     file_data=file_data.read()

                    input_file= open(output_file_path, "rb") 
                    l_file_data =mmap.mmap(input_file.fileno(), 0, access=mmap.ACCESS_READ)
                if (
                    str(rep).upper().replace(" ", "") == "AZURE"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from azd.AzureClient import AzureBlobClient
                        
                        client = AzureBlobClient("apnabackup")
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        if not bNoBackup:
                            folder_path="ApnaBackup"
                            s3_key = f"{folder_path}/{output_file_path.replace(os.sep,'/')}" if folder_path else output_file_path
                            #fid=client.upload_file(file_path=output_file_path,s3_key=s3_key)
                            fid=client.upload_data(file_name=output_file_path,data=l_file_data)#,content_type="apnabackup/data")                           
                            fid =fid.get("file_id",None)
                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(thiscurrentfile) - 1)
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        try:
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass
                if (
                    str(rep).upper().replace(" ", "") == "ONEDRIVE"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from onedrive.OneDriveClient import OneDriveClient , ConnectionError
                        
                        client = OneDriveClient()
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        if not bNoBackup:
                            folder_path="ApnaBackup"
                            client.create_folder(folder_name=folder_path)
                            s3_key = f"{folder_path}/{output_file_path.replace(app.config['UPLOAD_FOLDER'],'').replace(os.sep,'/')}" if folder_path else output_file_path
                            #fid=client.upload_file(file_path=output_file_path,s3_key=s3_key)
                            fid =client.upload_file(local_path=output_file_path, remote_path= s3_key)
                            #fid=client.upload_data(file_name=output_file_path,data=l_file_data)#,content_type="apnabackup/data")                           
                            fid =fid.get("id",None)
                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(thiscurrentfile) - 1)
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        try:
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass


                if (
                    str(rep).upper().replace(" ", "") == "AWSS3"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from awd.AWSClient import S3Client
                        

                        client = S3Client()
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        if not bNoBackup:
                            folder_path="ApnaBackup"
                            s3_key = f"{folder_path}/{output_file_path.replace(os.sep,'/')}" if folder_path else output_file_path
                            #fid=client.upload_file(file_path=output_file_path,s3_key=s3_key)
                            #fid=client.upload_data(file_path=output_file_path,file_data=l_file_data, s3_key=s3_key)
                            fid=client.upload_data(output_file_path,l_file_data, s3_key)

                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(thiscurrentfile) - 1)
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        try:
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass

                if (
                    str(rep).upper().replace(" ", "") == "GDRIVE"
                    or str(rep).upper().replace(" ", "") == "GOOGLE DRIVE"
                ):
                    # from pydispatch import dispatcher

                    try:
                        #output_file.flush()
                        #os.fsync(output_file.fileno())
                        from gd.GDClient import GDClient

                        client = GDClient()
                        # dispatcher.connect(gd_fileuploaded, signal=client.UPLOADED)
                        fid=None
                        if not bNoBackup:
                            fid = client.upload_file(
                                output_file_path, "text/abgd", j_sta
                            )
                        if bNoBackup:
                            fid=1234567890
                        if fid :
                            # sktio.emit("backup_data",{"backup_jobs":[{"name": pNameText , "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime('%Y-%m-%d %H:%M:%S') , "agent": epn , "progress_number": float(100*(float(currentfile)))/float(totalfiles)}]})
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(currentfile))
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                        elif not fid:
                            bdone = False
                            for chunk_file in chunk_files:
                                try:
                                    if os.path.exists(
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                    ):
                                        os.remove(os.path.join(temp_dir, chunk_file))
                                except Exception as fdel:
                                    print(str(fdel))
                                    asyncio.sleep(10)
                                    try:
                                        if os.path.exists(
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                        ):
                                            os.remove(
                                                os.path.join(temp_dir, chunk_file)
                                            )
                                    except Exception as fdel:
                                        print(str(fdel))
                            thiscurrentfile = (
                                currentfile if bdone else float(currentfile) - 1
                            )
                            sktio.emit(
                                "backup_data",
                                {
                                    "backup_jobs": [
                                        {
                                            "name": pNameText,
                                            "scheduled_time": datetime.datetime.fromtimestamp(
                                                float(j_sta)
                                            ).strftime(
                                                "%H:%M:%S"
                                            ),
                                            "agent": epn,
                                            "progress_number": float(
                                                100 * (float(thiscurrentfile) - 1)
                                            )
                                            / float(totalfiles),
                                            "id": j_sta,
                                            "repo": rep
                                        }
                                    ]
                                },
                            )
                            # return bdone
                    except Exception as dw:
                        print(str(dw))
                        bdone = false
                        # return bdone
                    finally:
                        try:
                            input_file.close()
                        except:
                            pass
                        try:
                            l_file_data.close()
                        except:
                            pass

                if (
                    str(rep).upper().replace(" ", "") == "UNC"
                ):
                        print("Waiting for unc")
                
                thiscurrentfile = currentfile if bdone else float(currentfile) - 1
                #print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
                save_savelogdata(
                    file_name,
                    total_chunks,
                    tcc,
                    abort,
                    epc,
                    epn,
                    tf,
                    pna,
                    rep,
                    ahi,
                    j_sta,
                    mimet,
                    pNameText,
                    pIdText,
                    bkupType,
                    thiscurrentfile,
                    totalfiles,
                    hash_function,
                    output_file_path,
                    mode_t="saving",
                    givn=givn,
                    gidn=fid,
                    backup_logs_id=backup_logs_id,
                    bdone=bdone,
                    tccsrc=tccsrc,
                    fidi=fidi,
                )
                # with client_backups_data_lock:
                data = load_backup_data(CLIENT_BACKUPS_DATA_FILE)
                new_item = {
                    "ip_address": epc,
                    "agent_name": epn,
                    "path": tcc,
                    "file_name": file_name,
                    "file_name_x": output_file_path,
                    "file_time": time(),
                    "file_code": hash_function.hexdigest(),  # calculate_file_digest(output_file_path),
                    "size": os.path.getsize(output_file_path),
                    "tf": tf,
                    "pna": pna,
                    "rep": rep,
                    "ahi": ahi,
                    "j_sta": j_sta,
                    "pNameText": pNameText,
                    "pIdText": pIdText,
                    "bkupType": bkupType,
                    "givn": givn,
                    "gidn": fid,  # drive
                    "fidi": fidi,  # drive
                }
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                from module2 import BackupLogs, BackupMain
                from datetime import date

                var = BackupLogs()
                engine = create_engine(f"sqlite:///{epc}.db")
                Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
                xession = Session()
                from sqlalchemy import func
                print(
                    f"Size of {output_file_path} => {os.path.getsize(output_file_path)}"
                )
                thiscurrentfile = currentfile if bdone else float(currentfile) - 1
                try:
                    try:
                        if bNoBackup:
                            q = xession.query(BackupLogs).filter(
                                    BackupLogs.sum_all == BackupLogs.sum_done,
                                    BackupLogs.pIdText == pIdText,
                                    BackupLogs.full_file_name==os.path.join(tcc, file_name),
                                    BackupLogs.size>0,
                                    #BackupLogs.fidi==fidi,
                                ) 
                            
                            if bkupType=="incremental" :
                                try:
                                    r_fidi=""
                                    try:
                                        r_fidi=q.order_by(BackupLogs.date_time).all()[-1].fidi
                                    except:
                                        print("")

                                    r=json.loads(q.order_by(BackupLogs.date_time).all()[-1].log)
                                    #BackupLogs.fidi==fidi,
                                    new_item["file_name_x"]=r["file_name_x"]
                                    new_item["file_time"]=r["file_time"]
                                    new_item["file_code"]=r["file_code"]
                                    new_item["size"]=r["size"]                                    
                                    new_item["fidi"]=r["fidi"]
                                    fidi=r["fidi"]
                                    if (
                                            str(rep).upper().replace(" ", "") == "GDRIVE"
                                            or str(rep).upper().replace(" ", "") == "GOOGLE DRIVE"
                                            or str(rep).upper().replace(" ", "") == "AWSS3"
                                            or str(rep).upper().replace(" ", "") == "AZURE"
                                        ):
                                        new_item["ip_address"]=r["ip_address"]#: epc,
                                        new_item["agent_name"]=r["agent_name"]#: epn,
                                        new_item["path"]=r["path"]
                                        new_item["file_name"]=r["file_name"]
                                        new_item["tf"]=r["tf"]
                                        new_item["pna"]=r["pna"]
                                        new_item["rep"]=r["rep"]
                                        new_item["ahi"]=r["ahi"]
                                        #new_item["j_sta"]=r["j_sta"]: j_sta,
                                        new_item["pNameText"]=r["pNameText"]
                                        new_item["pIdText"]=r["pIdText"]
                                        new_item["bkupType"]=r["bkupType"]
                                        new_item["givn"]=r["givn"]
                                        new_item["gidn"]=r["gidn"]

                                except:
                                    print("patching not done incremental file")
                             
                            if bkupType=="differential":
                                try:
                                    r=json.loads(q.order_by(BackupLogs.date_time).all()[0].log)
                                    new_item["file_name_x"]=r["file_name_x"]
                                    new_item["file_time"]=r["file_time"]
                                    new_item["file_code"]=r["file_code"]
                                    new_item["size"]=r["size"]

                                    new_item["fidi"]=r["fidi"]
                                    fidi=r["fidi"]
                                    if (
                                            str(rep).upper().replace(" ", "") == "GDRIVE"
                                            or str(rep).upper().replace(" ", "") == "GOOGLE DRIVE"
                                            or str(rep).upper().replace(" ", "") == "AWSS3"
                                            or str(rep).upper().replace(" ", "") == "AZURE"
                                        ):
                                        new_item["ip_address"]=r["ip_address"]#: epc,
                                        new_item["agent_name"]=r["agent_name"]#: epn,
                                        new_item["path"]=r["path"]
                                        new_item["file_name"]=r["file_name"], 
                                        new_item["tf"]=r["tf"]
                                        new_item["pna"]=r["pna"]
                                        new_item["rep"]=r["rep"]
                                        new_item["ahi"]=r["ahi"]
                                        #new_item["j_sta"]=r["j_sta"]: j_sta
                                        new_item["pNameText"]=r["pNameText"]
                                        new_item["pIdText"]=r["pIdText"]
                                        new_item["bkupType"]=r["bkupType"]
                                        new_item["givn"]=r["givn"]
                                        new_item["gidn"]=r["gidn"]
                                        new_item["fidi"]=r["fidi"]
                                        fidi=r["fidi"]
                                except:
                                    print("patching not done differential file")
     
                        record = BackupMain(
                            id=float(j_sta),
                            date_time=time(),
                            from_computer=epn,
                            from_path=tccsrc,
                            file_name=file_name if (mimet == "file") else "",
                            data_repo=rep,
                            mime_type=mimet,
                            size= 0 if bNoBackup else os.path.getsize(output_file_path) ,
                            pNameText=pNameText,
                            pIdText=pIdText,
                            bkupType=bkupType,
                            sum_all=totalfiles,
                            sum_done=thiscurrentfile,
                            done_all="xdone_all",
                            status="xdone_all",
                            mode="xdone_all",
                            data_repod="xdone_all",
                        )
                        # xession.add(record)
                        xession.merge(record)
                        xession.commit()
                    except Exception as ssees:
                        print(str("#### ssees ####################"))
                        print(str(ssees))
                        print(str("#### ssees ####################"))
                        xession.rollback()
                        from sqlalchemy import update

                        try:
                            xession.execute(
                                update(BackupMain)
                                .where(BackupMain.id == float(j_sta))
                                .values(
                                    size=BackupMain.size
                                    + os.path.getsize(output_file_path)
                                )
                            )
                        except Exception as dw:
                            print("ERRRR updating: " + str(dw))

                    try:
                        xsum_all = total_chunks
                        xsum_done, xdone_all = get_save_stats(
                            file_name, total_chunks, tcc, abort, epc,tccsrc=tccsrc,tfi=tfi
                        )
                        record2 = BackupLogs(
                            id=backup_logs_id,
                            name=float(j_sta),
                            date_time=int(time()),
                            from_computer=epn,
                            from_path=tcc,
                            data_repo=rep,
                            mime_type=mimet,
                            file_name=file_name,
                            full_file_name=os.path.join(tcc, file_name),
                            size=os.path.getsize(output_file_path),
                            log=json.dumps(new_item),
                            pNameText=pNameText,
                            pIdText=pIdText,
                            bkupType=bkupType,
                            sum_all=xsum_all,
                            sum_done=xsum_done,
                            done_all=xdone_all,
                            status="xdone_all",
                            mode="xdone_all",
                            data_repod="xdone_all",
                            repid="",
                            fidi=fidi,
                        )
                        # xession.add(record2)
                        xession.merge(record2)
                        xession.commit()
                    except Exception as ssees:
                        print(str("########################"))
                        print(str(ssees))
                        print(str("########################"))
                        xession.rollback()

                except Exception as ser:
                    print(str(ser))
                    bdone = False

                 
                try:
                    result = (
                        session.query(
                            BackupLogs.id,
                            func.sum(BackupLogs.sum_all).label("sumall"),
                            func.sum(BackupLogs.sum_done).label("sumdone")
                        )
                        .filter(BackupLogs.name == float(j_sta))
                        .group_by(BackupLogs.id)
                        .order_by(BackupLogs.id.desc())
                        .all()
                    )

                    for row in result:
                        session.query(BackupMain).filter(BackupMain.id == row.id).update(
                            {
                                BackupMain.sum_all: row.sumall,
                                BackupMain.sum_done: row.sumdone
                            },
                            synchronize_session=False
                        )

                    xession.commit()
                except:
                    pass
                xession.close()

                # data.append(new_item)
                # save_backup_data(data)

        except Exception as desd:
            logger.warning(f"error comes in save_final data error: {str(desd)}")
            bdone = False
            thiscurrentfile = currentfile if bdone else float(currentfile) - 1
            sktio.emit(
                "backup_data",
                {
                    "backup_jobs": [
                        {
                            "name": pNameText,
                            "scheduled_time": datetime.datetime.fromtimestamp(
                                float(j_sta)
                            ).strftime("%H:%M:%S"),
                            "agent": epn,
                            "progress_number": float(100 * (float(thiscurrentfile)))
                            / float(totalfiles),
                            "id": j_sta,
                            "repo": rep
                        }
                    ]
                },
            )
            print(str(desd))
            for chunk_file in chunk_files:
                try:
                    if os.path.exists(os.remove(os.path.join(temp_dir, chunk_file))):
                        os.remove(os.path.join(temp_dir, chunk_file))
                except Exception as fdel:
                    print(str(fdel))
                    asyncio.sleep(10)
                    try:
                        if os.path.exists(
                            os.remove(os.path.join(temp_dir, chunk_file))
                        ):
                            os.remove(os.path.join(temp_dir, chunk_file))
                    except Exception as fdel:
                        print(str(fdel))
            return ("500", 200)
        finally:
            try:
                input_file.close()
            except:
                pass
            try:
                l_file_data.close()
            except:
                pass
        if bNoBackup:
            try:
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)
            except Exception as dw:
                print(str(dw))
    else:
        bdone = False
        try:
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
        except Exception as dw:
            print(str(dw))

    # Clean up temporary chunk files
    for chunk_file in chunk_files:
        try:
            if os.path.exists(os.path.join(temp_dir, chunk_file)):
                os.remove(os.path.join(temp_dir, chunk_file))
        except:
            asyncio.sleep(10)
            try:
                if os.path.exists(os.path.join(temp_dir, chunk_file)):
                    os.remove(os.path.join(temp_dir, chunk_file))
            except:
                print("")

    print(f"File '{output_file_path}' assembled successfully")
    return bdone


def save_savelogdata(
    file_name,
    total_chunks,
    tcc,
    abort,
    epc,
    epn,
    tf,
    pna,
    rep,
    ahi,
    j_sta,
    mimet,
    pNameText,
    pIdText,
    bkupType,
    currentfile,
    totalfiles,
    hash_function=None,
    output_file_path="",
    mode_m="uploading",
    status_m="pending",
    mode_t="uploading",
    status_t="pending",
    givn=None,
    gidn=None,
    backup_logs_id=unique_time_float(),
    bdone=True,
    tccsrc="",fidi="",xsum_done=0,isMetaFile=False,size_data=0, file_id=None,
    chunk_index=None,
):

    import gzip
    import os
    import tempfile
    output_file_pathgd = os.path.join(tcc, f"{file_name}_{str(j_sta)}.gz")
    # with client_backups_data_lock:
    data = load_backup_data(CLIENT_BACKUPS_DATA_FILE)
    new_item = {}
    if file_id:
        backup_logs_id=file_id
    try:
        new_item = {
            "version":app.config["Version"],
            "ip_address": epc,
            "agent_name": epn,
            "path": tcc,
            "file_name": file_name,
            "file_name_x_old": output_file_path,
            "file_name_x": output_file_pathgd,
            "file_time": time(),
            "file_code": hash_function.hexdigest(),  # calculate_file_digest(output_file_path),
            "size": size_data,
            "tf": tf,
            "pna": pna,
            "rep": rep,
            "ahi": ahi,
            "j_sta": j_sta,
            "pNameText": pNameText,
            "pIdText": pIdText,
            "bkupType": bkupType,
            "givn": givn,
            "gidn": gidn,  # drive
            "metafile": isMetaFile,
            "isMetaFile": isMetaFile
        }
        logger.info(f"all data comes in savelogdata {new_item}")
    except Exception as exp:
        logger.warning(f"Error comes in savelogdata, backup name: {pNameText} and error: {str(exp)}")
        print(str(exp))

    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker
    # from module2 import BackupLogs, BackupMain
    # from datetime import date

    # var = BackupLogs()
    # engine = create_engine(f"sqlite:///{epc}.db")
    # Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    # xession = Session()
    from sqlite_managerA import SQLiteManager
    from module2 import create_database
    xession = SQLiteManager()
    dbname = os.path.join(app.config["location"], epc)
    # Ensure DB has backups_M (and related tables) so INSERT succeeds (e.g. for GDrive backup)
    try:
        create_database(dbname)
    except Exception as _:
        pass
    sql_logs = None
    sql_main = None
    size_val = size_data #os.path.getsize(output_file_path) if os.path.exists(output_file_path) else 0
    # print(f"Size of {output_file_path} => {os.path.getsize(output_file_path)}")
    try:
        try:
    #         record = BackupMain(
    #             id=float(j_sta),
    #             date_time=time(),
    #             from_computer=epn,
    #             from_path=tccsrc,
    #             file_name=file_name if (mimet == "file") else "",
    #             data_repo=rep,
    #             mime_type=mimet,
    #             size=os.path.getsize(output_file_path),
    #             pNameText=pNameText,
    #             pIdText=pIdText,
    #             bkupType=bkupType,
    #             sum_all=totalfiles,
    #             sum_done=currentfile,
    #             mode=mode_m,
    #             status=status_m,
    #             done_all=1,
    #             data_repod="",
    #         )
    #         # xession.add(record)
    #         xession.merge(record)
    #         xession.commit()
            # For GDrive/AWS/Azure/OneDrive: store cloud metadata in data_repod so restore can use it without a local manifest
            data_repod_val = ""
            rep_upper = str(rep).upper().replace(" ", "")
            _original_path = (tccsrc + os.sep + (file_name or "")).rstrip(os.sep) if file_name else tccsrc
            if gidn is not None or (rep_upper in ["GDRIVE", "GOOGLEDRIVE"] and givn is not None):
                # gidn_list must be a list of file-id objects (dict with 'id' or string id) for client restore
                _gidn_list = [gidn] if gidn is not None else []
                if isinstance(gidn, list):
                    _gidn_list = gidn
                elif isinstance(gidn, dict):
                    # single chunk: keep as list of one dict so client can do gfid['id']
                    _gidn_list = [gidn]
                elif gidn is not None:
                    _gidn_list = [gidn]
                # GDrive multi-chunk: merge this chunk's gidn into gidn_list by chunk_index (1-based) so we don't overwrite previous chunks
                if rep_upper in ["GDRIVE", "GOOGLEDRIVE"] and gidn is not None and not isinstance(gidn, list) and int(total_chunks or 0) > 1 and chunk_index is not None:
                    idx = int(chunk_index) - 1  # 1-based to 0-based
                    if 0 <= idx < int(total_chunks):
                        try:
                            q_existing = ("SELECT data_repod FROM backups_M WHERE id = " + str(float(j_sta)))
                            qrs_ex = [(dbname, [q_existing])]
                            res_ex = xession.execute_queries(qrs_ex)
                            db_res = res_ex.get(dbname, [])
                            if db_res and db_res[0][0] == "Success" and db_res[0][1]:
                                row = db_res[0][1][0]
                                existing_repod = (row[0] or "") if row else ""
                                if existing_repod:
                                    existing = json.loads(existing_repod) if isinstance(existing_repod, str) else existing_repod
                                    existing_list = existing.get("gidn_list")
                                    if isinstance(existing_list, list) and len(existing_list) <= int(total_chunks):
                                        _gidn_list = existing_list
                                        while len(_gidn_list) < int(total_chunks):
                                            _gidn_list.append(None)
                                        _gidn_list[idx] = gidn
                                    else:
                                        _gidn_list = [None] * int(total_chunks)
                                        _gidn_list[idx] = gidn
                                else:
                                    _gidn_list = [None] * int(total_chunks)
                                    _gidn_list[idx] = gidn
                            else:
                                _gidn_list = [None] * int(total_chunks)
                                _gidn_list[idx] = gidn
                        except Exception as merge_err:
                            logger.warning(f"GDrive gidn_list merge failed, using single: {merge_err}")
                            _gidn_list = [gidn]
                _data_repod_obj = {
                    "gidn": gidn,
                    "givn": givn,
                    "gidn_list": _gidn_list,
                    "path": tccsrc,
                    "file_name": file_name or "",
                    "original_path": _original_path,
                    "total_chunks": int(total_chunks),
                    "isMetaFile": isMetaFile,
                }
                data_repod_val = json.dumps(_data_repod_obj).replace("'", "''")
            elif rep_upper in ["AWSS3", "AZURE", "ONEDRIVE"]:
                # AWS/Azure/OneDrive: no local manifest; store object path/key so restore can fetch from cloud via server
                _file_name_x = (tccsrc + os.sep + (file_name or "") + "_" + str(j_sta) + ".gz").replace("\\", "/")
                if rep_upper == "ONEDRIVE":
                    _file_name_x = ("ApnaBackup" + os.sep + tccsrc + os.sep + (file_name or "") + "_" + str(j_sta) + ".gz").replace("\\", "/")
                _data_repod_obj = {
                    "path": tccsrc,
                    "file_name": file_name or "",
                    "j_sta": j_sta,
                    "file_name_x": _file_name_x,
                    "original_path": _original_path,
                    "total_chunks": int(total_chunks),
                    "givn": givn,
                    "isMetaFile": isMetaFile,
                }
                data_repod_val = json.dumps(_data_repod_obj).replace("'", "''")
            sql_main = (
                "INSERT INTO backups_M ("
                "id, date_time, from_computer, from_path, file_name, "
                "data_repo, mime_type, size, pNameText, pIdText, "
                "bkupType, sum_all, sum_done, done_all, mode, status, data_repod"
                ") VALUES ("
                f"{float(j_sta)}, {time()}, '{epn}', '{tccsrc}', "
                f"'{file_name if mimet=='file' else ''}', "
                f"'{rep}', '{mimet}', {size_val}, "
                f"'{pNameText}', '{pIdText}', '{bkupType}', "
                f"{int(totalfiles)}, {int(currentfile)}, 1, "
                f"'{mode_m}', '{status_m}', '{data_repod_val}'"
                ") ON CONFLICT(id) DO UPDATE SET "
                "date_time=excluded.date_time, "
                "from_computer=excluded.from_computer, "
                "from_path=excluded.from_path, "
                "file_name=excluded.file_name, "
                "data_repo=excluded.data_repo, "
                "mime_type=excluded.mime_type, "
                "size=excluded.size, "
                "pNameText=excluded.pNameText, "
                "pIdText=excluded.pIdText, "
                "bkupType=excluded.bkupType, "
                "sum_all=excluded.sum_all, "
                "sum_done=excluded.sum_done, "
                "done_all=excluded.done_all, "
                "mode=excluded.mode, "
                "status=excluded.status, "
                "data_repod=excluded.data_repod"
            )

            xession.execute_queries([(dbname, [sql_main])])
            logger.info(f"Save data successfully in the database backup main, Backup Name: {pNameText}")
        except Exception as ssees:
            print(str("#### ssees ####################"))
            print(str(ssees))
            logger.warning(f"problem in database in save in backup main, backup name: {pNameText} and error: {str(ssees)}")
            print(str("#### ssees ####################"))
            # xession.rollback()
            # from sqlalchemy import update

            # try:
            #     xession.execute(
            #         update(BackupMain)
            #         .where(BackupMain.id == float(j_sta))
            #         .values(size=BackupMain.size + os.path.getsize(output_file_path))
            #     )
            # except Exception as dw:
            #     print("ERRRR updating: " + str(dw))
            #     logger.warning(f"ERRRR updating: In backup main, backup name: {pNameText} and error: {str(dw)}")

        try:
            xsum_all = total_chunks
            # xsum_done, xdone_all = get_save_stats(
            #     file_name, total_chunks, tcc, abort, epc,tccsrc
            # )
            xdone_all =xsum_done*100/total_chunks

            # record2 = BackupLogs(
            #     id=backup_logs_id,
            #     name=float(j_sta),
            #     date_time=int(time()),
            #     from_computer=epn,
            #     from_path=tccsrc,
            #     data_repo=rep,
            #     mime_type="",
            #     file_name=file_name,
            #     full_file_name=os.path.join(tcc, file_name),
            #     size=os.path.getsize(output_file_path),
            #     log=json.dumps(new_item),
            #     pNameText=pNameText,
            #     pIdText=pIdText,
            #     bkupType=bkupType,
            #     sum_all=xsum_all,
            #     sum_done=xsum_done,
            #     done_all=xdone_all,
            #     mode=mode_t,
            #     status=status_t,
            # )
            # # xession.add(record2)
            # xession.merge(record2)
            # xession.commit()]
            log_escaped = json.dumps(new_item).replace("'", "''")
            sql_logs = (
                "INSERT OR REPLACE INTO backups ("
                "id, name, date_time, from_computer, from_path, data_repo, "
                "mime_type, file_name, full_file_name, size, log, pNameText, "
                "pIdText, bkupType, sum_all, sum_done, done_all, mode, status"
                ") VALUES ("
                f"{backup_logs_id}, {float(j_sta)}, {int(time())}, '{epn}', '{tccsrc}', '{rep}', "
                f"'', '{file_name}', '{os.path.join(tcc, file_name)}', "
                f"{size_val}, '{log_escaped}', "
                f"'{pNameText}', '{pIdText}', '{bkupType}', "
                f"{int(xsum_all)}, {int(xsum_done)}, '{xdone_all}', '{mode_t}', '{status_t}'"
                ")"
            )
            iretry=3
            while iretry>0:
                iretry-=1
                r = xession.execute_queries([(dbname, [sql_logs])])
                if not "success" in str(r).lower():
                    sleep(2.0)
                else:
                    iretry=0
                    sql_logs=None 
            print(r)
            logger.info(f"Save data successfully in the database backup logs, Backup Name: {pNameText}")
        except Exception as ssees:
            print(str("########################"))
            print(str(ssees))
            logger.warning(f"problem in database in save in backup logs, backup name: {pNameText} and error: {str(ssees)}")
            print(str("########################"))
            # xession.rollback()

    except Exception as ser:
        print(str(ser))
        logger.error(f"Unhandled error in save_savelogdata ({pNameText}): {ser}")
    try:
        # result = (
        #     xession.query(
        #         BackupLogs.id,
        #         func.sum(BackupLogs.sum_all).label("sumall"),
        #         func.sum(BackupLogs.sum_done).label("sumdone")
        #     )
        #     .filter(BackupLogs.name == float(j_sta))
        #     .group_by(BackupLogs.id)
        #     .order_by(BackupLogs.id.desc())
        #     .all()
        # )

        # for row in result:
        #     xession.query(BackupMain).filter(BackupMain.id == row.id).update(
        #         {
        #             BackupMain.sum_all: row.sumall,
        #             BackupMain.sum_done: row.sumdone
        #         },
        #         synchronize_session=False
        #     )

        # xession.commit()
        # Include UNC in backup progress aggregation - UNC backups now properly tracked
        sql_sum = (
            "SELECT id, SUM(sum_all), SUM(sum_done) "
            f"FROM backups WHERE name = {float(j_sta)} "
            "GROUP BY id ORDER BY id DESC"
        )

        res = xession.execute_queries([(dbname, [sql_sum])])
        if dbname in res:
            rows = res[dbname][0][1]  # list of (id, sum_all, sum_done)

            updates = []
            for rid, sumall, sumdone in rows:
                # updates.append(
                #     f"UPDATE backups_M SET sum_all={int(sumall)}, sum_done={int(sumdone)} "
                #     f"WHERE id={float(rid)}"
                # )
                updates.append(
                    f"UPDATE backups_M SET sum_done={int(sumdone)} "
                    f"WHERE id={float(rid)}"
                )

            if updates:
                xession.execute_queries([(dbname, updates)])
    except Exception as ser:
        logger.error(f"Unhandled error in save_savelogdata ({pNameText}): {ser}")
    # xession.close()

from module2 import create_database
@app.route('/saveinitlog', methods=['POST'])
def save_saveinit_log():
    data = request.json
    from time import strftime, localtime,time
    file_list = data['data']
    meta_data = data['meta_data']

    epc = meta_data.get("epc")
    epc = base64.b64decode(epc)
    epc = gzip.decompress(epc)
    epc = epc.decode("UTF-8")

    epn = meta_data.get("epn")
    epn = base64.b64decode(epn)
    epn = gzip.decompress(epn)
    epn = epn.decode("UTF-8")

    mimet = meta_data.get("ftype")
    rep = meta_data.get("repo")
    pNameText = meta_data.get("p_NameText")
    pIdText = meta_data.get("p_IdText")
    bkupType = meta_data.get("bkupType")
    totalfiles = meta_data.get("totalfiles")
    j_sta = meta_data.get("id")

    from sqlite_managerA import SQLiteManager
    xession = SQLiteManager()
    dbname = os.path.join(app.config["location"], epc)
    create_database(dbname)

    values_list = []

    for file in file_list:
        backup_logs_id = file['id']
        tccsrc = os.path.join(
            epc,
            str(meta_data.get("src_location", "")).replace(":", "{{DRIVE}}")
        )
        
        size_val = file['size']
        file_name = os.path.basename(file['path'])
        tcc = os.path.dirname(file['path'])


        
    
        try:
            # sql_logs = (
            #         "INSERT INTO backups ("
            #         "id, name, date_time, from_computer, from_path, data_repo, "
            #         "mime_type, file_name, full_file_name, size, log, pNameText, "
            #         "pIdText, bkupType, sum_all, sum_done, done_all, mode, status"
            #         ") VALUES ("
            #         f"{backup_logs_id}, {float(j_sta)}, {int(time())}, '{epn}', '{tccsrc}', '{rep}', "
            #         f"'', '{file_name}', '{os.path.join(tcc, file_name)}', "
            #         f"{size_val}, '', "
            #         f"'{pNameText}', '{pIdText}', '{bkupType}', "
            #         f"{int(0)}, {int(0)}, '', '', ''"
            #         ")"
            #     )

            row = (
                    f"({backup_logs_id}, {float(j_sta)}, {int(time())}, "
                    f"'{epn}', '{tccsrc}', '{rep}', "
                    f"'', '{file_name}', '{os.path.join(tcc, file_name)}', "
                    f"{size_val}, '', "
                    f"'{pNameText}', '{pIdText}', '{bkupType}', "
                    f"0, 0, '', '', '')"
                )

            values_list.append(row)

        except Exception as ser:
            logger.warning(f"Unhandled error in save_loginit ({pNameText}): {ser}")
    
    try:
        sql_main = (
            "INSERT INTO backups_M ("
            "id, date_time, from_computer, from_path, file_name, "
            "data_repo, mime_type, size, pNameText, pIdText, "
            "bkupType, sum_all, sum_done, done_all, mode, status, data_repod"
            ") VALUES ("
            f"{float(j_sta)}, {time()}, '{epn}', '{tccsrc}', "
            f"'{file_name if mimet=='file' else ''}', "
            f"'{rep}', '{mimet}', {size_val}, "
            f"'{pNameText}', '{pIdText}', '{bkupType}', "
            f"{int(totalfiles)}, {int(0)}, 0, "
            f"'', '', ''"
            ") ON CONFLICT(id) DO UPDATE SET "
            "date_time=excluded.date_time, "
            "from_computer=excluded.from_computer, "
            "from_path=excluded.from_path, "
            "file_name=excluded.file_name, "
            "data_repo=excluded.data_repo, "
            "mime_type=excluded.mime_type, "
            "size=excluded.size, "
            "pNameText=excluded.pNameText, "
            "pIdText=excluded.pIdText, "
            "bkupType=excluded.bkupType, "
            "sum_all=excluded.sum_all, "
            "sum_done=excluded.sum_done, "
            "done_all=excluded.done_all, "
            "mode=excluded.mode, "
            "status=excluded.status, "
            "data_repod=excluded.data_repod"
        )

        # xession.execute_queries([(dbname, [sql_main])])
    except Exception as ser:
        logger.warning(f"Unhandled error in save_initlog ({pNameText}): {ser}")

    sql_logs = (
    "INSERT INTO backups ("
    "id, name, date_time, from_computer, from_path, data_repo, "
    "mime_type, file_name, full_file_name, size, log, pNameText, "
    "pIdText, bkupType, sum_all, sum_done, done_all, mode, status"
    ") VALUES "
    + ", ".join(values_list)
    )

    try:
        r = xession.execute_queries([(dbname, [sql_main,sql_logs])])
        print(r)
    except:
        pass
    # try:
    #     sktio.emit(
    #         "backup_data",
    #         {
    #         "backup_jobs": [
    #             {
    #                 "status": "counting",
    #                 "paused": False,
    #                 "name": pNameText,
    #                 "agent": str(epn),
    #                 "scheduled_time": strftime(
    #                     "%H:%M:%S",
    #                     localtime(float(j_sta))
    #                 ),
    #                 "progress_number": totalfiles,
    #                 "id": float(j_sta),
    #                 "repo": rep
    #             }
    #         ]}
    #         )
    # except:
    #     pass
    return 'success',200

def update_filebackup_counts(
    jobid,
    epc
):

   

    from sqlalchemy import select, update,text
    from sqlalchemy import create_engine, Column, Integer, Float, func
    from sqlalchemy.orm import sessionmaker, declarative_base
    from module2 import BackupLogs, BackupMain
    from datetime import date
    var = BackupLogs()
    engine = create_engine(f"sqlite:///{epc}.db")
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    xession = Session()

    # try:
    #     result = (
    #         session.query(
    #             BackupLogs.id,
    #             func.sum(BackupLogs.sum_all).label("sumall"),
    #             func.sum(BackupLogs.sum_done).label("sumdone")
    #         )
    #         .filter(BackupLogs.name == float(jobid))
    #         .group_by(BackupLogs.id)
    #         .order_by(BackupLogs.id.desc())
    #         .all()
    #     )

    #     for row in result:
    #         session.query(BackupMain).filter(BackupMain.id == row.id).update(
    #             {
    #                 BackupMain.sum_all: row.sumall,
    #                 BackupMain.sum_done: row.sumdone
    #             },
    #             synchronize_session=False
    #         )

    #     xession.commit()
    # except :
    #     pass
    try:
        # subquery = (
        #     select(
        #         BackupLogs.id.label("log_id"),
        #         func.sum(BackupLogs.sum_all).label("sumall"),
        #         func.sum(BackupLogs.sum_done).label("sumdone"),
        #     )
        #     .group_by(BackupLogs.id)
        #     .subquery()
        # )

        # # --- Step 2: Perform bulk update using join ---
        # stmt = (
        #     update(BackupMain)
        #     .where(BackupMain.id == subquery.c.log_id)
        #     .values(
        #         sumall=subquery.c.sumall,
        #         sumdone=subquery.c.sumdone,
        #     )
        # )
        # xession.execute(stmt)

        # UNC backups are now included in progress aggregation
        # Previous exclusion removed to ensure UNC backup status updates correctly
        sql = text("""
        UPDATE backups_M
        SET sum_done = sq.sumdone
        FROM (
            SELECT name AS log_id,
                    count(sum_all) AS sumall,
                    count(sum_done) AS sumdone
            FROM backups
            WHERE (sum_done/sum_all)=1
            GROUP BY name
        ) AS sq
        WHERE backups_M.id = sq.log_id;
        """)  
        # Execute in one SQL statement
        xession.execute(sql)
        xession.commit()
    except:
        pass
    xession.close()


#################################################
def gd_fileuploaded(sender, file_path, file_jid, file_gid):
    print("")


#################################################
import sqlite3
import os
import json


def add_file(tree, path):
    current = tree
    folders, filename = os.path.split(path)
    for folder in folders.split(os.path.sep):
        if folder not in current["children"]:
            current["children"][folder] = {
                "type": "folder",
                "path": os.path.join(current["path"], folder),
                "children": {},
            }
        current = current["children"][folder]
    current["children"][filename] = {
        "type": "file",
        "path": str(path).replace("{{DRIVE}}", ":"),
        "children": {},
    }
    # print(json.dumps(current, indent=4))


def build_json_responseX(paths):
    hierarchy = {"type": "", "path": "", "children": {}}
    for path in paths:
        add_file(hierarchy, str(path).replace("", ""))
    return hierarchy


def restore_worker(event):
    import logging

    while not event.isSet():
        logging.debug("worker thread checking in")
        event.wait(1)


@app.route("/restore/file", methods=["POST"])
def get_restpre_file_data():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from module2 import BackupLogs, BackupMain
    from datetime import date
    
    backup_pid = request.json.get("backup_pid", None)
    file_name = request.json.get("file_name", None)
    obj = request.json.get("obj", None)
    dbname = os.path.join(app.config["location"], obj)
    
    bType = request.json.get("bType", None)
    if bType:
        engine = create_engine(f"sqlite:///{obj}.db")
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        xession = Session()
        q = xession.query(BackupLogs).filter(
            BackupLogs.sum_all == BackupLogs.sum_done,
            BackupLogs.pIdText == str(backup_pid),
            BackupLogs.full_file_name== str(str(obj) + os.sep +file_name).replace(":","{{DRIVE}}"), #) file_name,#os.path.join(tcc, file_name),
            #BackupLogs.size>0,
            BackupLogs.id == bType,
            #BackupLogs.fidi==fidi,
        )
        if q:
            if len(q.all())> 1:
                incr=q.order_by(BackupLogs.date_time).all()[-1]
                if incr:
                    incr={"timestamp": incr.date_time, "data" : incr.log}

                diff=q.order_by(BackupLogs.date_time).all()[0]
                if diff:
                    diff={"timestamp": diff.date_time, "data" : diff.log}
                
                return (jsonify(result={"incr":incr,"diff":diff}), 200)

            elif len(q.all())==1:
                incr=None
                incr=q.order_by(BackupLogs.date_time).all()[0]
                if incr:
                    diff={"timestamp": incr.date_time, "data" : incr.log}
                    incr={"timestamp": incr.date_time, "data" : incr.log}

                return (jsonify(result={"incr":incr,"diff":diff}), 200)
        
        return (jsonify(result={"incr":None,"diff":None}), 401)
        
                                    
    s_manager = SQLiteManager()

    if not backup_pid: #or not file_name or not obj:
       return 404
   
    file_name =  str(file_name).replace("{{DRIVE}}",":")

    if  str(file_name).startswith(str(obj)):
        file_name =  str(file_name).replace(str(obj)+"\\","")

    #q = "SELECT pidText, full_file_name ,name,id,from_computer,datetime(min(date_time), 'unixepoch') as first_c, datetime(max(date_time), 'unixepoch') as last_c FROM backups  where pidText = '" + str(backup_pid) + "' and sum_all=sum_done  group by pidText, from_computer,full_file_name"
    q = "SELECT pidText, replace(replace(full_file_name,'" + str(str(obj)+"\\") + "',''),'{{DRIVE}}',':') as file_path_name ,name,id,from_computer,datetime(min(date_time), 'unixepoch') as first_c, datetime(max(date_time), 'unixepoch') as last_c FROM backups  where pidText = '" + str( backup_pid )+ "' and sum_all=sum_done  group by pidText, from_computer,full_file_name"
    q = "SELECT pidText, replace(replace(full_file_name,'" + str(str(obj)+"\\") + "',''),'{{DRIVE}}',':') as file_path_name ,name,id,from_computer,min(date_time) as first_c, max(date_time)as last_c FROM backups  where pidText = '" + str( backup_pid )+ "' and replace(replace(full_file_name,'" + str(str(obj)+"\\") + "',''),'{{DRIVE}}',':') = file_name  and sum_all=sum_done  group by pidText, from_computer,full_file_name"
    q_min = "SELECT pidText, replace(replace(full_file_name,'" + str(str(obj)+"\\") + "',''),'{{DRIVE}}',':') as file_path_name ,name,id,from_computer,min(date_time) as first_c   FROM backups  where pidText = '" + str( backup_pid )+ "' and replace(replace(full_file_name,'" + str(str(obj)+"\\") + "',''),'{{DRIVE}}',':') = '" + file_name + "' and sum_all=sum_done  group by pidText, from_computer,full_file_name"
    q_max = "SELECT pidText, replace(replace(full_file_name,'" + str(str(obj)+"\\") + "',''),'{{DRIVE}}',':') as file_path_name ,name,id,from_computer,max(date_time) as last_c    FROM backups  where pidText = '" + str( backup_pid )+ "' and replace(replace(full_file_name,'" + str(str(obj)+"\\") + "',''),'{{DRIVE}}',':') = '" + file_name + "' and sum_all=sum_done  group by pidText, from_computer,full_file_name"

    file_paths=[]

    
    qrs = [(dbname,[q_max],)]
    
    results = s_manager.execute_queries(qrs)
    for db_path, db_results in results.items():
        print(f"Results for {db_path}:")
        for i, (result, records) in enumerate(db_results):
            print(f"  Query {i+1}: {result}")
            if result == "Success":
                if records is not None:
                    for file in records:
                        file_paths.append(dict(pidText =file[0], file_path_name=file[1],name =file[2],id =file[3],from_computer =file[4],first_c =0,last_c=file[5]))
                    print(f"    Records: {records}")
    
    qrs = [(dbname,[q_min],)]
    try:
        results = s_manager.execute_queries(qrs)
        for db_path, db_results in results.items():
            print(f"Results for {db_path}:")
            for i, (result, records) in enumerate(db_results):
                print(f"  Query {i+1}: {result}")
                if result == "Success":
                    if records is not None:
                        for file in records:
                            file_paths.append(dict(pidText =file[0], file_path_name=file[1],name =file[2],id =file[3],from_computer =file[4],first_c =file[5],last_c=0))
                        print(f"    Records: {records}")
    except:
        print("")
    # GDrive/cloud fallback: when backups is empty, query backups_M for file metadata
    if not file_paths and backup_pid and file_name:
        _fn_esc = str(os.path.basename(file_name)).replace("'", "''")
        _fn_full_esc = str(file_name).replace("'", "''")
        q_bm = (
            "SELECT pIdText, COALESCE(from_path || char(92) || file_name, file_name, from_path) as file_path_name, "
            "id, id, from_computer, date_time as first_c, date_time as last_c "
            "FROM backups_M WHERE pIdText = '" + str(backup_pid).replace("'", "''") + "' "
            "AND data_repo IN ('GDRIVE','GOOGLEDRIVE','AWSS3','AZURE','ONEDRIVE') "
            "AND (file_name = '" + _fn_esc + "' OR (from_path || char(92) || file_name) = '" + _fn_full_esc + "')"
        )
        try:
            qrs_bm = [(dbname, [q_bm])]
            res_bm = s_manager.execute_queries(qrs_bm)
            db_res = res_bm.get(dbname, [])
            if db_res and db_res[0][0] == "Success" and db_res[0][1]:
                for row in db_res[0][1]:
                    file_paths.append(dict(pidText=row[0], file_path_name=row[1], name=row[2], id=row[3], from_computer=row[4], first_c=row[5] or 0, last_c=row[6] or 0))
        except Exception:
            pass
    return (jsonify(result=file_paths), 200)

##kartik
# import tempfile
def add_unc_temppath():
    #base_temp = tempfile.gettempdir()  
    base_temp = os.path.join(app.config["UPLOAD_FOLDER"],"temp","received_chunks")
    try: 
        os.makedirs(base_temp, exist_ok=True)
    except:
        print("")
    if not base_temp.startswith("\\\\?\\"):
        base_temp = r'\\?\{}'.format(base_temp)
    return base_temp
##kartik
@app.route("/restore", methods=["POST"])
@role_required('admin','employee') ##kartik
@permission_required('restoreReadWrite')
def get_restore_data():
    # API contract: 200 = request processed (check result[] for per-file restore status).
    # 500 = restore failed; body has result=[{restore:"failed", reason:"..."}]. Frontend shows result[0].reason.
    import time
    from sqlalchemy.orm import sessionmaker
    from module2 import BackupLogs, BackupMain
    from datetime import date
    import sqlalchemy
    import json
    from sqlalchemy import create_engine, Column, Integer, String, Time, func
    from sqlalchemy.ext.declarative import declarative_base
    from pathlib import PureWindowsPath
    conn = None
    uid = None 
    pwd =None
    try:
        print(request.json)
    except:
        print("")

    if request.json is None:
        return (jsonify({"error": "invalid_or_expired_key"}), 401)
    selectedAction = request.json.get("action", "fetch")
    selectedStorageType = request.json.get("storageType", "LAN")
    selectedStorageTypeJSON = request.json.get("deststorageType", {"typ": "LAN"})
    requested_agent = request.json.get("agentName", "DESKTOP-SUCRQP8")
    requested_target_agent = request.json.get("targetAgentName", requested_agent)
    selectedAgent = requested_agent
    selectedAgentIP6 = request.json.get("agentIP6", "")
    selectedTargetAgent = requested_target_agent
    startDate = request.json.get("startDate", "15/11/2023, 12:00:00 AM")
    endDate = request.json.get("endDate", "15/11/2034, 11:59:00 PM")

    restore_job_id = ensure_job_id(
        request.json.get("t14")
        or request.json.get("j_sta")
        or request.json.get("backup_id")
    )
    log_event(
        logger,
        logging.INFO,
        restore_job_id,
        "restore",
        file_path=None,
        file_id=None,
        extra={
            "event": "restore_request",
            "action": selectedAction,
            "storage_type": selectedStorageType,
            "agent": request.json.get("agentName", ""),
            "target_agent": request.json.get("targetAgentName", ""),
            "start_date": startDate,
            "end_date": endDate,
        },
    )

    agent_lookup = search_client_nodes(selectedAgent)
    if agent_lookup.get("agent"):
        selectedAgent = agent_lookup["agent"]
    target_lookup = search_client_nodes(selectedTargetAgent)
    if target_lookup.get("agent"):
        selectedTargetAgent = target_lookup["agent"]

    if selectedTargetAgent == "":
        selectedTargetAgent = selectedAgent
    obj = search_client_nodes(selectedAgent)
    objIP = obj.get("ipAddress")
    if obj.get("ipAddress",None)!="":
        obj = clientnodes_x[obj.get("ipAddress")].get("key")
    else:
        obj = None
        from .jobdata import JobsRecordManager
        m=JobsRecordManager("records.db", "records.json",app=app)
        endp =[] 
        endpoints =[] 
        try:
            endp = m.fetch_nodes_as_json()
            m.close()
            if endp:
                for e in json.loads(endp):
                    if e["agent"] == requested_agent:
                        if e["idx"] in  app.config["agent_activation_keys"]:
                            x= search_clientnodes_x_nodes(e["idx"])
                            if x:
                                obj = x["key"]
                            else:
                                obj=e["idx"]
                            selectedAgent = requested_agent
                        break;

        except:
            print("AF")
        
        
          
    objTarget = search_client_nodes(selectedTargetAgent)
    objIPTarget = objTarget.get("ipAddress",None)

    try:
        objTarget = clientnodes_x[objTarget.get("ipAddress")].get("key")
    except Exception as excep:
        objTarget=obj
    
    selectedExtensions = request.json.get("selectedExtensions", ["*.*"])
    if not selectedExtensions:
        selectedExtensions = ["*.*"]
    all_types = "*.*" in selectedExtensions
    all_selected_types = {ext for ext in selectedExtensions if ext != "*.*"}

    if str(selectedStorageType).lower().replace(" ", "") in [
        "gdrive",
        "googledrive",
    ]:
        selectedStorageType = "GDRIVE"

    selectedStorageTYP = selectedStorageTypeJSON.get("typ", "LAN")
    selectedStorageIPC = selectedStorageTypeJSON.get("ipc", "")
    selectedStorageUID = selectedStorageTypeJSON.get("uid", "")
    selectedStorageIDN = selectedStorageTypeJSON.get("idn", "")
    selectedStorageLOC = selectedStorageTypeJSON.get("loc", "") 

    file_paths = []
    backup_jobs_json = {}

    #u, p = CredentialManager(selectedStorageIPC).retrieve_credentials(selectedStorageIPC)
    sbd=""   #SMB id
    sbc=""   #SMB pwd  
    
    if selectedAction == "browse" or selectedAction == "restore":

        selectedId = request.json.get("id", "0")
        s_manager = SQLiteManager()
        location_dir = app.config.get("location") or os.getcwd()
        dbname = os.path.join(location_dir, obj)

        # Query backups_M (GDrive/cloud metadata) first; fall back to "backups" for legacy LAN
        qry_m = (
            "SELECT from_path, file_name FROM backups_M WHERE "
            + "id = " + str(selectedId)
            + " AND data_repo = '" + str(selectedStorageType).replace("'", "''") + "'"
        )
        if not all_types and all_selected_types:
            qry_m += " AND (" + " OR ".join(
                [f"file_name LIKE '%{name.replace(chr(39), chr(39)+chr(39))}'" for name in all_selected_types]
            ) + ")"

        # Try multiple DB paths (no extension, .db, etc.) so we find the file that has backups_M
        exts = ["", ".db", ".sqlite", ".sqlite3", ".db3"]
        bases = [obj, request.json.get("agentName")]
        candidate_paths = []
        for b in bases:
            if not b:
                continue
            for e in exts:
                candidate_paths.append(os.path.join(location_dir, b + e))
        if dbname not in candidate_paths:
            candidate_paths.insert(0, dbname)

        for candidate in candidate_paths:
            if not os.path.isfile(candidate):
                continue
            try:
                qrs = [(candidate, [qry_m])]
                try_results = s_manager.execute_queries(qrs)
            except Exception:
                continue
            if candidate not in try_results or len(try_results[candidate]) == 0:
                continue
            status, records = try_results[candidate][0]
            if status == "Success" and records:
                for row in records:
                    from_path, file_name = (row[0] or ""), (row[1] or "")
                    path = (from_path + os.sep + file_name) if file_name else from_path
                    if path:
                        file_paths.append(path)
                break

        # Fallback: query legacy "backups" table (LAN backups)
        if not file_paths:
            qry = (
                "SELECT replace(replace(full_file_name,'',''), '"
                + os.path.join(obj, "").replace("'", "''") + "','') FROM backups WHERE "
                + "name = " + str(selectedId)
                + " AND data_repo = '" + str(selectedStorageType).replace("'", "''") + "'"
            )
            if not all_types and all_selected_types:
                qry = (
                    "SELECT replace(replace(full_file_name,'',''), '"
                    + os.path.join(obj, "").replace("'", "''") + "','') as xs FROM backups WHERE "
                    + "name = " + str(selectedId)
                    + " AND data_repo = '" + str(selectedStorageType).replace("'", "''") + "' "
                    + " AND (" + " OR ".join([f"full_file_name LIKE '%{n.replace(chr(39), chr(39)+chr(39))}'" for n in all_selected_types]) + ")"
                )
            qrs = [(dbname, [qry])]
            results = s_manager.execute_queries(qrs)
            for db_path, db_results in results.items():
                for i, (res, recs) in enumerate(db_results):
                    if res == "Success" and recs:
                        for file in recs:
                            file_paths.append(file[0])
                        break

        backup_jobs_json = build_json_responseX(file_paths)
        if selectedAction == "browse":
            return (jsonify(backup_jobs_json), 200)
    if selectedAction == "restore":
        # {
        #   'id': '1715576654.2687414',
        #   'agentName': 'DESKTOP-676DGF-3HS',
        #   'action': 'restore',
        #   'targetLocation': 'C:\\test01',
        #   'selectedFiles': ['C:\\test01\\ipmsg5.6.16_installer.exe'],
        #   'RestoreLocation': 'C:\\test01'
        #
        # }
        j_sta=str(time.time())
        # try:
        #     sktio.emit(
        #             "backup_data",
        #             {
        #                 "restore_flag":True,
        #                 "backup_jobs": [
        #                     {
        #                         "restore_flag":True,
        #                         "name": str(rec[11]),
        #                         "scheduled_time": datetime.datetime.fromtimestamp(
        #                             float(j_sta)
        #                         ).strftime("%H:%M:%S"),
        #                         "agent": str(selectedAgent) ,
        #                         "target_agent": str(selectedTargetAgent) ,
        #                         "progress_number": float(0),
        #                     }
        #                 ]
        #             },
        #         )
        # except:
        #     print("")
        try:
            if str(selectedStorageType).upper() in ['AWS','GDRIVE','ONEDRIVE','AZURE']:
                rec_response, status_code = validate_credentials_clouds(selectedStorageType)
                response_data = rec_response.json
                if status_code in [200,'200', 201,'201']:
                    if 'valid' in response_data and response_data['valid'] == False:
                        return jsonify({"error":f'Destination storage not configured {selectedStorageType}'})
                elif status_code in [400,404,500]:
                    return jsonify({"error":f'Unexpected problem {selectedStorageType},Please reconfigure or Contact for help'})

            print(str(request.json))
            # file_paths = []
            selectedId = request.json.get("id", "0")
            targetLocation = request.json.get("targetLocation", "")
            sourceLocation = request.json.get("sourceLocation", "") 
            selectedFiles = request.json.get("selectedFiles", [])
            selectedFolder = request.json.get("selectedFolder", [targetLocation])
            if selectedFolder is None:
                selectedFolder = [targetLocation]
            if selectedFiles is None:
                selectedFiles = []
            RestoreLocation = request.json.get("RestoreLocation", targetLocation)
            if RestoreLocation == None:
                RestoreLocation = targetLocation
            elif RestoreLocation and os.path.isfile(targetLocation):
                #RestoreLocation = os.path.join( RestoreLocation, os.path.basename(targetLocation))
                RestoreLocation = RestoreLocation
            
            # targetLocation = os.path.sep.join(targetLocation.split(os.path.sep)[0:], "")
            # RestoreLocation = os.path.sep.join(
            #     RestoreLocation.split(os.path.sep)[0:], ""
            # )
            # targetLocation = os.path.sep.join(targetLocation.split(os.path.sep)[0:], "")
            # RestoreLocation = os.path.sep.join(
            #     RestoreLocation.split(os.path.sep)[0:], ""
            # )

            k_qresults=[]
            qresults=[]
            try:
                dbname = os.path.join(app.config["location"], obj)
                # conn = sqlite3.connect(
                #     os.path.join(app.config["location"], obj) + ".db"
                # )
                # cursor = conn.cursor()
                # if len(selectedFiles) > 0:
                #     files = [
                #         "'"
                #         + os.path.join(f"{obj}", element.replace(":", "{{DRIVE}}"))
                #         + "'"
                #         for element in selectedFiles
                #     ]
                #     files = ",".join(files)
                #     print(files)
                # cursor.execute(
                #     "SELECT * FROM backups where "
                #     + "name = "
                #     + str(selectedId)
                #     + " and data_repo = '"
                #     + str(selectedStorageType)
                #     + "'"
                #     + " and full_file_name in ("
                #     + files
                #     + ")"
                # )
                # file_paths = cursor.fetchall()
                # cursor.close()
                # conn.close()
                s_manager = SQLiteManager()
                dbname = os.path.join(app.config["location"], obj)
                files=""
                backups_query=[]
                # if len(selectedFiles) <= 0:
                #     selectedFiles = file_paths
                #     if not all_types:
                #         if all_selected_types:
                #             print("todo selected file extentions")
##########################################
                if selectedFiles==None:
                    selectedFiles=[]
                if len(selectedFiles) > 0:
                    files = [
                        "'"
                        + os.path.join(f"{obj}", element.replace(":", "{{DRIVE}}"))
                        + "'"
                        for element in selectedFiles
                    ]
                    files = ",".join(files)
                    files = " and full_file_name in ("+ files + ")"

                    backups_query.append("SELECT *,'" + targetLocation.replace(":", "{{DRIVE}}") +"' as fpath   FROM backups where "
                    + "name = " + str(selectedId)
                    + " and data_repo = '" + str(selectedStorageType)+ "' "
                    + files)


                if not all_types and len(selectedFiles) <= 0:
                    if all_selected_types:

                        files = str("and (" + " OR ".join(
                                [
                                    f"full_file_name LIKE '%{name}'"
                                    for name in all_selected_types
                                ]
                            )
                            + ")"
                        )
                        backups_query.append("SELECT *,'" + targetLocation.replace(":", "{{DRIVE}}") +"' as fpath   FROM backups where "
                            + "name = " + str(selectedId)
                            + " and data_repo = '" + str(selectedStorageType)+ "' "
                            + files)
                
                if len(selectedFolder) > 0 and len(selectedFiles) <= 0:
                    for fpath in selectedFolder:
                        # files = [
                        #     " from_path like '"
                        #     + os.path.join(f"{obj}", element.replace(":", "{{DRIVE}}"))
                        #     + "%'"
                        #     for element in selectedFiles
                        # ]
                        # files = " or ".join(files)
                        # files = " and  ("+ files + ")" 
                        fpath_parent = str(PureWindowsPath(os.path.join(f"{obj}", fpath.replace(":", "{{DRIVE}}"))).parent)
                        if RestoreLocation==targetLocation:
                            fpath_parent =   targetLocation.replace(":", "{{DRIVE}}") 
                        backups_query.append("SELECT * ,'"+ fpath_parent +"' as fpath FROM backups where "
                                + " name = " + str(selectedId)
                                + " and data_repo = '" + str(selectedStorageType)+ "'"
                                + " and (from_path like '" + os.path.join(f"{obj}", fpath.replace(":", "{{DRIVE}}"))+ "%') "
                                )

                qrs = [
                        (
                            dbname,
                            [
                                # "SELECT * FROM backups where "
                                # + "name = " + str(selectedId)
                                # + " and data_repo = '" + str(selectedStorageType)+ "'"
                                # + files
                                " UNION ALL ".join(backups_query)
                            ,
                                "SELECT * FROM backups_m where "
                                + "id = "
                                + str(selectedId)
                                + " and data_repo = '"
                                + str(selectedStorageType)
                                + "'"
                                + ""
                            ],
                        )
                    ]
                
                results = s_manager.execute_queries(qrs)
                k_qresults=[]
                for db_path, db_results in results.items():
                    print(f"Results for {db_path}:")
                    for i, (result, records) in enumerate(db_results):
                        print(f"  Query {i+1}: {result}")
                        if result == "Success":
                            if records is not None:
                                #file_paths = [file for file in records]
                                k_qresults.append([file for file in records])
                                print(f"    Records: {records}")
                if len(qresults)==0:
                    qresults.append(k_qresults[0])
                    qresults.append(k_qresults[1])
                else:
                    qresults[0]+=k_qresults[0]
                    qresults[1]=k_qresults[1]
                # GDrive/cloud: Query 1 (backups) is empty, Query 2 (backups_M) has rows – use backups_M as file list
                if len(qresults[0]) == 0 and len(qresults[1]) > 0:
                    qresults[0] = list(qresults[1])
                
                k_qresults=None


            except Exception as e:
                print(
                    "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                )
                print(
                    "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                )
                print(str(e))
                print(
                    "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                )
                print(
                    "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                )
                # 500 = restore failed (body has reason). Frontend must show result[0].reason, not generic "Request failed with status code 500".
                return (jsonify(result=[{"restore": "failed", "reason": str(e)}]), 500)

            # file_paths = [row[0] for row in cursor.fetchall()]
            # file_paths = [row for row in cursor.fetchall()]
            # file_paths = [row for row in cursor.fetchall()]
            import base64

            # file_paths = [row for row in cursor.fetchall()]
            rr = []
            # rr_ = []
            # rr_ = []
            file_paths = qresults[0]
            totalfiles = len (file_paths)
            pendingfiles = len (file_paths)
            files_restored=0
            if totalfiles == 0:
                log_event(
                    logger,
                    logging.WARNING,
                    restore_job_id,
                    "restore",
                    file_path=None,
                    file_id=None,
                    error_code="NO_RESTORE_DATA",
                    error_message="No restore data available for selection",
                    extra={
                        "event": "restore_no_data",
                        "agent": selectedAgent,
                        "target_agent": selectedTargetAgent,
                        "storage_type": selectedStorageType,
                    },
                )
            backup_id=""
            backup_name=""
            frombackup_computer_name=selectedAgent
            torestore_computer_name=selectedTargetAgent
            res_json={}
            
##################

                

####################
            file_paths = qresults[0]
            file_master = [dict(bk) for bk in qresults[1]][0]
            mime_type="folder"
            if file_master:
                mime_type= file_master.get("mime_type","folder")
                if mime_type == "folder" and file_master.get("file_name","")!="":
                    mime_type="file"
                
            for rec in file_paths:
                rec_dict = dict(rec)
                if not rec_dict.get("full_file_name"):
                    rec_dict["full_file_name"] = (rec_dict.get("from_path") or "") + os.sep + (rec_dict.get("file_name") or "")
                # For GDrive/cloud: backups_M has data_repod (gidn/givn), not log; use it as log so client can restore
                if rec_dict.get("data_repod") and (not rec_dict.get("log") or rec_dict.get("log") == "{}"):
                    try:
                        _dr = rec_dict.get("data_repod")
                        if isinstance(_dr, str) and _dr.strip():
                            rec_dict["log"] = _dr
                    except Exception:
                        pass
                if not rec_dict.get("log"):
                    rec_dict["log"] = "{}"
                rec_dict.setdefault("fpath", RestoreLocation)
                rec_dict.setdefault("name", rec_dict.get("id"))
                backup_id = str(rec_dict.get("id", ""))
                backup_pid = str(rec_dict.get("name", rec_dict.get("id", "")))
                backup_name = str(rec_dict.get("pNameText", ""))
                backup_name_id = str(rec_dict.get("pIdText", ""))
                frombackup_computer_name = str(rec_dict.get("from_computer", ""))
                _tcc_value = str(rec_dict.get("full_file_name", ""))
                # Choose a source path that actually appears in _tcc_value so replacement works
                _rec_fpath = str(rec_dict.get("fpath", RestoreLocation))
                try:
                    _source_candidates = [
                        rec_dict.get("fpath"),
                        rec_dict.get("from_path"),
                        targetLocation,
                        RestoreLocation,
                    ]
                    for _cand in _source_candidates:
                        if not _cand:
                            continue
                        _cand_str = str(_cand)
                        _cand_norm = _cand_str.replace(":", "{{DRIVE}}")
                        if _cand_str in _tcc_value or _cand_norm in _tcc_value:
                            _rec_fpath = _cand_str
                            break
                except Exception:
                    pass
                
                sktio.emit(
                    "backup_data",
                    {
                        "restore_flag":True,
                        "backup_jobs": [
                            {
                                "restore_flag":True,
                                "name": backup_name,
                                "scheduled_time": datetime.datetime.fromtimestamp(
                                    float(j_sta)
                                ).strftime("%H:%M:%S"),
                                "agent": str(torestore_computer_name) ,
                                "progress_number": float(100 * (float(pendingfiles)))
                                / float(totalfiles),
                                "id": j_sta,
                                "restore_location":RestoreLocation, ##kartik
                            }
                        ]
                    },
                )
                print(
                    "DDD "
                    + _tcc_value.replace(
                        targetLocation.replace(":", "{{DRIVE}}"),
                        RestoreLocation.replace(":", "{{DRIVE}}"),
                    )
                )
                sbd=""   #SMB id
                sbc=""   #SMB pwd   
                jsrepd = json.loads(rec_dict.get("log", "{}"))
                try:
                    if isinstance(jsrepd, str):
                        jsrepd = json.loads(jsrepd)
                except:
                    print(".. .. ..")
                # Normalize GDrive gidn_list for restore: old backups may have only gidn (dict) or wrong gidn_list
                rep_upper_pre = str(selectedStorageType).upper().replace(" ", "")
                if rep_upper_pre in ["GDRIVE", "GOOGLEDRIVE"] and jsrepd:
                    gidn_list = jsrepd.get("gidn_list")
                    gidn = jsrepd.get("gidn")
                    total_chunks = int(jsrepd.get("total_chunks", 1)) or 1
                    if not gidn_list or not isinstance(gidn_list, list) or len(gidn_list) != total_chunks:
                        if gidn is not None:
                            if isinstance(gidn, list):
                                jsrepd["gidn_list"] = gidn
                            elif isinstance(gidn, dict):
                                jsrepd["gidn_list"] = [gidn]
                            else:
                                jsrepd["gidn_list"] = [gidn]
                            rec_dict["log"] = json.dumps(jsrepd)
                file_name_for_manifest = rec_dict.get("file_name") or os.path.basename(
                    rec_dict.get("full_file_name", "")
                )
                tcc_value = _tcc_value
                manifest_path = _final_manifest_path(tcc_value, file_name_for_manifest, backup_id)
                # GDrive/AWS/Azure/OneDrive: no local manifest; use data_repod (already in rec_dict["log"]) for restore
                rep_upper = str(selectedStorageType).upper().replace(" ", "")
                is_gdrive_restore = rep_upper in ["GDRIVE", "GOOGLEDRIVE"] and (
                    jsrepd.get("gidn") is not None or (jsrepd.get("gidn_list") and len(jsrepd.get("gidn_list", [])) > 0)
                )
                is_aws_azure_onedrive_restore = rep_upper in ["AWSS3", "AZURE", "ONEDRIVE"] and (
                    jsrepd.get("file_name_x") or (jsrepd.get("path") is not None and jsrepd.get("j_sta") is not None)
                )
                # UNC backups store data on remote share - treat like cloud restore (no local manifest)
                # UNC metadata includes: scombm (host), scombs (share), guid (folder containing chunks)
                is_unc_restore = rep_upper == "UNC" and jsrepd.get("scombm") and jsrepd.get("scombs")
                is_cloud_restore = is_gdrive_restore or is_aws_azure_onedrive_restore or is_unc_restore
                if is_cloud_restore:
                    total_chunks_g = int(jsrepd.get("total_chunks", 1)) or 1
                    manifest_data = {
                        "total_chunks": total_chunks_g,
                        "chunks": {str(i): "" for i in range(1, total_chunks_g + 1)},
                    }
                    found_manifest_path = None
                    
                    # UNC-specific: Build manifest from stored chunk metadata
                    # UNC backup stores chunks array with path, hash, size in jsrepd
                    if is_unc_restore and jsrepd.get("chunks"):
                        unc_chunks = jsrepd.get("chunks", [])
                        if isinstance(unc_chunks, list) and len(unc_chunks) > 0:
                            manifest_data["total_chunks"] = len(unc_chunks)
                            manifest_data["chunks"] = {}
                            for idx, chunk_info in enumerate(unc_chunks, 1):
                                if isinstance(chunk_info, dict):
                                    # Store chunk hash for verification
                                    manifest_data["chunks"][str(idx)] = chunk_info.get("hash", "")
                            # Store UNC connection info for client to use during restore
                            manifest_data["unc_host"] = jsrepd.get("scombm", "")
                            manifest_data["unc_share"] = jsrepd.get("scombs", "")
                            manifest_data["unc_guid"] = jsrepd.get("guid", "")
                            manifest_data["unc_chunks"] = unc_chunks  # Full chunk info for paths
                            if jsrepd.get("givn"):
                                manifest_data["givn"] = jsrepd.get("givn")
                            log_event(
                                logger, logging.INFO, ensure_job_id(j_sta), "restore",
                                file_path=rec_dict.get("full_file_name"), file_id=backup_id,
                                error_code="", error_message="",
                                extra={
                                    "event": "unc_manifest_built",
                                    "unc_host": manifest_data["unc_host"],
                                    "unc_share": manifest_data["unc_share"],
                                    "total_chunks": manifest_data["total_chunks"],
                                },
                            )
                    
                    try:
                        if os.path.exists(manifest_path):
                            with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                                disk_manifest = json.load(manifest_file)
                            if disk_manifest.get("total_chunks"):
                                manifest_data["total_chunks"] = disk_manifest.get("total_chunks")
                            # GDrive/AWS/Azure/OneDrive: do not use disk manifest chunk hashes - chunks live in cloud and disk manifest may be from a different backup, causing CHECKSUM_MISMATCH on restore
                            if not (is_gdrive_restore or is_aws_azure_onedrive_restore) and disk_manifest.get("chunks"):
                                manifest_data["chunks"] = disk_manifest.get("chunks")
                            if disk_manifest.get("file_hash"):
                                manifest_data["file_hash"] = disk_manifest.get("file_hash")
                            found_manifest_path = manifest_path
                    except Exception:
                        pass
                    if not manifest_data.get("file_hash"):
                        try:
                            base_temp = add_unc_temppath()
                            base_temp_candidates = [base_temp]
                            if str(base_temp).startswith("\\\\?\\"):
                                base_temp_candidates.append(str(base_temp).replace("\\\\?\\", ""))
                            from_path_raw = rec_dict.get("from_path") or ""
                            from_path_norm = str(from_path_raw).replace(":", "{{DRIVE}}")
                            best_manifest = None
                            best_mtime = 0
                            def _scan_for_manifest(scan_root, require_path_filter=True):
                                nonlocal best_manifest, best_mtime
                                if not scan_root or not os.path.exists(scan_root):
                                    return
                                for root, _, files in os.walk(scan_root):
                                    if require_path_filter and from_path_norm and from_path_norm not in root:
                                        continue
                                    for fname in files:
                                        if fname.startswith(f"{file_name_for_manifest}_") and fname.endswith(".manifest.json"):
                                            cand = os.path.join(root, fname)
                                            try:
                                                mtime = os.path.getmtime(cand)
                                            except Exception:
                                                mtime = 0
                                            if mtime >= best_mtime:
                                                best_manifest = cand
                                                best_mtime = mtime
                            for root in base_temp_candidates:
                                _scan_for_manifest(root, require_path_filter=True)
                            if not best_manifest:
                                for root in base_temp_candidates:
                                    _scan_for_manifest(root, require_path_filter=False)
                            if not best_manifest:
                                _scan_for_manifest(app.config.get("UPLOAD_FOLDER"), require_path_filter=False)
                            if best_manifest:
                                with open(best_manifest, "r", encoding="utf-8") as manifest_file:
                                    temp_manifest = json.load(manifest_file)
                                if temp_manifest.get("total_chunks"):
                                    manifest_data["total_chunks"] = temp_manifest.get("total_chunks")
                                # GDrive/AWS/Azure/OneDrive: keep empty chunk hashes so client skips per-chunk checksum (disk manifest hashes may not match cloud chunks)
                                if not (is_gdrive_restore or is_aws_azure_onedrive_restore) and temp_manifest.get("chunks"):
                                    manifest_data["chunks"] = temp_manifest.get("chunks")
                                if temp_manifest.get("file_hash"):
                                    manifest_data["file_hash"] = temp_manifest.get("file_hash")
                                found_manifest_path = best_manifest
                                if not os.path.exists(manifest_path):
                                    try:
                                        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
                                        import shutil
                                        shutil.copyfile(best_manifest, manifest_path)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                    if not manifest_data.get("file_hash") and jsrepd:
                        for key in ["file_hash", "filehash", "hash", "sha256", "sha256Checksum"]:
                            if jsrepd.get(key):
                                manifest_data["file_hash"] = str(jsrepd.get(key))
                                break
                    try:
                        log_event(
                            logger,
                            logging.INFO,
                            ensure_job_id(j_sta),
                            "restore",
                            file_path=rec_dict.get("full_file_name"),
                            file_id=backup_id,
                            error_code="",
                            error_message="",
                            extra={
                                "event": "restore_manifest_selected",
                                "manifest_path": found_manifest_path,
                                "final_manifest_path": manifest_path,
                                "manifest_total_chunks": manifest_data.get("total_chunks"),
                                "manifest_has_chunks": bool(manifest_data.get("chunks")),
                                "manifest_file_hash": manifest_data.get("file_hash"),
                            },
                        )
                    except Exception:
                        pass
                else:
                    if not os.path.exists(manifest_path):
                        log_event(
                            logger,
                            logging.ERROR,
                            ensure_job_id(j_sta),
                            "restore",
                            file_path=rec_dict.get("full_file_name"),
                            file_id=backup_id,
                            error_code="MISSING_CHUNKS",
                            error_message="Manifest missing; aborting restore",
                            extra={"event": "restore_aborted", "manifest_path": manifest_path},
                        )
                        resp_dict.append(
                            {
                                "file": rec_dict.get("full_file_name"),
                                "restore": "failed",
                                "reason": "MISSING_CHUNKS",
                            }
                        )
                        pendingfiles = pendingfiles - 1
                        continue
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                            manifest_data = json.load(manifest_file)
                        if not manifest_data.get("chunks") or not manifest_data.get("total_chunks"):
                            raise ValueError("Manifest missing chunk data")
                    except Exception as manifest_error:
                        log_event(
                            logger,
                            logging.ERROR,
                            ensure_job_id(j_sta),
                            "restore",
                            file_path=rec_dict.get("full_file_name"),
                            file_id=backup_id,
                            error_code="MISSING_CHUNKS",
                            error_message=str(manifest_error),
                            extra={"event": "restore_aborted", "manifest_path": manifest_path},
                        )
                        resp_dict.append(
                            {
                                "file": rec_dict.get("full_file_name"),
                                "restore": "failed",
                                "reason": "MISSING_CHUNKS",
                            }
                        )
                        pendingfiles = pendingfiles - 1
                        continue
                if str(selectedStorageType) =="UNC": # in ["UNC","NAS"]:
                    print(jsrepd)  
                    #jsrepd['scombm']
                    
                    if not conn:
                        try:
                            cm = CredentialManager(jsrepd.get("scombm", ""))
                            uid, pwd = cm.retrieve_credentials(jsrepd.get("scombm", ""))
                        
                            # if uid == None or pwd == None or  uid == "" or pwd == "":
                            #     print("failed to login")
                            #     uid, pwd = cm.retrieve_credentials(jsrepd.get("scom", ""))
                            #     if uid == None or pwd == None or  uid == "" or pwd == "":
                            #         print("failed to login")
                            # repo_d = {
                            #     "ipc": str(jsrepd["scombm"]),
                            #     "uid": str(uid),
                            #     "idn": str(pwd),
                            #     "loc": str(jsrepd["scombs"]),
                            # }
                            # conn = getConn(repo_d,keyx=obj)
                    

                        except Exception as e:
                            print(str(e))
                            # return (
                            #     jsonify({"file": "*", "restore": "failed", "reason": (str(e))}),
                            #     500,
                            # )
                full_name = rec_dict.get("full_file_name") or ""
                from_path = rec_dict.get("from_path") or ""
                suffix = full_name.replace(from_path, "")
                if mime_type == "file" and full_name and (not RestoreLocation.endswith("".join(suffix))):
                    original_p = suffix
                    if original_p.startswith(os.sep):
                        original_p="".join(original_p.split(os.sep)[0:])
                    RestoreLocation = os.path.join(RestoreLocation,original_p)
                
                #if conn:
                try:
                    sbd=str(uid)   #SMB id
                    sbc=str(pwd)   #SMB pwd 
                    #print("conn succeed")
                except:
                    pass
                # For UNC, use RestoreLocation directly (the complex _tcc_value replacement doesn't work)
                # For other storage types, use the replacement logic
                if str(selectedStorageType).upper() == "UNC":
                    # UNC: Use restore location directly with {{DRIVE}} placeholder
                    _tccx_value = str(RestoreLocation).replace(":", "{{DRIVE}}")
                    _tccn_value = str(RestoreLocation).replace(":", "{{DRIVE}}")
                else:
                    _tccx_value = _tcc_value.replace(
                        _rec_fpath.replace(":", "{{DRIVE}}"),
                        str(RestoreLocation+"\\").replace(":", "{{DRIVE}}"),
                    ).replace("\\\\","\\").rstrip('\\' if mime_type=='file' else '')
                    _tccn_value = _tccx_value  # Same transformation
                
                header = {
                    "id": backup_id,
                    "pid": backup_pid,
                    "obj": str(obj),
                    "pnametext": backup_name,
                    "mime": str(rec_dict.get("mime_type", "file")),
                    "objtarget": str(obj), #str(objTarget),
                    "tcc": base64.b64encode(
                        gzip.compress(
                            _tcc_value.encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "sbd": base64.b64encode(
                        gzip.compress(
                            str(sbd).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "sbc": base64.b64encode(
                        gzip.compress(
                            str(sbc).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "tccsrc": base64.b64encode(
                        gzip.compress(
                            _tcc_value.encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "tccx": base64.b64encode(
                        gzip.compress(
                            _tccx_value.encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "rep": base64.b64encode(
                        gzip.compress(
                            str(selectedStorageType).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "repd": base64.b64encode(
                        gzip.compress(
                            str(rec_dict.get("log") or "{}").encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "jid": base64.b64encode(
                        gzip.compress(
                            backup_name_id.encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "tccn": base64.b64encode(
                        gzip.compress(
                            os.path.join(
                                str(rec_dict.get("from_path", "")).replace(
                                    _rec_fpath.replace(":", "{{DRIVE}}"),
                                    str(RestoreLocation+"\\").replace(":", "{{DRIVE}}"),
                                ).replace("\\\\","\\").rstrip('\\' if mime_type=='file' else ''),
                                str(rec_dict.get("file_name", "")),
                            ).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "tccnna": base64.b64encode(
                        gzip.compress(
                            str(RestoreLocation.replace(":", "{{DRIVE}}"),
                                ).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "tccnrest": base64.b64encode(
                        gzip.compress(
                            str(RestoreLocation.replace(":", "{{DRIVE}}")).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                    "tccnstamp": base64.b64encode(
                        gzip.compress(
                            str(j_sta).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        )
                    ),
                }
                if mime_type == "file":                    
                    header.update({"tccn": base64.b64encode(
                        gzip.compress(
                            str( os.path.join( "X" + os.path.sep + RestoreLocation)).encode("UTF-8"),
                            9,
                            mtime=time.time(),
                        ))})
                print("FFF " + str(header))
                rr.append(header)
                event = threading.Event()
            resp_dict = []
            res=None
            ftotal=len(rr)
            fci=0
            for re in rr:
                res_json={}
                try:
                    res_json["backup_id"]=backup_id
                    res_json["backup_pid"]=backup_pid
                    res_json["backup_name"]=backup_name
                    res_json["backup_name_id"]=backup_name_id
                    res_json["frombackup_computer_name"]=frombackup_computer_name
                    res_json["torestore_computer_name"]=torestore_computer_name
                    res_json["targetLocation"]=targetLocation
                    res_json["RestoreLocation"]=RestoreLocation
                    res_json["selectedStorageType"]=selectedStorageType
                    res_json["t14"]=str(j_sta)
                    res_json["isMetaFile"]=jsrepd.get('isMetaFile',False)
                    try:
                        if is_cloud_restore:
                            res_json["chunk_manifest"] = manifest_data
                        else:
                            with open(manifest_path, "r", encoding="utf-8") as manifest_file:
                                res_json["chunk_manifest"] = json.load(manifest_file)
                    except Exception:
                        res_json["chunk_manifest"] = {}
                    
                    fci+=1
                    # threading.Thread(
                    #     target=requests.post(f"{objIP}/restoretest", headers=re,json={"test": "0","fci":str(fci),"ftotal":str(ftotal)})
                    # ).start()
                    date_time_now =datetime.datetime.now()                    
                    res_json.update({"file_start_time":date_time_now.strftime("%Y %m %d, %H:%M:%S")})
                    res_json.update({"file_start_end":""})
                    res_json.update({"file_restore_timetaken":""})
                    re.update({'extd':base64.b64encode(gzip.compress(str(res_json).encode("UTF-8"), 9,mtime=time.time(),))})
                    res = None
                    try:
                        res = requests.post(
                            f"{objIPTarget}/restoretest", headers=re, json={"test": "0","fci":str(fci),"ftotal":str(ftotal)},
                            timeout=300
                        )
                        # Only count as restored when response body explicitly says success
                        if res.status_code in [200, 201]:
                            try:
                                res_body = res.json() if res.content else {}
                                if res_body.get("restore") == "success":
                                    files_restored += 1
                            except Exception:
                                pass
                    except Exception as e:
                        log_event(
                            logger, logging.WARNING, ensure_job_id(j_sta), "restore",
                            file_path=rec_dict.get("full_file_name"), file_id=backup_id,
                            error_code="CLIENT_RESTORE_REQUEST_FAILED", error_message=str(e),
                            extra={"event": "restore_client_request_failed", "objIPTarget": objIPTarget},
                        )
                        res_json["restore"] = "failed"
                        res_json["reason"] = str(e) if str(e) else "Client connection closed or timeout"
                except Exception as e:
                    print("")
                
                date_time_finish_now =datetime.datetime.now()                    
                res_json.update({"file_start_end":date_time_finish_now.strftime("%Y %m %d, %H:%M:%S")})
                res_json.update({"file_restore_timetaken":(date_time_finish_now - date_time_now).seconds })
                if res is not None:
                    try:
                        res_body = res.json()
                        res_json.update(res_body)
                        if res.status_code not in [200, 201]:
                            client_reason = (res_body or {}).get("reason", getattr(res, "text", "") or "")
                            log_event(
                                logger, logging.WARNING, ensure_job_id(j_sta), "restore",
                                file_path=rec_dict.get("full_file_name"), file_id=backup_id,
                                error_code="CLIENT_RESTORE_5XX",
                                error_message=client_reason or str(res.status_code),
                                extra={"event": "restore_client_5xx", "status": res.status_code, "reason": client_reason},
                            )
                            if client_reason:
                                res_json["reason"] = client_reason
                    except Exception as parse_err:
                        res_json.setdefault("restore", "failed")
                        res_json.setdefault("reason", f"Client returned {res.status_code}")
                        try:
                            raw = getattr(res, "text", None) or ""
                            if raw:
                                res_json["reason"] = raw[:500]
                        except Exception:
                            pass
                resp_dict.append(res_json)  
                pendingfiles=pendingfiles-1
                
                sktio.emit(
                    "backup_data",
                    {
                        "restore_flag":True,
                        "backup_jobs": [
                            {
                                "restore_flag":True,
                                "name": backup_name,
                                "scheduled_time": datetime.datetime.fromtimestamp(
                                    float(j_sta)
                                ).strftime("%H:%M:%S"),
                                "agent": str(torestore_computer_name) ,
                                "progress_number": float(100 * (float(pendingfiles)))
                                / float(ftotal),
                                "id": j_sta,
                                "restore_accuracy": float(100 * (float(files_restored)))
                                / float(ftotal),
                                "restore_location":res_json["RestoreLocation"], ##kartik
                            }
                        ]
                    },
                )
            
            filescount=0
            try:
                filescount = float(ftotal) - float(pendingfiles)
            except:
                filescount=0
            from collections import defaultdict
            unique_records = set()
            result = []
            keys=["backup_id","backup_name","frombackup_computer_name","torestore_computer_name","targetLocation","RestoreLocation","selectedStorageType","t14"]
            for record in resp_dict:
                key_tuple = tuple(record.get(key) for key in keys)
                if key_tuple not in unique_records:
                    unique_records.add(key_tuple)
                    result.append({key: record[key] for key in keys})
            if len(result)>0:
                from sqlalchemy.orm import sessionmaker
                
                engine = create_engine("sqlite:///" + str(app.config.get("getCode",None))+".db")
                session = sessionmaker(bind=engine)()
                restore_parent_o = restore_parent(
                        RestoreLocation=RestoreLocation, 
                        backup_id=backup_pid,
                        storage_type=selectedStorageType,
                        backup_name=backup_name,                
                        p_id=backup_name_id,                
                        t14=float(str(j_sta)) ,
                        from_backup_pc=frombackup_computer_name, 
                        targetlocation=targetLocation,
                        torestore_pc=torestore_computer_name
                )
                q = session.query(restore_parent).filter_by(
                    RestoreLocation=RestoreLocation, 
                        backup_id=backup_pid,
                        storage_type=selectedStorageType,
                        backup_name=backup_name,                
                        p_id=backup_name_id,                
                        t14=float(str(j_sta)) ,
                        from_backup_pc=frombackup_computer_name, 
                        targetlocation=targetLocation,
                        torestore_pc=torestore_computer_name).first()
                if not q:
                    session.add(restore_parent_o)
                    session.commit()
                if resp_dict:
                    for f in resp_dict:
                        q = session.query(restore_child).filter_by(
                                RestoreLocation=RestoreLocation, 
                                backup_id=float(backup_pid),
                                backup_file_id=float(f.get("backup_id",0)),
                                backup_name=backup_name,
                                p_id=backup_name_id,
                                file=f.get("file",""), 
                                file_restore_time=f.get("file_restore_timetaken",""),
                                file_start=f.get("file_start_time",""),
                                file_end= f.get("file_start_end",""),
                                from_backup_pc=frombackup_computer_name, 
                                reason= f.get("reason",""),
                                restore=f.get("restore",""),
                                storage_type=selectedStorageType,
                                t14=float(str(j_sta)) ,
                                targetlocation=targetLocation,
                                torestore_pc=torestore_computer_name
                            ).first()
                        if not q:
                            restore_child_o = restore_child(
                                RestoreLocation=RestoreLocation, 
                                backup_id=float(backup_pid),
                                backup_file_id=float(f.get("backup_id",0)),
                                backup_name=backup_name,
                                p_id=backup_name_id,
                                file=f.get("file",""), 
                                file_restore_time=f.get("file_restore_timetaken",""),
                                file_start=f.get("file_start_time",""),
                                file_end= f.get("file_start_end",""),
                                from_backup_pc=frombackup_computer_name, 
                                reason= f.get("reason",""),
                                restore=f.get("restore",""),
                                storage_type=selectedStorageType,
                                t14=float(str(j_sta)) ,
                                targetlocation=targetLocation,
                                torestore_pc=torestore_computer_name
                            )
                            session.add(restore_child_o)
                            session.commit()
                session.close()

            restored_count = sum(1 for f in resp_dict if f.get("restore") == "success")
            failed_count = sum(1 for f in resp_dict if f.get("restore") == "failed")
            try:
                final_status = "failed" if failed_count > 0 else "completed"
                accuracy_pct = (restored_count / float(totalfiles)) * 100 if totalfiles else 0
                sktio.emit(
                    "backup_data",
                    {
                        "backup_jobs": [
                            {
                                "restore_flag": True,
                                "name": backup_name,
                                "scheduled_time": datetime.datetime.fromtimestamp(
                                    float(j_sta)
                                ).strftime("%H:%M:%S"),
                                "agent": str(torestore_computer_name),
                                "progress_number": 0,
                                "id": j_sta,
                                "restore_accuracy": accuracy_pct,
                                "restore_location": RestoreLocation,
                                "finished": True,
                                "status": final_status,
                            }
                        ]
                    },
                )
            except Exception:
                print("")
            # Only notify "restored" when all files succeed
            if restored_count > 0 and failed_count == 0:
                try:
                    nows = datetime.datetime.now()
                    m_j = {
                        "agent": str(f"from {selectedAgent} to {selectedTargetAgent}"),
                        "idx": str(app.config.get("getCode", None)),
                        "event": "restore",
                        "job_id": backup_id,
                        "job_name": backup_name,
                        "error_desc": str(
                            f"restore of {restored_count} files done from {selectedAgent} to {selectedTargetAgent}"
                        ),
                        "missed_time": str(nows),
                    }
                    res = requests.post(
                        "http://127.0.0.1:53335/api/sendtoserver",
                        json=m_j,
                    )
                    if res is not None:
                        print(res.content)
                except Exception:
                    print("")
            log_event(
                logger,
                logging.INFO,
                restore_job_id,
                "restore",
                file_path=None,
                file_id=None,
                extra={
                    "event": "restore_complete",
                    "total_files": totalfiles,
                    "restored": restored_count,
                    "failed": failed_count,
                    "storage_type": selectedStorageType,
                },
            )
            return (jsonify(result=resp_dict), 200)
        

        # backup_jobs_json = str(backup_jobs_json).replace("{{DRIVE}}", ":")
        # return 200  # jsonify(result=rr)
        except Exception as e:

            # 500 = restore failed (body has reason). Frontend must show result[0].reason or result.reason, not generic "Request failed with status code 500".
            return (jsonify(result=[{"restore": "failed", "reason": str(e)}]), 500)

        # return 200

        # return 200
    if selectedAction == "fetch" or selectedAction == "fetchAll":
        from sqlalchemy.orm import sessionmaker   
        from module2 import create_database
        create_database(str(app.config.get("getCode",None))+".db")
        engine = create_engine("sqlite:///" + str(app.config.get("getCode",None))+".db")
        restore_session = sessionmaker(bind=engine)()
        update_filebackup_counts(0,obj)

        if str(selectedStorageType).lower().replace(" ", "") in [
            "local",
            "localstorage",
        ]:
            selectedStorageType = "local','local storage','LAN','On-Premise'"

        if str(selectedStorageType).lower().replace(" ", "") in [
            "on-premise",
            "onpremise",
        ]:
            selectedStorageType = "LAN','On-Premise','local','local storage'"

        if str(selectedStorageType).lower().replace(" ", "") in [
            "gdrive",
            "googledrive",
        ]:
            selectedStorageType = "GDRIVE','Google Drive"
        agent_candidates = [value for value in {requested_agent, selectedAgent} if value]
        if selectedAction == "fetchAll":
            selectedStorageType = "local','local storage','LAN','On-Premise','GDRIVE','Google Drive','UNC','AWSS3','AZURE','ONEDRIVE" #','NAS"

        agent_filter_clause = ""
        if agent_candidates:
            agent_filter_clause = " and (from_computer in ('" + "', '".join(agent_candidates) + "'))"

        # selectedAgent =  "DESKTOP-SUCRQP8"
        # startDate =  "31/12/2023, 11:59:59 pm"
        # endDate =    "31/12/2030, 11:59:59 pm"

        date_format = "%d/%m/%Y, %I:%M:%S %p"

        import pytz

        p = pytz.timezone("Asia/Kolkata")

        startDate = datetime.datetime.strptime(startDate, date_format)
        startDate = p.localize(startDate)
        startDate = startDate.timestamp() * 1000
                    
        endDate = datetime.datetime.strptime(endDate, date_format)
        endDate = p.localize(endDate)
        endDate = endDate.timestamp() * 1000

        now = time.time()
        # var = BackupLogs()
        # engine = create_engine(f"sqlite:///{obj}.db",echo=True)
        # xession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        # session = xession()
        # backup_job_master = (
        #     session.query(BackupMain)
        #     .filter(
        #         BackupMain.id * 1000 >= startDate,
        #         BackupMain.id * 1000 <= endDate,
        #     )
        #     .filter(BackupMain.data_repo == selectedStorageType)
        #     .filter(BackupMain.from_computer == selectedAgent)
        #     .all()
        # )

        # # backup_jobs = session.query(BackupLogs).all()
        # # selected_fieldg = ["file_name"]

        # # backup_jobs_xg = (
        # #     session.query(BackupLogs.from_computer, BackupLogs.from_path)
        # #     .group_by(BackupLogs.from_computer, BackupLogs.from_path)
        # #     .filter_by(BackupLogs.date_time >= startDate, BackupLogs.date_time <= endDate)
        # #     .all()
        # # )
        # # backup_jobs_GP = (
        # #     session.query(BackupLogs)
        # #     .group_by(BackupLogs.from_computer, BackupLogs.from_path)
        # #     .all()
        # # )
        # session.close()
        batch_size = 1000
        backup_jobs_json = []
        s_manager = SQLiteManager()
        dbname = os.path.join(app.config["location"], obj)
        restore_query = (
            "SELECT backups_M.id,date_time,from_computer,from_path,"
            + " data_repo,mime_type,file_name,size,pNameText,"
            + " pIdText,bkupType,((sum_done*100)/sum_all) as wdone FROM backups_M where "
            + " ((id * 1000 >= "
            + str(startDate)
            + ") and (id * 1000 <= "
            + str(endDate)
            + "))"
            + " and (data_repo in('"
            + selectedStorageType
            + "'))"
            + agent_filter_clause
            + " order by date_time desc"
        )
        # Try multiple path variants: DBs may have no extension or .db/.sqlite/.sqlite3/.db3
        # and may be keyed by computer_id (obj) or by agent name (selectedAgent)
        location_dir = app.config.get("location") or ""
        db_extensions = ("", ".db", ".sqlite", ".sqlite3", ".db3")
        candidate_paths = []
        for base_name in (obj, selectedAgent, requested_agent):
            if not base_name:
                continue
            for ext in db_extensions:
                p = os.path.join(location_dir, base_name + ext)
                if p not in candidate_paths:
                    candidate_paths.append(p)
        for base_name in (obj, selectedAgent):
            if not base_name:
                continue
            for ext in db_extensions:
                p = os.path.join(os.getcwd(), base_name + ext)
                if p not in candidate_paths:
                    candidate_paths.append(p)
        # If no explicit paths yet, ensure dbname (location/obj) is tried
        if dbname not in candidate_paths:
            candidate_paths.insert(0, dbname)
        results = {}
        all_records = []  # aggregate from all candidate DBs when fetchAll so no backup is missed
        seen_ids = set()
        for candidate in candidate_paths:
            if not os.path.isfile(candidate):
                continue
            qrs = [(candidate, [restore_query])]
            try:
                try_results = s_manager.execute_queries(qrs)
            except Exception:
                continue
            if candidate in try_results and len(try_results[candidate]) > 0:
                status, records = try_results[candidate][0]
                if status == "Success" and records:
                    if selectedAction == "fetchAll":
                        for row in records:
                            row_id = dict(row).get("id")
                            if row_id is not None and row_id not in seen_ids:
                                seen_ids.add(row_id)
                                all_records.append(row)
                    else:
                        results = {dbname: [(status, records)]}
                        break
        if selectedAction == "fetchAll" and os.path.isdir(location_dir):
            # Fallback: list directory and try any file that looks like agent/obj (any extension)
            try:
                for fname in os.listdir(location_dir):
                    base, ext = os.path.splitext(fname)
                    if base not in (obj, selectedAgent, requested_agent):
                        continue
                    candidate = os.path.join(location_dir, fname)
                    if not os.path.isfile(candidate):
                        continue
                    if candidate in candidate_paths:
                        continue
                    qrs = [(candidate, [restore_query])]
                    try_results = s_manager.execute_queries(qrs)
                    if candidate in try_results and len(try_results[candidate]) > 0:
                        status, records = try_results[candidate][0]
                        if status == "Success" and records:
                            for row in records:
                                row_id = dict(row).get("id")
                                if row_id is not None and row_id not in seen_ids:
                                    seen_ids.add(row_id)
                                    all_records.append(row)
            except Exception:
                pass
        if selectedAction == "fetchAll" and all_records:
            results = {dbname: [("Success", all_records)]}
        if not results and os.path.isdir(location_dir):
            # Fallback when not fetchAll: list directory and try any file that looks like agent/obj
            try:
                for fname in os.listdir(location_dir):
                    base, ext = os.path.splitext(fname)
                    if base not in (obj, selectedAgent, requested_agent):
                        continue
                    candidate = os.path.join(location_dir, fname)
                    if not os.path.isfile(candidate):
                        continue
                    qrs = [(candidate, [restore_query])]
                    try_results = s_manager.execute_queries(qrs)
                    if candidate in try_results and len(try_results[candidate]) > 0:
                        status, records = try_results[candidate][0]
                        if status == "Success" and records:
                            results = {dbname: [(status, records)]}
                            break
            except Exception:
                pass
        if not results:
            results = s_manager.execute_queries([(dbname, [restore_query])])

        for db_path, db_results in results.items():
            print(f"Results for {db_path}:")
            for i, (result, records) in enumerate(db_results):
                print(f"  Query {i+1}: {result}")
                if result == "Success":
                    if records is not None:
                        backup_job_master = records
                        # backup_job_master_dict = [dict(row) for row in records]
                        # backup_job_master_row_wrapper = [
                        #     RowWrapper(record) for record in records
                        # ]
                        print(f"    Records: {records}")
                        for job in records:
                            job_dict = {
                                "id": dict(job)["id"],
                                "name": (
                                    dict(job)["pNameText"]
                                    + " ("
                                    + dict(job)["file_name"]
                                    + ")"
                                    if dict(job)["file_name"]
                                    else dict(job)["pNameText"]
                                ),
                                "last_modified": dict(job)["date_time"],
                                "last_modified": time.strftime(
                                    date_format, time.localtime(dict(job)["date_time"])
                                ),
                                "from_computer": dict(job)["from_computer"],
                                "location": str(
                                    str(dict(job)["from_path"]).replace(
                                        "{{DRIVE}}", ":"
                                    )
                                ).replace(obj + "\\", ""),
                                "target_location": str(
                                    str(dict(job)["from_path"]).replace(
                                        "{{DRIVE}}", ":"
                                    )
                                ).replace(obj + "\\", ""),
                                "data_repo": dict(job)["data_repo"],
                                "type": dict(job)["mime_type"],
                                "size": dict(job)["size"],
                                "wdone": dict(job)["wdone"],
                                
                            }

                            x= restore_session.query(restore_parent).filter_by(backup_id=dict(job)["id"])
                            job_dict.update({"restore_logs":[restore_parent.to_dict(fx,True,restore_session) for fx in x]})
                            backup_jobs_json.append(job_dict)

        # for job in backup_jobs:
        #     job_dict = {
        #         # column.name: getattr(job, column.name) for column in job.__table__.columns
        #         "Id": getattr(job, "id"),
        #         "name": getattr(job, "name"),
        #         "date_time": getattr(job, "date_time"),
        #         "from_computer": getattr(job, "from_computer"),
        #         "from_path": str(
        #             str(getattr(job, "from_path")).replace("{{DRIVE}}", ":")
        #         ).replace(obj + "\\", ""),
        #         "data_repo": getattr(job, "data_repo"),
        #         "file_name": json.loads(job.log)["file_name"],
        #         "file_time": json.loads(job.log)["file_time"],
        #         "path": json.loads(job.log)["path"],
        #     }
        #     backup_jobs_json.append(job_dict)
        # the following code has been commented and useful when sqlachemy is used
        # for job in backup_job_master:
        #     job_dict = {
        #         # column.name: getattr(job, column.name) for column in job.__table__.columns
        #         "id": getattr(job, "id"),
        #         # "name": str(
        #         #     str(
        #         #         os.path.join(
        #         #             getattr(job, "pNameText"), getattr(job, "pNameText")
        #         #         )
        #         #     ).replace("{{DRIVE}}", ":")
        #         # ).replace(obj + "\\", ""),
        #         # "name": str(getattr(job, "pNameText")) + f' ({str(getattr(job, "file_name"))})' ,
        #         "name": (
        #             getattr(job, "pNameText") + " (" + getattr(job, "file_name") + ")"
        #             if getattr(job, "file_name")
        #             else getattr(job, "pNameText")
        #         ),  # str(getattr(job, "pNameText")) + f' ({str(getattr(job, "file_name"))})' ,
        #         "last_modified": getattr(job, "date_time"),
        #         "last_modified": time.strftime(
        #             date_format, time.localtime(getattr(job, "date_time"))
        #         ),
        #         "from_computer": getattr(job, "from_computer"),
        #         "location": str(
        #             str(getattr(job, "from_path")).replace("{{DRIVE}}", ":")
        #         ).replace(obj + "\\", ""),
        #         "target_location": str(
        #             str(getattr(job, "from_path")).replace("{{DRIVE}}", ":")
        #         ).replace(obj + "\\", ""),
        #         "data_repo": getattr(job, "data_repo"),
        #         "type": getattr(job, "mime_type"),
        #         "size": getattr(job, "size"),
        #         # "file_name": json.loads(job.log)["file_name"],
        #         # "file_time": json.loads(job.log)["file_time"],
        #         # "path": json.loads(job.log)["path"],
        #     }
        #     backup_jobs_json.append(job_dict)

    return (jsonify(backup_jobs_json), 200)


################################################33
# import asyncio
# import httpx
# async def fetch_headers_async(host, timeout=5):
#     """
#     Async HTTP GET to retrieve headers from client.
#     Returns tuple: (XRefServer, XServer, XIDX) or (None, None, None) if offline.
#     """
#     XRefServer = XServer = XIDX = None
#     url = f"{host}/"
#     try:
#         async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, read=timeout)) as client:
#             response = await client.get(url)
#             if response.status_code == 200:
#                 XRefServer = response.headers.get('XRefServer')
#                 XServer = response.headers.get('XServer')
#                 XIDX = response.headers.get('XIDX')
#     except (httpx.RequestError, httpx.ConnectTimeout, httpx.ReadTimeout):
#         return False
#     return XRefServer, XServer, XIDX


import httpx

timeout = httpx.Timeout(5.0)

async def fetch_headers_async(host):
    url = f"{host}/"
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        ) as client:
            r = await client.head(url)
            if r.status_code != 200:
                return None, None, None

            h = r.headers
            return (
                h.get("XRefServer"),
                h.get("XServer"),
                h.get("XIDX"),
            )

    except httpx.HTTPError:
        return None, None, None

import asyncio
import threading

loop = asyncio.new_event_loop()

def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_loop, daemon=True).start()

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, loop).result()

def is_less_than_2_minutes(timestamp,data_dict=None):
    from datetime import datetime, timedelta

    # current_time = datetime.now()
    # epoch_time = datetime.fromtimestamp(float(timestamp))
    # return (current_time - epoch_time).seconds < 80

    XRefServer =""
    XServer = ""
    XIDX = ""
    try:
        # Use a service like 'httpbin.org' to get your public IP address
        current_ip =get_current_ip()
        try:
            if is_client_online(timestamp, timeout=5):
                # response = requests.get(str(timestamp)+"/",timeout=(5,5))
                XRefServer, XServer, XIDX = run_async(fetch_headers_async(str(timestamp)))
                # if response.status_code == 200:
                #     XRefServer =response.headers.get('XRefServer', None)
                #     XServer = response.headers.get('XServer', None)
                #     XIDX = response.headers.get('XIDX', None)
                # else:
                #     print("Failed to retrieve public IP. Status code:", response.status_code)
                #     return False
                
            else: 
                return False
        
        except Exception as e:
            sid = app.config["WSClients"].get(clientnodes_x[str(timestamp).replace("7777/","7777")].get("key"),None)
            if not sid:
                return (
                    jsonify(
                        {"allowed_hosts": ["*"],"current_host": "None","running": False,}),200,
                    )
            request_id = str(uuid.uuid4())
            event = threading.Event()
            result_holder = {}

            app.config["pending_requests"][request_id] = (event, result_holder)

            sktio.emit('scheduler_response', {
                "key": clientnodes_x[str(timestamp).replace("7777/","7777")].get("key"),
                "request_id": request_id
            }, to=sid)

            if event.wait(timeout=300):
                data = result_holder.get("scheduler_response", {})
                combined_response=data.get("combined_response",{
                    "allowed_hosts": ["*"],
                    "current_host": "None",
                    "running": False,
                })
                XRefServer =data.get('XRefServer', None)
                XServer = data.get('XServer', None)
                XIDX = data.get('XIDX', None)
            else:
                print(f"[Fallback Timeout] No response for request_id: {request_id}")

        b1 = False
        b2 = False
        try:
            b1 = XIDX in app.config["agent_activation_keys"]
        except:
            return False

        try:
            b2 = str(current_ip) == str(XServer)
            # b2=True
        except:
            return False

        return b1 and b2

    except Exception as e:
        print("An error occurred:", e)
        return False

##kartik
@app.route("/refreshclientnodes", methods=["GET"])
def refresh_client_nodes():
    print("*"*5)
    sktio.emit("show_me", {"show_me": "s_starting"})
    print("*"*5)
    return jsonify({"status": "success"}),200
##kartik

@app.route("/clientnodes", methods=["GET"])
# @auth_required
def client_nodes():
    session_id = request.cookies.get("session_id")
    """Renders the contact page."""

    if not clientnodes_x:
        clientnodes_x.update(load_clientnodes_x())
        update_clientnodes_list(clientnodes_x, clientnodes, clientnodes2x)

    # data = []
    # bNotFound = True
    # for condition in clientnodes:
    #     bNotFound = True
    #     for item in clientnodes2x:
    #         new_item = item.copy()
    #         if (
    #             item["ipAddress"] == condition["ipAddress"]
    #             and item["agent"] == condition["agent"]
    #         ):
    #             bNotFound = False
    #             new_item["lastConnected"] = str(
    #                 is_less_than_2_minutes(item["ipAddress"])
    #             )
    #             data.append(new_item)
    #     if bNotFound:
    #         data.append(
    #             {
    #                 "ipAddress": condition["ipAddress"],
    #                 "agent": condition["agent"],
    #                 "lastConnected": False,
    #             }
    #         )

    # # data = clientnodes2x
    # return jsonify(result=data)
    # data = []

    # for condition in clientnodes:
    #     match = next(
    #         (item for item in clientnodes2x if item["ipAddress"] == condition["ipAddress"] and item["agent"] == condition["agent"]),
    #         None,
    #     )
    #     if match:
    #         new_item = match.copy()
    #         new_item["lastConnected"] = str(is_less_than_2_minutes(str(match["ipAddress"])))
    #         data.append(new_item)
    #     else:
    #         data.append(
    #             {
    #                 "ipAddress": condition["ipAddress"],
    #                 "agent": condition["agent"],
    #                 "lastConnected": False,
    #                 "lastConnectedTime": condition["lastConnectedTime"],
    #                 "ip": condition["ip"],
    #                 "data": condition["data"],
    #             }
    #         )

    from concurrent.futures import ThreadPoolExecutor

    lookup = {
        (item["ipAddress"], item["agent"]): item
        for item in clientnodes2x
    }

    def process_condition(condition):
        match = lookup.get((condition["ipAddress"], condition["agent"]))

        if match:
            new_item = match.copy()
            new_item["lastConnected"] = str(
                is_less_than_2_minutes(str(match["ipAddress"]))
            )
            return new_item
        else:
            return {
                "ipAddress": condition["ipAddress"],
                "agent": condition["agent"],
                "lastConnected": False,
                "lastConnectedTime": condition["lastConnectedTime"],
                "ip": condition["ip"],
                "data": condition["data"],
            }

    with ThreadPoolExecutor(max_workers=8) as executor:
        data = list(executor.map(process_condition, clientnodes))

    return jsonify(result=data)


# @app.route("/about")
# def about():
#     """Renders the about page."""
#     return render_template(
#         "about.html",
#         title="About",
#         year=datetime.now(),  # .year,
#         message="Welcome to the Apna Backup.",
#     )


def send_email_via_mailgun(domain, api_key, to, subject, text):
    """
    Send an email using Mailgun's API.

    :param domain: Your Mailgun domain.
    :param api_key: Your Mailgun API key.
    :param to: Recipient's email address.
    :param subject: Subject of the email.
    :param text: Body of the email.
    """
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    data = {
        "from": f"Mailgun Sandbox <postmaster@{domain}>",
        "to": to,
        "subject": subject,
        "text": text,
    }

    response = requests.post(url, auth=auth, data=data, timeout=20)
    return response


@app.route("/sendemail")
def send_simple_message():
    # x= requests.post("https://api.mailgun.net/v3/sandboxb2ead55490704fa58e3ec813bb730ade.mailgun.org/messages", auth=("api", "7dab52a39a97c88bd07e568dd29423fc-7ecaf6b5-c5294d72"),		data={"from": "Excited User <mailgun@sandboxb2ead55490704fa58e3ec813bb730ade.mailgun.org>","to": ["kuldeepraaj@gmail.com","YOU@sandboxb2ead55490704fa58e3ec813bb730ade.mailgun.org"],"subject": "Hello","text": "Testing some Mailgun awesomeness!"})

    # return requests.post(
    # "https://api.mailgun.net/v3/sandboxb2ead55490704fa58e3ec813bb730ade.mailgun.org/messages",
    # auth=("api", "7dab52a39a97c88bd07e568dd29423fc-7ecaf6b5-c5294d72"),
    # data={"from": "Excited User <mailgun@sandboxb2ead55490704fa58e3ec813bb730ade.mailgun.org>",
    # "to": ["kuldeepraaj@gmail.com", "YOU@sandboxb2ead55490704fa58e3ec813bb730ade.mailgun.org"],
    # "subject": "Hello",
    # "text": "Testing some Mailgun awesomeness!"})
    domain = "sandboxb2ead55490704fa58e3ec813bb730ade.mailgun.org"  # Replace with your Mailgun domain
    api_key = "ac1af75f67e92b82f63f38e3729e1a64-78f6ccbe-a47b770b"  # Replace with your Mailgun API key
    to_email = "kuldeepraaj@gmail.com"
    subject = "Your query on 3Handshake Innovations.at "
    text = "Your query on 3Handshake Innovations has been received our team will contact you soon."

    response = send_email_via_mailgun(domain, api_key, to_email, subject, text)
    # print("Status: ", response.status_code)
    # print("Body: ", response.text)
    return "Done", 200


########################################################
@app.route("/get_restore_data")
def readdata():
    import json

    # Load the JSON data from the file
    if request.method == "POST":
        repository = (request.json)["repository"]
        agent = (request.json)["agent"]
        date_start = (request.json)["date_start"]
        date_end = (request.json)["date_end"]

    with open(CLIENT_BACKUPS_DATA_FILE, "r") as file:
        data = json.load(file)
    all_items = data

    # Example 2: Retrieve items where a certain condition is met
    filtered_items1 = [
        item
        for item in data
        if item["file_name"] == "40e336af-9996-482f-8fca-ba19d029427e.jpg"
    ]

    # Example 3: Retrieve items based on multiple conditions
    filtered_items2 = [
        item
        for item in data
        if item["file_name"] == "cctv camera.png" and item["file_time"] > 1714728268
    ]

    print("")


def calculate_file_digest(file_path, hash_algorithm="sha512", chunk_size=8192):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        hash_function = hashlib.new(hash_algorithm)
        total_size = os.path.getsize(file_path)
        processed_size = 0

        with open(file_path, "rb") as file:
            while chunk := file.read(chunk_size):
                hash_function.update(chunk)
                processed_size += len(chunk)

                # Send progress updates to connected clients
                # sktio.emit(
                #     "progress_update",
                #     {"percentage": (processed_size / total_size) * 100},
                # )

        return hash_function.hexdigest()
    except Exception as e:
        return str(e)


def calculate_file_digest_threaded(file_path, hash_algorithm="md5", chunk_size=8192):
    # Run the calculation in a separate thread
    def run_calculation():
        try:
            result = calculate_file_digest(file_path, hash_algorithm, chunk_size)
            # sktio.emit("calculation_complete", {"result": result})
        except Exception as e:
            print(e)
            # sktio.emit("calculation_error", {"error": str(e)})

    # thread = threading.Thread(target=run_calculation)
    # thread.start()


def get_file_metadata(file_path):
    try:
        stat_info = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        file_name = os.path.basename(file_path)
        # digest_value = calculate_file_digest(file_path)

        metadata = {
            "id": file_path,
            "path": file_path,
            "name": file_name,
            "type": "file" if os.path.isfile(file_path) else "directory",
            "size": stat_info.st_size,
            "last_modified": datetime.datetime.fromtimestamp(
                stat_info.st_mtime
            ).isoformat(),
            "mimetype": mime_type,
            # "dgid": digest_value,
        }
        return metadata
    except Exception as e:
        return str(e)


@sktio.on("connect")
def handle_connect():
    print(request.headers)
    # try:
    #     headers = request.hea
    # views.clientnodes_x[obj_ip].get("key")
    if request.headers.get("WSTD",None):
        if request.event.get('args',None):
            key=request.event['args'][1].get("key",None)
            if key:
                if not app.config.get("WSClients",None):
                    from flask import Config
                    app.config["WSClients"]={}
                app.config["WSClients"].update({key:request.sid})
                #sktio.emit("backupprofilescreate", {"backupprofilescreate": "s_starting"})#,to=request.sid)  
                #sktio.emit("show_me", {"show_me": "s_starting"})#,to=request.sid)
                return
                    
    tellme()
    print("Client connected")
    #emit("data", broadcast=False)
    #sktio.emit("show_me", {"show_me": "s_starting"},to=request.sid)  

@sktio.on('browse_response')
def handle_browse_response(data):
    request_id = data.get("request_id")
    if request_id in app.config["pending_requests"]:
        event, result_holder = app.config["pending_requests"][request_id]
        result_holder['browse_response'] = data
        event.set()

@sktio.on('scheduler_response')
def handle_scheduler_response(data):
    request_id = data.get("request_id")
    if request_id in app.config["pending_requests"]:
        event, result_holder = app.config["pending_requests"][request_id]
        result_holder['scheduler_response'] = data
        event.set()

@sktio.on('scheduler_action_reschedule_response')
def handle_scheduler_action_reschedule_response(data):
    request_id = data.get("request_id")
    if request_id in app.config["pending_requests"]:
        event, result_holder = app.config["pending_requests"][request_id]
        result_holder['scheduler_action_reschedule_response'] = data
        event.set()

@sktio.on('scheduler_action_response')
def handle_scheduler_action_response(data):
    request_id = data.get("request_id")
    if request_id in app.config["pending_requests"]:
        event, result_holder = app.config["pending_requests"][request_id]
        result_holder['scheduler_action_response'] = data
        event.set()

@sktio.on('backupprofilescreate_response')
def handle_backupprofilescreate_response(data):
    request_id = data.get("request_id")
    if request_id in app.config["pending_requests"]:
        event, result_holder = app.config["pending_requests"][request_id]
        result_holder['backupprofilescreate_response'] = data
        event.set()


@sktio.on("message")
def handle_message(message):
    #emit(" i have received your message " + str(message), broadcast=True)
    ##js[""]{"action":"play","agent":"DESKTOP-SUCRQP8"}
    try:
        js = message
        try:
            js = json.loads(message)
        except:
            print("")
        agent = js.get("agent")
        action = js.get("action")
        obj = search_client_nodes(agent)
        selectedAgentIPAddress = obj.get("ipAddress")
        selectedAgentName = obj.get("agent")
        if str(action).lower() == "play":
            action = "resume"
        c = clientnodes_x[obj.get("ipAddress")].get("key")
        x = requests.post(
            f"{selectedAgentIPAddress}/admin/job",
            json={"action": action},
            timeout=200,
        )
        print(str(x.content))
        if str(action).lower() == "play" or str(action).lower() == "resume":
            action = "pause"
        elif str(action).lower() == "pause":
            action = "play"
        sktio.emit("message", {"action": str(action), "agent": str(agent)})
        # sktio.emit("message",message)
    except:
        print("")


@sktio.on("backup_data")
def handle_backup_data(s_backup_data):
    # emit(" i have received your message " + str(message , broadcast=True))
    try:
        if isinstance(s_backup_data, str):
            s_backup_data = json.loads(s_backup_data)
        print(str(s_backup_data))
        s_backup_data = s_backup_data.get("backup_jobs")
        # if message:
        #     message = message.get("backup_jobs")
        if s_backup_data:
            sktio.emit("backup_data", {"backup_jobs": s_backup_data[0]})
            print("==========================   " + str(s_backup_data[0]))
    except Exception as dd:
        print(str(dd))

@sktio.on("connect",namespace="/starting")
def handle_starting_connect(s_starting):
    print("connected")
@sktio.on("connect",namespace="/socket.io")
def handle_starting_connects(s_starting):
    print("connected")

@sktio.on("starting")
def handle_starting_data(s_starting):
    # emit(" i have received your message " + str(message , broadcast=True))
    try:
        if isinstance(s_starting, str):
            s_starting = json.loads(s_starting)
        print(str(s_starting))
        s_starting = s_starting.get("backup_jobs")
        # if message:
        #     message = message.get("backup_jobs")
        if s_starting:
            sktio.emit("starting", {"backup_jobs": s_starting[0]})
            print("==========================   " + str(s_starting[0]))
    except Exception as dd:
        print(str(dd))

@sktio.on("show_me")
def handle_showme_data(s_starting):
    # emit(" i have received your message " + str(message , broadcast=True))
    try:
        if isinstance(s_starting, str):
            s_starting = json.loads(s_starting)
        print(str(s_starting))
        #s_starting = s_starting.get("show_me")
        # if message:
        #     message = message.get("show_me")
        if s_starting:
            #tellme()
            # sktio.emit("show_me", {"show_me": s_starting},to=request.sid)   ##kartik  
            print("==========================   " + str(s_starting))
            return "asdfasdfasdf"
    except Exception as dd:
        print(str(dd))

@sktio.on("restore_data")
def handle_restore_data(s_restore):
    try:
        if isinstance(s_restore, str):
            s_restore = json.loads(s_restore)
        print(str(s_restore))
        s_restore = s_restore.get("restore_jobs")
        if s_restore:
            sktio.emit("restore_data", {"restore_jobs": s_restore[0]})
            print("==========================   " + str(s_restore[0]))
    except Exception as dd:
        print(str(dd))


# @sktio.on("ping")
# def handle_ping():
#     print("Received ping from client")
#     emit("pong")


# @sktio.on("pong")
# def handle_pong():
#     print("Received pong from client")
#     emit("ping")


@sktio.on("/mes")
def handle_mes(message):
    sktio.emit("message",{"message":message})
    send("I have received your mes  " + message)

@app.route("/socket.io/")
@sktio.on("/socket.io")
@sktio.on("/socket.io/")
@sktio.on("socket.io")
@sktio.on("socketio")
@sktio.on("socket")
def handle_socketio(message):
    send("I have received your mes  " + message)

    

@app.route("/api/browseUNC", methods=["POST"])
def browseUNC():
    import requests
    # UNC logging - import from parent FlaskWebProject3 folder (same level as lans.py)
    try:
        from unc_logger import log_browse_unc_request, log_error, log_info
        has_unc_logger = True
    except ImportError:
        has_unc_logger = False
        def log_browse_unc_request(*args, **kwargs): pass
        def log_error(*args, **kwargs): pass
        def log_info(*args, **kwargs): pass

    ip = ""
    try:
        rdata = request.json
        current_path = rdata.get("path", "")
        client_node_browse = rdata.get("node", "")
        userid = rdata.get("noidadd", "")
        password = rdata.get("noidacc", "")
        domain = rdata.get("noidman", "")
        method = rdata.get("method", ".")
        donl = rdata.get("donl", True)
        level = rdata.get("level", 4)
        from lans import NetworkShare
        from lans import NetworkScanner

        if current_path == "" and method == ".":
            method = "."
        if current_path == "" and method == "browse":
            method = "shares"
        if method == "":
            method = "."

        # Log incoming browseUNC request with masked credentials
        client_ip = request.remote_addr if request else None
        log_browse_unc_request(client_node_browse, current_path, method, client_ip)

        if (client_node_browse) == "" or (userid) == "" or (password) == "":
            log_error("browseUNC", "Invalid host/credentials", context="missing_params")
            return (jsonify({"messsage": "invalid host/credentials"}), 200)
        
        conn = NetworkShare(client_node_browse, current_path, userid, password)
        if not conn:
            conn = SMBConnection("admin","Server123","","192.168.2.15",use_ntlm_v2=True,is_direct_tcp=True)
        
        if rdata:
            if method == ".":
                try:
                    conn = NetworkScanner()
                    data = conn.run()
                    log_info(f"BROWSE_UNC_SCAN | nodes_found={len(data)}")
                    return (jsonify(nodes=data), 200)
                except Exception as eas:
                    log_error("browseUNC_scan", eas)
                    return (jsonify({"messsage": str(eas)}), 500)

            if method == "trace":
                try:
                    conn = NetworkShare(client_node_browse, "", userid, password)
                    if conn.test_connection():
                        log_info(f"BROWSE_UNC_TRACE | host={client_node_browse} | result=success")
                        return (jsonify({"messsage": "Connection successfull"}), 200)
                    else:
                        log_info(f"BROWSE_UNC_TRACE | host={client_node_browse} | result=failed")
                        return (jsonify({"messsage": "Connection failed"}), 200)
                except Exception as eas:
                    log_error("browseUNC_trace", eas, context=client_node_browse)
                    return (jsonify({"messsage": str(eas)}), 500)

            if method == "browse":
                try:
                    if conn.connect():
                        json = conn.create_file_paths_json(
                            "file_paths.json", donl, level
                        )
                        conn.disconnect()
                        return (json, 200)
                    else:
                        log_error("browseUNC_browse", "Connection failed", context=client_node_browse)
                        return (jsonify({"messsage": "Connection failed"}), 200)
                except Exception as eas:
                    log_error("browseUNC_browse", eas, context=client_node_browse)
                    return (jsonify({"messsage": str(eas)}), 500)
                finally:
                    conn.disconnect

            if method == "shares":
                try:
                    if conn.connect():
                        json = conn.get_shared_list()
                        conn.disconnect()
                        return (json, 200)
                    else:
                        log_error("browseUNC_shares", "Connection failed", context=client_node_browse)
                        return (jsonify({"messsage": "Connection failed"}), 200)
                except Exception as eas:
                    log_error("browseUNC_shares", eas, context=client_node_browse)
                    return (jsonify({"messsage": str(eas)}), 500)
                finally:
                    conn.disconnect

    except Exception as exs:
        log_error("browseUNC", exs, context="unhandled_exception")
    return (rdata, 500)


# @app.route("/api/browse", methods=["POST"])
# def browseNode():

#     import requests

#     ip = ""
#     try:

#         rdata = request.json

#         current_path = rdata.get("path", os.getcwd())
#         client_node_browse = rdata.get("node", "")

#         if rdata:
#             if rdata.get("node",None):
#                 try:
#                     ip = search_client_nodes(rdata["node"])["ipAddress"]
#                     url = str(f"d{ip}/api/browse")
#                     print(rdata["node"])
#                     tstart = time()
#                     response = requests.post(
#                         url,
#                         json={"path": current_path},
#                         headers={"Accept-Encoding": "application/gzip"},
#                         timeout=20,
#                     )
#                     print(f"time taken {time()-tstart}")
#                     # response = requests.post(url
#                     #                          ,data= gzip.compress( {'path':current_path},9)
#                     #                          ,headers={
#                     #                             'Accept-Encoding': 'gzip'
#                     #                              })
#                     if response.status_code == 200:
#                         return (response.content, 200)
#                 except Exception as eas:
#                     print(str(eas))
#                     sid = app.config["WSClients"].get(clientnodes_x[ip].get("key"),None)
#                     if not sid:
#                         return (
#                             jsonify(
#                                 {"allowed_hosts": ["*"],"current_host": "None","running": False,}),200,
#                             )
#                     request_id = str(uuid.uuid4())
#                     event = threading.Event()
#                     result_holder = {}

#                     app.config["pending_requests"][request_id] = (event, result_holder)

#                     sktio.emit('browse_response', {
#                         "key": clientnodes_x[ip].get("key"),
#                         "request_id": request_id,
#                         "path": current_path
#                     }, to=sid)

#                     if event.wait(timeout=300):
#                         data = result_holder.get("browse_response", {})
#                         combined_response=data.get("combined_response",None)
#                     else:
#                         print(f"[Fallback Timeout] No response for request_id: {request_id}")
#                         return ({"error": "invalid ws timed out request"}, 500)

#                     return (combined_response, 200)

#     except Exception as exs:
#         print(str(exs))
#     return ({"error": "invalid request"}, 500)


@app.route("/api/browse", methods=["POST"])
def browseNode():
    rdata = request.json

    current_path = rdata.get("path", os.getcwd())
    ip = search_client_nodes(rdata["node"])["ipAddress"]
    sid = app.config["WSClients"].get(clientnodes_x[ip].get("key"),None)
    if not sid:
        return (
            jsonify(
                {"allowed_hosts": ["*"],"current_host": "None","running": False,}),200,
            )
    request_id = str(uuid.uuid4())
    event = threading.Event()
    result_holder = {}

    app.config["pending_requests"][request_id] = (event, result_holder)

    sktio.emit('browse_response', {
        "key": clientnodes_x[ip].get("key"),
        "request_id": request_id,
        "path": current_path
    }, to=sid)

    if event.wait(timeout=300):
        data = result_holder.get("browse_response", {})
        combined_response=data.get("combined_response",None)
    else:
        print(f"[Fallback Timeout] No response for request_id: {request_id}")
        return ({"error": "invalid ws timed out request"}, 500)

    return (combined_response, 200)


def browse():
    folders = []
    current_path = request.json.get("path", os.getcwd())
    if current_path == NULL or current_path == "" or current_path == "HOME":
        drive_info = []

        partitions = psutil.disk_partitions(all=True)
        for partition in partitions:
            if (not partition.opts.__contains__("cdrom")) and (
                not partition.opts.__contains__("removable") > 0
            ):
                current_path = partition.mountpoint
                du = psutil.disk_usage(current_path)
                contents = []
                folders.append({"path": current_path, "contents": contents})
        return jsonify(paths=folders)
    else:
        contents = [
            get_file_metadata(os.path.join(current_path, item))
            for item in os.listdir(current_path)
        ]
        response_data = {"path": current_path, "contents": contents}
        folders.append(response_data)
        return jsonify(paths=folders)

def _ensure_clientnodes_loaded():
    if not clientnodes_x:
        clientnodes_x.update(load_clientnodes_x())
        update_clientnodes_list(clientnodes_x, clientnodes, clientnodes2x)
 
 
def _normalize_ip_url(value):
    value = str(value or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    # already has host:port (e.g. 10.109.164.78:7777) – add scheme only
    if ":" in value:
        parts = value.rsplit(":", 1)
        if len(parts) == 2 and parts[1].isdigit():
            return f"http://{value}"
    # raw IP (no port), add scheme and default port
    if value.count(".") == 3:
        return f"http://{value}:7777"
    return value
    
@app.route("/api/open-file", methods=["POST"])
def open_file():
    file_path = request.json.get("path")

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        abort(404, f"File not found: {file_path}")

    return get_file_content(file_path)


@app.route("/api/go-up", methods=["POST"])
def go_up():
    current_path = request.json.get("path", os.getcwd())
    parent_data = get_parent_directory(current_path)

    return jsonify(parent_data)


@app.route("/api/calculatehash", methods=["POST"])
def calculate_hash():
    file_path = request.json.get("file_path")
    calculate_file_digest_threaded(file_path)
    return jsonify({"message": "Calculation started. Check for progress updates."})

@app.route("/api/getclients", methods=["GET","POST"])
def get_top10_jobs():
    endpoints =[] 
    try:
        for e in app.config["agent_activation_keys"]:
            x= search_clientnodes_x_nodes(e)
            if x:
                # flag=is_less_than_2_minutes(float(x['lastConnected']))
                from datetime import datetime, timedelta
                current_time = datetime.now()
                epoch_time = datetime.fromtimestamp(float(x['lastConnected']))
                flag =(current_time - epoch_time).seconds > 120
                endpoints.append({"idx":x["key"],"agent":x["agent"],"ipAddress":x["ipAddress"],"lastConnected":str(flag)})
            # else:
            #     endpoints.append({"idx":e,"agent":e["agent"],"ipAddress":e,"lastConnected":str(True)})
        

        #return (jsonify({"agents":json.loads(endpoints)}),200)
        return (jsonify({"result":endpoints}),200)
    except:
        #m.close()
        return (jsonify({"result":endpoints}),500)
 

@app.route('/restore_nodes', methods=['GET'])
def restore_nodes():
    from .jobdata import JobsRecordManager
    _ensure_clientnodes_loaded()
 
    m = JobsRecordManager("records.db", "records.json", app=app)
    endpoints = []
    try:
        endp = m.fetch_nodes_as_json()
        m.close()
 
        for e in json.loads(endp):
            if e["idx"] in app.config["agent_activation_keys"]:
                x = (
                    search_clientnodes_x_nodes(e["idx"])
                    or search_clientnodes_x_nodes(e.get("agent", ""))
                )
 
                if x:
                    # Use same ipAddress string as /clientnodes for online check (consistent status)
                    ip_raw = str(x.get("ipAddress") or "")
                    is_online = is_less_than_2_minutes(ip_raw) if ip_raw else False
                    ip_addr = _normalize_ip_url(ip_raw)  # normalized for response

                    endpoints.append({
                        "idx": x["key"],
                        "agent": x["agent"],
                        "ipAddress": ip_addr,
                        "ip": x.get("ip", ""),
                        "lastConnected": str(is_online),  # True=Online (same as /clientnodes)
                        "lastConnectedTime": x.get("lastConnectedTime", "")
                    })
                else:
                    # fallback if not present in clientnodes_x
                    endpoints.append({
                        "idx": e.get("idx"),
                        "agent": e.get("agent"),
                        "ipAddress": _normalize_ip_url(e.get("idx")),
                        "lastConnected": "False",
                        "lastConnectedTime": ""
                    })
 
        # If no endpoints from job records, show all activated agents (same as Endpoints page)
        # so Restore page can list agents and user can select one (restore points may be empty until backups exist)
        if not endpoints:
            for e in app.config["agent_activation_keys"]:
                x = search_clientnodes_x_nodes(e)
                if x:
                    ip_raw = str(x.get("ipAddress") or "")
                    is_online = is_less_than_2_minutes(ip_raw) if ip_raw else False
                    ip_addr = _normalize_ip_url(ip_raw)
                    endpoints.append({
                        "idx": x["key"],
                        "agent": x["agent"],
                        "ipAddress": ip_addr,
                        "ip": x.get("ip", ""),
                        "lastConnected": str(is_online),
                        "lastConnectedTime": x.get("lastConnectedTime", "")
                    })
 
        return jsonify({"result": endpoints}), 200
    except Exception:
        return jsonify({"result": endpoints}), 500


#@app.route("/bkp", methods=["get"])
#def get_data_bkp():
#    import sqlite3
#
#    source_db = r"D:\PyRepos\FlaskWebProject3\FlaskWebProject3\7c3eb001aa90c597e790f0468db1e0416a89089266e5d1dbc018bac5aa8a306a.db"
#    dump_file = "backup.sql"
#
#    conn = sqlite3.connect(source_db)
#    connD = sqlite3.connect(source_db+"ss.db")
#
#    try:
#        source_conn = sqlite3.connect(f"file:{source_db}?mode=ro", uri=True)
#        dest_conn = sqlite3.connect(f"{source_db}{time()}.db")
#        source_conn.backup(dest_conn,pages=500)
#        dest_conn.close()
#        source_conn.close()
#        return True
#    except sqlite3.Error as e:
#        print(f"Backup failed for {source_file}: {e}")
#        return False
#    # try:
#    #     with open(dump_file, "w", encoding="utf-8") as f:
#    #         for line in conn.iterdump():
#    #             f.write(f"{line}\n")
#    # except Exception as errr:
#    #     print(errr)
#
#    conn.close()
#
#    print(f"SQL dump complete → {dump_file}")
#    return (jsonify({"top10":"top_n_grouped_records"}),200)


@app.route("/api/top10jobs", methods=["POST"])
def get_restore_nodes():
    from .jobdata import JobsRecordManager
    m=JobsRecordManager("records.db", "records.json",app=app)
    top_n_grouped_records =[]
    try:
        top_n_grouped_records = m.fetch_jobs_as_json()
        m.close()
        return (jsonify({"top10":json.loads(top_n_grouped_records)}),200)
    except:
        m.close()
        return (jsonify({"top10":top_n_grouped_records}),500)
        
@app.route("/api/sendtoserver", methods=["POST"])
def api_sendtoserver():
    from .jobdata import JobsRecordManager
    reqJSON = None
    try:
        reqJSON =request.get_json(force=True)
    except Exception as sss: 
        print(str(sss))   ##kartik
        return jsonify({"status": "error", "message": str(sss)}), 500
    js_event = reqJSON.get("event",None)
    if js_event:
        if js_event in ["success"]:
            print("succeed")
            try:
                if reqJSON.get("succeed_count",None):
                    if reqJSON.get("idx",None):
                        app.config["job_success_data"].update({reqJSON.get("idx",None):reqJSON.get("succeed_count",None)})
            except:
                pass
            
        if js_event in ["restoresuccess"]:
            print("succeed")
        if js_event in ["error"]:
            try:
                if reqJSON.get("failed_count",None):
                    if reqJSON.get("idx",None):
                        app.config["job_failed_data"].update({reqJSON.get("idx",None):reqJSON.get("failed_count",None)})
            except:
                pass

            print("error")
        if js_event in ["All Jobs"]:
            print("alljobs ")
        if js_event in ["jobdelete"]:
            print("job deleted")
        if js_event in ["jobadded"]:
            print("succeed")
        if js_event in ["jobreschedule"]:
            print("succeed")
    if reqJSON.get("donot_send_to_customer",False):
        return jsonify({"status": "success"}), 200 
    try:
        r= requests.post("http://127.0.0.1:5000/notifier",json= request.json)
        return jsonify({"status": "success"}), 200 ##kartik
    except Exception as ss:
        print(str(ss))
        return jsonify({"status": "error", "message": str(ss)}), 500
        


def get_file_content(file_path):
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e)


def get_parent_directory(path):
    parent_path = os.path.abspath(os.path.dirname(path))

    # Check if the parent directory exists
    if not os.path.exists(parent_path) or not os.path.isdir(parent_path):
        return {"error": f"Invalid parent directory: {parent_path}"}

    # Filter out invalid entries (e.g., '.' and '..') and get file metadata
    contents = [
        get_file_metadata(os.path.join(parent_path, item))
        for item in os.listdir(parent_path)
    ]

    response_data = {"path": parent_path, "contents": contents}

    return response_data


########################################################
# def calculate_file_digest(file_path, hash_algorithm='md5', chunk_size=8192):
#     try:
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"File not found: {file_path}")

#         hash_function = hashlib.new(hash_algorithm)
#         lock = threading.Lock()

#         def hash_chunk(chunk):
#             nonlocal hash_function
#             hash_function.update(chunk)

#         with open(file_path, 'rb') as file:
#             threads = []
#             while chunk := file.read(chunk_size):
#                 thread = threading.Thread(target=hash_chunk, args=(chunk,))
#                 threads.append(thread)
#                 thread.start()

#             for thread in threads:
#                 thread.join()

#         return hash_function.hexdigest()
#     except Exception as e:
#         return ""# str(e)

# def calculate_file_digest(file_path, hash_algorithm='md5'):
#     try:
#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"File not found: {file_path}")

#         hash_function = hashlib.new(hash_algorithm)
#         with open(file_path, 'rb') as file:
#             while chunk := file.read(8192):
#                 hash_function.update(chunk)
#         return hash_function.hexdigest()
#     except Exception as e:
#         return ""#str(e)

# def get_directory_contents(path):
#     try:
#         contents = os.listdir(path)
#         return contents
#     except Exception as e:
#         return str(e)

# def get_file_metadata(file_path):
#     try:
#         stat_info = os.stat(file_path)
#         mime_type, _ = mimetypes.guess_type(file_path)
#         if not mime_type:
#             mime_type = 'application/octet-stream'  # Default MIME type for unknown files

#         file_name = os.path.basename(file_path)
#         digest_value = calculate_file_digest(file_path)

#         metadata = {
#             'name': file_name,
#             'type': 'file' if os.path.isfile(file_path) else 'directory',
#             'size': stat_info.st_size,
#             'last_modified': datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
#             'mimetype': mime_type,
#             'dgid': digest_value,
#         }
#         return metadata
#     except Exception as e:
#         return str(e)

# def get_file_content(file_path):
#     try:
#         return send_file(file_path, as_attachment=True)
#     except Exception as e:
#         return str(e)

#

# @app.route('/api/browse', methods=['POST'])
# def browse():
#     current_path = request.json.get('path', os.getcwd())

#     contents = [get_file_metadata(os.path.join(current_path, item)) for item in get_directory_contents(current_path)]

#     response_data = {
#         'path': current_path,
#         'contents': contents
#     }

#     return jsonify(response_data)

# @app.route('/api/open-file', methods=['POST'])
# def open_file():
#     file_path = request.json.get('path')

#     if not os.path.exists(file_path) or not os.path.isfile(file_path):
#         abort(404, f'File not found: {file_path}')

#     return get_file_content(file_path)

# @app.route('/api/go-up', methods=['POST'])
# def go_up():
#     current_path = request.json.get('path', os.getcwd())
#     parent_data = get_parent_directory(current_path)

#     return jsonify(parent_data)


################################################################################
# @app.after_request
# def after_request(response):
#     try :
#         if request.headers['origin']:
#             if request.headers['origin'] == "http://localhost:3001":
#                 response.headers.add('Access-Control-Allow-Origin',request.origin)
#                 response.headers.add('Content-Security-Policy',request.origin)
#             else:
#                 response.headers.add('Access-Control-Allow-Origin', request.headers['host'])
#                 response.headers.add('Content-Security-Policy',request.headers['host'])
#         else:
#                 response.headers.add('Access-Control-Allow-Origin', request.headers['host'])
#                 response.headers.add('Content-Security-Policy',request.headers['host'])
#     except Exception as e:
#         response.headers.add('Access-Control-Allow-Origin', request.headers['host'])
#         response.headers.add('Content-Security-Policy',request.headers['host'])
#     # response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'X-PINGTOGETHER,Content-Type,Authorization,Origin,Accept, x-requested-with')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     response.headers.add('Connection', 'keep-alive')
#     response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data:"

#     return response

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=True)
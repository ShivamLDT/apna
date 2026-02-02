"""
Routes and views for the flask application.
"""

# from crypt import methods
from ast import Try
import atexit
from collections import deque
from datetime import datetime
from fileinput import filename
import gc
from genericpath import isfile
from io import BytesIO
import json
from operator import contains
import os
import os.path
import os.path
from pathlib import Path
from sched import scheduler
from shutil import copy, copyfile
import shutil
from socket import create_connection
import subprocess
from sys import path
from time import time
from wsgiref import headers
from xml.dom import WrongDocumentErr
import zipfile

from pkg_resources import FileMetadata
from flask import Response, jsonify, make_response, render_template, request
from flask_apscheduler.api import add_job
from flask_socketio import send, emit
from requests.exceptions import HTTPError
import sqlalchemy
from sqlalchemy.util import win32
from fClient import app

# from  .sktiof import sktio
import websocket

from fClient.fingerprint import getCode, getKey
from fClient.p7zstd import p7zstd
# sktio.init_app(app)

##kartik
import logging
import logging.handlers
import sys
from fClient.structured_logging import log_event, log_chunk_event, ensure_job_id

# Create a logs folder if it doesn't exist
os.makedirs("every_logs", exist_ok=True)

LOG_FILE = "every_logs/client_view.log"

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

# --- 3 Windows Event Viewer handler ---
try:
    event_handler = logging.handlers.NTEventLogHandler(appname="ABC")
    event_handler.setLevel(logging.DEBUG)
    event_formatter = logging.Formatter(
        "[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    event_handler.setFormatter(event_formatter)
    logger.addHandler(event_handler)
except Exception as e:
    logger.warning(f"Could not attach Windows Event Viewer handler: {e}")

# Add file + console handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
##kartik

@app.route("/")
@app.route("/home")
def home():
    """Renders the home page."""
    # return render_template(
    #     "index.html",
    #     title="Home Page",
    #     year=datetime.now().year,
    # )
    return ("", 200)

def extract_chunks(data: bytes, pattern: bytes):
    plen = len(pattern)
    i = 0
    starts = []

    # Collect pattern start indices efficiently
    while i <= len(data) - plen:
        if data[i:i+plen] == pattern:
            starts.append(i)
            i += plen  # optional: move by plen for faster skip
        else:
            i += 1

    # Slice between the starts
    for idx in range(len(starts)):
        start = starts[idx]
        end = starts[idx + 1] if idx + 1 < len(starts) else len(data)
        yield data[start:end]


def extract_chunks_stream(file_path: str, pattern: bytes, buffer_size: int = 1024 * 1024):
    plen = len(pattern)
    buffer = b""
    with open(file_path, "rb") as f:
        for data in iter(lambda: f.read(buffer_size), b""):
            buffer += data
            while True:
                idx = buffer.find(pattern, 1)
                if idx == -1:
                    break
                yield buffer[:idx]
                buffer = buffer[idx:]
        if buffer:
            yield buffer

@app.route("/restoretest", methods=["POST"])
def restoretest():
    import base64
    import gzip
    import os
    import requests
    import hashlib
    from fClient.unc import EncryptedFileSystem, NetworkShare
    from fClient.cm import CredentialManager
    from gd import GDClient

    # from Crypto.Cipher import AES
    # from Crypto.Util.Padding import pad, unpad
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend

    import binascii
    res_h1={}
    isMetaFile=False
    try:
        print(request.headers)
    except:
        print("")
    target_file_name=""
    is_dycryption_done=False
    try:
        id = request.headers.get("id")
        pid = request.headers.get("pid")
        obj = request.headers.get("obj")        
        p_NameText= request.headers.get("pnametext",None)    
        mime = request.headers.get("mime") 

        objtarget = request.headers.get("objtarget",None)

        
        tcc = request.headers.get("tcc")
        tcc = base64.b64decode(tcc)
        tcc = gzip.decompress(tcc)
        tcc = tcc.decode("UTF-8")

        tccx = request.headers.get("tccx","")
        tccx = base64.b64decode(tccx)
        tccx = gzip.decompress(tccx)
        tccx = tccx.decode("UTF-8")
        tccx = tccx.replace("{{DRIVE}}", ":")
        
        # Fix malformed paths where drive letter is at the end (e.g., "Users\LDT\Documents\C:")
        # This can happen due to server-side path replacement issues
        import re
        if tccx and not re.match(r'^[A-Za-z]:[\\/]', tccx):
            # Check if drive letter is at the end
            drive_at_end = re.search(r'[\\/]([A-Za-z]:)$', tccx)
            if drive_at_end:
                drive_letter = drive_at_end.group(1)
                # Remove drive from end and prepend it correctly
                tccx = drive_letter + "\\" + tccx[:drive_at_end.start()]
            else:
                # No drive letter found - might be relative path, prepend nothing
                pass
        
        tccx = tccx.split(os.path.sep)
        if "Testing" in tccx:
            print("")
        rep = request.headers.get("rep")
        rep = base64.b64decode(rep)
        rep = gzip.decompress(rep)
        rep = rep.decode("UTF-8")

        sbd = request.headers.get("sbd")
        sbd = base64.b64decode(sbd)
        sbd = gzip.decompress(sbd)
        sbd = sbd.decode("UTF-8")
        uid=None
        pwd=None
        sbc = request.headers.get("sbc")
        sbc = base64.b64decode(sbc)
        sbc = gzip.decompress(sbc)
        sbc = sbc.decode("UTF-8")
        
        jid = request.headers.get("jid")
        jid = base64.b64decode(jid)
        jid = gzip.decompress(jid)
        jid = jid.decode("UTF-8")
        job_id = ensure_job_id(jid or id)

        repd = request.headers.get("repd")
        repd = base64.b64decode(repd)
        repd = gzip.decompress(repd)
        repd = repd.decode("UTF-8")
        jsrepd = json.loads(repd)

        if rep in ['AWS','AWSS3','GDRIVE','ONEDRIVE','AZURE']:
            payload = {"action":"repo_check", "rep":rep}
            req_onserver = requests.post(f'http://{app.config["server_ip"]}:{app.config["server_port"]}/dststorage',json=payload)
            response_data = req_onserver.json()
            if req_onserver.status_code in [200,'200', 201,'201']:
                if 'valid' in response_data and response_data['valid'] == False:
                    raise RuntimeError(f'Destination storage not configured {rep}')
                else: 
                    payload = {"rep":rep, "key":app.config.get('getCode', None)}
                    with requests.post(f'http://{app.config["server_ip"]}:{app.config["server_port"]}/download_cred',json=payload, stream=True) as r:
                        r.raise_for_status()
                        if rep == 'ONEDRIVE':
                            enc_file_name = f"OneDrive_credentials.enc"
                        elif rep == 'AZURE':
                            enc_file_name = f"Azure_credentials.enc"
                        elif rep == 'GDRIVE':
                            enc_file_name = f"token.pickle"
                        elif rep == 'AWSS3':
                            enc_file_name = f"AWS_credentials.enc"

                        with open(enc_file_name, "wb") as f:
                            import shutil
                            # shutil.copyfileobj(r.cont, f)
                            f.write(r.content)
            elif req_onserver.status_code in [400,404,500]:
                raise RuntimeError(f'Unexpected problem {rep},Please reconfigure or Contact for help')

        import ast
        extd = request.headers.get("extd",None)
        if extd:
            extd = base64.b64decode(extd)
            extd = gzip.decompress(extd)
            extd = extd.decode("UTF-8")
            try:
                if not type(extd) is dict:
                    extd = json.loads(extd)
            except:

                try:
                    extd = ast.literal_eval(extd)
                except (ValueError, SyntaxError) as e:
                    extd = None
            isMetaFile=extd.get('isMetaFile',False)
        try:
            if isinstance(jsrepd, str):
                jsrepd = json.loads(jsrepd)
                res_h1.update({"jsrepd":jsrepd}) 
        except:
            print(".. .. ..")
        
        # os.makedirs(tcc, exist_ok=True)
        tccn = request.headers.get("tccn")
        tccn = base64.b64decode(tccn)
        tccn = gzip.decompress(tccn)
        tccn = tccn.decode("UTF-8")
        tccn = tccn.replace("{{DRIVE}}", ":")
        
        # Fix malformed paths where drive letter is at the end (e.g., "Users\LDT\Documents\C:")
        # This can happen due to server-side path replacement issues
        import re as re_path_fix
        if tccn and not re_path_fix.match(r'^[A-Za-z]:[\\/]', tccn):
            drive_at_end = re_path_fix.search(r'[\\/]([A-Za-z]:)$', tccn)
            if drive_at_end:
                drive_letter = drive_at_end.group(1)
                tccn = drive_letter + "\\" + tccn[:drive_at_end.start()]
        
        tccn = tccn.split(os.path.sep)
        # Path normalization applied above
        
        tccnrest = request.headers.get("tccnrest")
        tccnrest = base64.b64decode(tccnrest)
        tccnrest = gzip.decompress(tccnrest)
        tccnrest = tccnrest.decode("UTF-8")
        tccnrest = tccnrest.replace("{{DRIVE}}", ":")
        
        tccnstamp = request.headers.get("tccnstamp")
        tccnstamp = base64.b64decode(tccnstamp)
        tccnstamp = gzip.decompress(tccnstamp)
        tccnstamp = tccnstamp.decode("UTF-8")
        
        try:
            import pytz
            from datetime import datetime
            tccnstamp_date= float(tccnstamp)
            date_format = "_%y%m%d_%I%M%S%p"
            p = pytz.timezone("Asia/Kolkata")
            #import datetime;
            #tccnstamp_date = datetime.datetime.utcfromtimestamp(tccnstamp_date).replace(tzinfo=p).strftime(date_format)
            #tccnstamp_date = datetime.datetime.utcfromtimestamp(tccnstamp_date).replace(tzinfo=pytz.utc).astimezone(date_format)
            tccnstamp_date = datetime.fromtimestamp(tccnstamp_date).replace(tzinfo=p).strftime(date_format)


        except:
            tccnstamp_date =tccnstamp

        res_h1.update({"id":id})
        res_h1.update({"pid":pid})
        res_h1.update({"obj":obj})
        res_h1.update({"p_NameText":p_NameText})
        res_h1.update({"objtarget":objtarget}) 
        res_h1.update({"tcc":tcc}) 
        res_h1.update({"tccx":tccx}) 
        res_h1.update({"rep":rep}) 
        res_h1.update({"sbd":sbd}) 
        res_h1.update({"sbc":sbc}) 
        res_h1.update({"repd":repd}) 
        res_h1.update({"tccn":tccn}) 
        res_h1.update({"tccnrest":tccnrest}) 
        res_h1.update({"tccnstamp":tccnstamp}) 
        
        res_h1=None
        if extd:
            res_h1=extd
            res_h1.update({"id":id})
            res_h1.update({"pid":pid})
        chunk_manifest = {}
        if extd and isinstance(extd, dict):
            chunk_manifest = extd.get("chunk_manifest", {}) or {}
        if not chunk_manifest or not chunk_manifest.get("chunks") or not chunk_manifest.get("total_chunks"):
            log_event(
                logger,
                logging.ERROR,
                job_id,
                "restore",
                file_path="",
                file_id=obj,
                error_code="MISSING_CHUNKS",
                error_message="Missing chunk manifest; aborting restore",
                extra={"event": "restore_aborted"},
            )
            log_event(
                logger,
                logging.ERROR,
                job_id,
                "restore",
                file_path="",
                file_id=obj,
                error_code="RESTORE_ABORTED",
                error_message="Restore aborted due to missing manifest",
                extra={"event": "restore_aborted"},
            )
            return make_response(jsonify({"restore": "failed", "reason": "MISSING_CHUNKS"}), 500)

        pattern = b'\x37\x7A\xBC\xAF\x27\x1C' #'b'7z\xbc'
        delimiter = b"---CHUNK-END---"

        iv = b""
        if jsrepd.get("givn", "") != "":
            try:
                iv = bytes.fromhex(jsrepd.get("givn", ""))
                decoded = iv.decode('utf-8')
                if not decoded.isprintable():
                    iv = jsrepd.get("givn", "")
            except Exception:
                iv = jsrepd.get("givn", "")
        # try:
        #     rem_path=f"{tccn}.svs"
        #     os.remove(rem_path)
        # except:
        #     print("")

        
        import re; is_drive = lambda p: bool(re.match(r'^[A-Za-z]:[\\/]', str(p)))
        start_index= 0 if is_drive((os.sep).join(tccn)) else 1
        # tccx (restore target) must keep drive letter - use its own start_index, not tccn's
        tccx_start_index = 0 if (tccx and len(tccx) > 0 and re.match(r'^[A-Za-z]:$', str(tccx[0]))) else start_index
        if len(tccn) > 1:
            os.makedirs(os.path.sep.join(tccn[start_index : len(tccn) - 1]), exist_ok=True)
        else:
            os.makedirs(os.path.sep.join(tccn[start_index:]), exist_ok=True)
        # tccn = os.path.sep.join(tccn[1:len(tcc)-2])

        tccn = os.path.sep.join(tccn[start_index:])
        res_h1.update({"tccn":tccn}) 
        log_event(
            logger,
            logging.INFO,
            job_id,
            "restore",
            file_path=tccn,
            file_id=obj,
            extra={"event": "job_start"},
        )
        log_event(
            logger,
            logging.INFO,
            job_id,
            "restore",
            file_path=tccn,
            file_id=obj,
            extra={"event": "file_start"},
        )
        log_event(
            logger,
            logging.INFO,
            job_id,
            "restore",
            file_path=tccn,
            file_id=obj,
            extra={"event": "restore_start"},
        )
        if len(tccx) > 1:
            os.makedirs(os.path.sep.join(tccx[tccx_start_index : len(tccx) - 1]), exist_ok=True)
        else:
            os.makedirs(os.path.sep.join(tccx[tccx_start_index:]), exist_ok=True)
        # tccx (restore path) uses tccx_start_index so drive letter is preserved
        tccx = os.path.sep.join(tccx[tccx_start_index:])       
        res_h1.update({"tccx":tccx}) 
        # responset = requests.post("http://"+request.remote_addr+":53335/data/download",headers={"id":id},stream=True)

        # x= Response(responset.iter_content(chunk_size=1024), content_type=responset.headers['content-type'])
        try:
            os.makedirs(os.path.dirname(tccn), exist_ok=True)
        except:
            pass
        # if other than UNC
        is_dycryption_done=False
        if (
            (str(rep).upper() == "AZURE") or (str(rep).upper() == "AWSS3") or (str(rep).upper() == "GDRIVE") or  (str(rep).upper() == "LAN") or (str(rep).upper().startswith("LOCAL")) or (str(rep).upper().startswith("ONEDRIVE"))
            ):
            target_file_name = tccn
            try:
                import magic  # type: ignore
            except Exception:
                magic = None
            from fClient.cktio import cl_socketio_obj
            extracted_data=b''
            file_metada=None
            isMetaFile=extd.get('isMetaFile',False)
            # GDrive/cloud non-meta: build file_metada from chunk_manifest so chunk-download loop runs (no server metadata fetch)
            if not isMetaFile and chunk_manifest and (str(rep).upper() in ["GDRIVE", "GOOGLEDRIVE", "AWSS3", "AZURE", "ONEDRIVE"]):
                expected_total = int(chunk_manifest.get("total_chunks") or 0)
                chunks_keys = chunk_manifest.get("chunks") or {}
                file_metada = sorted(chunks_keys.keys(), key=lambda x: int(x)) if chunks_keys else (list(range(1, expected_total + 1)) if expected_total else [])
                # GDrive: require gidn_list in jsrepd with length matching total_chunks
                if str(rep).upper() in ["GDRIVE", "GOOGLEDRIVE"]:
                    gidn_list = jsrepd.get("gidn_list")
                    if not gidn_list or not isinstance(gidn_list, (list, tuple)):
                        log_event(logger, logging.ERROR, job_id, "restore", file_path=tccn, file_id=obj, error_code="GDRIVE_MISSING_GIDN_LIST", error_message="gidn_list missing or invalid in backup metadata", extra={"event": "restore_aborted"})
                        return make_response(jsonify({"restore": "failed", "reason": "GDRIVE_MISSING_GIDN_LIST: gidn_list missing or invalid in backup metadata"}), 500)
                    if len(gidn_list) != expected_total:
                        log_event(logger, logging.ERROR, job_id, "restore", file_path=tccn, file_id=obj, error_code="GDRIVE_GIDN_LIST_LENGTH", error_message=f"gidn_list length {len(gidn_list)} != total_chunks {expected_total}", extra={"event": "restore_aborted"})
                        return make_response(jsonify({"restore": "failed", "reason": f"GDRIVE_GIDN_LIST_LENGTH: gidn_list has {len(gidn_list)} items, expected {expected_total}"}), 500)
                state_path = f"{tccn}.restore.state.json"
                completed_chunks = set()
                if os.path.exists(state_path):
                    try:
                        with open(state_path, "r", encoding="utf-8") as state_file:
                            state_data = json.load(state_file)
                            completed_chunks = set(state_data.get("completed_chunks", []))
                    except Exception:
                        completed_chunks = set()
            if isMetaFile:
                with requests.post(
                    f"http://{app.config['server_ip']}:{app.config['server_port']}/data/download",
                    headers={"id": id, "obj": obj, "pid": pid},
                    stream=True,
                ) as response_from_server:
                    response_from_server.raise_for_status()
                    if str(rep).upper() == "ONEDRIVE":
                        extracted_data=b''
                        response = requests.get(response_from_server.text, stream=True,verify=False)
                        for chunk in response.iter_content(4096):
                            extracted_data+=chunk
                        file_metada= json.loads(extracted_data.decode('utf-8'))
                    else:
                        file_metada= json.loads(response_from_server.content)
                import hashlib
                state_path = f"{tccn}.restore.state.json"
                completed_chunks = set()
                if os.path.exists(state_path):
                    try:
                        with open(state_path, "r", encoding="utf-8") as state_file:
                            state_data = json.load(state_file)
                            completed_chunks = set(state_data.get("completed_chunks", []))
                    except Exception:
                        completed_chunks = set()
                    if completed_chunks:
                        log_event(
                            logger,
                            logging.INFO,
                            job_id,
                            "restore",
                            file_path=tccn,
                            file_id=obj,
                            extra={"event": "restore_resume", "completed_chunks": len(completed_chunks)},
                        )
                expected_total = int(chunk_manifest.get("total_chunks") or 0)
                if expected_total and (file_metada is None or len(file_metada) != expected_total):
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        error_code="CHUNK_SEQUENCE_ERROR",
                        error_message="Metadata chunk count mismatch",
                        extra={"event": "restore_aborted", "expected": expected_total, "actual": len(file_metada)},
                    )
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        error_code="RESTORE_ABORTED",
                        error_message="Restore aborted due to chunk sequence mismatch",
                        extra={"event": "restore_aborted"},
                    )
                    return make_response(jsonify({"restore": "failed", "reason": "CHUNK_SEQUENCE_ERROR"}), 500)
            if file_metada is not None:
                expected_total = int(chunk_manifest.get("total_chunks") or 0)
                if expected_total and len(file_metada) != expected_total:
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        error_code="CHUNK_SEQUENCE_ERROR",
                        error_message="Metadata chunk count mismatch",
                        extra={"event": "restore_aborted", "expected": expected_total, "actual": len(file_metada)},
                    )
                    return make_response(jsonify({"restore": "failed", "reason": "CHUNK_SEQUENCE_ERROR"}), 500)
                ichunkscount=0
                ichunks_percent=0
                # if  os.path.exists(target_file_name): 
                #     os.remove(target_file_name)
                tempfilecreate=None
                try:
                    for file in file_metada:
                        extracted_data=b''
                        file_id = ichunkscount if str(rep).upper() == "GDRIVE" else file
                        log_chunk_event(
                            logger,
                            logging.DEBUG,
                            job_id,
                            "restore",
                            file_path=tccn,
                            file_id=obj,
                            chunk_index=ichunkscount + 1,
                            extra={"event": "chunk_download_start"},
                        )
                        if str(rep).upper() == "GDRIVE":
                            gd = GDClient()
                            gfid = jsrepd["gidn_list"][int(ichunkscount)]
                            if isinstance(gfid,dict):
                                gfid = gfid['id']
                            extracted_data = gd.download_file_bytesio(gfid).read()
                        else:
                            with requests.post(
                                f"http://{app.config['server_ip']}:{app.config['server_port']}/data/download/file",
                                headers={"id": id, "obj": obj, "pid": pid,"source":str(file_id), "fe":"1234567890987654321","mime":mime,"rep":str(rep), "repd":base64.b64encode(gzip.compress(str(repd).encode("UTF-8"),9,mtime=time())),"pro":json.dumps({"name": p_NameText,"tccnstamp":tccnstamp,"tccn":tccn,"agent": str(app.config.get("getCodeHost", None)),"pro":ichunks_percent})},
                                stream=True
                            ) as response_from_server:
                                response_from_server.raise_for_status()
                                # response=response_from_server
                                # extracted_data=response.content
                                chunk_index=0
                                if str(rep).upper() == "ONEDRIVE":
                                    try:
                                        response = requests.get(response_from_server.text, stream=True,verify=False)
                                    except:
                                        response = requests.get(response_from_server.text, stream=True)
                                    for chunk in response.iter_content(2**30):
                                        extracted_data+=chunk
                                else:
                                    extracted_data= response_from_server.content
                                
                        filetype= (magic.from_buffer(extracted_data))

                        # extracted_data = BytesIO(extracted_data)
                        if filetype.__contains__("gzip"):
                            try:
                                with gzip.GzipFile(fileobj=BytesIO(extracted_data), mode='rb') as gz_file:
                                    extracted_data = gz_file.read()
                            except Exception as e:
                                logger.warning(f"Error {str(e)}")
                        ichunkscount+=1
                        ichunks_percent = float(100*float(ichunkscount))/float(len(file_metada))
                        backup_status = {
                            "restore_flag":True,
                            "backup_jobs": [
                                {
                                    "status": "counting",
                                    "restore_flag":True,
                                    "name": p_NameText,
                                    "agent": str(app.config.get("getCodeHost", None)),
                                    "scheduled_time": datetime.fromtimestamp(
                                    float(tccnstamp)
                                ).strftime("%H:%M:%S"),
                                    "progress_number": ichunks_percent,
                                    "id": tccnstamp,
                                    "repo":rep,
                                    "filename": tccn,

                                }
                            ]
                        }    
                        try:
                            if not cl_socketio_obj.connected:
                                try:
                                    cl_socketio_obj.connect(
                                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                    )
                                except:
                                    cl_socketio_obj.connect(
                                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                    )
                            if cl_socketio_obj.connected:
                                cl_socketio_obj.emit("backup_data",backup_status)
                        except Exception as emit_error_occurs:
                            print("")
                        
                        # tempfilecreate = target_file_name + f"{ichunkscount}.bin"
                        tempfilecreate = target_file_name + ".bin"
                        pZip= p7zstd(iv)
                        # with open(tempfilecreate, "wb") as ftarget:
                        if isinstance(extracted_data,bytes):
                            print("Bytes data found ")   
                        else:
                            print("BytesIO data found ")
                        if str(ichunkscount + 1) in completed_chunks:
                            continue
                        with open(tempfilecreate, "ab") as ftarget:
                            #for df in extracted_data:
                            if extracted_data:
                                decompressed_data= pZip.decompress(encrypted_data=extracted_data,file_name=tccn)
                                expected_hash = str(chunk_manifest.get("chunks", {}).get(str(ichunkscount + 1), ""))
                                actual_hash = hashlib.sha256(decompressed_data).hexdigest()
                                if expected_hash and expected_hash != actual_hash:
                                    log_event(
                                        logger,
                                        logging.ERROR,
                                        job_id,
                                        "restore",
                                        file_path=tccn,
                                        file_id=obj,
                                        chunk_index=ichunkscount + 1,
                                        error_code="CHECKSUM_MISMATCH",
                                        error_message="Chunk checksum mismatch",
                                        extra={"event": "chunk_failed"},
                                    )
                                    log_event(
                                        logger,
                                        logging.ERROR,
                                        job_id,
                                        "restore",
                                        file_path=tccn,
                                        file_id=obj,
                                        chunk_index=ichunkscount + 1,
                                        error_code="RESTORE_ABORTED",
                                        error_message="Restore aborted due to chunk checksum mismatch",
                                        extra={"event": "restore_aborted"},
                                    )
                                    raise RuntimeError("Chunk checksum mismatch")
                                ftarget.write(decompressed_data)
                                ftarget.flush()
                                #restored_data +=decompressed_data
                                gc.collect()
                                completed_chunks.add(str(ichunkscount + 1))
                                try:
                                    with open(state_path, "w", encoding="utf-8") as state_file:
                                        json.dump({"completed_chunks": sorted(completed_chunks)}, state_file)
                                except Exception:
                                    pass
                        log_chunk_event(
                            logger,
                            logging.DEBUG,
                            job_id,
                            "restore",
                            file_path=tccn,
                            file_id=obj,
                            chunk_index=ichunkscount + 1,
                            extra={"event": "chunk_download_end"},
                        )
                except Exception as restore_error:
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        chunk_index=ichunkscount + 1,
                        error_code="RESTORE_CHUNK_FAILED",
                        error_message=str(restore_error),
                        extra={"event": "chunk_failed"},
                    )
                    if os.path.exists(tempfilecreate):
                        os.remove(tempfilecreate)

                del extracted_data
                del pZip
                gc.collect()

                try:
                    
                    if os.path.exists(tempfilecreate):

                        if os.path.exists(target_file_name):
                            ## write your existing file backup code here
                            try:
                                os.remove(target_file_name)
                            except Exception as restore_move:
                                #write res
                                print("")
                        try:
                            # subprocess.run(
                            #     ["cmd.exe", "/c", "move","/Y"] + [tempfilecreate] + [target_file_name],
                            #     shell=False,
                            #     check=True
                            # )

                            
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            startupinfo.wShowWindow = subprocess.SW_HIDE
                            cmd = f'move /Y "{tempfilecreate}" "{target_file_name}"'
                            subprocess.run(
                                 cmd, #["cmd.exe", "/c", "move", "/Y", f'"{tempfilecreate}"', f'"{target_file_name}"'],
                                shell=True,
                                check=True,
                                startupinfo=startupinfo,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )
                        except Exception as restore_move:
                            #write res
                            print("")
                            send_response=make_response (
                                jsonify({"file": jsrepd.get("original_path", tccn), "restore": "failed", "reason": (str(restore_move))}),
                                500,
                            )
                            if res_h1:
                                for key, value in res_h1.items():
                                    send_response.headers[key] = value
                            return send_response

                    
                except Exception as dddd:
                    print(str(dddd))
                    send_response=make_response (
                        jsonify({"file": jsrepd.get("original_path", tccn), "restore": "failed", "reason": (str(dddd))}),
                        500,
                    )
                    if res_h1:
                        for key, value in res_h1.items():
                            send_response.headers[key] = value
                    return send_response
                        
                if os.path.exists(tempfilecreate):
                    os.remove(tempfilecreate)
                        
                gc.collect()
                expected_file_hash = str(chunk_manifest.get("file_hash", ""))
                if expected_file_hash:
                    file_hasher = hashlib.sha256()
                    with open(tccn, "rb") as restored_file:
                        for block in iter(lambda: restored_file.read(1024 * 1024), b""):
                            file_hasher.update(block)
                    actual_file_hash = file_hasher.hexdigest()
                    if actual_file_hash != expected_file_hash:
                        log_event(
                            logger,
                            logging.ERROR,
                            job_id,
                            "restore",
                            file_path=tccn,
                            file_id=obj,
                            error_code="FILE_CHECKSUM_MISMATCH",
                            error_message="Restored file checksum mismatch",
                            extra={"event": "restore_aborted"},
                        )
                        log_event(
                            logger,
                            logging.ERROR,
                            job_id,
                            "restore",
                            file_path=tccn,
                            file_id=obj,
                            error_code="RESTORE_ABORTED",
                            error_message="Restore aborted due to file checksum mismatch",
                            extra={"event": "restore_aborted"},
                        )
                        return make_response(jsonify({"file": tccn, "restore": "failed", "reason": "FILE_CHECKSUM_MISMATCH"}), 500)
                else:
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        error_code="FILE_CHECKSUM_MISMATCH",
                        error_message="Missing expected file hash",
                        extra={"event": "restore_aborted"},
                    )
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        error_code="RESTORE_ABORTED",
                        error_message="Restore aborted due to missing file hash",
                        extra={"event": "restore_aborted"},
                    )
                    return make_response(jsonify({"file": tccn, "restore": "failed", "reason": "FILE_CHECKSUM_MISMATCH"}), 500)

                try:
                    state_path = f"{tccn}.restore.state.json"
                    if os.path.exists(state_path):
                        os.remove(state_path)
                except Exception:
                    pass
                send_response = make_response(jsonify({"file": tccn, "restore": "success", "reason": ""}), 200)
                # Add custom headers
                if res_h1:
                    for key, value in res_h1.items():
                        send_response.headers[key] = value
                log_event(
                    logger,
                    logging.INFO,
                    job_id,
                    "restore",
                    file_path=tccn,
                    file_id=obj,
                    extra={"event": "file_end"},
                )
                log_event(
                    logger,
                    logging.INFO,
                    job_id,
                    "restore",
                    file_path=tccn,
                    file_id=obj,
                    extra={"event": "restore_success"},
                )
                log_event(
                    logger,
                    logging.INFO,
                    job_id,
                    "restore",
                    file_path=tccn,
                    file_id=obj,
                    extra={"event": "job_end"},
                )
                return send_response
                # return 200
            log_chunk_event(
                logger,
                logging.DEBUG,
                job_id,
                "restore",
                file_path=tccn,
                file_id=obj,
                extra={"event": "chunk_download_start"},
            )
            temp_stream_path = tccn + ".svs"
            with requests.post(
                f"http://{app.config['server_ip']}:{app.config['server_port']}/data/download",
                headers={"id": id, "obj": obj, "pid": pid},
                stream=True,
            ) as response_from_server:
                response_from_server.raise_for_status()
                response = response_from_server
                if ((str(rep).upper().startswith("ONEDRIVE"))):
                    response = requests.get(response.text, stream=True,verify=False)
                with open(temp_stream_path, "wb") as stream_file:
                    for chunk in response.iter_content(1024 * 1024):
                        if chunk:
                            stream_file.write(chunk)
            log_chunk_event(
                logger,
                logging.DEBUG,
                job_id,
                "restore",
                file_path=tccn,
                file_id=obj,
                extra={"event": "chunk_download_end"},
            )

            filetype = magic.from_buffer(open(temp_stream_path, "rb").read(1024))
            stream_path = temp_stream_path
            if filetype.__contains__("gzip"):
                ungz_path = temp_stream_path + ".ungz"
                with gzip.open(temp_stream_path, "rb") as gz_file, open(ungz_path, "wb") as out_file:
                    shutil.copyfileobj(gz_file, out_file)
                stream_path = ungz_path

            expected_total = int(chunk_manifest.get("total_chunks") or 0)
            state_path = f"{tccn}.restore.state.json"
            completed_chunks = set()
            if os.path.exists(state_path):
                try:
                    with open(state_path, "r", encoding="utf-8") as state_file:
                        state_data = json.load(state_file)
                        completed_chunks = set(state_data.get("completed_chunks", []))
                except Exception:
                    completed_chunks = set()
                if completed_chunks:
                    log_event(
                        logger,
                        logging.INFO,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        extra={"event": "restore_resume", "completed_chunks": len(completed_chunks)},
                    )

            pZip = p7zstd(iv)
            chunk_index = 0
            with open(target_file_name, "ab") as ftarget:
                for raw_chunk in extract_chunks_stream(stream_path, pattern):
                    if not raw_chunk:
                        continue
                    chunk_index += 1
                    if not raw_chunk.startswith(pattern):
                        raw_chunk = pattern + raw_chunk
                    if str(chunk_index) in completed_chunks:
                        continue
                    log_chunk_event(
                        logger,
                        logging.DEBUG,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        chunk_index=chunk_index,
                        extra={"event": "chunk_start"},
                    )
                    decompressed_data = pZip.decompress(encrypted_data=raw_chunk, file_name=tccn)
                    expected_hash = str(chunk_manifest.get("chunks", {}).get(str(chunk_index), ""))
                    actual_hash = hashlib.sha256(decompressed_data).hexdigest()
                    if expected_hash and expected_hash != actual_hash:
                        log_event(
                            logger,
                            logging.ERROR,
                            job_id,
                            "restore",
                            file_path=tccn,
                            file_id=obj,
                            chunk_index=chunk_index,
                            error_code="CHECKSUM_MISMATCH",
                            error_message="Chunk checksum mismatch",
                            extra={"event": "chunk_failed"},
                        )
                        log_event(
                            logger,
                            logging.ERROR,
                            job_id,
                            "restore",
                            file_path=tccn,
                            file_id=obj,
                            chunk_index=chunk_index,
                            error_code="RESTORE_ABORTED",
                            error_message="Restore aborted due to chunk checksum mismatch",
                            extra={"event": "restore_aborted"},
                        )
                        raise RuntimeError("Chunk checksum mismatch")
                    ftarget.write(decompressed_data)
                    ftarget.flush()
                    completed_chunks.add(str(chunk_index))
                    try:
                        with open(state_path, "w", encoding="utf-8") as state_file:
                            json.dump({"completed_chunks": sorted(completed_chunks)}, state_file)
                    except Exception:
                        pass
                    log_chunk_event(
                        logger,
                        logging.DEBUG,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        chunk_index=chunk_index,
                        extra={"event": "chunk_end"},
                    )
            if expected_total and chunk_index != expected_total:
                log_event(
                    logger,
                    logging.ERROR,
                    job_id,
                    "restore",
                    file_path=tccn,
                    file_id=obj,
                    error_code="CHUNK_SEQUENCE_ERROR",
                    error_message="Chunk count mismatch",
                    extra={"event": "restore_aborted", "expected": expected_total, "actual": chunk_index},
                )
                log_event(
                    logger,
                    logging.ERROR,
                    job_id,
                    "restore",
                    file_path=tccn,
                    file_id=obj,
                    error_code="RESTORE_ABORTED",
                    error_message="Restore aborted due to chunk count mismatch",
                    extra={"event": "restore_aborted"},
                )
                raise RuntimeError("Chunk count mismatch")

            try:
                os.remove(temp_stream_path)
            except:
                pass
            try:
                if stream_path != temp_stream_path and os.path.exists(stream_path):
                    os.remove(stream_path)
            except:
                pass
            output_directory = os.path.dirname(tccn)
            output_directory_tmp = output_directory
            target_file_name = tccn
            try:
                os.makedirs(output_directory, exist_ok=True)
            except Exception as dd:
                logger.warning(f"Error creating directory Error: {str(dd)}")
                print(str(dd))

            if os.path.exists(target_file_name):
                
                try:
                    if os.path.isfile(tccnrest):
                        output_directory_tmp = os.path.join(str(Path(tccnrest).parent),f"_bak{tccnstamp_date}")
                    else:
                        output_directory_tmp = os.path.join(tccnrest,f"_bak{tccnstamp_date}")

                    os.makedirs(output_directory_tmp, exist_ok=True)
                except Exception as dd:
                    logger.warning(f"Error {str(dd)}")
                    print(str(dd))

                try:
                    from zipfile import PyZipFile,ZipFile as ZF
                    from zipfile import ZIP_LZMA,ZIP64_LIMIT,ZIP_DEFLATED 
                    
                    zip_file_path = os.path.join(output_directory_tmp,f"bak_{tccnstamp_date}.zip")
                    zip_f = ZF(zip_file_path,"a",ZIP_DEFLATED ,compresslevel=9)
                    zip_f.write(target_file_name, os.path.abspath(target_file_name).replace(":","_DRIVE"),ZIP_DEFLATED ,compresslevel=9)
                    zip_f.close()
                except Exception as e:
                    logger.warning(f"Error {str(e)}")
                    print("ddd")


                #copyfile(output_directory_tmp,output_directory_tmp+ str(time())+ ".bak")

            # if os.path.exists(target_file_name):
            #     copyfile(target_file_name,target_file_name+str(time())+ ".bak")
            target_file_name_abdc = tccn + ".abdc"
##########chunkfilegz.decompress_file(target_file_name, output_directory)
            if (str(rep).upper() in ["LAN", "LOCAL", "LOCAL STORAGE", "GDRIVE","AWSS3","AZURE","ONEDRIVE"]) :

                from Crypto.Cipher import AES as myAES
                from Crypto.Util.Padding  import unpad as myUnPad
                import zlib
                #cipher = myAES.new(getKey(keyx=obj), myAES.MODE_CBC, iv)
                chunk=True #extracted_data
                #chunks= chunk.split(delimiter)
                #decrypted_chunks=[]
                restored_data=b""
                #if chunk:
                #    chunk = restored_data.join(chunks)
                if chunk:
                    # decrypted= chunk #myUnPad(cipher.decrypt(chunk), myAES.block_size)
                    # decompressed_data = decrypted # zlib.decompress(decrypted)
                    # #the following line not found in 12022025 backup of this code
                    # decompressed_data = zlib.decompress(decrypted)
                    
                    extracted_data = extracted_data.split(pattern)
                    extracted_data = deque(extracted_data) 
                    pZip= p7zstd(iv)
                    with open(target_file_name, "ab") as ftarget:
                        #for df in extracted_data:
                        while extracted_data:
                            df = extracted_data.popleft()
                            if not df==b'':
                                df= pattern+df
                                decompressed_data= pZip.decompress(encrypted_data=df,file_name=tccn)
                                ftarget.write(decompressed_data)
                                ftarget.flush()
                                restored_data +=decompressed_data 
                            del df
                            gc.collect()
                    del extracted_data
                    del pZip

                    chunkfile = ZLibFileHandler(restored_data)
                    del restored_data
                    gc.collect()

                # # # with open(target_file_name_abdc, "wb") as ftarget:
                    

                    # cipher = Cipher(
                    #     algorithms.AES(getKey()), modes.CBC(iv), backend=default_backend()
                    # )
                    # unpadder = padding.PKCS7(128).unpadder()
                    # decrypted_data = b""
                    # with open(target_file_name, "rb") as f:
                    #     chunk = f.read(1024 * 1024 * 50)
                    #     decryptor = cipher.decryptor()
                    #     while chunk:
                    #         print("")
                    #         padded_data = decryptor.update(chunk) + decryptor.finalize()
                    #         decrypted_data += unpadder.update(padded_data)
                    #         # file.write(chunk)
                    #         chunk = f.read(1024 * 1024 * 50)
                    # ftarget.write(decrypted_data)
                    # # # with open(target_file_name, "rb") as f:
                    # # #     from Crypto.Cipher import AES as myAES
                    # # #     from Crypto.Util.Padding  import unpad as myUnPad
                    # # #     import zlib
                    # # #     #cipher = myAES.new(getKey(keyx=objtarget), myAES.MODE_CBC, iv)
                    # # #     cipher = myAES.new(getKey(keyx=obj), myAES.MODE_CBC, iv)
                    # # #     # chunk = f.read(1024 * 1024 * 50)
                    # # #     # restored_data=b""
                    # # #     # while chunk:
                    # # #     #     decrypted= myUnPad(cipher.decrypt(chunk), myAES.block_size)
                    # # #     #     decompressed_data = decrypted # zlib.decompress(decrypted)
                    # # #     #     restored_data +=decompressed_data 
                    # # #     #     chunk = f.read(1024 * 1024 * 50)#next cnhunk
                    # # # #ftarget.write(restored_data)
                    # # #     chunk = f.read()
                    # # #     chunks= chunk.split(delimiter)
                    # # #     decrypted_chunks=[]
                    # # #     restored_data=b""
                    # # #     if chunk:
                    # # #         chunk = restored_data.join(chunks)
                    # # #     if chunk:
                    # # #         decrypted= myUnPad(cipher.decrypt(chunk), myAES.block_size)
                    # # #         decompressed_data = decrypted # zlib.decompress(decrypted)
                    # # #         #the following line not found in 12022025 backup of this code
                    # # #         decompressed_data = zlib.decompress(decrypted)
                    # # #         restored_data +=decompressed_data 
                    # # #         chunk = f.read()#next cnhunkftarget.write(restored_data)
                    # # #     # for encrypted_chunk in chunks:
                    # # #     #     if encrypted_chunk:  # Ensure the chunk is not empty
                    # # #     #         if encrypted_chunk!= b'':
                    # # #     #             decrypted_chunk = myUnPad(cipher.decrypt(encrypted_chunk), myAES.block_size)
                    # # #     #             restored_data +=decrypted_chunk
                    # # #ftarget.write(restored_data)



            if jsrepd.get("givn", "") != "" and (str(rep).upper() != "GDRIVE" and str(rep).upper() != "AWSS3" and str(rep).upper() != "AZURE" and str(rep).upper() != "ONEDRIVE"):
                # #chunkfile.decompress_file(target_file_name_abdc, output_directory)
                # #chunkfile.decompress_straeam(target_file_name_abdc, output_directory)
                 
                # # try:
                    
                # #     copyfile(target_file_name_abdc,target_file_name)
                # # except:
                # #     print("Copied")
                # with open(target_file_name, "wb") as ftarget:
                #     ftarget.write(restored_data)
                print("")
            elif(str(rep).upper() == "GDRIVE" or str(rep).upper() == "AWSS3" or str(rep).upper() == "AZURE" or str(rep).upper() == "ONEDRIVE"):
                # #the following line has been writting twice for a reason
                # # copyfile(target_file_name,target_file_name_abdc)
                # # chunkfile = ZLibFileHandler(target_file_name_abdc )
                # # chunkfile.decompress_file(target_file_name, output_directory)
                # # # chunkfile.decompress_file(target_file_name_abdc, output_directory)
                # # # try:
                # # #     copyfile(target_file_name_abdc,target_file_name)
                # # # except:
                # # #     print("Copied")
                # with open(target_file_name, "wb") as ftarget:
                #     ftarget.write(restored_data)
                print("")
                
            elif(str(rep).upper() == "AMAZS3"):
                print("S3Download")
                
            else:
                chunkfile.decompress_file(target_file_name, output_directory)
            try:
                os.remove(tccn + ".svs")
            except:
                print("")
            try:
                os.remove(target_file_name_abdc)
            except:
                print("")
            #return (jsonify({"file": tccn, "restore": "success", "reason": ""}), 200)
            
            expected_file_hash = str(chunk_manifest.get("file_hash", ""))
            if expected_file_hash:
                file_hasher = hashlib.sha256()
                with open(tccn, "rb") as restored_file:
                    for block in iter(lambda: restored_file.read(1024 * 1024), b""):
                        file_hasher.update(block)
                actual_file_hash = file_hasher.hexdigest()
                if actual_file_hash != expected_file_hash:
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        error_code="FILE_CHECKSUM_MISMATCH",
                        error_message="Restored file checksum mismatch",
                        extra={"event": "restore_aborted"},
                    )
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "restore",
                        file_path=tccn,
                        file_id=obj,
                        error_code="RESTORE_ABORTED",
                        error_message="Restore aborted due to file checksum mismatch",
                        extra={"event": "restore_aborted"},
                    )
                    return make_response(jsonify({"file": tccn, "restore": "failed", "reason": "FILE_CHECKSUM_MISMATCH"}), 500)
            else:
                log_event(
                    logger,
                    logging.ERROR,
                    job_id,
                    "restore",
                    file_path=tccn,
                    file_id=obj,
                    error_code="FILE_CHECKSUM_MISMATCH",
                    error_message="Missing expected file hash",
                    extra={"event": "restore_aborted"},
                )
                log_event(
                    logger,
                    logging.ERROR,
                    job_id,
                    "restore",
                    file_path=tccn,
                    file_id=obj,
                    error_code="RESTORE_ABORTED",
                    error_message="Restore aborted due to missing file hash",
                    extra={"event": "restore_aborted"},
                )
                return make_response(jsonify({"file": tccn, "restore": "failed", "reason": "FILE_CHECKSUM_MISMATCH"}), 500)

            try:
                state_path = f"{tccn}.restore.state.json"
                if os.path.exists(state_path):
                    os.remove(state_path)
            except Exception:
                pass
            send_response = make_response(jsonify({"file": tccn, "restore": "success", "reason": ""}), 200)
            # Add custom headers
            for key, value in res_h1.items():
                send_response.headers[key] = value
            log_event(
                logger,
                logging.INFO,
                job_id,
                "restore",
                file_path=tccn,
                file_id=obj,
                extra={"event": "file_end"},
            )
            log_event(
                logger,
                logging.INFO,
                job_id,
                "restore",
                file_path=tccn,
                file_id=obj,
                extra={"event": "restore_success"},
            )
            log_event(
                logger,
                logging.INFO,
                job_id,
                "restore",
                file_path=tccn,
                file_id=obj,
                extra={"event": "job_end"},
            )
            return send_response

        if str(rep).upper() == "UNC":# or str(rep).upper() == "NAS":
            is_dycryption_done=False
            try:
                target_file_name = tccx #jsrepd.get('original_path',"90809hkjbhh7y6guhvfgd453we5eytgfjhjadisufaodhfkgeragfjksdjh")
                #######
                
                try:
                    #target_file_name = jsrepd.get("restore_path",jsrepd.get("original_path",""))
                    file_name=jsrepd.get("original_path","").split(os.sep)[-1]
                    if os.path.exists(target_file_name):
                        if not target_file_name.endswith(file_name):
                            file_path=jsrepd.get("original_path","").split(os.sep)[-1]
                            target_file_name = os.path.join(target_file_name,file_path)
                except Exception as e:
                    logger.warning(f"Error {str(e)}")
                    pass
                #######
                if os.path.exists(target_file_name)and os.path.isfile(target_file_name):
                
                    
                    try:
                        output_directory_tmp = os.path.join(tccnrest,f"_bak{tccnstamp_date}")
                        if os.path.isfile(tccnrest):
                            output_directory_tmp = os.path.join(os.path.dirname( tccnrest),f"_bak{tccnstamp_date}")
                        # if os.path.isfile(tccnrest):
                        #     output_directory_tmp = os.path.join(tccnrest,f"_bak{tccnstamp_date}")
                        os.makedirs(output_directory_tmp, exist_ok=True)
                    except Exception as dd:
                        logger.warning(f"Error {str(dd)}")
                        print(str(dd))

                    try:
                        from zipfile import PyZipFile,ZipFile as ZF
                        from zipfile import ZIP_LZMA,ZIP64_LIMIT,ZIP_DEFLATED 
                    
                        zip_file_path = os.path.join(output_directory_tmp,f"bak_{tccnstamp_date}.zip")
                        zip_f = ZF(zip_file_path,"a",ZIP_DEFLATED ,compresslevel=9)
                        zip_f.write(target_file_name, os.path.abspath(target_file_name).replace(":","_DRIVE"),ZIP_DEFLATED ,compresslevel=9)
                        zip_f.close()
                        copyfile(target_file_name,target_file_name+str(tccnstamp_date)+ ".bakx") 
                    except Exception as e:
                        logger.warning(f"Error {str(e)}")
                        print("ddd")
            except Exception as e:
                logger.warning(f"Error {str(e)}")
                print("SS")
            try:
                uid=sbd
                pwd=sbc
                if sbd == None or sbc == None or sbd == "" or sbc == "" or sbd == str(None) or sbc == str(None):
                    cm = CredentialManager(jsrepd.get("scombm", ""),keyx=obj)
                    uid, pwd = cm.retrieve_credentials(jsrepd.get("scombm", ""))
                if uid == None or pwd == None or uid == "" or pwd == "" or uid == str(None) or pwd == str(None):
                    print("failed to login")
                    uid, pwd = cm.retrieve_credentials(jsrepd.get("scombm", ""))
                    if uid == None or pwd == None:
                        print("failed to login")
                repo_d = {
                    "ipc": str(jsrepd["scombm"]),
                    "uid": str(uid),
                    "idn": str(pwd),
                    "loc": str(jsrepd["scombs"]),
                }
                conn = getConn(repo_d,keyx=obj,job_id= jid)
                if conn:
                    conn.key =getKey(keyx=obj)
                
                jsrepd["restore_path"]=tccx
                jsrepd["restore_path_verification"]=tccnrest
                x=tccx

                try:
                    if os.path.exists(x):
                        copyfile(x,target_file_name+str(tccnstamp_date)+ ".bakx") 
                except:
                    print("Copied")

                # try:
                #     if jsrepd["restore_path"]:
                #         if os.path.exists(jsrepd["restore_path"]):
                #             copyfile(x,target_file_name+str(tccnstamp_date)+ ".bakx") 
                # except:
                #     print("Copied")
                is_dycryption_done=False
                if conn:
                    from fClient.cktio import cl_socketio_obj
                    from datetime import datetime as dt_restore
                    def _unc_restore_progress_cb(chunk_idx, total_chunks, progress_pct):
                        """Emit restore progress to server for UI update."""
                        try:
                            backup_status = {
                                "restore_flag": True,
                                "backup_jobs": [
                                    {
                                        "status": "counting",
                                        "restore_flag": True,
                                        "name": p_NameText,
                                        "agent": str(app.config.get("getCodeHost", "")),
                                        "scheduled_time": dt_restore.fromtimestamp(float(tccnstamp)).strftime("%H:%M:%S"),
                                        "progress_number": float(progress_pct),
                                        "id": float(tccnstamp),
                                        "repo": rep,
                                        "filename": os.path.sep.join(tccn) if isinstance(tccn, list) else tccn,
                                        "restore_location": tccx,
                                    }
                                ]
                            }
                            if not cl_socketio_obj.connected:
                                try:
                                    cl_socketio_obj.connect(f"ws://{app.config['server_ip']}:{app.config['server_port']}")
                                except Exception:
                                    pass
                            if cl_socketio_obj.connected:
                                cl_socketio_obj.emit("backup_data", backup_status)
                        except Exception as cb_err:
                            logger.debug(f"UNC restore progress emit: {cb_err}")
                    is_dycryption_done=conn.decrypt_and_reassemble_file(
                        file_path=jsrepd["original_path"], metadata=jsrepd,
                        progress_callback=_unc_restore_progress_cb
                    )
                else:
                    try:
                        if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                            copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                            os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
                    except:
                        print("Copied")

                    send_response =make_response (
                        jsonify(
                            {
                                "file": jsrepd["original_path"],
                                "restore": "failed",
                                "reason": "Couln't Connect to Fileserver",
                            }
                        ),
                        500,
                    )

                    # Add custom headers
                    for key, value in res_h1.items():
                        send_response.headers[key] = value
                    return send_response
                
                # try:
                #     if conn:
                #         is_dycryption_done = conn.decrypt_and_reassemble_file(
                #             file_path=jsrepd["original_path"], metadata=jsrepd
                #         )
                # except:
                #     print("Connention close exception")


            except Exception as e:
                logger.warning(f"Error {str(e)}")
                print("")
                if not is_dycryption_done:
                    try:
                        if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                            copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                            os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
                    except:
                        print("Copied")
                    send_response =make_response (
                        jsonify(
                            {
                                "file": jsrepd["original_path"],
                                "restore": "failed",
                                "reason": "Couln't Connect to Fileserver",
                            }
                        ),
                        500,
                    )
                    for key, value in res_h1.items():
                        send_response.headers[key] = value
                    return send_response
                else:
                    try:
                        os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
                    except:
                        print("not removed")

                send_response=make_response (
                    jsonify({"file": jsrepd["original_path"], "restore": "failed", "reason": (str(e))}),
                    500,
                )
                for key, value in res_h1.items():
                    send_response.headers[key] = value
                return send_response
            finally:
                conn=None
                del conn
        if not is_dycryption_done:
            try:
                if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                    copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                    os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
            except:
                print("Copied")
            send_response =make_response (
                jsonify(
                    {
                        "file": jsrepd["original_path"],
                        "restore": "failed",
                        "reason": "Couln't Connect to Fileserver",
                    }
                ),
                500,
            )
            for key, value in res_h1.items():
                send_response.headers[key] = value
            return send_response
        # else:
        #     try:
        #         os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
        #     except:
        #         print("not removed")

        # Verify file actually exists before reporting success (UNC/restore path)
        restore_target = tccx if tccx else (target_file_name or jsrepd.get("restore_path", ""))
        if restore_target and str(rep).upper() == "UNC":
            if not os.path.isfile(restore_target):
                log_event(
                    logger,
                    logging.ERROR,
                    job_id,
                    "restore",
                    file_path=restore_target,
                    file_id=obj,
                    error_code="RESTORE_FILE_MISSING",
                    error_message=f"File not found after restore: {restore_target}",
                    extra={"event": "restore_file_verify_failed", "restore_path": restore_target},
                )
                send_response = make_response(
                    jsonify({
                        "file": jsrepd.get("original_path", ""),
                        "restore": "failed",
                        "reason": f"File was not written to target: {restore_target}",
                    }),
                    500,
                )
                if res_h1:
                    for key, value in res_h1.items():
                        send_response.headers[key] = value
                return send_response

        send_response = make_response (jsonify({"file": jsrepd.get("original_path", target_file_name or ""), "restore": "success", "reason": ""}), 200)
        if res_h1:
            for key, value in res_h1.items():
                send_response.headers[key] = value
        return send_response

    except (HTTPError, Exception) as e:
        import traceback
        traceback.print_exc()
        log_event(
            logger,
            logging.ERROR,
            job_id,
            "restore",
            file_path=target_file_name or "",
            file_id=obj if "obj" in locals() else None,
            error_code="RESTORE_FAILED",
            error_message=str(e),
            extra={"event": "job_failed"},
        )
        logger.warning(f"Error {str(e)}")
        reason=str(e)
        if str(rep).upper() != "UNC":
            is_dycryption_done=True
            x=target_file_name

        if not is_dycryption_done :
            try:

                if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                    copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                    os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
            except:
                print("Copied")
            # Only HTTPError has .response; KeyError/AttributeError etc. do not
            e_response = getattr(e, "response", None)
            if e_response is not None and e_response.status_code == 404:
                reason="source file not found on fileserver"
            response= make_response (
                jsonify(
                    {
                        "file": x,
                        "restore": "failed",
                        "reason": reason,
                    }
                ),
                500,
            )
            if res_h1:
                for key, value in res_h1.items():
                    response.headers[key] = value
            return response
        else:
            try:
                os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
            except:
                print("not removed")

        response= make_response (jsonify({"file": jsrepd.get("original_path", jsrepd.get("path", "")), "restore": "failed", "reason": (str(e))}), 500)
        if res_h1:
            for key, value in res_h1.items():
                response.headers[key] = value
        return response

@app.route("/restoretest2", methods=["POST"])
def restoretest2():
    import base64
    import gzip
    import os
    import requests
    from fClient.unc import EncryptedFileSystem, NetworkShare
    from fClient.cm import CredentialManager

    # from Crypto.Cipher import AES
    # from Crypto.Util.Padding import pad, unpad
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend

    import binascii
    res_h1={}
    try:
        print(request.headers)
    except:
        print("")
    target_file_name=""
    is_dycryption_done=False
    try:
        id = request.headers.get("id")
        pid = request.headers.get("pid")
        obj = request.headers.get("obj")        
        objtarget = request.headers.get("objtarget",None)

        
        tcc = request.headers.get("tcc")
        tcc = base64.b64decode(tcc)
        tcc = gzip.decompress(tcc)
        tcc = tcc.decode("UTF-8")

        tccx = request.headers.get("tccx","")
        tccx = base64.b64decode(tccx)
        tccx = gzip.decompress(tccx)
        tccx = tccx.decode("UTF-8")
        tccx = tccx.replace("{{DRIVE}}", ":")
        
        # Fix malformed paths where drive letter is at the end (e.g., "Users\LDT\Documents\C:")
        import re as re_fix
        if tccx and not re_fix.match(r'^[A-Za-z]:[\\/]', tccx):
            drive_at_end = re_fix.search(r'[\\/]([A-Za-z]:)$', tccx)
            if drive_at_end:
                drive_letter = drive_at_end.group(1)
                tccx = drive_letter + "\\" + tccx[:drive_at_end.start()]
        
        tccx = tccx.split(os.path.sep)
         
        rep = request.headers.get("rep")
        rep = base64.b64decode(rep)
        rep = gzip.decompress(rep)
        rep = rep.decode("UTF-8")

        sbd = request.headers.get("sbd")
        sbd = base64.b64decode(sbd)
        sbd = gzip.decompress(sbd)
        sbd = sbd.decode("UTF-8")
        uid=None
        pwd=None
        sbc = request.headers.get("sbc")
        sbc = base64.b64decode(sbc)
        sbc = gzip.decompress(sbc)
        sbc = sbc.decode("UTF-8")
        
        jid = request.headers.get("jid")
        jid = base64.b64decode(jid)
        jid = gzip.decompress(jid)
        jid = jid.decode("UTF-8")

        repd = request.headers.get("repd")
        repd = base64.b64decode(repd)
        repd = gzip.decompress(repd)
        repd = repd.decode("UTF-8")
        jsrepd = json.loads(repd)

        import ast
        extd = request.headers.get("extd",None)
        if extd:
            extd = base64.b64decode(extd)
            extd = gzip.decompress(extd)
            extd = extd.decode("UTF-8")
            try:
                extd = json.loads(extd)
            except:

                try:
                    extd = ast.literal_eval(extd)
                except (ValueError, SyntaxError) as e:
                    extd = None

        try:
            if isinstance(jsrepd, str):
                jsrepd = json.loads(jsrepd)
                res_h1.update({"jsrepd":jsrepd}) 
        except:
            print(".. .. ..")
        
        # os.makedirs(tcc, exist_ok=True)
        tccn = request.headers.get("tccn")
        tccn = base64.b64decode(tccn)
        tccn = gzip.decompress(tccn)
        tccn = tccn.decode("UTF-8")
        tccn = tccn.replace("{{DRIVE}}", ":")
        
        # Fix malformed paths where drive letter is at the end (e.g., "Users\LDT\Documents\C:")
        import re as re_tccn_fix
        if tccn and not re_tccn_fix.match(r'^[A-Za-z]:[\\/]', tccn):
            drive_at_end = re_tccn_fix.search(r'[\\/]([A-Za-z]:)$', tccn)
            if drive_at_end:
                drive_letter = drive_at_end.group(1)
                tccn = drive_letter + "\\" + tccn[:drive_at_end.start()]
        
        tccn = tccn.split(os.path.sep)
       #here is a problem that path is comming WrongDocumentErr (Fixed with drive letter check above)
        import re as re_tccx2
        tccx_start_index = 0 if (tccx and len(tccx) > 0 and re_tccx2.match(r'^[A-Za-z]:$', str(tccx[0]))) else 1
        
        tccnrest = request.headers.get("tccnrest")
        tccnrest = base64.b64decode(tccnrest)
        tccnrest = gzip.decompress(tccnrest)
        tccnrest = tccnrest.decode("UTF-8")
        tccnrest = tccnrest.replace("{{DRIVE}}", ":")
        
        tccnstamp = request.headers.get("tccnstamp")
        tccnstamp = base64.b64decode(tccnstamp)
        tccnstamp = gzip.decompress(tccnstamp)
        tccnstamp = tccnstamp.decode("UTF-8")
        
        try:
            import pytz
            tccnstamp_date= float(tccnstamp)
            date_format = "_%y%m%d_%I%M%S%p"
            p = pytz.timezone("Asia/Kolkata")
            import datetime;
            #tccnstamp_date = datetime.datetime.utcfromtimestamp(tccnstamp_date).replace(tzinfo=p).strftime(date_format)
            #tccnstamp_date = datetime.datetime.utcfromtimestamp(tccnstamp_date).replace(tzinfo=pytz.utc).astimezone(date_format)
            tccnstamp_date = datetime.datetime.fromtimestamp(tccnstamp_date).replace(tzinfo=p).strftime(date_format)


        except:
            tccnstamp_date =tccnstamp

        res_h1.update({"id":id})
        res_h1.update({"pid":pid})
        res_h1.update({"obj":obj})
        res_h1.update({"objtarget":objtarget}) 
        res_h1.update({"tcc":tcc}) 
        res_h1.update({"tccx":tccx}) 
        res_h1.update({"rep":rep}) 
        res_h1.update({"sbd":sbd}) 
        res_h1.update({"sbc":sbc}) 
        res_h1.update({"repd":repd}) 
        res_h1.update({"tccn":tccn}) 
        res_h1.update({"tccnrest":tccnrest}) 
        res_h1.update({"tccnstamp":tccnstamp}) 
        
        res_h1=None
        if extd:
            res_h1=extd
            res_h1.update({"id":id})
            res_h1.update({"pid":pid})

        delimiter = b"---CHUNK-END---"

        iv = b""
        if jsrepd.get("givn", "") != "":
            iv = bytes.fromhex(jsrepd.get("givn", ""))
        try:
            os.remove(tccn + ".svs")
        except:
            print("")

        if len(tccn) > 1:
            os.makedirs(os.path.sep.join(tccn[1 : len(tccn) - 1]), exist_ok=True)
        else:
            os.makedirs(os.path.sep.join(tccn[1:]), exist_ok=True)
        # tccn = os.path.sep.join(tccn[1:len(tcc)-2])

        tccn = os.path.sep.join(tccn[1:])
        res_h1.update({"tccn":tccn}) 
        if len(tccx) > 1:
            os.makedirs(os.path.sep.join(tccx[tccx_start_index : len(tccx) - 1]), exist_ok=True)
        else:
            os.makedirs(os.path.sep.join(tccx[tccx_start_index:]), exist_ok=True)
        # tccx (restore path) uses tccx_start_index so drive letter is preserved
        tccx = os.path.sep.join(tccx[tccx_start_index:])       
        res_h1.update({"tccx":tccx}) 
        # responset = requests.post("http://"+request.remote_addr+":53335/data/download",headers={"id":id},stream=True)

        # x= Response(responset.iter_content(chunk_size=1024), content_type=responset.headers['content-type'])
        try:
            os.makedirs(os.path.dirname(tccn), exist_ok=True)
        except:
            pass
        # if other than UNC
        is_dycryption_done=False
        if ((str(rep).upper() == "AZURE") or (str(rep).upper() == "AWSS3") or (str(rep).upper() == "GDRIVE") or  (str(rep).upper() == "LAN") or (str(rep).upper().startswith("LOCAL")) or (str(rep).upper().startswith("ONEDRIVE"))):
            target_file_name = tccn
            with requests.post(
                f"http://{request.remote_addr}:{app.config['server_port']}/data/download",
                headers={"id": id, "obj": obj, "pid": pid},
                stream=True,
            ) as response:
                response.raise_for_status()
                with open(tccn + ".svs", "wb") as file:
                    file.write(response.content)
            from fClient.gzpks.class1 import GzipFileHandler, ZLibFileHandler

            chunkfilegz = GzipFileHandler(tccn + ".svs")

            chunkfile = ZLibFileHandler(tccn + ".svs")
            output_directory = os.path.dirname(tccn)
            output_directory_tmp = output_directory
            target_file_name = tccn
            try:
                os.makedirs(output_directory, exist_ok=True)
            except Exception as dd:
                print(str(dd))

            if os.path.exists(target_file_name):
                
                try:
                    if os.path.isfile(tccnrest):
                        output_directory_tmp = os.path.join(str(Path(tccnrest).parent),f"_bak{tccnstamp_date}")
                    else:
                        output_directory_tmp = os.path.join(tccnrest,f"_bak{tccnstamp_date}")

                    os.makedirs(output_directory_tmp, exist_ok=True)
                except Exception as dd:
                    print(str(dd))

                try:
                    from zipfile import PyZipFile,ZipFile as ZF
                    from zipfile import ZIP_LZMA,ZIP64_LIMIT,ZIP_DEFLATED 
                    
                    zip_file_path = os.path.join(output_directory_tmp,f"bak_{tccnstamp_date}.zip")
                    zip_f = ZF(zip_file_path,"a",ZIP_DEFLATED ,compresslevel=9)
                    zip_f.write(target_file_name, os.path.abspath(target_file_name).replace(":","_DRIVE"),ZIP_DEFLATED ,compresslevel=9)
                    zip_f.close()
                except:
                    print("ddd")

            target_file_name_abdc = tccn + ".abdc"
            chunkfilegz.decompress_file(target_file_name, output_directory)
            if (str(rep).upper() in ["LAN", "LOCAL", "LOCAL STORAGE", "GDRIVE","AWSS3","AZURE","ONEDRIVE"]) :
                with open(target_file_name_abdc, "wb") as ftarget:
                    with open(target_file_name, "rb") as f:
                        from Crypto.Cipher import AES as myAES
                        from Crypto.Util.Padding  import unpad as myUnPad
                        import zlib

                        cipher = myAES.new(getKey(keyx=obj), myAES.MODE_CBC, iv)
                        chunk = f.read()
                        chunks= chunk.split(delimiter)
                        decrypted_chunks=[]
                        restored_data=b""
                        if chunk:
                            chunk = restored_data.join(chunks)
                        if chunk:
                            # decrypted= myUnPad(cipher.decrypt(chunk), myAES.block_size)
                            # decompressed_data = decrypted # zlib.decompress(decrypted)
                            # #the following line not found in 12022025 backup of this code
                            # decompressed_data = zlib.decompress(decrypted)
                            pZip= p7zstd(iv)
                            decompressed_data= pZip.decompress(data=chunk,file_name=tccn)
                            del pZip
                            restored_data +=decompressed_data 
                            chunk = f.read()

                    ftarget.write(restored_data)
            if jsrepd.get("givn", "") != "" and (str(rep).upper() != "GDRIVE" and str(rep).upper() != "AWSS3" and str(rep).upper() != "AZURE" and str(rep).upper() != "ONEDRIVE"):
                chunkfile.decompress_file(target_file_name_abdc, output_directory)
                try:
                    copyfile(target_file_name_abdc,target_file_name)
                except:
                    print("Copied")

            elif((str(rep).upper() == "GDRIVE") or (str(rep).upper() == "AWSS3") or (str(rep).upper() == "AZURE") or (str(rep).upper() == "ONEDRIVE")):
                #the following line has been writting twice for a reason
                # copyfile(target_file_name,target_file_name_abdc)
                # chunkfile = ZLibFileHandler(target_file_name_abdc )
                # chunkfile.decompress_file(target_file_name, output_directory)
                chunkfile.decompress_file(target_file_name_abdc, output_directory)
                try:
                    copyfile(target_file_name_abdc,target_file_name)
                except:
                    print("Copied")
            elif(str(rep).upper() == "AMAZS3"):
                print("S3Download")
                
            else:
                chunkfile.decompress_file(target_file_name, output_directory)
            
            os.remove(tccn + ".svs")
            os.remove(target_file_name_abdc)
            #return (jsonify({"file": tccn, "restore": "success", "reason": ""}), 200)
            
            send_response = make_response(jsonify({"file": tccn, "restore": "success", "reason": ""}), 200)
            # Add custom headers
            for key, value in res_h1.items():
                send_response.headers[key] = value
            return send_response

        if str(rep).upper() == "UNC":# or str(rep).upper() == "NAS":
            is_dycryption_done=False
            try:
                target_file_name = tccx #jsrepd.get('original_path',"90809hkjbhh7y6guhvfgd453we5eytgfjhjadisufaodhfkgeragfjksdjh")
                #######
                
                try:
                    #target_file_name = jsrepd.get("restore_path",jsrepd.get("original_path",""))
                    file_name=jsrepd.get("original_path","").split(os.sep)[-1]
                    if os.path.exists(target_file_name):
                        if not target_file_name.endswith(file_name):
                            file_path=jsrepd.get("original_path","").split(os.sep)[-1]
                            target_file_name = os.path.join(target_file_name,file_path)
                except:
                    pass
                #######
                if os.path.exists(target_file_name)and os.path.isfile(target_file_name):
                
                    
                    try:
                        output_directory_tmp = os.path.join(tccnrest,f"_bak{tccnstamp_date}")
                        if os.path.isfile(tccnrest):
                            output_directory_tmp = os.path.join(os.path.dirname( tccnrest),f"_bak{tccnstamp_date}")
                        # if os.path.isfile(tccnrest):
                        #     output_directory_tmp = os.path.join(tccnrest,f"_bak{tccnstamp_date}")
                        os.makedirs(output_directory_tmp, exist_ok=True)
                    except Exception as dd:
                        print(str(dd))

                    try:
                        from zipfile import PyZipFile,ZipFile as ZF
                        from zipfile import ZIP_LZMA,ZIP64_LIMIT,ZIP_DEFLATED 
                    
                        zip_file_path = os.path.join(output_directory_tmp,f"bak_{tccnstamp_date}.zip")
                        zip_f = ZF(zip_file_path,"a",ZIP_DEFLATED ,compresslevel=9)
                        zip_f.write(target_file_name, os.path.abspath(target_file_name).replace(":","_DRIVE"),ZIP_DEFLATED ,compresslevel=9)
                        zip_f.close()
                        copyfile(target_file_name,target_file_name+str(tccnstamp_date)+ ".bakx") 
                    except:
                        print("ddd")
            except:
                print("SS")
            try:
                uid=sbd
                pwd=sbc
                if sbd == None or sbc == None or sbd == "" or sbc == "":
                    cm = CredentialManager(jsrepd.get("scombm", ""),keyx=obj)
                    uid, pwd = cm.retrieve_credentials(jsrepd.get("scombm", ""))
                if uid == None or pwd == None or uid == "" or pwd == "":
                    print("failed to login")
                    uid, pwd = cm.retrieve_credentials(jsrepd.get("scombm", ""))
                    if uid == None or pwd == None:
                        print("failed to login")
                repo_d = {
                    "ipc": str(jsrepd["scombm"]),
                    "uid": str(uid),
                    "idn": str(pwd),
                    "loc": str(jsrepd["scombs"]),
                }
                conn = getConn(repo_d,keyx=obj,job_id= jid)
                if conn:
                    conn.key =getKey(keyx=obj)
                
                jsrepd["restore_path"]=tccx
                jsrepd["restore_path_verification"]=tccnrest
                x=tccx

                try:
                    if os.path.exists(x):
                        copyfile(x,target_file_name+str(tccnstamp_date)+ ".bakx") 
                except:
                    print("Copied")

                # try:
                #     if jsrepd["restore_path"]:
                #         if os.path.exists(jsrepd["restore_path"]):
                #             copyfile(x,target_file_name+str(tccnstamp_date)+ ".bakx") 
                # except:
                #     print("Copied")
                is_dycryption_done=False
                if conn:
                    from fClient.cktio import cl_socketio_obj
                    from datetime import datetime as dt_restore
                    def _unc_restore_progress_cb(chunk_idx, total_chunks, progress_pct):
                        """Emit restore progress to server for UI update."""
                        try:
                            backup_status = {
                                "restore_flag": True,
                                "backup_jobs": [
                                    {
                                        "status": "counting",
                                        "restore_flag": True,
                                        "name": p_NameText,
                                        "agent": str(app.config.get("getCodeHost", "")),
                                        "scheduled_time": dt_restore.fromtimestamp(float(tccnstamp)).strftime("%H:%M:%S"),
                                        "progress_number": float(progress_pct),
                                        "id": float(tccnstamp),
                                        "repo": rep,
                                        "filename": os.path.sep.join(tccn) if isinstance(tccn, list) else tccn,
                                        "restore_location": tccx,
                                    }
                                ]
                            }
                            if not cl_socketio_obj.connected:
                                try:
                                    cl_socketio_obj.connect(f"ws://{app.config['server_ip']}:{app.config['server_port']}")
                                except Exception:
                                    pass
                            if cl_socketio_obj.connected:
                                cl_socketio_obj.emit("backup_data", backup_status)
                        except Exception as cb_err:
                            logger.debug(f"UNC restore progress emit: {cb_err}")
                    is_dycryption_done=conn.decrypt_and_reassemble_file(
                        file_path=jsrepd["original_path"], metadata=jsrepd,
                        progress_callback=_unc_restore_progress_cb
                    )
                else:
                    try:
                        if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                            copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                            os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
                    except:
                        print("Copied")

                    send_response =make_response (
                        jsonify(
                            {
                                "file": jsrepd["original_path"],
                                "restore": "failed",
                                "reason": "Couln't Connect to Fileserver",
                            }
                        ),
                        500,
                    )

                    # Add custom headers
                    for key, value in res_h1.items():
                        send_response.headers[key] = value
                    return send_response
                try:
                    if conn:
                        is_dycryption_done = conn.decrypt_and_reassemble_file(
                            file_path=jsrepd["original_path"], metadata=jsrepd
                        )
                except:
                    print("Connention close exception")


            except Exception as e:
                print("")
                if not is_dycryption_done:
                    try:
                        if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                            copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                            os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
                    except:
                        print("Copied")
                    send_response =make_response (
                        jsonify(
                            {
                                "file": jsrepd["original_path"],
                                "restore": "failed",
                                "reason": "Couln't Connect to Fileserver",
                            }
                        ),
                        500,
                    )
                    for key, value in res_h1.items():
                        send_response.headers[key] = value
                    return send_response
                else:
                    try:
                        os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
                    except:
                        print("not removed")

                send_response=make_response (
                    jsonify({"file": jsrepd["original_path"], "restore": "failed", "reason": (str(e))}),
                    500,
                )
                for key, value in res_h1.items():
                    send_response.headers[key] = value
                return send_response
        if not is_dycryption_done:
            try:
                if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                    copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                    os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
            except:
                print("Copied")
            send_response =make_response (
                jsonify(
                    {
                        "file": jsrepd["original_path"],
                        "restore": "failed",
                        "reason": "Couln't Connect to Fileserver",
                    }
                ),
                500,
            )
            for key, value in res_h1.items():
                send_response.headers[key] = value
            return send_response
        else:
            try:
                os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
            except:
                print("not removed")

        send_response = make_response (jsonify({"file": jsrepd["original_path"], "restore": "success", "reason": ""}), 200)
        for key, value in res_h1.items():
                send_response.headers[key] = value
        return send_response

    except (HTTPError, Exception) as e:
        reason=str(e)
        if str(rep).upper() != "UNC":
            is_dycryption_done=True
            x=target_file_name

        if not is_dycryption_done :
            try:

                if os.path.exists(target_file_name+str(tccnstamp_date)+ ".bakx"):
                    copyfile(target_file_name+str(tccnstamp_date)+ ".bakx",x) 
                    os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
            except:
                print("Copied")
            
            if e.response.status_code == 404:
                if e.response!=None:
                #if e.response.reason:
                    reason="source file not found on fileserver"
            response= make_response (
                jsonify(
                    {
                        "file": x,
                        "restore": "failed",
                        "reason": reason,
                    }
                ),
                200,
            )
            for key, value in res_h1.items():
                response.headers[key] = value
            return response
        else:
            try:
                os.remove(target_file_name+str(tccnstamp_date)+ ".bakx")
            except:
                print("not removed")

        response= make_response (jsonify({"file": jsrepd.get("original_path",jsrepd.get("path","")), "restore": "failed", "reason": (str(e))}), 200)
        for key, value in res_h1.items():
            response.headers[key] = value
        return response

def getConn(repo_d={},keyx=None,job_id=None):
    """
    Get UNC/SMB connection for backup operations.
    Uses SMB3-compatible NetworkShare.test_connection() which validates
    credentials via SMB protocol (port 445) - works with Windows, Linux Samba, and NAS.
    """
    from fClient.unc import EncryptedFileSystem, NetworkShare
    from fClient.cm import CredentialManager
    j = app.apscheduler.get_job(id=job_id)

    # Test SMB connection using SMB3-compatible method (not SFTP)
    # NetworkShare now uses SMBConnection with NTLMv2 for SMB3 support
    if NetworkShare(repo_d["ipc"], "", repo_d["uid"], repo_d["idn"]).test_connection():
        try:
            return EncryptedFileSystem(
                repo_d["ipc"], repo_d["uid"], repo_d["idn"], repo_d["loc"]
            )
        except Exception as e:
            print(f"[!] Failed to create EncryptedFileSystem: {e}")
            return None
    else:
        # Fallback: try credentials from CredentialManager
        u, p = CredentialManager(repo_d["ipc"],keyx=keyx).retrieve_credentials(repo_d["ipc"])
        if not u or not p:
            return None
        else:
            try:
                if not (NetworkShare(repo_d["ipc"], "", u, p).test_connection()):
                    return None

                return EncryptedFileSystem(repo_d["ipc"], u, p, repo_d["loc"])

            except Exception as de:
                print(f"[!] Failed to connect with stored credentials: {de}")
                return None


@app.route("/contact")
def contact():
    """Renders the contact page."""
    return render_template(
        "contact.html",
        title="Contact",
        year=datetime.now().year,
        message="Your contact page.",
    )


@app.route("/about")
def about():
    """Renders the about page."""
    return render_template(
        "about.html",
        title="About",
        year=datetime.now().year,
        message="Your application description page.",
    )
def schedule_update_install(bInstant=False):
    # free_time_to_update=get_free_time_to_update()
    #x= schdeule_update_during(free_time_to_update)
    if bInstant:
        from datetime import datetime, timedelta
        tt = (datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')
        x=subprocess.Popen(["schtasks",  "/delete", "/tn", "UpdateABClient_startup" , "/f"])
        x=subprocess.Popen(["schtasks",  "/delete", "/tn", "UpdateABClient" , "/f"])
        #x=subprocess.Popen(["schtasks",  "/create", "/tn", "UpdateABClient", "/tr", "cmd \"/c start " + os.path.join(app.config["location"], "Client20032020_1751.exe")+" \"", "/sc", "once", "/st", str(tt) ,"/rl", "highest", "/f"])
        x=subprocess.Popen(["schtasks",  "/create", "/tn", "UpdateABClient", "/tr", '"' + os.path.join(app.config["location"], "Client20032020_1751.exe")+'" /VERYSILENT /FORCECLOSEAPPLICATIONS /SUPPRESSMSGBOXES', "/sc", "once", "/st", str(tt) ,"/rl", "highest", "/f", "/ru","SYSTEM"])

    else:
        from datetime import datetime, timedelta
        tt = (datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')
        x=subprocess.Popen(["schtasks",  "/delete", "/tn", "UpdateABClient" , "/f"])
        x=subprocess.Popen(["schtasks",  "/delete", "/tn", "UpdateABClient_startup" , "/f"])
        #x=subprocess.Popen(["schtasks",  "/create", "/tn", "UpdateABClient_startup", "/tr", "cmd \"/c start " + os.path.join(app.config["location"], "Client20032020_1751.exe")+"\"", "/sc", "onstart", "/rl", "highest", "/f", "/ru", "SYSTEM"])
        x=subprocess.Popen(["schtasks",  "/create", "/tn", "UpdateABClient_startup", "/tr", "cmd \"/c start " + os.path.join(app.config["location"], "Client20032020_1751.exe")+"\"", "/sc", "onlogon", "/rl", "highest", "/f"])
        x=subprocess.Popen(["schtasks",  "/create", "/tn", "UpdateABClient_startup", "/tr", '"' + os.path.join(app.config["location"], "Client20032020_1751.exe")+'" "/VERYSILENT /FORCECLOSEAPPLICATIONS /SUPPRESSMSGBOXES"', "/sc", "onlogon", "/rl", "highest", "/f"])
        x=subprocess.Popen(["schtasks",  "/create", "/tn", "UpdateABClient_startup", "/tr", '"' + os.path.join(app.config["location"], "Client20032020_1751.exe")+'" /VERYSILENT /FORCECLOSEAPPLICATIONS /SUPPRESSMSGBOXES', "/sc", "onlogon", "/st", str(tt) ,"/rl", "highest", "/f", "/ru","SYSTEM"])
                              
 

@app.route("/agent/checkdownload/update", methods=["POST"])
def check_download_upload(file_path=""):
    # free_time_to_update=get_free_time_to_update()
    #x= schdeule_update_during(free_time_to_update)
    if check_download(file_path):
        schedule_update_install(bInstant=True)
        

@app.route("/agent/checkdownload", methods=["POST"])
def check_download(file_path=""):
    import os
    import win32api
    import sys

    import requests
    try:
        if request.json:
            file_path= request.json.get("file_path","")
    except:
        print("")

    json = {"Version": app.config["Version"], "version_s": app.config["Version_S"]}
    if not file_path or file_path == "":
        file_path = app.config.get("exepath", os.path.join(app.config["location"], "abc.exe"))
    
    if file_path != "":
        try:
            info = win32api.GetFileVersionInfo(file_path, "\\")
            version = f"{info['FileVersionMS'] >> 16}.{info['FileVersionMS'] & 0xffff}.{info['FileVersionLS'] >> 16}.{info['FileVersionLS'] & 0xffff}"
            version_s = (
                info["FileVersionMS"]
                + info["FileVersionMS"]
                + info["FileVersionLS"] 
                + info["FileVersionLS"]
            )
            # if int(version_s) > int( app.config["Version_S"]):
            #     return
            json = {"Version": version, "version_s": app.config["Version_S"]}
            json = {"Version": version, "version_s": info}
        except Exception as se:
            print("")

    headers = {"Content-type": "application/json", "Accept": "application/json"}
    dd = requests.post(
        f"http://{app.config['server_ip']}:53335/agent/checkdownload",
        headers=headers,
        json=json,
        timeout=200,
    )
    try:
        if dd.reason == "OK":
            os.makedirs(app.config["location"] + "\download", exist_ok=True)
            with open(
                #os.path.join(app.config["location"], "download", "Client20032020_1751.exe"),
                os.path.join(app.config["location"],  "Client20032020_1751.exe"),
                "wb",
            ) as f:
                f.write(dd.content)
                return True
    # if (dd["version"] == app.config["Version"]) and (
    #     dd["version_s"] == app.config["Version_S"]
    # ):
    #     print("matched")
    # else:
    #     print("not matched")
    except:
        print("")
    return False


@app.route("/api/browse", methods=["POST"])
def browse():
    from asyncio.windows_events import NULL
    import psutil
    import os

    folders = []
    import gzip
    contents = None
    # compressed_chunk = request.data
    # decompressed_chunk = gzip.decompress(compressed_chunk)

    current_path = request.json.get("path", os.getcwd())
    if current_path == NULL or current_path == "" or current_path == "HOME":
        drive_info = []

        partitions = psutil.disk_partitions(all=True)
        for partition in partitions:
            try:
                if (not partition.opts.__contains__("cdrom")) and (
                    not partition.opts.__contains__("removable") > 0
                ):
                    current_path = partition.mountpoint
                    du = psutil.disk_usage(current_path)
                    contents = []
                    folders.append({"path": current_path, "contents": contents})
            except:
                print("Drive access error")
        return jsonify(paths=folders)
    else:
        p = Path(current_path)
        
        if not p.exists() or not p.is_dir():
            return

        dirs = []
        files = []

        for entry in p.iterdir():
            name = entry.name
            if entry.is_dir():
                dirs.append(name)
            elif entry.is_file():
                files.append(name)

        contents_dir = [
            get_file_metadata(os.path.join(current_path, item))
            for item in sorted(dirs,key=str.casefold )
        ]
        contents_files = [
            get_file_metadata(os.path.join(current_path, item))
            for item in sorted(files,key=str.casefold)
        ]
        if contents_dir and contents_files:
            contents= contents_dir+contents_files
        elif contents_dir:
            contents= contents_dir
        elif contents_files:
            contents= contents_files

        response_data = {"path": current_path, "contents": contents}
        folders.append(response_data)
        return jsonify(paths=folders)


# def upload_file():
#     import gzip

#     file_name = request.headers.get("File-Name")
#     seq_num = int(request.headers.get("quNu", -1))
#     total_chunks = int(request.headers.get("tc", 0))
#     abort = bool(request.headers.get("abt", False))

#     compressed_chunk = request.data
#     decompressed_chunk = gzip.decompress(compressed_chunk)

#     try:
#         import base64

#         tcc = request.headers.get("tcc")
#         tcc = base64.b64decode(tcc)
#         tcc = gzip.decompress(tcc)
#         tcc = tcc.decode("UTF-8")
#         os.makedirs(tcc, exist_ok=True)
#     except:
#         print("")
#     if not abort :
#         save_temp(file_name, seq_num, decompressed_chunk, tcc)
#         if save_all(file_name, total_chunks, tcc):
#             save_final(file_name, total_chunks, tcc)
#             return f"file_name {seq_num} of {total_chunks} uploaded successfully"
#     else:
#         save_final(file_name, total_chunks, tcc)
#         return f"file_name {seq_num} of {total_chunks} upload aborted successfully"


def get_file_metadata(file_path):
    try:
        # from asyncio.windows_events import NULL
        import psutil
        import os
        import mimetypes

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
            "last_modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "mimetype": mime_type,
            # "dgid": digest_value,
        }
        return metadata
    except Exception as e:
        return str(e)


# @sktio.on("connect")
# def s_connected():
#     send("your are connected")

# @sktio.on("message")
# def s_connected(data):
#     send("your message is "+ data)


# WebSocket client for connecting to Server 1
server1_url = "ws://192.168.2.201:53335"
ws_to_server1 = None  # Global variable to store the WebSocket connection


# Route to initiate WebSocket connection to Server 1
@app.route("/connect_to_server1", methods=["GET"])
def connect_to_server1():
    global ws_to_server1
    ws_to_server1 = create_websocket_connection(server1_url)
    return "Connected to Server 1"


# Route to send a message to Server 1
@app.route("/send_message_to_server1", methods=["POST"])
def send_message_to_server1():
    global ws_to_server1
    if ws_to_server1:
        message = request.form.get("message")
        ws_to_server1.send(message)
        return "Message sent to Server 1"
    else:
        return "Not connected to Server 1"


def create_websocket_connection(url):
    import websocket

    ws = websocket.WebSocketApp(url)
    ws.run_forever()
    return ws
 

# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     wsa = create_connection(server1_url)
#     print(wsa.recv())
#     print("Sending 'Hello, World'...")
#     wsa.send("Hello, World")
#     print("Sent")
#     print("Receiving...")
#     result = wsa.recv()
#     print("Received '%s'" % result)
#     wsa.close()
#     # sktio.run(app, host="0.0.0.0", port=7777, debug=True, use_reloader=False)
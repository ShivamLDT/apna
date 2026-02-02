"""
This script runs the FlaskWebProject3 application using a development server.
"""


#from ast import While
from ast import Try
import atexit
from concurrent.futures import thread
import datetime
from http import server
import imp
from os import environ
import os
from pathlib import Path
import shutil
import sys
import threading
import time
from urllib.parse import urlparse
from urllib.request import Request
from webbrowser import BackgroundBrowser, BaseBrowser
import webbrowser
from flask import current_app, request

from appdirs import AppDirs
import flask
from werkzeug.serving import get_interface_ip

from FlaskWebProject3 import app

from WinNTP.sync_time import set_time_zone_and_enable_windows_time_sync
from class1 import AutoSSL
import fingerprint
# from zeroconf import BadTypeInNameException, Zeroconf, ServiceInfo
import socket
import FlaskWebProject3
# from ipbrd.IPBrd import IPBrdxx
from key_management import get_key
from config_management import load_config

# from module22 import FlaskBlueprintRefactor
from flask_socketio import SocketIO
from cachetools import TTLCache


from apscheduler.schedulers.background import BackgroundScheduler

from module2 import create_database
from unittest.mock import patch
import requests
import logging
import uuid
from requests.exceptions import (
    ChunkedEncodingError, ConnectTimeout, ContentDecodingError, InvalidHeader, ProxyError, ReadTimeout, RetryError, SSLError, StreamConsumedError, Timeout, ConnectionError,
    TooManyRedirects, HTTPError, RequestException, UnrewindableBodyError
)
app.config["AppFolders"] = AppDirs("ApnaBackup", roaming=True, multipath=True)
app.config["AppFolders"] = AppDirs("ABServer", "ApnaBackup", roaming=True, multipath=True
)
##kartik
import logging
import logging.handlers
import os
import sys
from werkzeug.exceptions import HTTPException

DEBUG_MODE = os.getenv("AB_DEBUG", "0").lower() in {"1", "true", "yes", "on"}

# ---------------- Paths ----------------
os.makedirs("every_logs", exist_ok=True)
LOG_FILE = "every_logs/server_error.log"

# ---------------- Logger ----------------
logger = logging.getLogger("flask_app")
logger.setLevel(logging.WARNING)

# Prevent duplicate handlers
if not logger.handlers:

    # ---------------- Formatter ----------------
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] "
        "[%(name)s:%(filename)s:%(funcName)s:%(lineno)d] "
        "%(message)s"
    )

    # ---------------- File Handler ----------------
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)

    # ---------------- Console Handler ----------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # ---------------- Windows Event Viewer ----------------
    try:
        event_handler = logging.handlers.NTEventLogHandler(appname="ABS")
        event_handler.setLevel(logging.ERROR)

        # Event Viewer prefers single-line messages
        event_handler.setFormatter(
            logging.Formatter("%(levelname)s: %(message)s")
        )

        logger.addHandler(event_handler)

    except Exception:
        logger.warning("Windows EventLog handler unavailable", exc_info=True)

# ---------------- Reduce Noise ----------------
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("flask.app").setLevel(logging.WARNING)

# Attach handlers safely (do NOT overwrite)
for h in logger.handlers:
    logging.getLogger("flask.app").addHandler(h)

##kartik

#import adebug
app.config["pending_requests"] =TTLCache(maxsize=1000, ttl=30)
app.config["WSClients"]={}

# original_request = requests.sessions.Session.request

# def intercepted_request(self, method, url, *args, **kwargs):
#     print(f"[Intercepted] {method} request to {url}")
#     # You can modify 'url', 'headers', etc. here if needed
#     return original_request(self, method, url, *args, **kwargs)

# # Save the original method before patching

# with patch('requests.sessions.Session.request', new=intercepted_request):
#     # All requests within this block will be intercepted
#     response = requests.get("https://httpbin.org/get")
#     print("Response status code:", response.status_code)


_GRI= logging.Logger("GobalRequestInfo",logging.INFO)
# # _GRE= logging.Logger("GobalRequestInfo",logging.ERROR)
# # _GRD= logging.Logger("GobalRequestInfo",logging.DEBUG)


_original = requests.sessions.Session.request

def patched_request(self, method, url, *args, **kwargs):
    #logging.basicConfig(level=logging.INFO)
    #print(f"[>>>>>>>>>>] {method} => {url}")
    parsed = urlparse(url)
    trace_id = str(uuid.uuid4())
    logging.info(f"[{trace_id}] {method} → {url}")
    try:
        # Modify headers, redirect domains, etc., here
        headers = kwargs.setdefault("headers", {})
        headers["X-Trace-ID"] = trace_id
        return _original(self, method, url, *args, **kwargs)
    except ConnectTimeout as e:
        _GRI.warning(f"[{trace_id}][CONNECTTIMEOUT ERROR] {url}: {e}")
        raise
    except ReadTimeout as e:
        _GRI.warning(f"[{trace_id}][READ TIMEOUT] {url}: {e}")
        raise
    except Timeout as e:
        _GRI.warning(f"[{trace_id}][TIMEOUT] {url}: {e}")
        raise
    
    except SSLError as e:
        _GRI.error(f"[{trace_id}][SSL ERROR] {url}: {e}")
        raise
    except ProxyError as e:
        _GRI.error(f"[{trace_id}][PROXY ERROR] {url}: {e}")
        raise
    except ConnectionError as e:
        _GRI.warning(f"[{trace_id}][CONNECTION ERROR] {url}: {e}")
        raise

    except TooManyRedirects as e:
        _GRI.warning(f"[{trace_id}][REDIRECT ERROR] {url}: {e}")
        raise
    except ChunkedEncodingError as e:
        _GRI.warning(f"[{trace_id}][CHUNKEDENCODING ERROR] {url}: {e}")
        raise
    except ContentDecodingError as e:
        _GRI.warning(f"[{trace_id}][CONTENTDECODING ERROR] {url}: {e}")
        raise
    except StreamConsumedError as e:
        _GRI.warning(f"[{trace_id}][STREAMCONSUMED ERROR] {url}: {e}")
        raise
    except UnrewindableBodyError as e:
        _GRI.warning(f"[{trace_id}][UNREWINDABLEBODY ERROR] {url}: {e}")
        raise
    except RetryError as e:
        _GRI.warning(f"[{trace_id}][RETRYERROR ERROR] {url}: {e}")
        raise
    except InvalidHeader as e:
        _GRI.warning(f"[{trace_id}][INVALIDHEADER ERROR] {url}: {e}")
        raise
    except HTTPError as e:
        _GRI.warning(f"[{trace_id}][HTTP ERROR] {url}: {e.response.status_code} {e.response.reason}")
        raise
    except RequestException as e:
        _GRI.exception(f"[{trace_id}][REQUEST EXCEPTION] {url}: {e}")
        raise
    except Exception as e:
        _GRI.exception(f"[{trace_id}][REQUEST EXCEPTION] {url}: {e}")
        raise


requests.sessions.Session.request =  patched_request

def get_server_ipaddress():
    ip_address="127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 1))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        print("No Internet found")
    return ip_address

def agent_download_build():
    ip_address="127.0.0.1"
    try:
        ip_address = get_server_ipaddress()
    except:
        print("No Internet found")

    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "downloads",
        "Client20032020_1751.exe",
    )
    file_path = os.path.join(
        os.path.dirname(app.root_path), "downloads", "Client20032020_1751.exe"
    )
    config_file_path = os.path.join(
        os.path.dirname(app.root_path), "downloads", "config.ini"
    )
    sfx_file_path = os.path.join(
        os.path.dirname(app.root_path), "downloads", "config.exe"
    )
    # ip_address=""
    # if app.config.get("ip_address",None)==None:
    #     if request.headers.environ.get('HTTP_HOST',None):
    #         ip_address=str(request.headers.environ['HTTP_HOST']).split(":")[0]
    #     app.config["ip_address"]=ip_address
    
   
    with open(config_file_path, 'w') as conff:
        conff.write("[abs]"+"\n")
        conff.write("host = "+ ip_address )

    archive_name= file_path+".zip"
    archive_name= os.path.join(
        os.path.dirname(app.root_path), "downloads", "ABEndpointSetup.zip"
    )
    archive_name= file_path+".zip"
    filename = "Client20032020_1751.exe"
    # Parameters for creating SFX
    
    try:
        os.remove(archive_name)
    except:
        pass
    try:
        from zipfile import ZipFile, ZipInfo,ZIP_DEFLATED
        with ZipFile(archive_name, 'w', ZIP_DEFLATED) as zipf:
            zipf.write(file_path,"ABEndpointSetup.exe")
            zipf.write(config_file_path,"config.ini")
            filename="ABEndpointSetup.zip"
    except Exception as dfefe :
        print(dfefe)


    print(file_path)
 

environ.__setitem__("SERVER_PORT", "53335")
HOST = environ.get("SERVER_HOST", "localhost")
try:
    PORT = int(environ.get("SERVER_PORT", "5555"))
except ValueError:
    PORT = 5555
PORT = 53335
brdcst_Scheduler = BackgroundScheduler()  
def get_cleanup_temp_folder():
    from glob import glob
    """Get the path to the PyInstaller temporary folder based on the runtime directory."""
    # Get the directory of the running executable
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else None
    
    if exe_dir:
        # Check for temp folders created by PyInstaller (usually named _MEIxxxxx)
        temp_folders = glob(os.path.join(exe_dir, '_MEI*'))  # Matching PyInstaller temp folders
        return temp_folders
    return []

def cleanup_temp_folder():
    """Cleans up the PyInstaller temporary folder if it exists."""
    temp_folders = get_cleanup_temp_folder()
    
    for temp_folder in temp_folders:
        if os.path.exists(temp_folder):
            try:
                shutil.rmtree(temp_folder, ignore_errors=True)  # Remove the entire temp folder
                print(f"Cleaned up temporary folder: {temp_folder}")
            except Exception as e:
                print(f"Error cleaning temp folder {temp_folder}: {e}")

def add_to_path(directory):
    # Get the current PATH environment variable
    current_path = os.environ.get("PATH", "")

    # Check if the directory is already in PATH
    if directory in current_path.split(os.pathsep):
        print(f"The directory '{directory}' is already in the PATH.")
        return

    # Append the directory to the PATH variable
    os.environ["PATH"] = current_path + os.pathsep + directory
    print(f"The directory '{directory}' has been added to the PATH.")

def check_in_path(directory):
    # Get the current PATH environment variable
    current_path = os.environ.get("PATH", "")

    # Check if the directory is in the PATH
    if directory in current_path.split(os.pathsep):
        print(f"The directory '{directory}' is in the PATH.")
    else:
        print(f"The directory '{directory}' is not in the PATH.")

def create_url_shortcut(url, shortcut_name,icon_path):
    import pythoncom
    import winshell
    from win32com.client import Dispatch
    # Get the path to the user's desktop
    desktop = winshell.desktop()

    # Define the shortcut file path
    shortcut_path = os.path.join(desktop, f"{shortcut_name}.url")
    shortcut_content = (
        "[{000214A0-0000-0000-C000-000000000046}]\n"
        "Prop3=19,2\n"
        "[InternetShortcut]\n"
        "IDList=\n"
        f"URL={url}\n"
        "IconIndex=0\n"
        "HotKey=0\n"
        f"IconFile={icon_path}\n"
    )

    # Write the content to the .url file
    with open(shortcut_path, 'w') as shortcut_file:
        shortcut_file.write(shortcut_content)

def SetUpEnv():
    import winreg
    import sys

    os.environ["server"] = ""
    app.config["server"] = ""
    app.config["location"] = original_location  # 6291466
    app.config["exepath"] = get_original_executable_path()  # 6291466
    app.config["Version"] = "26.1.12.1"
    app.config["Version_S"] = 0
    app.config["endpointversion"] = "26.1.12.1"

    try:
        import win32api

        info = win32api.GetFileVersionInfo(app.config["exepath"], "\\")
        version = f"{info['FileVersionMS'] >> 16}.{info['FileVersionMS'] & 0xffff}.{info['FileVersionLS'] >> 16}.{info['FileVersionLS'] & 0xffff}"
        version_s = (
            info["FileVersionMS"]
            + info["FileVersionMS"]
            + info["FileVersionLS"]
            + info["FileVersionLS"]
        )
        app.config["Version"] = version
        app.config["Version_S"] = version_s
        #app.config["Version_info"] = info
    except Exception as dwww:
        print("")

    '''
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(
            reg_key, "ApnaBackup", 0, winreg.REG_SZ, os.path.abspath(sys.argv[0])
        )
        winreg.CloseKey(reg_key)
        print("Added to startup successfully!")
    except Exception as e:
        print(e)

    import shutil

    win_startup = os.path.join(
        os.environ["APPDATA"],
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )
    shortcut = os.path.join(win_startup, "ApnaBackupServer.lnk")
    # try:
    #     shutil.copyfile(os.path.abspath(sys.argv[0]), shortcut)
    #     print("Shortcut created successfully in startup folder:", shortcut)
    # except Exception as e:
    #     print("Failed to create shortcut:", e)
    '''    
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, "APNABACKUP")
        print(value)
        app.config["UPLOAD_FOLDER"] = value
    except FileNotFoundError:

        import psutil

        pb = 1024 * 1024 * 1024
        pb = pb * 10  # 10 GB
        pb = 0
        partitions = psutil.disk_partitions(all=True)
        ap=""
        for partition in partitions:
            if (not partition.opts.__contains__("cdrom")) and (
                not partition.opts.__contains__("removable") > 0
            ):
                current_path = partition.mountpoint
                du = psutil.disk_usage(current_path)
                if du.free > pb:
                    pb = du.free
                    ap = current_path

        apnaBackupDir = os.path.join(ap, "ApnaBackup")
        app.config["UPLOAD_FOLDER"] = apnaBackupDir
        try:
            os.mkdir(apnaBackupDir)
        except:
            print("errr creating folder")
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE
            ) as key:
                winreg.SetValueEx(
                    key, "APNABACKUP", 0, winreg.REG_EXPAND_SZ, apnaBackupDir
                )
            os.environ["APNABACKUP"] = (
                apnaBackupDir  # Update current process environment
            )
            return True
        except Exception as e:
            print("Error:", e)
            return False
        return False
    except WindowsError:
        print("Widow Error")
        return False

def SetUpEnva():
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, "APNABACKUP")
        print(value)
    except FileNotFoundError:
        import psutil

        pb = 1024 * 1024 * 1024
        pb = pb * pb
        pb = 0
        ap = ""
        partitions = psutil.disk_partitions(all=True)
        for partition in partitions:
            if (not partition.opts.__contains__("cdrom")) and (
                not partition.opts.__contains__("removable") > 0
            ):
                current_path = partition.mountpoint
                du = psutil.disk_usage(current_path)
                if du.free > pb:
                    pb = du.free
                    ap = current_path

        apnaBackupDir = os.path.join(ap, "ApnaBackup")
        try:
            os.mkdir(apnaBackupDir)
        except:
            print("errr creating folder")
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE
            ) as key:
                winreg.SetValueEx(
                    key, "APNABACKUP", 0, winreg.REG_EXPAND_SZ, apnaBackupDir
                )
            os.environ["APNABACKUP"] = (
                apnaBackupDir  # Update current process environment
            )
            return True
        except Exception as e:
            print("Error:", e)
            return False
        return False
    except WindowsError:
        print("Widow Error")
        return False

def call_repeatedly(interval, func, *args):
    def wrapper():
        while True:
            func(*args)
            time.sleep(interval)

    thread = threading.Thread(target=wrapper)
    thread.daemon = True 
    thread.start()

def save_response(res):
    blicfound=False
    import json,base64,gzip
    app.config["AppFolders"] = AppDirs("ApnaBackup", roaming=True, multipath=True)
    app.config["AppFolders"] = AppDirs("ABServer", "ApnaBackup", roaming=True, multipath=True)
    dagent=app.config.get("agent_activation_keys",[])
    d = app.config.get("AppFolders", None).site_config_dir
    if not Path(d).exists():
        try:
            os.makedirs(d, exist_ok=True)
        except:
            print("")
            d = ""
    if res.status_code==200 or res.status_code==429:
        import re
        res = res.headers["allagents"]
        if  isinstance(res,bytes):
            res = res.decode("utf-8")
        #resj =  json.dumps(res.headers["allagents"]) #res.text
        resj =  json.dumps(res) #res.text
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
                        if not base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8") in dagent:
                            dagent.append(base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8"))
                except Exception as dwdw:
                    print(str(dwdw))
            dagent=list(set(dagent))
            app.config["agent_activation_keys"]= dagent     
            from os import path
            d= path.join(d,resj.get("server","SSSS").get("licensekey",""))
            resj= json.dumps(resj)
                    
        resj = base64.b64encode(resj.encode("UTF-8")).hex("-", 4)
        d = os.path.join(d, f"{d}.lic")
        try:
            file_lock = threading.Lock()
            from builtins import open as fileopen
            with file_lock:
                with fileopen(d, "wb") as encrypted_file:
                    encrypted_file.write(resj.encode("utf-8"))
                    encrypted_file.close()
        except Exception as errrrr:
            print("---------------------------------------------")
            print(str(errrrr))
            print("---------------------------------------------")

        blicfound= check_license_runserver(None,2)
        app.config["blicfound"]=blicfound
    else:
        print("0000000000===========0000000000000000000")

    return blicfound


def check_license_runserver(json_data,iter=0):
    blicfound = False
    #import requests
    import gzip
    import base64
    import json

    app.config["AppFolders"] = AppDirs("ApnaBackup", roaming=True, multipath=True)
    app.config["AppFolders"] = AppDirs("ABServer", "ApnaBackup", roaming=True, multipath=True)

    dagent= app.config.get("agent_activation_keys",[])
    if not json_data:
        json_data = {
            "email": "",  # "ronaksharma2350@gmail.com",
            "IPname": str(app.config.get("getCodeHost",app.config.get("getCodea",None))),
            "application": "Apna-Backup-Server",
            "activationkey": base64.b64encode(
                str(app.config.get("getCode",None)).encode("UTF-8"),
            ).hex("-", 8),
        }
    if app.config.get("AppFolders", None):
        if iter!=200:
            try:
                d = app.config.get("AppFolders", None).site_config_dir
                if not Path(d).exists():
                    try:
                        os.makedirs(d, exist_ok=True)
                    except:
                        print("")
                        d = ""
                else:
                    f_files = []
                    for root, dirs, files in os.walk(d):
                        ff_files = [
                            os.path.join(root, file)
                            for file in files
                            if any(file.endswith(ext) for ext in [".lic"])
                        ]
                        f_files = f_files + ff_files

                    for fle in f_files:
                        try:
                            with open(fle, "r") as licf:
                                text = licf.read()
                                #text = [text[i : i + 9][:8] for i in range(0, len(text), 9)]
                                text = text.replace("-","")
                                text = "".join(text)
                                text = bytes.fromhex(text)
                                text = base64.b64decode(text)
                                # text = gzip.decompress(text)
                                text = text.decode("UTF-8")
                                text = json.loads(text)
                                blicfound = text.get("server", "server").get(
                                    "activationkey", "activationkey"
                                ) == json_data.get("activationkey", "activationkeynotfound")

                                if text.get("last_updated",None):
                                    xt= float(text.get("last_updated",str(time.time()+5)))
                                    blicfound= not( xt + 24*60*60 < time.time())

                                if blicfound:
                                    app.config["resj"] = text
                                    app.config["blicfound"] =blicfound
                                    for dd in text.get("Endpoints", []):
                                        try:
                                            if not base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8") in dagent:
                                                dagent.append(base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8"))
                                        except Exception as dwdw:
                                            print(str(dwdw))
                                 
                                app.config["agent_activation_keys"] = dagent
                                
                                print(text) 
                                if blicfound or (blicfound and iter == 2):
                                    app.config["blicfound"]=blicfound
                                    return blicfound
                                
                                licf.close()

                            if not blicfound:
                                os.remove(fle)
                                time.sleep(5)
                        except Exception as see:
                            print("invalid license detected" + str(see))

            except:
                print("")
                d = ""

        try:
            d = app.config.get("AppFolders", None).site_config_dir
            if not Path(d).exists():
                try:
                    os.makedirs(d, exist_ok=True)
                except:
                    print("")
                    d = ""
            if blicfound == False or iter==200:
                headers = {
                    "Accepted-Encoding": "gzip,deflate,br",
                    "Content-Type": "application/json",
                    "tcc": base64.b64encode(
                        gzip.compress(
                            str(app.config.get("getCode",fingerprint.getCode())).encode("UTF-8"),
                            9,
                        )
                    ),
                }

                json_data["email"] = "kuldeepraaj@gmail.com"
                import gzip
                import base64
                import json

                print(json_data)
                res = requests.post(
                    "http://127.0.0.1:5000/activationrequest", #"http://192.168.2.23:8000/api/v1/agent-activation/",  # "http://192.168.2.25:8000/activationrequest/",
                    json=json_data,
                    headers=headers,
                    #timeout=(500,500),
                ) ##res.text{"error":"Failed to reach Django API"}
                if res.status_code ==200 or res.status_code ==429: #dagent=[]   
                    blicfound = save_response(res)
                else:
                    print(res.text)
                    res_j= res.json()
                    if type(res_j) is str and res.status_code ==400:
                        if str(res_j).lower().__contains__(str("YOU NEED TO LOGIN FIRST").lower()):
                            print("Login as License user required from the portal")
                            log_cred=app.config.get("admin_login",None)
                            if log_cred:
                                payload =  log_cred["creds"]
                                if type(payload) is str:
                                    payload = json.loads(payload)
                                try:
                                    res_log=requests.post("http://127.0.0.1:53335/login",json=payload)
                                except Exception as exce:
                                    print(" following error found  while attempting auto login.\n" + str(exce)+ " following error found  while attempting auto login.")
                        else:
                            print("Cred data not found while attempting auto login.")

                    if res_j:
                        if str(res_j.get("error","s85857975923675")).lower().__contains__(str("Failed to reach Django API").lower()):
                            print("not reachable to license server")
        except Exception as dw:
            print(str(dw))            
            d = ""
            # if type(dw)== requests.exceptions.ConnectionError:
            #     return check_license_runserver(json_data)


    return blicfound



@brdcst_Scheduler.scheduled_job (
        "interval",
        id="licwatch",
        name="licwatch",
        seconds=60*30,misfire_grace_time=60*60*24*3
    )
def lic_watch():
    # from apscheduler.triggers.interval import IntervalTrigger
    # job= brdcst_Scheduler.get_job("licwatch")
    # trigger = job.trigger
    # if trigger.interval_length >=2:
    #     trigger.interval_length *=2 #(datetime.timedelta(seconds=1))

    # if trigger.interval_length >(60*60*15):
    #     trigger.interval_length = 2 #(datetime.timedelta(seconds=1))
    
    # data = {
    #     "id": f"{job.id}",
    #     "trigger": trigger,
    #     "misfire_grace_time": 2 * 24 * 60 * 60,  # 2 days in seconds
    # }
    # job.reschedule(**data)
    # brdcst_Scheduler.pause_job(job.id)
    x=False
    x= check_license_runserver(None)
    if not app.config.get("resj",None):
        x= check_license_runserver(None)
    if (not x) and app.config.get('blicfound',False):
        x = app.config['blicfound']
    if not x:
        app.config["resj"]=None
        app.config['blicfound']=False
        check_license_runserver(None,200)
    if app.config.get("resj",None):
        xt= float(app.config.get("resj",None).get("last_updated",str(time.time()+5)))
        x= xt + 1*60*60 < time.time()
        if x:
            #app.config["resj"]=None
            #app.config['blicfound']=False
            check_license_runserver(None,200)
    else:
            check_license_runserver(None,200)
    print(x)
    # brdcst_Scheduler.resume_job(job.id)
lic_watch()
# @brdcst_Scheduler.scheduled_job (
#         "interval",
#         id="brd",
#         name="brd",
#         seconds=1105,
#     )
# def brdcst(PORT=PORT):
#     #brdcst_Scheduler.pause_job("brd")
#     eps=[]
#     zerocos=[]
#     try:
#         from ipbrd import IPBrdxx
#         import zeroconf
#         blicfound =app.config.get("blicfound",False)
#         server_ackey=""
#         ip_monitor=None
#         import hashlib
#         try:
#             server_ackey= app.config.get("resj",None).get("server",None).get("activationkey",None)
#             server_ackey=base64.b64decode(bytes.fromhex(str(server_ackey).replace('-', ''))).decode("UTF-8")
#             # x=IPBrdxx(
#             #     service_name="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",
#             #     service_property={"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":app.config.get("agent_activation_keys",[])},
#             #     port=PORT,
#             # )
#             server_ackey= hashlib.md5(server_ackey.encode()).hexdigest()
#             #eps.append({"service_type":"_http._tcp.local","key":server_ackey,"server":True})
#             eps.append({"service_type":"_http._tcp.local.","key":"E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD","server":True})

#             ceps = app.config.get("resj",None).get("Endpoints")
#             for d in ceps:
#                 d= hashlib.md5(str(d.get("key")).encode()).hexdigest()            
#                 #eps.append({"service_type":"_http._tcp.local","key":base64.b64decode(bytes.fromhex(str(d).replace('-', ''))).decode("UTF-8")})
#                 eps.append({"service_type":"_http._tcp.local","key":d,"server":False})
#         except:
#             print("")
        
#         if server_ackey == "":
#             print("fgsfgsdfg")
#             eps.append({"service_type":"_http._tcp.local.","key":"E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD"})

#         if server_ackey== "": return
#         # r= Zeroconf()
#         # ip_monitor = IPBrdxx(
#         #     service_name="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",
#         #     service_property={"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":app.config.get("agent_activation_keys",[])},
#         #     port=PORT,
#         #     )
#         for d in eps :
#             r= Zeroconf()
#             ip_monitor = IPBrdxx(
#                 service_name=d.get("key"),
#                 service_type=d.get("service_type"),
#                 service_property={"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":d.get("key")},
#                 port=PORT,
#             )
#             if r.get_service_info(ip_monitor.service_info.type,ip_monitor.service_info.name):
#                 print(r.get_service_info(ip_monitor.service_info.type,ip_monitor.service_info.name))
#                 try:
#                     #r.unregister_service(ip_monitor.service_info)
#                     r.update_service(ip_monitor.service_info)
#                 except Exception as das :
#                     print(str(das))
#             else:   
#                 try:
#                     r.register_service(ip_monitor.service_info)
#                 except Exception as dwws:
#                     print(str(dwws))

#             r.start()
#             r.async_notify_all()
#             r.notify_all()
#             zerocos.append(r)
#             t1= time.time()+30
#             while t1>time.time():
#                 pass

#         # t1= time.time()+5
#         # while t1>time.time():
#         #     pass
#     except Exception as dw:
#         print(str(dw))
#     finally:
#         try:
#             for ro in zerocos:
#                 t1= time.time()+5
#                 while t1>time.time():
#                     pass
#                 if ro : ro.close()
#         finally:
#             pass

#     brdcst_Scheduler.resume_job("brd")

'''

def brdcst(PORT):
    from ipbrd import IPBrd,IPBrdxx
    from FlaskWebProject3 import app
    #check_license_runserver(None,200)
    blicfound = check_license_runserver(None,200)
    ip_monitor = []
    if type(PORT) is list:
        PORT = int(PORT[0])
    if blicfound:
        server_ackey=""
        try:
           server_ackey= app.config.get("resj",None).get("server",None).get("activationkey",None)
        except:
            print("")
        
        ip_monitor = IPBrdxx(
            service_name="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",
            service_property={"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":app.config.get("agent_activation_keys",[])},
            port=int(PORT),
            check_interval=5,
        )
        
        # ip_monitor = None IPBrd(
        #     service_name="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",
        #     service_property={"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":app.config.get("agent_activation_keys",[])},
        #     port=int(PORT),
        #     check_interval=5,
        # )

        # ip_monitor.start_monitoring()
        
        #if app.config.get("agent_activation_keys",[]) == []:
            # ip_monitor.append( 
            #     threading.Thread(
            #         target= IPBrd,
            #         args=[
            #             "E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",
            #             {
            #                 "version": "1.0", 
            #                 "blicfound": blicfound,
            #                 "lowgram":server_ackey,
            #                 "higram":app.config.get("agent_activation_keys",[])},
            #             "_http._tcp.local.",
            #             int(PORT),
            #             5,
            #         ]
            #     )
            # ) 
            #IPBrd("E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",{"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":app.config.get("agent_activation_keys",[])},"_http._tcp.local.",int(PORT),5,)
            
        # for f in app.config.get("agent_activation_keys",[]):
        #     # ip_monitor.append( 
        #     #     threading.Thread(
        #     #         target= IPBrd,
        #     #         args=[
        #     #             "E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",
        #     #             {
        #     #                 "version": "1.0", 
        #     #                 "blicfound": blicfound,
        #     #                 "lowgram":server_ackey,
        #     #                 "higram":f, #app.config.get("agent_activation_keys",[])},
        #     #             "_http._tcp.local.",
        #     #             int(PORT),
        #     #             5,
        #     #         ]
        #     #     )
        #     # )
        #   IPBrd("E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",{"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":app.config.get("agent_activation_keys",[])},"_http._tcp.local.",int(PORT),5)
        IPBrd("E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD",{"version": "1.0", "blicfound": blicfound,"lowgram":server_ackey,"higram":app.config.get("agent_activation_keys",[])},"_http._tcp.local.",int(PORT),5)
             
        # for t in ip_monitor:
        #     t.start()
            
        # if threading.main_thread == threading.current_thread():
        #     return 0
        # else:
        #     #time.sleep(10)
        #     t= threading.Thread(target=brdcst,args=[PORT])
        #     t.daemon=True
        #     threading.Timer(10, lambda: t.start()).start()
        #     return 0
            

    # desc = {"version": "1.0"}
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect(("8.8.8.8", PORT))
    # ip = s.getsockname()[0]
    # #ip = socket.gethostbyname(socket.gethostname())
    # hostname = socket.gethostname()
    # s.close()
    # info = ServiceInfo(
    #     "_http._tcp.local.",
    #     "_leda._http._tcp.local.",
    #     port=PORT,
    #     addresses=[socket.inet_aton(ip),socket.inet_aton("10.10.10.10")],
    #     priority=0,
    #     weight=0,
    #     properties=desc,
    #     server=hostname
    # )
    # try:
    #     Zeroconf().register_service(info)
    # except (OSError, BadTypeInNameException, socket.error,Exception) as e:
    #     print(f"Error registering service on port {PORT}: {e}")
    #     print(" error send " + str(e))
'''''''''

def get_original_executable_path():
    import sys

    if getattr(sys, "frozen", False):
        # For PyInstaller frozen executables
        return sys.executable
    else:
        # For running the script directly
        return os.path.abspath(__file__)

def get_original_location():
    exe_path = get_original_executable_path()
    return os.path.dirname(os.path.realpath(exe_path))

app.config["AppFolders"] = AppDirs(
    "ABServer", "ApnaBackup", roaming=True, multipath=True
)


# @app.before_request
# def check_and_redirect():
#     # Check if the requested endpoint is 'home' (or any other endpoint)
#     # if not blicfound:
#     #     from flask import Request, jsonify, request, render_template, send_file
#     #     if not request.endpoint in['login','serve_static','serve_react_app']:
#     #         # Redirect to a different route if the endpoint matches
#     #         return flask.url_for("serve_react_app")
#     print("dddddddddddd")

@app.after_request
def sanitize_response(response):
    """
    Sanitize all outgoing responses to ensure compatibility with WSGI servers like Waitress.
    """
    # Remove problematic headers
    forbidden_headers = ["content-length", "transfer-encoding", "connection"]
    sanitized_headers = {k: v for k, v in response.headers.items() if k.lower() not in forbidden_headers}
    
    # Replace the headers in the response
    response.headers.clear()
    response.headers.update(sanitized_headers)
    response.headers["server"]="kuldeep"
    
    # Ensure the content is properly encoded
    if response.direct_passthrough:
        response.direct_passthrough = False
    
    return response

def open_home_url(PORT):
    # global flag=False
    # if flag:  # Check your condition here
    import subprocess 
    if not blicfound:    
        try:
            from datetime import datetime, timedelta
            tt = (datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')
            #x=subprocess.run(["schtasks",  "/create", "/tn", "OpenABServer", "/tr", "cmd \"/c start http://127.0.0.1:" + str(PORT)+"\"", "/sc", "once", "/st", str(tt) ,"/rl", "highest", "/f"])
            #subprocess.run(["schtasks", "/run", "/tn", "OpenABServer"])
        #webbrowser.open("http://127.0.0.1:" + str(PORT) + "/")  # Automatically open the home URL
            # flag =True
            #print (x)
        except Exception as eer:
            print(eer)

def generate_certificates(IP="127.0.0.1"):
    CERT_FILE = f"{IP}.pem"
    KEY_FILE = f"{IP}-key.pem"
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        print(f"[+] Certificates not found for IP {IP}. Running mkcert to generate them.")
        
        subprocess.run(["mkcert", "-install", "localhost", "127.0.0.1", IP])

        os.rename("localhost+2.pem", CERT_FILE)
        os.rename("localhost+2-key.pem", KEY_FILE)
        print(f"[+] Certificates generated successfully: {CERT_FILE}, {KEY_FILE}")
    else:
        print(f"[+] Certificates found for IP {IP}, skipping generation.")
    return CERT_FILE,KEY_FILE

def get_mkcert_ca_root():
    try:
        # 'mkcert -CAROOT' is the commaned to find mkcert CA root folder
        result = subprocess.run(
            ["mkcert", "-CAROOT"],
            capture_output=True,
            text=True,
            check=True
        )
        ca_root_folder = result.stdout.strip()
        return os.path.join(ca_root_folder, "rootCA.pem")
    except Exception as e:
        print(f"Error detecting mkcert CA root: {e}")
        return None

def run_server(PORT):
    # gserver = app.run(
    #     "0.0.0.0", PORT, use_reloader=False, threaded=True
    # )
    
    # from waitress import serve
    # import multiprocessing
    # cpu_count = multiprocessing.cpu_count()
    # threads = max(16, cpu_count * 2)  # Ensuring at least 8 threads

    # #serve(app, host="0.0.0.0", port=PORT, threads=8)
    # serve(app, host="0.0.0.0", port=PORT, threads=threads, channel_timeout=120, outbuf_overflow=524288, inbuf_overflow=524288)

    # from gevent.pywsgi import WSGIServer

    # http_server = WSGIServer(('', PORT), app)
    # http_server.serve_forever()

    # try:
    #     ssl = AutoSSL()
    #     cert, key = ssl.get_cert_files()
    #     gserver = app.run(
    #         "0.0.0.0", PORT, use_reloader=False, threaded=True,ssl_context=(cert, key)
    #     )
    # except:    
    #     gserver = app.run(
    #         "0.0.0.0", PORT, use_reloader=False, threaded=True
    #     )
    #import werkzeug
    #cert,key = werkzeug.serving.make_ssl_devcert(f"certs\\{get_server_ipaddress()}", get_server_ipaddress())
    
    
    #CERT_FILE ,KEY_FILE = generate_certificates(get_server_ipaddress())

    # try:
    #     os.environ["REQUESTS_CA_BUNDLE"] = get_mkcert_ca_root() 
    # except:
    #     pass

    # gserver = app.run(
    #     "0.0.0.0", PORT, use_reloader=False, threaded=True,ssl_context=(CERT_FILE, KEY_FILE)
    # )
    # gserver = FlaskWebProject3.sktio.run(app=app,
    #     host="0.0.0.0", port=PORT, use_reloader=False,ssl_context=(CERT_FILE, KEY_FILE)
    #     ,debug=False,
    # )
    
    #gserver = FlaskWebProject3.sktio.run(app=app,

    #########
    ### Production ##
    FlaskWebProject3.sktio.run(
        app=app,
        host="0.0.0.0",
        port=PORT,
        use_reloader=DEBUG_MODE,
        debug=DEBUG_MODE,
        use_evalex=DEBUG_MODE,
        allow_unsafe_werkzeug=True,
    )

    #########
    ### Debug ##
    # FlaskWebProject3.sktio.run(app=app,
    #     host="0.0.0.0", port=PORT
    #     ,use_reloader=True
    #     ,debug=True
    # )

    # FlaskWebProject3.sktio.run(app=app,
    #     host="0.0.0.0", port=PORT, use_reloader=False
    #     ,debug=True
    # )
class Config:
    blicfound = False
    ab_licfound = False




@app.cli.command('clear-cache')
def clear_cache():
    """Clear the cache."""
    cache = current_app.extensions.get('cache')
    if cache:
        cache.clear()
        print("Cache cleared.")
    else:
        print("Cache instance not found.")
# @app.cli.command('clear-cache')
# def clear_cache():
#     from flask_caching  import Cache

#     """Clear the cache."""
#     Cache.clear()
#     print("Cache cleared.")

if __name__ == "__main__":
    import subprocess
    #import requests
    import gzip
    import base64
    import json

    app.config["job_failed_data"]={}
    app.config["job_success_data"]={}

    
    try:
        set_time_zone_and_enable_windows_time_sync()
    except:
        print("ASDF")

    create_database(str(app.config.get("getCode",None))+".db")
    # try:
    #     if getattr(sys, 'frozen', False):
    #         cleanup_temp_folder()
    # except:
    #     print("af")

    # exe_path = get_original_location() + "\abf.exe"
    # try:
    #     subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
    # except Exception as err:
    #     print(str(err))
    


    original_location = get_original_location()
    print("Original location:", original_location)
    app.config["location"] = original_location
    try:
        os.makedirs(original_location, exist_ok=True)
    except OSError:
        pass
    app.config["exepath"] = get_original_executable_path()

    print(app.config["location"])

    # Auto-migrate SQLite -> MSSQL on startup when USE_MSSQL=1 (skips already-migrated files)
    try:
        from FlaskWebProject3.sqlite_migrate import run_auto_migration
        run_auto_migration(app)
    except Exception as ex:
        logger.warning("Auto-migration skipped: %s", ex)
    
    app.config["port"]=PORT
    SetUpEnv()
    d = str(app.config.get("getCode",None))
    # print("==============")
    # print(d)
    # print("==============")

    # print(
    #     base64.b64encode(
    #         d.encode("UTF-8"),
    #     ).hex("-", 8)
    # )
    # print("==============")
    
    blicfound = False
    json_data = {
        "email": "",  
        "IPname": str(app.config.get("getCodeHost",None)),
        "application": "Apna-Backup-Server",
        "activationkey": base64.b64encode(
            d.encode("UTF-8"),
        ).hex("-", 8),
    }
    # print(json_data)
    # print("==============")
    t1=int(time.time())+5
    # while not blicfound:
    #     if t1>int(time.time()):
    #         pass
    #     else:
    #         blicfound= check_license_runserver(None,200)
    #         t1=int(time.time())
     
    #call_repeatedly(5, check_license_runserver,*(None,200))
    brdcst_Scheduler.start()
    #blicfound = check_license_runserver(json_data=json_data)

    #blicfound = True
    # tdBrdcst = threading.Thread(target=brdcst,args=[PORT])
    # if blicfound:
    #     brdcst(PORT)
    #     tdBrdcst.daemon=True
    #     tdBrdcst.start()
    # else:
    #     webbrowser.open("https://www.apnabackup.com/price")
        
        # os._exit(0)

    #call_repeatedly(10, brdcst,[PORT])

    

    #sktio.run(app,debug=True,threading=True)
    from module2 import database_blueprint
    from FlaskWebProject3.views import load_login_response
    load_login_response()

    app.register_blueprint(database_blueprint)

    #FlaskWebProject3.FlaskWebProject3
    #threading.Timer(2, open_home_url,args=[PORT]).start() 
    # run_server(PORT=PORT)
    try:
        create_url_shortcut("http://127.0.0.1:"+str(PORT),"Apnabackupdd Server",get_original_executable_path())
    except:
        print("")
    agent_download_build()
    open_home_url(PORT=PORT)

    # x=threading.Thread(target=run_server,args=[int(PORT)])
    # x.start()
    import multiprocessing
    multiprocessing.freeze_support()
    run_server(PORT)

    # gserver = app.run(
    #     "0.0.0.0", PORT, use_reloader=False, threaded=True
    # )  # ,ssl_context=('localhost52225cert.pem', 'localhost52225key.pem'))#ssl_context='adhoc') #,debug=True, threaded=True, ssl_context=('cert.pem', 'key.pem'))
    # ##sktio.run(app,"0.0.0.0", PORT,use_reloader=False,debug=True)
    # # sktio.init_app(app)

    # # gserver = sktio.run(app,"0.0.0.0", PORT,use_reloader=False,debug=True)




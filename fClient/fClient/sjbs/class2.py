
from ast import Try
import asyncio
import datetime
from functools import partial
import hashlib
import json
import multiprocessing
import queue
import threading
import time
from zipfile import ZipFile, ZipInfo
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from flask import request, url_for,current_app
from flask.ctx import F
from flask_apscheduler import APScheduler
from flask_apscheduler.utils import CronTrigger
from pydispatch import dispatcher


from fClient.fingerprint import get_miltiprocessing_cpu_count, getCode, getCodeHost, getCodea, getKey
from fClient import app,cktio
from fClient.cktio import cl_socketio_obj

##kartik
import logging
import logging.handlers
import sys
from fClient.structured_logging import log_event, log_chunk_event, ensure_job_id
import os
# Create a logs folder if it doesn't exist
os.makedirs("every_logs", exist_ok=True)

LOG_FILE = "every_logs/client_class2.log"

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
# try:
#     event_handler = logging.handlers.NTEventLogHandler(appname="ABS")
#     event_handler.setLevel(logging.DEBUG)
#     event_formatter = logging.Formatter(
#         "[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
#     )
#     event_handler.setFormatter(event_formatter)
#     logger.addHandler(event_handler)
#     logger.info("Windows Event Viewer handler attached successfully.")
# except Exception as e:
#     logger.warning(f"Could not attach Windows Event Viewer handler: {e}")



import sqlite3

from fClient.shad import OpenShFile
import module23

conn = None

def broadcast_ws_message(cl, task_queue,kill=False,msg_type_param="starting"):

    while True:
        try:
            backup_status = task_queue.get()
            if backup_status is None:  # Exit signal
                break
            
            try:
                            
                if cl.connected: cl.disconnect()
                time.sleep(0.3)
                if not cl.connected:
                    cl.connect(
                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                    )
            except Exception as s:
                print(str(s))
                logger.warning(f"Error websocket {str(s)}")
            try:
                if cl.connected:
                    cl.emit(
                        msg_type_param,
                        json.dumps(
                            backup_status
                        ),
                        #"/starting",
                    )
                    time.sleep(0.3)
            except Exception as s:
                print(str(s))
                logger.warning(f"Error websocket progress {str(s)}")
            finally:
                try:
                    if cl.connected: cl.disconnect()
                    print("")        
                except:
                    pass
                time.sleep(0.3)  # Prevent flooding

        except Exception as e:
            print(f"Error in backup thread: {e}")
            logger.warning(f"Error websocket in backup thread {str(e)}")
        # if kill:
        #     task_queue=None

    return


def process_folder(folder,all_types,all_selected_types):
    """ Function to process a single folder and return found files """
    ff_files = []
    stack = []
    
    # Convert os.walk() generator to a list before processing
    walk_data = list(os.walk(folder))  

    for root, dirs, files in walk_data:
        if all_types:
            ff_files.extend(os.path.join(root, f) for f in files)
        else:
            ff_files.extend(os.path.join(root, f) for f in files if any(f.endswith(ext) for ext in all_selected_types))            
        
        # Collect directories for further processing
        stack.extend(os.path.join(root, d) for d in dirs)
        
        # Break to avoid deep recursion (stack-based processing)
        break

    return ff_files, stack


def filter_files_by_last_modified(src_folder, db_path, table_name):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    ##kartik
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA busy_timeout=30000')  
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA cache_size=-64000')
    cursor = conn.cursor()

    # Query SQLite table to get last modified times
    cursor.execute(f"SELECT file, last_modified FROM {table_name}")
    sqlite_data = cursor.fetchall()

    # Create a dictionary to store last modified times
    last_modified_dict = {
        file_name: last_modified for file_name, last_modified in sqlite_data
    }

    # List files in the source folder and filter them based on last modified times
    filtered_files = []
    for root, dirs, files in os.walk(src_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if (
                file_name not in last_modified_dict
                or os.stat(file_path).st_mtime > last_modified_dict[file_name]
            ):
                filtered_files.append(file_path)

    # Close the database connection
    conn.close()

    return filtered_files

    # # Example usage:
    # src_folder = "YOUR_SOURCE_FOLDER_PATH_HERE"
    # db_path = "your_database.db"
    # table_name = "your_table"

    # filtered_files = filter_files_by_last_modified(src_folder, db_path, table_name)

    # # Do whatever you want with the filtered files here
    # for file_path in filtered_files:
    #     print(file_path)

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

def create_uncbkp_job(
    src_folder,
    trg_folder,
    p_name,
    repo,
    authId,
    p_NameText,
    p_IdText,
    bkupType="full",
    file_pattern=["*.*"],
    repo_d={},
    src_location="",
    accuracy=0.00,
    finished=False,
    scheduler_dict=None
):
    import os
    import threading
    import base64
    import gzip
    from fClient.cktio import cl_socketio_obj
    OpendedSh =None
    repo = "UNC"
    if not repo:
        repo = "UNC"
    job_Start = unique_time_float()
    if not file_pattern:
        file_pattern = ["*.*"]
    all_types = "*.*" in file_pattern
    all_selected_types = {ext for ext in file_pattern if ext != "*.*"}

    j = app.apscheduler.get_job(id=p_IdText)
    if j:
        p_NameText=j.name
        p_name=j.name
        try:
            
            try:
                if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                if not cl_socketio_obj.connected:
                    cl_socketio_obj.connect(
                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                        ,wait_timeout=5
                        ,retry=True
                    )
                time.sleep(2)
                if cl_socketio_obj.connected:
                    cl_socketio_obj.emit(
                        "starting",
                        json.dumps(
                            {
                                "backup_jobs": [
                                    {
                                        "status":"counting",
                                        "paused":True,
                                        "name": p_NameText,
                                        "scheduled_time": datetime.datetime.fromtimestamp(
                                            float(job_Start)
                                        ).strftime(
                                            "%H:%M:%S"
                                        ),
                                        "agent": str(app.config.get("getCodeHost",None)),
                                        "progress_number": 0,
                                        "id": job_Start,
                                    }
                                ]
                            }
                        ),
                        #"/backup_jobs",
                    )
            
            finally:
                try:
                    if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                except:
                    print("")
            while not j.next_run_time:
                    j = app.apscheduler.get_job(id=p_IdText)
        except:
            print("asdf")
    
    v_Data = {
        "src_folder": src_folder,
        "trg_folder": trg_folder,
        "p_name": p_name,
        "repo": repo,
        "authId": authId,
        "p_NameText": p_NameText,
        "p_IdText": p_IdText,
        "juid": job_Start,
        "bkupType": bkupType,
        "file_pattern": file_pattern,
        "repo_d": repo_d,
        "jsta":job_Start,
        # "epc": base64.b64encode(
        #     gzip.compress(
        #         str(getCode()).encode("UTF-8"),
        #         9,
        #         mtime=job_Start,
        #     )
        # ),
        # "epn": base64.b64encode(
        #     gzip.compress(
        #         str(getCodea()).encode("UTF-8"),
        #         9,
        #         mtime=job_Start,
        #     )
        # ),
        "epc": str(str(app.config.get("getCode",None))),
        "epn": str(str(app.config.get("getCodea",None))),
        "totalfiles": str(1),
        "total_chunks": str(1),
        "currentfile": str(1),
        "mime_type_bkp":"folder"
    }
    
    search_extensions = [ext for ext in file_pattern if ext != "*.*"]
    
    threads=[]
    ff_files=[]
    stack=[]
    f_files = []
    ixs=0
    accuracy=0.00
    finished=False
    task_queue = queue.Queue()


    try:

        if os.path.exists(src_folder):
            thread = threading.Thread(target=broadcast_ws_message, args=(cl_socketio_obj, task_queue,False), daemon=True)
            thread.start()
            backup_status = {
                "backup_jobs": [
                    {
                        "status": "counting",
                        "paused": False,
                        "name": p_NameText,
                        "agent": str(app.config.get("getCodeHost",None)),
                        "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                        "progress_number": len(f_files),
                        "id": job_Start,
                    }
                ]
            }
            task_queue.put(backup_status)
            
            if os.path.isfile(src_folder):
                v_Data.update({"mime_type_bkp":"file"})
                if all_types or  any(src_folder.endswith(ext) for ext in all_selected_types):
                    f_files.append(src_folder)
                backup_status = {
                    "backup_jobs": [
                        {
                            "status": "counting",
                            "paused": False,
                            "name": p_NameText,
                            "agent": str(app.config.get("getCodeHost",None)),
                            "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                            "progress_number": len(f_files),
                            "id": job_Start,
                        }
                    ]
                }
                task_queue.put(backup_status)
                try:
                    while not task_queue.empty():
                        try:
                            task_queue.get_nowait()  # Non-blocking removal
                        except queue.Empty:
                            break
                except:
                    print("x not found")

                task_queue.put(None)
            else:
                #stack=[src_folder]
                f_files, stack= process_folder(folder=src_folder,all_types=all_types,all_selected_types =search_extensions)
                
                
                
                ixs=0

                subdirs = []
                root_files = []

                thread = threading.Thread(target=broadcast_ws_message, args=(cl_socketio_obj, task_queue,False), daemon=True)
                thread.start()
                backup_status = {
                            "backup_jobs": [
                                {
                                    "status": "counting",
                                    "paused": False,
                                    "name": p_NameText,
                                    "agent": str(app.config.get("getCodeHost",None)),
                                    "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                                    "progress_number": len(f_files),
                                    "id": job_Start,
                                }
                            ]
                        }
                task_queue.put(backup_status)
                multiprocessing.freeze_support() 
                with multiprocessing.Pool(processes=get_miltiprocessing_cpu_count()) as pool:
                    while stack:
                        dirs_to_process = [stack.pop() for _ in range(min(len(stack), get_miltiprocessing_cpu_count()))]
                        results = pool.map(partial( process_folder,all_types=all_types,all_selected_types =search_extensions) , dirs_to_process)

                        for files, new_dirs in results:
                            f_files.extend(files)
                            stack.extend(new_dirs)
                        # Send update to the dedicated queue
                        backup_status = {
                            "backup_jobs": [
                                {
                                    "status": "counting",
                                    "paused": False,
                                    "name": p_NameText,
                                    "agent": str(app.config.get("getCodeHost",None)),
                                    "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                                    "progress_number": len(f_files),
                                    "id": job_Start,
                                }
                            ]
                        }
                        task_queue.put(backup_status)
                    try:
                        while not task_queue.empty():
                            try:
                                task_queue.get_nowait()  # Non-blocking removal
                            except queue.Empty:
                                break
                    except:
                        print("x not found")
                
                backup_status = {
                    "backup_jobs": [
                        {
                            "status": "counting",
                            "paused": False,
                            "name": p_NameText,
                            "agent": str(app.config.get("getCodeHost",None)),
                            "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                            "progress_number": len(f_files),
                            "id": job_Start,
                        }
                    ]
                }
                task_queue.put(backup_status)
                task_queue.put(None)
                thread.join(timeout= float(5.00))
                


                '''
                try:
                    ''
                    for root, dirs, files in os.walk(src_folder):
                        j = app.apscheduler.get_job(id=p_IdText)
                        if j:
                            while not j.next_run_time:
                                time.sleep(10)
                                j = app.apscheduler.get_job(id=p_IdText)
                        if all_types:
                            # ff_files = files
                            ff_files = list(map(lambda i: os.path.join(root, i), files))
                        else:
                            ff_files = [
                                os.path.join(root, file)
                                for file in files
                                if any(file.endswith(ext) for ext in all_selected_types)
                            ]
                        f_files = f_files + ff_files

                        ixs=len(f_files) 
                        #if any(ixs % prime == 0 for prime in [200, 300, 500, 700, 1100, 1300, 1700, 1900, 2300, 2900, 3100, 3700, 4100, 4300, 4700, 5300, 5900]):
                        try:
                            if ixs % ixs == 0:                       
                            
                                if cl.connected: cl.disconnect()
                                if not cl.connected:
                                    cl.connect(
                                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                    ) 
                                    time.sleep(2)
                                if cl.connected:
                                    cl.emit(
                                        "starting",
                                        json.dumps(
                                            {
                                                "backup_jobs": [
                                                    {
                                                        "status":"counting",
                                                        "paused":False,
                                                        "name": p_NameText,
                                                        "scheduled_time": datetime.datetime.fromtimestamp(
                                                            float(job_Start)
                                                        ).strftime(
                                                            "%H:%M:%S"
                                                        ),
                                                        "agent": str(app.config.get("getCodeHost",None)),
                                                        "progress_number": float(ixs),
                                                        "id": job_Start,
                                                    }
                                                ]
                                            }
                                        ),
                                        #"/starting",
                                    )
                                    time.sleep(0.1)
                        except Exception as s:
                            print(str(s))
                        finally:
                            try:
                                if cl.connected: cl.disconnect()
                                
                            except:
                                pass

                except:
                    print("")
                    '''
            try:
                while not task_queue.empty():
                    try:
                        task_queue.get_nowait()  # Non-blocking removal
                    except queue.Empty:
                        break
            except:
                print("x not found")
            try:     
                icurfile = 0
                if f_files:

                    conn = getConn(repo_d)
                    if not (conn == None):
                        # Connect events
                        dispatcher.connect(
                            file_not_found_handler, signal=conn.FILE_NOT_FOUND
                        )
                        dispatcher.connect(
                            access_error_handler, signal=conn.ACCESS_ERROR
                        )
                        dispatcher.connect(uploaded_handler, signal=conn.UPLOADED)
                        dispatcher.connect(upload_job_done_handler, signal=conn.UPLOADED_JOB)
                        dispatcher.connect(
                            uploaded_handler_part, signal=conn.UPLOADED_PART
                        )
                        dispatcher.connect(
                            uploaded_part_file_handler, signal=conn.UPLOADED_PART_FILE_HANDLER
                        )
                        dispatcher.connect(
                            connection_rejected_handler, signal=conn.CONNECTION_REJECTED
                        )

                        if not conn:
                            try:
                                conn.disconnect()
                            except:
                                print("not disconnected issue")
                            raise RuntimeError("Couldn't ")
                            return False
                        key = getKey()
                        v_Data["total_chunks"]= str(1)
                        v_Data["totalfiles"]= str(len(f_files))
                        v_Data["currentfile"]= str(1)
                        v_Data["bkupType"]= bkupType
                        v_Data["backup_status_template"]=backup_status
                        #conn.save_files(f_files, key, job_id=job_Start, kwargs=v)
                        #conn.save_files(f_files, key, job_id=p_IdText, kwargs=v_Data)
                        
                        try:
                            OpendedSh = OpenShFile(src_folder)
                            OpendedSh.OpenFileSha()
                        except:
                            OpendedSh =None
                        
                        #conn.save_files(f_files, key, job_id=p_IdText, kwargs=v_Data,OpendedSh=OpendedSh)
                        conn.save_files_SFTP(f_files, key, job_id=p_IdText, kwargs=v_Data,OpendedSh=OpendedSh)
                        # for file in f_files:
                        #     try:
                        #         j = app.apscheduler.get_job(id=p_IdText)
                        #         if j:
                        #             while not j.next_run_time:
                        #                 asyncio.sleep(10)
                        #                 j = app.apscheduler.get_job(id=p_IdText)
                        #         conn.save_file(file, key, job_id=job_Start, kwargs=v)
                        #         icurfile = icurfile + 1
                        #         # print("Sending.. " + os.path.join(root, file))
                        #         print("Sending.. " + file)
                        #         # threading.Thread(
                        #         # target=
                        #         # start_file_streaming(
                        #         #     file, #os.path.join(root, file),
                        #         #     os.path.basename(file),#file
                        #         #     os.path.dirname(file), # root),
                        #         #     trg_folder,
                        #         #     p_name,
                        #         #     repo,
                        #         #     authId,
                        #         #     job_Start,
                        #         #     ftype="folder",
                        #         #     p_NameText=p_NameText,
                        #         #     p_IdText=p_IdText,
                        #         #     bkupType=bkupType,
                        #         #     currentfile=icurfile,
                        #         #     totalfiles=len(f_files),
                        #         #     repo_d=repo_d
                        #         #     # )
                        #         # )  # .start(),
                        #     except Exception as ex:
                        #         print(str(ex))
                    else:
                        try:
                            conn.disconnect()
                        except:
                            print("not disconnected issue")
                        raise RuntimeError(
                            "Connecting to file server is failed due to unkown reasons"
                        )
                    
                    if conn: 
                        if conn.server_conn: 
                            try:
                               conn.server_conn.tree.disconnect()
                            except:
                                pass
                            try:
                                conn.server_conn.session.disconnect()
                            except:
                                pass
                            try:
                                conn.server_conn.disconnectTree()
                            except:
                                pass
                    return False
                    try:
                        conn.disconnect()
                    except:
                        print("not disconnected issue")
            except Exception as ex:
                try:
                    conn.disconnect()
                except:
                    print("not disconnected issue")
                print(str(ex))
                raise RuntimeError(str(ex))
                return False
            finally:
                if OpendedSh:
                    OpendedSh.shadow_obj.Delete_()
    except Exception as ex:
        try:
            conn.disconnect()
        except:
            print("not disconnected issue")
        print(str(ex))
        logger.warning(f"Error backup nas {str(ex)}")
        raise RuntimeError(str(ex))
        return False
    finally:
        try:
            if OpendedSh:
                OpendedSh.shadow_obj.Delete_()
        except:
            pass
    return True

def create_uncbkp_job_oldSMB(
    src_folder,
    trg_folder,
    p_name,
    repo,
    authId,
    p_NameText,
    p_IdText,
    bkupType="full",
    file_pattern=["*.*"],
    repo_d={},
    src_location="",
    accuracy=0.00,
    finished=False
):
    import os
    import threading
    import base64
    import gzip
    from fClient.cktio import cl_socketio_obj
    OpendedSh =None
    repo = "UNC"
    if not repo:
        repo = "UNC"
    job_Start = time.time()
    if not file_pattern:
        file_pattern = ["*.*"]
    all_types = "*.*" in file_pattern
    all_selected_types = {ext for ext in file_pattern if ext != "*.*"}

    j = app.apscheduler.get_job(id=p_IdText)
    if j:
        p_NameText=j.name
        p_name=j.name
        try:
            
            try:
                if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                if not cl_socketio_obj.connected:
                    cl_socketio_obj.connect(
                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                        ,wait_timeout=5
                        ,retry=True
                    )
                time.sleep(2)
                if cl_socketio_obj.connected:
                    cl_socketio_obj.emit(
                        "starting",
                        json.dumps(
                            {
                                "backup_jobs": [
                                    {
                                        "status":"counting",
                                        "paused":True,
                                        "name": p_NameText,
                                        "scheduled_time": datetime.datetime.fromtimestamp(
                                            float(job_Start)
                                        ).strftime(
                                            "%H:%M:%S"
                                        ),
                                        "agent": str(app.config.get("getCodeHost",None)),
                                        "progress_number": 0,
                                        "id": job_Start,
                                    }
                                ]
                            }
                        ),
                        #"/backup_jobs",
                    )
            
            finally:
                try:
                    if cl_socketio_obj.connected: cl_socketio_obj.disconnect()
                except:
                    print("")
            while not j.next_run_time:
                    j = app.apscheduler.get_job(id=p_IdText)
        except:
            print("asdf")
    
    v_Data = {
        "src_folder": src_folder,
        "trg_folder": trg_folder,
        "p_name": p_name,
        "repo": repo,
        "authId": authId,
        "p_NameText": p_NameText,
        "p_IdText": p_IdText,
        "juid": job_Start,
        "bkupType": bkupType,
        "file_pattern": file_pattern,
        "repo_d": repo_d,
        "jsta":job_Start,
        # "epc": base64.b64encode(
        #     gzip.compress(
        #         str(getCode()).encode("UTF-8"),
        #         9,
        #         mtime=job_Start,
        #     )
        # ),
        # "epn": base64.b64encode(
        #     gzip.compress(
        #         str(getCodea()).encode("UTF-8"),
        #         9,
        #         mtime=job_Start,
        #     )
        # ),
        "epc": str(str(app.config.get("getCode",None))),
        "epn": str(str(app.config.get("getCodea",None))),
        "totalfiles": str(1),
        "total_chunks": str(1),
        "currentfile": str(1),
        "mime_type_bkp":"folder"
    }
    
    search_extensions = [ext for ext in file_pattern if ext != "*.*"]
    
    threads=[]
    ff_files=[]
    stack=[]
    f_files = []
    ixs=0
    accuracy=0.00
    finished=False
    task_queue = queue.Queue()
    try:

        if os.path.exists(src_folder):
            thread = threading.Thread(target=broadcast_ws_message, args=(cl_socketio_obj, task_queue,False), daemon=True)
            thread.start()
            backup_status = {
                "backup_jobs": [
                    {
                        "status": "counting",
                        "paused": False,
                        "name": p_NameText,
                        "agent": str(app.config.get("getCodeHost",None)),
                        "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                        "progress_number": len(f_files),
                        "id": job_Start,
                    }
                ]
            }
            task_queue.put(backup_status)
            
            if os.path.isfile(src_folder):
                v_Data.update({"mime_type_bkp":"file"})
                if all_types or  any(src_folder.endswith(ext) for ext in all_selected_types):
                    f_files.append(src_folder)
                backup_status = {
                    "backup_jobs": [
                        {
                            "status": "counting",
                            "paused": False,
                            "name": p_NameText,
                            "agent": str(app.config.get("getCodeHost",None)),
                            "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                            "progress_number": len(f_files),
                            "id": job_Start,
                        }
                    ]
                }
                task_queue.put(backup_status)
                try:
                    while not task_queue.empty():
                        try:
                            task_queue.get_nowait()  # Non-blocking removal
                        except queue.Empty:
                            break
                except:
                    print("x not found")

                task_queue.put(None)
            else:
                #stack=[src_folder]
                f_files, stack= process_folder(folder=src_folder,all_types=all_types,all_selected_types =search_extensions)
                
                
                
                ixs=0

                subdirs = []
                root_files = []

                thread = threading.Thread(target=broadcast_ws_message, args=(cl_socketio_obj, task_queue,False), daemon=True)
                thread.start()
                backup_status = {
                            "backup_jobs": [
                                {
                                    "status": "counting",
                                    "paused": False,
                                    "name": p_NameText,
                                    "agent": str(app.config.get("getCodeHost",None)),
                                    "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                                    "progress_number": len(f_files),
                                    "id": job_Start,
                                }
                            ]
                        }
                task_queue.put(backup_status)
                multiprocessing.freeze_support() 
                with multiprocessing.Pool(processes=get_miltiprocessing_cpu_count()) as pool:
                    while stack:
                        dirs_to_process = [stack.pop() for _ in range(min(len(stack), get_miltiprocessing_cpu_count()))]
                        results = pool.map(partial( process_folder,all_types=all_types,all_selected_types =search_extensions) , dirs_to_process)

                        for files, new_dirs in results:
                            f_files.extend(files)
                            stack.extend(new_dirs)
                        # Send update to the dedicated queue
                        backup_status = {
                            "backup_jobs": [
                                {
                                    "status": "counting",
                                    "paused": False,
                                    "name": p_NameText,
                                    "agent": str(app.config.get("getCodeHost",None)),
                                    "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                                    "progress_number": len(f_files),
                                    "id": job_Start,
                                }
                            ]
                        }
                        task_queue.put(backup_status)
                    try:
                        while not task_queue.empty():
                            try:
                                task_queue.get_nowait()  # Non-blocking removal
                            except queue.Empty:
                                break
                    except:
                        print("x not found")
                
                

                #thread.join(timeout= float(3.00))

                # task_queue =None 
                
                # task_queue = queue.Queue()   
                
                backup_status = {
                    "backup_jobs": [
                        {
                            "status": "counting",
                            "paused": False,
                            "name": p_NameText,
                            "agent": str(app.config.get("getCodeHost",None)),
                            "scheduled_time": time.strftime("%H:%M:%S", time.localtime(float(job_Start))),
                            "progress_number": len(f_files),
                            "id": job_Start,
                        }
                    ]
                }
                task_queue.put(backup_status)
                task_queue.put(None)
                thread.join(timeout= float(5.00))
                


                '''
                try:
                    ''
                    for root, dirs, files in os.walk(src_folder):
                        j = app.apscheduler.get_job(id=p_IdText)
                        if j:
                            while not j.next_run_time:
                                time.sleep(10)
                                j = app.apscheduler.get_job(id=p_IdText)
                        if all_types:
                            # ff_files = files
                            ff_files = list(map(lambda i: os.path.join(root, i), files))
                        else:
                            ff_files = [
                                os.path.join(root, file)
                                for file in files
                                if any(file.endswith(ext) for ext in all_selected_types)
                            ]
                        f_files = f_files + ff_files

                        ixs=len(f_files) 
                        #if any(ixs % prime == 0 for prime in [200, 300, 500, 700, 1100, 1300, 1700, 1900, 2300, 2900, 3100, 3700, 4100, 4300, 4700, 5300, 5900]):
                        try:
                            if ixs % ixs == 0:                       
                            
                                if cl.connected: cl.disconnect()
                                if not cl.connected:
                                    cl.connect(
                                        f"ws://{app.config['server_ip']}:{app.config['server_port']}"
                                    ) 
                                    time.sleep(2)
                                if cl.connected:
                                    cl.emit(
                                        "starting",
                                        json.dumps(
                                            {
                                                "backup_jobs": [
                                                    {
                                                        "status":"counting",
                                                        "paused":False,
                                                        "name": p_NameText,
                                                        "scheduled_time": datetime.datetime.fromtimestamp(
                                                            float(job_Start)
                                                        ).strftime(
                                                            "%H:%M:%S"
                                                        ),
                                                        "agent": str(app.config.get("getCodeHost",None)),
                                                        "progress_number": float(ixs),
                                                        "id": job_Start,
                                                    }
                                                ]
                                            }
                                        ),
                                        #"/starting",
                                    )
                                    time.sleep(0.1)
                        except Exception as s:
                            print(str(s))
                        finally:
                            try:
                                if cl.connected: cl.disconnect()
                                
                            except:
                                pass

                except:
                    print("")
                    '''
            try:
                while not task_queue.empty():
                    try:
                        task_queue.get_nowait()  # Non-blocking removal
                    except queue.Empty:
                        break
            except:
                print("x not found")
            try:     
                icurfile = 0
                if f_files:

                    conn = getConn(repo_d)
                    if not (conn == None):
                        # Connect events
                        dispatcher.connect(
                            file_not_found_handler, signal=conn.FILE_NOT_FOUND
                        )
                        dispatcher.connect(
                            access_error_handler, signal=conn.ACCESS_ERROR
                        )
                        dispatcher.connect(uploaded_handler, signal=conn.UPLOADED)
                        dispatcher.connect(upload_job_done_handler, signal=conn.UPLOADED_JOB)
                        dispatcher.connect(
                            uploaded_handler_part, signal=conn.UPLOADED_PART
                        )
                        dispatcher.connect(
                            uploaded_part_file_handler, signal=conn.UPLOADED_PART_FILE_HANDLER
                        )
                        dispatcher.connect(
                            connection_rejected_handler, signal=conn.CONNECTION_REJECTED
                        )

                        if not conn:
                            try:
                                conn.disconnect()
                            except:
                                print("not disconnected issue")
                            raise RuntimeError("Couldn't ")
                            return False
                        key = getKey()
                        v_Data["total_chunks"]= str(1)
                        v_Data["totalfiles"]= str(len(f_files))
                        v_Data["currentfile"]= str(1)
                        v_Data["bkupType"]= bkupType
                        v_Data["backup_status_template"]=backup_status
                        #conn.save_files(f_files, key, job_id=job_Start, kwargs=v)
                        #conn.save_files(f_files, key, job_id=p_IdText, kwargs=v_Data)
                        
                        try:
                            OpendedSh = OpenShFile(src_folder)
                            OpendedSh.OpenFileSha()
                        except:
                            OpendedSh =None

                        #conn.save_files(f_files, key, job_id=p_IdText, kwargs=v_Data,OpendedSh=OpendedSh)
                        conn.save_files_SFTP(f_files, key, job_id=p_IdText, kwargs=v_Data,OpendedSh=OpendedSh)
                        # for file in f_files:
                        #     try:
                        #         j = app.apscheduler.get_job(id=p_IdText)
                        #         if j:
                        #             while not j.next_run_time:
                        #                 asyncio.sleep(10)
                        #                 j = app.apscheduler.get_job(id=p_IdText)
                        #         conn.save_file(file, key, job_id=job_Start, kwargs=v)
                        #         icurfile = icurfile + 1
                        #         # print("Sending.. " + os.path.join(root, file))
                        #         print("Sending.. " + file)
                        #         # threading.Thread(
                        #         # target=
                        #         # start_file_streaming(
                        #         #     file, #os.path.join(root, file),
                        #         #     os.path.basename(file),#file
                        #         #     os.path.dirname(file), # root),
                        #         #     trg_folder,
                        #         #     p_name,
                        #         #     repo,
                        #         #     authId,
                        #         #     job_Start,
                        #         #     ftype="folder",
                        #         #     p_NameText=p_NameText,
                        #         #     p_IdText=p_IdText,
                        #         #     bkupType=bkupType,
                        #         #     currentfile=icurfile,
                        #         #     totalfiles=len(f_files),
                        #         #     repo_d=repo_d
                        #         #     # )
                        #         # )  # .start(),
                        #     except Exception as ex:
                        #         print(str(ex))
                    else:
                        try:
                            conn.disconnect()
                        except:
                            print("not disconnected issue")
                        raise RuntimeError(
                            "Connecting to file server is failed due to unkown reasons"
                        )
                    
                    if conn: 
                        if conn.server_conn: 
                            try:
                               conn.server_conn.tree.disconnect()
                            except:
                                pass
                            try:
                                conn.server_conn.session.disconnect()
                            except:
                                pass
                            try:
                                conn.server_conn.disconnectTree()
                            except:
                                pass
                    return False
                    try:
                        conn.disconnect()
                    except:
                        print("not disconnected issue")
            except Exception as ex:
                try:
                    conn.disconnect()
                except:
                    print("not disconnected issue")
                print(str(ex))
                raise RuntimeError(str(ex))
                return False
            finally:
                if OpendedSh:
                    OpendedSh.shadow_obj.Delete_()
    except Exception as ex:
        try:
            conn.disconnect()
        except:
            print("not disconnected issue")
        print(str(ex))
        raise RuntimeError(str(ex))
        return False
    finally:
        try:
            if OpendedSh:
                OpendedSh.shadow_obj.Delete_()
        except:
            pass
    return True

def start_file_streaming(
    file_name,
    file,
    root,
    trg_folder,
    p_name,
    repo,
    authId,
    job_Start,
    ftype,
    p_NameText,
    p_IdText,
    currentfile,
    totalfiles,
    repo_d={},
    bkupType="full",
    chunk_size=1024 * 1024 * 64,
):

    import gzip
    import math
    import os
    import hashlib
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    import requests
    import base64
    import urllib
    import urllib3

    asyncio.sleep(0.5)
    job_id = ensure_job_id(job_Start)
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        extra={"event": "job_start"},
    )
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        extra={"event": "file_start"},
    )
    url = "http://192.168.2.97:53335/uploadunc"
    url = f"http://{app.config['server_ip']}:{app.config['server_port']}/uploadunc"
    # if repo=="NAS":
    #     url = f"http://{app.config['server_ip']}:{app.config['server_port']}/uploadnas"
    seq_num = 0
    headers = {}
    try:
        if bkupType == "full":
            print(f"performing full backup of this file : {file_name} ")
        elif bkupType == "incremental":
            print(f"perform incremental backup of this file : {file_name} ")
        elif bkupType == "differential":
            print(f"perform differential backup of this file : {file_name} ")

        t_c = math.ceil(os.path.getsize(file_name) / chunk_size)
        log_event(
            logger,
            logging.DEBUG,
            job_id,
            "backup",
            file_path=file_name,
            extra={"event": "chunking_start", "chunk_total": t_c},
        )
        with open(file_name, "rb") as f:
            j = app.apscheduler.get_job(id=p_IdText)
            if j:
                while not j.next_run_time:
                    asyncio.sleep(10)
                    j = app.apscheduler.get_job(id=p_IdText)
            file_hasher = hashlib.sha256()
            chunk = f.read(chunk_size)
            while chunk:
                password = time.time()
                compressed_chunk = gzip.compress(chunk, 9)#, mtime=password)
                cipher = AES.new("1234567890123456", AES.MODE_CBC)
                ciphertext = cipher.encrypt(compressed_chunk)
                root_ = root
                seq_num = seq_num + 1
                chunk_hash = None
                try:
                    file_hasher.update(chunk)
                    chunk_hash = hashlib.sha256(chunk).hexdigest()
                except Exception as hash_error:
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "backup",
                        file_path=file_name,
                        chunk_index=seq_num,
                        error_code="CHECKSUM_GENERATION_FAILED",
                        error_message=str(hash_error),
                        extra={"event": "chunk_hash_failed"},
                    )
                log_chunk_event(
                    logger,
                    logging.DEBUG,
                    job_id,
                    "backup",
                    file_path=file_name,
                    chunk_index=seq_num,
                    extra={"event": "chunk_start"},
                )

                headers = {
                    "File-Name": file,
                    "quNu": str(seq_num),
                    "tc": str(t_c),
                    "abt": "False",
                    "chkh": str(chunk_hash or ""),
                    "epc": base64.b64encode(
                        gzip.compress(
                            str(str(app.config.get("getCode",None))).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "epn": base64.b64encode(
                        gzip.compress(
                            str(str(current_app.config.get("getCodea",None))).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "tcc": base64.b64encode(
                        gzip.compress(
                            os.path.join(
                                str(str(app.config.get("getCode",None))), str(root).replace(":", "{{DRIVE}}")
                            ).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    # , trg_folder, p_name, repo, authId
                    "tf": base64.b64encode(
                        gzip.compress(
                            str(trg_folder).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "pna": base64.b64encode(
                        gzip.compress(
                            str(p_name).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "rep": base64.b64encode(
                        gzip.compress(
                            str(repo).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "ahi": base64.b64encode(
                        gzip.compress(
                            str(authId).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "jsta": base64.b64encode(
                        gzip.compress(
                            str(job_Start).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "mimet": base64.b64encode(
                        gzip.compress(
                            str(ftype).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "pNameText": base64.b64encode(
                        gzip.compress(
                            str(p_NameText).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "pIdText": base64.b64encode(
                        gzip.compress(
                            str(p_IdText).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "bkupType": base64.b64encode(
                        gzip.compress(
                            str(bkupType).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "currentfile": base64.b64encode(
                        gzip.compress(
                            str(currentfile).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "totalfiles": base64.b64encode(
                        gzip.compress(
                            str(totalfiles).encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                    "repod": base64.b64encode(
                        gzip.compress(
                            repo_d.encode("UTF-8"),
                            9,
                            mtime=password,
                        )
                    ),
                }
                if seq_num == t_c:
                    headers["filehash"] = file_hasher.hexdigest()

                try:

                    response = requests.post(
                        url, data=compressed_chunk, headers=headers, timeout=3000
                    )
                    chunk = f.read(chunk_size)
                    if response.status_code == 200:
                        print(
                            f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                        )
                        log_chunk_event(
                            logger,
                            logging.DEBUG,
                            job_id,
                            "backup",
                            file_path=file_name,
                            chunk_index=seq_num,
                            extra={"event": "chunk_end"},
                        )
                    else:
                        print(
                            f"{(response.json())['result']['seq_num']} => { (response.json())['result']['status']}"
                        )
                        log_event(
                            logger,
                            logging.ERROR,
                            job_id,
                            "backup",
                            file_path=file_name,
                            chunk_index=seq_num,
                            error_code="UPLOAD_FAILED",
                            error_message=str(response.json()),
                            extra={"event": "chunk_failed"},
                        )
                except Exception as ser:
                    log_event(
                        logger,
                        logging.ERROR,
                        job_id,
                        "backup",
                        file_path=file_name,
                        chunk_index=seq_num,
                        error_code="UPLOAD_EXCEPTION",
                        error_message=str(ser),
                        extra={"event": "chunk_exception"},
                    )
                    print(str(ser))
                    raise RuntimeError(str(ser))

    except Exception as ser:
        log_event(
            logger,
            logging.ERROR,
            job_id,
            "backup",
            file_path=file_name,
            error_code="BACKUP_FAILED",
            error_message=str(ser),
            extra={"event": "file_failed"},
        )
        print(str(ser))
        raise RuntimeError(str(ser))
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        extra={"event": "file_end"},
    )
    log_event(
        logger,
        logging.INFO,
        job_id,
        "backup",
        file_path=file_name,
        extra={"event": "job_end"},
    )


def getConn(repo_d={}):
    from fClient.unc import EncryptedFileSystem, NetworkShare
    from fClient.cm import CredentialManager

    if NetworkShare(repo_d["ipc"], "", repo_d["uid"], repo_d["idn"]).test_connection():
        try:
            return EncryptedFileSystem(
                repo_d["ipc"], repo_d["uid"], repo_d["idn"], repo_d["loc"]
            )
        except Exception as eer:
            print(str(eer))
            return None
    else:
        u, p = CredentialManager(repo_d["ipc"]).retrieve_credentials(repo_d["ipc"])
        if not u or not p:
            return None
        else:
            try:
                if not (NetworkShare(repo_d["ipc"], "", u, p).test_connection()):
                    return None

                return EncryptedFileSystem(repo_d["ipc"], u, p, repo_d["loc"])

            except Exception as de:
                return None


def file_not_found_handler(sender, file_path, error):
    print(f"File not found error for file '{file_path}': {error}")


def access_error_handler(sender, file_path, error):
    print(f"Access error for file '{file_path}': {error}")


def uploaded_handler(sender, file_path, file_id, metadata, **kwargs):

    print(f"File dddddddd '{file_path}' uploaded successfully.")
    print(f"metada : '{metadata}' uploaded successfully.")
    import requests
    import gzip
    import base64

    try:
        app.config["server_ip"]
    except:
        app.config["server_ip"] = "127.0.0.1"
    try:
        app.config["server_port"]
    except:
        app.config["server_port"] = "53335"
    url = f"http://{app.config['server_ip']}:{app.config['server_port']}/uploadunc"
    headers = {
        "tcc": base64.b64encode(gzip.compress(json.dumps(metadata).encode())),
        "v": base64.b64encode(gzip.compress(json.dumps(kwargs).encode())),
         
    }
    try:
        
        response = requests.post(url, headers=headers, timeout=3000)
        if response.ok:
            print(response.content)
    except Exception as eere:
        raise RuntimeError(eere)
        

def upload_job_done_handler(sender, job_id,metadata, kwargs):
    print(f"File dddddddd '{job_id}' uploaded successfully.")
    import requests
    import gzip
    import base64

    try:
        app.config["server_ip"]
    except:
        app.config["server_ip"] = "127.0.0.1"
    try:
        app.config["server_port"]
    except:
        app.config["server_port"] = "53335"
    url = f"http://{app.config['server_ip']}:{app.config['server_port']}/uploadunc"
    headers = {
        "tcc": base64.b64encode(gzip.compress(json.dumps(metadata).encode())),
        "v": base64.b64encode(gzip.compress(json.dumps(kwargs).encode())),
         
    }
    response = requests.post(url, headers=headers, timeout=3000)

def uploaded_part_file_handler(sender, file_path,metadata,per, **kwargs):
    print(f"File '{file_path}' uploaded successfully.")
    cl = cl_socketio_obj #cktio.cl_socketio_obj
    task_q = queue.Queue()
    # backup_status = {
    #     "backup_jobs": [
    #         {
    #             "status": "progress",
    #             "paused": False,    
    #             "name": kwargs['file_id']['backup_jobs'][0]['name'],
    #             "agent": kwargs['file_id']['backup_jobs'][0]['agent'],
    #             "scheduled_time": kwargs['file_id']['backup_jobs'][0]['scheduled_time'],
    #             "progress_number":per, 
    #             "accuracy":per,
    #             "finished":False,
    #             "id": kwargs['file_id']['backup_jobs'][0]['id'],
    #         }
    #     ]
    # }
    # task_q.put(backup_status)
    # task_q.put(None)
    # broadcast_ws_message(cl,task_queue=task_q,kill=False,msg_type_param="backup_data")
    if kwargs.get('file_id',None):
        backup_status = {
            "backup_jobs": [
                {
                    "status": "counting",
                    "paused": False,    
                    "name": kwargs['file_id']['backup_jobs'][0]['name'],
                    "agent": kwargs['file_id']['backup_jobs'][0]['agent'],
                    "scheduled_time": kwargs['file_id']['backup_jobs'][0]['scheduled_time'],
                    "progress_number_file":per, 
                    "accuracy":per,
                    "finished":False, 
                    "id": kwargs['file_id']['backup_jobs'][0]['id'],
                    "filename": file_path,
                }
            ]
        }

    task_q.put(backup_status)
    task_q.put(None)
    broadcast_ws_message(cl,task_queue=task_q,kill=False,msg_type_param="starting")


def uploaded_handler_part(sender, file_path,metadata,per, **kwargs):
    print(f"File '{file_path}' uploaded successfully.")
    cl = cl_socketio_obj #cktio.cl_socketio_obj
    task_q = queue.Queue()
    pNameText=kwargs['kwargs']['kwargs']['p_NameText']
    j_sta=kwargs['kwargs']['kwargs']['jsta']
    epn=getCodea()
    thiscurrentfile=float(kwargs['kwargs']['kwargs']['currentfile'])-1
    if thiscurrentfile<0: 
        thiscurrentfile=0
    totalfiles=float(kwargs['kwargs']['kwargs']['totalfiles'])
    # backup_status = {
    #     "backup_jobs": [
    #         {
    #             "name": pNameText,
    #             "scheduled_time": datetime.datetime.fromtimestamp(
    #                 float(j_sta)
    #             ).strftime("%H:%M:%S"),
    #             "agent": epn,
    #             "progress_number": float(100 * (float(per)+float(thiscurrentfile)))
    #             / float(totalfiles), 
    #             "id": j_sta,
    #         }
    #     ]
    # }
    backup_status = {
        "backup_jobs": [
            {
                "name": pNameText,
                "scheduled_time": datetime.datetime.fromtimestamp(float(j_sta)).strftime("%H:%M:%S"),
                "agent": epn,
                "progress_number": float(100 * (float(per/100)+float(thiscurrentfile)))/ float(totalfiles),
                "accuracy": float(100 * (float(per/100)+float(thiscurrentfile)))/ float(totalfiles),
                "finished": False,
                "id": j_sta
            }
        ]
    }
    task_q.put(backup_status)
    task_q.put(None)
    broadcast_ws_message(cl,task_queue=task_q,kill=False,msg_type_param="backup_data")

        
    
def connection_rejected_handler(sender, file_path, error):
    print(f"Connection rejected for file '{file_path}': {error}")

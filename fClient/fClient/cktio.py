"""
This script runs the fClient application using a development server.
"""

from argparse import Namespace
from ast import Try
from asyncio import SubprocessProtocol
from os import environ
import threading
from time import sleep
import time
from tkinter import TRUE, W
from turtle import window_height
from uu import Error
from venv import logger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from requests import head
import requests
from sqlalchemy import try_cast
from sqlalchemy.sql.util import selectables_overlap
import websocket
from websocket import WebSocket, create_connection, send
from fClient import app
# from zeroconf import Zeroconf, ServiceInfo
from flask import Flask, request, jsonify
import socket
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_cors import CORS

# from fClient import sktio
import socketio
import websocket
import ssl

# from fClient.defaultResponse import post_process_context


ssl_clx_context = ssl.create_default_context()
ssl_clx_context.check_hostname = False
ssl_clx_context.verify_mode = ssl.CERT_NONE

global r_cl
global cl
# def get_connected_RCL(r_clx: websocket.WebSocketApp =None,headers={}):
#     try:
#         #websocket.WebSocketApp("wss://testnet.binance.vision/ws/btcusdt@trade", on_message=on_message)
#         if not headers:
#             headers={"IP": str(app.config.get("getCodea",None)), "key": str(app.config.get("getCode",None)),"version":app.config.get("Version",None) }

#         r_clx=websocket.WebSocketApp(
#             f"ws://{app.config['server_ip']}:{app.config['server_port']}/socket.io/?EIO=4&transport=websocket",
#             header=headers,
#             on_open= on_open,
#             on_message= on_message,
#             on_error=on_error,
#             on_close=on_close,
#             on_ping= on_ping,
#             on_pong=on_pong,
#             on_cont_message=on_cont_message,
#             keep_running= True,
#             get_mask_key=get_mask_key,
#             #cookie=cookie,
#             #subprotocols=subprotocols,
#             on_data=on_data,
#             #socket: socket,
#         )
#             #clx.wait()
#         time.sleep(.5)
#         if r_clx:
#             return r_clx
#     except Exception as dere:
#         return None

# def run_ws():
#     r_cl = get_connected_RCL()
#     try:
#         r_cl.run_forever(
#             sslopt={"cert_reqs": ssl.CERT_NONE}
#             ,reconnect=True
#             ,ping_interval=30
#             ,ping_timeout=10
#         )
#     except Exception as exeee:
#         pass


# run_ws()


# def socketio_post_process(fn):
#     def wrapper(*args, **kwargs):
#         result = fn(*args, **kwargs)
#         return post_process_context(None, result, is_socket=True)
#     return wrapper

r_cl = socketio.Client(reconnection=True,reconnection_attempts=60*60*10,reconnection_delay=20,reconnection_delay_max=20)
cl_socketio_obj = socketio.Client(reconnection=True,reconnection_attempts=60*60*20,reconnection_delay=10,reconnection_delay_max=20)


@cl_socketio_obj.on("connect")
#@socketio_post_process
def handle_connect():
    print("Connected to server")


@cl_socketio_obj.on("show_me")
#@socketio_post_process
def handle_show_me(data):
    print("Connected to server cl_socketio_obj")


@cl_socketio_obj.on("backupprofilescreate")
#@socketio_post_process
def cl_on_backupprofilescreate(data):
    print("on(backupprofilescreate)")


###############################


@r_cl.on("disconnect")
#@socketio_post_process
def handle_connect_r_cl():
    print("disconnect to r_cl server")


@r_cl.on("close")
#@socketio_post_process
def handle_connect_r_cl():
    print("close to r_cl server")


@r_cl.on("connect")
#@socketio_post_process
def handle_connect_r_cl():
    print("Connected to r_cl server")

##  @r_cl.on("show_me") pasted in runserver.py of client ##kartik

@r_cl.on("scheduler_action_reschedule_response")
#@socketio_post_process
def schedulers_sctions_reschedule(json_data):
   
    rdata = json_data.get("rdata",None)
    if not json_data: return (jsonify({"result":"payload error" }),500)
    key = json_data.get("key", None)
    request_id = json_data.get("request_id", None)
    next_time=None
    allowed_days=None
    # action_info = json_data.get("action_info",None)
    # jobid=action_info.get("jobId",None)
    # action=action_info.get("action",None)
    # agentName = action_info.get("agent",None)
    # runEveryUnit = json_data.get("runEveryUnit",None)
    # runAgainEvery = json_data.get("runAgainEvery",None)
    rdata.get("action",None)
    action_info = rdata.get("action",None)
    jobid=action_info.get("jobId",None)
    action=action_info.get("action",None)
    agentName = action_info.get("agent",None)
    runEveryUnit = rdata.get("runEveryUnit",None)
    runAgainEvery = rdata.get("runAgainEvery",None)
    

    ip = "http://127.0.0.1:7777"
    # if action: action = str(action).lower()
    # if jobid: jobid = str(jobid).lower()
    # if agentName: agentName = str(agentName).lower()
    # if selected_agent_ip: 
    #     ip = str(selected_agent_ip).lower()
    # selected_agent_ip = str(selected_agent_ip).lower()
    # if key: key = str(key).lower()
    response=None
    resp=None
    if action =="reschedule":
        try:  
            if ip and jobid:
                url = str(f'{ip}/scheduler/jobreschedule')
                response = requests.post(url,json=rdata, timeout=200)
                
        except Exception as exs:
            print(exs)

    if response:
        if response.status_code == 200 or response.status_code == 204:
            resp ={"response_content":response.json(),"response_code":200}      
        
    combined_response_data = {
        "request_id": request_id,
        "key": key,
        "combined_response": resp,
    }

    r_cl.emit("scheduler_action_reschedule_response", combined_response_data)

@r_cl.on("scheduler_action_response")
#@socketio_post_process
def handle_scheduler_job_rename_response(json_data):
    # {"key": "key","request_id": request_id}
    key = json_data.get("key", None)
    request_id = json_data.get("request_id", None)
    jobid=json_data.get("jobid",None)
    agentName = json_data.get("agentName",None)
    action = json_data.get("action",None)
    jobNewName = json_data.get("jobNewName",None)
    resp=None
    response=None
    bTry=False
    ip = "http://127.0.0.1:7777"
    if action =="delete":
        try:  
            if ip and jobid:
                url = str(f'{ip}/scheduler/{key}/jobs/{jobid}')
                print("ip")
                response = requests.delete(url, timeout=20)
        except Exception as exs:
            print(exs)
            bTry=True
    elif action =="play":
        try:  
            if ip and jobid:
                url = str(f'{ip}/scheduler/{key}/jobs/{jobid}/resume')
                print("ip")
                response = requests.post(url, timeout=20)
        except Exception as exs:
            print(exs)
            bTry=True
    elif action =="pause":
        try:  
            if ip and jobid:
                url = str(f'{ip}/scheduler/{key}/jobs/{jobid}/pause')
                print("ip")
                response = requests.post(url, timeout=20)
        except Exception as exs:
            print(exs)
            bTry=True
    elif action =="rename":
        try:  
            if ip and jobid:
                url = str(f'{ip}/scheduler/jobrename')
                response = requests.post(url,json={"job_id":jobid,"new_job_name":jobNewName}, timeout=20)
        except Exception as exs:
            print(exs)
            bTry=True
    elif action =="reschedule":
        pass

    combined_response_data = {
            "request_id": request_id,
            "key": key,
            "combined_response": None,
        }
    if response is not None:
        if response.status_code in (200, 204):
            print("Job has been deleted")

            combined_response_data = {
                "request_id": request_id,
                "key": key,
                "combined_response": {
                    "response_content": response.content,
                    "response_code": response.status_code,
                },
            }
        else:
            print(f"Job action failed with status {response.status_code}")

        print(f"Combined response >>> {combined_response_data}")
        r_cl.emit("scheduler_action_response", combined_response_data)

    else:
        print("No response received from server")
        r_cl.emit("scheduler_action_response", combined_response_data)

    
from urllib.parse import urlparse
@r_cl.on("scheduler_response")
#@socketio_post_process
def handle_scheduler_response(json_data):

    # {"key": "key","request_id": request_id}
    key = json_data.get("key", None)
    request_id = json_data.get("request_id", None)

    ip = "http://127.0.0.1:7777"
    url = str(f"{ip}/scheduler/{key}")
    url2 = str(f"{ip}/scheduler/{key}/jobs")
    fields_to_extract = [
        
        "day_of_week",
        "hour",
        "id",
        "minute",
        "name",
        "next_run_time",
        "second",
    ]

    s = requests.session()
    response = s.get(url, timeout=200)
    response2 = s.get(url2, timeout=200)
    combined_response_data = {
        "request_id": request_id,
        "key": key,
        "combined_response": None,
    }
    if response.status_code == 200 and response2.status_code == 200:
        data = response2.json()
        # filtered_data = [
        #     {key: entry[key] for key in fields_to_extract if key in entry}
        #     for entry in data
        # ]
        filtered_data = []
        for entry in data:
            d={key: entry[key] for key in fields_to_extract if key in entry}
            d.update({"src_location":entry["args"][0]})
            d.update({"repo":entry["args"][3]})
            filtered_data.append(d)
        
        ws_url = r_cl.connection_url
        parsed = urlparse(ws_url)
        server_ip = parsed.hostname

        xserver = str(app.config.get("server_ip", ""))
        xcode = str(app.config.get("getCode", ""))
        combined_response_data = {
            "request_id": request_id,
            "key": key,
            "combined_response": {"scheduler": response.json(), "jobs": filtered_data},
            "XRefServer" : server_ip, #request.remote_addr,
            "XServer": xserver,
            "XIDX": xcode         
        }
         
        print("Connected scheduler_response")
        r_cl.emit("scheduler_response", combined_response_data)
    


@r_cl.on("browse_response")
def handle_browse_response(json_data):

    # {"key": "key","request_id": request_id}
    key = json_data.get("key", None)
    request_id = json_data.get("request_id", None)
    current_path = json_data.get("path", None)
    xserver = str(app.config.get("server_ip", ""))
    xcode = str(app.config.get("getCode", ""))
    ip = "http://127.0.0.1:7777"
    url = str(f"{ip}/api/browse")

    resdata=None
    s = requests.session()
    response = requests.post(
        url,
        json={"path": current_path},
        headers={"Accept-Encoding": "application/gzip"},
        timeout=20,
    )
    combined_response_data = {
        "request_id": request_id,
        "key": key,
        "combined_response": None,
        "XRefServer" :xserver,
        "XServer": xserver,
        "XIDX": xcode 
    }
    if response.status_code == 200:
        resdata = response.content
        xserver = str(app.config.get("server_ip", ""))
        xcode = str(app.config.get("getCode", ""))
        combined_response_data = {
            "request_id": request_id,
            "key": key,
            "combined_response": response.json(),
            "XRefServer" :xserver,
            "XServer": xserver,
            "XIDX": xcode         
        }

        r_cl.emit("browse_response", combined_response_data)

    print("Connected browse_response")


# @cl.on('ping')
# def handle_ping():
#     print('Received ping from client')
#     try:
#         cl.emit('pong')
#     except Exception as e:
#         print("asfd")


def on_open(wsapp, message="asdf"):
    print(">>>>>_____>>>>>> " + message)


def on_cont_message(wsapp, message):
    print("Got a ping! A pong reply has already been automatically sent.")


def get_mask_key(wsapp, message):
    print("Got a pong! No need to respond")


def on_data(wsapp, data, o, t):
    print(f"Error: {data}")


def on_message(wsapp, message):
    print(">>>>>_____>>>>>> " + message)


def on_ping(wsapp, message):
    print("Got a ping! A pong reply has already been automatically sent.")


def on_pong(wsapp, message):
    print("Got a pong! No need to respond")


def on_error(wsapp, error):
    print(f"Error: {error}")


def on_close(wsapp, close_status_code, close_msg):
    print(f"Closed with status code {close_status_code}: {close_msg}")


def cktio_main():

    print("Sending 'Hello, World'ddd...")

    websocket.enableTrace(True)
    cl_socketio_obj.connect("ws://192.168.2.97:53335", wait=True)

    sleep(5)
    # print(cl.recv())
    cl_socketio_obj.wait()
    # cl.disconnect()


def get_connected(clx, headers={}, auth_body={}):
    try:
        if not auth_body:
            auth_body = {
                "IP": str(app.config.get("getCodea", None)),
                "key": str(app.config.get("getCode", None)),
                "version": app.config.get("Version", None),
            }
        try:
            if clx.connected:
                clx.disconnect()
        except:
            pass
        if not clx.connected:
            clx.connect(
                f"ws://{app.config['server_ip']}:{app.config['server_port']}?asdf=ifaopsdfipasidpfips",
                wait_timeout=200,
                retry=True,
                headers=headers,
                auth=auth_body,
            )
            # clx.wait()
        time.sleep(0.5)
        if clx.connected:
            url = f'http://localhost:7777/callself'
            requeston = requests.post(url, {})
            return True, clx
    except Exception as dere:
        return False, None

    return False, None


def send_message(clx, message_type, message_body, headers={}, disconnect=True):
    ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
        s.close()
    except:
        print("No Internet found")
    try:
        # if clx.connected: clx.disconnect()
        if not clx.connected:

            isConnected, clx = get_connected(clx, headers=headers)
            if isConnected:
                time.sleep(0.5)
                try:
                    if not message_body.get("e_key", None):
                        message_body.update("e_key", app.config["getCode"])
                except:
                    pass
                try:
                    if not message_body.get("e_name", None):
                        message_body.update("e_name", app.config["getCodea"])
                except:
                    pass

                try:
                    if not message_body.get("e_ip", None):
                        message_body.update("e_ip", ip)
                except:
                    pass

                clx.emit(message_type, message_body)
                time.sleep(0.5)
                if disconnect:
                    clx.disconnect()
                else:
                    clx.wait()
    except Exception as dddd:
        pass


def run_ws(r_clx):
    try:
        # send_message(r_cl,"message_type", "message_body",headers={"WST_D":True},disconnect=False)
        # global r_cl
        x, dd = get_connected(r_clx, headers={"WSTD": "dfa"}, auth_body=None)
        return dd
    except Exception as exeee:
        print("ERROR CREATING REMOTE Socket")
        # finally:
        return None
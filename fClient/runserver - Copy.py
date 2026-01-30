"""
This script runs the fClient application using a development server.
"""

from argparse import Namespace
from ast import Try
from asyncio import SubprocessProtocol
from os import environ
from time import sleep
import time
from tkinter import TRUE, W
from turtle import window_height
from uu import Error
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from sqlalchemy.sql.util import selectables_overlap
import websocket
from websocket import create_connection, send
from fClient import app
from zeroconf import Zeroconf, ServiceInfo
from flask import Flask, request, jsonify
import socket
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_cors import CORS
from fClient import sktio
from fClient.fingerprint import getCode

cors = CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
import socketio
import websocket

global cl
cl = socketio.Client()

import websocket


@cl.on("connect")
def handle_connect():
    print("Connected to server")


@cl.on("ping")
def handle_ping():
    print("Received ping from client")
    try:
        cl.emit("pong")
    except Exception as e:
        print("asfd")


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


def show_users():
    """Print all users."""
    try:
        with db.app.app_context():
            print(User.query.all())
    except Exception as e:
        print(str(e))


class Config:
    """App configuration."""

    JOBS = [
        {
            "id": "job010320241544",
            "func": show_users,
            "trigger": "interval",
            "seconds": 2,
        }
    ]

    # SQLALCHEMY_DATABASE_URI = "sqlite:///flask_context.db"
    # SCHEDULER_JOBSTORES = {
    #     "default": SQLAlchemyJobStore(url="sqlite:///flask_context.db")
    # }

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(app.config.get("getCode",None))

    SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(url="sqlite:///" + str(app.config.get("getCode",None)))}

    SCHEDULER_API_ENABLED = True


# def brdcst():
#     desc = {'version':'1.0'}
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(("8.8.8.8", 7777))
#     ip = s.getsockname()[0]
#     s.close()
#     info = ServiceInfo("_http._tcp.local.",
#                    "_led._http._tcp.local.",
#                    port= 7777,
#                    addresses= [socket.inet_aton(ip)]
#                    ,priority=  0,weight= 0,properties=
#                    desc)
#     Zeroconf().register_service(info)

if __name__ == "__main__":
    HOST = environ.get("SERVER_HOST", "localhost")
    try:
        PORT = int(environ.get("SERVER_PORT", "5555"))
    except ValueError:
        PORT = 5555
    # brdcst()
    print("Sending 'Hello, World'ddd...")

    websocket.enableTrace(True)
    cl.connect("http://192.168.2.97:53335", wait=True)

    # cl.send("")
    # cl.send(websocket.ABNF.OPCODE_PING)
    sleep(5)
    # print(cl.recv())
    cl.wait()
    cl.disconnect()
    # wsapp =  websocket.WebSocketApp("ws://192.168.29.156:53335/socket.io/?transport=polling&EIO=4&t=1709623348.818709", on_message=on_message,on_ping=on_ping)
    # wsapp =  websocket.WebSocketApp("ws://192.168.29.156:53335/socket.io/?transport=websocket&EIO=4&t=1709623348.818709", on_message=on_message,on_ping=on_ping,on_pong=on_pong)
    # wsapp.run_forever()

    # srcName ="ws://192.168.29.156:53335/socket.io/connect/?transport=websocket&EIO=4&t="+str(time.time())
    # # print(srcName)

    # wsapp =  websocket.WebSocketApp(srcName, on_ping=on_ping,on_pong=on_pong,on_error=on_error,on_close=on_close)
    # # wsapp.run_forever(ping_interval=60, ping_timeout=20, ping_payload="This is an optional ping payload")
    # while True:
    #     try:
    #         # wsapp.run_forever(ping_interval=60, ping_timeout=20, ping_payload="This is an optional ping payload")
    #         wsapp.run_forever()
    #     except KeyboardInterrupt:
    #         break
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         time.sleep(1)
    # ws = create_connection(srcName)

    # # Perform the initial connection handshake
    # ws.send("2probe")
    # ws.recv()

    # # Send a ping and wait for the pong
    # while True:
    #     ws.send("5")
    #     response = ws.recv()
    #     if response == "3":
    #         print("Received pong from server")
    #     time.sleep(1)

    print("=========================")
    # wsa = create_connection("ws://192.168.29.156:53335")#,http_proxy_port="53335",subprotocols=["quividicontent","binary", "base64"])
    # print(wsa.recv())
    # print("Sending 'Hello, World'...")
    # wsa.send("Hello, World")
    # print("Sent")
    # print("Receiving...")
    # result =  wsa.recv()
    # print("Received '%s'" % result)
    # wsa.close()

    # wsa= websocket.WebSocket();
    # wsa.connect("ws://192.168.29.156:53335/",origin="http://192.168.29.156:7777")
    # wsa.send("Hello, Server")
    # print(wsa.recv())
    # wsa.close()

    app.config.from_object(Config())
    db = SQLAlchemy()
    db.app = app
    db.init_app(app)

    class User(db.Model):
        """User model."""

        id = db.Column(db.Integer, primary_key=True)  # noqa: A003, VNE003
        username = db.Column(db.String(80), unique=True)
        email = db.Column(db.String(120), unique=True)

    # initialize scheduler
    scheduler = APScheduler()
    # if you don't wanna use a config, you can set options here:
    # scheduler.api_enabled = True
    scheduler.init_app(app)

    # interval example
    @scheduler.task("interval", id="do_job_1", seconds=30, misfire_grace_time=900)
    def job1():
        print("Job 1 executed")

    # cron examples
    @scheduler.task("cron", id="do_job_2", minute="*")
    def job2():
        print("Job 2 executed")

    @scheduler.task("cron", id="do_job_3", week="*", day_of_week="sun")
    def job3():
        print("Job 3 executed")

        scheduler.add_listener(job2, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    try:
        scheduler.shutdown(wait=False)
    except Exception as e:
        print(str(e))
    # scheduler.start()
    app.run(host="0.0.0.0", port=7777, debug=True, use_reloader=False)

    # sktio.run(app, host="0.0.0.0", port=7777, debug=True, use_reloader=False)

"""
The flask application package.
"""

from ast import Import
from flask import Flask, sessions, request, make_response
import sys,os
import logging
from flask_socketio import SocketIO
import threading
from engineio.async_drivers import threading
import websocket
from werkzeug.exceptions import HTTPException

#from reactapp.reactapp import ReactAppProxyUpdater
from reactapp.reactapp import ReactProxyReplacer2 

# app =Flask(__name__, static_url_path='/static', static_folder='../reactapp')
# app =Flask(__name__, static_url_path='/reactapp', static_folder='../reactapp')
# if getattr(sys, "frozen", False):
#     print("_MMMMMMMMM")
#     base_dir = os.path.join(sys._MEIPASS)
#     static_url_path = os.path.join(base_dir, 'rapp','static')
#     static_path = os.path.join(base_dir, 'rapp')
#     template_path = os.path.join(base_dir, 'rapp')    
#     print(base_dir)
#     print(static_url_path)
#     print(static_path)
#     print(template_path)
#     app = Flask(__name__, static_url_path=static_url_path, static_folder=static_path,template_folder=template_path) 
# else:
#     app = Flask(__name__, static_url_path='/rapp/static', static_folder='rapp') 

#from werkzeug.middleware.profiler import ProfilerMiddleware

app = Flask(__name__, static_url_path='/rapp/static', static_folder='rapp') 
app = Flask(__name__, static_url_path='', static_folder='rapp')
from FlaskWebProject3.ephemeral_crypto import init_crypto ##kartik
init_crypto(app)  ##kartik
from fingerprint import getCodeHost,getCode,getKey,getRequestKey,get_hKey

#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=r"D:\tmp_f\flask_profiler") 
app.config["getCode"]=getCode()
app.config["getCode"]= getCode()
app.config["getCodea"]=getCodeHost()
app.config["getCodeHost"]=str(app.config.get("getCodea",None))
app.config["getKey"]=getKey()
app.config["getRequestKey"]=getRequestKey()
app.config["get_hKey"]=get_hKey() 
if hasattr(sys, '_MEIPASS'): 
    print ("=================================================")
    print ("=================================================")
    print ("=================================================")
    app.static_folder = os.path.join(sys._MEIPASS, 'rapp')
# updater = ReactAppProxyUpdater('package.json')
# updater.update_proxy()

project_dir = app.static_folder

ips=["192.168.2.61","192.168.2.58","192.168.2.61","192.168.2.97","192.168.2.21","192.168.2.22","192.168.43.34","192.168.2.26","192.168.2.253","192.168.2.200","192.168.2.20","192.168.2.75"]
for ip in ips:
    replacer = ReactProxyReplacer2(project_directory=project_dir,old_proxy_value=ip)
    replacer.replace_proxy_in_directory()
try:
    replacer = ReactProxyReplacer2(project_directory=project_dir
                                   ,old_proxy_value="__LICSERVERLINK__"
                                   ,new_proxy_value="192.168.2.201:5000")
    replacer.replace_proxy_in_directory()
except:
    print("asdf")

try:
    replacer = ReactProxyReplacer2(project_directory=project_dir
                                   ,old_proxy_value="__UPGRADEURL__"
                                   ,new_proxy_value="http://192.168.2.201:5000")
    replacer.replace_proxy_in_directory()
except:
    print("asdf")


#sktio =   SocketIO(app,cors_allowed_origins="*",logger=False, engineio_logger=False,async_mode= "threading")
sktio =   SocketIO(app,cors_allowed_origins="*",logger=False, engineio_logger=False,async_mode= "threading", ping_interval=10, ping_timeout=5) ##kartik

error_logger = logging.getLogger("server_error")
if not error_logger.handlers:
    os.makedirs("every_logs", exist_ok=True)
    error_handler = logging.FileHandler(
        os.path.join("every_logs", "server_error.log"),
        mode="a",
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)


@app.errorhandler(Exception)
def handle_unhandled_exception(error):
    try:
        route = request.path
        method = request.method
        body = request.get_data(as_text=True) or ""
    except Exception:
        route = "<no-request-context>"
        method = "<no-request-context>"
        body = ""

    if len(body) > 4000:
        body = body[:4000] + " ... (truncated)"

    error_logger.exception(
        "Unhandled exception",
        extra={
            "route": route,
            "method": method,
            "body": body,
        },
    )

    if isinstance(error, HTTPException):
        return error.get_response()
    return make_response("Internal Server Error", 500)


from flask_talisman import Talisman, GOOGLE_CSP_POLICY ##kartik 
custom_csp = {
    'default-src': ["'self'"],
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        'https://cdn.jsdelivr.net'
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        'https://fonts.googleapis.com',
        'https://cdn.jsdelivr.net',
        "https://www.youtube.com",
    ],
    'font-src': [
        "'self'",
        'https://fonts.gstatic.com',
        'data:' 
    ],
    'img-src': [
        "'self'",
        'data:',
        'blob:'
    ],
    'connect-src': [
        "'self'",
        'https://chatbot.apnabackup.com'
    ],
    'frame-src': [
        "'self'",
        "https://www.youtube.com"
    ]
}

permissions_policy = {
    "microphone": "(self)"
}

Talisman(app, content_security_policy=custom_csp, permissions_policy=permissions_policy, force_https=False, x_xss_protection=True) ##kartik

#sktio.init_app(app)

#from .socketio import sktio 

import FlaskWebProject3.views
from sqlite_managerA import SQLiteManager,RowWrapper
#from sqlite_manager import SQLiteManager
global gserver 
from .shared_data import notifications
from FlaskWebProject3.notifications.views import notifications_bp
from FlaskWebProject3.live_data.views import live_data_bp
from FlaskWebProject3.cm import CredentialManager
from FlaskWebProject3.unc import NetworkShare
from gd.GDClient import GDClient 
# from FlaskWebProject3.sfx import ZipToSFX commented 21/04/2025
from FlaskWebProject3.csystemreport import ServerSystemReportGenerator
# app.register_blueprint(notifications_bp) commented 21/04/2025
# app.register_blueprint(live_data_bp) commented 21/04/2025


from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTExtendedException
from flask import jsonify
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', 'rO5iDMtuWwapBX2AgvXe6GclgUO9Pg33')
jwt_app = JWTManager()
jwt_app.init_app(app)

# import argparse
# import logging
# from threading import Thread
import threading
from time import sleep, time
# from typing import cast

# from pytz import ZERO
# from zeroconf import (
#     IPVersion,
#     ServiceBrowser,
#     ServiceStateChange,
#     Zeroconf,
#     ZeroconfServiceTypes,
# )
# from config_management.config_handler import load_config, save_config
# import fClient
# from fClient import fingerprint
# from fClient.fingerprint import getCode, getKey
# from key_management import get_key as get_fixed_length_key
# from config_management import create_config, add_or_update_config, delete_config
from fClient import app
import os

# from key_management.key_handler import get_key

config_file = os.path.join(app.config["AppFolders"].site_config_dir, "config.json.enc")

#########################################


# class SearchSrvr:
    
#     def __init__(self, services=None, ip_version=IPVersion.All):
#         import hashlib
#         """Initialize the ZeroconfService."""
#         if services is None:
#                 # "_led._http._tcp.local.",
#                 # "_leda._http._tcp.local.",
#                 # #"E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD._http._tcp.local.",
#                 # "_ledas._http._tcp.local.",
#                 # "_http._tcp.local.",
#                 # "_hap._tcp.local."
#             services=["_http._tcp.local."]
#             services.append("_https._tcp.local.")

#             # services=["E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD_http._tcp.local."]
#             # services.append("E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD_https._tcp.local.")
#             # services.append(str(hashlib.md5(getCode().encode()).hexdigest())+"_http._tcp.local.")
#             # services.append(str(hashlib.md5(getCode().encode()).hexdigest())+"_https._tcp.local.")
#         self.services = services
#         self.ip_version = ip_version
#         self.zeroconf = None
#         self.browser = None
#         self.thread = None

#     def on_service_state_change_old(self, zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange) -> None:
#         """Handle the state change of services."""
#         print(f"Service {name} of type {service_type} state changed: {state_change}")

#         if state_change in [ServiceStateChange.Added, ServiceStateChange.Updated]:
#             info = zeroconf.get_service_info(service_type, name)
#             print(f"Info from zeroconf.get_service_info: {info}")

#             if info:
#                 addresses = [
#                     "%s:%d" % (addr, cast(int, info.port))
#                     for addr in info.parsed_scoped_addresses()
#                 ]
#                 print("  Addresses: %s" % ", ".join(addresses))
#                 print(f"  Weight: {info.weight}, priority: {info.priority}")
#                 print(f"  Server: {info.server}")
#                 if info.properties:
#                     print("  Properties are:")
#                     for key, value in info.properties.items():
#                         print(f"    {key!r}: {value!r}")
#                 else:
#                     print("  No properties")
#             else:
#                 print("  No info")
#             print("\n")
    
#     def on_service_state_change(
#         zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
#     ) -> None:
#         try:
#             print(f"Service {name} of type {service_type} state changed: {state_change}")

#             if (
#                 state_change is ServiceStateChange.Added
#                 or state_change is ServiceStateChange.Updated
#             ):
#                 try:
#                     info = zeroconf.get_service_info(service_type, name)
#                     print("Info from zeroconf.get_service_info: %r" % (info))

#                     if info:
#                         from fClient import app
#                         import os

#                         addresses = [
#                             "%s:%d" % (addr, cast(int, info.port))
#                             for addr in info.parsed_scoped_addresses()
#                         ]
#                         #print("  Addresses: %s" % ", ".join(addresses))
#                         #print("  Weight: %d, priority: %d" % (info.weight, info.priority))
#                         #print(f"  Server: {info.server}")

#                         server = info.properties.get(b"server", b"34545345234523452")
#                         b_both_matched =False

#                         if str(server.decode())!="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD":
#                             print(str(server.decode()))
#                         elif str(server.decode())=="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD":
                
#                             higram = info.properties.get(b"higram", None)
#                             lowgram = info.properties.get(b"lowgram", None)
                
#                             from urllib.parse import urlparse
#                             import json
#                             if type(app.config.get("resj",None)) is str: 
#                                 app.config["resj"] = json.loads(app.config.get("resj",None))
#                             if app.config.get("resj",None): ## license exist
#                                 print (app.config["resj"])
#                                 if app.config["resj"]['server'].get('activationkey',None):
#                                     b_both_matched = app.config["resj"]['server'].get('activationkey',"") == str(lowgram)
                    
#                             url = str(addresses[0])
#                             if not url.startswith(("http://", "https://")):
#                                 url = "http://" + url
#                                 parsed_url = urlparse(url)
#                                 domain = parsed_url.hostname
#                                 port = parsed_url.port

#                                 #commented on 18/10
#                                 # app.config["server_ip"] = str(domain)
#                                 # os.environ["server_ip"] = str(domain)

#                                 # app.config["server_port"] = str(port)
#                                 # os.environ["server_port"] = str(port)

#                                 # gk = get_key(fingerprint.getCode())
#                                 gk = get_key(str(app.config.get("getCode",None)))
#                                 add_or_update_config(config_file, gk, "server_ip", str(domain))
#                                 import requests, base64, gzip
#                                 json_data = str(app.config.get("getRequestKey",None))
#                                 headers = {
#                                     "Accepted-Encoding": "gzip,deflate,br",
#                                     "Content-Type": "application/json",
#                                     "tcc": base64.b64encode(
#                                         str(app.config.get("getCode",None)).encode("UTF-8"),
#                                     ),
#                                 }
#                                 # try:
#                                 #     res = requests.post(url+"/restister",json=fingerprint.getRequestKey(),headers=headers)
#                                 #     if res.ok:
#                                 #         print("set")
#                                 #     else:
#                                 #         print("not set")
#                                 # except Exception as ess:
#                                 #     print (str(ess))
                    
#                                 if check_agent_license_update():
#                                     app.config["server"] = str(addresses[0])
#                                     os.environ["server"] = str(addresses[0])
#                                     zeroconf.close()
#                                     return addresses[0]

#                                 # if info.properties:
#                                 #     print("  Properties are:")
#                                 #     for key, value in info.properties.items():
#                                 #         print(f"    {key!r}: {value!r}")
#                                 # else:
#                                 #     print("  No properties")
                    
                
#                     else:
#                         print("searching")
#                     print("searching\n")
#                 except:
#                     print ("error fetching service")
#             elif(
#                 state_change is ServiceStateChange.Removed
#             ):
#                 print("4")
#             print("4w") 
#         except Exception as dw:
#             print(str(dw))

#     def browse_services(self):
#         """Start the service browsing."""
#         logging.basicConfig(level=logging.DEBUG)
#         self.zeroconf = Zeroconf(ip_version=self.ip_version)

#         # self.browser = ServiceBrowser(self.zeroconf, self.services, handlers=[self.on_service_state_change])
#         self.browser = ServiceBrowser(self.zeroconf, self.services, handlers=[on_service_state_change])
#         try:
#             t1 = time()+5
#             while True: #time()<t1: #
#                 sleep(0.1)  # Keep the thread alive without consuming too many resources.
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.zeroconf.close()

#     def start(self):
#         """Start Zeroconf browsing in a separate thread."""
#         self.thread = threading.Thread(target=self.browse_services)
#         self.thread.daemon = True
#         self.thread.start()

#     def stop(self):
#         """Stop Zeroconf service browsing."""
#         if self.zeroconf:
#             self.zeroconf.close()
#         if self.thread:
#             self.thread.join()


# #########################################

# def on_service_state_change(
#     zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
# ) -> None:
#     print(f"Service {name} of type {service_type} state changed: {state_change}")

#     if (
#         state_change is ServiceStateChange.Added
#         or state_change is ServiceStateChange.Updated
#     ):
#         try:
#             info = zeroconf.get_service_info(service_type, name)
#             print("Info from zeroconf.get_service_info: %r" % (info))

#             if info:
#                 from fClient import app
#                 import os

#                 addresses = [
#                     "%s:%d" % (addr, cast(int, info.port))
#                     for addr in info.parsed_scoped_addresses()
#                 ]
#                 #print("  Addresses: %s" % ", ".join(addresses))
#                 #print("  Weight: %d, priority: %d" % (info.weight, info.priority))
#                 #print(f"  Server: {info.server}")

#                 server = info.properties.get(b"server", b"34545345234523452")
#                 b_both_matched =False

#                 if str(server.decode())!="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD":
#                     print(str(server.decode()))
#                 elif (not bool(app.config.get("blicfound",None))) and str(server.decode())=="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD":# and bool(info.properties.get(b"blicfound", False)) :
                
#                     name= info.name.replace ( "."+ info.type,"")
#                     # thisfound= name == fingerprint.get_hKey()
#                     thisfound= name == str(app.config.get("get_hKey",None))
#                     lowgram = info.properties.get(b"lowgram", None)#server
#                     higram = info.properties.get(b"higram", None)
#                     if thisfound:
#                         #app.config["blicfound"]=True
                
#                         from urllib.parse import urlparse
#                         import json
#                         if type(app.config.get("resj",None)) is str: 
#                             app.config["resj"] = json.loads(app.config.get("resj",None))
#                         if app.config.get("resj",None): ## license exist
#                             print (app.config["resj"])
#                             if app.config["resj"]['server'].get('activationkey',None):
#                                 b_both_matched = app.config["resj"]['server'].get('activationkey',"") == str(lowgram.decode("UTF-8"))
                    
#                         url = str(addresses[0])
#                         if not url.startswith(("http://", "https://")):
#                             url = "http://" + url
#                             parsed_url = urlparse(url)
#                             domain = parsed_url.hostname
#                             port = parsed_url.port
#                             #commented on 18/10
#                             # app.config["server_ip"] = str(domain)
#                             # os.environ["server_ip"] = str(domain)

#                             # app.config["server_port"] = str(port)
#                             # os.environ["server_port"] = str(port)
#                             #gk = get_key(fingerprint.getCode())
#                             gk = get_key(str(app.config.get("getCode",None)))
#                             add_or_update_config(config_file, gk, "server_ip", str(domain))
#                             import requests, base64, gzip
#                             json_data = str(app.config.get("getRequestKey",None))
#                             # headers = {
#                             #     "Accepted-Encoding": "gzip,deflate,br",
#                             #     "Content-Type": "application/json",
#                             #     "tcc": base64.b64encode(
#                             #         fingerprint.getCode().encode("UTF-8"),
#                             #     ),
#                             # }
#                             # try:
#                             #     res = requests.post(url+"/restister",json=fingerprint.getRequestKey(),headers=headers)
#                             #     if res.ok:
#                             #         print("set")
#                             #     else:
#                             #         print("not set")
#                             # except Exception as ess:
#                             #     print (str(ess))
                    
#                             # if check_agent_license_update():
#                             #     app.config["server"] = str(addresses[0])
#                             #     os.environ["server"] = str(addresses[0])
#                             #     return addresses[0]
                             
#                             app.config["server"] = str(addresses[0])
#                             os.environ["server"] = str(addresses[0])
#                             #return addresses[0]

#                             # if info.properties:
#                             #     print("  Properties are:")
#                             #     for key, value in info.properties.items():
#                             #         print(f"    {key!r}: {value!r}")
#                             # else:
#                             #     print("  No properties")
#                     else:
#                         from urllib.parse import urlparse
#                         import json
#                         print("this computer is not in list")
#                         url = str(addresses[0])
#                         if not url.startswith(("http://", "https://")):
#                             url = "http://" + url
#                         parsed_url = urlparse(url)
#                         domain = parsed_url.hostname
#                         port = parsed_url.port

#                         #commented on 18/10
#                         # app.config["server_ip"] = str(domain)
#                         # os.environ["server_ip"] = str(domain)

#                         # app.config["server_port"] = str(port)
#                         # os.environ["server_port"] = str(port)
#                         check_agent_license_update()
#             else:
#                 print("searching")
#             print("searching\n")
#         except:
#             print ("error fetching service")
#     elif(
#         state_change is ServiceStateChange.Removed
#     ):
#         print("4")
#     print("4w") 

    

# # if __name__ == '__main__':


# def dwwxx( zeroconf):
#     import base64
#     try:
#         logging.basicConfig(level=logging.DEBUG)
#         # parser = argparse.ArgumentParser()
#         # parser.add_argument('--debug', action='store_true')
#         # parser.add_argument('--find', action='store_true', help='Browse all available services')
#         # version_group = parser.add_mutually_exclusive_group()
#         # version_group.add_argument('--v6-only', action='store_true')
#         # version_group.add_argument('--v4-only', action='store_true')
#         # args = parser.parse_args()

#         # if args.debug:
#         #     logging.getLogger('zeroconf').setLevel(logging.DEBUG)
#         # if args.v6_only:
#         #     ip_version = IPVersion.V6Only
#         # elif args.v4_only:
#         #     ip_version = IPVersion.V4Only
#         # else:
#         #     ip_version = IPVersion.All

#         logging.getLogger('zeroconf').setLevel(logging.DEBUG)
#         ip_version = IPVersion.All

#         # zeroconf = Zeroconf(ip_version=ip_version)
#         services = ["_http._tcp.local.", "_hap._tcp.local."]
#         services = [
#             "E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD._http._tcp.local.",
#             "_ledas._http._tcp.local.",
#         ]
#         services = ["E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD._http._tcp.local.","_ledas._http._tcp.local.", "_http._tcp.local.", "_hap._tcp.local."]
#         # if args.find:
#         #     services = list(ZeroconfServiceTypes.find(zc=zeroconf))

#         #print("\nBrowsing %d service(s), press Ctrl-C to exit...\n" % len(services))
#         browser = ServiceBrowser(
#             zeroconf,
#             services,
#             handlers=[on_service_state_change],
#         )
#         # ti1= int(time())+20
#         # while (int(time())<int(ti1)) or not browser.done:
#         #         print("waiting...")
             
#         # if app.config.get("server", None):
#         #     browser.cancel()
#         #     zeroconf.close()
#         # print("waiting..  ..  ..")

#     except Exception as ere :
#         print(str(ere))
#     finally:
#         #zeroconf.close()
#         browser.cancel()

        
# def dww():
#     zeroconf = Zeroconf(ip_version=3)
#     from fClient import app
#     import os

#     try:
#         ti1= int(time())+5
#         while( app.config.get("server", None) == None):
#             if (int(time())>int(ti1)) :
#                 sd = dwwxx(zeroconf)                
#                 ti1= int(time())+5

#                 # zeroconf.close()
#                 # zeroconf = Zeroconf(ip_version=3)

#     except KeyboardInterrupt:
#         pass
#     finally:
#         zeroconf.close()
    


def check_agent_license(iter=0):
    blicfound = False
    if check_agent_license_local():
        return True
    # else:
    #     if check_agent_license_update():
    #         return True

    return blicfound


def check_agent_license_local(iter=0):
    servermatched = False
    blicfound = False
    import requests
    import gzip
    import base64
    import json
    from pathlib import Path
    dagent=[]
    json_data = str(app.config.get("getRequestKey",None))
    json_data = app.config.get("getRequestKey",None)
    if app.config.get("AppFolders", None):
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
                from builtins import open as fileopen
                for fle in f_files:
                    try:
                        with fileopen(fle, "r") as licf:
                            text = licf.read()
                            text = [text[i : i + 9][:8] for i in range(0, len(text), 9)]
                            text = "".join(text)
                            text = bytes.fromhex(text)
                            text = base64.b64decode(text)
                            # text = gzip.decompress(text)
                            text = text.decode("UTF-8")
                            text = json.loads(text)
                            servermatched = text.get("server", "server").get(
                                "activationkey", "activationkey"
                            ) == json_data.get("activationkey", "activationkeynotfound")

                            servermatched=True
                            blicfound=False
                            if text.get("last_updated",None):
                                    xt= float(text.get("last_updated",str(time()+5)))
                                    servermatched= not( xt + 1*60*60 < time())
                                    app.config["blicfound"]=blicfound
                                  

                            if servermatched:
                                app.config["resj"] = text
                                dagent = [
                                    base64.b64decode(bytes.fromhex(dd.get("activationkey","").replace('-', ''))).decode("UTF-8")
                                    #dd.get("activationkey", "")
                                    for dd in text.get("Endpoints", []) 
                                ]
                                dagent=list(set(dagent))
                                app.config["agent_activation_keys"] = dagent
                                josonkey= base64.b64decode(bytes.fromhex(json_data.get("activationkey", "activationkeynotfound").replace('-', ''))).decode("UTF-8")
                                blicfound = josonkey in dagent
                                app.config["blicfound"]=blicfound
                            print("=======text========")
                            print(text)
                            print("=======text========")
                            if blicfound or (blicfound and iter == 2):
                                return blicfound                                
                        if not blicfound:
                            os.remove(fle)
                            sleep(5)
                    except Exception as see:
                        print("invalid license detected" + str(see))

        except:
            print("")
            d = ""
            return False
    return blicfound


def check_agent_license_update(iter=0):
    blicfound = False
    import requests, gzip, base64, json
    from pathlib import Path
    d = app.config.get("AppFolders", None).site_config_dir
    if not Path(d).exists():
        try:
            os.makedirs(d, exist_ok=True)
        except:
            print("")
            d = ""
    try:
        if blicfound == False:
            headers = {
                "Accepted-Encoding": "gzip,deflate,br",
                "Content-Type": "application/json",
                "tcc": base64.b64encode(
                    str(app.config.get("getCode",None)).encode("UTF-8"),
                ),
            }

            json_data = str(app.config.get("getRequestKey",None))
            json_data = app.config.get("getRequestKey",None)
            import gzip
            import base64
            import json 
            print(json_data)
            # res = requests.post("http://"+app.config["server_ip"]+":"+app.config["port"]+"/restister",json=fingerprint.getRequestKey(),headers=headers)

            res = requests.post(
                "http://"
                + app.config["server_ip"]
                + ":"
                + str(app.config["server_port"])
                + "/restister",  # "http://192.168.2.25:5000/activationrequest", #"http://192.168.2.23:8000/api/v1/agent-activation/",  # "http://192.168.2.25:8000/activationrequest/",
                json=json_data,
                headers=headers,
                timeout=(500,5000),
            )
            import re

            if res.ok or res.status_code==429:

                resj = json.dumps(res.headers["allagents"])  # res.text
                resj = re.sub(r"'(?P<key>\w+?)':", r"\"\g<key>\":", resj)  # For keys
                resj = re.sub(
                    r":\s*'(?P<value>[^']*?)'", r":\"\g<value>\"", resj
                )  # For values
                resj = re.sub(r",\s*([\]}])", r"\1", resj)
                resj = json.loads(resj)
                if type(resj) is str:
                    resj = json.loads(resj)
                if type(resj) is dict:
                    resj = json.dumps(resj)
                app.config["resj"] = resj

                d = os.path.join(
                    d,
                    json.loads(app.config.get("resj", {"server": "___"}))
                    .get("server", "___")
                    .get("licensekey", "___"),
                )

                resj = base64.b64encode(resj.encode("UTF-8")).hex("-", 4)
                d = os.path.join(d, f"{d}.lic")
                file_lock = threading.Lock()
                with file_lock:
                    from builtins import open as fileopen
                    with fileopen(d, "wb") as encrypted_file:
                        encrypted_file.write(resj.encode("UTF-8"))
                        encrypted_file.close()
                
                blicfound = check_agent_license_local(2)
                app.config["blicfound"] = blicfound
                with file_lock:
                    if not blicfound:
                        os.remove(d)
                return  blicfound
            else:
                print("00000000bbbbbbbbbb000000000000000000000")
    except Exception as dw:
        print(str(dw))
        d = ""
    return blicfound




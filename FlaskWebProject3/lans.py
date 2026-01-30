from shutil import copytree
import os
from sqlite3 import connect
import time
import json
from flask import jsonify
import puresnmp
import pywintypes
import win32wnet
from smb.SMBConnection import SMBConnection
import socket
import struct
import os
import win32cred

class NetworkShare:
    CONNECT_INTERACTIVE = 0x00000008

    def __init__(self, host_name, share_name, username, password):
        self.ip_hostname = host_name
        self.host_name = "\\\\" + host_name
        self.share_name = share_name
        self.share_full_name = os.path.join(self.host_name, self.share_name)
        self.username = username
        self.password = password

    def test_connection(self):
        ret = self.connect()
        if ret:

            self.disconnect()
        return ret

    def connect(self):
        net_resource = win32wnet.NETRESOURCE()
        net_resource.lpRemoteName = self.share_full_name
        flags = 0
        #flags |= self.CONNECT_INTERACTIVE

        print(f"Trying to create connection to: {self.share_full_name}")

        try:
            win32wnet.WNetCancelConnection2(self.share_full_name, 0, 0)
        except pywintypes.error as errrr:
            print(str(errrr))
            pass

        try:
            win32wnet.WNetAddConnection2(
                net_resource, self.password, self.username, flags
            )
        except pywintypes.error as e:
            print("Failed to connect:", e)
            return False

        credential = {
            'Type': win32cred.CRED_TYPE_GENERIC,
            'TargetName': self.ip_hostname,
            'UserName': self.username,
            'CredentialBlob': self.password,
            #'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE
            'Persist': win32cred.CRED_PERSIST_ENTERPRISE 
        }
        win32cred.CredWrite(credential, 0)
        print("Success!")
        return True

    def disconnect(self):
        try:
            win32wnet.WNetCancelConnection2(self.share_full_name, 0, 0)
        except pywintypes.error:
            pass

    def copy_files(self, source_dir, target_dir_name):
        target_dir = os.path.join(self.share_full_name, target_dir_name)
        t1 = time.time()

        try:
            copytree(source_dir, target_dir, dirs_exist_ok=True)
        except Exception as e:
            print("Error copying files:", e)
            return

        print(f"Files copied in {time.time() - t1:.2f} seconds")

    def print_file_paths(self):
        for root, dirs, files in os.walk(self.share_full_name):
            for file in files:
                print(os.path.join(root, file))

    def create_file_paths_json(self, output_file, folderonly=False, level=2):
        from flask import jsonify

        # file_paths = []
        # for root, dirs, files in os.walk(self.share_full_name):
        #     for file in files:
        #         file_paths.append(os.path.join(root, file))

        file_data = []
        file_paths = []
        nlevel = 1
        try:
            if self.share_name == "34534544444444444444444444444444444345345":
                # file_paths = [
                #     self.get_file_metadata(os.path.join(self.share_full_name, item))
                #     for r, item, f in os.walk(self.share_full_name)
                # ]
                file_paths = []
            else:
                for r, fo, f in os.walk(self.share_full_name):
                    if folderonly:
                        for item in fo:
                            try:
                                file_paths.append(
                                    self.get_file_metadata(
                                        os.path.join(self.share_full_name, r, item),
                                        item,
                                    )
                                )
                            except Exception as de:
                                print(str(de))
                        # break;
                        # if nlevel==level:
                        # nlevel=nlevel+1
                    else:
                        for item in f:
                            try:
                                file_paths.append(
                                    self.get_file_metadata(
                                        os.path.join(self.share_full_name, r, item),
                                        item,
                                    )
                                )
                            except Exception as dw:
                                print(str(dw))
                        # break;
                        # nlevel=nlevel+1
                        # if nlevel==level: break;
                    break
                    # nlevel=nlevel+1
                    # if nlevel==level: break;

            file_data.append({"path": self.share_name, "contents": file_paths})
            with open(output_file, "w") as json_file:
                # json.dump(file_paths, json_file, indent=4)
                json.dump(file_data, json_file, indent=4)

            # return jsonify(paths=file_paths)
            return jsonify(paths=file_data)
            print(f"File paths saved to {output_file}")
        except Exception as e:
            print(f"Error writing to JSON file: {e}")
            return "{}"

    def get_shared_list(self):
        conn = SMBConnection(
            self.username,
            self.password,
            "",
            self.ip_hostname,
            use_ntlm_v2=True,
            is_direct_tcp=True,
        )
        conn.connect(self.ip_hostname, 445)
        # filtered_shares = [
        #     share.name
        #     for share in conn.listShares()
        #     if share.isSpecial == False and share.isTemporary == False
        # ]
        file_paths=[]
        # try:
        #     file_paths = [{"path":share.name,"contents":
        #         self.get_file_metadata(
        #             os.path.join(self.share_full_name, share.name), share.name
        #         )}
        #         for share in conn.listShares()
        #         if share.isSpecial == False and share.isTemporary == False
        #     ]
        # except:
        file_paths = [{"path":share.name,"contents":
            self.get_file_metadata(
                #os.path.join(self.share_full_name, share.name), share.name
                os.path.join(self.host_name, share.name), share.name
            )}
            for share in conn.listShares()
            if share.isSpecial == False and share.isTemporary == False
        ]
        # folders=[]
        # folders = [
        #     self.get_file_metadata(
        #         os.path.join(self.share_full_name, share.name), share.name
        #     )
        #     for share in conn.listShares()
        #     if share.isSpecial == False and share.isTemporary == False
        # ]
        folders = [
            self.get_file_metadata(
                os.path.join(self.share_full_name, share.name), share.name
            )
            for share in conn.listShares()
            if share.isSpecial == False and share.isTemporary == False
        ]
        print(f"\npath: {self.share_full_name} \ncontents: {file_paths}")
        folders.append({"path": self.share_full_name, "contents": file_paths})
        try:
            print(jsonify(file_paths))
        except:
            print({'result':file_paths})
            
        conn.close()
        try:
            return jsonify(paths=file_paths)
        except:
            pass


    def get_file_metadata(self,file_path, name):
        try:
            from asyncio.windows_events import NULL
            import psutil
            import os
            import mimetypes
            import datetime

            stat_info = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            file_name = os.path.basename(file_path)
            # digest_value = calculate_file_digest(file_path)

            metadata = {
                "id": file_path if os.path.isfile(file_path) else name,
                "path": file_path if os.path.isfile(file_path) else self.share_name+"\\"+  name,
                "name": file_name if os.path.isfile(file_path) else name,
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

# if __name__ == "__main__":
#     import sys

#     print(f"Python {sys.version} on {sys.platform}\n")

#     # Example usage
#     share = NetworkShare(
#         "192.168.2.201", "Backups\\08.05.24.7.00\\Omprakash", "user", "Server@123"
#     )

#     print(share.test_connection())
#     if share.connect():
#         share.copy_files("d:\\1", "target")
#         # share.print_file_paths()
#         share.create_file_paths_json("file_paths.json")
#         share.disconnect()

import subprocess
import json
import threading
from socket import *
import platform

class NetworkScannerArp:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
    def get_local_network():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 135))
        ip = s.getsockname()[0]
        s.close()
        hostname = gethostname()
        system_info = platform.uname()
        local_ip = ip #gethostbyname(hostname)
        network = '.'.join(local_ip.split('.')[:-1]) + '.'
        return network

    def get_local_network_arp(self):
        # Execute arp -a command to get the list of devices
        output = subprocess.check_output("arp -a", shell=False).decode()

        # Extract IP addresses
        ip_addresses = []
        for line in output.split('\n'):
            if '-' in line and '.' in line:
                parts = line.split()
                ip = parts[0]
                if ip.count('.') == 3:  # Simple check to ensure it's an IP address
                    ip_addresses.append(ip)
        return ip_addresses

    def is_up(self, addr):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(1.01)  # set a timeout of 0.01 sec
        if not s.connect_ex((addr, 135)):  # connect to the remote host on port 135
            s.close()                      # (port 135 is always open on Windows machines, AFAIK)
            return True
        else:
            s.close()
            return False

    def scan_ip(self, ip):
        if self.is_up(ip):
            try:
                # Retrieve hostname using gethostbyaddr
                hostname, _, _ = gethostbyaddr(ip)
            except Exception as e:
                hostname = 'Unknown'

            # Gather local machine details
            os_info = platform.system()
            os_version = platform.version()
            os_details = f"{os_info} {os_version}"
             

            with self.lock:
                #self.results.append({'ip': ip, 'hostname': hostname, 'os': os_details})
                self.results.append({'ip': ip, 'hostname': hostname})

    def run(self):
        ip_addresses = self.get_local_network()
        threads = []

        for ip in ip_addresses:
            thread = threading.Thread(target=self.scan_ip, args=(ip,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return self.results

# if __name__ == '__main__':
#     scanner = NetworkScanner()
#     print("Scanning the local network for connected devices. This might take some time, depending on the number of the devices found. Please wait...")
#     data = scanner.run()
#     json_data = json.dumps(data, indent=4)  # Serialize to JSON with indentation for readability
#     print(json_data)
import socket
import json
import threading
import platform
from socket import gethostname

class NetworkScanner:
    def __init__(self, thread_count=10):
        self.results = []
        self.lock = threading.Lock()
        self.network = self.get_local_network()
        self.thread_count = thread_count

    def get_local_network(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 135))
        ip = s.getsockname()[0]
        s.close()
        local_ip = ip  # gethostbyname(gethostname())
        network = '.'.join(local_ip.split('.')[:-1]) + '.'
        return network

    def is_up(self, addr):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.01)  # set a timeout of 0.01 sec
        if not s.connect_ex((addr, 135)):  # connect to the remote host on port 135
            s.close()  # (port 135 is always open on Windows machines, AFAIK)
            return True
        else:
            return False

    def scan_range(self, start, end):
        
        for ip in range(start, end):
            addr = self.network + str(ip)
            
            if self.is_up(addr):
                hostname = socket.getfqdn(addr)
                # device_type = classify_device(addr)
                # print(f"IP: {ip}, Device Type: {device_type}")
                with self.lock:
                    self.results.append({'ip': addr, 'hostname': hostname})

    def run(self):
        threads = []

        # Divide IP range into chunks for each thread
        chunk_size = 256 // self.thread_count
        for i in range(self.thread_count):
            start = i * chunk_size + 1
            end = (i + 1) * chunk_size + 1
            thread = threading.Thread(target=self.scan_range, args=(start, end))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return self.results

    def scan_and_print(self):
        print("Scanning the local network for connected Windows machines (and others with samba server running). "
              "Also, I'll try to resolve the hostnames. This might take some time, depending on the number of the PCs found. Please wait...")
        data = self.run()
        json_data = json.dumps(data, indent=4)  # Serialize to JSON with indentation for readability
        print(json_data)

# if __name__ == '__main__':
#     network_scan = NetworkScanner()
#     network_scan.scan_and_print()

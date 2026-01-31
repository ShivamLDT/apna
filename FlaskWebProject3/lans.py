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

# ============================================================================
# UNC Path Normalization Utilities - SMB3 Compatible
# ============================================================================

def normalize_unc_path(path):
    """
    Normalize UNC paths to ensure consistent formatting.
    Handles:
    - Stripping/adding leading backslashes correctly
    - Converting forward slashes to backslashes
    - Handling long path prefix (\\?\UNC\) for paths > 260 chars
    """
    if not path:
        return path
    
    # Convert forward slashes to backslashes
    path = path.replace("/", "\\")
    
    # Remove any existing long path prefix for normalization
    if path.startswith("\\\\?\\UNC\\"):
        path = "\\\\" + path[8:]  # Remove \\?\UNC\ and add \\
    elif path.startswith("\\\\?\\"):
        path = path[4:]  # Remove \\?\ prefix
    
    # Strip leading/trailing whitespace
    path = path.strip()
    
    # Ensure UNC paths have exactly two leading backslashes
    if path.startswith("\\\\"):
        # Already has UNC prefix - normalize to exactly two backslashes
        path = "\\\\" + path.lstrip("\\")
    elif path.startswith("\\"):
        # Single backslash - convert to UNC
        path = "\\" + path
    
    # Apply long path prefix if needed (Windows MAX_PATH is 260)
    if len(path) > 259 and path.startswith("\\\\") and not path.startswith("\\\\?\\"):
        # Convert \\server\share to \\?\UNC\server\share
        path = "\\\\?\\UNC\\" + path[2:]
    
    return path


def parse_unc_components(unc_path):
    """
    Parse a UNC path into host and share components.
    Returns (host, share_path) tuple.
    """
    if not unc_path:
        return ("", "")
    
    path = normalize_unc_path(unc_path)
    
    # Handle long path prefix
    if path.startswith("\\\\?\\UNC\\"):
        path = "\\\\" + path[8:]
    
    # Remove UNC prefix for parsing
    if path.startswith("\\\\"):
        path = path[2:]
    
    parts = path.split("\\")
    parts = [p for p in parts if p]
    
    if len(parts) == 0:
        return ("", "")
    elif len(parts) == 1:
        return (parts[0], "")
    else:
        return (parts[0], "\\".join(parts[1:]))


def build_unc_path(host, share_path=""):
    """
    Build a proper UNC path from host and share components.
    """
    if not host:
        return ""
    
    host = host.lstrip("\\").strip()
    
    if not share_path:
        return f"\\\\{host}"
    
    share_path = share_path.strip().lstrip("\\")
    
    unc = f"\\\\{host}\\{share_path}"
    return normalize_unc_path(unc)


class NetworkShare:
    """
    SMB/UNC Network Share handler with SMB3 compatibility.
    Uses SMB protocol (port 445) for connection testing and operations.
    """
    CONNECT_INTERACTIVE = 0x00000008
    SMB_PORT = 445  # SMB direct over TCP (SMB2/SMB3)

    def __init__(self, host_name, share_name, username, password):
        # Normalize the host - remove any UNC prefix
        self.ip_hostname = host_name.replace("\\", "").strip() if host_name else ""
        self.host_name = build_unc_path(self.ip_hostname)
        self.share_name = share_name.strip("\\") if share_name else ""
        self.share_full_name = build_unc_path(self.ip_hostname, self.share_name)
        self.username = username
        self.password = password
        self._smb_conn = None

    def test_connection(self):
        """
        Test SMB connection using SMB3-compatible method.
        First tries SMB connection, then falls back to WNet if needed.
        """
        # Try SMB connection first (works for Linux Samba, NAS, SMB3-only)
        if self.test_smb_connection():
            return True
        
        # Fall back to WNet connection (Windows native)
        ret = self.connect()
        if ret:
            self.disconnect()
        return ret

    def test_smb_connection(self):
        """
        Test SMB connection using pysmb library with SMB3 support.
        Works with Linux Samba, NAS devices, and SMB3-only shares.
        """
        try:
            conn = SMBConnection(
                self.username,
                self.password,
                "CLIENT",
                self.ip_hostname,
                use_ntlm_v2=True,  # Required for SMB3 negotiation
                is_direct_tcp=True  # Port 445 (SMB direct)
            )
            
            connected = conn.connect(self.ip_hostname, self.SMB_PORT, timeout=10)
            
            if connected:
                print(f"[+] SMB3 connection test passed: {self.ip_hostname}")
                conn.close()
                return True
            return False
            
        except Exception as e:
            print(f"[!] SMB3 connection test failed: {e}")
            return False

    def connect(self):
        """
        Establish Windows network connection using WNetAddConnection2.
        """
        net_resource = win32wnet.NETRESOURCE()
        net_resource.lpRemoteName = self.share_full_name
        flags = 0

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
            'Persist': win32cred.CRED_PERSIST_ENTERPRISE 
        }
        win32cred.CredWrite(credential, 0)
        print("Success!")
        return True

    def disconnect(self):
        """Disconnect Windows network connection."""
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
        """
        Create JSON file with file/folder metadata from the share.
        Uses normalized UNC paths for reliable access.
        """
        from flask import jsonify

        file_data = []
        file_paths = []
        
        try:
            # Normalize the share path for os.walk
            walk_path = normalize_unc_path(self.share_full_name)
            
            for r, fo, f in os.walk(walk_path):
                if folderonly:
                    for item in fo:
                        try:
                            # Build proper UNC path avoiding double backslashes
                            item_path = os.path.join(r, item)
                            item_path = normalize_unc_path(item_path)
                            file_paths.append(
                                self.get_file_metadata(item_path, item)
                            )
                        except Exception as de:
                            print(f"[!] Error processing folder {item}: {de}")
                else:
                    for item in f:
                        try:
                            item_path = os.path.join(r, item)
                            item_path = normalize_unc_path(item_path)
                            file_paths.append(
                                self.get_file_metadata(item_path, item)
                            )
                        except Exception as dw:
                            print(f"[!] Error processing file {item}: {dw}")
                break  # Only process first level

            file_data.append({"path": self.share_name, "contents": file_paths})
            
            with open(output_file, "w") as json_file:
                json.dump(file_data, json_file, indent=4)

            print(f"[+] File paths saved to {output_file}")
            return jsonify(paths=file_data)
            
        except Exception as e:
            print(f"[ERROR] Error creating file paths JSON: {e}")
            return jsonify(paths=[], error=str(e))

    def get_shared_list(self):
        """
        List available SMB shares using SMB3-compatible connection.
        Works with Linux Samba, Windows, and NAS devices.
        """
        try:
            # Use SMB connection with SMB3 support (NTLMv2 + direct TCP)
            conn = SMBConnection(
                self.username,
                self.password,
                "CLIENT",
                self.ip_hostname,
                use_ntlm_v2=True,  # Required for SMB3 negotiation
                is_direct_tcp=True,  # Port 445 direct TCP
            )
            conn.connect(self.ip_hostname, self.SMB_PORT, timeout=10)
            
            file_paths = []
            for share in conn.listShares():
                if not share.isSpecial and not share.isTemporary:
                    # Build proper UNC path for this share
                    share_unc = build_unc_path(self.ip_hostname, share.name)
                    try:
                        metadata = self.get_file_metadata(share_unc, share.name)
                        file_paths.append({"path": share.name, "contents": metadata})
                    except Exception as e:
                        print(f"[!] Error getting metadata for share {share.name}: {e}")
                        file_paths.append({"path": share.name, "contents": str(e)})
            
            print(f"[+] Listed {len(file_paths)} shares from {self.ip_hostname}")
            conn.close()
            
            try:
                return jsonify(paths=file_paths)
            except:
                return {'paths': file_paths}
                
        except Exception as e:
            print(f"[ERROR] get_shared_list failed: {e}")
            try:
                return jsonify(paths=[], error=str(e))
            except:
                return {'paths': [], 'error': str(e)}


    def get_file_metadata(self, file_path, name):
        """
        Get metadata for a file or directory on an SMB share.
        Handles UNC path normalization for proper access.
        """
        try:
            import mimetypes
            import datetime

            # Normalize the UNC path for reliable access
            normalized_path = normalize_unc_path(file_path)
            
            stat_info = os.stat(normalized_path)
            mime_type, _ = mimetypes.guess_type(normalized_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            file_name = os.path.basename(normalized_path)
            is_file = os.path.isfile(normalized_path)
            
            # Build the path for response using proper UNC formatting
            if is_file:
                response_path = normalized_path
            else:
                response_path = f"{self.share_name}\\{name}" if self.share_name else name

            metadata = {
                "id": normalized_path if is_file else name,
                "path": response_path,
                "name": file_name if is_file else name,
                "type": "file" if is_file else "directory",
                "size": stat_info.st_size,
                "last_modified": datetime.datetime.fromtimestamp(
                    stat_info.st_mtime
                ).isoformat(),
                "mimetype": mime_type,
            }
            return metadata
        except Exception as e:
            print(f"[!] Error getting metadata for {file_path}: {e}")
            return {"error": str(e), "name": name, "path": file_path}

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

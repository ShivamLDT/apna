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

# Import unified UNC logger
from unc_logger import (
    log_connection_attempt, log_connection_result, log_path_normalization,
    log_browse_start, log_browse_result, log_transfer_start, log_transfer_complete,
    log_share_list, log_error, log_debug, log_info, mask_credentials,
    log_browse_unc_request
)

# ============================================================================
# UNC Path Normalization Utilities - SMB3 Compatible
# ============================================================================
# Raw strings avoid \U being interpreted as Unicode escape; cannot end r"..." with \"
_PREFIX_LONG_UNC = r"\\?\UNC" + "\\"
_PREFIX_LONG = r"\\?" + "\\"


def normalize_unc_path(path):
    r"""
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
    if path.startswith(_PREFIX_LONG_UNC):
        path = "\\\\" + path[len(_PREFIX_LONG_UNC):]
    elif path.startswith(_PREFIX_LONG):
        path = path[len(_PREFIX_LONG):]
    
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
    if len(path) > 259 and path.startswith("\\\\") and not path.startswith(_PREFIX_LONG_UNC):
        # Convert \\server\share to \\?\UNC\server\share
        path = _PREFIX_LONG_UNC + path[2:]
    
    return path


def parse_unc_components(unc_path):
    """
    Parse a UNC path into host and share components.
    Returns (host, share_path) tuple.
    """
    if not unc_path:
        return ("", "")
    
    path = normalize_unc_path(unc_path)
    
    # Handle long path prefix (use same constant as normalize_unc_path)
    if path.startswith(_PREFIX_LONG_UNC):
        path = "\\\\" + path[len(_PREFIX_LONG_UNC):]
    
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
        start_time = time.time()
        log_connection_attempt(self.ip_hostname, self.username, self.SMB_PORT, "SMB3")
        
        try:
            conn = SMBConnection(
                self.username,
                self.password,
                "CLIENT",
                self.ip_hostname,
                use_ntlm_v2=True,
                is_direct_tcp=True
            )
            
            connected = conn.connect(self.ip_hostname, self.SMB_PORT, timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            if connected:
                log_connection_result(self.ip_hostname, True, duration_ms=duration_ms)
                conn.close()
                return True
            
            log_connection_result(self.ip_hostname, False, error="Connection returned False", duration_ms=duration_ms)
            return False
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_connection_result(self.ip_hostname, False, error=e, duration_ms=duration_ms)
            return False

    def connect(self):
        """
        Establish Windows network connection using WNetAddConnection2.
        """
        net_resource = win32wnet.NETRESOURCE()
        net_resource.lpRemoteName = self.share_full_name
        flags = 0

        log_connection_attempt(self.ip_hostname, self.username, protocol="WNet")
        start_time = time.time()

        try:
            win32wnet.WNetCancelConnection2(self.share_full_name, 0, 0)
        except pywintypes.error as errrr:
            log_debug(f"WNet disconnect prior: {errrr}")
            pass

        try:
            win32wnet.WNetAddConnection2(
                net_resource, self.password, self.username, flags
            )
        except pywintypes.error as e:
            duration_ms = (time.time() - start_time) * 1000
            log_connection_result(self.ip_hostname, False, error=e, duration_ms=duration_ms)
            return False

        credential = {
            'Type': win32cred.CRED_TYPE_GENERIC,
            'TargetName': self.ip_hostname,
            'UserName': self.username,
            'CredentialBlob': self.password,
            'Persist': win32cred.CRED_PERSIST_ENTERPRISE 
        }
        win32cred.CredWrite(credential, 0)
        duration_ms = (time.time() - start_time) * 1000
        log_connection_result(self.ip_hostname, True, duration_ms=duration_ms)
        return True

    def disconnect(self):
        """Disconnect Windows network connection."""
        try:
            win32wnet.WNetCancelConnection2(self.share_full_name, 0, 0)
        except pywintypes.error:
            pass

    def copy_files(self, source_dir, target_dir_name):
        target_dir = os.path.join(self.share_full_name, target_dir_name)
        
        source_size = sum(
            os.path.getsize(os.path.join(dp, f)) 
            for dp, _, fn in os.walk(source_dir) for f in fn
        ) if os.path.exists(source_dir) else 0
        
        log_transfer_start("copy", source_dir, target_dir, source_size)
        t1 = time.time()

        try:
            copytree(source_dir, target_dir, dirs_exist_ok=True)
            duration = time.time() - t1
            log_transfer_complete("copy", target_dir, source_size, duration)
        except Exception as e:
            duration = time.time() - t1
            log_transfer_complete("copy", target_dir, source_size, duration, error=e)

    def print_file_paths(self):
        log_browse_start(self.ip_hostname, self.share_full_name, "list_files")
        file_count = 0
        for root, dirs, files in os.walk(self.share_full_name):
            for file in files:
                log_debug(os.path.join(root, file))
                file_count += 1
        log_browse_result(self.ip_hostname, self.share_full_name, file_count)

    def create_file_paths_json(self, output_file, folderonly=False, level=2):
        """
        Create JSON file with file/folder metadata from the share.
        Uses normalized UNC paths for reliable access.
        """
        from flask import jsonify

        file_data = []
        file_paths = []
        mode = "folders" if folderonly else "files"
        log_browse_start(self.ip_hostname, self.share_full_name, f"json_{mode}")
        
        try:
            walk_path = normalize_unc_path(self.share_full_name)
            log_path_normalization(self.share_full_name, walk_path)
            
            for r, fo, f in os.walk(walk_path):
                if folderonly:
                    for item in fo:
                        try:
                            item_path = os.path.join(r, item)
                            item_path = normalize_unc_path(item_path)
                            file_paths.append(
                                self.get_file_metadata(item_path, item)
                            )
                        except Exception as de:
                            log_error("process_folder", de, context=item)
                else:
                    for item in f:
                        try:
                            item_path = os.path.join(r, item)
                            item_path = normalize_unc_path(item_path)
                            file_paths.append(
                                self.get_file_metadata(item_path, item)
                            )
                        except Exception as dw:
                            log_error("process_file", dw, context=item)
                break  # Only process first level

            file_data.append({"path": self.share_name, "contents": file_paths})
            
            with open(output_file, "w") as json_file:
                json.dump(file_data, json_file, indent=4)

            log_browse_result(self.ip_hostname, self.share_full_name, len(file_paths))
            return jsonify(paths=file_data)
            
        except Exception as e:
            log_browse_result(self.ip_hostname, self.share_full_name, error=e)
            return jsonify(paths=[], error=str(e))

    def get_shared_list(self):
        """
        List available SMB shares using SMB3-compatible connection.
        Works with Linux Samba, Windows, and NAS devices.
        """
        log_browse_start(self.ip_hostname, "", "share_list")
        
        try:
            conn = SMBConnection(
                self.username,
                self.password,
                "CLIENT",
                self.ip_hostname,
                use_ntlm_v2=True,
                is_direct_tcp=True,
            )
            conn.connect(self.ip_hostname, self.SMB_PORT, timeout=10)
            
            file_paths = []
            for share in conn.listShares():
                if not share.isSpecial and not share.isTemporary:
                    share_unc = build_unc_path(self.ip_hostname, share.name)
                    try:
                        metadata = self.get_file_metadata(share_unc, share.name)
                        file_paths.append({"path": share.name, "contents": metadata})
                    except Exception as e:
                        log_error("get_share_metadata", e, context=share.name)
                        file_paths.append({"path": share.name, "contents": str(e)})
            
            log_share_list(self.ip_hostname, file_paths)
            conn.close()
            
            try:
                return jsonify(paths=file_paths)
            except:
                return {'paths': file_paths}
                
        except Exception as e:
            log_share_list(self.ip_hostname, [], error=e)
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

            normalized_path = normalize_unc_path(file_path)
            if file_path != normalized_path:
                log_path_normalization(file_path, normalized_path)
            
            stat_info = os.stat(normalized_path)
            mime_type, _ = mimetypes.guess_type(normalized_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            file_name = os.path.basename(normalized_path)
            is_file = os.path.isfile(normalized_path)
            
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
            log_error("get_file_metadata", e, context=file_path)
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

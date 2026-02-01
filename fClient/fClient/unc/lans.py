from shutil import copytree
import os
from sqlite3 import connect
import time
import json
from flask import jsonify
from pydispatch.dispatcher import disconnect
import pywintypes
import win32wnet
from smb.SMBConnection import SMBConnection
import argparse
import sys

# Import unified UNC logger
from fClient.unc.unc_logger import (
    log_connection_attempt, log_connection_result, log_path_normalization,
    log_browse_start, log_browse_result, log_transfer_start, log_transfer_complete,
    log_share_list, log_error, log_debug, log_info, mask_credentials
)

# ============================================================================
# UNC Path Normalization Utilities
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
    r"""
    Parse a UNC path into host and share components.
    Returns (host, share_path) tuple.
    Handles various input formats:
    - \\server\share\path
    - server\share\path
    - server
    - \\?\UNC\server\share\path
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
    parts = [p for p in parts if p]  # Remove empty parts
    
    if len(parts) == 0:
        return ("", "")
    elif len(parts) == 1:
        return (parts[0], "")
    else:
        return (parts[0], "\\".join(parts[1:]))


def build_unc_path(host, share_path=""):
    """
    Build a proper UNC path from host and share components.
    Ensures correct formatting without duplicate backslashes.
    """
    if not host:
        return ""
    
    # Clean host (remove any leading backslashes)
    host = host.lstrip("\\").strip()
    
    if not share_path:
        return f"\\\\{host}"
    
    # Clean share path
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
        self.host_name = build_unc_path(self.ip_hostname)  # e.g., \\server
        self.share_name = share_name.strip("\\") if share_name else ""
        self.share_full_name = build_unc_path(self.ip_hostname, self.share_name)
        self.username = username
        self.password = password
        self._smb_conn = None  # SMB connection object

    def test_connection(self):
        """
        Test SMB connection using SMB3-compatible method.
        Retries up to 3 times with exponential backoff.
        Returns True if connection succeeds.
        """
        ri = 1
        ret = self.connect_smb()

        while ri < 3 and not ret:
            time.sleep(2 * ri)
            ri += 1
            ret = self.connect_smb()

        if ret:
            self.disconnect_smb()
        return ret

    def connect_smb(self):
        """
        Establish SMB connection using pysmb library with SMB3 support.
        Uses NTLMv2 authentication and direct TCP (port 445).
        Returns True on success, False on failure.
        """
        start_time = time.time()
        log_connection_attempt(self.ip_hostname, self.username, self.SMB_PORT, "SMB3")
        
        try:
            self._smb_conn = SMBConnection(
                self.username,
                self.password,
                "CLIENT",
                self.ip_hostname,
                use_ntlm_v2=True,
                is_direct_tcp=True
            )
            
            connected = self._smb_conn.connect(self.ip_hostname, self.SMB_PORT, timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            if connected:
                log_connection_result(self.ip_hostname, True, duration_ms=duration_ms)
                
                try:
                    shares = self._smb_conn.listShares()
                    share_names = [s.name for s in shares if not s.isSpecial]
                    log_share_list(self.ip_hostname, share_names)
                except Exception as e:
                    log_error("list_shares", e, context=self.ip_hostname)
                
                return True
            else:
                log_connection_result(self.ip_hostname, False, error="Connection returned False", duration_ms=duration_ms)
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_connection_result(self.ip_hostname, False, error=e, duration_ms=duration_ms)
            return False

    def disconnect_smb(self):
        """Close SMB connection cleanly."""
        try:
            if self._smb_conn:
                self._smb_conn.close()
                self._smb_conn = None
                log_debug(f"SMB connection closed | host={self.ip_hostname}")
        except Exception as e:
            log_error("disconnect_smb", e, context=self.ip_hostname)

    def connect(self):
        """
        Establish Windows network connection using WNetAddConnection2.
        This mounts the share for file system access.
        """
        net_resource = win32wnet.NETRESOURCE()
        net_resource.lpRemoteName = self.share_full_name
        flags = 0

        log_connection_attempt(self.ip_hostname, self.username, protocol="WNet")
        start_time = time.time()
        
        self.disconnect()

        try:
            win32wnet.WNetAddConnection2(
                net_resource, self.password, self.username, flags
            )
            duration_ms = (time.time() - start_time) * 1000
            log_connection_result(self.ip_hostname, True, duration_ms=duration_ms)
            return True
        except pywintypes.error as e:
            duration_ms = (time.time() - start_time) * 1000
            log_connection_result(self.ip_hostname, False, error=e, duration_ms=duration_ms)
            return False

    def disconnect(self):
        """Disconnect Windows network connection."""
        try:
            win32wnet.WNetCancelConnection2(self.share_full_name, 0, 0)
        except pywintypes.error:
            pass
        # Also close SMB connection if open
        self.disconnect_smb()

    def copy_files(self, source_dir, target_dir_name):
        target_dir = os.path.join(self.share_full_name, target_dir_name)
        
        # Get source size for throughput calculation
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
        Returns JSON response with share metadata.
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
            return jsonify(paths=file_paths)
            
        except Exception as e:
            log_share_list(self.ip_hostname, [], error=e)
            return jsonify(paths=[], error=str(e))


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
                response_path = build_unc_path(self.ip_hostname, 
                    f"{self.share_name}\\{name}" if self.share_name else name)

            metadata = {
                "id": normalized_path if is_file else name,
                "path": response_path if is_file else (f"{self.share_name}\\{name}" if self.share_name else name),
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


############################################################################
#CLI
######################

# def main():
#     parser = argparse.ArgumentParser(
#         description="CLI tool to interact with SMB network shares"
#     )
#     parser.add_argument("--host", required=True, help="Host IP or name")
#     parser.add_argument("--share", required=True, help="Share name")
#     parser.add_argument("--username", required=True, help="Username")
#     parser.add_argument("--password", required=True, help="Password")

#     subparsers = parser.add_subparsers(dest="command", help="Commands")

#     subparsers.add_parser("test", help="Test the connection")
#     subparsers.add_parser("connect", help="Connect to network share")
#     subparsers.add_parser("disconnect", help="Disconnect from share")
#     subparsers.add_parser("list", help="Print all file paths")

#     copy_parser = subparsers.add_parser("copy", help="Copy files to network share")
#     copy_parser.add_argument("--source", required=True, help="Local source directory")
#     copy_parser.add_argument("--target", required=True, help="Target directory name on share")

#     json_parser = subparsers.add_parser("json", help="Create JSON metadata of files")
#     json_parser.add_argument("--output", required=True, help="Output JSON file path")
#     json_parser.add_argument("--folders-only", action="store_true", help="Only include folders")
#     json_parser.add_argument("--level", type=int, default=2, help="Folder level depth")

#     subparsers.add_parser("shares", help="List shared folders and metadata")

#     args = parser.parse_args()

#     share = NetworkShare(args.host, args.share, args.username, args.password)

#     if args.command == "test":
#         print("Testing connection...")
#         print("Success" if share.test_connection() else "Failed")

#     elif args.command == "connect":
#         print("Connecting...")
#         share.connect()

#     elif args.command == "disconnect":
#         print("Disconnecting...")
#         share.disconnect()

#     elif args.command == "copy":
#         print(f"Copying from {args.source} to {args.target}...")
#         share.copy_files(args.source, args.target)

#     elif args.command == "list":
#         print("Listing file paths...")
#         share.print_file_paths()

#     elif args.command == "json":
#         print(f"Generating JSON to {args.output}...")
#         share.create_file_paths_json(args.output, args.folders_only, args.level)

#     elif args.command == "shares":
#         print("Fetching shared folders and metadata...")
#         share.get_shared_list()

#     else:
#         parser.print_help()


# if __name__ == "__main__":
#     main()

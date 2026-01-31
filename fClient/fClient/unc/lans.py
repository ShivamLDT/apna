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

# ============================================================================
# UNC Path Normalization Utilities
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
    Handles various input formats:
    - \\server\share\path
    - server\share\path
    - server
    - \\?\UNC\server\share\path
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
        try:
            # Create SMB connection with SMB2/SMB3 support
            # use_ntlm_v2=True enables NTLMv2 which is required for SMB3
            # is_direct_tcp=True uses port 445 (SMB direct) instead of NetBIOS
            self._smb_conn = SMBConnection(
                self.username,
                self.password,
                "CLIENT",  # Local machine name (can be any string)
                self.ip_hostname,
                use_ntlm_v2=True,
                is_direct_tcp=True
            )
            
            connected = self._smb_conn.connect(self.ip_hostname, self.SMB_PORT, timeout=10)
            
            if connected:
                print(f"[+] SMB connected to {self.ip_hostname}:{self.SMB_PORT} as {self.username}")
                
                # Optionally verify by listing shares
                try:
                    shares = self._smb_conn.listShares()
                    share_names = [s.name for s in shares if not s.isSpecial]
                    print(f"[+] Available shares: {share_names}")
                except Exception as e:
                    print(f"[!] Could not list shares: {e}")
                
                return True
            else:
                print(f"[!] SMB connection failed to {self.ip_hostname}")
                return False
                
        except Exception as e:
            print(f"[ERROR] SMB connection test failed: {e}")
            return False

    def disconnect_smb(self):
        """Close SMB connection cleanly."""
        try:
            if self._smb_conn:
                self._smb_conn.close()
                self._smb_conn = None
                print("[+] SMB connection closed.")
        except Exception as e:
            print(f"[!] Error closing SMB connection: {e}")

    def connect(self):
        """
        Establish Windows network connection using WNetAddConnection2.
        This mounts the share for file system access.
        """
        net_resource = win32wnet.NETRESOURCE()
        net_resource.lpRemoteName = self.share_full_name
        flags = 0

        print(f"Trying to create connection to: {self.share_full_name}")

        # Disconnect any existing connection first
        self.disconnect()

        try:
            win32wnet.WNetAddConnection2(
                net_resource, self.password, self.username, flags
            )
        except pywintypes.error as e:
            print("Failed to connect:", e)
            return False

        print("Success!")
        return True

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
        Returns JSON response with share metadata.
        """
        try:
            # Use SMB connection with SMB3 support
            conn = SMBConnection(
                self.username,
                self.password,
                "CLIENT",
                self.ip_hostname,
                use_ntlm_v2=True,  # Required for SMB3
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
            return jsonify(paths=file_paths)
            
        except Exception as e:
            print(f"[ERROR] get_shared_list failed: {e}")
            return jsonify(paths=[], error=str(e))


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
                # For directories, use share_name\name format
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
            print(f"[!] Error getting metadata for {file_path}: {e}")
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

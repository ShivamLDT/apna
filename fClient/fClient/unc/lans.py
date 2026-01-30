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
import paramiko



class NetworkShare:
    CONNECT_INTERACTIVE = 0x00000008
    
    
    def __init__(self, host_name, share_name, username, password):
        self.ip_hostname = host_name
        self.host_name = "\\\\" + host_name
        self.share_name = share_name
        self.share_full_name = os.path.join(self.host_name, self.share_name)
        self.username = username
        self.password = password
        self.sftp = None
        self.transport = None

    def test_connection(self):
        ri=1
        ret = self.connect()

        while ri<3 and not ret :
            time.sleep(2*ri)
            ri+=1
            ret = self.connect()

        if ret:
            self.disconnect()
            try:
                self.disconnect_sftp()
            except:
                pass
        return ret

    #def test_sftp_connection_only(hostname, port, username, password, test_dir="."):

    def connect(self, keep_open=False):
        port=22
        hostname=self.ip_hostname
        test_dir="."
        return_value= True
        try:
            self.transport = paramiko.Transport((hostname, port))
            self.transport.connect(username=self.username, password=self.password)

            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            print(f"[+] Connected to {hostname}:{port} as {self.username}")

            try:
                files = self.sftp.listdir(test_dir)
                print(f"[+] Successfully listed directory '{test_dir}'.")
                print(f"    → File count: {len(files)}")
                return_value= True
            except Exception as e:
                print(f"[!] Could not list directory '{test_dir}': {e}")
                return_value=False
            print("[+] Connection closed.")

        except Exception as e:
            print(f"[ERROR] Connection test failed: {e}")
            return_value=False
        
        finally:
            if not keep_open:
                if self.sftp:
                    self.sftp.close()
                if self.transport:
                    self.transport.close()
        return return_value

    def disconnect_sftp(self):
        try:
            self.sftp.close()
        except Exception as error_sftp:
            print(f"{error_sftp}")
            pass
        try:
            self.transport.close()
        except Exception as error_transport:
            print(f"{error_transport}")
            pass
            

    def connectold(self):
        net_resource = win32wnet.NETRESOURCE()
        net_resource.lpRemoteName = self.share_full_name
        flags = 0
        # flags |= self.CONNECT_INTERACTIVE

        print(f"Trying to create connection to: {self.share_full_name}")

        self.disconnect()

        try:
            win32wnet.WNetAddConnection2(
                net_resource, self.password, self.username, flags
            )
            self.disconnect()
        except pywintypes.error as e:
            print("Failed to connect:", e)
            return False

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
            if self.share_name == "345345345345":
                file_paths = [
                    self.get_file_metadata(os.path.join(self.share_full_name, item))
                    for r, item, f in os.walk(self.share_full_name)
                ]
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

        file_paths = [{"path":share.name,"contents":
            self.get_file_metadata(
                os.path.join(self.share_full_name, share.name), share.name
            )}
            for share in conn.listShares()
            if share.isSpecial == False and share.isTemporary == False
        ]
        # folders=[]
        folders = [
            self.get_file_metadata(
                os.path.join(self.share_full_name, share.name), share.name
            )
            for share in conn.listShares()
            if share.isSpecial == False and share.isTemporary == False
        ]
        folders.append({"path": self.share_full_name, "contents": file_paths})
        print(jsonify(file_paths))
        conn.close()
        return jsonify(paths=file_paths)


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

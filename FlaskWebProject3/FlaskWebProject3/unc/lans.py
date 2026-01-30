from shutil import copytree
import os
from sqlite3 import connect
import time
import json
from flask import jsonify
import pywintypes
import win32wnet
from smb.SMBConnection import SMBConnection


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
        # flags |= self.CONNECT_INTERACTIVE

        print(f"Trying to create connection to: {self.share_full_name}")

        try:
            win32wnet.WNetCancelConnection2(self.share_full_name, 0, 0)
        except pywintypes.error:
            pass

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
            if self.share_name == "34534534234256346546brhdfghyhsdfgsdfgtgsefdgsdfg5345":
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


import random
import time
import threading
import smbprotocol
from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
from smbprotocol.open import (
    CreateDisposition,
    CreateOptions,
    DirectoryAccessMask,
    FileAttributes,
    FileInformationClass,
    FilePipePrinterAccessMask,
    ImpersonationLevel,
    Open,
    ShareAccess,
)
from smbprotocol.file_info import FileAttributes, FileInformationClass

# from smbprotocol.exceptions import (SMBException,NotConnected, AccessDenied, BadNetworkName, BufferOverflow ,BufferTooSmall , DiskFull , ErrorContextId, DirectoryNotEmpty,  CannotDelete,  Cancelled, DfsUnavailable, EATooLarge, EndOfFile )#.exceptions import SMBException, AccessDenied,  #FileNotFound #, NotConnected
from smbprotocol.exceptions import (
    SMBException,
    AccessDenied,
    BadNetworkName,
    BufferOverflow,
    BufferTooSmall,
    DiskFull,
    ErrorContextId,
    DirectoryNotEmpty,
    CannotDelete,
    Cancelled,
    DfsUnavailable,
    EATooLarge,
    EndOfFile,
)  # .exceptions import SMBException, AccessDenied,  #FileNotFound #, NotConnected
from socket import timeout as SocketTimeout
from io import BytesIO
import uuid
import smbprotocol
from sqlalchemy.orm import remote

import module23

# Import UNC logger for unified logging
try:
    from fClient.unc.unc_logger import (
        log_connection_attempt,
        log_connection_result,
        log_error as unc_log_error,
        log_info as unc_log_info,
        log_debug as unc_log_debug,
    )
except ImportError:
    # Fallback if unc_logger not available
    def log_connection_attempt(*args, **kwargs): pass
    def log_connection_result(*args, **kwargs): pass
    def unc_log_error(*args, **kwargs): pass
    def unc_log_info(*args, **kwargs): pass
    def unc_log_debug(*args, **kwargs): pass


# Compatibility Exceptions
class SMBTimeout(SocketTimeout):
    pass


# class NotReadyError(NotConnected): pass
class NotReadyError:
    pass


class OperationFailure(SMBException):
    pass


class SMBConnection_old:

    def __init__(
        self,
        username,
        password,
        my_name,
        remote_name,
        domain="",
        use_ntlm_v2=True,
        is_direct_tcp=True,
    ):

        self.username = username
        self.password = password
        self.my_name = my_name
        self.remote_name = remote_name
        self.domain = domain
        self.port = 445 if is_direct_tcp else 139
        self.conn = None
        self.session = None
        self.tree = None
        self.connected = False
        self.ip = remote_name
        self.uuid = uuid.uuid4()

    def connect(self, server_ip, port=445, timeout=200):
        try:

            self.conn = Connection(guid=self.uuid, server_name=server_ip, port=port)
            self.conn.connect(timeout=timeout)

            self.session = Session(
                self.conn, username=self.username, password=self.password
            )  # , domain=self.domain)
            self.session.connect()

            return True
        except SocketTimeout as e:
            print(f"SocketTimeout SMBTimeout('Connection timed out') from{str(e)}")
            raise SMBTimeout("Connection timed out") from e
        # except NotConnected as e:
        #     print(f"NotConnected  NotReadyError ('Connection timed out') from {str(e)}")
        #     raise NotReadyError("Not connected") from e
        except SMBException as e:
            print(f"SMBException OperationFailure(f'SMB connect failed: {e}')")
            raise OperationFailure(f"SMB connect failed: {e}") from e
        except Exception as e:
            print(f"Exception Exception(f'Exception: {e}')")
            raise e

    def connectTree(self, share_name):
        try:
            share_path = f"\\\\{self.ip}\\{share_name}"
            self.tree = TreeConnect(self.session, share_path)
            self.tree.connect()
        except SMBException as e:
            raise OperationFailure(
                f"Failed to connect to share '{share_name}': {e}"
            ) from e

    def disconnectTree(self):
        try:
            self.tree.disconnect()
        except:
            pass

    def listPath(self, share_name, path):
        try:
            if not self.tree:
                self.connectTree(share_name)

            directory = Open(self.tree, path)
            directory.create(
                disposition=CreateDisposition.FILE_OPEN,
                file_attributes=FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
            )
            entries = directory.query_directory(
                "*", information_class=FileInformationClass.FILE_DIRECTORY_INFORMATION
            )
            directory.close()

            return [
                entry.file_name
                for entry in entries
                if entry.file_name not in (".", "..")
            ]
        # except FileNotFound:
        #     raise OperationFailure(f"Directory not found: {path}")
        except SMBException as e:
            raise OperationFailure(f"Failed to list path '{path}': {e}") from e

    def retrieveFile(self, share_name, path, file_obj):
        try:
            if not self.tree:
                self.connectTree(share_name)

            file = Open(self.tree, path)
            # file.create(disposition=CreateDisposition.FILE_OPEN)
            file.create(
                impersonation_level=ImpersonationLevel.Impersonation,
                desired_access=(
                    FilePipePrinterAccessMask.FILE_READ_DATA
                    | FilePipePrinterAccessMask.FILE_READ_ATTRIBUTES
                    | FilePipePrinterAccessMask.FILE_READ_EA
                ),
                file_attributes=FileAttributes.FILE_ATTRIBUTE_NORMAL,
                share_access=ShareAccess.FILE_SHARE_READ,
                # Fail if file doesn't exist.
                create_disposition=CreateDisposition.FILE_OPEN,
                create_options=(
                    CreateOptions.FILE_NON_DIRECTORY_FILE
                    | CreateOptions.FILE_OPEN_REPARSE_POINT
                ),
            )

            size = file.end_of_file

            offset = 0
            chunk_size = 1024 * 1024
            while offset < size:
                to_read = min(chunk_size, size - offset)
                data = file.read(offset=offset, length=to_read)
                file_obj.write(data)
                offset += len(data)

            file_obj.seek(0)
            file.close()
        # except FileNotFound:
        #     raise OperationFailure(f"File not found: {path}")
        except AccessDenied:
            raise OperationFailure(f"Access denied: {path}")
        except SMBException as e:
            raise OperationFailure(f"Failed to retrieve file '{path}': {e}") from e

    def storeFileSFTP(self, share_name, path, file_obj):
        try:
            # self.disconnectTree()
            if not self.tree:
                self.connectTree(share_name)

            file = Open(self.tree, path)
            # file.create(create_disposition=CreateDisposition.FILE_OVERWRITE_IF,
            #            file_attributes=FileAttributes.FILE_ATTRIBUTE_NORMAL)
            file.create(
                ImpersonationLevel.Impersonation,
                FilePipePrinterAccessMask.GENERIC_WRITE
                | FilePipePrinterAccessMask.DELETE,
                FileAttributes.FILE_ATTRIBUTE_NORMAL,
                ShareAccess.FILE_SHARE_READ,
                CreateDisposition.FILE_OVERWRITE_IF,
                CreateOptions.FILE_NON_DIRECTORY_FILE,  # | CreateOptions.FILE_DELETE_ON_CLOSE,
            )
            offset = 0
            lasposition = 0
            # chunk_size = min(4 * 1024 * 1024, self.session.connection.max_read_size or 1024 * 1024)
            chunk_size = min(
                16 * 1024 * 1024,
                self.session.connection.max_read_size or 4 * 1024 * 1024,
            )

            file_obj.seek(0)

            while True:
                lasposition = file_obj.tell()
                chunk_size = min(
                    16 * 1024 * 1024,
                    self.session.connection.max_read_size or 4 * 1024 * 1024,
                )
                print(
                    f"NAS Max bytes size allowed:  {self.session.connection.max_read_size} "
                )
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                # try:
                #     file.write(chunk, offset=offset)
                #     offset += len(chunk)
                # except SMBException as e:
                #     if "credits" in str(e).lower():
                #         print('Throttled by NAS  retrying after pause.')
                #         time.sleep(2)
                #         continue
                #     raise
                r = [2, 2, 2]
                for sl in r:
                    try:
                        file.write(chunk, offset=offset)
                        offset += len(chunk)
                        break
                    except SMBException as e:
                        if "credits" in str(e).lower():
                            print("Throttled by NAS  retrying after pause.")
                            time.sleep(2)

            file.close()
        except AccessDenied:
            raise OperationFailure(f"Access denied to write: {path}")
        except SMBException as e:
            raise OperationFailure(f"Failed to store file '{path}': {e}") from e
        except Exception as ee:
            raise e
    def storeFile(self, share_name, path, file_obj):
        try:
            # self.disconnectTree()
            if not self.tree:
                self.connectTree(share_name)

            file = Open(self.tree, path)
            # file.create(create_disposition=CreateDisposition.FILE_OVERWRITE_IF,
            #            file_attributes=FileAttributes.FILE_ATTRIBUTE_NORMAL)
            file.create(
                ImpersonationLevel.Impersonation,
                FilePipePrinterAccessMask.GENERIC_WRITE
                | FilePipePrinterAccessMask.DELETE,
                FileAttributes.FILE_ATTRIBUTE_NORMAL,
                ShareAccess.FILE_SHARE_READ,
                CreateDisposition.FILE_OVERWRITE_IF,
                CreateOptions.FILE_NON_DIRECTORY_FILE,  # | CreateOptions.FILE_DELETE_ON_CLOSE,
            )
            offset = 0
            lasposition = 0
            # chunk_size = min(4 * 1024 * 1024, self.session.connection.max_read_size or 1024 * 1024)
            chunk_size = min(
                16 * 1024 * 1024,
                self.session.connection.max_read_size or 4 * 1024 * 1024,
            )

            file_obj.seek(0)

            while True:
                lasposition = file_obj.tell()
                chunk_size = min(
                    16 * 1024 * 1024,
                    self.session.connection.max_read_size or 4 * 1024 * 1024,
                )
                print(
                    f"NAS Max bytes size allowed:  {self.session.connection.max_read_size} "
                )
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                # try:
                #     file.write(chunk, offset=offset)
                #     offset += len(chunk)
                # except SMBException as e:
                #     if "credits" in str(e).lower():
                #         print('Throttled by NAS  retrying after pause.')
                #         time.sleep(2)
                #         continue
                #     raise
                r = [2, 2, 2]
                for sl in r:
                    try:
                        file.write(chunk, offset=offset)
                        offset += len(chunk)
                        break
                    except SMBException as e:
                        if "credits" in str(e).lower():
                            print("Throttled by NAS  retrying after pause.")
                            time.sleep(2)

            file.close()
        except AccessDenied:
            raise OperationFailure(f"Access denied to write: {path}")
        except SMBException as e:
            raise OperationFailure(f"Failed to store file '{path}': {e}") from e
        except Exception as ee:
            raise e

    def isConnected(self):
        return self.connected

    def close(self):
        try:
            if self.tree:
                self.tree.disconnect()
            if self.session:
                self.session.disconnect()
            if self.conn:
                self.conn.disconnect()
        except SMBException:
            pass


import time
import uuid
import logging
import argparse
import os
import sys
from io import BytesIO
from socket import timeout as SocketTimeout

import smbprotocol
from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
from smbprotocol.open import (
    CreateDisposition,
    CreateOptions,
    DirectoryAccessMask,
    FileAttributes,
    FileInformationClass,
    FilePipePrinterAccessMask,
    ImpersonationLevel,
    Open,
    ShareAccess,
)
from smbprotocol.exceptions import (
    # SMBException, NotConnected, AccessDenied
    SMBException,
    AccessDenied,
)

# Setup logger
logger = logging.getLogger("SMBConnection")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# Compatibility Exceptions
class SMBTimeout(SocketTimeout):
    pass


# class NotReadyError(NotConnected): pass
class OperationFailure(SMBException):
    pass


class SMBConnection:
    def __init__(
        self,
        username,
        password,
        my_name,
        remote_name,
        domain="",
        use_ntlm_v2=True,
        is_direct_tcp=True,
    ):
        self._lock = threading.Lock()
        self.username = username
        self.password = password
        self.my_name = my_name
        self.remote_name = remote_name
        self.domain = domain
        self.port = 445 if is_direct_tcp else 139
        self.conn = None
        self.session = None
        self.tree = None
        self.connected = False
        self.ip = remote_name
        self.uuid = uuid.uuid4()
        self.share_path="ApnaBackup/" 
        self.uploader =None
    # def __enter__(self):
    #     return self
    # def __exit__(self):

    #     try:
    #         self.close_connection()
    #     except:
    #         pass

    def close_connection(self):
        try:
            self.disconnectTree()
        except:
            pass
        try:
            self.session.disconnect()
        except:
            pass
        try:
            self.tree.disconnect()
        except:
            pass

    def connect(self, server_ip, port=445, timeout=200):
        import time as conn_time
        start_time = conn_time.time()
        log_connection_attempt(server_ip, self.username, port, "SMB3")
        try:
            logger.info("Connecting to %s:%d", server_ip, port)
            self.conn = Connection(guid=self.uuid, server_name=server_ip, port=port)
            self.conn.connect(timeout=timeout)

            self.session = Session(
                self.conn, username=self.username, password=self.password
            )
            self.session.connect()

            duration_ms = (conn_time.time() - start_time) * 1000
            logger.info("Connection and session established successfully")
            log_connection_result(server_ip, True, duration_ms=duration_ms)
            return True
        except SocketTimeout as e:
            duration_ms = (conn_time.time() - start_time) * 1000
            logger.error("SocketTimeout: %s", str(e))
            log_connection_result(server_ip, False, error=f"Timeout: {e}", duration_ms=duration_ms)
            raise SMBTimeout("Connection timed out") from e
        except SMBException as e:
            duration_ms = (conn_time.time() - start_time) * 1000
            logger.error("SMBException: %s", str(e))
            log_connection_result(server_ip, False, error=f"SMBException: {e}", duration_ms=duration_ms)
            raise OperationFailure(f"SMB connect failed: {e}") from e
        except Exception as e:
            duration_ms = (conn_time.time() - start_time) * 1000
            logger.exception("Unexpected error during connection")
            log_connection_result(server_ip, False, error=f"Unexpected: {e}", duration_ms=duration_ms)
            raise

    def connectTree(self, share_name):
        try:
            self.disconnectTree()
        except:
            pass

        try:
            self.share_path = share_name
            share_path = f"\\\\{self.ip}\\{share_name}"
            self.tree = TreeConnect(self.session, share_path)
            self.tree.connect()
            logger.info("Connected to tree/share: %s", share_name)
        except SMBException as e:
            logger.error("Failed to connect to share '%s': %s", share_name, str(e))
            raise OperationFailure(
                f"Failed to connect to share '{share_name}': {e}"
            ) from e

    def disconnectTree(self):
        try:
            if self.tree:
                self.tree.disconnect()
                logger.info("Disconnected from tree")
        except Exception:
            logger.warning("Error while disconnecting tree", exc_info=True)

    def ensure_connected(self, share_name):
        with self._lock:
            # If no connection object or session is invalid, reconnect
            if self.conn is None:
                self.tree = None
                self.session = None
                self.connect(self.remote_name, self.port)

            try:
                if self.session is None:
                    self.session = Session(
                        self.conn, username=self.username, password=self.password
                    )
                    self.session.connect()
                    self.tree = None
                # else:
                #     # Try a dummy operation to check session health
                #     self.session.connect()
                if not self.session._connected:
                    self.session.connect()
                    self.tree = None

            except SMBException as e:
                logger.warning("Session reconnect due to: %s", str(e))
                self.session = Session(
                    self.conn, username=self.username, password=self.password
                )
                self.session.connect()
                self.tree = None

            if self.tree is None:
                logger.info("Tree not connected connecting . . . ")
                self.connectTree(share_name)

    def ensure_remote_folder(self, share_name, folder_path):

        self.ensure_connected(share_name=share_name)
        folder = Open(self.tree, folder_path)
        try:
            # Try to open folder to check if exists
            folder.create(
                # desired_access=DirectoryAccessMask.FILE_LIST_DIRECTORY,
                # file_attributes=FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                # share_access=ShareAccess.FILE_SHARE_READ,
                # create_disposition=CreateDisposition.FILE_OPEN,
                # create_options=CreateOptions.FILE_DIRECTORY_FILE,
                ImpersonationLevel.Impersonation,
                DirectoryAccessMask.GENERIC_READ | DirectoryAccessMask.GENERIC_WRITE,
                FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                CreateDisposition.FILE_OPEN_IF,
                CreateOptions.FILE_DIRECTORY_FILE,
            )
            folder.close()
            return
        except SMBException as e:
            try:
                folder.close()
            except:
                pass

            # Folder doesn't exist, create it
            # To create nested folders, you may need to create each part recursively
            logger.info(f"Creating remote folder 1: {folder_path}")
            self.create_remote_folder_recursive(share_name, folder_path)
        except Exception as e:
            try:
                folder.close()
            except:
                pass
            # Folder doesn't exist, create it
            # To create nested folders, you may need to create each part recursively
            logger.info(f"Creating remote folder 3: {folder_path}")
            self.create_remote_folder_recursive(share_name, folder_path)

    def create_remote_folder_recursive(
        self,
        share_name,
        folder_path,
        folder_path_prefix_add=False,
        folder_path_sep_char="\\",
    ):
        from pathlib import PureWindowsPath

        self.ensure_connected(share_name=share_name)
        # folder_path = folder_path.strip("/")
        # folder_path = folder_path.strip(os.sep)
        # folder_path = folder_path.replace("/", os.sep)
        # parts = folder_path.replace("\\", "/").split("/")
        parts = folder_path.replace("\\", "/").strip("/").split("/")
        current_path = ""
        for part in parts:
            # current_path = f"{current_path}\\{part}" if current_path else part
            current_path = (
                str(PureWindowsPath(current_path) / part) if current_path else part
            )
            cp = current_path
            # current_path = current_path.strip("/")
            logger.info(f"Creating remote folder current_path: {current_path}")
            folder = Open(self.tree, cp)
            try:
                folder.create(
                    ImpersonationLevel.Impersonation,
                    DirectoryAccessMask.GENERIC_READ
                    | DirectoryAccessMask.GENERIC_WRITE,
                    FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                    ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                    CreateDisposition.FILE_OPEN_IF,
                    CreateOptions.FILE_DIRECTORY_FILE,
                )
                folder.close()
            except SMBException:
                try:
                    folder.close()
                except:
                    pass
                # Folder doesn't exist, create it now
                try:
                    cp = "\\" + current_path
                    logger.info(
                        f"trying creating remote folder current_path 2: {current_path} ({cp})"
                    )
                    folder = Open(self.tree, cp)
                    folder.create(
                        ImpersonationLevel.Impersonation,
                        DirectoryAccessMask.GENERIC_READ
                        | DirectoryAccessMask.GENERIC_WRITE,
                        FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                        ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                        CreateDisposition.FILE_OPEN_IF,
                        CreateOptions.FILE_DIRECTORY_FILE,
                    )
                    folder.close()
                except:
                    try:
                        folder.close()
                    except:
                        pass
                    # Folder doesn't exist, create it now
                    try:
                        cp = current_path.replace("\\", "/")
                        logger.info(
                            f"trying creating remote folder current_path 2: {current_path} ({cp})"
                        )
                        folder = Open(self.tree, current_path)
                        folder.create(
                            ImpersonationLevel.Impersonation,
                            DirectoryAccessMask.GENERIC_READ
                            | DirectoryAccessMask.GENERIC_WRITE,
                            FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                            ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
                            CreateDisposition.FILE_OPEN_IF,
                            CreateOptions.FILE_DIRECTORY_FILE,
                        )
                        folder.close()
                    except:
                        try:
                            folder.close()
                        except:
                            pass

                        try:
                            cp = "/" + current_path.replace("\\", "/")
                            logger.info(
                                f"Creating remote folder current_path 2: {current_path} ({cp})"
                            )
                            folder = Open(self.tree, cp)
                            folder.create(
                                ImpersonationLevel.Impersonation,
                                DirectoryAccessMask.GENERIC_READ
                                | DirectoryAccessMask.GENERIC_WRITE,
                                FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                                ShareAccess.FILE_SHARE_READ
                                | ShareAccess.FILE_SHARE_WRITE,
                                CreateDisposition.FILE_OPEN_IF,
                                CreateOptions.FILE_DIRECTORY_FILE,
                            )
                            folder.close()
                        except:
                            try:
                                folder.close()
                            except:
                                pass
            finally:
                try:
                    folder.close()
                except:
                    pass

    def listPath(self, share_name, path):
        try:
            if not self.tree:
                self.connectTree(share_name)

            directory = Open(self.tree, path)
            directory.create(
                disposition=CreateDisposition.FILE_OPEN,
                file_attributes=FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
            )
            entries = directory.query_directory(
                "*", information_class=FileInformationClass.FILE_DIRECTORY_INFORMATION
            )
            directory.close()

            logger.info("Listed directory: %s", path)
            return [
                entry.file_name
                for entry in entries
                if entry.file_name not in (".", "..")
            ]
        except SMBException as e:
            logger.error("Failed to list path '%s': %s", path, str(e))
            raise OperationFailure(f"Failed to list path '{path}': {e}") from e

    def retrieveFile(self, share_name, path, file_obj):
        try:
            if not self.tree:
                self.connectTree(share_name)

            file = Open(self.tree, path)
            file.create(
                impersonation_level=ImpersonationLevel.Impersonation,
                desired_access=(
                    FilePipePrinterAccessMask.FILE_READ_DATA
                    | FilePipePrinterAccessMask.FILE_READ_ATTRIBUTES
                    | FilePipePrinterAccessMask.FILE_READ_EA
                ),
                file_attributes=FileAttributes.FILE_ATTRIBUTE_NORMAL,
                share_access=ShareAccess.FILE_SHARE_READ,
                create_disposition=CreateDisposition.FILE_OPEN,
                create_options=(
                    CreateOptions.FILE_NON_DIRECTORY_FILE
                    | CreateOptions.FILE_OPEN_REPARSE_POINT
                ),
            )

            size = file.end_of_file
            offset = 0
            chunk_size = 1024 * 1024

            while offset < size:
                to_read = min(chunk_size, size - offset)
                data = file.read(offset=offset, length=to_read)
                file_obj.write(data)
                offset += len(data)

            file_obj.seek(0)
            file.close()
            logger.info("File retrieved: %s", path)
        except AccessDenied:
            logger.error("Access denied: %s", path)
            raise OperationFailure(f"Access denied: {path}")
        except SMBException as e:
            logger.error("Failed to retrieve file '%s': %s", path, str(e))
            raise OperationFailure(f"Failed to retrieve file '{path}': {e}") from e
    
    def get_SFTP_uploader(self, share_name, path, file_obj):
        try:
            if not self.uploader:
                self.uploader = module23.SFTPUploader(
                    hostname=self.ip,
                    port=22,
                    username=self.username,
                    password=self.password,
                    max_workers=16
                )
        except:
            self.uploader =None
        return self.uploader
            
           
    def storeFileSFTP(self, share_name, local_path, file_obj):
        try:
            remote_path=os.path.join(share_name,local_path).replace("\\","/")
            

            retries = 3
            while retries<4:
                try:
                    self.get_SFTP_uploader(share_name, local_path, file_obj)

                    self.uploader._upload_file_Bytes(local_path=local_path
                                                     ,remote_path=remote_path
                                                     ,encrypted_chunk=file_obj)
                    break
                except Exception as e:
                    
                    logger.error(
                        "Write failed at offset %d: %s")  
                retries=retries+1         
            logger.info("File stored successfully: %s", local_path)
        except AccessDenied:
            logger.error("Access denied to write: %s", local_path)
            raise OperationFailure(f"Access denied to write: {local_path}")
        except SMBException as e:
            logger.error("Failed to store file '%s': %s", local_path, str(e))
            raise Exception(f"Failed to store file '{local_path}': {e}") from e

    def storeFile(self, share_name, path, file_obj):
        import time as store_time
        start_time = store_time.time()
        unc_log_info(f"SMB_STORE_START | share={share_name} | path={path}")
        
        try:
            self.ensure_connected(share_name)

            file = Open(self.tree, path)
            file.create(
                ImpersonationLevel.Impersonation,
                FilePipePrinterAccessMask.GENERIC_WRITE
                | FilePipePrinterAccessMask.DELETE,
                FileAttributes.FILE_ATTRIBUTE_NORMAL,
                ShareAccess.FILE_SHARE_READ,
                CreateDisposition.FILE_OVERWRITE_IF,
                CreateOptions.FILE_NON_DIRECTORY_FILE,
            )

            offset = 0
            # Adaptive chunk size based on connection type:
            # - Localhost (127.0.0.1): Use smaller chunks to avoid credit exhaustion
            # - LAN/Remote: Use larger chunks for better throughput (fewer round trips)
            is_localhost = self.ip in ("127.0.0.1", "localhost", "::1")
            if is_localhost:
                chunk_size = 4 * 1024 * 1024  # 4 MB for local Windows SMB
                unc_log_debug(f"Using 4MB chunks for localhost connection")
            else:
                # For LAN/remote, use larger chunks (16 MB) - more efficient over network
                chunk_size = 16 * 1024 * 1024  # 16 MB for network transfers
                unc_log_debug(f"Using 16MB chunks for network connection to {self.ip}")

            file_obj.seek(0)
            bytes_written = 0

            while True:
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break

                retries = 3
                while retries:
                    try:
                        file.write(chunk, offset=offset)
                        offset += len(chunk)
                        bytes_written += len(chunk)
                        break
                    except SMBException as e:
                        if "credit" in str(e).lower() or "STATUS_INSUFFICIENT_RESOURCES" in str(e):
                            backoff = 2 + random.uniform(0, 2)
                            logger.warning("SMB throttled. Waiting %.1fs before retrying...", backoff)
                            unc_log_info(f"SMB_THROTTLE | path={path} | backoff={backoff:.1f}s")
                            time.sleep(backoff)
                            retries -= 1
                        else:
                            logger.error("Write failed at offset %d: %s", offset, str(e))
                            unc_log_error("smb_write", e, context=f"path={path} offset={offset}")
                            raise

            file.close()
            duration = store_time.time() - start_time
            logger.info("File stored successfully: %s", path)
            unc_log_info(f"SMB_STORE_SUCCESS | path={path} | bytes={bytes_written} | duration={duration:.2f}s")
        except AccessDenied as e:
            duration = store_time.time() - start_time
            logger.error("Access denied to write: %s", path)
            unc_log_error("smb_store_access_denied", e, context=f"path={path} duration={duration:.2f}s")
            raise OperationFailure(f"Access denied to write: {path}")
        except SMBException as e:
            duration = store_time.time() - start_time
            logger.error("Failed to store file '%s': %s", path, str(e))
            unc_log_error("smb_store", e, context=f"path={path} duration={duration:.2f}s")
            raise Exception(f"Failed to store file '{path}': {e}") from e


def upload_files(smb_conn, share_name, local_files, remote_folder):

    for local_file in local_files:
        try:
            filename = os.path.basename(local_file)
            remote_path = f"{remote_folder}\\{filename}" if remote_folder else filename
            logger.info(
                f"Uploading file {local_file} to {remote_path} on share {share_name}"
            )

            with open(local_file, "rb") as f:
                smb_conn.storeFile(share_name, remote_path, f)

            logger.info(f"Uploaded {local_file} successfully.")
        except Exception as e:
            logger.error(f"Failed to upload {local_file}: {e}")


def download_files(smb_conn, share_name, remote_files, local_folder):
    for remote_file in remote_files:
        try:
            filename = os.path.basename(remote_file)
            local_path = os.path.join(local_folder, filename)
            logger.info(
                f"Downloading file {remote_file} from share {share_name} to {local_path}"
            )

            with open(local_path, "wb") as f:
                smb_conn.retrieveFile(share_name, remote_file, f)

            logger.info(f"Downloaded {remote_file} successfully.")
        except Exception as e:
            logger.error(f"Failed to download {remote_file}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="SMBConnection CLI for batch upload/download"
    )
    parser.add_argument("host", help="SMB server hostname or IP")
    parser.add_argument("share", help="SMB share name")
    parser.add_argument("username", help="Username")
    parser.add_argument("password", help="Password")
    parser.add_argument("--domain", default="", help="Domain (optional)")
    parser.add_argument(
        "--operation",
        choices=["upload", "download"],
        required=True,
        help="Operation to perform",
    )
    parser.add_argument(
        "--files", nargs="+", required=True, help="Files to upload/download"
    )
    parser.add_argument(
        "--remote-folder", default="", help="Remote folder inside the share (optional)"
    )
    parser.add_argument(
        "--local-folder",
        default=".",
        help="Local folder for downloads (default current dir)",
    )

    args = parser.parse_args()

    smb_conn = SMBConnection(
        username=args.username,
        password=args.password,
        my_name="localclient",  # Replace with your client name if needed
        remote_name=args.host,
        domain=args.domain,
    )

    try:
        smb_conn.connect(args.host)
        smb_conn.connectTree(args.share)

        if args.operation == "upload":
            smb_conn.ensure_remote_folder(args.share, args.remote_folder)
            upload_files(smb_conn, args.share, args.files, args.remote_folder)
        elif args.operation == "download":
            download_files(smb_conn, args.share, args.files, args.local_folder)

    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)
    finally:
        smb_conn.disconnectTree()


if __name__ == "__main__":
    main()


#from bz2 import compress
from concurrent.futures import ThreadPoolExecutor
import os
from time import sleep
from types import NoneType
import wmi
import pythoncom  # Required for COM initialization
from pathlib import Path
import ctypes
import subprocess
from datetime import datetime

##kartik
import logging
import logging.handlers
import sys

# Create a logs folder if it doesn't exist
os.makedirs("every_logs", exist_ok=True)

LOG_FILE = "every_logs/class1x.log"

# Create the main logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Define a detailed log format
detailed_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s:%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
)

# --- 1 File handler ---
file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_format)

# --- 2 Console handler ---
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(detailed_format)

# Add file + console handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# --- 3 Windows Event Viewer handler ---
try:
    event_handler = logging.handlers.NTEventLogHandler(appname="ABS")
    event_handler.setLevel(logging.DEBUG)
    event_formatter = logging.Formatter(
        "[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    event_handler.setFormatter(event_formatter)
    logger.addHandler(event_handler)
except Exception as e:
    logger.warning(f"Could not attach Windows Event Viewer handler: {e}")
##kartik


class ShadowCopyFailure(Exception):
    pass

class OpenShFile:
    def __init__(self, file, mode="r", buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None,shadow_scheduler_GUID=None):
        
        # """
        # Creates a shadow copy of the volume containing `file` and opens the shadowed version.
        # Supports all parameters of Python’s built-in `open()`.
        
        # :param file: Path to the file that needs to be shadowed and opened.
        # :param mode: File open mode (e.g., "r", "rb", "w", etc.).
        # :param buffering: Buffering policy (-1 for default, 0 for unbuffered, etc.).
        # :param encoding: Encoding name (for text mode).
        # :param errors: Error handling strategy.
        # :param newline: How newlines are handled in text mode.
        # :param closefd: Whether to close the file descriptor after the file is closed.
        # :param opener: Custom opener function.
        # """

        self.original_file = Path(file).resolve()
        self.mode = mode
        self.buffering = buffering
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        self.closefd = closefd
        self.opener = opener
        self.encryption_key=None
        self.iv=None

        self.shadow_obj = None
        self.shadow_file = None
        self.file_handle = None
        self.shadow_id = None
        self.shadow_GUID = None
        self.shadow_scheduler_GUID = shadow_scheduler_GUID
        self.Volume=self.get_drive_letter()
    def __enter__(self):   
        
        try:
            self.OpenFileSha()
            return self.file_handle
        except:
            print("asdf")
            try:
                self.OpenFlatFile()
                return self.file_handle
            except Exception as err:
                raise ShadowCopyFailure(f"Unable to return file. Error Code: {str(err)}")

    @staticmethod
    def get_recent_shadow_copy(volume_letter, max_age_seconds=60):
        """
        Finds any shadow copy for the given volume created within 'max_age_seconds'.
        Returns the shadow copy ID or None.
    
        Args:
            volume_letter: Drive letter (e.g., 'C:\\') or volume path
            max_age_seconds: Maximum age in seconds for valid shadow copies
    
        Returns:
            Shadow copy ID string or None
        """
        pythoncom.CoInitialize()
        c = wmi.WMI()
    
        # Normalize volume letter to uppercase without trailing backslash
        normalized_volume = volume_letter.rstrip(os.sep).upper()
    
        try:
            all_shadows = c.Win32_ShadowCopy()
        except Exception as e:
            logger.error(f"Failed to query shadow copies: {str(e)}")
            return None
    
        for sc in all_shadows:
            try:
                # Get volume information from shadow copy
                # VolumeName property contains the volume GUID path
                volume_name = getattr(sc, "VolumeName", None)
            
                if not volume_name:
                    continue
            
                # Convert volume GUID path to drive letter for comparison
                # Example: '\\?\Volume{guid}\' -> 'C:\'
                try:
                    # Use GetVolumePathNamesForVolumeName to map GUID to drive letter
                    import win32file
                    drive_letters = win32file.GetVolumePathNamesForVolumeName(volume_name)
                
                    if not drive_letters:
                        continue
                
                    # Check if any mapped drive letter matches our target
                    match_found = False
                    for drive in drive_letters:
                        if drive.rstrip(os.sep).upper() == normalized_volume:
                            match_found = True
                            break
                
                    if not match_found:
                        continue
                    
                except Exception:
                    # Fallback: direct string comparison if win32file not available
                    # This handles cases where volume_name might directly contain drive letter
                    if normalized_volume not in volume_name.upper():
                        continue
            
                # Check shadow copy age
                if not sc.InstallDate:
                    continue
            
                # Parse InstallDate (format: YYYYMMDDHHMMSS.mmmmmm±UUU)
                install_date_str = sc.InstallDate.split('.')[0]
                install_time = datetime.strptime(install_date_str, "%Y%m%d%H%M%S")
            
                # Calculate age in seconds
                current_time = datetime.now()
                age = (current_time - install_time).total_seconds()
            
                if age <= max_age_seconds:
                    logger.info(f"Found recent shadow copy (age: {age:.1f}s): {sc.ID}")
                    return sc.ID
                
            except Exception as e:
                logger.debug(f"Error processing shadow copy {getattr(sc, 'ID', 'unknown')}: {str(e)}")
                continue
    
        return None

    def get_drive_letter(self):
        drive_letter_with_colon, rest_of_path = os.path.splitdrive(self.original_file)
        return drive_letter_with_colon
    
    def OpenFileSha(self):
        pythoncom.CoInitialize()
        c = wmi.WMI()
        if self.shadow_scheduler_GUID:            
            try:
                self.shadow_id =self.shadow_scheduler_GUID
                self.shadow_obj = c.Win32_ShadowCopy(ID=self.shadow_id )[0]
                if not self.shadow_obj:
                    self.shadow_id =None
            except:
                self.shadow_id =None
                self.shadow_obj =None

        # Extract drive and path
        drive_letter_with_colon, rest_of_path = os.path.splitdrive(self.original_file)
        rest_of_path = rest_of_path.lstrip(os.sep)

        Volume=f"{drive_letter_with_colon}{os.sep}"

        self.shadow_id = OpenShFile.get_recent_shadow_copy(volume_letter=Volume, max_age_seconds=60)

        if not self.shadow_id: 
            # Create a shadow copy of the volume
            i_retry=6
            while(i_retry>0):
                i_retry=i_retry-1
                result, self.shadow_id = c.Win32_ShadowCopy.Create(
                    Context="ClientAccessible", Volume=Volume
                )
                # if not os.path.isfile(self.original_file):
                #     self.file_handle=None
                #     return result, shadow_id 
            
                if result ==0:
                    i_retry=0
                    break
                else:
                    sleep(15)
                    if i_retry==0:
                        i_retry=-1
                        if result != 0:
                            raise ShadowCopyFailure(f"Unable to create sha file. Error Code: {result}")
                        

        # Retrieve shadow copy object
        self.shadow_obj = c.Win32_ShadowCopy(ID=self.shadow_id)[0]
        shadow_volume_path = self.shadow_obj.DeviceObject

        # Construct the shadowed file path
        self.shadow_file = os.path.join(shadow_volume_path, rest_of_path)

        if not os.path.exists(self.shadow_file):
            raise FileNotFoundError(f"Shadowed file not found: {self.original_file}")

        # Open the shadowed file with all original parameters
        try:
            self.file_handle = open(
                self.shadow_file,
                mode=self.mode,
                buffering=self.buffering,
                encoding=self.encoding,
                errors=self.errors,
                newline=self.newline,
                closefd=self.closefd,
                opener=self.opener
            )
            return self.file_handle
        except Exception as shadow_error:
            logger.warning(f"Error in shadow copy {str(shadow_error)}")
            return self.shadow_id

    
    def get_path(self,original_file):
        pythoncom.CoInitialize()
        c = wmi.WMI()

        # Extract drive and path
        drive_letter_with_colon, rest_of_path = os.path.splitdrive(original_file)
        rest_of_path = rest_of_path.lstrip(os.sep)
        if not self.shadow_obj:
            logger.warning("Shadow object not available; using original path")
            return None
        shadow_volume_path = getattr(self.shadow_obj, "DeviceObject", None)
        if not shadow_volume_path:
            logger.warning("Shadow object missing DeviceObject; using original path")
            return None

        # Construct the shadowed file path
        shadow_file = os.path.join(shadow_volume_path, rest_of_path)

        if not os.path.exists(shadow_file):
            raise FileNotFoundError(f"Shadowed file not found: {shadow_file}")
            return None
        # Open the shadowed file with all original parameters
        
        return shadow_file
        

    def OpenFlatFile(self):
        if not os.path.exists(self.original_file):
            raise FileNotFoundError(f"file not found (Flat): {self.original_file}")
            return

        # Directories cannot be opened with open() — causes [Errno 13] Permission denied on Windows.
        # For folder backups we only need the path; each file is opened by path later.
        if self.original_file.is_dir():
            self.file_handle = None
            return self.file_handle

        self.file_handle = open(
            self.original_file,
            mode=self.mode,
            buffering=self.buffering,
            encoding=self.encoding,
            errors=self.errors,
            newline=self.newline,
            closefd=self.closefd,
            opener=self.opener
        )

        return self.file_handle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_handle:
            self.file_handle.close()

        # Delete the shadow copy
        if self.shadow_obj:
            self.shadow_obj.Delete_()
    
    def encrypt_chunk(self, chunk):
        """Encrypt a chunk using AES-256."""
        from concurrent.futures import ThreadPoolExecutor
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        iv = self.iv #os.urandom(16)  # Generate a random IV for each chunk
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        return iv + encryptor.update(chunk) + encryptor.finalize()

    def decrypt_chunk(self, chunk):
        """Decrypt an AES-256 encrypted chunk."""
        from concurrent.futures import ThreadPoolExecutor
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        iv = chunk[:16]
        encrypted_data = chunk[16:]
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()

    def get_compressed(self,CHUNK_SIZE=-1):

        from zstandard import ZstdCompressor
        compressor = ZstdCompressor(level=22,threads=4)
        try:
            chunk = self.file_handle.read(CHUNK_SIZE)
            compressed_chunk = compressor.compress(chunk)
            return compressed_chunk
        except Exception as exce:
            return None
    def get_decompressed(self,CHUNK_SIZE=-1):

        from zstandard import ZstdCompressor
        compressor = ZstdCompressor(level=22,threads=4)
        try:
            chunk = self.file_handle.read(CHUNK_SIZE)
            compressed_chunk = compressor.compress(chunk)
            return compressed_chunk
        except Exception as exce:
            return None
    
    # def get_compressed_encrypted(self,CHUNK_SIZE=-1):
    #     #import zstd
    #     from zstandard import ZstdCompressor
    #     compressor = ZstdCompressor(level=22)
    #     raw_data = bytearray()
    #     total_size = os.path.getsize(self.shadow_file)
    #     with ThreadPoolExecutor(max_workers=4) as executor:
    #         futures = []
    #         for _ in range(0, total_size, CHUNK_SIZE):
    #             chunk = self.file_handle.read(CHUNK_SIZE)
    #             compressed_chunk = compressor.compress(chunk)
    #             encrypted_chunk = self.encrypt_chunk(compressed_chunk)
    #             futures.append(executor.submit(raw_data.extend, encrypted_chunk))

    #         for future in futures:
    #             future.result()

    #     return bytes(raw_data)



# shadow_id=NoneType
# file_n= r"D:\76767\d.txt"
# dd= OpenShFile(r"D:\76767")
# xse = dd.OpenFileSha()
# try:
#     with open(dd.get_path( original_file= file_n)) as dts:
#         print(dts.read())
# except:
#     print("")
# dd.shadow_obj.Delete_()

# # with OpenShFile("D:\76767") as x:
# #     print(x)
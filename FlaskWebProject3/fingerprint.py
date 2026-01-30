# unique_fingerprint.py

import base64
import hashlib
import platform
#from typing import Any
import uuid
#import sys
import os
#import shutil
#import ctypes

#from ctypes import wintypes
#import cpuinfo
import subprocess

#from flask import app

##kartik 8-11-2025
import logging
import logging.handlers
import sys

# Create a logs folder if it doesn't exist
os.makedirs("every_logs", exist_ok=True)

LOG_FILE = "every_logs/server_fpt.log"

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

##kartik 8-11-2025
##kartik 8-11-2025
try:
    import win32com.client
except Exception:
    win32com = None

def safe_cmd(cmd, args=None):
    """Run a command safely, return stdout as str."""
    try:
        if args:
            proc = subprocess.run([cmd] + args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        else:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False, shell=True)
        return proc.stdout.decode(errors="ignore").strip()
    except Exception:
        return None


def safe_powershell(command):
    """Run PowerShell safely and return output."""
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            stderr=subprocess.DEVNULL
        )
        return out.decode(errors="ignore").strip()
    except Exception:
        return None


def try_wmi_query(query, field):
    """Return ALL WMI values for the given field."""
    if win32com is None:
        return None
    try:
        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        svc = locator.ConnectServer(".", "root\\cimv2")
        res = svc.ExecQuery(query)

        values = []
        for r in res:
            val = getattr(r, field, None)
            if val:
                values.append(str(val).strip())

        return values if values else None

    except Exception:
        return None


# ---------------- Serial Fetch Functions ----------------
def get_bios_serial_s():
    val = try_wmi_query("SELECT SerialNumber FROM Win32_BIOS", "SerialNumber")
    if val and val[0] not in ["None", None, ""]:
        return val[0]

    for ps in [
        "(Get-CimInstance Win32_BIOS).SerialNumber",
        "(Get-WmiObject Win32_BIOS).SerialNumber",
        "Get-CimInstance -ClassName Win32_BIOS | Select -ExpandProperty SerialNumber"
    ]:
        out = safe_powershell(ps)
        if out and out != 'None':
            return out.strip()

    out = safe_cmd("wmic", ["bios", "get", "SerialNumber"])
    if out and out != 'None':
        lines = [l.strip() for l in out.splitlines() if l.strip() and "serial" not in l.lower()]
        return lines[0] if lines else None

    return None 


def get_board_serial_s():
    val = try_wmi_query("SELECT SerialNumber FROM Win32_BaseBoard", "SerialNumber")
    if val and val[0] not in ["None", None, ""]:
        return val[0]

    for ps in [
        "(Get-CimInstance Win32_BaseBoard).SerialNumber",
        "(Get-WmiObject Win32_BaseBoard).SerialNumber",
        "Get-CimInstance -ClassName Win32_BaseBoard | Select -ExpandProperty SerialNumber"
    ]:
        out = safe_powershell(ps)
        if out and out != 'None':
            return out.strip()

    out = safe_cmd("wmic", ["baseboard", "get", "SerialNumber"])
    if out and out != 'None':
        lines = [l.strip() for l in out.splitlines() if l.strip() and "serial" not in l.lower()]
        return lines[0] if lines else None

    return None


def get_cpu_id_s():
    val = try_wmi_query("SELECT ProcessorId FROM Win32_Processor", "ProcessorId")
    if val:
        return val

    for ps in [
        "(Get-CimInstance Win32_Processor).ProcessorId",
        "(Get-WmiObject Win32_Processor).ProcessorId",
        "Get-CimInstance -ClassName Win32_Processor | Select -ExpandProperty ProcessorId"
    ]:
        out = safe_powershell(ps)
        if out and out != 'None':
            return [out.strip()]

    out = safe_cmd("wmic", ["cpu", "get", "ProcessorId"])
    if out and out != 'None':
        lines = [l.strip() for l in out.splitlines() if l.strip() and "processor" not in l.lower()]
        return lines if lines else None

    return None


def get_hdd_serials_s():
    serials = []

    # WMI COM
    if win32com is not None:
        try:
            locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            svc = locator.ConnectServer(".", "root\\cimv2")
            res = svc.ExecQuery("SELECT SerialNumber FROM Win32_DiskDrive")
            for r in res:
                sn = getattr(r, "SerialNumber", None)
                if sn:
                    serials.append(sn.strip())
        except Exception:
            pass

    # PowerShell (CIM + WMI + PhysicalDisk)
    for ps in [
        "(Get-CimInstance Win32_DiskDrive | Select -ExpandProperty SerialNumber)",
        "(Get-WmiObject Win32_DiskDrive | Select -ExpandProperty SerialNumber)",
        "(Get-PhysicalDisk | Select -ExpandProperty SerialNumber)",
        "(Get-Disk | Select -ExpandProperty SerialNumber)",
        "Get-CimInstance -ClassName Win32_DiskDrive | Select -ExpandProperty SerialNumber"
    ]:
        out = safe_powershell(ps)
        if out and out != 'None':
            serials += [line.strip() for line in out.splitlines() if line.strip()]

    # WMIC fallback
    out = safe_cmd("wmic", ["diskdrive", "get", "SerialNumber"])
    if out and out != 'None':
        lines = [l.strip() for l in out.splitlines() if l.strip() and "serial" not in l.lower()]
        serials += lines

    return list(dict.fromkeys([s for s in serials if s]))
##kartik 8-11-2025

def get_hdd_serials():
    hdd_serials = []
    if platform.system() == "Windows":
        # output = (
        #     subprocess.check_output("wmic diskdrive get serialnumber", shell=False)
        #     .decode()
        #     .strip()
        #     .split("\n")[1:]
        # )
        hdd = get_hdd_serials_s()
 
        hdd_serials = hdd #[serial.strip() for serial in output if serial.strip()] 
        # print("343333333333333333333333333333333333333333333333333333333333444888 hdd", [serial.strip() for serial in output if serial.strip()])
      
    elif platform.system() == "Linux":
        output = (
            subprocess.check_output(
                "lsblk -o NAME,SERIAL | grep -v '^\\s*$'", shell=False
            )
            .decode()
            .strip()
            .split("\n")[1:]
        )
        hdd_serials = [line.split()[1] for line in output if len(line.split()) > 1]

    return hdd_serials


def get_cpu_ids():
    try:    
        cpu_ids = []
        if platform.system() == "Windows":
            # For Windows, use WMI to get the processor IDs
            # output = (
            #     subprocess.check_output("wmic cpu get processorid", shell=False)
            #     .decode()
            #     .strip()
            #     .split("\n")[1:]
            # )
            cpu = get_cpu_id_s()
    
       
            cpu_ids = cpu #[cpu_id.strip() for cpu_id in output if cpu_id.strip()] 
            # print("343333333333333333333333333333333333333333333333333333333333444888 cou",[cpu_id.strip() for cpu_id in output if cpu_id.strip()])
           
        elif platform.system() == "Linux":
            # For Linux, get CPU information from /proc/cpuinfo
            output = (
                subprocess.check_output(
                    "cat /proc/cpuinfo | grep 'processor\\|model name'", shell=False
                )
                .decode()
                .strip()
                .split("\n")
            )
            cpu_ids = [
                line.split(":")[-1].strip() for line in output if "processor" in line
            ]

        return cpu_ids
    except:
        return None

def get_motherboard_serial():
    import subprocess
    import platform
    try:    
        serial_number = None
        if platform.system() == "Windows":
            # For Windows, use WMI to get the motherboard serial number
            # output = (
            #     subprocess.check_output("wmic baseboard get serialnumber", shell=False)
            #     .decode()
            #     .strip()
            #     .split("\n")[1:]  # Ignore the header row
            # )
            board = get_board_serial_s()
          
            serial_number = board #output[0].strip() if output else None 
            # print("343333333333333333333333333333333333333333333333333333333333444888 mo", output[0].strip() if output else None)
           
        elif platform.system() == "Linux":
            # For Linux, get motherboard serial number from dmidecode
            output = (
                subprocess.check_output("sudo dmidecode -s baseboard-serial-number", shell=False)
                .decode()
                .strip()
            )
            serial_number = output if output else None

        return serial_number
    except:# Exception as e:
        return None


def get_bios_serial():
    import subprocess
    import platform
    try:    
        serial_number = None
        if platform.system() == "Windows":
            # For Windows, use WMI to get the BIOS serial number
            # output = (
            #     subprocess.check_output("wmic bios get serialnumber", shell=False)
            #     .decode()
            #     .strip()
            #     .split("\n")[1:]  # Ignore the header row
            # )
            bios = get_bios_serial_s()
           
            serial_number = bios #output[0].strip() if output else None
            # print("343333333333333333333333333333333333333333333333333333333333444888 bo", output[0].strip() if output else None)
         
        elif platform.system() == "Linux":
            # For Linux, use dmidecode to get the BIOS serial number
            output = (
                subprocess.check_output("sudo dmidecode -s system-serial-number", shell=False)
                .decode()
                .strip()
            )
            serial_number = output if output else None
        return serial_number
    except:# Exception as e:
        return None


def concatenate_ids(ids):
    # Sort ids to maintain consistent order
    # change this to any other rule to maintain the order needed
    sorted_ids = sorted(ids)
    return "".join(sorted_ids)


def getCode():
    #from pyarmor.pyarmor import make_license_key
    from FlaskWebProject3 import app
    try:
        if not app.config["getCode"] is None:
            return app.config["getCode"]
    except:
        pass
    if True:
        system_info = platform.uname()
        ma = ":".join(hex(uuid.getnode())[2:].zfill(12)[i : i + 2] for i in range(0, 12, 2))
        us = f"ku{system_info.node}ld-ee{system_info.processor}pr-aa{ma}js-ha{system_info.system}rm-a{system_info.machine}"
        # import wmi
        # c= wmi.WMI()
        # for board in c.Win32_BaseBoard():
        #     print(f"Manufacturer: {board.Manufacturer}")
        #     print(f"Product: {board.Product}")
        #     print(f"Serial Number: {board.SerialNumber}")
        # for cpu in c.Win32_Processor():
        #     print(f"Processor ID: {cpu.ProcessorId}")
        #     print(f"Name: {cpu.Name}")
        #     print(f"Cores: {cpu.NumberOfCores}")
        #     print(f"Clock Speed: {cpu.MaxClockSpeed} MHz")
        # for disk in c.Win32_DiskDrive():
        #     print(f"Model: {disk.Model}")
        #     print(f"Serial Number: {disk.SerialNumber}")
        #     print(f"Size: {int(disk.Size) / (1024 ** 3):.2f} GB")
        #hdds = get_hdd_serials()
        cpus = get_cpu_ids()
        bios_serial =get_bios_serial()
        motherboard_serial =get_motherboard_serial()
        hdd_serials = ""
        cpu_ids = ""
        # if hdds:
        #     hdd_serials = concatenate_ids(hdds)
        #     #print("Concatenated HDD Serial Numbers:", hdd_serials)
        # else:
        #     print("")#No HDD serial numbers found.")

        if cpus:
            cpu_ids = concatenate_ids(cpus)
            #print("Concatenated CPU IDs:", cpu_ids)
        else:
            print("No IDs found.")
    # ####################################################################################################################################### 
    #     # if (hdds is not None and hdds != "None" and
    #     # cpus is not None and cpus != "None" and
    #     # bios_serial is not None and bios_serial != "None" and
    #     # motherboard_serial is not None and motherboard_serial != "None"):
    #     if hdds is not None and cpus is not None and bios_serial is not None and motherboard_serial is not None:
    #         us = f"ku{cpu_ids}ld-ee{motherboard_serial}pr-aa{bios_serial}js-ha{bios_serial}rm-a{cpu_ids}"
    #         # print(f"343333333333333333333333333333333333333333333333333333333333444444444444 fingerprint {us}")
    #         # print("==============")
    #         # print(us)
    #         # print("==============")
    #         # print(f"33333333333333333333333333333333333333333333333333333333333333333333data {us}")
    #         uh = hashlib.sha256(us.encode("utf-8")).hexdigest()
    #         # hdd = get_hdd_serials_s()
    #         # bios = get_bios_serial_s()
    #         # board = get_board_serial_s()
    #         # cpu = get_cpu_id_s()
    #         # print(f" cput   {cpu}")
    #         # cpus = concatenate_ids(cpu)
    #         # usss = f"ku{cpus}ld-ee{board}pr-aa{bios}js-ha{bios}rm-a{cpus}"
    #         # uhh = hashlib.sha256(usss.encode("utf-8")).hexdigest()
    #         # print(f"print usss {usss} ")
    #         # regcode = make_license_key(
    #         #     "ddd.lic",
    #         #     {
    #         #         "code": "1234",  # Optional: customer code or identifier
    #         #         "days": 30,  # License valid for 30 days
    #         #         "bind": uh,  # Bind to hardware if provided
    #         #     },
    #         # )
    
    #         # print(f"print key outputed {uh}")
    #         # print(f"print key outputed my {uhh}")
    #         return uh
    #     else:
    #         logger.warning(f"We dont find \n"
    #                        f"Processor or cpu serial number: {cpu_ids} \n"
    #                        f"Hard disk serial number: {hdds} \n"
    #                        f"BIOS serial number: {bios_serial} \n"
    #                        f"Mother board serail number: {motherboard_serial} \n"
    #                        )
    #         if getattr(sys, "frozen", False):
    #             sys.exit(0)
        
    ###################################################################################################################################### 

        ## the following is the alternate code that goes with some validations in above commented block
        ## the following code can be found in the true part of that block.    
        us = f"ku{cpu_ids}ld-ee{motherboard_serial}pr-aa{bios_serial}js-ha{bios_serial}rm-a{cpu_ids}"
        logger.info(f"For  testing check difference server abs {us}")
        # print(f"343333333333333333333333333333333333333333333333333333333333444444444444 fingerprint {us}")
        # print("==============")
        # print(us)
        # print("==============")
        # print(f"33333333333333333333333333333333333333333333333333333333333333333333data {us}")
        uh = hashlib.sha256(us.encode("utf-8")).hexdigest()
        return uh


def getCodeHost():
    system_info = platform.uname()
    us = f"{system_info.node}"

    return us


def getKey(keya: str = None,keyx: str = None):
    if not keya and not keyx:
        keya = getCode()
    if keyx:
        keya=keyx
    key = hashlib.sha256(keya.encode()).digest()
    for i in range(25):
        key = hashlib.sha256(key).digest()
    
    print(str(key))
    return key

def getRequestKey():
    from FlaskWebProject3 import app 
    import base64
    d = getCode()
    json_data = {
        "email": "",
        "IPname": str(app.config.get("getCodeHost",None)),
        "application": "Apna-Backup-Server",
        "activationkey": base64.b64encode(
            d.encode("UTF-8"),
        ).hex("-", 8),
    }
    return json_data

def get_hKey(keya: str = None):
    if not keya:
        keya = getCode()
    key= hashlib.md5(keya.encode()).hexdigest()
    return key


def get_encryption_key_storage():
    unique_id = getCode()
    hash_key = hashlib.sha256(unique_id.encode()).digest()
    return base64.urlsafe_b64encode(hash_key[:32])

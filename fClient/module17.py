import os
import platform
import psutil
from typing import List, Optional

def get_hdd_serials() -> List[str]:
    hdd_serials = []
    try:
        if platform.system() == "Windows":
            import win32com.client
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            conn = wmi.ConnectServer(".", "root\\cimv2")
            drives = conn.ExecQuery("SELECT SerialNumber FROM Win32_DiskDrive")
            hdd_serials = [drive.SerialNumber.strip() for drive in drives if drive.SerialNumber]
        elif platform.system() == "Linux":
            for disk in psutil.disk_partitions(all=True):
                base_device = os.path.basename(disk.device)
                serial_path = f"/sys/block/{base_device}/serial"
                if os.path.exists(serial_path):
                    with open(serial_path, "r") as f:
                        serial = f.read().strip()
                        if serial:
                            hdd_serials.append(serial)
    except Exception as e:
        print(f"Error getting HDD serials: {e}")
    return hdd_serials


def get_cpu_ids() -> List[str]:
    cpu_ids = []
    try:
        if platform.system() == "Windows":
            import win32com.client
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            conn = wmi.ConnectServer(".", "root\\cimv2")
            cpus = conn.ExecQuery("SELECT ProcessorId FROM Win32_Processor")
            cpu_ids = [cpu.ProcessorId.strip() for cpu in cpus if cpu.ProcessorId]
        elif platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "processor" in line:
                        cpu_ids.append(line.split(":")[-1].strip())
    except Exception as e:
        print(f"Error getting CPU IDs: {e}")
    return cpu_ids


def get_motherboard_serial() -> Optional[str]:
    try:
        if platform.system() == "Windows":
            import win32com.client
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            conn = wmi.ConnectServer(".", "root\\cimv2")
            boards = conn.ExecQuery("SELECT SerialNumber FROM Win32_BaseBoard")
            return boards[0].SerialNumber.strip() if boards else None
        elif platform.system() == "Linux":
            path = "/sys/devices/virtual/dmi/id/board_serial"
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read().strip()
    except Exception as e:
        print(f"Error getting motherboard serial: {e}")
    return None


def get_bios_serial() -> Optional[str]:
    try:
        if platform.system() == "Windows":
            import win32com.client
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            conn = wmi.ConnectServer(".", "root\\cimv2")
            bios = conn.ExecQuery("SELECT SerialNumber FROM Win32_BIOS")
            return bios[0].SerialNumber.strip() if bios else None
        elif platform.system() == "Linux":
            path = "/sys/devices/virtual/dmi/id/bios_version"
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read().strip()
    except Exception as e:
        print(f"Error getting BIOS serial: {e}")
    return None


# # Test Outputs
# if __name__ == "__main__":
#     from time import time
#     print(time())
#     print(f"HDD Serials: {get_hdd_serials()}")
#     print(f"CPU IDs: {get_cpu_ids()}")
#     print(f"Motherboard Serial: {get_motherboard_serial()}")
#     print(f"BIOS Serial: {get_bios_serial()}")
#     print(time())
#     print("==========================================")
#     print(time())
#     import fClient.fingerprint as fp
#     print(fp.get_hdd_serials())
#     print(fp.get_cpu_ids())
#     print(fp.get_motherboard_serial())
#     print(fp.get_bios_serial())
#     print(time())



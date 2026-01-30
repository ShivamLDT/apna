import json
import os
import platform
import psutil
import subprocess
from fpdf import FPDF
import xlsxwriter
import uuid
import wmi
import sys
def get_original_executable_path():
    if getattr(sys, "frozen", False):
        # For PyInstaller frozen executables
        return sys.executable
    else:
        # For running the script directly
        return os.path.abspath(__file__)

class ServerSystemReportGenerator:
    def __init__(self,app,computer_id="_computer_"
                 ,client_version="_unknown_"
                 ,client_activation_date="_unknown_"
                 ,client_connected_nodes="_unknown_"):
        self.data = {}
        self.app=app
        self.computer_id = computer_id
        self.client_version = self.get_client_version(app,client_version)
        self.client_activation_date = client_activation_date
        self.client_connected_nodes = client_connected_nodes
    @staticmethod
    def get_client_version(app,sversion):
        path=""
        if not app:
            path = get_original_executable_path() 
        else:
            path =app.config["exepath"] 
        try:
            import win32api
            info = win32api.GetFileVersionInfo(path, "\\")
            version = f"{info['FileVersionMS'] >> 16}.{info['FileVersionMS'] & 0xffff}.{info['FileVersionLS'] >> 16}.{info['FileVersionLS'] & 0xffff}"
            return version
        except:
            return sversion

    def get_local_ip(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 135))
        ip = s.getsockname()[0]
        s.close()
        system_info = platform.uname()
        local_ip = ip         
        return ip

    def _get_os_info(self):
        self.data['os'] = {
            'name': platform.system(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'type': platform.system()
        }

    def _get_processor_info(self):
        self.data['processor'] = {
            'name': platform.processor(),
            'count': psutil.cpu_count(logical=True),
            'physical': psutil.cpu_count(logical=False),
            'usage': psutil.cpu_percent(interval=None)
        }

    def _get_processor_info_new(self):
        from cpuinfo import get_cpu_info
        j= get_cpu_info()
        self.data['processor'] = {
            'name':  f"{j.get('vendor_id_raw', platform.processor())} {j.get('brand_raw', '')}" ,
            'count': psutil.cpu_count(logical=True),
            'physical': psutil.cpu_count(logical=False),
            'usage': psutil.cpu_percent(interval=None)
        }

    def _get_gpu_info(self):
        try:
            gpu_info = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader']).decode('utf-8').strip()
            self.data['gpu'] = {'name': gpu_info}
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.data['gpu'] = {'name': 'Not Detected'}

    def _get_memory_info(self):
        mem = psutil.virtual_memory()
        self.data['memory'] = {
            'total': f"{mem.total / (1024 ** 3):.2f} GB",
            'available': f"{mem.available / (1024 ** 3):.2f} GB",
            'used': f"{mem.used / (1024 ** 3):.2f} GB",
            'percentage': mem.percent
        }

    def _get_disk_info(self):
        disks = psutil.disk_partitions()
        disk_data = []
        for disk in disks:
            try:
                usage = psutil.disk_usage(disk.mountpoint)
                disk_data.append({
                    'device': disk.device,
                    'mountpoint': disk.mountpoint,
                    'type': disk.fstype,
                    'total': f"{usage.total / (1024 ** 3):.2f} GB",
                    'used': f"{usage.used / (1024 ** 3):.2f} GB",
                    'free': f"{usage.free / (1024 ** 3):.2f} GB",
                    'percent': usage.percent
                })
            except (PermissionError, FileNotFoundError):
                pass
        self.data['disk'] = disk_data

    def _get_network_info(self):
        net_io = psutil.net_io_counters()
        self.data['network'] = {
            'sent': f"{net_io.bytes_sent / (1024 ** 2):.2f} MB",
            'received': f"{net_io.bytes_recv / (1024 ** 2):.2f} MB"
        }

    def _get_system_info(self):
        import pythoncom
        pythoncom.CoInitialize ()
        from wmi import WMI
        c = WMI()
        system_info = c.Win32_ComputerSystem()[0]
        self.data['system'] = {
            'name': system_info.Name,
            'manufacturer': system_info.Manufacturer,
            'model': system_info.Model,
            #'serial_number': system_info.SerialNumber,  # May require administrator privileges
            #'type': 'workstation'  # Adjust based on your logic
        }
    
    def _get_ip_addresses(self):
        ip_addresses = []
        mac_addresses = []
        gotten_ip=self.get_local_ip()
        import netifaces
        for interface in netifaces.interfaces():
            try:
                if_data = netifaces.ifaddresses(interface)
                # if netifaces.AF_INET in if_data:
                #     ip_addresses.append(if_data[netifaces.AF_INET][0]['addr'])
                # if netifaces.AF_LINK in if_data:
                #     mac_addresses.append(if_data[netifaces.AF_LINK][0]['addr'])
                if netifaces.AF_INET in if_data and netifaces.AF_LINK in if_data:
                    if if_data[netifaces.AF_INET][0].get('addr','')==gotten_ip:
                    #if if_data[netifaces.AF_LINK][0].get('addr','')!="":
                        ip_addresses.append(if_data[netifaces.AF_INET][0]['addr'])
                        mac_addresses.append(if_data[netifaces.AF_LINK][0]['addr'])
                        break
            except Exception as e:
                print(f"Error getting IP address for interface {interface}: {e}")

        self.data['ip_addresses'] =  ", ".join(ip_addresses)
        self.data['mac_addresses'] = ", ".join(mac_addresses)


    def generate_report(self):
        self._get_os_info()
        self._get_processor_info()
        self._get_gpu_info()
        self._get_memory_info()
        self._get_disk_info()
        self._get_network_info()
        self._get_system_info()
        self.data['computer_id'] = self.computer_id
        self.data['client_version'] = self.client_version
        self.data['client_activation_date'] = self.client_activation_date 
        self.data['client_connected_nodes'] = self.client_connected_nodes 
        self._get_ip_addresses()

    def get_report_data(self):
        self.generate_report()
        return self.data

# if __name__ == "__main__":
#     report_generator = SystemReportGenerator()
#     report_generator.generate_report()
#     #report_generator.save_as_json()
#     #report_generator.save_as_pdf()
#     #report_generator.save_as_excel()
#     #report_generator.show_data()
#     print(json.dumps( report_generator.get_report_data(),indent=10))

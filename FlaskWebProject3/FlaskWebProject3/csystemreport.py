import json
import os
import platform
import psutil
import subprocess
from fpdf import FPDF
import xlsxwriter
import uuid
import wmi 

class ServerSystemReportGenerator:
    def __init__(self,app,computer_id="_computer_"
                 ,server_version="_unknown_"
                 ,server_activation_date="_unknown_"
                 ,server_connected_nodes="_unknown_"):
        self.data = {}
        self.app=app
        self.computer_id = computer_id
        self.server_version = server_version
        self.server_activation_date = server_activation_date
        self.server_connected_nodes = server_connected_nodes

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
            'usage': psutil.cpu_percent(interval=1)
        }

    def _get_processor_info_new(self):
        from cpuinfo import get_cpu_info
        j= get_cpu_info()
        self.data['processor'] = {
            'name':  f"{j.get('vendor_id_raw', platform.processor())} {j.get('brand_raw', '')}" ,
            'count': psutil.cpu_count(logical=True),
            'physical': psutil.cpu_count(logical=False),
            'usage': psutil.cpu_percent(interval=1)
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
                self.data['disk'] = disk_data
            except (OSError,PermissionError, FileNotFoundError):
                continue

    def _get_network_info(self):
        net_io = psutil.net_io_counters()
        self.data['network'] = {
            'sent': f"{net_io.bytes_sent / (1024 ** 2):.2f} MB",
            'received': f"{net_io.bytes_recv / (1024 ** 2):.2f} MB"
        }

    def _get_system_info(self):
        from wmi import WMI
        import pythoncom
        pythoncom.CoInitialize ()
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
        self.data['server_version'] = self.server_version
        self.data['server_activation_date'] = self.server_activation_date 
        self.data['server_connected_nodes'] = self.server_connected_nodes 
        self._get_ip_addresses()

    def get_report_data(self):
        self.generate_report()
        return self.data

if __name__ == "__main__":
    report_generator = ServerSystemReportGenerator(app=None)
    report_generator.generate_report()
    #report_generator.save_as_json()
    #report_generator.save_as_pdf()
    #report_generator.save_as_excel()
    #report_generator.show_data()
    print(json.dumps( report_generator.get_report_data(),indent=10))

import json
import os
import platform
import psutil
import subprocess
from fpdf import FPDF
import xlsxwriter
import uuid
import wmi 
class SystemReportGenerator:
    def __init__(self,computer_id="_computer_"
                 ,server_version="_unknown_"
                 ,server_activation_date="_unknown_"):
        self.data = {}
        self.computer_id = computer_id
        self.server_version = server_version
        self.server_activation_date = server_activation_date

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
        import netifaces
        for interface in netifaces.interfaces():
            try:
                if_data = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in if_data:
                    ip_addresses.append(if_data[netifaces.AF_INET][0]['addr'])
            except Exception as e:
                print(f"Error getting IP address for interface {interface}: {e}")

        self.data['ip_addresses'] = ip_addresses

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
        self._get_ip_addresses()

    def get_report_data(self):
        self.generate_report()
        return self.data

if __name__ == "__main__":
    report_generator = SystemReportGenerator()
    report_generator.generate_report()
    #report_generator.save_as_json()
    #report_generator.save_as_pdf()
    #report_generator.save_as_excel()
    #report_generator.show_data()
    print(json.dumps( report_generator.get_report_data(),indent=10))

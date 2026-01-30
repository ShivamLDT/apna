import socket
import time
import threading
from zeroconf import Zeroconf, ServiceInfo

# class IPBrdBrw:
#     def __init(self,)

class IpBrd:
    def __init__(
        self,
        service_name,
        service_type="_http._tcp.local.",
        port=7777,
        check_interval=10,
    ):
        self.service_name = service_name
        self.service_type = service_type
        self.port = port
        self.check_interval = check_interval
        self.current_ip = self.get_current_ip()
        self.zeroconf = Zeroconf()
        self.service_info = self.create_service_info(self.current_ip)
        self.register_service()
        # self.monitor_thread = threading.Thread(target=self.monitor_ip_change)
        # self.monitor_thread.daemon = True

    def get_current_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 7777))
            ip_address = s.getsockname()[0]
            #hostname = socket.gethostname()
            s.close()

            return ip_address
        except socket.gaierror as e:
            print(f"Error getting IP address: {e}")
            return None

    def create_service_info(self, ip_address):
        desc = {"version": "1.0"}
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", self.port))
        #ip = s.getsockname()[0]
        # ip = socket.gethostbyname(socket.gethostname())
        hostname = socket.gethostname()
        s.close()
        info = ServiceInfo(
            "_http._tcp.local.",
            self.service_name +"._http._tcp.local.",
            port=self.port,
            addresses=[socket.inet_aton(ip_address)],
            priority=0,
            weight=0,
            properties=desc,
            server=hostname,
        )
        return info

    def register_service(self):
        #print(f"Registering service with IP: {self.current_ip}")
        self.zeroconf.register_service(self.service_info)
        print(f"Registering service with IP: {self.current_ip}")

    def update_service(self, new_ip):
        self.zeroconf.unregister_service(self.service_info)
        self.service_info = self.create_service_info(new_ip)
        self.register_service()

    def monitor_ip_change(self):
        while True:
            new_ip = self.get_current_ip()
            if new_ip != self.current_ip:
                print(f"IP Address changed from {self.current_ip} to {new_ip}")
                self.update_service(new_ip)
                self.current_ip = new_ip
            time.sleep(self.check_interval)

    # def start_monitoring(self):
    #     self.monitor_thread.start()

    def close(self):
        self.zeroconf.unregister_service(self.service_info)
        self.zeroconf.close()


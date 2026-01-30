# from zeroconf import Zeroconf, ServiceInfo
# import socket
# import time
# import threading

# import zeroconf

# class IPBrd:

#     def __init__(
#         self,
#         service_name,
#         service_property={"version": "1.0"},
#         service_type="_http._tcp.local.",
#         port=7777,
#         check_interval=10,
#     ):
#         self.service_name = service_name
#         self.service_type = service_type
#         self.service_property = service_property
#         self.service_property["server"]="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD"
#         self.port = port
#         self.check_interval = check_interval
#         self.ip_monitor = IPBrdxx(
#             service_name=self.service_name,
#             service_type="_abs._tcp.local.",
#             service_property= self.service_property,
#             port=int(self.port),
#             check_interval= self.check_interval,
#         )
#         #self.ip_monitor.start_monitoring()
#         self.ip_monitor.monitor_ip_change()
        
#     #def ip_monitor.start_monitoring(self):


# class IPBrdxx:
#     def __init__(
#         self,
#         service_name,
#         service_property={"version": "1.0"},
#         service_type="_http._tcp.local.",
#         port=53335,
#         check_interval=10,
#     ):
#         self.service_name = service_name
#         self.service_type = service_type
#         self.service_property = service_property
#         if self.service_property.get("server",None)== None:
#             self.service_property["server"]="E8B8C8F3-DC90-4CD9-A6A2-D7DDC31EAABD"
#         self.port = port
#         self.check_interval = check_interval
#         self.current_ip = self.get_current_ip()
#         self.zeroconf = Zeroconf()
#         self.service_info = self.create_service_info(self.current_ip)
#         self.register_service()
#         self.monitor_thread = threading.Thread(target=self.monitor_ip_change)
#         self.monitor_thread.daemon = True
        

#     def get_current_ip(self):
#         try:
#             s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             s.connect(("8.8.8.8", 7777))
#             ip_address = s.getsockname()[0]
#             hostname = socket.gethostname()
#             s.close()

#             return ip_address
#         except socket.gaierror as e:
#             print(f"Error getting IP address: {e}")
#             return None

#     def create_service_info(self, ip_address):
#         desc = self.service_property
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", self.port))
#         ip = s.getsockname()[0]
#         # ip = socket.gethostbyname(socket.gethostname())
#         hostname = socket.gethostname()
#         s.close()
#         info = ServiceInfo(
#             "_http._tcp.local.",
#             self.service_name +"._http._tcp.local.",
#             port=self.port,
#             addresses=[socket.inet_aton(ip_address)],
#             priority=0,
#             weight=0,
#             properties=desc,
#             server=hostname,
#         )
#         return info

#     def register_service(self):
#         #print(f"Registering service with IP: {self.current_ip}")
#         try:
#             self.zeroconf.register_service(self.service_info)
#             print(f"Registering service with IP: {self.current_ip}")
#         except Exception as ew:
#             print (str(ew))

#     def update_service(self, new_ip):
#         self.zeroconf.unregister_service(self.service_info)
#         self.service_info = self.create_service_info(new_ip)
#         self.register_service()
#         self.zeroconf.async_notify_all

#     def monitor_ip_change(self):
#         while True:
#             try:
#                 from runserver import check_license_runserver #, brdcst
#                 check_license_runserver(None)
#             except:
#                 print("")
#             try:
#                 new_ip = self.get_current_ip()
#                 if new_ip != self.current_ip:
#                     print(f"IP Address changed from {self.current_ip} to {new_ip}")
#                     self.update_service(new_ip)
#                     self.current_ip = new_ip
#                 else:
#                     self.update_service(new_ip)
#                 time.sleep(self.check_interval)
#             except:
#                 print ("DDDD")

#     def start_monitoring(self):
#         self.monitor_thread.start()

#     def close(self):
#         self.zeroconf.unregister_service(self.service_info)
#         self.zeroconf.close()


# # Example usage:
# # if __name__ == "__main__":
# #     ip_monitor = IPBrd(service_name="_leda", port=int(7777), check_interval=5)
# #     ip_monitor.start_monitoring()

# #      
# #     try:
# #         while True:
# #             # Simulating other application tasks
# #             print("press any key to stop " + ip_monitor.current_ip)
# #             time.sleep(5)  
# #     except KeyboardInterrupt:
# #         ip_monitor.close()
# #         print("Service unregistered and zeroconf closed.")

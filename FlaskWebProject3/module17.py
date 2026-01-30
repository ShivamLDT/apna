# import uuid
# from scapy.all import ARP, Ether, srp

# class NetworkScan:
#     def __init__(self, target_ip):
#         self.target_ip = target_ip

#     def scan(self):
#         # Create ARP request
#         arp = ARP(pdst=self.target_ip)
#         ether = Ether(dst="ff:ff:ff:ff:ff:ff")
#         packet = ether / arp

#         # Send packet and get response
#         result = srp(packet, timeout=3, verbose=0)[0]

#         # Process result
#         devices = []
#         for sent, received in result:
#             devices.append({'ip': received.psrc, 'mac': received.hwsrc})

#         return devices

#     def display_results(self, devices):
#         print("Available devices in the network:")
#         print("IP" + " "*18+"MAC")
#         for device in devices:
#             print("{:16}    {}".format(device['ip'], device['mac']))



# #============================

# import netifaces as ni

# def get_mac_address(interface=''):
#     """
#     Gets the MAC address of the specified network interface.

#     Args:
#         interface (str, optional): Name of the network interface (e.g., 'eth0', 'wlan0'). 
#                                     If empty, attempts to find the first available interface.

#     Returns:
#         str: The MAC address in the format "XX:XX:XX:XX:XX:XX" or None if not found.
#     """
#     try:
#         if not interface:
#             interfaces = ni.interfaces()
#             if interfaces:
#                 interface = interfaces[0]  # Use the first available interface
#             else:
#                 return None

#         if_info = ni.ifaddresses(interface)[ni.AF_LINK]
#         return if_info[0]['addr']
#     except (KeyError, IndexError, ValueError):
#         return None

# if __name__ == "__main__":
#     mac_address = get_mac_address() 
#     if mac_address:
#         print("MAC Address:", mac_address)
#     else:
#         print("Could not find MAC address.")

# #if __name__ == "__main__":
#     import uuid
    
#     mac = uuid.getnode()
#     mac  =':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])

#     # Replace '192.168.1.1/24' with your network IP range
#     target_ip = "192.168.2.1/24"
#     network_scan = NetworkScan(target_ip)
#     devices = network_scan.scan()
#     network_scan.display_results(devices)


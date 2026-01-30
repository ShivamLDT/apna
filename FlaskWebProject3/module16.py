# import subprocess
# import json
# import threading
# from socket import *
# import platform

# results = []
# lock = threading.Lock()

# def get_local_network():
#     # Execute arp -a command to get the list of devices
#     output = subprocess.check_output("arp -a", shell=False).decode()

#     # Extract IP addresses
#     ip_addresses = []
#     for line in output.split('\n'):
#         if '-' in line and '.' in line:
#             parts = line.split()
#             ip = parts[0]
#             if ip.count('.') == 3:  # Simple check to ensure it's an IP address
#                 ip_addresses.append(ip)
#     return ip_addresses

# def is_up(addr):
#     return True
#     s = socket(AF_INET, SOCK_STREAM)
#     s.settimeout(0.01)  # set a timeout of 0.01 sec
#     if not s.connect_ex((addr, 135)):  # connect to the remote host on port 135
#         s.close()  # (port 135 is always open on Windows machines, AFAIK)
#         return True
#     else:
#         s.close()
#         return False

# def scan_ip(ip):
#     global results
#     if is_up(ip):
#         hostname = 'Unknown'
#         try:
#             # Retrieve hostname using gethostbyaddr
#             hostname, _, _ = gethostbyaddr(ip)
#         except:
#             pass

#         # Gather local machine details
#         os_info = platform.system()
#         os_version = platform.version()
#         os_details = f"{os_info} {os_version}"

#         with lock:
#             results.append({'ip': ip, 'hostname': hostname, 'os': os_details})

# def run():
#     global results
#     ip_addresses = get_local_network()
#     threads = []

#     for ip in ip_addresses:
#         thread = threading.Thread(target=scan_ip, args=(ip,))
#         threads.append(thread)
#         thread.start()

#     # Wait for all threads to complete
#     for thread in threads:
#         thread.join()

#     return results

# # if __name__ == '__main__':
# #     print("Scanning the local network for connected devices. This might take some time, depending on the number of the devices found. Please wait...")
# #     data = run()
# #     json_data = json.dumps(data, indent=4)  # Serialize to JSON with indentation for readability
# #     print(json_data)

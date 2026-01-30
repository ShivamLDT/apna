from socket import gethostname,gethostbyname
import socket
import json
import threading
import platform
import subprocess
results = []
lock = threading.Lock()
def get_local_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 135))
    ip = s.getsockname()[0]
    s.close()
    hostname = gethostname()
    system_info = platform.uname()
    local_ip = ip #gethostbyname(hostname)
    network = '.'.join(local_ip.split('.')[:-1]) + '.'
    return network


def is_up(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.01)    ## set a timeout of 0.01 sec
    if not s.connect_ex((addr, 135)):    # connect to the remote host on port 135
        s.close()                       ## (port 135 is always open on Windows machines, AFAIK)
        return True
    else:
        return False

def scan_range(start, end):
    global results
    for ip in range(start, end):
        addr = network + str(ip)
        if is_up(addr):
            hostname = socket.getfqdn(addr)
            with lock:
                results.append({'ip': addr, 'hostname': hostname})

def run():
    global results
    global network
    network = get_local_network()
    threads = []
    thread_count = 10  # Number of threads to use

    # Divide IP range into chunks for each thread
    chunk_size = 256 // thread_count
    for i in range(thread_count):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        #scan_range(start, end)
        thread = threading.Thread(target=scan_range, args=(start, end))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return results

# if __name__ == '__main__':
#     print("Scanning the local network for connected Windows machines (and others with samba server running). Also, I'll try to resolve the hostnames. This might take some time, depending on the number of the PCs found. Please wait...")
#     data = run()
#     json_data = json.dumps(data, indent=4)  # Serialize to JSON with indentation for readability
#     print(json_data)

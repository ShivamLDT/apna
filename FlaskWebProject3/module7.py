import argparse
from io import BytesIO
import io
import time
from smb.SMBConnection import SMBConnection
import   netifaces
import ipaddress

def list_files_on_smb(server_ip, share_name, username, password, folder_path):
    print("Establish the SMB connection")
    conn = SMBConnection(username, password,"",server_ip, use_ntlm_v2=True,is_direct_tcp=True)
    #assert conn.connect(server_ip, 139), "Could not connect to the server"
    #assert conn.connect(server_ip, 445), "Could not connect to the server"
    conn.connect(server_ip,445)
    
    ##############
    file_path="C:\\74\\ttttCopy.txt"
    file_path=r"C:\7676744444\asdf - Copy.txt"
    
    file_path=f'test_{str(time.time()).replace(".","_")}.txt'
    # with open(file_path, "rb") as file_obj:
    #      conn.storeFile(share_name, "file_pathz", file_obj)
    # file_obj.close()
    b=io.BytesIO(f"This is file {file_path} at {time.asctime()}".encode())
    conn.storeFile(share_name, file_path, b)
    
    with open(file_path, "wb") as file_obxwj:
         conn.retrieveFile(share_name, file_path, file_obxwj)
    file_obxwj.close()
    ###########

    filtered_shares = [share for share in conn.listShares() if share.isSpecial==False and share.isTemporary==False ]
    
    # List files in the specified folder
    
    file_list = conn.listPath(share_name, folder_path)

    conn.close()
    return [file.filename for file in file_list]# if file.isDirectory == False]

def get_network_range():
    # Get the default network interface (usually 'eth0' or 'wlan0' for Linux, 'en0' for macOS)
    interfaces = netifaces.interfaces()
    network_range= None
    for interface in interfaces:
        try:
            # Get the address info for each interface
            addrs = netifaces.ifaddresses(interface)
            ipv4_info = addrs.get(netifaces.AF_INET)
            if ipv4_info:
                if not network_range:
                    network_range = []

                local_ip = ipv4_info[0]['addr']
                netmask = ipv4_info[0]['netmask']
                print(f"Local IP: {local_ip}, Subnet Mask: {netmask}")

                # Calculate the network range
                network = ipaddress.IPv4Network(f"{local_ip}/{netmask}", strict=False)
                network_range.append( 
                    {
                        "local_ip":local_ip, 
                        "subnet_mask":netmask,
                        "network_address":network.network_address,
                        "network_prefixlen":network.prefixlen,
                    }
                )
                #network_range = str(network.network_address) + "/" + str(network.prefixlen
                print(f"Network Range: {network_range}")
                #return network_range
        except KeyError:
            continue
    #return None
    return network_range

# Get the network range of the local machine
network_range = get_network_range()
if network_range:
    for net_work in network_range:
        print("\n=========================================================\n")
        #print(f"network_range: {net_work}")
        print(f'local_ip: {net_work.get("local_ip","------")}')
        print(f'subnet_mask : {net_work.get("subnet_mask","------")}')
        print(f'network_address: {net_work.get("network_address","------")}')
        print(f'network_prefixlen: {net_work.get("network_prefixlen","------")}') 
else:
    print("Unable to identify the network range.")
# Usage
server_ip = '192.168.2.186'
share_name = 'ApnaBackup'
username = 'Danish'
password = 'Server@1234'
folder_path = 'Test_Data_Backup'#'01.06.24.7.00'

server_ip = '192.168.2.186'
share_name = 'ApnaBackup'
username = 'Danish'
password = 'Server@1234'
folder_path = 'Test_Data_Backup'

server_ip = '192.168.2.15'
share_name = 'kuldeep'
username = 'admin'
password = 'Server123'
folder_path = ''#'01.06.24.7.00'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMB BytesIO CLI Tool")
    #parser.add_argument("mode", choices=["upload", "download"])
    parser.add_argument("--server", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--share", required=True)
    #parser.add_argument("--file", required=True)

    args = parser.parse_args()
    server_ip = args.server
    share_name = args.share
    username = args.username
    password = args.password 
    print (args)
    files = list_files_on_smb(server_ip, share_name, username, password, folder_path)
    print("Files available for download:")
    for file in files:
        print(file)


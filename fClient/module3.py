import ctypes
from ctypes import c_ulong, c_bool, c_char, c_byte, POINTER, Structure, c_ulonglong

# Load necessary libraries
iphlpapi = ctypes.windll.iphlpapi
kernel32 = ctypes.windll.kernel32

# Define constants
ERROR_BUFFER_OVERFLOW = 111  # Buffer size insufficient error

# Define structures
class IP_ADDR_STRING(Structure):
    _fields_ = [
        ('Next', POINTER('IP_ADDR_STRING')),
        ('IpAddress', c_char * 16)
    ]

class IP_ADAPTER_UNICAST_ADDRESS(Structure):
    _fields_ = [
        ('Address', c_byte * 16),  # Assumed to be 16 bytes for MAC address
        ('Length', c_ulong),
        ('Next', POINTER('IP_ADAPTER_UNICAST_ADDRESS'))
    ]

class IP_ADAPTER_MULTICAST_ADDRESS(Structure):
    _fields_ = [
        ('Address', c_byte * 16),  # Assumed to be 16 bytes for multicast address
        ('Length', c_ulong),
        ('Next', POINTER('IP_ADAPTER_MULTICAST_ADDRESS'))
    ]

class IP_ADAPTER_INFO(Structure):
    _fields_ = [
        ('Next', POINTER('IP_ADAPTER_INFO')),  # Corrected: Use POINTER(IP_ADAPTER_INFO)
        ('ComboIndex', c_ulong),
        ('AdapterName', c_char * 256),
        ('Description', c_char * 256),
        ('AddressLength', c_ulong),
        ('Address', c_byte * 8),
        ('Index', c_ulong),
        ('Type', c_ulong),
        ('DhcpEnabled', c_bool),
        ('CurrentIpAddress', c_char * 16),
        ('IpAddressList', POINTER(IP_ADDR_STRING)),
        ('GatewayList', POINTER(IP_ADDR_STRING)),
        ('IpMaskList', POINTER(IP_ADDR_STRING)),
        ('DnsServerList', POINTER(IP_ADDR_STRING)),
        ('HaveWindowsNTStatus', c_bool),
        ('Mtu', c_ulong),
        ('Metric', c_ulong),
        ('Ieee1394Guid', c_ulonglong),
        ('NumberOfLinks', c_ulong),
        ('LinkSpeed', c_ulong),
        ('TransmitLinkSpeed', c_ulong),
        ('ReceiveLinkSpeed', c_ulong),
        ('LinkSpeedUnits', c_ulong),
        ('MaxFrameSize', c_ulong),
        ('Transmits', c_ulong),
        ('Receives', c_ulong),
        ('OutOctets', c_ulonglong),
        ('InOctets', c_ulonglong),
        ('OutUcastPkts', c_ulong),
        ('InUcastPkts', c_ulong),
        ('OutNUcastPkts', c_ulong),
        ('InNUcastPkts', c_ulong),
        ('OutDiscards', c_ulong),
        ('InDiscards', c_ulong),
        ('OutErrors', c_ulong),
        ('InErrors', c_ulong),
        ('OutUnknownProtos', c_ulong),
        ('InUnknownProtos', c_ulong),
        ('IpAddressListLength', c_ulong),
        ('GatewayListLength', c_ulong),
        ('IpMaskListLength', c_ulong),
        ('DnsServerListLength', c_ulong),
        ('UnicastAddresses', POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
        ('MulticastAddresses', POINTER(IP_ADAPTER_MULTICAST_ADDRESS))
    ]

def get_mac_addresses():
    """
    Retrieves MAC addresses of network interfaces on the current system.

    Returns:
        A list of MAC addresses as strings.
    """

    mac_addresses = []
    adapter_info = IP_ADAPTER_INFO()
    adapter_info_size = c_ulong(0)  # Initially set buffer size to 0

    # First call to get the required buffer size
    result = iphlpapi.GetAdaptersInfo(ctypes.byref(adapter_info), ctypes.byref(adapter_info_size))
    
    # Check if buffer size is insufficient
    if result == ERROR_BUFFER_OVERFLOW:
        # Allocate a buffer of the required size
        buffer = ctypes.create_string_buffer(adapter_info_size.value)
        adapter_info = ctypes.cast(buffer, POINTER(IP_ADAPTER_INFO))

        # Second call to retrieve the adapter information
        result = iphlpapi.GetAdaptersInfo(adapter_info, ctypes.byref(adapter_info_size))
    
    # Check if the function succeeded
    if result != 0:
        print(f"Error: GetAdaptersInfo failed with code {result}")
        return mac_addresses

    # Traverse the adapter list
    current_adapter = adapter_info.contents
    while current_adapter:
        mac_address = ":".join("{:02x}".format(x) for x in current_adapter.Address[:current_adapter.AddressLength])
        mac_addresses.append(mac_address)
        # Ensure the next adapter is valid before accessing it
        if current_adapter.Next:
            current_adapter = current_adapter.Next.contents
        else:
            break  # Exit if no more adapters

    return mac_addresses

if __name__ == "__main__":
    try:
        mac_addresses = get_mac_addresses()
        if mac_addresses:
            print("MAC Addresses:")
            for mac in mac_addresses:
                print(f"  {mac}")
        else:
            print("No MAC addresses found.")
    except Exception as ddsf:
        print(str(ddsf))

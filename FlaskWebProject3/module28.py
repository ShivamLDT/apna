import socket
import struct

def encode_oid(oid):
    """Encodes an OID into SNMP BER format"""
    oid_parts = [int(i) for i in oid.split(".")]
    oid_encoded = bytes([40 * oid_parts[0] + oid_parts[1]])  # First two OID parts

    for sub_id in oid_parts[2:]:
        if sub_id < 128:
            oid_encoded += struct.pack("B", sub_id)
        else:
            # Encode large numbers using multiple bytes
            encoded = []
            while sub_id:
                encoded.insert(0, (sub_id & 0x7F) | 0x80)  # Set MSB for all but last byte
                sub_id >>= 7
            encoded[-1] &= 0x7F  # Clear MSB for last byte
            oid_encoded += bytes(encoded)
    
    return oid_encoded

def build_snmp_get(community, oid, request_id=1):
    """Builds an SNMP GET request packet"""
    version = b"\x00"  # SNMP v1 (use b"\x01" for v2c)
    community_bytes = community.encode("utf-8")
    community_len = len(community_bytes)

    oid_encoded = encode_oid(oid)
    oid_len = len(oid_encoded)

    # SNMP GET PDU (Tag: 0xA0)
    pdu = (
        b"\xA0"  # PDU Type: GET
        + struct.pack("B", 18 + oid_len)  # PDU Length
        + b"\x02\x04" + struct.pack(">I", request_id)  # Request ID
        + b"\x02\x01\x00"  # Error Status
        + b"\x02\x01\x00"  # Error Index
        + b"\x30" + struct.pack("B", 6 + oid_len)  # VarBind List Length
        + b"\x30" + struct.pack("B", 4 + oid_len)  # VarBind Length
        + b"\x06" + struct.pack("B", oid_len) + oid_encoded  # OID
        + b"\x05\x00"  # NULL value
    )

    # Full SNMP packet
    snmp_packet = (
        b"\x30" + struct.pack("B", 13 + community_len + len(pdu))  # Message Length
        + version  # SNMP version
        + b"\x04" + struct.pack("B", community_len) + community_bytes  # Community
        + pdu  # PDU
    )

    return snmp_packet

def send_snmp_request(ip, community, oid):
    """Sends an SNMP GET request and receives a response"""
    port = 161  # SNMP UDP Port
    request_id = 1  # Unique request ID (change if needed)

    # Build SNMP GET request packet
    snmp_packet = build_snmp_get(community, oid, request_id)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)  # Set timeout for response

    try:
        # Send SNMP request
        sock.sendto(snmp_packet, (ip, port))
        response, _ = sock.recvfrom(1024)  # Receive response (max 1024 bytes)
        return parse_snmp_response(response)
    except socket.timeout:
        return "SNMP request timed out"
    except Exception as e:
        return f"Error: {e}"
    finally:
        sock.close()

def parse_snmp_response(response):
    """Parses SNMP response and extracts the returned value"""
    try:
        response_data = response[response.index(b"\x05\x00") + 2:]  # Find the value
        if response_data[0] == 2:  # Integer type
            value = int.from_bytes(response_data[2:], byteorder="big")
            return f"Integer: {value}"
        elif response_data[0] == 4:  # Octet String
            return f"String: {response_data[2:].decode('utf-8', errors='ignore')}"
        else:
            return f"Unknown type: {response_data.hex()}"
    except Exception as e:
        return f"Error parsing response: {e}"

# Example Usage
host = "192.168.2.1"  # Change to your SNMP-enabled device IP
oid = "1.3.6.1.2.1.1.5.0"  # OID for sysName (hostname)
community = "public"  # SNMP Community string

result = send_snmp_request(host, community, oid)
print("SNMP Response:", result)

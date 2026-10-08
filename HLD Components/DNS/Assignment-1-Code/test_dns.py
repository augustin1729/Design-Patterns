import socket
import struct

def build_query(domain):
    # Transaction ID: 0x1234
    # Flags: 0x0100 (Standard query)
    # Questions: 1
    # Answer RRs: 0, Authority RRs: 0, Additional RRs: 0
    header = struct.pack("!6H", 0x1234, 0x0100, 1, 0, 0, 0)
    
    # QNAME
    qname = b""
    for part in domain.split("."):
        qname += bytes([len(part)]) + part.encode("utf-8")
    qname += b"\x00"
    
    # QTYPE: 1 (A), QCLASS: 1 (IN)
    question = struct.pack("!HH", 1, 1)
    
    return header + qname + question

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)
server_address = ("127.0.0.1", 6122)

query = build_query("google.com")
print(f"Sending query for google.com to {server_address}...")
sock.sendto(query, server_address)

try:
    data, _ = sock.recvfrom(512)
    print(f"Received {len(data)} bytes in response!")
except socket.timeout:
    print("Timeout! No response received.")

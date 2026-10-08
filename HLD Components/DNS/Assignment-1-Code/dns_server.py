import socket
import struct
import time
from dataclasses import dataclass
from typing import Tuple, Dict

# --- Data Structures ---
# Using Dataclasses here is a great OOP practice because it clearly defines
# the shape of the data we're working with across the application.

@dataclass
class DNSHeader:
    transaction_id: int
    flags: int
    qdcount: int
    ancount: int
    nscount: int
    arcount: int

@dataclass
class DNSQuestion:
    qname: str
    qtype: int
    qclass: int
    raw_bytes: bytes  # Keeping the raw bytes makes building cached responses easier

@dataclass
class CachedRecord:
    ip: str
    ttl: int
    expiry_time: float
    raw_rdata: bytes


# --- Parsers ---
# A helper class strictly responsible for converting binary data into our objects
class DNSPacketParser:
    @staticmethod
    def parse_header(data: bytes) -> DNSHeader:
        unpacked = struct.unpack("!6H", data[:12])
        return DNSHeader(*unpacked)

    @staticmethod
    def parse_question(data: bytes, offset: int = 12) -> Tuple[DNSQuestion, int]:
        """ Parses a standard DNS Question section. """
        qname_parts = []
        start_offset = offset
        
        while True:
            length = data[offset]
            if length == 0:
                offset += 1
                break
            
            # This handles standard length-prefixed strings (e.g., \x06google\x03com\x00)
            offset += 1
            qname_parts.append(data[offset:offset+length].decode('utf-8'))
            offset += length
        
        qname = ".".join(qname_parts)
        qtype, qclass = struct.unpack("!HH", data[offset:offset+4])
        raw_bytes = data[start_offset:offset+4]
        
        return DNSQuestion(qname, qtype, qclass, raw_bytes), offset + 4


# --- Core Components ---
# We split the Cache out into its own class to separate memory management 
# from the networking logic.
class DNSCache:
    def __init__(self):
        # Key: (domain_name, record_type) -> Value: CachedRecord
        self._cache: Dict[Tuple[str, int], CachedRecord] = {}

    def get(self, domain: str, qtype: int) -> CachedRecord:
        key = (domain, qtype)
        if key in self._cache:
            record = self._cache[key]
            # Check if TTL expired
            if time.time() < record.expiry_time:
                return record
            else:
                del self._cache[key] 
        return None

    def put(self, domain: str, qtype: int, ip: str, ttl: int, raw_rdata: bytes):
        key = (domain, qtype)
        expiry_time = time.time() + ttl
        self._cache[key] = CachedRecord(ip, ttl, expiry_time, raw_rdata)


class DNSServer:
    def __init__(self, port=6122, upstream_ip="8.8.8.8", upstream_port=53):
        self.port = port
        self.upstream = (upstream_ip, upstream_port)
        
        # Socket for listening to clients (dig)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Socket for forwarding to upstream (8.8.8.8)
        self.forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.forward_socket.settimeout(2.0)
        
        self.cache = DNSCache()

    def start(self):
        self.server_socket.bind(("127.0.0.1", self.port))
        print(f"[*] DNS Forwarding Server started on 127.0.0.1:{self.port}")
        
        while True:
            try:
                data, addr = self.server_socket.recvfrom(512)
                self._handle_query(data, addr)
            except Exception as e:
                print(f"[!] Error handling request: {e}")

    def _handle_query(self, data: bytes, client_addr: Tuple[str, int]):
        header = DNSPacketParser.parse_header(data)
        
        # 1. Validation: Extract bits using bitwise operations
        is_query = (header.flags & 0x8000) == 0 # QR bit
        opcode = (header.flags & 0x7800) >> 11  # Opcode bits
        
        if not is_query or opcode != 0:
            print(f"[-] Dropping non-standard query from {client_addr}")
            return
            
        if header.qdcount == 0:
            return
            
        question, _ = DNSPacketParser.parse_question(data)
        print(f"[*] Query received for {question.qname} from {client_addr}")
        
        # 2. Check Cache
        cached_record = self.cache.get(question.qname, question.qtype)
        
        if cached_record:
            print(f"[+] Cache HIT for {question.qname}")
            response = self._build_cached_response(header.transaction_id, question, cached_record)
            self.server_socket.sendto(response, client_addr)
        else:
            print(f"[-] Cache MISS for {question.qname}, forwarding upstream...")
            self._forward_and_cache(data, client_addr, header.transaction_id, question)

    def _build_cached_response(self, txid: int, question: DNSQuestion, record: CachedRecord) -> bytes:
        """Constructs a synthetic DNS response from cache."""
        # Standard response flags: QR=1, RA=1, RCODE=0 -> 0x8180
        flags = 0x8180
        header_bytes = struct.pack("!6H", txid, flags, 1, 1, 0, 0)
        
        remaining_ttl = max(0, int(record.expiry_time - time.time()))
        
        # Answer section pointer to name at offset 12 (0xC00C)
        answer_bytes = struct.pack("!HHHLH", 0xC00C, question.qtype, question.qclass, remaining_ttl, len(record.raw_rdata))
        answer_bytes += record.raw_rdata
        
        return header_bytes + question.raw_bytes + answer_bytes

    def _forward_and_cache(self, query_data: bytes, client_addr: Tuple[str, int], original_txid: int, original_question: DNSQuestion):
        """Forwards query, validates response, caches A records, and sends to client."""
        try:
            # Send upstream
            self.forward_socket.sendto(query_data, self.upstream)
            response_data, _ = self.forward_socket.recvfrom(512)
            
            # Security validation layer
            resp_header = DNSPacketParser.parse_header(response_data)
            
            # Transaction ID Match
            if resp_header.transaction_id != original_txid:
                print(f"[!] Validation failed: TXID mismatch")
                return
                
            # Check QR=1 and RCODE=0
            is_response = (resp_header.flags & 0x8000) != 0
            rcode = resp_header.flags & 0x000F
            if not is_response or rcode != 0:
                self.server_socket.sendto(response_data, client_addr)
                return
                
            # Echo check
            resp_question, offset = DNSPacketParser.parse_question(response_data)
            if resp_question.qname != original_question.qname or resp_question.qtype != original_question.qtype:
                print("[!] Validation failed: Question echo mismatch")
                return
                
            # Cache Injection (Only caching Type A records for simplicity)
            if resp_header.ancount > 0 and resp_question.qtype == 1: 
                self._extract_and_cache(response_data, offset, resp_question.qname, resp_header.ancount)
                
            # Forward the valid response back to the client
            self.server_socket.sendto(response_data, client_addr)
            
        except socket.timeout:
            print("[!] Upstream forward timeout")
            
    def _extract_and_cache(self, data: bytes, offset: int, qname: str, ancount: int):
        """Extracts the IP from the answer section and stores it in cache."""
        # Simple extraction assuming the first record is a pointer. 
        # (A fully robust parser would handle compression properly here)
        for _ in range(ancount):
            # Check if name is a pointer (starts with 11 bits)
            if (data[offset] & 0xC0) == 0xC0:
                offset += 2
            else:
                while data[offset] != 0: offset += data[offset] + 1
                offset += 1
                
            atype, aclass, attl, rdlength = struct.unpack("!HHIH", data[offset:offset+10])
            offset += 10
            rdata = data[offset:offset+rdlength]
            offset += rdlength
            
            # Type A (1), Class IN (1)
            if atype == 1 and aclass == 1: 
                ip_str = socket.inet_ntoa(rdata)
                self.cache.put(qname, 1, ip_str, attl, rdata)
                print(f"[+] Cached A record: {qname} -> {ip_str} (TTL: {attl})")
                break

if __name__ == "__main__":
    server = DNSServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down.")
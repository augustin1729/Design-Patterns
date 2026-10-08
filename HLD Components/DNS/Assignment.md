# Mini-Lab: Build a Caching DNS Forwarder & Validation Harness

### Objective

Implement a lightweight **Caching DNS Forwarder (Recursive Stub Proxy)** in Python listening locally on `127.0.0.1:5353` (or port 53 if run with elevated privileges). Your server will receive standard DNS queries from tools like `dig` or your custom query script, resolve them via an upstream recursive resolver (e.g., `8.8.8.8:53`), cache valid responses, and enforce strict sanity checks to detect and reject spoofed/mismatched packets.

---

### Core Functional Requirements

#### 1. Inbound Query Listener & Dissector

* Bind a UDP socket to `127.0.0.1:5353`.
* Read incoming packets and parse the 12-byte header using `struct.unpack`:
* Extract `Transaction ID`, `Flags`, `QDCOUNT`, `ANCOUNT`, etc.
* Validate that the message is a standard Query (`QR == 0`, `Opcode == 0`).


* Parse the Question Section to extract the queried domain name (handling length-prefixed labels like `\x06google\x03com\x00`) and the `QTYPE` (focus primarily on `A` records).

#### 2. Local In-Memory Cache with TTL Expiry

* Maintain an internal hash map/dictionary for cached answers:

$$\text{Key: } (\text{domain\_name}, \text{record\_type}) \implies \text{Value: } (\text{IP\_address}, \text{expiry\_timestamp}, \text{raw\_ttl})$$


* **Cache Hit:** If a valid, non-expired record exists:
* Construct a synthetic DNS response on the fly.
* Set `QR = 1`, `RA = 1`, `RCODE = 0`.
* Set the Transaction ID to match the client's query ID.
* Decrement or include the remaining TTL.
* Send the packet directly back to the client without querying upstream.


* **Cache Miss:** Forward the query upstream to `8.8.8.8:53`.

#### 3. Upstream Forwarding & Security Validation Layer

When proxying to the upstream resolver, your forwarder must protect itself against poisoned or rogue responses by validating packet integrity before accepting or caching them:

1. **Transaction ID Matching:** The response Transaction ID must strictly match the ID generated for the upstream query.
2. **Question Section Echo Check:** The Question section in the upstream response must identically match the domain and type originally sent.
3. **Response Bit Validation:** Ensure the `QR` bit is set to `1` (Response) and `RCODE` is `0` (NoError) before caching.
4. **Cache Injection:** If all checks pass, extract the `A` record IP and `TTL` from the Answer section and store them in the local cache. If checks fail, discard the packet as invalid/spoofed and do not pollute the cache.

---

### Verification & Testing Tasks

1. **Basic Query Verification:**
* Run your server on `127.0.0.1:5353`.
* Query it using `dig`:
```bash
dig @127.0.0.1 -p 5353 google.com A

```


* Confirm that your server logs a **Cache Miss**, queries `8.8.8.8`, and returns the correct IP.


2. **Cache Hit Verification:**
* Immediately re-run the same `dig` command.
* Confirm that your server logs a **Cache Hit**, does **not** touch the network/upstream, and returns the response with the decremented TTL.


3. **Spoofing & Poisoning Rejection Test:**
* Write a small test harness script that listens or sends an unsolicited, malicious UDP response packet to your server (e.g., claiming `google.com -> 6.6.6.6` with a mismatched Transaction ID or non-matching Question).
* Verify that your server’s validation layer detects the mismatch, drops the packet, and keeps the cache unpolluted.

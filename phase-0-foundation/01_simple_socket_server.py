import socket
import time
from urllib.parse import urlparse, parse_qs
from collections import deque

# 1. Create a socket (AF_INET = IPv4, SOCK_STREAM = TCP)
# AF_INET refers to the address family for IPv4
# SOCK_STREAM means it's a connection-oriented TCP protocol
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Bind it to an address and port
# '127.0.0.1' is localhost, 8080 is the port
server_socket.bind(('127.0.0.1', 8080))

# 3. Start listening for incoming "calls"
# The argument 1 is the backlog (number of unaccepted connections allowed)
server_socket.listen(1)
print("Server is listening on http://127.0.0.1:8080 ...")

recent = deque()

try:
    while True:
        # 4. Accept a connection
        # This blocks until a client connects
        client_conn, client_addr = server_socket.accept()
        print(f"Connected by {client_addr}")
        start_time = time.time()
        # 5. Receive the data (max 1024 bytes)
        data = client_conn.recv(1024)
        if not data:
            break
        
        request_text = data.decode('utf-8')
        print(f"Received raw data:\n{request_text}")

        # --- PATH DETECTION LOGIC ---
        # 1. Get the first line (e.g., "GET /user/ HTTP/1.1")
        first_line = request_text.split('\n')[0]
        # 2. Split by space to get [Method, Path, Protocol]
        parts = first_line.split(' ')
        if len(parts) > 1:
            requested_path = parts[1]
            print(f"🎯 DETECTED PATH: {requested_path}")
            parsed = urlparse(requested_path)
            qs = parse_qs(parsed.query)
            try:
                delay = float(qs.get("delay", ["0"])[0])
            except Exception:
                delay = 0.0
            try:
                size = int(qs.get("size", ["0"])[0])
            except Exception:
                size = 0
            if delay > 0:
                print(f"⏳ Simulating delay: {delay}s")
                time.sleep(delay)
        else:
            requested_path = "unknown"

        # 6. Send a minimal HTTP response
        # We'll include the detected path in the response!
        processing_ms = (time.time() - start_time) * 1000.0
        if 'size' in locals() and size > 0:
            body_bytes = (("X" * size)).encode('utf-8')
        else:
            body = f"Hello! You requested the path: {requested_path}\r\nData: {str({'name': 'nas'})}"
            body_bytes = body.encode('utf-8')
        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            f"X-Response-Time: {processing_ms:.2f}ms\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8')
        client_conn.sendall(headers + body_bytes)
        end_time = time.time()
        recent.append(end_time)
        while recent and (end_time - recent[0]) > 1.0:
            recent.popleft()
        print(f"📈 rt_ms={((end_time - start_time)*1000):.2f} throughput_1s={len(recent)}")
        
        # 7. Close the connection
        client_conn.close()
finally:
    server_socket.close()

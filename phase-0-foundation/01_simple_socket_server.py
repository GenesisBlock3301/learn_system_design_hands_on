import socket
import time

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

try:
    while True:
        # 4. Accept a connection
        # This blocks until a client connects
        client_conn, client_addr = server_socket.accept()
        print(f"Connected by {client_addr}")
        
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
            
            # --- SIMULATE BLOCKING ---
            # We sleep for 10 seconds to keep the connection open and block the loop
            print("⏳ Simulating a very slow request (10 seconds)...")
            time.sleep(10)
        else:
            requested_path = "unknown"

        # 6. Send a minimal HTTP response
        # We'll include the detected path in the response!
        body = f"Hello! You requested the path: {requested_path}\r\nData: {str({'name': 'nas'})}"
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{body}"
        client_conn.sendall(response.encode('utf-8'))
        
        # 7. Close the connection
        client_conn.close()
finally:
    server_socket.close()

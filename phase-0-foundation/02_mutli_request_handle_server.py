import asyncio

async def handle_client(reader, writer):
    """
    This function handles each client connection independently.
    Because it's 'async', the server can handle many of these at once!
    """
    addr = writer.get_extra_info('peername')
    print(f"[*] New connection from {addr}")

    # 1. Read the request
    # reader.read(1024) is a 'coroutine' - we 'await' it without blocking others
    data = await reader.read(1024)
    request_text = data.decode('utf-8')
    
    if request_text:
        # 2. Extract the path (same logic as before)
        first_line = request_text.split('\n')[0]
        parts = first_line.split(' ')
        requested_path = parts[1] if len(parts) > 1 else "unknown"
        print(f"🎯 DETECTED PATH: {requested_path} from {addr}")

        # 3. Simulate a "Slow Task" (e.g., Database lookup or AI processing)
        # In a sync server, this would freeze everything for 5 seconds.
        # In async, other users can still connect and get responses!
        if "/slow" in requested_path:
            print(f"⏳ Sleeping for 5 seconds for {addr}...")
            await asyncio.sleep(5)

        # 4. Prepare and send the response
        body = f"Hello from Async Server!\nYour Path: {requested_path}\nYour Address: {addr}"
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )
        
        writer.write(response.encode('utf-8'))
        await writer.drain() # Ensure all data is sent

    # 5. Close the connection
    print(f"[*] Closing connection from {addr}")
    writer.close()
    await writer.wait_closed()

async def main():
    # Start the server on port 8080
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8080)
    
    addr = server.sockets[0].getsockname()
    print(f"🚀 Async Server serving on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

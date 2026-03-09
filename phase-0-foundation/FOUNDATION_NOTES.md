# Phase 0 – Foundation: Instructor Notes

Use this file to teach the fundamentals your students will need before real “system design.” It connects hands-on code from this folder with the core theory: how clients find servers (DNS), how they talk (HTTP), and how programs communicate (sockets). It also includes guided labs to demonstrate behavior.

## Learning Outcomes
- Explain the end‑to‑end journey of a web request: Browser → DNS → Server → Response.
- Read and construct minimal HTTP/1.1 requests and responses.
- Build a TCP server with sockets and reason about blocking, backlog, and concurrency.
- Compare synchronous sockets vs asyncio for handling multiple clients.
- Use a framework (Flask) to avoid manual parsing and implement JSON APIs quickly.
- Resolve hostnames to IPs and understand why multiple IPs exist for one hostname.

## Mental Model: Request Journey
- You type a URL (e.g., https://example.com).
- DNS resolves “example.com” to one or more IPs (A/AAAA records).
- Your browser opens a TCP connection to IP:PORT (default 80 for HTTP, 443 for HTTPS).
- It sends an HTTP request; the server parses it and replies with an HTTP response.
- The browser renders the response based on headers like Content-Type.

## Sockets 101 (TCP vs UDP)
- Address family: AF_INET (IPv4), AF_INET6 (IPv6)
- Type: SOCK_STREAM (TCP, reliable, ordered), SOCK_DGRAM (UDP, connectionless, faster but no guarantees)
- Key server calls (TCP):
  - socket() → bind((host, port)) → listen(backlog) → accept() → recv()/send()/close()
- Client connects using connect((host, port)) then send()/recv().
- Backlog = number of pending connections the OS can queue while the app is busy.
- Blocking I/O: accept(), recv(), and time.sleep() stall the single thread.
- Concurrency options:
  - Threads/Processes: preemptive parallelism, more overhead.
  - Asyncio: cooperative, a single event loop multiplexes many connections efficiently.

Code references:
- Blocking server: [01_simple_socket_server.py](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/phase-0-foundation/01_simple_socket_server.py)
- Async server: [02_mutli_request_handle_server.py](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/phase-0-foundation/02_mutli_request_handle_server.py)

## HTTP/1.1 Essentials
- Request line: METHOD SP PATH SP VERSION (e.g., “GET / HTTP/1.1”)
- Headers: one per line; end headers with a blank line (CRLF CRLF).
- Body: optional (present in POST/PUT, etc.); server must know length or use chunked encoding.
- Response format:
  - Status line: “HTTP/1.1 200 OK”
  - Headers: Content-Type, Content-Length, Connection
  - Blank line
  - Body
- Why CRLF matters: HTTP is a text protocol; CRLF delineates lines so the client can parse status, headers, and body correctly.
- Idempotency: GET/HEAD are typically idempotent; POST is not.
- Keep-Alive vs Connection: close: impacts throughput and latency.

See minimal response assembly in:
- [01_simple_socket_server.py](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/phase-0-foundation/01_simple_socket_server.py)
- Async variant in:
- [02_mutli_request_handle_server.py](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/phase-0-foundation/02_mutli_request_handle_server.py)

## DNS Basics
- Purpose: Translate human-readable hostnames to IP addresses.
- Core records: A (IPv4), AAAA (IPv6), CNAME (alias), NS (nameserver).
- Resolution path (simplified):
  - Stub resolver (your OS) asks a recursive resolver (usually your ISP or public DNS).
  - Recursive resolver queries authoritative nameservers, caches results honoring TTL.
- Multiple IPs for one hostname:
  - Load distribution (round-robin DNS).
  - Geo-routing (direct users to nearby regions).
  - Resilience/failover (if one IP is down, others still serve).
- Anycast: Same IP announced from many locations; packets route to the nearest site.

Code reference:
- Basic resolvers: [04_dns_resolver.py](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/phase-0-foundation/04_dns_resolver.py)

## Framework Contrast: Flask vs Raw Sockets
- Raw sockets:
  - Must parse request line, headers, body manually.
  - Manage Content-Length, CRLF boundaries, methods, status codes.
  - Concurrency is your responsibility (threads/async).
- Flask:
  - Routing, JSON parsing, and error handling are built-in.
  - Quick to build REST APIs and focus on business logic.

Code reference:
- Flask API: [03_flask_rest_api.py](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/phase-0-foundation/03_flask_rest_api.py)
- API test: [test_flask_api.py](file:///Users/mdnuraminsifat/Desktop/learn_system_design_hands_on/phase-0-foundation/test_flask_api.py)

## Guided Labs
1) Blocking vs Backlog (Single-threaded socket)
- Run server: python3 phase-0-foundation/01_simple_socket_server.py
- In another terminal: python3 phase-0-foundation/test_concurrency.py
- Observe:
  - First request returns ~10s, second ~20s, third may timeout (backlog=1) or ~30s.
  - Why: time.sleep() blocks; server can’t accept the next client until done.

2) Async Fairness (Non-blocking asyncio)
- Run server: python3 phase-0-foundation/02_mutli_request_handle_server.py
- In another terminal: python3 phase-0-foundation/test_async_concurrency.py
- Observe:
  - /slow takes ~5s but /fast responds immediately.
  - Why: await asyncio.sleep() yields control to the event loop.

3) REST Without the Plumbing (Flask)
- Start API: python3 phase-0-foundation/03_flask_rest_api.py
- Test: python3 phase-0-foundation/test_flask_api.py
- Observe:
  - JSON parsing, 201 Created for POST, request validation.
  - Compare to raw socket parsing complexity.

4) DNS Introspection
- Run: python3 phase-0-foundation/04_dns_resolver.py
- Observe:
  - Multiple IPs for large services.
  - Canonical names (CNAME), aliases, and IP lists from gethostbyname_ex.

## Teaching Prompts
- What breaks first when a single-threaded server gets popular?
- How does backlog differ from concurrency?
- Why do browsers care about Content-Type and Content-Length?
- How does TTL influence DNS caching and user experience during deployments?
- When would you prefer threads over asyncio, and vice versa?

## Key Terms (Quick Reference)
- Socket, Port, Backlog, Blocking I/O, Event Loop, Coroutine, Header, Status Line,
  Content-Type, Content-Length, Idempotency, DNS A/AAAA/CNAME, TTL, Anycast.

## Next Steps
- Phase 1 moves into core building blocks: load balancers, databases, caching.
- Keep the mental model: bottlenecks first, then evolve designs (naive → scalable).


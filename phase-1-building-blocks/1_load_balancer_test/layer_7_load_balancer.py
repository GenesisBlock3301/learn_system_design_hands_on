import os
import itertools
from fastapi import FastAPI, Request, Response
import httpx
import uvicorn


app = FastAPI()

def parse_backends():
    env = os.environ.get("BACKENDS", "")
    if env:
        bs = [b.strip() for b in env.split(",") if b.strip()]
    else:
        bs = ["http://127.0.0.1:9000", "http://127.0.0.1:9001"]
    return bs

BACKENDS = parse_backends()
RR = itertools.cycle(BACKENDS)

HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade"
}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def proxy(path: str, request: Request):
    target = next(RR)
    url = target + "/" + path
    if request.url.query:
        url += "?" + request.url.query

    headers = dict(request.headers)
    headers.pop("host", None)
    client_ip = request.client.host if request.client else None
    xff = headers.get("x-forwarded-for")
    if client_ip:
        headers["x-forwarded-for"] = f"{xff}, {client_ip}" if xff else client_ip

    body = await request.body()
    timeout = httpx.Timeout(5.0, read=10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        req = client.build_request(request.method, url, headers=headers, content=body)
        try:
            upstream = await client.send(req)
        except httpx.RequestError as e:
            return Response(status_code=502, content=f"Bad gateway: {e}")

    resp_headers = {k: v for k, v in upstream.headers.items() if k.lower() not in HOP_BY_HOP}
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=resp_headers,
        media_type=upstream.headers.get("content-type")
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)

from fastapi import FastAPI
import asyncio
import uvicorn

app = FastAPI()
INSTANCE_ID = "A"

@app.get("/")
async def root():
    return {"instance": INSTANCE_ID}

@app.get("/health")
async def health():
    return {"status": "ok", "instance": INSTANCE_ID}

@app.get("/slow")
async def slow(delay: float = 0.5):
    await asyncio.sleep(delay)
    return {"instance": INSTANCE_ID, "delay": delay}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
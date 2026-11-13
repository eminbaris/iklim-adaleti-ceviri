import asyncio
import uvicorn
from app import app


async def main():
    s80 = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=80, backlog=2048, ws_ping_interval=25, ws_ping_timeout=25))
    s3000 = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=3000, backlog=2048, ws_ping_interval=25, ws_ping_timeout=25))
    s8000 = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000, backlog=2048, ws_ping_interval=25, ws_ping_timeout=25))
    await asyncio.gather(s80.serve(), s3000.serve(), s8000.serve())


if __name__ == "__main__":
    asyncio.run(main())

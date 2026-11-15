import asyncio
import uvicorn
from app import app


async def main():
    cfg = dict(
        host="0.0.0.0",
        backlog=4096,
        limit_concurrency=None,
        timeout_keep_alive=15,
        ws_ping_interval=30,
        ws_ping_timeout=30,
    )
    s80 = uvicorn.Server(uvicorn.Config(app, port=80, **cfg))
    s3000 = uvicorn.Server(uvicorn.Config(app, port=3000, **cfg))
    s8000 = uvicorn.Server(uvicorn.Config(app, port=8000, **cfg))
    await asyncio.gather(s80.serve(), s3000.serve(), s8000.serve())


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import uvicorn
from app import app


async def main():
    s80 = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=80))
    s3000 = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=3000))
    s8000 = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))
    await asyncio.gather(s80.serve(), s3000.serve(), s8000.serve())


if __name__ == "__main__":
    asyncio.run(main())

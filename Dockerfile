FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY glossary.py app.py ./
COPY static ./static

EXPOSE 80 8000

CMD ["python", "-c", "import asyncio, uvicorn; from app import app; asyncio.run(asyncio.gather(uvicorn.Server(uvicorn.Config(app, host='0.0.0.0', port=80)).serve(), uvicorn.Server(uvicorn.Config(app, host='0.0.0.0', port=8000)).serve()))"]

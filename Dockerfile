FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY glossary.py app.py run.py ./
COPY static ./static

EXPOSE 80 3000 8000

CMD ["python", "run.py"]

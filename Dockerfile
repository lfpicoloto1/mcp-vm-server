FROM python:3.11-slim

WORKDIR /app

COPY server.py .

RUN pip install --no-cache-dir "mcp[cli]" httpx

CMD ["python", "server.py"] 
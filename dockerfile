FROM python:3.12-slim

WORKDIR /app

COPY tracker.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "tracker.py"]

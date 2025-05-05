FROM python:3.10-slim

RUN apt-get update && apt-get install -y espeak libsndfile1 ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# COPY ./app /app
# COPY ./models /app/models
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

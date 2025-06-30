FROM python:3.10-slim

RUN apt-get update && apt-get install -y espeak libsndfile1 ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements_trans.txt .
# RUN pip install --no-cache-dir -r requirements_trans.txt
RUN pip install -r requirements_trans.txt
RUN pip install fastapi uvicorn sentencepiece protobuf google
COPY ./app /app/app
COPY ./models /app/models

EXPOSE 9000

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/app
CMD ["uvicorn", "app.main_trans:app", "--host", "0.0.0.0", "--port", "9000"]

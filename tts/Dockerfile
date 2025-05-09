FROM nvcr.io/nvidia/pytorch:24.02-py3

# RUN apt-get update && apt-get install -y espeak libsndfile1 ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg
COPY requirements_tts.txt .
# RUN pip install --no-cache-dir -r requirements_tts.txt
RUN pip install -r requirements_tts.txt
RUN pip install fastapi uvicorn httpx

COPY ./app /app/app
COPY ./models /app/models

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/app
CMD ["uvicorn", "app.main_tts:app", "--host", "0.0.0.0", "--port", "8000"]

FROM nvcr.io/nvidia/pytorch:24.02-py3

# RUN apt-get update && apt-get install -y espeak libsndfile1 ffmpeg && rm -rf /var/lib/apt/lists/*


WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install --no-cache-dir fastapi uvicorn python-multipart faster-whisper httpx
# COPY requirements_asr.txt .
# RUN pip install --no-cache-dir -r requirements_asr.txt
# RUN pip install -r requirements_tts.txt

COPY ./app /app/app
COPY ./models /app/models

EXPOSE 7000

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/app
CMD ["uvicorn", "app.main_asr:app", "--host", "0.0.0.0", "--port", "7000"]
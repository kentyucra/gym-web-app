FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /etl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts ./scripts

CMD ["python", "scripts/process_exercise_videos.py"]

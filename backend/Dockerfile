FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    libwebp-dev \
    libpng-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install gunicorn==26.0.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY foodgram/ ./foodgram/
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

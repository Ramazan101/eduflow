FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libcairo2 \
        libffi-dev \
        libgdk-pixbuf-2.0-0 \
        libglib2.0-0 \
        libharfbuzz0b \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libjpeg62-turbo \
        libopenjp2-7 \
        shared-mime-info \
        fonts-liberation \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN mkdir -p storage/documents

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]

FROM python:3.11-slim AS Base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 appuser  \
    && useradd --uid 1000 --gid appuser --create-home --shell /bin/bash appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . .

RUN mkdir -p /app/instance && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000

CMD  ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

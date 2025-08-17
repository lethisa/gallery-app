FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Optional: system deps for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps system-wide so gunicorn goes to /usr/local/bin
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy source
COPY . .

# Create non-root user (optional)
RUN useradd -m -u 10001 appuser
USER appuser

EXPOSE 5000

# App config path (mounted via compose)
ENV CONFIG_PATH=/app/config.ini

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
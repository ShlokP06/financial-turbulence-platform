FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (build tools for scientific wheels if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

# Install the package (CPU torch by default; swap for a CUDA base image if GPU is needed)
RUN pip install --upgrade pip && pip install .

EXPOSE 8000

# Serve the FastAPI inference API
CMD ["uvicorn", "turballoc.serve.app:app", "--host", "0.0.0.0", "--port", "8000"]

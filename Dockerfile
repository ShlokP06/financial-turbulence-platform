FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

#Installing the package
RUN pip install --upgrade pip && pip install .

EXPOSE 8000

#Serving FastAPI inference
CMD ["uvicorn", "turballoc.serve.app:app", "--host", "0.0.0.0", "--port", "8000"]

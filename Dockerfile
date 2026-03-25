# Stage 1: Backend Wheel Build
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./


RUN pip install --upgrade pip setuptools wheel

COPY src ./src
RUN pip wheel --prefer-binary -w /app/wheels .




# Stage 2: Serve
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

EXPOSE 8000

CMD ["uvicorn", "ai_tomator.app:app", "--host", "0.0.0.0", "--port", "8000"]

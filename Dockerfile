FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./
COPY src ./src

RUN pip install --upgrade pip setuptools wheel
RUN pip wheel --no-deps -w /app/wheels .


FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "ai_tomator.main:app", "--host", "0.0.0.0", "--port", "8000"]

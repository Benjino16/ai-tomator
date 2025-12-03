# AI-Tomator – Setup Instructions

## Setup with Docker Compose

1. Create a directory for the service:
```
   mkdir ai-tomator
   cd ai-tomator
```
2. Place the [compose.yaml](/compose.yaml) file inside this directory.

3. Start the service:
```
   docker compose up -d
```

## Setup with Docker Run

Run the container directly:
```
   docker run \
     --name ai-tomator \
     -p 8000:8000 \
     -e DB_PATH=/data/db/database.db \
     -e STORAGE_DIR=/data/storage \
     -v db-data:/data/db \
     -v storage-data:/data/storage \
     ghcr.io/benjino16/ai-tomator:latest
```

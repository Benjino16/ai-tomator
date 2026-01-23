AI-Tomator is an all-in-one solution for scientific file evaluation using LLMs. It provides a web dashboard to easily create and manage batches with different models and settings, and to access and export results efficiently. It also supports existing batch APIs from supported providers (OpenAI, Google), allowing you to process large numbers of files without the need for a constantly running server, while reducing API costs (see [Roadmap](#roadmap)).   

<br>

> [!WARNING]
> This project is still in development and does not have a stable release yet. It is **not recommended** to run an instance on a publicly accessible server. Usage costs will apply when using commercial API backends.

<br>

## Setup with Docker Compose (recommended)

1. Create a directory for the service:
```
   mkdir ai-tomator
   cd ai-tomator
```
2. Place the [compose.yaml](/compose.yaml) file inside this directory.
```
   curl -L https://raw.githubusercontent.com/Benjino16/ai-tomator/main/compose.yaml -o compose.yaml
```

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

## Features
- Automatic evaluation and analysis of large file collections using LLMs
- Written in low-level, modular Python, making the project easy to customize and adapt to individual user requirements
- Support for multiple backends: OpenAI, Gemini, DeepSeek, Ollama
- Multiple file readers and configurable pipelines
- File upload support (depending on model/provider capabilities)
- Multi-user system for running a shared instance on a server
- Export results as CSV or Excel
- Automatic parsing and interpretation of JSON-formatted model outputs

## Roadmap
- User group system for collaborative workflows
- Optimized file uploads
  - Persist provider upload IDs in the database to avoid re-uploading identical files
- Robust worker backend using Celery + Redis
- Support for provider-side batch processing
  - Enables up to 50% cost reduction (e.g. OpenAI, Google)
- Migration to a React frontend
- Run locally using a single .exe — no technical knowledge required
- Option to use small models as file readers instead of traditional file reader modules

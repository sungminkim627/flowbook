# Running Flowbook as a Docker Container

Flowbook is now containerized! This means users with Docker and Python installed can run the entire application with a single command.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

Then open your browser to: **http://localhost:8000**

### Option 2: Using Docker directly

```bash
docker build -t flowbook:latest .
docker run -p 8000:8000 -v $(pwd)/examples:/app/examples flowbook:latest
```

Then open your browser to: **http://localhost:8000**

## What's Included

The containerized Flowbook includes:
- **Python Backend**: FastAPI server running Jupyter kernels for executing flowbook nodes
- **React Frontend**: Full UI pre-built and served from the container
- **Static File Serving**: Frontend is served directly from the API

## Features

- **Single Container**: No need to manage multiple services
- **Health Check**: Built-in health check endpoint at `/health`
- **API Documentation**: Interactive API docs available at `/docs`
- **Volume Mounting**: Examples folder is mounted for easy access to sample files

## Volumes

When using Docker, you can mount your local directories:

```bash
docker run -p 8000:8000 \
  -v $(pwd)/examples:/app/examples \
  -v $(pwd)/my-flowbooks:/app/my-flowbooks \
  flowbook:latest
```

## Ports

- **8000**: FastAPI server (includes UI + API)
- Access the UI at `http://localhost:8000`
- Access API docs at `http://localhost:8000/docs`

## Environment Variables

- `PYTHONUNBUFFERED=1`: Python output is sent straight to logs (default in docker-compose.yml)

## Stopping the Container

```bash
# If using docker-compose
docker-compose down

# If using docker run, press Ctrl+C or:
docker stop <container_id>
```

## Building Without Docker Compose

If you prefer to manage the image manually:

```bash
# Build the image
docker build -t flowbook:latest .

# Run the container
docker run -d --name flowbook -p 8000:8000 flowbook:latest

# View logs
docker logs -f flowbook

# Stop the container
docker stop flowbook
```

## Troubleshooting

### Port 8000 already in use
```bash
docker run -p 8001:8000 flowbook:latest
# Then access at http://localhost:8001
```

### Container exits immediately
Check the logs:
```bash
docker-compose logs -f
```

### Changes not reflecting
You need to rebuild the image:
```bash
docker-compose up --build
```

## Development vs Production

**Current Setup**: This configuration is suitable for development and local use.

For production deployment, consider:
- Using a production ASGI server (Gunicorn with Uvicorn workers)
- Adding authentication/authorization
- Setting up reverse proxy (Nginx/Apache)
- Using environment variables for configuration
- Implementing proper error handling and logging

## Architecture

```
┌─────────────────────────────────────────┐
│         Docker Container                │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   React Frontend (Static)        │  │
│  │   - Built from flowbook-ui       │  │
│  │   - Served on /                  │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   FastAPI Backend                │  │
│  │   - /api endpoints               │  │
│  │   - /health                      │  │
│  │   - Python code execution        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Jupyter Kernel                 │  │
│  │   - Isolated execution environment
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

## Next Steps

1. Run the container with `docker-compose up --build`
2. Open http://localhost:8000 in your browser
3. Start creating flowbook nodes!
4. Check `/docs` for API documentation

# Build stage for React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY flowbook-ui/package.json flowbook-ui/package-lock.json ./
RUN npm ci
COPY flowbook-ui/ ./
RUN npm run build

# Final stage with Python backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Jupyter
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY flowbook/ ./flowbook/
COPY examples/ ./examples/
COPY schema/ ./schema/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/build ./static

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs')" || exit 1

# Run the app
CMD ["uvicorn", "flowbook.api:app", "--host", "0.0.0.0", "--port", "8000"]

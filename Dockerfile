# Build frontend
FROM node:20 AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# Debug frontend build
RUN echo "=== Frontend build contents ===" && \
    ls -la /app/frontend/build/ && \
    echo "=== Frontend build structure ===" && \
    find /app/frontend/build -type f

# Build backend
FROM python:3.11.7-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install build dependencies and debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
WORKDIR /app
RUN mkdir -p /app/backend/static

# Copy backend files
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/

# Debug: Show directory structure before copy
RUN echo "=== Directory structure before frontend copy ===" && \
    tree /app

# Copy frontend build to backend static directory with verbose output
RUN echo "=== Copying frontend build to static directory ==="
COPY --from=frontend-build /app/frontend/build/. /app/backend/static/

# Debug: Verify static files
RUN echo "=== Final static directory contents ===" && \
    ls -la /app/backend/static/ && \
    echo "=== Full directory structure ===" && \
    tree /app && \
    echo "=== Verifying index.html ===" && \
    if [ -f "/app/backend/static/index.html" ]; then \
        echo "index.html exists" && cat /app/backend/static/index.html; \
    else \
        echo "index.html not found"; \
    fi

# Expose port
EXPOSE 8000

# Start the application with debug logging
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
# Build frontend
FROM node:20 AS frontend-build
WORKDIR /app

# Copy package files first
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copy all frontend files
COPY frontend/ ./frontend/

# Build frontend and verify output
RUN cd frontend && \
    echo "=== Building frontend ===" && \
    npm run build && \
    echo "=== Frontend build structure ===" && \
    find frontend/build -type f && \
    echo "=== Frontend build contents ===" && \
    ls -la frontend/build/ && \
    echo "=== Verifying index.html ===" && \
    cat frontend/build/index.html

# Build backend
FROM python:3.11.7-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install build dependencies and debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tree \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prepare static directory with proper permissions
RUN mkdir -p /app/backend/static && \
    chmod -R 755 /app/backend/static

# Debug: Show directory structure before copy
RUN echo "=== Directory structure before copy ===" && \
    tree /app

# Copy frontend build files to static directory
COPY --from=frontend-build /app/frontend/build/. /app/backend/static/

# Verify frontend files were copied correctly
RUN echo "=== Verifying static directory after frontend copy ===" && \
    ls -la /app/backend/static/ && \
    if [ ! -f "/app/backend/static/index.html" ]; then \
        echo "ERROR: index.html not found in static directory" && \
        exit 1; \
    fi

# Install Python dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy remaining backend files
COPY backend/ /app/backend/

# Final verification
RUN echo "=== Final directory structure ===" && \
    tree /app && \
    echo "=== Static directory contents ===" && \
    ls -la /app/backend/static/ && \
    echo "=== Verifying index.html content ===" && \
    if [ -f "/app/backend/static/index.html" ]; then \
        head -n 10 /app/backend/static/index.html; \
    else \
        echo "ERROR: index.html not found in final verification" && \
        exit 1; \
    fi

# Expose port
EXPOSE 8000

# Start the application with debug logging
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
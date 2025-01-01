# Use Python image as base
FROM python:3.11.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NODE_VERSION=20
ENV DEBUG=1

# Install Node.js and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create backend structure first
RUN mkdir -p /app/backend/static && \
    chmod -R 755 /app/backend/static

# Copy backend files
COPY backend/ ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend files
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

COPY frontend/ ./frontend/

# Build frontend and copy to static directory
RUN cd frontend && \
    echo "Building frontend..." && \
    npm run build && \
    echo "Frontend build contents:" && \
    ls -la build/ && \
    echo "Copying frontend build to static directory..." && \
    cp -rv build/* /app/backend/static/ && \
    echo "Verifying static directory contents:" && \
    ls -la /app/backend/static/ && \
    if [ ! -f "/app/backend/static/index.html" ]; then \
        echo "ERROR: index.html not found" && \
        exit 1; \
    fi && \
    echo "Static directory permissions:" && \
    ls -la /app/backend/ | grep static && \
    echo "Index.html contents:" && \
    head -n 5 /app/backend/static/index.html

# Final verification
RUN echo "=== Final directory structure ===" && \
    find /app -type f -name "index.html" -ls && \
    echo "=== Static files ===" && \
    ls -la /app/backend/static/ && \
    echo "=== Static directory permissions ===" && \
    stat /app/backend/static

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
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

# Copy frontend files and build
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

COPY frontend/ ./frontend/
RUN cd frontend && \
    npm run build && \
    echo "Frontend build contents:" && \
    ls -la frontend/build/

# Create backend structure
RUN mkdir -p /app/backend/static && \
    chmod -R 755 /app/backend/static

# Copy backend files
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

# Copy frontend build to static directory with verbose output
RUN echo "Copying frontend build files..." && \
    rm -rf /app/backend/static/* && \
    cp -rv /app/frontend/build/* /app/backend/static/ && \
    echo "Verifying static directory contents:" && \
    ls -la /app/backend/static/ && \
    if [ ! -f "/app/backend/static/index.html" ]; then \
        echo "ERROR: index.html not found after copy" && \
        exit 1; \
    fi && \
    echo "Setting permissions:" && \
    chmod -R 755 /app/backend/static && \
    echo "Final static directory structure:" && \
    find /app/backend/static -type f -ls

# Expose port
EXPOSE 8000

# Start the application with debug logging
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
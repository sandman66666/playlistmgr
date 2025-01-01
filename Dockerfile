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

# Create directory structure
RUN mkdir -p /app/frontend/build && \
    mkdir -p /app/backend && \
    chmod -R 755 /app/frontend/build

# Copy backend files first
COPY backend/ ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend files
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

COPY frontend/ ./frontend/

# Build frontend
RUN cd frontend && \
    echo "Building frontend..." && \
    npm run build && \
    echo "Frontend build contents:" && \
    ls -la build/ && \
    echo "Verifying build files:" && \
    if [ ! -f "build/index.html" ]; then \
        echo "ERROR: index.html not found in build directory" && \
        exit 1; \
    fi && \
    echo "Index.html contents:" && \
    head -n 5 build/index.html

# Final verification
RUN echo "=== Directory structure ===" && \
    find /app -type f -name "index.html" -ls && \
    echo "=== Frontend build files ===" && \
    ls -la /app/frontend/build/ && \
    echo "=== Build directory permissions ===" && \
    stat /app/frontend/build

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
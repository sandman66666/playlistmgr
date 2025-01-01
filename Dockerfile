# Use Python image as base
FROM python:3.11.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NODE_VERSION=20

# Install Node.js and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy frontend files
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

COPY frontend/ ./frontend/

# Build frontend
RUN cd frontend && npm run build && \
    echo "Frontend build contents:" && \
    ls -la frontend/build/

# Create and prepare static directory
RUN mkdir -p /app/backend/static && \
    cp -rv frontend/build/* /app/backend/static/ && \
    echo "Static directory contents:" && \
    ls -la /app/backend/static/

# Copy backend files
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

# Verify final structure
RUN echo "Final static directory contents:" && \
    ls -la /app/backend/static/ && \
    echo "Verifying index.html:" && \
    cat /app/backend/static/index.html

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
# Build frontend
FROM node:20 AS frontend-build
WORKDIR /frontend-build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build && \
    echo "Frontend build contents:" && \
    ls -la build/

# Build static files
FROM alpine:latest AS static-build
WORKDIR /static-build
COPY --from=frontend-build /frontend-build/build/ ./
RUN echo "Static build contents:" && \
    ls -la

# Final stage
FROM python:3.11.7-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DEBUG=1

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend files first
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

# Create static directory
RUN mkdir -p /app/backend/static && \
    chmod -R 755 /app/backend/static

# Copy static files from build stage
COPY --from=static-build /static-build/ /app/backend/static/

# Verify static files
RUN echo "Final static directory contents:" && \
    ls -la /app/backend/static/ && \
    if [ ! -f "/app/backend/static/index.html" ]; then \
        echo "ERROR: index.html not found" && \
        exit 1; \
    fi && \
    echo "Static directory permissions:" && \
    ls -la /app/backend/ | grep static && \
    echo "Index.html contents:" && \
    head -n 5 /app/backend/static/index.html

# Create volume for static files
VOLUME /app/backend/static

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
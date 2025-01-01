# Build frontend
FROM node:20 AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# Build backend
FROM python:3.11.7-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
WORKDIR /app
RUN mkdir -p /app/backend/static

# Copy backend files
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/

# Copy frontend build to backend static directory
COPY --from=frontend-build /app/frontend/build/. /app/backend/static/

# Debug: List contents of static directory
RUN ls -la /app/backend/static/

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
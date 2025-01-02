#!/bin/bash
# Create static directory if it doesn't exist
mkdir -p backend/static

# Remove existing files in static directory (except .gitkeep)
find backend/static -type f ! -name '.gitkeep' -delete

# Copy frontend build files to static directory
cp -r frontend/build/* backend/static/

echo "Frontend build files copied to backend/static/"
#!/bin/bash
set -e

echo "Starting frontend build file copy process..."

# Create static directory if it doesn't exist
mkdir -p backend/static
echo "Created backend/static directory"

# Clean existing files (preserve .gitkeep)
echo "Cleaning existing files..."
find backend/static -type f ! -name '.gitkeep' -exec rm -f {} +
find backend/static -type d ! -name 'static' ! -name '.' ! -name '..' -exec rm -rf {} +

# Check if frontend/build exists
if [ ! -d "frontend/build" ]; then
    echo "Error: frontend/build directory not found. Running build first..."
    cd frontend && npm run build && cd ..
fi

# Copy files with verbose output
echo "Copying files from frontend/build to backend/static..."
cp -rv frontend/build/* backend/static/

# Verify copy
echo "Verifying copied files..."
echo "Contents of backend/static:"
ls -la backend/static/

if [ -d "backend/static/static" ]; then
    echo "Contents of backend/static/static:"
    ls -la backend/static/static/
else
    echo "Warning: static subdirectory not found"
fi

# Check for critical files
if [ ! -f "backend/static/index.html" ]; then
    echo "Error: index.html not found in destination"
    exit 1
fi

echo "Copy process completed successfully"
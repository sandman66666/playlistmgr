#!/bin/bash

echo "=== Starting build verification ==="

# Check if frontend/build exists
if [ ! -d "frontend/build" ]; then
  echo "ERROR: frontend/build directory not found!"
  exit 1
fi

# Check if index.html exists in frontend/build
if [ ! -f "frontend/build/index.html" ]; then
  echo "ERROR: index.html not found in frontend/build!"
  exit 1
fi

# Create backend/static directory
mkdir -p backend/static

# Copy build files
echo "Copying build files to backend/static..."
cp -rv frontend/build/* backend/static/

# Verify copy
echo "Verifying copied files..."
if [ ! -f "backend/static/index.html" ]; then
  echo "ERROR: index.html not found in backend/static after copy!"
  exit 1
fi

echo "Listing backend/static contents:"
ls -la backend/static/

echo "=== Build verification complete ==="
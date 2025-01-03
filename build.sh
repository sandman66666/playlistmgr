#!/bin/bash

# Exit on error
set -e

echo "Starting build process..."

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install

# Build frontend
echo "Building frontend..."
npm run build

# Create static directory if it doesn't exist
echo "Setting up static directory..."
cd ..
mkdir -p backend/static

# Copy frontend build to backend static directory
echo "Copying frontend build to backend static..."
if [ -d "frontend/build" ]; then
    echo "Copying build files..."
    cp -r frontend/build/* backend/static/
    echo "Verifying static directory contents..."
    ls -la backend/static/
else
    echo "Error: frontend/build directory not found!"
    exit 1
fi

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r ../requirements.txt

echo "Build process completed successfully!"
echo "Static directory contents:"
ls -la static/
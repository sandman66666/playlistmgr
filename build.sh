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
    # First, clean the static directory
    rm -rf backend/static/*
    
    # Copy all files from build directory
    cp -r frontend/build/* backend/static/
    
    # If there's a nested static directory, move its contents up
    if [ -d "backend/static/static" ]; then
        mv backend/static/static/* backend/static/
        rm -rf backend/static/static
    fi
    
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
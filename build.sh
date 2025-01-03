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
cp -r frontend/build/* backend/static/

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r ../requirements.txt

echo "Build process completed successfully!"
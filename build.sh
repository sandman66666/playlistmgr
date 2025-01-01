#!/bin/bash

# Exit on error
set -e

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building frontend..."
npm run build

echo "Moving back to root directory..."
cd ..

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"
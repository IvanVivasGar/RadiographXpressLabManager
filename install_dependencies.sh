#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Radiograph Xpress Dependency Installer ==="

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js before continuing."
    echo "Visit https://nodejs.org/ to download and install."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm."
    exit 1
fi

echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

# Install Frontend Dependencies
if [ -d "frontend" ]; then
    echo "-----------------------------------"
    echo "Installing Frontend dependencies..."
    echo "-----------------------------------"
    cd frontend
    npm install
    
    # Return to root
    cd ..
    echo "Frontend dependencies installed successfully."
else
    echo "Error: 'frontend' directory not found. Please ensure you are in the project root."
    exit 1
fi

echo "-----------------------------------"
echo "All dependencies installed successfully!"
echo "To start the application, you can run:"
echo "  cd frontend && npm start"
echo "-----------------------------------"

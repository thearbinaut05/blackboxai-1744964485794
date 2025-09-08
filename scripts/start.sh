#!/bin/bash

# Start script for click-clack-cash-flow monitoring system

echo "Starting Click-Clack-Cash-Flow Payment Verification and Monitoring System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r swarm/requirements.txt

# Set environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env"
    export $(cat .env | xargs)
fi

# Start the FastAPI application
echo "Starting payment verification and monitoring system..."
python -m uvicorn core.main:app --host 0.0.0.0 --port 8000 --reload
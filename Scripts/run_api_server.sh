#!/bin/bash

echo "Starting RAG API Server..."

# Activate virtual environment
if [ -d "rag_env" ]; then
    source rag_env/bin/activate
    echo "Activated virtual environment"
else
    echo "Virtual environment not found. Please run setup_environment.sh first"
    exit 1
fi

# Set environment variables
export FLASK_APP=API_Server/rag_api.py
export FLASK_ENV=development
export PYTHONPATH="\${PYTHONPATH}:\$(pwd)"

# Create logs directory
mkdir -p Logs

# Start the server
echo "Starting server on http://localhost:5000"
python API_Server/rag_api.py 2>&1 | tee Logs/api_server.log

#!/bin/bash

echo "Setting up Conversational Agent Environment..."

# Create virtual environment
python3 -m venv rag_env
source rag_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create necessary directories
mkdir -p Database/data
mkdir -p Logs
mkdir -p Data_Storage/vector_store
mkdir -p Data_Storage/cache

# Initialize database
python Scripts/setup_database.py

echo "Environment setup complete!"
echo "To activate: source rag_env/bin/activate"
echo "To start server: ./Scripts/run_api_server.sh"
#!/bin/bash
set -e

echo "Setting up Coppelia MVP development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Created virtual environment"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file - please add your OpenAI API key"
fi

# Set up pre-commit hooks
pre-commit install

echo "Development environment setup complete!"
echo "Don't forget to:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Add your OpenAI API key to .env file"
echo "3. Run tests: python -m pytest tests/ -v"

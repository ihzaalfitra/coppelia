#!/bin/bash
set -e

echo "Running Coppelia MVP test suite..."

# Activate virtual environment
source venv/bin/activate

# Run code formatting check
echo "Checking code formatting..."
black --check src/ tests/

# Run type checking
echo "Running type checks..."
mypy src/

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit/ -v --cov=src/coppelia

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration/ -v

echo "All tests completed!"

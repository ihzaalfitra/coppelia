@echo off
echo Setting up Coppelia MVP development environment...

REM Check if virtual environment exists
if not exist "venv" (
    python -m venv venv
    echo Created virtual environment
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

REM Create .env file if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo Created .env file - please add your OpenAI API key
)

REM Set up pre-commit hooks
pre-commit install

echo Development environment setup complete!
echo Don't forget to:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Add your OpenAI API key to .env file
echo 3. Run tests: python -m pytest tests/ -v
pause

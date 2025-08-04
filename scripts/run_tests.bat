@echo off
echo Running Coppelia MVP test suite...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run code formatting check
echo Checking code formatting...
black --check src/ tests/

REM Run type checking
echo Running type checks...
mypy src/

REM Run unit tests
echo Running unit tests...
python -m pytest tests/unit/ -v --cov=src/coppelia

REM Run integration tests
echo Running integration tests...
python -m pytest tests/integration/ -v

echo All tests completed!
pause

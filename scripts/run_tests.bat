@echo off
rem Running all tests

echo Running unit tests...
python -m pytest tests/ -v

echo Generating coverage report...
python -m pytest tests/ --cov=statis_log --cov-report=term --cov-report=html:htmlcov

rem Results
if %errorlevel% == 0 (
    echo Tests passed!
    echo Coverage report has been generated in htmlcov directory
    exit /b 0
) else (
    echo Tests failed!
    exit /b 1
) 
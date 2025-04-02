@echo off
echo Installing development environment...

REM Check if Poetry is installed
where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing Poetry...
    powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
)

REM Install project dependencies
echo Installing project dependencies...
poetry install

REM Install pre-commit hooks (if configured)
if exist ".pre-commit-config.yaml" (
    echo Installing pre-commit hooks...
    poetry run pre-commit install
)

echo Development environment setup complete! 
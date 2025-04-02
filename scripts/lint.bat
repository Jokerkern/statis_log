@echo off
echo Running code formatting and linting...

REM Run isort to sort imports
echo Running isort...
poetry run isort statis_log tests

REM Run black for code formatting
echo Running black...
poetry run black statis_log tests

REM Run flake8 for code linting
echo Running flake8...
poetry run flake8 statis_log tests

REM Run mypy for type checking
echo Running mypy...
poetry run mypy statis_log

echo Code formatting and linting completed! 
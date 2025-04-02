@echo off
echo Cleaning old build files...
rmdir /s /q dist build 2>nul
del /s /q *.egg-info 2>nul

REM Run tests first
echo Running tests...
poetry run pytest

REM Build package
echo Building project...
poetry build

REM Publish to PyPI (optional, requires user confirmation)
set /p response=Do you want to publish to PyPI? (y/n)
if /i "%response%"=="y" (
    echo Publishing to PyPI...
    poetry publish
) else (
    echo Skipping PyPI publishing
)

echo Build process completed! 
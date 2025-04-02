@echo off
echo Starting development server...

REM If config file is provided, use it
if not "%~1"=="" if exist "%~1" (
    set CONFIG_FILE=%~1
    echo Using config file: %CONFIG_FILE%
    poetry run statis-log --config "%CONFIG_FILE%"
) else (
    REM Use default configuration
    echo Using default configuration
    poetry run statis-log
) 
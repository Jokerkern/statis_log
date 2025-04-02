@echo off
echo 正在启动开发服务器...

REM 如果有配置文件，可以从特定配置文件启动
if not "%~1"=="" if exist "%~1" (
    set CONFIG_FILE=%~1
    echo 使用配置文件: %CONFIG_FILE%
    poetry run statis-log --config "%CONFIG_FILE%"
) else (
    REM 默认配置
    echo 使用默认配置
    poetry run statis-log
) 
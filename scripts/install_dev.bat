@echo off
echo 正在安装开发环境...

REM 检查Poetry是否已安装
where poetry >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 正在安装Poetry...
    powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
)

REM 安装项目依赖
echo 正在安装项目依赖...
poetry install

REM 安装pre-commit钩子（如果已配置）
if exist ".pre-commit-config.yaml" (
    echo 正在安装pre-commit钩子...
    poetry run pre-commit install
)

echo 开发环境安装完成！ 
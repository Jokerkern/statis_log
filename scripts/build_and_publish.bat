@echo off
echo 正在清理旧的构建文件...
rmdir /s /q dist build 2>nul
del /s /q *.egg-info 2>nul

REM 首先运行测试
echo 正在运行测试...
poetry run pytest

REM 构建包
echo 正在构建项目...
poetry build

REM 发布到PyPI（可选，需要用户确认）
set /p response=是否要发布到PyPI？(y/n)
if /i "%response%"=="y" (
    echo 发布到PyPI...
    poetry publish
) else (
    echo 跳过发布到PyPI
)

echo 构建过程完成！ 
@echo off
rem 运行所有测试

echo 正在运行单元测试...
python -m pytest tests/ -v

echo 正在生成覆盖率报告...
python -m pytest tests/ --cov=statis_log --cov-report=term --cov-report=html:htmlcov

rem 运行结果
if %errorlevel% == 0 (
    echo 测试通过
    echo 覆盖率报告已生成在 htmlcov 目录中
    exit /b 0
) else (
    echo 测试失败
    exit /b 1
) 
@echo off
echo 正在运行代码格式化和检查...

REM 使用isort排序导入
echo 正在运行isort...
poetry run isort statis_log tests

REM 使用black格式化代码
echo 正在运行black...
poetry run black statis_log tests

REM 使用flake8检查代码
echo 正在运行flake8...
poetry run flake8 statis_log tests

REM 使用mypy进行类型检查
echo 正在运行mypy...
poetry run mypy statis_log

echo 代码格式化和检查完成！ 
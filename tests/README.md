# StatisLog 测试指南

本目录包含 StatisLog 项目的测试代码。以下是关于如何运行测试以及测试结构的说明。

## 运行测试

可以使用以下方法运行测试:

### Windows

```bash
.\run_tests.bat
```

或手动运行:

```bash
# 运行所有测试
python -m pytest tests/ -v

# 生成覆盖率报告
python -m pytest tests/ --cov=statis_log --cov-report=term --cov-report=html:htmlcov
```

### Linux/macOS

```bash
./run_tests.sh
```

或手动运行:

```bash
# 运行所有测试
python -m pytest tests/ -v

# 生成覆盖率报告
python -m pytest tests/ --cov=statis_log --cov-report=term --cov-report=html:htmlcov
```

## 测试结构

测试按照模块进行组织:

- `test_core.py`: 测试核心模块功能，包括 StatisLog 类和 PluginRegistry
- `test_config.py`: 测试配置管理功能
- `test_plugin.py`: 测试插件装饰器和注册功能
- `test_cli.py`: 测试命令行接口
- `test_integration.py`: 测试组件集成功能

## 覆盖率报告

运行测试后，覆盖率报告将生成在 `htmlcov` 目录中，可通过浏览器打开 `htmlcov/index.html` 查看详细的覆盖率情况。

## 添加新测试

添加新测试时，请遵循以下规则:

1. 为每个主要模块创建单独的测试文件
2. 使用类对相关测试进行分组
3. 测试方法名应清晰描述被测试的功能
4. 尽可能使用 pytest 夹具
5. 合理使用模拟和补丁来隔离测试

## 注意事项

- 所有测试都应该是独立的，不应依赖于其他测试的运行结果
- 测试应该专注于一个功能或一个行为，而不是多个
- 测试失败时，错误信息应该清晰地指出失败的原因 
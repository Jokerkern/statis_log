"""
pytest配置文件

定义测试所需的通用夹具和配置
"""

import logging
import os
import tempfile

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """设置测试的日志记录"""
    # 配置根日志记录器，使其不输出到控制台
    logging.basicConfig(level=logging.INFO, handlers=[])

    # 创建一个空的处理器，防止输出到控制台
    null_handler = logging.NullHandler()
    logging.getLogger("statis_log").addHandler(null_handler)


@pytest.fixture
def temp_dir():
    """创建一个临时目录"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_config():
    """创建一个示例配置"""
    return {
        "collectors": {
            "file_collector": {
                "type": "file",
                "enabled": True,
                "path": "/tmp",
                "pattern": "*.log",
            }
        },
        "analyzers": {
            "pattern_analyzer": {
                "type": "pattern",
                "enabled": True,
                "rules": [
                    {"name": "error_rule", "pattern": "ERROR", "severity": "error"}
                ],
            }
        },
        "notifiers": {"console_notifier": {"type": "console", "enabled": True}},
    }


@pytest.fixture
def sample_logs():
    """创建一个示例日志列表"""
    return [
        {
            "source": "file_collector",
            "file": "/tmp/app.log",
            "line": 1,
            "content": "2023-01-01 12:00:00 INFO: 正常操作",
            "timestamp": "2023-01-01T12:00:00",
        },
        {
            "source": "file_collector",
            "file": "/tmp/app.log",
            "line": 2,
            "content": "2023-01-01 12:01:00 ERROR: 发生了错误",
            "timestamp": "2023-01-01T12:01:00",
        },
        {
            "source": "file_collector",
            "file": "/tmp/app.log",
            "line": 3,
            "content": "2023-01-01 12:02:00 WARNING: 警告信息",
            "timestamp": "2023-01-01T12:02:00",
        },
    ]

"""
集成测试模块

测试日志收集、分析和通知流程的集成
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from statis_log.analyzers.pattern_analyzer import PatternAnalyzer
from statis_log.collectors.file_collector import FileCollector
from statis_log.core import StatisLog


class TestIntegration:
    """测试组件集成功能"""

    @pytest.fixture
    def test_log_file(self):
        """创建测试日志文件"""
        # 创建临时日志文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", encoding="utf-8", delete=False
        ) as temp:
            # 写入一些测试日志
            temp.write("2023-01-01 12:00:00 INFO: 正常操作\n")
            temp.write("2023-01-01 12:01:00 ERROR: 发生了错误\n")
            temp.write("2023-01-01 12:02:00 WARNING: 警告信息\n")
            temp.write("2023-01-01 12:03:00 INFO: 另一条正常日志\n")
            temp.write("2023-01-01 12:04:00 ERROR: 另一个错误\n")
            temp_path = temp.name

        # 提供文件路径，并在测试后清理
        yield temp_path

        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def mock_notifier(self):
        """模拟通知器"""
        mock = MagicMock()
        mock.notify.return_value = True
        return mock

    def test_file_collector_directly(self, test_log_file):
        """直接测试文件收集器"""
        # 创建收集器
        collector_config = {
            "path": os.path.dirname(test_log_file),
            "pattern": os.path.basename(test_log_file),
            "encoding": "utf-8",
        }
        collector = FileCollector("test_collector", collector_config)

        # 执行收集
        logs = collector.collect()

        # 验证结果
        assert len(logs) == 5
        assert any("ERROR" in log["content"] for log in logs)
        assert any("WARNING" in log["content"] for log in logs)
        assert any("INFO" in log["content"] for log in logs)

        # 验证日志格式
        for log in logs:
            assert "source" in log
            assert "file" in log
            assert "line" in log
            assert "content" in log
            assert "timestamp" in log

    def test_pattern_analyzer_directly(self):
        """直接测试模式分析器"""
        # 准备测试日志
        logs = [
            {"content": "2023-01-01 12:00:00 INFO: 正常操作"},
            {"content": "2023-01-01 12:01:00 ERROR: 发生了错误"},
            {"content": "2023-01-01 12:02:00 WARNING: 警告信息"},
        ]

        # 创建分析器
        analyzer_config = {
            "rules": [
                {
                    "name": "error_rule",
                    "pattern": "ERROR",
                    "severity": "error",
                    "description": "检测错误",
                },
                {
                    "name": "warning_rule",
                    "pattern": "WARNING",
                    "severity": "warning",
                    "description": "检测警告",
                },
            ]
        }
        analyzer = PatternAnalyzer("test_analyzer", analyzer_config)

        # 执行分析
        result = analyzer.analyze(logs)

        # 验证结果
        assert "matches" in result
        assert "summary" in result
        assert len(result["matches"]) == 2  # 匹配两条日志
        assert result["summary"]["matched_logs"] == 2
        assert result["summary"]["rule_matches"]["error_rule"] == 1
        assert result["summary"]["rule_matches"]["warning_rule"] == 1
        assert result["summary"]["severity_counts"]["error"] == 1
        assert result["summary"]["severity_counts"]["warning"] == 1

    def test_workflow_without_notifiers(self, test_log_file):
        """测试工作流程，但不测试通知部分"""
        # 构建测试配置
        log_dir = os.path.dirname(test_log_file)
        log_name = os.path.basename(test_log_file)

        config = {
            "collectors": {
                "file_collector": {
                    "type": "file",
                    "enabled": True,
                    "path": log_dir,
                    "pattern": log_name,
                    "encoding": "utf-8",
                }
            },
            "analyzers": {
                "pattern_analyzer": {
                    "type": "pattern",
                    "enabled": True,
                    "content_field": "content",
                    "rules": [
                        {
                            "name": "error_rule",
                            "pattern": "ERROR",
                            "severity": "error",
                            "description": "检测错误",
                        },
                        {
                            "name": "warning_rule",
                            "pattern": "WARNING",
                            "severity": "warning",
                            "description": "检测警告",
                        },
                    ],
                }
            },
            # 不使用通知器，避免需要额外的mock
            "notifiers": {},
        }

        # 运行StatisLog
        statis_log = StatisLog(config=config)

        # 执行工作流
        result = statis_log.run()

        # 验证运行结果
        assert result["status"] == "success"
        assert result["logs_collected"] > 0
        # 不测试通知部分
        assert result["notification_count"] == 0

"""
测试命令行通知器功能
"""

import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from statis_log.notifiers.cli_notifier import CliNotifier


class TestCliNotifier:
    """测试命令行通知器功能"""

    def test_init_default_config(self):
        """测试默认配置初始化"""
        notifier = CliNotifier("test_cli")
        
        # 验证默认配置
        assert notifier.name == "test_cli"
        assert notifier.use_color is True
        assert notifier.output_format == "text"
        assert notifier.output_file is None

    def test_init_custom_config(self):
        """测试自定义配置初始化"""
        config = {
            "use_color": False,
            "output_format": "json",
            "output_file": "test.log",
            "severity_colors": {
                "info": "blue",
                "error": "magenta"
            }
        }
        
        notifier = CliNotifier("test_cli", config)
        
        # 验证自定义配置
        assert notifier.name == "test_cli"
        assert notifier.use_color is False
        assert notifier.output_format == "json"
        assert notifier.output_file == "test.log"
        
        # 验证颜色自定义
        assert notifier.severity_colors["info"] == notifier.COLORS["blue"]
        assert notifier.severity_colors["error"] == notifier.COLORS["magenta"]

    @patch("sys.stdout", new_callable=StringIO)
    def test_notify_text_format(self, mock_stdout):
        """测试文本格式通知"""
        # 创建通知器
        notifier = CliNotifier("test_cli", {"use_color": False})  # 禁用颜色以便于测试
        
        # 发送通知
        title = "测试标题"
        message = "测试消息"
        data = {
            "matched_logs": 5,
            "error_count": 2,
            "warning_count": 3,
            "severity": "error"
        }
        
        # 调用通知方法
        result = notifier.notify(title, message, data)
        
        # 验证结果
        assert result is True
        
        # 获取输出内容
        output = mock_stdout.getvalue()
        
        # 验证输出内容包含标题和消息
        assert title in output
        assert message in output
        
        # 验证输出包含数据摘要
        assert "matched_logs: 5" in output
        assert "error_count: 2" in output
        assert "warning_count: 3" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_notify_json_format(self, mock_stdout):
        """测试JSON格式通知"""
        # 创建通知器
        notifier = CliNotifier("test_cli", {"output_format": "json"})
        
        # 发送通知
        title = "测试标题"
        message = "测试消息"
        data = {"matched_logs": 5}
        
        # 调用通知方法
        result = notifier.notify(title, message, data)
        
        # 验证结果
        assert result is True
        
        # 获取输出内容
        output = mock_stdout.getvalue()
        
        # 验证输出是有效JSON
        import json
        output_data = json.loads(output)
        
        # 验证JSON内容
        assert output_data["title"] == title
        assert output_data["message"] == message
        assert "timestamp" in output_data
        assert output_data["data"]["matched_logs"] == 5

    def test_notify_to_file(self, tmp_path):
        """测试输出到文件"""
        # 创建临时文件路径
        temp_file = tmp_path / "test_output.log"
        
        # 创建通知器
        notifier = CliNotifier("test_cli", {"output_file": str(temp_file)})
        
        # 发送通知
        title = "文件通知测试"
        message = "这是一条测试消息"
        
        # 调用通知方法
        result = notifier.notify(title, message)
        
        # 验证结果
        assert result is True
        
        # 验证文件已创建
        assert temp_file.exists()
        
        # 验证文件内容
        content = temp_file.read_text(encoding="utf-8")
        assert title in content
        assert message in content

    def test_format_message(self):
        """测试消息格式化"""
        notifier = CliNotifier("test_cli")
        
        # 带变量的消息模板
        template = "检测到 {count} 个错误，严重程度: {severity}"
        data = {"count": 5, "severity": "高"}
        
        # 格式化消息
        result = notifier.format_message(template, data)
        
        # 验证结果
        assert result == "检测到 5 个错误，严重程度: 高"
        
        # 测试缺少键的情况
        template = "缺少键 {missing}"
        result = notifier.format_message(template, data)
        
        # 验证结果 - 应该返回原始模板
        assert result == template

    @patch.dict(os.environ, {"NO_COLOR": "1"})
    def test_no_color_env_var(self):
        """测试NO_COLOR环境变量禁用颜色"""
        notifier = CliNotifier("test_cli", {"use_color": True})
        
        # 验证颜色被禁用
        assert notifier.use_color is False 
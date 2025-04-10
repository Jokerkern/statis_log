"""
命令行通知器

直接在命令行中显示通知信息
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from statis_log.utils.plugin import notifier

from .base import BaseNotifier

logger = logging.getLogger(__name__)


@notifier("cli")
class CliNotifier(BaseNotifier):
    """命令行通知器"""

    # ANSI颜色代码
    COLORS = {
        "reset": "\033[0m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bold": "\033[1m",
    }

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化命令行通知器

        Args:
            name: 通知器名称
            config: 通知器配置，可选字段：
                use_color: 是否使用彩色输出（默认True）
                output_format: 输出格式，支持text、json、yaml（默认text）
                output_file: 输出文件路径（默认None，表示标准输出）
                severity_colors: 不同严重程度的颜色配置
        """
        super().__init__(name, config)
        self.use_color = self.config.get("use_color", True)
        self.output_format = self.config.get("output_format", "text")
        self.output_file = self.config.get("output_file")
        
        # 检查是否在不支持ANSI颜色的环境中
        if "NO_COLOR" in os.environ or not sys.stdout.isatty():
            self.use_color = False
            
        # 设置不同严重程度的颜色
        self.severity_colors = {
            "info": self.COLORS.get("green"),
            "warning": self.COLORS.get("yellow"),
            "error": self.COLORS.get("red"),
            "critical": self.COLORS.get("bold") + self.COLORS.get("red"),
        }
        
        # 使用用户配置覆盖默认颜色
        user_colors = self.config.get("severity_colors", {})
        for severity, color in user_colors.items():
            if color in self.COLORS:
                self.severity_colors[severity] = self.COLORS.get(color)

    def notify(
        self, title: str, message: str, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送命令行通知

        Args:
            title: 通知标题
            message: 通知内容
            data: 附加数据，可用于格式化消息

        Returns:
            发送结果
        """
        try:
            # 处理消息内容
            formatted_message = message
            if data:
                formatted_message = self.format_message(message, data)
                
            # 准备输出内容
            output = self.format_output(title, formatted_message, data)
            
            # 输出到文件或标准输出
            if self.output_file:
                with open(self.output_file, "a", encoding="utf-8") as f:
                    f.write(output + "\n")
            else:
                print(output)
                
            logger.info(f"命令行通知已显示: {title}")
            return True
            
        except Exception as e:
            logger.error(f"命令行通知显示失败: {e}")
            return False
            
    def format_output(self, title: str, message: str, data: Optional[Dict[str, Any]]) -> str:
        """
        根据配置的格式输出通知内容

        Args:
            title: 通知标题
            message: 通知内容
            data: 附加数据

        Returns:
            格式化后的输出内容
        """
        if self.output_format == "json":
            output_data = {
                "title": title,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
            if data:
                output_data["data"] = data
            return json.dumps(output_data, ensure_ascii=False, indent=2)
            
        elif self.output_format == "yaml":
            try:
                import yaml
                output_data = {
                    "title": title,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
                if data:
                    output_data["data"] = data
                return yaml.dump(output_data, default_flow_style=False, sort_keys=False)
            except ImportError:
                logger.warning("未安装yaml库，回退使用文本格式")
                self.output_format = "text"
                
        # 默认使用文本格式
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 根据严重程度确定颜色
        severity = "info"
        if data and "severity" in data:
            severity = data["severity"]
            
        # 构建带颜色的输出
        if self.use_color and severity in self.severity_colors:
            color = self.severity_colors[severity]
            header = f"{color}{self.COLORS['bold']}[{timestamp}] {title}{self.COLORS['reset']}"
        else:
            header = f"[{timestamp}] {title}"
            
        # 构建完整输出
        output = f"{header}\n{message}"
        
        # 如果有数据，添加摘要
        if data and isinstance(data, dict) and self.output_format == "text":
            summary = []
            
            # 提取重要信息到摘要
            important_keys = ["matched_logs", "error_count", "warning_count", "analysis_count"]
            for key in important_keys:
                if key in data:
                    summary.append(f"{key}: {data[key]}")
                    
            if summary:
                output += f"\n\n摘要信息:\n" + "\n".join(summary)
                
        return output 
"""
命令行接口模块

提供命令行工具的主要接口
"""

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import yaml

from statis_log.core import (
    StatisLog,
    analyzer_registry,
    collector_registry,
    notifier_registry,
)
from statis_log.utils.config import load_config, save_config
from statis_log.utils.logger import setup_logging
from statis_log import __version__

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器

    Returns:
        参数解析器对象
    """
    parser = argparse.ArgumentParser(
        description="statis_log - 日志收集、分析和通知工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # 添加版本参数选项
    parser.add_argument("-v", "--version", action="store_true", help="显示版本信息")

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # run 命令
    run_parser = subparsers.add_parser("run", help="运行日志收集和分析")
    run_parser.add_argument("-c", "--config", help="配置文件路径", required=True)
    run_parser.add_argument(
        "--log-level",
        help="日志级别",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )
    run_parser.add_argument("--log-file", help="日志输出文件")

    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化配置文件")
    init_parser.add_argument("-o", "--output", help="输出配置文件路径", required=True)
    init_parser.add_argument(
        "--format", help="配置文件格式", choices=["json", "yaml"], default="yaml"
    )

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出可用的插件")
    list_parser.add_argument(
        "--type",
        help="插件类型",
        choices=["collector", "analyzer", "notifier", "all"],
        default="all",
    )

    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证配置文件")
    validate_parser.add_argument("-c", "--config", help="配置文件路径", required=True)

    return parser


def handle_run(args: argparse.Namespace) -> int:
    """
    处理run命令

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    # 设置日志
    setup_logging(log_level=args.log_level, log_file=args.log_file)

    try:
        # 初始化并运行
        statis_log = StatisLog(config_path=args.config)
        result = statis_log.run()

        # 输出摘要
        print("\n运行摘要:")
        print(f"状态: {result['status']}")
        print(f"执行时间: {result['execution_time']:.2f} 秒")
        print(f"收集日志: {result['logs_collected']} 条")
        print(f"分析结果: {result['analysis_count']} 个")
        print(f"发送通知: {result['notification_count']} 个")

        # 返回状态码
        return 0 if result["status"] == "success" else 1

    except Exception as e:
        logger.error(f"运行错误: {e}")
        return 1


def handle_init(args: argparse.Namespace) -> int:
    """
    处理init命令，生成示例配置文件

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    # 创建示例配置
    config = {
        "collectors": {
            "app_logs": {
                "type": "file",
                "path": "/var/log/app",
                "pattern": "*.log",
                "content_filter": "ERROR|WARN",
                "max_size": 10,
            }
        },
        "analyzers": {
            "error_analyzer": {
                "type": "pattern",
                "content_field": "content",
                "rules": [
                    {
                        "name": "exception",
                        "pattern": "Exception|Error|错误|异常",
                        "severity": "error",
                        "description": "检测异常和错误",
                    },
                    {
                        "name": "timeout",
                        "pattern": "timeout|超时",
                        "severity": "warning",
                        "description": "检测超时问题",
                    },
                ],
            }
        },
        "notifiers": {
            "cli_notifier": {
                "type": "cli",
                "use_color": True,
                "output_format": "text"
            },
            "admin_email": {
                "type": "email",
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "username": "user@example.com",
                "password": "password",
                "sender": "alerts@example.com",
                "recipients": ["admin@example.com"],
                "use_tls": True,
                "html_format": True,
            }
        },
        "notification_rules": {
            "error_alert": {
                "analyzer": "error_analyzer",
                "notifier": "cli_notifier",  # 默认使用命令行通知器
                "title": "检测到日志错误",
                "message": "共检测到 {matched_logs} 条错误日志，其中包括 {error_count} 个错误和 {warning_count} 个警告。",
                "condition": {
                    "type": "threshold",
                    "field": "summary.matched_logs",
                    "operator": ">",
                    "value": 0,
                },
            }
        },
        "plugins": [],
    }

    try:
        # 保存配置文件
        file_format = args.format.lower()
        file_ext = ".json" if file_format == "json" else ".yaml"

        if not args.output.endswith(file_ext):
            output_path = args.output + file_ext
        else:
            output_path = args.output

        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            if file_format == "json":
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"配置文件已生成: {output_path}")
        return 0

    except Exception as e:
        print(f"生成配置文件失败: {e}")
        return 1


def handle_list(args: argparse.Namespace) -> int:
    """
    处理list命令，列出可用的插件

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    # 初始化插件注册表
    from statis_log.core import StatisLog

    StatisLog()._load_plugins()

    # 根据类型列出插件
    plugin_type = args.type.lower()

    if plugin_type in ("collector", "all"):
        collectors = collector_registry.list_plugins()
        print("\n可用的收集器:")
        for collector in collectors:
            print(f"  - {collector}")

    if plugin_type in ("analyzer", "all"):
        analyzers = analyzer_registry.list_plugins()
        print("\n可用的分析器:")
        for analyzer in analyzers:
            print(f"  - {analyzer}")

    if plugin_type in ("notifier", "all"):
        notifiers = notifier_registry.list_plugins()
        print("\n可用的通知器:")
        for notifier in notifiers:
            print(f"  - {notifier}")

    return 0


def handle_validate(args: argparse.Namespace) -> int:
    """
    处理validate命令，验证配置文件

    Args:
        args: 命令行参数

    Returns:
        退出码
    """
    try:
        # 加载配置
        config = load_config(args.config)
        if not config:
            print(f"配置文件无效或为空: {args.config}")
            return 1

        # 验证基本结构
        required_sections = [
            "collectors",
            "analyzers",
            "notifiers",
            "notification_rules",
        ]
        missing_sections = [
            section for section in required_sections if section not in config
        ]

        if missing_sections:
            print(f"配置文件缺少以下必要部分: {', '.join(missing_sections)}")
            return 1

        # 验证组件配置
        for name, collector_config in config.get("collectors", {}).items():
            if "type" not in collector_config:
                print(f"收集器 '{name}' 缺少 'type' 字段")
                return 1

        for name, analyzer_config in config.get("analyzers", {}).items():
            if "type" not in analyzer_config:
                print(f"分析器 '{name}' 缺少 'type' 字段")
                return 1

        for name, notifier_config in config.get("notifiers", {}).items():
            if "type" not in notifier_config:
                print(f"通知器 '{name}' 缺少 'type' 字段")
                return 1

        # 验证通知规则
        for name, rule_config in config.get("notification_rules", {}).items():
            if "analyzer" not in rule_config:
                print(f"通知规则 '{name}' 缺少 'analyzer' 字段")
                return 1
            if "notifier" not in rule_config:
                print(f"通知规则 '{name}' 缺少 'notifier' 字段")
                return 1

            # 检查引用的分析器和通知器是否存在
            analyzer_name = rule_config["analyzer"]
            if analyzer_name not in config.get("analyzers", {}):
                print(f"通知规则 '{name}' 引用了不存在的分析器: {analyzer_name}")
                return 1

            notifier_name = rule_config["notifier"]
            if notifier_name not in config.get("notifiers", {}):
                print(f"通知规则 '{name}' 引用了不存在的通知器: {notifier_name}")
                return 1

        print(f"配置文件验证通过: {args.config}")
        return 0

    except Exception as e:
        print(f"验证配置文件失败: {e}")
        return 1


def main() -> int:
    """
    命令行工具主函数

    Returns:
        退出码
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # 处理版本信息
    if args.version:
        print(f"statis_log 版本: {__version__}")
        return 0

    if not args.command:
        parser.print_help()
        return 1

    # 根据命令调用相应的处理函数
    if args.command == "run":
        return handle_run(args)
    elif args.command == "init":
        return handle_init(args)
    elif args.command == "list":
        return handle_list(args)
    elif args.command == "validate":
        return handle_validate(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

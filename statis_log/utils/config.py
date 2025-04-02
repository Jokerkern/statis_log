"""
配置管理工具

提供配置加载和保存功能
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径，支持JSON和YAML格式

    Returns:
        配置字典
    """
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在: {config_path}")
        return {}

    try:
        file_ext = os.path.splitext(config_path)[1].lower()

        with open(config_path, "r", encoding="utf-8") as f:
            if file_ext in [".yml", ".yaml"]:
                config = yaml.safe_load(f)
            elif file_ext == ".json":
                config = json.load(f)
            else:
                logger.error(f"不支持的配置文件格式: {file_ext}")
                return {}

        logger.info(f"成功加载配置文件: {config_path}")
        return config or {}

    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {}


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    保存配置到文件

    Args:
        config: 配置字典
        config_path: 配置文件路径

    Returns:
        保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)

        file_ext = os.path.splitext(config_path)[1].lower()

        with open(config_path, "w", encoding="utf-8") as f:
            if file_ext in [".yml", ".yaml"]:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            elif file_ext == ".json":
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                logger.error(f"不支持的配置文件格式: {file_ext}")
                return False

        logger.info(f"成功保存配置到文件: {config_path}")
        return True

    except Exception as e:
        logger.error(f"保存配置到文件失败: {e}")
        return False


def merge_configs(
    base_config: Dict[str, Any], override_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    合并配置，override_config中的值会覆盖base_config中的值

    Args:
        base_config: 基础配置
        override_config: 覆盖配置

    Returns:
        合并后的配置
    """
    merged = base_config.copy()

    for key, value in override_config.items():
        # 如果两个配置中都有同名的字典，则递归合并
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value

    return merged

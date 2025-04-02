"""
日志收集器基类

提供日志收集器的基本接口和功能
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """日志收集器基类"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化收集器

        Args:
            name: 收集器名称
            config: 收集器配置
        """
        self.name = name
        self.config = config or {}
        logger.debug(f"初始化收集器 {name}")

    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """
        执行日志收集操作

        Returns:
            收集到的日志列表
        """
        pass

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            配置是否有效
        """
        return True

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

"""
通知器基类

提供通知器的基本接口和功能
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class BaseNotifier(ABC):
    """通知器基类"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化通知器

        Args:
            name: 通知器名称
            config: 通知器配置
        """
        self.name = name
        self.config = config or {}
        logger.debug(f"初始化通知器 {name}")

    @abstractmethod
    def notify(
        self, title: str, message: str, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送通知

        Args:
            title: 通知标题
            message: 通知内容
            data: 附加数据

        Returns:
            发送结果
        """
        pass

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            配置是否有效
        """
        return True

    def format_message(self, template: str, data: Dict[str, Any]) -> str:
        """
        根据模板和数据格式化消息

        Args:
            template: 消息模板
            data: 数据字典

        Returns:
            格式化后的消息
        """
        try:
            return template.format(**data)
        except KeyError as e:
            logger.error(f"格式化消息失败，缺少键: {e}")
            return template
        except Exception as e:
            logger.error(f"格式化消息失败: {e}")
            return template

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

"""
日志分析器基类

提供日志分析器的基本接口和功能
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """日志分析器基类"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化分析器
        
        Args:
            name: 分析器名称
            config: 分析器配置
        """
        self.name = name
        self.config = config or {}
        logger.debug(f"初始化分析器 {name}")
    
    @abstractmethod
    def analyze(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行日志分析操作
        
        Args:
            logs: 待分析的日志列表
            
        Returns:
            分析结果
        """
        pass
    
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
        """
        return True
    
    def preprocess(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        预处理日志数据
        
        Args:
            logs: 原始日志数据
            
        Returns:
            预处理后的日志数据
        """
        return logs
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})" 
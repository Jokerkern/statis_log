"""
插件工具模块

提供插件注册和管理的工具函数和装饰器
"""

import logging
from typing import Any, Callable, Dict, Type, TypeVar

from statis_log.core import collector_registry, analyzer_registry, notifier_registry
from statis_log.collectors.base import BaseCollector
from statis_log.analyzers.base import BaseAnalyzer
from statis_log.notifiers.base import BaseNotifier

logger = logging.getLogger(__name__)

T = TypeVar('T')


def collector(name: str) -> Callable[[Type[BaseCollector]], Type[BaseCollector]]:
    """
    注册收集器插件的装饰器
    
    Args:
        name: 收集器名称
        
    Returns:
        装饰器函数
    """
    def decorator(cls: Type[BaseCollector]) -> Type[BaseCollector]:
        collector_registry.register(name, cls)
        return cls
    return decorator


def analyzer(name: str) -> Callable[[Type[BaseAnalyzer]], Type[BaseAnalyzer]]:
    """
    注册分析器插件的装饰器
    
    Args:
        name: 分析器名称
        
    Returns:
        装饰器函数
    """
    def decorator(cls: Type[BaseAnalyzer]) -> Type[BaseAnalyzer]:
        analyzer_registry.register(name, cls)
        return cls
    return decorator


def notifier(name: str) -> Callable[[Type[BaseNotifier]], Type[BaseNotifier]]:
    """
    注册通知器插件的装饰器
    
    Args:
        name: 通知器名称
        
    Returns:
        装饰器函数
    """
    def decorator(cls: Type[BaseNotifier]) -> Type[BaseNotifier]:
        notifier_registry.register(name, cls)
        return cls
    return decorator


def register_plugin(plugin_type: str, name: str) -> Callable[[Type[T]], Type[T]]:
    """
    通用插件注册装饰器
    
    Args:
        plugin_type: 插件类型 (collector, analyzer, notifier)
        name: 插件名称
        
    Returns:
        装饰器函数
    """
    def decorator(cls: Type[T]) -> Type[T]:
        if plugin_type == "collector":
            if not issubclass(cls, BaseCollector):
                logger.warning(f"插件类型错误: {cls.__name__} 不是 BaseCollector 的子类")
                return cls
            collector_registry.register(name, cls)
        elif plugin_type == "analyzer":
            if not issubclass(cls, BaseAnalyzer):
                logger.warning(f"插件类型错误: {cls.__name__} 不是 BaseAnalyzer 的子类")
                return cls
            analyzer_registry.register(name, cls)
        elif plugin_type == "notifier":
            if not issubclass(cls, BaseNotifier):
                logger.warning(f"插件类型错误: {cls.__name__} 不是 BaseNotifier 的子类")
                return cls
            notifier_registry.register(name, cls)
        else:
            logger.error(f"未知的插件类型: {plugin_type}")
        return cls
    return decorator


def discover_plugins(module_path: str) -> None:
    """
    自动发现并加载指定模块中的插件
    
    Args:
        module_path: 模块路径
    """
    try:
        __import__(module_path)
        logger.info(f"已加载插件模块: {module_path}")
    except ImportError as e:
        logger.error(f"加载插件模块失败: {module_path} - {e}") 
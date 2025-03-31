"""
日志配置工具

提供日志设置和配置功能
"""

import os
import logging
import logging.config
from typing import Dict, Any, Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    log_date_format: Optional[str] = None,
    log_console: bool = True,
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则不写入文件
        log_format: 日志格式
        log_date_format: 日期格式
        log_console: 是否输出到控制台
        
    Returns:
        根日志记录器
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 设置默认格式
    if not log_format:
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    if not log_date_format:
        log_date_format = "%Y-%m-%d %H:%M:%S"
    
    # 创建日志配置
    handlers = []
    
    if log_console:
        handlers.append("console")
    
    if log_file:
        handlers.append("file")
        # 确保日志目录存在
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": log_date_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": numeric_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # 根日志记录器
                "handlers": handlers,
                "level": numeric_level,
                "propagate": True,
            },
            "statis_log": {  # 程序日志记录器
                "handlers": handlers,
                "level": numeric_level,
                "propagate": False,
            },
        }
    }
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": numeric_level,
            "formatter": "standard",
            "filename": log_file,
            "encoding": "utf-8",
        }
    
    # 应用配置
    logging.config.dictConfig(config)
    
    return logging.getLogger()


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name) 
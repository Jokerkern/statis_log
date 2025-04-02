"""
文件日志收集器

从文件系统收集日志文件
"""

import os
import re
import glob
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Pattern

from .base import BaseCollector
from statis_log.utils.plugin import collector

logger = logging.getLogger(__name__)


@collector("file")
class FileCollector(BaseCollector):
    """文件日志收集器，从文件系统收集日志"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化文件收集器
        
        Args:
            name: 收集器名称
            config: 收集器配置，必须包含 'path' 和 'pattern' 字段
                path: 日志文件路径
                pattern: 日志文件名匹配模式，支持glob格式
                content_filter: 日志内容过滤正则表达式（可选）
                max_size: 单个文件最大处理大小，单位MB（可选）
                encoding: 文件编码（可选，默认utf-8）
        """
        super().__init__(name, config)
        self.path = self.config.get('path')
        self.pattern = self.config.get('pattern')
        self.content_filter = self.config.get('content_filter')
        self.max_size = self.config.get('max_size', 100)  # 默认100MB
        self.encoding = self.config.get('encoding', 'utf-8')
        
        # 编译正则表达式
        self._content_regex = None
        if self.content_filter:
            try:
                self._content_regex = re.compile(self.content_filter)
            except re.error as e:
                logger.error(f"正则表达式编译失败: {e}")
                
    def validate_config(self) -> bool:
        """验证配置有效性"""
        if not self.path:
            logger.error("缺少必要的配置: path")
            return False
        if not self.pattern:
            logger.error("缺少必要的配置: pattern")
            return False
        if not os.path.exists(self.path):
            logger.error(f"路径不存在: {self.path}")
            return False
        return True
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        收集符合条件的日志文件内容
        
        Returns:
            日志记录列表，每条包含文件名、行号、内容等信息
        """
        if not self.validate_config():
            return []
            
        results = []
        file_pattern = os.path.join(self.path, self.pattern)
        matching_files = glob.glob(file_pattern)
        
        for file_path in matching_files:
            try:
                file_logs = self._process_file(file_path)
                results.extend(file_logs)
            except Exception as e:
                logger.error(f"处理文件失败 {file_path}: {e}")
                
        return results
    
    def _process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """处理单个日志文件"""
        file_logs = []
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > self.max_size:
            logger.warning(f"文件大小超过限制 {file_path}: {file_size_mb}MB > {self.max_size}MB")
            return []
            
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                for line_num, line in enumerate(f, 1):
                    # 如果有内容过滤器，检查行是否匹配
                    if self._content_regex and not self._content_regex.search(line):
                        continue
                        
                    log_entry = {
                        'source': self.name,
                        'file': file_path,
                        'line': line_num,
                        'content': line.strip(),
                        'timestamp': datetime.now().isoformat(),
                    }
                    file_logs.append(log_entry)
        except UnicodeDecodeError:
            logger.error(f"文件编码错误 {file_path}，请检查编码设置")
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            
        return file_logs 
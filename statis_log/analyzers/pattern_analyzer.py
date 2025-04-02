"""
模式匹配分析器

根据预定义的模式规则分析日志内容
"""

import re
import logging
from typing import Any, Dict, List, Optional, Pattern

from .base import BaseAnalyzer
from statis_log.utils.plugin import analyzer

logger = logging.getLogger(__name__)


class PatternRule:
    """模式匹配规则"""
    
    def __init__(self, name: str, pattern: str, severity: str = "info", description: str = ""):
        """
        初始化匹配规则
        
        Args:
            name: 规则名称
            pattern: 正则表达式模式
            severity: 严重程度 (info, warning, error, critical)
            description: 规则描述
        """
        self.name = name
        self.pattern_str = pattern
        self.severity = severity
        self.description = description
        
        # 编译正则表达式
        try:
            self.pattern = re.compile(pattern)
        except re.error as e:
            logger.error(f"规则 '{name}' 的正则表达式编译失败: {e}")
            self.pattern = None
    
    def match(self, text: str) -> bool:
        """检查文本是否匹配规则"""
        if not self.pattern:
            return False
        return bool(self.pattern.search(text))
    
    def to_dict(self) -> Dict[str, str]:
        """将规则转换为字典"""
        return {
            'name': self.name,
            'pattern': self.pattern_str,
            'severity': self.severity,
            'description': self.description
        }


@analyzer("pattern")
class PatternAnalyzer(BaseAnalyzer):
    """
    模式分析器，根据预定义规则分析日志
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化模式分析器
        
        Args:
            name: 分析器名称
            config: 分析器配置，可包含以下字段:
                rules: 规则列表，每个规则包含 name, pattern, severity, description
                content_field: 日志中包含内容的字段名 (默认: content)
        """
        super().__init__(name, config)
        self.rules = []
        self.content_field = self.config.get('content_field', 'content')
        
        # 初始化规则
        rules_config = self.config.get('rules', [])
        for rule_config in rules_config:
            rule = PatternRule(
                name=rule_config.get('name', '未命名规则'),
                pattern=rule_config.get('pattern', ''),
                severity=rule_config.get('severity', 'info'),
                description=rule_config.get('description', '')
            )
            
            if rule.pattern:  # 只添加正则表达式有效的规则
                self.rules.append(rule)
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        if not self.rules:
            logger.warning(f"分析器 {self.name} 没有有效的规则配置")
            return False
        return True
    
    def analyze(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析日志内容，查找匹配的模式
        
        Args:
            logs: 日志列表
            
        Returns:
            分析结果，包含匹配规则和对应日志
        """
        if not self.validate_config():
            return {'matches': [], 'summary': {}}
        
        matches = []
        rule_match_counts = {rule.name: 0 for rule in self.rules}
        severity_counts = {'info': 0, 'warning': 0, 'error': 0, 'critical': 0}
        
        for log in logs:
            if self.content_field not in log:
                continue
                
            content = log.get(self.content_field, '')
            log_matches = []
            
            for rule in self.rules:
                if rule.match(content):
                    log_matches.append(rule.name)
                    rule_match_counts[rule.name] += 1
                    severity_counts[rule.severity] += 1
            
            if log_matches:
                match_entry = {
                    'log': log,
                    'rules': log_matches
                }
                matches.append(match_entry)
        
        # 生成分析摘要
        summary = {
            'total_logs': len(logs),
            'matched_logs': len(matches),
            'rule_matches': rule_match_counts,
            'severity_counts': severity_counts,
        }
        
        return {
            'matches': matches,
            'summary': summary
        } 
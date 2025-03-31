"""
核心功能模块

提供日志收集、分析和通知的集成功能
"""

import os
import time
import logging
import importlib
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic

from statis_log.collectors.base import BaseCollector
from statis_log.analyzers.base import BaseAnalyzer
from statis_log.notifiers.base import BaseNotifier
from statis_log.utils.config import load_config, merge_configs

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PluginRegistry(Generic[T]):
    """插件注册表，用于管理各类插件"""
    
    def __init__(self):
        self._registry = {}
    
    def register(self, name: str, plugin_class: Type[T]) -> None:
        """注册插件类"""
        if name in self._registry:
            logger.warning(f"覆盖已存在的插件: {name}")
        self._registry[name] = plugin_class
        logger.debug(f"注册插件: {name} -> {plugin_class.__name__}")
    
    def get(self, name: str) -> Optional[Type[T]]:
        """获取插件类"""
        if name not in self._registry:
            logger.error(f"插件不存在: {name}")
            return None
        return self._registry[name]
    
    def list_plugins(self) -> List[str]:
        """获取所有已注册的插件名称列表"""
        return list(self._registry.keys())


# 全局插件注册表
collector_registry = PluginRegistry[BaseCollector]()
analyzer_registry = PluginRegistry[BaseAnalyzer]()
notifier_registry = PluginRegistry[BaseNotifier]()


class StatisLog:
    """日志统计分析主类"""
    
    def __init__(self, config_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        初始化日志统计分析器
        
        Args:
            config_path: 配置文件路径
            config: 直接提供的配置字典，会覆盖配置文件中的同名配置
        """
        self.config = {}
        
        # 加载配置
        if config_path and os.path.exists(config_path):
            file_config = load_config(config_path)
            self.config = file_config
            
        # 合并直接提供的配置
        if config:
            self.config = merge_configs(self.config, config)
        
        # 初始化组件
        self.collectors = {}
        self.analyzers = {}
        self.notifiers = {}
        
        # 加载插件
        self._load_plugins()
        
        # 初始化组件
        self._init_components()
    
    def _load_plugins(self) -> None:
        """加载内置和自定义插件"""
        # 注册内置收集器
        from statis_log.collectors.file_collector import FileCollector
        collector_registry.register("file", FileCollector)
        
        # 注册内置分析器
        from statis_log.analyzers.pattern_analyzer import PatternAnalyzer
        analyzer_registry.register("pattern", PatternAnalyzer)
        
        # 注册内置通知器
        from statis_log.notifiers.email_notifier import EmailNotifier
        notifier_registry.register("email", EmailNotifier)
        
        # 加载自定义插件
        custom_plugins = self.config.get("plugins", [])
        for plugin_path in custom_plugins:
            try:
                importlib.import_module(plugin_path)
                logger.info(f"加载自定义插件: {plugin_path}")
            except ImportError as e:
                logger.error(f"加载自定义插件失败: {plugin_path} - {e}")
    
    def _init_components(self) -> None:
        """初始化收集器、分析器和通知器"""
        # 初始化收集器
        collectors_config = self.config.get("collectors", {})
        for name, config in collectors_config.items():
            collector_type = config.get("type")
            if not collector_type:
                logger.error(f"收集器配置缺少类型: {name}")
                continue
                
            collector_class = collector_registry.get(collector_type)
            if not collector_class:
                logger.error(f"未知的收集器类型: {collector_type}")
                continue
                
            try:
                collector = collector_class(name, config)
                self.collectors[name] = collector
                logger.info(f"初始化收集器: {name} ({collector_type})")
            except Exception as e:
                logger.error(f"初始化收集器失败: {name} - {e}")
        
        # 初始化分析器
        analyzers_config = self.config.get("analyzers", {})
        for name, config in analyzers_config.items():
            analyzer_type = config.get("type")
            if not analyzer_type:
                logger.error(f"分析器配置缺少类型: {name}")
                continue
                
            analyzer_class = analyzer_registry.get(analyzer_type)
            if not analyzer_class:
                logger.error(f"未知的分析器类型: {analyzer_type}")
                continue
                
            try:
                analyzer = analyzer_class(name, config)
                self.analyzers[name] = analyzer
                logger.info(f"初始化分析器: {name} ({analyzer_type})")
            except Exception as e:
                logger.error(f"初始化分析器失败: {name} - {e}")
        
        # 初始化通知器
        notifiers_config = self.config.get("notifiers", {})
        for name, config in notifiers_config.items():
            notifier_type = config.get("type")
            if not notifier_type:
                logger.error(f"通知器配置缺少类型: {name}")
                continue
                
            notifier_class = notifier_registry.get(notifier_type)
            if not notifier_class:
                logger.error(f"未知的通知器类型: {notifier_type}")
                continue
                
            try:
                notifier = notifier_class(name, config)
                self.notifiers[name] = notifier
                logger.info(f"初始化通知器: {name} ({notifier_type})")
            except Exception as e:
                logger.error(f"初始化通知器失败: {name} - {e}")
    
    def run(self) -> Dict[str, Any]:
        """
        执行完整的日志收集、分析和通知流程
        
        Returns:
            运行结果摘要
        """
        start_time = time.time()
        
        # 收集日志
        logs = self.collect_logs()
        
        # 分析日志
        results = self.analyze_logs(logs)
        
        # 发送通知
        notifications = self.send_notifications(results)
        
        end_time = time.time()
        
        # 生成运行摘要
        summary = {
            "status": "success",
            "execution_time": end_time - start_time,
            "logs_collected": len(logs),
            "analysis_count": len(results),
            "notification_count": len(notifications),
            "collectors": list(self.collectors.keys()),
            "analyzers": list(self.analyzers.keys()),
            "notifiers": list(self.notifiers.keys()),
        }
        
        logger.info(f"运行完成: 收集 {len(logs)} 条日志, 分析 {len(results)} 个结果, 发送 {len(notifications)} 个通知")
        return summary
    
    def collect_logs(self) -> List[Dict[str, Any]]:
        """
        从所有收集器收集日志
        
        Returns:
            收集到的所有日志
        """
        all_logs = []
        
        for name, collector in self.collectors.items():
            try:
                logger.info(f"开始收集日志: {name}")
                logs = collector.collect()
                logger.info(f"收集日志完成: {name}, 获取 {len(logs)} 条记录")
                all_logs.extend(logs)
            except Exception as e:
                logger.error(f"收集日志失败: {name} - {e}")
        
        logger.info(f"总共收集 {len(all_logs)} 条日志记录")
        return all_logs
    
    def analyze_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        使用所有分析器分析日志
        
        Args:
            logs: 收集到的日志列表
            
        Returns:
            分析结果字典，以分析器名称为键
        """
        results = {}
        
        for name, analyzer in self.analyzers.items():
            try:
                logger.info(f"开始分析日志: {name}")
                result = analyzer.analyze(logs)
                logger.info(f"分析日志完成: {name}")
                results[name] = result
            except Exception as e:
                logger.error(f"分析日志失败: {name} - {e}")
        
        return results
    
    def send_notifications(self, results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据分析结果发送通知
        
        Args:
            results: 分析结果，以分析器名称为键
            
        Returns:
            通知发送结果
        """
        notifications = []
        
        notification_config = self.config.get("notification_rules", {})
        
        for rule_name, rule in notification_config.items():
            # 从规则中获取通知器、分析器和条件
            notifier_name = rule.get("notifier")
            analyzer_name = rule.get("analyzer")
            condition = rule.get("condition", {})
            
            if not notifier_name or not analyzer_name:
                logger.error(f"通知规则配置不完整: {rule_name}")
                continue
            
            if notifier_name not in self.notifiers:
                logger.error(f"通知规则使用了未知的通知器: {notifier_name}")
                continue
                
            if analyzer_name not in results:
                logger.warning(f"通知规则使用了没有结果的分析器: {analyzer_name}")
                continue
                
            # 获取分析结果
            analyzer_result = results[analyzer_name]
            
            # 评估通知条件
            should_notify = self._evaluate_notification_condition(analyzer_result, condition)
            
            if should_notify:
                notifier = self.notifiers[notifier_name]
                
                # 格式化通知内容
                title = rule.get("title", f"日志分析通知: {analyzer_name}")
                message_template = rule.get("message", "检测到 {matched_logs} 条匹配的日志")
                
                # 准备通知数据
                notification_data = {
                    "rule_name": rule_name,
                    "analyzer_name": analyzer_name,
                    "result": analyzer_result,
                    **self._extract_notification_data(analyzer_result)
                }
                
                # 发送通知
                try:
                    success = notifier.notify(title, message_template, notification_data)
                    notification_result = {
                        "rule": rule_name,
                        "notifier": notifier_name,
                        "success": success,
                        "timestamp": time.time()
                    }
                    notifications.append(notification_result)
                    
                    if success:
                        logger.info(f"通知发送成功: {rule_name} -> {notifier_name}")
                    else:
                        logger.error(f"通知发送失败: {rule_name} -> {notifier_name}")
                        
                except Exception as e:
                    logger.error(f"发送通知异常: {rule_name} -> {notifier_name} - {e}")
        
        return notifications
    
    def _evaluate_notification_condition(self, result: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """评估是否应该发送通知"""
        # 如果没有条件，默认发送通知
        if not condition:
            return True
            
        # 支持多种条件类型
        condition_type = condition.get("type", "threshold")
        
        if condition_type == "threshold":
            # 阈值条件，例如匹配日志数超过某个值
            field = condition.get("field", "matched_logs")
            operator = condition.get("operator", ">")
            value = condition.get("value", 0)
            
            # 从结果中提取字段值
            field_value = None
            
            # 处理嵌套字段，例如 summary.matched_logs
            if "." in field:
                parts = field.split(".")
                field_obj = result
                for part in parts:
                    if isinstance(field_obj, dict) and part in field_obj:
                        field_obj = field_obj[part]
                    else:
                        logger.warning(f"条件中的字段不存在: {field}")
                        return False
                field_value = field_obj
            else:
                field_value = result.get(field)
                if field_value is None and "summary" in result:
                    field_value = result["summary"].get(field)
            
            if field_value is None:
                logger.warning(f"找不到条件字段的值: {field}")
                return False
                
            # 评估条件
            if operator == ">":
                return field_value > value
            elif operator == ">=":
                return field_value >= value
            elif operator == "<":
                return field_value < value
            elif operator == "<=":
                return field_value <= value
            elif operator == "==":
                return field_value == value
            elif operator == "!=":
                return field_value != value
            else:
                logger.warning(f"不支持的条件操作符: {operator}")
                return False
                
        elif condition_type == "presence":
            # 存在性条件，检查某个字段是否存在
            field = condition.get("field", "")
            exists = condition.get("exists", True)
            
            field_exists = False
            if "." in field:
                parts = field.split(".")
                field_obj = result
                for part in parts:
                    if isinstance(field_obj, dict) and part in field_obj:
                        field_obj = field_obj[part]
                    else:
                        field_exists = False
                        break
                else:
                    field_exists = True
            else:
                field_exists = field in result
                if not field_exists and "summary" in result:
                    field_exists = field in result["summary"]
            
            return field_exists == exists
            
        else:
            logger.warning(f"不支持的条件类型: {condition_type}")
            return False
    
    def _extract_notification_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """从分析结果中提取用于通知的数据"""
        data = {}
        
        # 如果结果有摘要，提取关键信息
        if "summary" in result:
            summary = result["summary"]
            if "total_logs" in summary:
                data["total_logs"] = summary["total_logs"]
            if "matched_logs" in summary:
                data["matched_logs"] = summary["matched_logs"]
            
            # 提取严重性计数
            if "severity_counts" in summary:
                for severity, count in summary["severity_counts"].items():
                    data[f"{severity}_count"] = count
        
        # 提取匹配信息
        if "matches" in result:
            data["matches"] = len(result["matches"])
            
            # 提取部分匹配示例
            if result["matches"]:
                sample_size = min(3, len(result["matches"]))
                samples = []
                
                for i in range(sample_size):
                    match = result["matches"][i]
                    if "log" in match and "content" in match["log"]:
                        samples.append(match["log"]["content"])
                        
                data["sample_matches"] = samples
        
        return data 
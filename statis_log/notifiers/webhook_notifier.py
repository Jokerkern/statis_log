"""
Webhook通知器

通过HTTP请求向指定URL发送webhook通知
"""

import json
import logging
from typing import Any, Dict, List, Optional

import requests

from statis_log.utils.plugin import notifier

from .base import BaseNotifier

logger = logging.getLogger(__name__)


@notifier("webhook")
class WebhookNotifier(BaseNotifier):
    """Webhook通知器，支持向指定URL发送HTTP POST请求"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化Webhook通知器

        Args:
            name: 通知器名称
            config: 通知器配置，必须包含以下字段：
                url: Webhook URL地址
                可选字段：
                headers: 请求头信息字典
                timeout: 请求超时时间（秒）
                method: 请求方法，默认为POST
                content_type: 内容类型，默认为application/json
                retry_count: 重试次数，默认为3
                retry_interval: 重试间隔（秒），默认为1
        """
        super().__init__(name, config)
        self.url = self.config.get("url")
        self.headers = self.config.get("headers", {})
        self.timeout = self.config.get("timeout", 10)
        self.method = self.config.get("method", "POST")
        self.content_type = self.config.get("content_type", "application/json")
        self.retry_count = self.config.get("retry_count", 3)
        self.retry_interval = self.config.get("retry_interval", 1)

        # 如果未指定Content-Type，添加默认的Content-Type
        if "Content-Type" not in self.headers and self.content_type:
            self.headers["Content-Type"] = self.content_type

    def validate_config(self) -> bool:
        """验证配置有效性"""
        if not self.url:
            logger.error("缺少必要的配置: url")
            return False
        return True

    def notify(
        self, title: str, message: str, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送Webhook通知

        Args:
            title: 通知标题
            message: 通知内容
            data: 附加数据，可用于格式化消息和构建请求内容

        Returns:
            发送结果
        """
        if not self.validate_config():
            return False

        try:
            # 准备请求数据
            payload = self._prepare_payload(title, message, data or {})

            # 发送请求
            for attempt in range(self.retry_count):
                try:
                    if self.method.upper() == "POST":
                        response = requests.post(
                            self.url,
                            json=payload,
                            headers=self.headers,
                            timeout=self.timeout,
                        )
                    elif self.method.upper() == "GET":
                        response = requests.get(
                            self.url,
                            params=payload,
                            headers=self.headers,
                            timeout=self.timeout,
                        )
                    else:
                        logger.error(f"不支持的请求方法: {self.method}")
                        return False

                    # 检查响应状态
                    if response.status_code >= 200 and response.status_code < 300:
                        logger.info(
                            f"Webhook通知发送成功: {title} (状态码: {response.status_code})"
                        )
                        return True
                    else:
                        logger.warning(
                            f"Webhook通知返回非成功状态码: {response.status_code}, 响应: {response.text}"
                        )

                        # 最后一次尝试失败
                        if attempt == self.retry_count - 1:
                            return False

                        # 等待重试
                        import time

                        time.sleep(self.retry_interval)

                except requests.RequestException as e:
                    logger.warning(f"Webhook请求异常: {e}")

                    # 最后一次尝试失败
                    if attempt == self.retry_count - 1:
                        raise

                    # 等待重试
                    import time

                    time.sleep(self.retry_interval)

            return False

        except Exception as e:
            logger.error(f"Webhook通知发送失败: {e}")
            return False

    def _prepare_payload(
        self, title: str, message: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        准备Webhook请求的数据负载

        Args:
            title: 通知标题
            message: 通知内容
            data: 附加数据

        Returns:
            请求负载数据
        """
        # 处理消息内容
        formatted_message = message
        if data:
            formatted_message = self.format_message(message, data)

        # 基础负载
        payload = {
            "title": title,
            "content": formatted_message,
        }

        # 添加data中的其他字段
        for key, value in data.items():
            if key not in payload:
                payload[key] = value

        # 如果配置中提供了自定义的负载模板，使用它来格式化负载
        payload_template = self.config.get("payload_template")
        if payload_template:
            try:
                # 将当前的payload作为数据，应用模板
                formatted_payload = json.loads(
                    self.format_message(json.dumps(payload_template), payload)
                )
                return formatted_payload
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"格式化负载模板失败: {e}")
                # 如果模板处理失败，返回基本负载

        return payload

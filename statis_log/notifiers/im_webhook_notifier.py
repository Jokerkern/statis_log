"""
4399IM Webhook通知器

专门用于向4399IM发送消息的通知器
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import requests

from statis_log.utils.plugin import notifier

from .base import BaseNotifier

logger = logging.getLogger(__name__)


@notifier("im_webhook")
class IMWebhookNotifier(BaseNotifier):
    """4399IM Webhook通知器，支持向4399IM发送消息"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化4399IM Webhook通知器

        Args:
            name: 通知器名称
            config: 通知器配置，必须包含以下字段：
                url: Webhook URL地址，默认为 https://im-api.4399om.com/message/sendByWebhook
                app_id: 应用ID
                app_secret: 应用密钥
                可选字段：
                sender_id: 发送者ID
                timeout: 请求超时时间（秒），默认为10
                retry_count: 重试次数，默认为3
                retry_interval: 重试间隔（秒），默认为1
        """
        super().__init__(name, config)
        self.url = self.config.get(
            "url", "https://im-api.4399om.com/message/sendByWebhook"
        )
        self.app_id = self.config.get("app_id")
        self.app_secret = self.config.get("app_secret")
        self.sender_id = self.config.get("sender_id", "system")
        self.timeout = self.config.get("timeout", 10)
        self.retry_count = self.config.get("retry_count", 3)
        self.retry_interval = self.config.get("retry_interval", 1)

        # 默认请求头
        self.headers = {"Content-Type": "application/json"}

    def validate_config(self) -> bool:
        """验证配置有效性"""
        if not self.url:
            logger.error("缺少必要的配置: url")
            return False
        if not self.app_id:
            logger.error("缺少必要的配置: app_id")
            return False
        if not self.app_secret:
            logger.error("缺少必要的配置: app_secret")
            return False
        return True

    def notify(
        self, title: str, message: str, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送4399IM消息通知

        Args:
            title: 通知标题
            message: 通知内容
            data: 附加数据，可用于格式化消息和构建请求内容
                可包含以下字段:
                receiver_type: 接收者类型，可以是"user"或"group"，默认为"user"
                receiver_id: 接收者ID，必须指定
                message_type: 消息类型，可以是text, markdown, picture, file等，默认为"text"

        Returns:
            发送结果
        """
        if not self.validate_config():
            return False

        data = data or {}

        try:
            # 获取必要的参数
            receiver_type = data.get("receiver_type", "user")
            receiver_id = data.get("receiver_id")
            message_type = data.get("message_type", "text")

            if not receiver_id:
                logger.error("缺少必要的参数: receiver_id")
                return False

            # 准备消息内容
            formatted_message = message
            if data:
                formatted_message = self.format_message(message, data)

            # 构建不同类型的消息内容
            content = {}
            if message_type == "text":
                content = {"text": formatted_message}
            elif message_type == "markdown":
                content = {"content": formatted_message}
            elif message_type == "picture":
                content = {
                    "title": title,
                    "url": data.get("url", ""),
                    "description": formatted_message,
                }
            else:
                # 其他类型的消息使用data中的content字段
                content = data.get("content", {"text": formatted_message})

            # 构建完整的请求负载
            payload = {
                "appId": self.app_id,
                "appSecret": self.app_secret,
                "messageType": message_type,
                "senderId": self.sender_id,
                "receiverType": receiver_type,
                "receiverId": receiver_id,
                "content": content,
            }

            # 发送请求
            for attempt in range(self.retry_count):
                try:
                    response = requests.post(
                        self.url,
                        json=payload,
                        headers=self.headers,
                        timeout=self.timeout,
                    )

                    # 解析响应
                    response_data = response.json()
                    success = response_data.get("status") == "success"

                    if success:
                        logger.info(f"4399IM消息发送成功: {title}")
                        return True
                    else:
                        error_code = response_data.get("code", "unknown")
                        error_msg = response_data.get("msg", "Unknown error")
                        logger.warning(
                            f"4399IM消息发送失败: 错误码={error_code}, 错误信息={error_msg}"
                        )

                        # 最后一次尝试失败
                        if attempt == self.retry_count - 1:
                            return False

                        # 等待重试
                        import time

                        time.sleep(self.retry_interval)

                except Exception as e:
                    logger.warning(f"4399IM请求异常: {e}")

                    # 最后一次尝试失败
                    if attempt == self.retry_count - 1:
                        raise

                    # 等待重试
                    import time

                    time.sleep(self.retry_interval)

            return False

        except Exception as e:
            logger.error(f"4399IM消息发送失败: {e}")
            return False

    def send_text_message(
        self, receiver_id: str, message: str, receiver_type: str = "user"
    ) -> bool:
        """
        发送文本消息

        Args:
            receiver_id: 接收者ID
            message: 消息内容
            receiver_type: 接收者类型，user或group

        Returns:
            发送结果
        """
        data = {
            "receiver_id": receiver_id,
            "receiver_type": receiver_type,
            "message_type": "text",
        }
        return self.notify("文本消息", message, data)

    def send_markdown_message(
        self, receiver_id: str, content: str, receiver_type: str = "user"
    ) -> bool:
        """
        发送Markdown消息

        Args:
            receiver_id: 接收者ID
            content: Markdown内容
            receiver_type: 接收者类型，user或group

        Returns:
            发送结果
        """
        data = {
            "receiver_id": receiver_id,
            "receiver_type": receiver_type,
            "message_type": "markdown",
        }
        return self.notify("Markdown消息", content, data)

    def send_picture_message(
        self,
        receiver_id: str,
        url: str,
        title: str = "",
        description: str = "",
        receiver_type: str = "user",
    ) -> bool:
        """
        发送图片消息

        Args:
            receiver_id: 接收者ID
            url: 图片URL
            title: 图片标题
            description: 图片描述
            receiver_type: 接收者类型，user或group

        Returns:
            发送结果
        """
        data = {
            "receiver_id": receiver_id,
            "receiver_type": receiver_type,
            "message_type": "picture",
            "url": url,
        }
        return self.notify(title, description, data)

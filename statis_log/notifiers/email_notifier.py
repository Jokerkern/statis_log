"""
邮件通知器

通过SMTP发送邮件通知
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, List, Optional

from .base import BaseNotifier

logger = logging.getLogger(__name__)


class EmailNotifier(BaseNotifier):
    """SMTP邮件通知器"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化邮件通知器
        
        Args:
            name: 通知器名称
            config: 通知器配置，必须包含以下字段：
                smtp_server: SMTP服务器地址
                smtp_port: SMTP服务器端口
                username: SMTP用户名
                password: SMTP密码
                sender: 发件人邮箱
                recipients: 收件人邮箱列表
                use_tls: 是否使用TLS加密（可选，默认True）
                html_format: 是否使用HTML格式（可选，默认True）
        """
        super().__init__(name, config)
        self.smtp_server = self.config.get('smtp_server')
        self.smtp_port = self.config.get('smtp_port', 587)
        self.username = self.config.get('username')
        self.password = self.config.get('password')
        self.sender = self.config.get('sender')
        self.recipients = self.config.get('recipients', [])
        self.use_tls = self.config.get('use_tls', True)
        self.html_format = self.config.get('html_format', True)
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        if not self.smtp_server:
            logger.error("缺少必要的配置: smtp_server")
            return False
        if not self.username or not self.password:
            logger.error("缺少必要的配置: username/password")
            return False
        if not self.sender:
            logger.error("缺少必要的配置: sender")
            return False
        if not self.recipients:
            logger.error("缺少必要的配置: recipients")
            return False
        return True
    
    def notify(self, title: str, message: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送邮件通知
        
        Args:
            title: 邮件主题
            message: 邮件内容
            data: 附加数据，可用于格式化消息
            
        Returns:
            发送结果
        """
        if not self.validate_config():
            return False
            
        try:
            # 创建消息对象
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = title
            
            # 处理消息内容
            formatted_message = message
            if data:
                formatted_message = self.format_message(message, data)
                
            # 设置消息类型
            content_type = 'html' if self.html_format else 'plain'
            msg.attach(MIMEText(formatted_message, content_type, 'utf-8'))
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
            logger.info(f"邮件通知发送成功: {title}")
            return True
            
        except Exception as e:
            logger.error(f"邮件通知发送失败: {e}")
            return False 
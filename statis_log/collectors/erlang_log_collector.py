"""
Erlang日志收集器

从多个Erlang节点收集日志，首先通过登录服获取服务器列表，然后从各服务器收集日志文件
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from statis_log.utils.erlang import call
from statis_log.utils.plugin import collector

from .base import BaseCollector

logger = logging.getLogger(__name__)


@collector("erlang_log")
class ErlangLogCollector(BaseCollector):
    """Erlang日志收集器，从多个Erlang节点收集日志"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化Erlang日志收集器

        Args:
            name: 收集器名称
            config: 收集器配置，必须包含:
                login_node: 登录服节点名称（用于获取服务器列表）
                login_cookie: 登录服的Erlang cookie
                log_dir: 日志目录路径
                log_pattern: 日志文件名匹配模式
                server_cookie: 服务器的Erlang cookie（如果与login_cookie不同）
                server_prefix: 游戏服前缀，用于构建服务器节点名称
                content_filter: 日志内容过滤正则表达式（可选）
                max_size: 单个文件最大处理大小，单位MB（可选）
                encoding: 文件编码（可选，默认utf-8）
        """
        super().__init__(name, config)
        self.login_node = self.config.get("login_node")
        self.login_cookie = self.config.get("login_cookie")
        self.log_dir = self.config.get("log_dir")
        self.log_pattern = self.config.get("log_pattern")
        self.server_list_module = self.config.get("server_list_module")
        self.server_list_function = self.config.get("server_list_function", "get_server_list")
        self.server_cookie = self.config.get("server_cookie", self.login_cookie)
        self.server_prefix = self.config.get("server_prefix", "")
        self.content_filter = self.config.get("content_filter")
        self.max_size = self.config.get("max_size", 100)  # 默认100MB
        self.encoding = self.config.get("encoding", "utf-8")

    def validate_config(self) -> bool:
        """验证配置有效性"""
        if not self.login_node:
            logger.error("缺少必要的配置: login_node")
            return False
        if not self.login_cookie:
            logger.error("缺少必要的配置: login_cookie")
            return False
        if not self.log_dir:
            logger.error("缺少必要的配置: log_dir")
            return False
        if not self.log_pattern:
            logger.error("缺少必要的配置: log_pattern")
            return False
        if not self.server_list_module:
            logger.error("缺少必要的配置: server_list_module")
            return False
        
        # server_prefix是可选的，但如果提供了，记录相关信息
        if self.server_prefix:
            logger.info(f"将使用服务器前缀: {self.server_prefix}")
            
        return True

    def collect(self) -> List[Dict[str, Any]]:
        """
        从Erlang服务器收集日志

        Returns:
            日志记录列表，每条包含服务器、文件名、行号、内容等信息
        """
        if not self.validate_config():
            return []

        results = []
        
        # 获取服务器列表
        servers = self._get_server_list()
        if not servers:
            logger.error("无法获取服务器列表")
            return []
            
        logger.info(f"成功获取服务器列表，共{len(servers)}个服务器")
        
        # 从每个服务器收集日志
        for server in servers:
            server_logs = self._collect_from_server(server)
            results.extend(server_logs)
            
        return results
        
    def _get_server_list(self) -> List[str]:
        """
        从登录服获取服务器列表
        
        Returns:
            服务器节点名称列表
        """
        try:
            logger.info(f"正在从登录服 {self.login_node} 获取服务器列表")
            result = call(
                node=self.login_node,
                module=self.server_list_module,
                function=self.server_list_function,
                cookie=self.login_cookie
            )
            
            # 解析返回的服务器列表
            # 结果可能是类似 ['server1@host', 'server2@host', ...] 或 [{"id": 1, "ip": "192.168.1.1"}, ...]
            servers = []
            try:
                # 去除返回值中的方括号和引号，然后按逗号分割
                cleaned_result = result.strip("[]' ").replace("'", "").replace("\"", "")
                if cleaned_result:
                    raw_servers = [s.strip() for s in cleaned_result.split(",")]
                    
                    # 如果指定了服务器前缀，则使用前缀+服号+@+IP构建节点名
                    if self.server_prefix:
                        for srv in raw_servers:
                            # 尝试解析服务器ID和IP
                            if "{" in srv and "}" in srv:
                                # 解析JSON/字典格式的服务器信息
                                try:
                                    # 格式可能类似 {id:1,ip:192.168.1.1} 或 {id:1,host:192.168.1.1}
                                    parts = srv.strip("{}").split(",")
                                    server_data = {}
                                    for part in parts:
                                        key, value = part.split(":", 1)
                                        server_data[key.strip()] = value.strip()
                                    
                                    server_id = server_data.get("id")
                                    server_ip = server_data.get("ip") or server_data.get("host")
                                    
                                    if server_id and server_ip:
                                        node_name = f"{self.server_prefix}{server_id}@{server_ip}"
                                        servers.append(node_name)
                                except Exception as e:
                                    logger.error(f"解析服务器信息失败: {e}, 原始数据: {srv}")
                            else:
                                # 尝试从现有格式中提取信息
                                if "@" in srv:
                                    srv_parts = srv.split("@")
                                    if len(srv_parts) == 2:
                                        srv_name, srv_ip = srv_parts
                                        # 尝试从服务器名中提取ID
                                        import re
                                        id_match = re.search(r'\d+', srv_name)
                                        if id_match:
                                            server_id = id_match.group()
                                            node_name = f"{self.server_prefix}{server_id}@{srv_ip}"
                                            servers.append(node_name)
                                        else:
                                            # 如果无法提取ID，则保留原始格式
                                            servers.append(srv)
                                    else:
                                        servers.append(srv)
                                else:
                                    servers.append(srv)
                    else:
                        # 如果没有指定前缀，直接使用原始节点名
                        servers = raw_servers
            except Exception as e:
                logger.error(f"解析服务器列表失败: {e}")
                
            return servers
        except Exception as e:
            logger.error(f"获取服务器列表失败: {e}")
            return []
            
    def _collect_from_server(self, server_node: str) -> List[Dict[str, Any]]:
        """
        从单个服务器收集日志
        
        Args:
            server_node: 服务器节点名称
            
        Returns:
            日志记录列表
        """
        logs = []
        try:
            # 获取远程服务器上的文件列表
            logger.info(f"正在从服务器 {server_node} 获取日志文件列表")
            file_list_result = call(
                node=server_node,
                module="file",
                function="list_dir",
                args=f"[\"{self.log_dir}\"]",
                cookie=self.server_cookie
            )
            
            # 解析文件列表
            files = []
            try:
                # 去除返回值中的方括号和引号，然后按逗号分割
                cleaned_result = file_list_result.strip("[]' ").replace("'", "").replace("\"", "")
                if cleaned_result:
                    files = [s.strip() for s in cleaned_result.split(",")]
                
                # 根据pattern过滤文件
                import fnmatch
                files = [f for f in files if fnmatch.fnmatch(f, self.log_pattern)]
            except Exception as e:
                logger.error(f"解析文件列表失败: {e}")
                return logs
                
            # 处理每个匹配的文件
            for file_name in files:
                file_path = os.path.join(self.log_dir, file_name)
                try:
                    file_logs = self._process_remote_file(server_node, file_path)
                    
                    # 添加服务器节点信息
                    for log in file_logs:
                        log["server"] = server_node
                        
                    logs.extend(file_logs)
                except Exception as e:
                    logger.error(f"处理服务器 {server_node} 上的文件 {file_path} 失败: {e}")
        except Exception as e:
            logger.error(f"从服务器 {server_node} 收集日志失败: {e}")
            
        return logs
        
    def _process_remote_file(self, server_node: str, file_path: str) -> List[Dict[str, Any]]:
        """
        处理远程服务器上的日志文件
        
        Args:
            server_node: 服务器节点名称
            file_path: 文件路径
            
        Returns:
            日志记录列表
        """
        file_logs = []
        
        try:
            # 检查文件大小
            file_size_result = call(
                node=server_node,
                module="filelib",
                function="file_size",
                args=f"[\"{file_path}\"]",
                cookie=self.server_cookie
            )
            
            try:
                file_size = int(file_size_result.strip())
                file_size_mb = file_size / (1024 * 1024)
                
                if file_size_mb > self.max_size:
                    logger.warning(
                        f"文件大小超过限制 {server_node}:{file_path}: {file_size_mb}MB > {self.max_size}MB"
                    )
                    return []
            except Exception as e:
                logger.error(f"检查文件大小失败: {e}")
                return []
                
            # 读取文件内容
            file_content_result = call(
                node=server_node,
                module="file",
                function="read_file",
                args=f"[\"{file_path}\"]",
                cookie=self.server_cookie
            )
            
            # 解析结果，Erlang的file:read_file返回 {ok, Binary} 或 {error, Reason}
            if not file_content_result.startswith("{ok,"):
                logger.error(f"读取文件失败 {server_node}:{file_path}: {file_content_result}")
                return []
                
            # 提取二进制内容并解码
            try:
                content_binary = file_content_result[5:-1]  # 去除 {ok, 和结束的 }
                content = content_binary.decode(self.encoding)
                
                # 按行处理内容
                for line_num, line in enumerate(content.splitlines(), 1):
                    # 如果有内容过滤器，检查行是否匹配
                    if self.content_filter and not line.find(self.content_filter) >= 0:
                        continue
                        
                    log_entry = {
                        "source": self.name,
                        "file": file_path,
                        "line": line_num,
                        "content": line.strip(),
                        "timestamp": datetime.now().isoformat(),
                    }
                    file_logs.append(log_entry)
            except Exception as e:
                logger.error(f"处理文件内容失败: {e}")
        except Exception as e:
            logger.error(f"处理远程文件失败 {server_node}:{file_path}: {e}")
            
        return file_logs 
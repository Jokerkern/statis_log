"""
测试配置模块功能
"""

import os
import json
import pytest
import tempfile
import yaml
from unittest.mock import patch, mock_open

from statis_log.utils.config import load_config, save_config, merge_configs


class TestConfig:
    """测试配置模块功能"""

    def test_load_yaml_config(self):
        """测试加载YAML配置文件"""
        # 模拟YAML配置内容
        yaml_content = """
        collectors:
          file_collector:
            type: file
            path: /var/log/app.log
        analyzers:
          error_analyzer:
            type: pattern
            patterns:
              - ERROR
        """
        
        # 模拟文件存在
        with patch("os.path.exists", return_value=True):
            # 模拟open函数
            with patch("builtins.open", mock_open(read_data=yaml_content)):
                # 加载配置
                config = load_config("config.yaml")
                
                # 验证配置内容
                assert "collectors" in config
                assert "file_collector" in config["collectors"]
                assert config["collectors"]["file_collector"]["type"] == "file"
                assert "analyzers" in config
                assert "error_analyzer" in config["analyzers"]

    def test_load_json_config(self):
        """测试加载JSON配置文件"""
        # 模拟JSON配置内容
        json_content = """
        {
            "collectors": {
                "file_collector": {
                    "type": "file",
                    "path": "/var/log/app.log"
                }
            },
            "analyzers": {
                "error_analyzer": {
                    "type": "pattern",
                    "patterns": ["ERROR"]
                }
            }
        }
        """
        
        # 模拟文件存在
        with patch("os.path.exists", return_value=True):
            # 模拟open函数
            with patch("builtins.open", mock_open(read_data=json_content)):
                # 加载配置
                config = load_config("config.json")
                
                # 验证配置内容
                assert "collectors" in config
                assert "file_collector" in config["collectors"]
                assert config["collectors"]["file_collector"]["type"] == "file"
                assert "analyzers" in config
                assert "error_analyzer" in config["analyzers"]

    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        # 模拟文件不存在
        with patch("os.path.exists", return_value=False):
            # 加载配置
            config = load_config("nonexistent.yaml")
            
            # 验证返回空字典
            assert config == {}

    def test_save_yaml_config(self):
        """测试保存YAML配置"""
        # 准备测试配置
        config = {
            "collectors": {
                "file_collector": {
                    "type": "file",
                    "path": "/var/log/app.log"
                }
            }
        }
        
        # 使用临时文件
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
            temp_path = temp.name
            
        try:
            # 保存配置
            result = save_config(config, temp_path)
            
            # 验证保存成功
            assert result is True
            
            # 验证文件内容
            with open(temp_path, 'r') as f:
                saved_config = yaml.safe_load(f)
                assert saved_config == config
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_json_config(self):
        """测试保存JSON配置"""
        # 准备测试配置
        config = {
            "collectors": {
                "file_collector": {
                    "type": "file",
                    "path": "/var/log/app.log"
                }
            }
        }
        
        # 使用临时文件
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
            temp_path = temp.name
            
        try:
            # 保存配置
            result = save_config(config, temp_path)
            
            # 验证保存成功
            assert result is True
            
            # 验证文件内容
            with open(temp_path, 'r') as f:
                saved_config = json.load(f)
                assert saved_config == config
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_merge_configs(self):
        """测试合并配置"""
        # 基础配置
        base_config = {
            "collectors": {
                "file_collector": {
                    "type": "file",
                    "path": "/var/log/app.log",
                    "enabled": True
                }
            },
            "analyzers": {
                "error_analyzer": {
                    "type": "pattern"
                }
            }
        }
        
        # 覆盖配置
        override_config = {
            "collectors": {
                "file_collector": {
                    "path": "/var/log/new.log"
                },
                "syslog_collector": {
                    "type": "syslog"
                }
            },
            "notifiers": {
                "email": {
                    "type": "email"
                }
            }
        }
        
        # 合并配置
        merged = merge_configs(base_config, override_config)
        
        # 验证合并结果
        assert merged["collectors"]["file_collector"]["type"] == "file"
        assert merged["collectors"]["file_collector"]["path"] == "/var/log/new.log"
        assert merged["collectors"]["file_collector"]["enabled"] is True
        assert "syslog_collector" in merged["collectors"]
        assert "error_analyzer" in merged["analyzers"]
        assert "notifiers" in merged
        assert "email" in merged["notifiers"] 
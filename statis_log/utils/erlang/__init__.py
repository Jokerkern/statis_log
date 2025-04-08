"""
erlang包提供与Erlang节点交互的工具

包含：
- erpc: 用于远程调用Erlang节点的函数
"""

from .erpc import call

__all__ = ['call'] 
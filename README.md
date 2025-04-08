# statis_log

一个工程化的日志收集、分析和通知工具，提供灵活的扩展性。基于Python 3.12开发，使用简单的插件系统实现高度可定制化。

[![Python Version](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 特点

- **模块化设计**：收集器、分析器和通知器完全解耦，可独立扩展
- **日志收集**：从多种来源收集日志，包括文件、数据库、API、Erlang节点等
- **日志分析**：使用多种分析器处理日志内容，识别模式和问题
- **智能通知**：基于分析结果触发条件通知，支持多种通知方式
- **易于扩展**：简单的插件注册机制，便于添加自定义功能
- **配置驱动**：通过YAML配置文件灵活配置所有组件

## 安装

### 使用pip安装

```bash
pip install statis-log
```

### 使用Poetry安装（推荐）

```bash
pip install poetry
poetry add statis-log
```

### 从源码安装

```bash
git clone https://github.com/jokerkern/statis_log.git
cd statis_log
pip install -e .
```

## 快速开始

### 初始化配置文件

```bash
statis-log init -o config.yaml
```

### 验证配置文件

```bash
statis-log validate -c config.yaml
```

### 运行日志分析

```bash
statis-log run -c config.yaml
```

### 查看可用插件

```bash
statis-log list
```

## 配置示例

```yaml
collectors:
  app_logs:
    type: file
    path: /var/log/app
    pattern: "*.log"
    content_filter: "ERROR|WARN"
    max_size: 10
  
  erlang_logs:
    type: erlang
    node_name: my_erlang_node
    cookie: my_cookie
    host: 192.168.1.100
    timeout: 10
    max_logs: 200
    log_path: "/var/log/erlang"

analyzers:
  error_analyzer:
    type: pattern
    content_field: content
    rules:
      - name: exception
        pattern: "Exception|Error|错误|异常"
        severity: error
        description: "检测异常和错误"
      - name: timeout
        pattern: "timeout|超时"
        severity: warning
        description: "检测超时问题"

notifiers:
  admin_email:
    type: email
    smtp_server: smtp.example.com
    smtp_port: 587
    username: user@example.com
    password: password
    sender: alerts@example.com
    recipients:
      - admin@example.com
    use_tls: true
    html_format: true

notification_rules:
  error_alert:
    analyzer: error_analyzer
    notifier: admin_email
    title: "检测到日志错误"
    message: "共检测到 {matched_logs} 条错误日志，其中包括 {error_count} 个错误和 {warning_count} 个警告。"
    condition:
      type: threshold
      field: summary.matched_logs
      operator: ">"
      value: 0
```

## 主要组件

### 收集器 (Collectors)

负责从不同来源收集日志数据：

- **文件收集器**：从本地或远程文件系统读取日志文件
- **Erlang节点收集器**：连接到Erlang节点获取日志数据
- **数据库收集器**：从各种数据库中查询日志记录
- **API收集器**：通过HTTP API获取日志数据
- **自定义收集器**：通过插件系统扩展

### 分析器 (Analyzers)

负责分析日志内容，识别模式和问题：

- **模式分析器**：使用正则表达式识别日志中的特定模式
- **统计分析器**：统计日志中的关键指标
- **异常分析器**：专注于识别和分类异常情况
- **自定义分析器**：通过插件系统扩展

### 通知器 (Notifiers)

负责发送各种形式的通知：

- **邮件通知器**：发送电子邮件通知
- **短信通知器**：发送短信通知
- **WebHook通知器**：调用WebHook URL
- **自定义通知器**：通过插件系统扩展

## 扩展性设计

### 自定义收集器

创建自定义收集器需要继承 `BaseCollector` 类并实现 `collect` 方法：

```python
from statis_log.collectors.base import BaseCollector
from statis_log.core import collector_registry

class MyCustomCollector(BaseCollector):
    def collect(self):
        # 实现自定义收集逻辑
        return logs

# 注册收集器
collector_registry.register("my_custom", MyCustomCollector)
```

### Erlang收集器配置

使用Erlang收集器需要添加额外依赖：

```bash
# 使用pip
pip install statis-log[erlang]

# 使用Poetry
poetry add statis-log -E erlang
```

Erlang收集器配置示例：

```yaml
collectors:
  erlang_logs:
    type: erlang
    node_name: my_erlang_node  # Erlang节点名称 (必填)
    cookie: my_cookie          # Erlang分布式cookie (必填)
    host: 192.168.1.100        # 主机地址 (可选，默认localhost)
    port: 4369                 # 端口 (可选)
    timeout: 10                # 连接超时(秒) (可选，默认5秒)
    max_logs: 200              # 最大日志条数 (可选，默认100条)
    log_path: "/var/log/erlang" # 日志路径 (可选)
```

### 自定义分析器

创建自定义分析器需要继承 `BaseAnalyzer` 类并实现 `analyze` 方法：

```python
from statis_log.analyzers.base import BaseAnalyzer
from statis_log.core import analyzer_registry

class MyCustomAnalyzer(BaseAnalyzer):
    def analyze(self, logs):
        # 实现自定义分析逻辑
        return results

# 注册分析器
analyzer_registry.register("my_custom", MyCustomAnalyzer)
```

### 自定义通知器

创建自定义通知器需要继承 `BaseNotifier` 类并实现 `notify` 方法：

```python
from statis_log.notifiers.base import BaseNotifier
from statis_log.core import notifier_registry

class MyCustomNotifier(BaseNotifier):
    def notify(self, title, message, data=None):
        # 实现自定义通知逻辑
        return success

# 注册通知器
notifier_registry.register("my_custom", MyCustomNotifier)
```

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 待办事项

- [x] 增加更多内置收集器类型（已添加Erlang收集器）
- [ ] 增强分析器功能，支持机器学习模型
- [ ] 提供Web界面进行管理
- [ ] 完善文档和示例

## 版本历史

- **0.1.0** - 初始版本发布

## 许可证

MIT 
# statis_log

一个工程化的日志收集、分析和通知工具，提供灵活的扩展性。

## 主要功能

- **日志收集**：从多种来源收集日志，包括文件、数据库等
- **日志分析**：使用多种分析器分析日志内容，识别模式和问题
- **通知**：基于分析结果发送各种形式的通知

## 安装

```bash
pip install statis_log
```

或者从源码安装：

```bash
git clone https://github.com/yourusername/statis_log.git
cd statis_log
pip install -e .
```

## 使用方法

### 初始化配置

```bash
statis-log init -o config.yaml
```

### 验证配置

```bash
statis-log validate -c config.yaml
```

### 运行

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

## 拓展性设计

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

## 许可证

MIT 
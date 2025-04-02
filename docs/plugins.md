# 插件开发指南

## 插件系统概述

StatisLog使用插件系统来扩展功能，共有三种类型的插件：

1. **收集器(Collector)** - 负责从各种来源收集日志
2. **分析器(Analyzer)** - 负责分析日志数据并生成结果
3. **通知器(Notifier)** - 负责发送分析结果的通知

每种类型的插件都有对应的基类和注册机制。

## 使用装饰器注册插件

StatisLog提供了装饰器，使插件的注册变得简单。使用装饰器，你可以轻松地创建自定义插件并自动注册它们。

### 导入装饰器

首先，导入所需的装饰器：

```python
from statis_log.utils.plugin import collector, analyzer, notifier
```

### 创建和注册收集器

```python
from statis_log.collectors.base import BaseCollector
from statis_log.utils.plugin import collector

@collector("my_collector")
class MyCollector(BaseCollector):
    """自定义收集器"""
    
    def __init__(self, name, config=None):
        super().__init__(name, config)
        # 初始化你的收集器
        
    def collect(self):
        # 实现收集逻辑
        return []
```

### 创建和注册分析器

```python
from statis_log.analyzers.base import BaseAnalyzer
from statis_log.utils.plugin import analyzer

@analyzer("my_analyzer")
class MyAnalyzer(BaseAnalyzer):
    """自定义分析器"""
    
    def __init__(self, name, config=None):
        super().__init__(name, config)
        # 初始化你的分析器
        
    def analyze(self, logs):
        # 实现分析逻辑
        return {"matches": [], "summary": {}}
```

### 创建和注册通知器

```python
from statis_log.notifiers.base import BaseNotifier
from statis_log.utils.plugin import notifier

@notifier("my_notifier")
class MyNotifier(BaseNotifier):
    """自定义通知器"""
    
    def __init__(self, name, config=None):
        super().__init__(name, config)
        # 初始化你的通知器
        
    def notify(self, title, message, data=None):
        # 实现通知逻辑
        return True
```

## 加载自定义插件

### 方法1：在配置文件中指定插件模块

在配置文件中，你可以指定要加载的自定义插件模块：

```yaml
plugins:
  - my_package.my_plugins
  - another_package.plugins
```

### 方法2：在配置中指定插件目录

你也可以指定包含插件的目录：

```yaml
plugin_dirs:
  - /path/to/my/plugins
  - ./plugins
```

### 方法3：在代码中手动导入

```python
import importlib
importlib.import_module("my_package.my_plugins")
```

## 示例自定义插件

请参考 `examples/custom_plugin.py` 文件，其中包含三个自定义插件的完整示例：

1. `JsonFileCollector` - 从JSON文件收集日志
2. `KeywordAnalyzer` - 基于关键词分析日志
3. `ConsoleNotifier` - 在控制台输出通知

## 插件开发最佳实践

1. **继承正确的基类** - 确保你的插件继承自适当的基类
2. **实现必要的方法** - 实现基类中定义的抽象方法
3. **使用装饰器注册** - 使用提供的装饰器自动注册你的插件
4. **提供完整的文档** - 为你的插件类和方法提供详细的文档
5. **验证配置** - 实现 `validate_config` 方法来检查配置的有效性
6. **错误处理** - 妥善处理异常，记录错误日志 
"""
statis_log - 日志收集、分析和通知工具

安装配置文件
"""

from setuptools import setup, find_packages
import os

# 读取版本信息
with open(os.path.join("statis_log", "__init__.py"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("'\"")
            break
    else:
        version = "0.1.0"

# 读取长描述
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="statis_log",
    version=version,
    description="一个工程化的日志收集、分析和通知工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/statis_log",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
    install_requires=[
        "pyyaml>=5.1",
    ],
    entry_points={
        "console_scripts": [
            "statis-log=statis_log.cli:main",
        ],
    },
    python_requires=">=3.6",
) 
---
title: Python运维脚本库
aliases: [运维脚本, Python运维, 自动化脚本]
tags: [python, 运维, 自动化]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# Python 运维脚本库

## 概述

本脚本库提供Python运维自动化的常用代码模板。

## 1. 系统监控

### CPU监控

```python
import psutil

def get_cpu_info():
    """获取CPU信息"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'cpu_count': psutil.cpu_count(),
        'cpu_freq': psutil.cpu_freq()._asdict()
    }

# 使用
cpu_info = get_cpu_info()
print(f"CPU使用率: {cpu_info['cpu_percent']}%")
```

### 内存监控

```python
def get_memory_info():
    """获取内存信息"""
    mem = psutil.virtual_memory()
    return {
        'total': mem.total,
        'available': mem.available,
        'percent': mem.percent,
        'used': mem.used,
        'free': mem.free
    }

# 使用
mem_info = get_memory_info()
print(f"内存使用率: {mem_info['percent']}%")
```

### 磁盘监控

```python
def get_disk_info():
    """获取磁盘信息"""
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent
    }

# 使用
disk_info = get_disk_info()
print(f"磁盘使用率: {disk_info['percent']}%")
```

## 2. 进程管理

### 查找进程

```python
def find_process(name):
    """查找进程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if name.lower() in proc.info['name'].lower():
            yield proc

# 使用
for proc in find_process('python'):
    print(f"PID: {proc.pid}, Name: {proc.name()}")
```

### 杀死进程

```python
def kill_process(pid):
    """杀死进程"""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
        return True
    except:
        return False

# 使用
kill_process(12345)
```

## 3. 文件操作

### 文件搜索

```python
import os
import glob

def find_files(directory, pattern):
    """查找文件"""
    return glob.glob(os.path.join(directory, pattern))

# 使用
files = find_files('/path/to/dir', '*.log')
```

### 文件监控

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"文件创建: {event.src_path}")
    
    def on_modified(self, event):
        print(f"文件修改: {event.src_path}")

# 使用
observer = Observer()
observer.schedule(MyHandler(), path='/path/to/watch', recursive=True)
observer.start()
```

## 4. 网络操作

### HTTP请求

```python
import requests

def get_request(url):
    """GET请求"""
    response = requests.get(url)
    return response.json()

def post_request(url, data):
    """POST请求"""
    response = requests.post(url, json=data)
    return response.json()

# 使用
data = get_request('https://api.example.com/data')
```

### SSH操作

```python
import paramiko

def ssh_command(host, command):
    """执行SSH命令"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='user', password='pass')
    
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode()
    
    ssh.close()
    return result

# 使用
result = ssh_command('192.168.1.100', 'ls -la')
```

## 5. 日志处理

### 日志解析

```python
import re

def parse_log_line(line):
    """解析日志行"""
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.*)'
    match = re.match(pattern, line)
    if match:
        return {
            'timestamp': match.group(1),
            'level': match.group(2),
            'message': match.group(3)
        }
    return None

# 使用
with open('app.log', 'r') as f:
    for line in f:
        log = parse_log_line(line)
        if log and log['level'] == 'ERROR':
            print(f"错误: {log['message']}")
```

### 日志统计

```python
from collections import Counter

def analyze_log_levels(log_file):
    """分析日志级别"""
    levels = Counter()
    with open(log_file, 'r') as f:
        for line in f:
            log = parse_log_line(line)
            if log:
                levels[log['level']] += 1
    return levels

# 使用
levels = analyze_log_levels('app.log')
for level, count in levels.most_common():
    print(f"{level}: {count}")
```

## 6. 定时任务

### 使用schedule

```python
import schedule
import time

def job():
    print("执行定时任务...")

# 每小时执行
schedule.every(1).hours.do(job)

# 每天执行
schedule.every().day.at("10:00").do(job)

# 运行
while True:
    schedule.run_pending()
    time.sleep(1)
```

### 使用APScheduler

```python
from apscheduler.schedulers.blocking import BlockingScheduler

def job():
    print("执行定时任务...")

scheduler = BlockingScheduler()
scheduler.add_job(job, 'interval', hours=1)
scheduler.start()
```

## 相关页面

- [[Python数据分析工具箱]]
- [[SSH隧道与远程管理]]
- [[XXL-JOB定时任务管理]]

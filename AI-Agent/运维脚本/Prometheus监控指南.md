---
title: Prometheus监控指南
aliases: [Prometheus教程, 监控系统, 告警配置]
tags: [prometheus, 监控, 运维]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# Prometheus 监控指南

## 概述

本指南提供Prometheus监控系统的配置方法和最佳实践。

## 1. 基础配置

### 配置文件

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node1:9100', 'node2:9100']
```

### 启动命令

```bash
# 启动Prometheus
./prometheus --config.file=prometheus.yml

# 检查配置
./promtool check config prometheus.yml
```

## 2. 数据模型

### 指标类型

```bash
# 计数器（Counter）
http_requests_total{method="GET", handler="/api"} 100

# 仪表（Gauge）
memory_usage_bytes{instance="node1"} 1073741824

# 直方图（Histogram）
http_request_duration_seconds_bucket{le="0.1"} 100
http_request_duration_seconds_bucket{le="0.5"} 200
http_request_duration_seconds_bucket{le="1"} 250
http_request_duration_seconds_sum 125.5
http_request_duration_seconds_count 250

# 摘要（Summary）
http_request_duration_seconds{quantile="0.5"} 0.5
http_request_duration_seconds{quantile="0.9"} 0.9
http_request_duration_seconds{quantile="0.99"} 0.99
http_request_duration_seconds_sum 125.5
http_request_duration_seconds_count 250
```

## 3. PromQL查询

### 基础查询

```promql
# 查询所有指标
http_requests_total

# 条件查询
http_requests_total{method="GET"}

# 正则匹配
http_requests_total{handler=~"/api/.*"}

# 范围查询
http_requests_total[5m]
```

### 聚合查询

```promql
# 求和
sum(http_requests_total)

# 按标签分组
sum by (method) (http_requests_total)

# 平均值
avg(memory_usage_bytes)

# 最大值
max(cpu_usage_percent)

# 最小值
min(disk_free_bytes)
```

### 函数

```promql
# 速率
rate(http_requests_total[5m])

# 增量
increase(http_requests_total[1h])

# 变化率
deriv(memory_usage_bytes[5m])

# 预测
predict_linear(memory_usage_bytes[1h], 3600)
```

## 4. 告警规则

### 告警配置

```yaml
# alert_rules.yml
groups:
  - name: example
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 90% for 5 minutes"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 10%"
```

## 5. Exporter配置

### Node Exporter

```bash
# 安装
wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz
tar xvf node_exporter-1.3.1.linux-amd64.tar.gz
./node_exporter

# systemd服务
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

### MySQL Exporter

```bash
# 安装
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.14.0/mysqld_exporter-0.14.0.linux-amd64.tar.gz
tar xvf mysqld_exporter-0.14.0.linux-amd64.tar.gz

# 配置
export DATA_SOURCE_NAME="exporter:password@(localhost:3306)/database"
./mysqld_exporter
```

### Redis Exporter

```bash
# 安装
wget https://github.com/oliver006/redis_exporter/releases/download/v1.43.0/redis_exporter-v1.43.0.linux-amd64.tar.gz
tar xvf redis_exporter-v1.43.0.linux-amd64.tar.gz

# 启动
./redis_exporter -redis.addr localhost:6379
```

## 6. Grafana集成

### 数据源配置

```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "isDefault": true
}
```

### 常用Dashboard

- Node Exporter Full
- MySQL Overview
- Redis Dashboard
- Kubernetes Cluster Monitoring

## 7. 告警管理

### Alertmanager配置

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@example.com'
        subject: 'Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

## 8. 性能优化

### 存储优化

```bash
# 数据保留时间
--storage.tsdb.retention.time=15d

# 数据压缩
--storage.tsdb.retention.size=10GB
```

### 查询优化

```promql
# 使用子查询
rate(http_requests_total[5m])[1h:1m]

# 使用录制规则
groups:
  - name: example
    rules:
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))
```

## 相关页面

- [[Grafana可视化指南]]
- [[Linux运维常用命令]]
- [[Docker容器化指南]]

---
title: "Grafana可视化指南"
aliases:
  - Grafana配置
  - Grafana Dashboard
  - 监控可视化
tags:
  - grafana
  - 可视化
  - 监控
  - dashboard
  - 运维
type: reference
status: active
created: 2025-01-01
updated: 2025-06-27
source: internal
difficulty: intermediate
project: AI-Agent
---

# Grafana可视化指南

## 概述

Grafana是开源的可视化与监控平台，支持多种数据源，广泛用于运维监控、业务指标展示和告警管理。

---

## 1. 安装与配置

### 1.1 Docker部署

```yaml
# docker-compose.yml
version: "3.8"
services:
  grafana:
    image: grafana/grafana:10.2.0
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_SERVER_ROOT_URL=https://grafana.example.com
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./provisioning:/etc/grafana/provisioning
    restart: unless-stopped

volumes:
  grafana-data:
```

### 1.2 核心配置

```ini
# grafana.ini
[server]
protocol = http
http_port = 3000
domain = grafana.example.com
root_url = https://%(domain)s/

[security]
admin_user = admin
admin_password = ${GF_ADMIN_PASSWORD}
disable_gravatar = true
cookie_secure = true
cookie_samesite = strict

[auth.ldap]
enabled = true
config_file = /etc/grafana/ldap.toml

[alerting]
enabled = true
execute_alerts = true

[dashboards]
default_home_dashboard_path = /var/lib/grafana/dashboards/home.json
```

### 1.3 自动化Provisioning

```yaml
# provisioning/datasources/datasources.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "logstash-*"
    jsonData:
      esVersion: "8.0.0"
      timeField: "@timestamp"
      logMessageField: message
      logLevelField: level

  - name: MySQL
    type: mysql
    url: mysql:3306
    database: grafana
    user: grafana
    secureJsonData:
      password: ${MYSQL_PASSWORD}
```

```yaml
# provisioning/dashboards/dashboards.yml
apiVersion: 1
providers:
  - name: default
    orgId: 1
    folder: "运维监控"
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

---

## 2. 数据源配置

### 2.1 Prometheus

```yaml
# provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    jsonData:
      httpMethod: POST
      exemplarTraceIdDestinations:
        - name: traceID
          datasourceUid: tempo
    secureJsonData:
      httpHeaderValue1: "Bearer ${PROMETHEUS_TOKEN}"
```

**常用PromQL查询：**

```promql
# CPU使用率
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 磁盘使用率
(1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100

# HTTP请求速率
sum(rate(http_requests_total[5m])) by (method, status)

# 请求延迟P99
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

### 2.2 Elasticsearch

```json
// Lucene查询示例
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } },
        { "range": { "@timestamp": { "gte": "now-1h" } } }
      ],
      "must_not": [
        { "match": { "message": "health_check" } }
      ]
    }
  },
  "size": 100
}
```

---

## 3. Dashboard设计

### 3.1 Dashboard JSON模型

```json
{
  "dashboard": {
    "id": null,
    "uid": "server-overview",
    "title": "服务器概览",
    "tags": ["server", "linux", "node-exporter"],
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "templating": {
      "list": [
        {
          "name": "instance",
          "type": "query",
          "datasource": "Prometheus",
          "query": "label_values(node_uname_info, instance)",
          "refresh": 2,
          "multi": true,
          "includeAll": true
        }
      ]
    },
    "panels": [
      {
        "title": "CPU使用率",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\", instance=~\"$instance\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                { "value": null, "color": "green" },
                { "value": 70, "color": "yellow" },
                { "value": 90, "color": "red" }
              ]
            }
          }
        }
      }
    ]
  }
}
```

### 3.2 变量与模板

```json
{
  "templating": {
    "list": [
      {
        "name": "datasource",
        "type": "datasource",
        "query": "prometheus"
      },
      {
        "name": "job",
        "type": "query",
        "datasource": "${datasource}",
        "query": "label_values(up, job)",
        "refresh": 2
      },
      {
        "name": "instance",
        "type": "query",
        "datasource": "${datasource}",
        "query": "label_values(up{job=\"$job\"}, instance)",
        "refresh": 2,
        "multi": true,
        "includeAll": true
      },
      {
        "name": "interval",
        "type": "interval",
        "query": "1m,5m,15m,30m,1h",
        "auto": true,
        "auto_min": "1m",
        "auto_count": 30
      }
    ]
  }
}
```

### 3.3 常用Panel类型

```yaml
# 各Panel适用场景
timeseries:  # 时间序列图 - CPU/内存/网络趋势
stat:        # 单一统计值 - 当前在线用户数
gauge:       # 仪表盘 - 磁盘使用率
bar gauge:   # 条形仪表 - 各服务CPU占用
table:       # 表格 - 告警列表/日志
pie chart:   # 饼图 - 流量来源分布
heatmap:     # 热力图 - 请求延迟分布
logs:        # 日志面板 - 实时日志流
```

### 3.4 Grafana API管理Dashboard

```bash
# 导出Dashboard
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "http://grafana:3000/api/dashboards/uid/server-overview" | jq '.dashboard' > dashboard.json

# 导入Dashboard
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -d "{\"dashboard\": $(cat dashboard.json), \"overwrite\": true, \"folderId\": 0}" \
  "http://grafana:3000/api/dashboards/db"

# 创建API Key
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -d '{"name":"automation","role":"Admin"}' \
  "http://grafana:3000/api/auth/keys"
```

---

## 4. 告警配置

### 4.1 Grafana Alerting（v9+）

```yaml
# provisioning/alerting/rules.yml
apiVersion: 1
groups:
  - orgId: 1
    name: 服务器告警
    folder: 基础设施
    interval: 1m
    rules:
      - uid: cpu-high
        title: CPU使用率过高
        condition: C
        data:
          - refId: A
            datasourceUid: prometheus
            model:
              expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
          - refId: C
            datasourceUid: __expr__
            model:
              type: threshold
              expression: A
              conditions:
                - evaluator:
                    type: gt
                    params: [85]
                  operator:
                    type: and
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "实例 {{ $labels.instance }} CPU使用率超过85%"
          description: "当前值: {{ $value | printf \"%.1f\" }}%"
```

### 4.2 告警联系点

```yaml
# provisioning/alerting/contactpoints.yml
apiVersion: 1
contactPoints:
  - orgId: 1
    name: ops-team
    receivers:
      - uid: slack-ops
        type: slack
        settings:
          url: https://hooks.slack.com/services/xxx/yyy/zzz
          recipient: "#ops-alerts"
          title: "{{ .CommonLabels.alertname }}"
          text: "{{ .CommonAnnotations.description }}"

      - uid: email-ops
        type: email
        settings:
          addresses: ops@example.com
          singleEmail: false

      - uid: webhook-ops
        type: webhook
        settings:
          url: https://api.example.com/alert
          method: POST
          httpMethod: POST

notificationPolicies:
  - orgId: 1
    receiver: ops-team
    group_by: [alertname, instance]
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 4h
    routes:
      - receiver: ops-team
        matchers:
          - severity = critical
        repeat_interval: 1h
```

---

## 5. Grafonnet（Jsonnet生成Dashboard）

```jsonnet
// dashboard.jsonnet
local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local prometheus = grafana.prometheus;
local graphPanel = grafana.graphPanel;

dashboard.new(
  'Server Overview',
  tags=['server', 'node-exporter'],
  refresh='30s',
  time_from='now-1h',
)
.addPanel(
  graphPanel.new(
    'CPU Usage',
    datasource='Prometheus',
    format='percent',
    min=0,
    max=100,
  )
  .addTarget(
    prometheus.target(
      '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
      legendFormat='{{instance}}',
    )
  ),
  gridPos={ h: 8, w: 12, x: 0, y: 0 },
)
```

```bash
# 使用jsonnet生成JSON
jsonnet -J vendor dashboard.jsonnet > dashboard.json

# 导入到Grafana
grafana-cli admin import-dashboard dashboard.json
```

---

## 最佳实践

| 编号 | 实践 | 说明 |
|------|------|------|
| 1 | 使用Provisioning管理 | 数据源、Dashboard、告警均通过代码管理 |
| 2 | 变量化Dashboard | 通过模板变量实现环境/实例切换 |
| 3 | 统一颜色方案 | green→yellow→red 阈值标准 |
| 4 | 合理设置刷新间隔 | 避免过频繁查询压垮数据源 |
| 5 | 告警分级 | P1(电话)/P2(即时)/P3(邮件) |
| 6 | Dashboard分层 | 概览→服务→实例三层 |
| 7 | 版本控制 | Dashboard JSON纳入Git管理 |
| 8 | 权限最小化 | 按团队分配文件夹权限 |

---

## 相关页面

- [[Shell脚本编程指南]] - 自动化脚本基础
- [[Terraform基础设施即代码]] - Grafana基础设施部署
- [[ELK进阶配置]] - Elasticsearch作为Grafana数据源
- [[监控告警体系设计]] - 监控告警整体方案

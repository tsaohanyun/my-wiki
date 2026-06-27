---
title: ELK日志分析指南
aliases: [ELK教程, 日志系统, Elasticsearch]
tags: [elk, 日志, 运维]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: advanced
project: 运维
---
# ELK 日志分析指南

## 概述

本指南提供ELK（Elasticsearch、Logstash、Kibana）日志系统的配置方法和最佳实践。

## 1. 基础架构

### 组件说明

- **Elasticsearch**：分布式搜索和分析引擎
- **Logstash**：数据处理管道
- **Kibana**：数据可视化平台
- **Beats**：轻量级数据采集器

### 架构图

```
应用日志 → Filebeat → Logstash → Elasticsearch → Kibana
                ↓
            Kafka/Redis（可选）
```

## 2. Elasticsearch配置

### 安装配置

```yaml
# elasticsearch.yml
cluster.name: my-cluster
node.name: node-1
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node

# 内存配置
bootstrap.memory_lock: true
```

### 启动命令

```bash
# 启动Elasticsearch
./bin/elasticsearch

# 后台启动
./bin/elasticsearch -d

# 检查状态
curl -X GET "localhost:9200/"
```

### 索引管理

```bash
# 创建索引
curl -X PUT "localhost:9200/my-index"

# 查看索引
curl -X GET "localhost:9200/_cat/indices?v"

# 删除索引
curl -X DELETE "localhost:9200/my-index"
```

## 3. Logstash配置

### 基础配置

```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
  
  file {
    path => "/var/log/nginx/access.log"
    start_position => "beginning"
  }
}

filter {
  grok {
    match => { "message" => "%{COMBINEDAPACHELOG}" }
  }
  
  date {
    match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
  }
  
  geoip {
    source => "clientip"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "nginx-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
```

### 常用过滤器

```ruby
# Grok过滤器
filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
  }
}

# Mutate过滤器
filter {
  mutate {
    rename => { "hostname" => "server_name" }
    remove_field => ["timestamp"]
    convert => { "response_time" => "integer" }
  }
}

# GeoIP过滤器
filter {
  geoip {
    source => "client_ip"
    target => "geoip"
  }
}
```

## 4. Filebeat配置

### 基础配置

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    paths:
      - /var/log/nginx/*.log
    fields:
      app: nginx
    fields_under_root: true

output.logstash:
  hosts: ["logstash:5044"]

# 或直接输出到Elasticsearch
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "nginx-%{+yyyy.MM.dd}"
```

### 模块配置

```yaml
# filebeat.yml
filebeat.modules:
  - module: nginx
    access:
      enabled: true
      var.paths: ["/var/log/nginx/access.log"]
    error:
      enabled: true
      var.paths: ["/var/log/nginx/error.log"]
  
  - module: mysql
    slowlog:
      enabled: true
      var.paths: ["/var/log/mysql/slow.log"]
```

## 5. Kibana配置

### 基础配置

```yaml
# kibana.yml
server.port: 5601
server.host: "localhost"
elasticsearch.hosts: ["http://localhost:9200"]
```

### 索引模式

```
1. 进入 Management → Index Patterns
2. 创建索引模式：nginx-*
3. 选择时间字段：@timestamp
4. 创建模式
```

### 可视化

```
1. 创建Dashboard
2. 添加Visualization
3. 选择图表类型
4. 配置数据源和指标
5. 保存并添加到Dashboard
```

## 6. 查询语法

### Elasticsearch查询

```json
// 简单查询
GET /my-index/_search
{
  "query": {
    "match": {
      "message": "error"
    }
  }
}

// 范围查询
GET /my-index/_search
{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "2026-06-01",
        "lte": "2026-06-30"
      }
    }
  }
}

// 聚合查询
GET /my-index/_search
{
  "size": 0,
  "aggs": {
    "by_level": {
      "terms": {
        "field": "level.keyword"
      }
    }
  }
}
```

### KQL查询

```
# 简单查询
message: "error"

# 组合查询
message: "error" and level: "ERROR"

# 范围查询
@timestamp >= "2026-06-01" and @timestamp <= "2026-06-30"

# 通配符查询
message: "err*"
```

## 7. 告警配置

### Watcher告警

```json
// 创建Watcher
PUT _watcher/watch/my-watch
{
  "trigger": {
    "schedule": {
      "interval": "5m"
    }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["nginx-*"],
        "body": {
          "size": 0,
          "query": {
            "bool": {
              "must": [
                {
                  "match": {
                    "level": "ERROR"
                  }
                },
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-5m"
                    }
                  }
                }
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total": {
        "gt": 10
      }
    }
  },
  "actions": {
    "send_email": {
      "email": {
        "to": "admin@example.com",
        "subject": "Error Alert",
        "body": {
          "text": "Found {{ctx.payload.hits.total}} errors in last 5 minutes"
        }
      }
    }
  }
}
```

## 8. 性能优化

### Elasticsearch优化

```yaml
# jvm.options
-Xms4g
-Xmx4g

# elasticsearch.yml
indices.memory.index_buffer_size: 20%
indices.fielddata.cache.size: 30%
```

### 索引优化

```json
// 创建索引模板
PUT _index_template/nginx-template
{
  "index_patterns": ["nginx-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "5s"
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "message": {
          "type": "text"
        },
        "level": {
          "type": "keyword"
        }
      }
    }
  }
}
```

## 9. 备份恢复

### 快照备份

```bash
# 创建仓库
PUT _snapshot/my_backup
{
  "type": "fs",
  "settings": {
    "location": "/backup/elasticsearch"
  }
}

# 创建快照
PUT _snapshot/my_backup/snapshot_1

# 恢复快照
POST _snapshot/my_backup/snapshot_1/_restore
```

## 相关页面

- [[Prometheus监控指南]]
- [[Linux运维常用命令]]
- [[Docker容器化指南]]

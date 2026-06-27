---
title: "ELK进阶配置"
aliases:
  - ELK Stack
  - Elasticsearch配置
  - Logstash管道
  - Kibana查询
tags:
  - elasticsearch
  - logstash
  - kibana
  - elk
  - 日志
  - 运维
type: reference
status: active
created: 2025-01-01
updated: 2025-06-27
source: internal
difficulty: advanced
project: AI-Agent
---

# ELK进阶配置

## 概述

ELK Stack（Elasticsearch + Logstash + Kibana）是业界最流行的日志收集、存储和分析平台。本文档覆盖集群配置、管道优化和高级查询。

---

## 1. Elasticsearch集群配置

### 1.1 集群架构

```yaml
# elasticsearch.yml - Master节点
cluster.name: prod-logs
node.name: es-master-01
node.roles: [master]
network.host: 0.0.0.0
discovery.seed_hosts:
  - es-master-01
  - es-master-02
  - es-master-03
cluster.initial_master_nodes:
  - es-master-01
  - es-master-02
  - es-master-03

# 安全配置
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.keystore.path: certs/transport.p12
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: certs/http.p12
```

```yaml
# elasticsearch.yml - Data节点
node.name: es-data-01
node.roles: [data_hot, data_content]
path.data: /data/elasticsearch
path.logs: /var/log/elasticsearch

# JVM内存设置（不超过物理内存的50%，不超过32GB）
# jvm.options
-Xms16g
-Xmx16g
```

```yaml
# elasticsearch.yml - Coordinating节点
node.name: es-coord-01
node.roles: []
```

### 1.2 索引生命周期管理（ILM）

```json
// 创建ILM策略
PUT _ilm/policy/logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_primary_shard_size": "50gb",
            "max_age": "1d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "3d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {},
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### 1.3 索引模板

```json
// 创建索引模板
PUT _index_template/logs-template
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "logs-policy",
      "index.lifecycle.rollover_alias": "logs-write",
      "index.codec": "best_compression",
      "index.refresh_interval": "10s"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "@timestamp": { "type": "date" },
        "message": { "type": "text", "analyzer": "standard" },
        "level": { "type": "keyword" },
        "service": { "type": "keyword" },
        "host": {
          "properties": {
            "name": { "type": "keyword" },
            "ip": { "type": "ip" }
          }
        },
        "request": {
          "properties": {
            "method": { "type": "keyword" },
            "path": { "type": "keyword" },
            "duration_ms": { "type": "float" },
            "status_code": { "type": "short" }
          }
        }
      }
    },
    "aliases": {
      "logs-read": {}
    }
  },
  "priority": 200
}

// 初始化写入别名
PUT logs-write-000001
{
  "aliases": {
    "logs-write": { "is_write_index": true }
  }
}
```

### 1.4 集群运维API

```bash
# 集群健康状态
GET _cluster/health

# 节点状态
GET _cat/nodes?v&h=name,heap.percent,ram.percent,cpu,load_1m,node.role

# 索引状态
GET _cat/indices?v&s=store.size:desc&h=index,health,status,pri,rep,docs.count,store.size

# 分片分配
GET _cat/shards?v&h=index,shard,prirep,state,docs,store,node&s=store:desc

# 热点线程
GET _nodes/hot_threads

# 待处理任务
GET _cluster/pending_tasks

# 强制合并（谨慎使用）
POST logs-2024.01.*/_forcemerge?max_num_segments=1

# 关闭/打开索引节省内存
POST logs-2023.12.*/_close
POST logs-2023.12.*/_open
```

---

## 2. Logstash管道

### 2.1 主配置文件

```ruby
# logstash.yml
node.name: logstash-01
path.data: /var/lib/logstash
path.logs: /var/log/logstash
pipeline.workers: 4
pipeline.batch.size: 125
pipeline.batch.delay: 50
```

### 2.2 Nginx日志管道

```ruby
# pipelines/nginx.conf
input {
  beats {
    port => 5044
    ssl => true
    ssl_certificate => "/etc/logstash/certs/logstash.crt"
    ssl_key => "/etc/logstash/certs/logstash.key"
  }
}

filter {
  # 解析Nginx访问日志
  if [fields][log_type] == "nginx_access" {
    grok {
      match => {
        "message" => '%{IPORHOST:client_ip} - %{DATA:user} \[%{HTTPDATE:timestamp}\] "%{WORD:method} %{URIPATHPARAM:request} HTTP/%{NUMBER:http_version}" %{NUMBER:status:int} %{NUMBER:bytes:int} "%{DATA:referrer}" "%{DATA:user_agent}" %{NUMBER:request_time:float}'
      }
      remove_field => ["message"]
    }

    date {
      match => ["timestamp", "dd/MMM/yyyy:HH:mm:ss Z"]
      target => "@timestamp"
    }

    geoip {
      source => "client_ip"
      target => "geo"
    }

    useragent {
      source => "user_agent"
      target => "ua"
    }

    # 请求时间转毫秒
    ruby {
      code => "event.set('request_duration_ms', event.get('request_time') * 1000)"
    }

    # 根据状态码标记
    if [status] >= 500 {
      mutate { add_tag => ["error_5xx"] }
    } else if [status] >= 400 {
      mutate { add_tag => ["error_4xx"] }
    }
  }

  # 解析应用日志
  if [fields][log_type] == "app_log" {
    json {
      source => "message"
      target => "app"
      skip_on_invalid_json => true
    }

    if "_jsonparsefailure" not in [tags] {
      mutate {
        rename => {
          "[app][level]" => "level"
          "[app][msg]" => "log_message"
          "[app][trace_id]" => "trace_id"
        }
      }
    }
  }

  # 通用处理
  mutate {
    remove_field => ["agent", "ecs", "input", "log"]
  }
}

output {
  if "error_5xx" in [tags] {
    elasticsearch {
      hosts => ["https://es-coord-01:9200", "https://es-coord-02:9200"]
      user => "logstash_writer"
      password => "${ES_PASSWORD}"
      index => "logs-5xx-%{+YYYY.MM.dd}"
      ssl => true
      cacert => "/etc/logstash/certs/ca.crt"
    }
  } else {
    elasticsearch {
      hosts => ["https://es-coord-01:9200", "https://es-coord-02:9200"]
      user => "logstash_writer"
      password => "${ES_PASSWORD}"
      index => "logs-%{+YYYY.MM.dd}"
      ssl => true
      cacert => "/etc/logstash/certs/ca.crt"
    }
  }

  # 调试输出
  # stdout { codec => rubydebug }
}
```

### 2.3 多管道配置

```yaml
# pipelines.yml
- pipeline.id: nginx-logs
  path.config: "/etc/logstash/pipelines/nginx.conf"
  pipeline.workers: 4

- pipeline.id: app-logs
  path.config: "/etc/logstash/pipelines/app.conf"
  pipeline.workers: 2

- pipeline.id: metrics
  path.config: "/etc/logstash/pipelines/metrics.conf"
  pipeline.workers: 1
```

### 2.4 性能优化

```ruby
# 使用Persistent Queue
# logstash.yml
queue.type: persisted
queue.max_bytes: 4gb
queue.checkpoint.writes: 1024

# Grok性能优化
# 使用更具体的pattern，避免.*贪婪匹配
# 使用dissect替代简单的grok
filter {
  dissect {
    mapping => {
      "message" => "%{timestamp} %{+timestamp} [%{level}] %{service} - %{msg}"
    }
  }
}

# 批量写入ES
output {
  elasticsearch {
    hosts => ["es:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    flush_size => 5000
    idle_flush_time => 1
  }
}
```

---

## 3. Kibana高级查询

### 3.1 KQL（Kibana Query Language）

```
# 精确匹配
level: "ERROR"

# 模糊匹配
message: timeout

# 范围查询
request.duration_ms > 1000
status_code >= 500 and status_code < 600

# 组合查询
level: "ERROR" and service: "payment-api" and not message: "health_check"

# 存在性检查
request.duration_ms: *

# 通配符
host.name: web-*
```

### 3.2 Lucene高级查询

```
# 正则表达式
message: /timeout|connection_refused/i

# 模糊匹配
message: tiemout~2

# 近似匹配
message: "database connection"~3

# 范围
request.duration_ms: [100 TO 500]
@timestamp: [now-1h TO now]

# 嵌套字段
"host.name": "web-01" AND "request.status_code": >=500
```

### 3.3 ES聚合查询

```json
// 按服务统计错误率
GET logs-*/_search
{
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "range": { "@timestamp": { "gte": "now-1h" } } }
      ]
    }
  },
  "aggs": {
    "by_service": {
      "terms": { "field": "service", "size": 20 },
      "aggs": {
        "error_count": {
          "filter": { "term": { "level": "ERROR" } }
        },
        "error_rate": {
          "bucket_script": {
            "buckets_path": {
              "errors": "error_count._count",
              "total": "_count"
            },
            "script": "params.errors / params.total * 100"
          }
        }
      }
    }
  }
}

// 响应时间直方图
GET logs-*/_search
{
  "size": 0,
  "aggs": {
    "response_times": {
      "histogram": {
        "field": "request.duration_ms",
        "interval": 50
      }
    },
    "percentiles": {
      "percentiles": {
        "field": "request.duration_ms",
        "percents": [50, 90, 95, 99]
      }
    }
  }
}
```

---

## 4. Filebeat配置

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/nginx/access.log
    fields:
      log_type: nginx_access
    fields_under_root: false
    multiline:
      pattern: '^\d{4}-\d{2}-\d{2}'
      negate: true
      match: after

  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
  - drop_event:
      when:
        regexp:
          message: "health_check|kube-probe"

output.logstash:
  hosts: ["logstash:5044"]
  ssl.certificate_authorities: ["/etc/filebeat/ca.crt"]
  bulk_max_size: 2048
```

---

## 5. 备份与恢复

```bash
# 注册快照仓库
PUT _snapshot/backup
{
  "type": "s3",
  "settings": {
    "bucket": "es-backup",
    "region": "us-west-2",
    "base_path": "snapshots"
  }
}

# 创建快照
PUT _snapshot/backup/snapshot-2024.01.15?wait_for_completion=true
{
  "indices": "logs-2024.01.*",
  "ignore_unavailable": true,
  "include_global_state": false
}

# 恢复快照
POST _snapshot/backup/snapshot-2024.01.15/_restore
{
  "indices": "logs-2024.01.15",
  "ignore_unavailable": true
}

# 定时快照（使用SLM）
PUT _slm/policy/nightly-snapshots
{
  "schedule": "0 30 1 * * ?",
  "name": "<nightly-snap-{now/d}>",
  "repository": "backup",
  "config": {
    "indices": ["logs-*"],
    "ignore_unavailable": true,
    "include_global_state": false
  },
  "retention": {
    "expire_after": "30d",
    "min_count": 5,
    "max_count": 50
  }
}
```

---

## 最佳实践

| 编号 | 实践 | 说明 |
|------|------|------|
| 1 | 索引生命周期管理 | Hot/Warm/Cold/Delete自动流转 |
| 2 | 合理设置分片数 | 单个分片10-50GB，避免过度分片 |
| 3 | 使用ILM自动rollover | 避免单索引过大 |
| 4 | Persistent Queue | Logstash启用持久化队列防丢数据 |
| 5 | 安全认证 | 启用X-Pack Security，HTTPS通信 |
| 6 | 定期备份 | SLM策略自动快照 |
| 7 | Grok优化 | 优先用dissect，grok用具体pattern |
| 8 | 监控集群自身 | 使用Monitoring或Metricbeat监控ES |

---

## 相关页面

- [[Shell脚本编程指南]] - 日志分析脚本编写
- [[Grafana可视化指南]] - Elasticsearch作为Grafana数据源
- [[Terraform基础设施即代码]] - ELK集群基础设施管理
- [[监控告警体系设计]] - 日志告警方案设计

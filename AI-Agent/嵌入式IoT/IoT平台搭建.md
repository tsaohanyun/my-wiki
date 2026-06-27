---
title: "IoT平台搭建"
aliases:
  - IoT Platform
  - IoT平台
  - ThingsBoard
  - EMQX平台
tags:
  - iot
  - platform
  - thingsboard
  - emqx
  - device-management
  - rule-engine
  - data-collection
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: "原创整理 + ThingsBoard/EMQX 官方文档"
difficulty: intermediate
project: "嵌入式IoT知识库"
---

# IoT平台搭建

> 本页面涵盖 IoT 平台搭建的全流程：ThingsBoard 部署、EMQX 集群、设备管理、数据采集与存储、规则引擎配置等。

---

## 目录

- [1. IoT 平台架构概览](#1-iot-平台架构概览)
- [2. ThingsBoard 部署与配置](#2-thingsboard-部署与配置)
- [3. EMQX 消息中间件](#3-emqx-消息中间件)
- [4. 设备管理](#4-设备管理)
- [5. 数据采集与存储](#5-数据采集与存储)
- [6. 规则引擎](#6-规则引擎)
- [7. 最佳实践](#7-最佳实践)
- [相关页面](#相关页面)

---

## 1. IoT 平台架构概览

### 1.1 典型 IoT 平台架构

```
┌──────────────────────────────────────────────────────────────┐
│                        IoT 平台架构                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  设备层          边缘层           平台层          应用层     │
│  ┌─────┐       ┌──────┐       ┌──────────┐    ┌────────┐  │
│  │MCU  │──MQTT──│Gateway│──────│ EMQX     │───│Dashboard│  │
│  │传感器│──CoAP──│       │──────│ Broker   │    │  面板   │  │
│  │执行器│──HTTP──│       │      └────┬─────┘    └────────┘  │
│  └─────┘       └──────┘            │                        │
│                                    ▼                        │
│                              ┌──────────┐                   │
│                              │Rule Engine│                   │
│                              │ 规则引擎  │                   │
│                              └────┬─────┘                   │
│                          ┌───────┼───────┐                   │
│                          ▼       ▼       ▼                   │
│                     ┌──────┐ ┌──────┐ ┌──────┐              │
│                     │TSDB  │ │RelDB │ │Stream│              │
│                     │Influx│ │Postgr│ │Kafka │              │
│                     └──────┘ └──────┘ └──────┘              │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 技术选型对比

| 平台 | 部署方式 | 开源协议 | 优势 | 适用场景 |
|------|----------|----------|------|----------|
| ThingsBoard | 自托管/云 | Apache 2.0 | 开箱即用、规则引擎 | 中小企业 IoT |
| EMQX | 自托管/云 | Apache 2.0 | 高性能 Broker | 大规模消息路由 |
| Mainflux | 自托管 | Apache 2.0 | 微服务架构 | 定制化需求 |
| IoTSharp | 自托管 | MIT | 轻量级 | 小规模项目 |
| AWS IoT Core | 云服务 | 商业 | 全球覆盖、集成丰富 | 云原生 IoT |

---

## 2. ThingsBoard 部署与配置

### 2.1 Docker Compose 部署

```yaml
# docker-compose.yml — ThingsBoard 完整部署
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15
    container_name: tb-postgres
    environment:
      POSTGRES_DB: thingsboard
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - tb-pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # ThingsBoard 核心服务
  thingsboard:
    image: thingsboard/tb-postgres:3.6.3
    container_name: thingsboard
    depends_on:
      - postgres
    environment:
      DB_ENTITIES_TYPE: sql
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/thingsboard
      SPRING_DATASOURCE_USERNAME: postgres
      SPRING_DATASOURCE_PASSWORD: postgres
      MQTT_BIND_PORT: 1883
      MQTT_BIND_ADDRESS: 0.0.0.0
      COAP_BIND_PORT: 5683
      TB_QUEUE_TYPE: in-memory
      # 邮件配置
      SMTP_MAIL_FROM: "iot-alert@example.com"
      SMTP_HOST: "smtp.example.com"
      SMTP_PORT: "587"
      SMTP_USERNAME: "alert@example.com"
      SMTP_PASSWORD: "email-password"
    volumes:
      - tb-data:/data
      - tb-logs:/var/log/thingsboard
    ports:
      - "8080:9090"     # Web UI
      - "1883:1883"     # MQTT
      - "5683:5683/udp" # CoAP
      - "7070:7070"     # Edge RPC
    restart: unless-stopped

  # 时序数据库（可选）
  influxdb:
    image: influxdb:2.7
    container_name: tb-influxdb
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: AdminP@ss123
      DOCKER_INFLUXDB_INIT_ORG: iot
      DOCKER_INFLUXDB_INIT_BUCKET: telemetry
    volumes:
      - tb-influx:/var/lib/influxdb2
    ports:
      - "8086:8086"

volumes:
  tb-pgdata:
  tb-data:
  tb-logs:
  tb-influx:
```

```bash
# 启动 ThingsBoard
docker compose up -d

# 等待初始化完成（约 2-3 分钟）
docker logs -f thingsboard

# 访问 Web UI
# http://localhost:8080
# 默认管理员: sysadmin@thingsboard.org / sysadmin
# 默认租户管理员: tenant@thingsboard.org / tenant
```

### 2.2 设备接入配置

```bash
# 创建设备并获取凭证
# 通过 ThingsBoard REST API

# 1. 获取 JWT Token
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type:application/json" \
  -d '{"username":"tenant@thingsboard.org","password":"tenant"}' \
  | jq -r '.token')

# 2. 创建设备
curl -s -X POST http://localhost:8080/api/device \
  -H "Content-Type:application/json" \
  -H "X-Authorization: Bearer $TOKEN" \
  -d '{
    "name": "TemperatureSensor_001",
    "type": "default",
    "label": "Living Room Temperature Sensor"
  }' | jq .

# 3. 获取设备访问令牌
DEVICE_TOKEN="YourDeviceAccessToken"  # 从创建结果中获取
```

### 2.3 设备端 MQTT 接入示例

```python
import paho.mqtt.client as mqtt
import json
import time
import random

# ThingsBoard 设备接入
THINGSBOARD_HOST = "localhost"
ACCESS_TOKEN = "YourDeviceAccessToken"

client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

# 遥测数据上报主题: v1/devices/me/telemetry
# 属性上报主题:     v1/devices/me/attributes
# RPC 命令订阅主题: v1/devices/me/rpc/request/+

def on_connect(client, userdata, flags, rc):
    print(f"Connected to ThingsBoard (rc={rc})")
    # 订阅 RPC 命令
    client.subscribe("v1/devices/me/rpc/request/+")

def on_message(client, userdata, msg):
    if msg.topic.startswith("v1/devices/me/rpc"):
        # 处理 RPC 请求
        request = json.loads(msg.payload.decode())
        method = request.get("method")
        params = request.get("params")
        req_id = msg.topic.split("/")[-1]

        print(f"RPC: {method}({params})")

        # 响应 RPC
        response = {"result": "ok"}
        if method == "setGpio":
            response = {"gpio17": "set to " + str(params)}
        elif method == "getGpio":
            response = {"pin17": 1, "pin18": 0}

        client.publish(f"v1/devices/me/rpc/response/{req_id}",
                       json.dumps(response))

def on_disconnect(client, userdata, rc):
    print(f"Disconnected (rc={rc})")

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

# 模拟传感器数据上报
try:
    while True:
        telemetry = {
            "temperature": round(25.0 + random.uniform(-2, 2), 2),
            "humidity":    round(60.0 + random.uniform(-5, 5), 2),
            "battery":     random.randint(80, 100)
        }
        client.publish("v1/devices/me/telemetry", json.dumps(telemetry))
        print(f"Sent: {telemetry}")
        time.sleep(10)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
```

### 2.4 设备共享属性与客户端属性

```python
# 上报客户端属性（设备自己的属性）
client_attributes = {
    "model": "ESP32-WROOM-32",
    "firmware_version": "1.2.3",
    "serial_number": "SN-2026-0001",
    "location": {"lat": 30.5728, "lon": 104.0668}
}
client.publish("v1/devices/me/attributes",
               json.dumps(client_attributes))

# 请求服务端共享属性
request_id = "1"
client.publish(
    f"v1/devices/me/attributes/request/{request_id}",
    json.dumps({"sharedKeys": "target_temperature,alert_threshold"})
)
# 响应会在 v1/devices/me/attributes/response/+ 收到
```

---

## 3. EMQX 消息中间件

### 3.1 EMQX 集群部署

```yaml
# emqx-cluster.yml — EMQX 集群 + 负载均衡
version: '3.8'

services:
  haproxy:
    image: haproxy:2.8
    container_name: mqtt-lb
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    ports:
      - "1883:1883"    # MQTT
      - "8883:8883"    # MQTT/TLS
      - "8404:8404"    # HAProxy Stats
    depends_on:
      - emqx1
      - emqx2

  emqx1:
    image: emqx/emqx:5.4.0
    container_name: emqx-node1
    environment:
      EMQX_NAME: emqx
      EMQX_HOST: emqx1
      EMQX_CLUSTER__DISCOVERY: dns
      EMQX_CLUSTER__DNS__TYPE: srv
      EMQX_CLUSTER__DNS__NAME: emqx
      EMQX_DASHBOARD__DEFAULT_USERNAME: admin
      EMQX_DASHBOARD__DEFAULT_PASSWORD: "EmqxD@sh123"
    volumes:
      - emqx1-data:/opt/emqx/data
    ports:
      - "18083:18083"  # Dashboard (通过 node1)

  emqx2:
    image: emqx/emqx:5.4.0
    container_name: emqx-node2
    environment:
      EMQX_NAME: emqx
      EMQX_HOST: emqx2
      EMQX_CLUSTER__DISCOVERY: dns
    volumes:
      - emqx2-data:/opt/emqx/data

volumes:
  emqx1-data:
  emqx2-data:
```

```bash
# HAProxy 配置 — MQTT 负载均衡
cat > haproxy.cfg << 'EOF'
global
    maxconn 50000

defaults
    mode tcp
    timeout connect 5s
    timeout client 600s
    timeout server 600s

frontend mqtt_frontend
    bind *:1883
    default_backend mqtt_backend

frontend mqtt_tls_frontend
    bind *:8883
    default_backend mqtt_tls_backend

backend mqtt_backend
    balance leastconn
    option tcp-check
    tcp-check expect string RRTIMEOUT
    server emqx1 emqx1:1883 check
    server emqx2 emqx2:1883 check

backend mqtt_tls_backend
    balance leastconn
    server emqx1 emqx1:8883 check
    server emqx2 emqx2:8883 check

listen stats
    bind *:8404
    mode http
    stats enable
    stats uri /
EOF
```

### 3.2 EMQX 规则引擎 — 数据桥接

```sql
-- EMQX 规则 SQL：提取设备遥测数据
SELECT
    clientid AS device_id,
    payload.temperature AS temperature,
    payload.humidity AS humidity,
    timestamp AS ts,
    topic
FROM
    "devices/+/telemetry"
WHERE
    payload.temperature IS NOT NULL
```

```bash
# 通过 EMQX REST API 创建规则
curl -X POST http://localhost:18083/api/v5/rules \
  -u "admin:EmqxD@sh123" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "rule_telemetry_to_influxdb",
    "sql": "SELECT clientid AS device_id, payload.temperature AS temperature, payload.humidity AS humidity, timestamp AS ts FROM \"devices/+/telemetry\"",
    "actions": [
      {
        "function": "bridge_to_influxdb",
        "args": {
          "url": "http://influxdb:8086",
          "token": "your-influx-token",
          "org": "iot",
          "bucket": "telemetry",
          "measurement": "sensor_data"
        }
      }
    ]
  }'
```

---

## 4. 设备管理

### 4.1 设备生命周期

```
注册 → 配置 → 激活 → 在线 → 固件升级 → 维护 → 退役
  │                          │         │
  │     ┌────────────────────┘         │
  │     ▼                               │
  │  告警/事件 ←─── 数据上报 ──→ 规则引擎│
  │                                     │
  └─────────────────────────────────────┘
```

### 4.2 设备批量注册（ThingsBoard REST API）

```python
import requests
import csv
import json

TB_URL = "http://localhost:8080"
TOKEN  = "eyJhbGciOiJIUzUxMiJ9..."

headers = {
    "Content-Type": "application/json",
    "X-Authorization": f"Bearer {TOKEN}"
}

def batch_create_devices(csv_file):
    """从 CSV 批量创建设备"""
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            device = {
                "name": row['device_name'],
                "type": row['device_type'],
                "label": row.get('label', ''),
            }
            resp = requests.post(
                f"{TB_URL}/api/device",
                headers=headers,
                json=device
            )
            if resp.status_code == 200:
                dev = resp.json()
                print(f"Created: {dev['name']} → ID: {dev['id']['id']}")

                # 设置设备凭证
                cred = {
                    "deviceId": dev['id']['id'],
                    "credentialsType": "ACCESS_TOKEN",
                    "credentialsId": row['access_token']
                }
                requests.post(
                    f"{TB_URL}/api/device/credentials",
                    headers=headers,
                    json=cred
                )
            else:
                print(f"Failed: {row['device_name']} → {resp.status_code}")

# CSV 格式: device_name,device_type,label,access_token
# sensor_001,Temperature Sensor,Room A,TOKEN_s001
# sensor_002,Humidity Sensor,Room B,TOKEN_s002
batch_create_devices("devices.csv")
```

### 4.3 设备分组与资产

```bash
# 通过 ThingsBoard 创建资产（分组设备）
curl -X POST http://localhost:8080/api/asset \
  -H "X-Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Building_Floor3",
    "type": "Building",
    "label": "3rd Floor Environment Monitoring"
  }'

# 将设备关联到资产
curl -X POST "http://localhost:8080/api/relation" \
  -H "X-Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {"entityType": "ASSET", "id": "asset-uuid-here"},
    "to":   {"entityType": "DEVICE", "id": "device-uuid-here"},
    "type": "Contains"
  }'
```

---

## 5. 数据采集与存储

### 5.1 时序数据存储架构

```
设备 ──MQTT──► Broker ──► 规则引擎 ──► 持久化
                                    ├──► InfluxDB (时序数据)
                                    ├──► PostgreSQL (元数据)
                                    ├──► Kafka (流处理)
                                    └──► Redis (实时缓存)
```

### 5.2 InfluxDB 数据写入

```python
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
import json
import paho.mqtt.client as mqtt

# InfluxDB 配置
INFLUX_URL    = "http://localhost:8086"
INFLUX_TOKEN  = "your-influx-token"
INFLUX_ORG    = "iot"
INFLUX_BUCKET = "telemetry"

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=ASYNCHRONOUS)

# MQTT → InfluxDB 数据桥接
def on_mqtt_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        device_id = msg.topic.split("/")[1]

        point = (
            Point("sensor_data")
            .tag("device_id", device_id)
            .tag("location", data.get("location", "unknown"))
            .field("temperature", float(data.get("temperature", 0)))
            .field("humidity", float(data.get("humidity", 0)))
            .field("battery", int(data.get("battery", 0)))
            .time(data.get("timestamp"), WritePrecision.S)
        )

        write_api.write(bucket=INFLUX_BUCKET, record=point)
    except Exception as e:
        print(f"Error processing message: {e}")

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.subscribe("devices/+/telemetry")
mqtt_client.loop_forever()
```

### 5.3 InfluxDB 查询示例

```python
from influxdb_client import InfluxDBClient

query_api = influx_client.query_api()

# 查询最近 24 小时的温度数据
query = '''
from(bucket: "telemetry")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "temperature")
  |> filter(fn: (r) => r.device_id == "sensor_001")
  |> aggregateWindow(every: 1h, fn: mean)
  |> yield(name: "avg_temperature")
'''

result = query_api.query(query)
for table in result:
    for record in table.records:
        print(f"{record.get_time()} → {record.get_value():.2f}°C")
```

### 5.4 Grafana 可视化

```yaml
# Grafana 接入 InfluxDB 数据源
# docker-compose.yml 追加
services:
  grafana:
    image: grafana/grafana:10.4.0
    container_name: iot-grafana
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: GrafanaP@ss123
      GF_INSTALL_PLUGINS: "grafana-clock-panel,grafana-piechart-panel"
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - influxdb

volumes:
  grafana-data:
```

```sql
-- Grafana InfluxQL 查询示例（温度趋势图）
SELECT mean("temperature") AS "temp_avg",
       max("temperature")  AS "temp_max",
       min("temperature")  AS "temp_min"
FROM "sensor_data"
WHERE ("device_id" =~ /^$device$/)
  AND $timeFilter
GROUP BY time($__interval), "device_id" fill(null)
```

---

## 6. 规则引擎

### 6.1 ThingsBoard 规则链

ThingsBoard 使用可视化规则链（Rule Chain）处理设备消息。

```
[消息输入] → [消息类型路由] → [遥测数据保存] → [告警判断]
                                ↓                    │
                          [时序数据存储]         [是否超阈值?]
                                                    │
                                          ┌─────────┴─────────┐
                                          ▼                   ▼
                                   [发送告警邮件]        [发送REST回调]
```

### 6.2 自定义规则节点（JS 转换）

```javascript
// ThingsBoard Transformation 节点 — JavaScript
// 将原始遥测数据转换为标准格式

var newMsg = {};

// 温度单位转换: 华氏 → 摄氏
if (msg.temperature_f !== undefined) {
    newMsg.temperature = ((msg.temperature_f - 32) * 5 / 9).toFixed(2);
}

// 保留其他字段
newMsg.humidity = msg.humidity;
newMsg.device_id = msg.deviceId || metadata.deviceName;
newMsg.timestamp = msg.ts || Date.now();

// 数据质量标记
newMsg.quality = "good";
if (msg.temperature === null || msg.humidity === null) {
    newMsg.quality = "bad";
}

return { msg: newMsg, metadata: metadata, msgType: msgType };
```

### 6.3 告警规则配置

```javascript
// ThingsBoard 告警规则 — 温度超过阈值

// 创建告警条件
var temperature = msg.temperature;
var threshold = metadata.shared.threshold || 35.0;

if (temperature > threshold) {
    return {
        msg: {
            ...msg,
            alarm_type: "High Temperature",
            severity: temperature > threshold + 5 ? "CRITICAL" : "WARNING"
        },
        metadata: metadata,
        msgType: "ALARM"
    };
}

return { msg: msg, metadata: metadata, msgType: msgType };
```

### 6.4 EMQX 规则引擎 — Webhook 集成

```bash
# 创建 Webhook 规则动作
curl -X POST http://localhost:18083/api/v5/actions \
  -u "admin:EmqxD@sh123" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "webhook",
    "args": {
      "url": "http://api-server:8080/api/iot/callback",
      "method": "post",
      "headers": {"content-type": "application/json"},
      "body": "{\"device\":\"${device_id}\",\"temp\":${temperature},\"ts\":${ts}}"
    }
  }'
```

---

## 7. 最佳实践

### 7.1 可扩展性设计

```
设备规模规划:

  < 1,000 设备     → 单机部署 (ThingsBoard + EMQX)
  1,000 ~ 50,000   → Docker Compose + 独立数据库
  50,000 ~ 500,000 → K8s 集群 + EMQX 集群 + 分库分表
  > 500,000        → 微服务架构 + Kafka + 分布式存储
```

### 7.2 数据安全

```yaml
# 安全配置清单
security:
  device_auth:
    method: "X.509 mTLS"         # 优于 Token 认证
    cert_rotation: "365 days"
    cert_revocation: "CRL/OCSP"

  data_encryption:
    in_transit: "TLS 1.3"
    at_rest: "AES-256"

  access_control:
    rbac: true                   # 基于角色的访问控制
    audit_log: true              # 审计日志
    rate_limit: "100 msg/min/device"
```

### 7.3 OTA 固件升级

```python
# ThingsBoard OTA 固件升级流程
import requests
import hashlib

TB_URL = "http://localhost:8080"
TOKEN  = "Bearer token"

# 1. 上传固件包
with open("firmware_v2.0.0.bin", "rb") as f:
    checksum = hashlib.sha256(f.read()).hexdigest()
    f.seek(0)

    resp = requests.post(
        f"{TB_URL}/api/otaPackage",
        headers={"X-Authorization": TOKEN},
        json={
            "title": "Sensor Firmware",
            "version": "2.0.0",
            "type": "FIRMWARE",
            "deviceProfileId": {"entityType": "DEVICE_PROFILE", "id": "profile-uuid"},
            "checksumAlgorithm": "SHA256",
            "checksum": checksum,
            "fileName": "firmware_v2.0.0.bin",
            "contentType": "application/octet-stream",
            "data": f.read().hex()
        }
    )

# 2. 设备端检查并下载固件
def check_firmware_update(mqtt_client, access_token):
    # 请求当前固件信息
    mqtt_client.publish(
        "v2/fw/request/1/check",
        json.dumps({"current": "1.5.0"})
    )
    # ThingsBoard 返回最新固件信息
    # 设备下载 → 校验 → 升级
```

### 7.4 监控与告警

```yaml
# Prometheus + Grafana 监控 EMQX
# prometheus.yml
scrape_configs:
  - job_name: 'emqx'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['emqx1:18083', 'emqx2:18083']

  - job_name: 'thingsboard'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['thingsboard:9090']
```

```
# 关键监控指标

EMQX:
  - mqtt_connections_count      (当前连接数)
  - mqtt_messages_received      (消息接收速率)
  - mqtt_messages_sent          (消息发送速率)
  - session_count               (活跃会话数)
  - cpu_usage / memory_usage    (资源使用)

ThingsBoard:
  - tb_msg_count               (消息处理量)
  - tb_rule_engine_queue_size  (规则引擎队列)
  - jvm_memory_used            (JVM 内存)
  - db_query_duration          (数据库查询延迟)
```

---

## 相关页面

- [[MQTT协议实战]] — MQTT Broker 深度配置与安全
- [[嵌入式Linux开发]] — 设备端 Linux 系统构建
- [[单片机开发指南]] — 嵌入式设备固件开发
- [[边缘AI部署]] — 边缘端 AI 推理与数据预处理

---

> **最后更新**：2026-06-28 | **维护者**：嵌入式IoT知识库

---
title: MQTT协议指南
aliases:
  - MQTT
  - MQTT Protocol
  - MQTT协议
tags:
  - IoT
  - MQTT
  - 协议
  - 消息队列
  - 物联网
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: personal-notes
difficulty: intermediate
project: AI-Agent
---

# MQTT协议指南

> MQTT（Message Queuing Telemetry Transport）是一种轻量级的发布/订阅消息传输协议，专为物联网（IoT）和远程通信场景设计，具有低带宽占用、低功耗、高可靠性的特点。

## 目录

- [核心概念](#核心概念)
- [Broker（消息代理）](#broker消息代理)
- [Topic（主题）](#topic主题)
- [QoS（服务质量等级）](#qos服务质量等级)
- [保留消息（Retained Message）](#保留消息retained-message)
- [遗嘱消息（Last Will & Testament）](#遗嘱消息last-will--testament)
- [Python实战示例](#python实战示例)
- [安全与认证](#安全与认证)
- [最佳实践](#最佳实践)
- [相关页面](#相关页面)

---

## 核心概念

MQTT 基于发布/订阅（Publish/Subscribe）模式运行，解耦消息的发送者和接收者：

```
┌──────────┐    Publish     ┌──────────┐    Subscribe    ┌──────────┐
│ Publisher │ ────────────→ │  Broker  │ ──────────────→ │Subscriber │
└──────────┘                └──────────┘                  └──────────┘
     │                           │
     │      ┌──────────┐         │
     └─────→│  Broker  │←────────┘
            └──────────┘
```

| 组件 | 说明 |
|------|------|
| **Broker** | 消息代理服务器，接收所有消息并路由给订阅者 |
| **Publisher** | 消息发布者，向特定 Topic 发送消息 |
| **Subscriber** | 消息订阅者，订阅感兴趣的主题 |
| **Topic** | 消息主题，层级化的路由地址 |

---

## Broker（消息代理）

### 常见 Broker 实现

| Broker | 语言 | 特点 | 适用场景 |
|--------|------|------|----------|
| **EMQX** | Erlang | 高性能、百万级连接、规则引擎 | 大规模生产环境 |
| **Mosquitto** | C | 轻量、开源、低资源占用 | 边缘网关、开发测试 |
| **HiveMQ** | Java | 企业级、高可用集群 | 企业IoT平台 |
| **RabbitMQ-MQTT** | Erlang | 与AMQP互通 | 混合消息系统 |

### Docker 快速启动 Mosquitto

```yaml
# docker-compose.yml
version: '3.8'
services:
  mosquitto:
    image: eclipse-mosquitto:2.0
    container_name: mosquitto
    ports:
      - "1883:1883"   # MQTT
      - "9001:9001"   # WebSocket
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto_data:/mosquitto/data
      - mosquitto_log:/mosquitto/log

volumes:
  mosquitto_data:
  mosquitto_log:
```

```ini
# mosquitto.conf
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
```

```bash
docker-compose up -d
```

---

## Topic（主题）

Topic 是 MQTT 的消息路由地址，使用 `/` 分隔层级，类似文件路径：

```
home/         # 顶层
home/living_room/      # 子层级
home/living_room/sensor/temperature    # 具体设备
```

### 通配符

| 通配符 | 说明 | 示例 |
|--------|------|------|
| `+` | 单层匹配 | `home/+/temperature` 匹配 `home/room1/temperature` |
| `#` | 多层匹配（必须放最后） | `home/#` 匹配 `home/` 下所有层级 |

```python
# 通配符订阅示例
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # 订阅所有房间的温度
    client.subscribe("home/+/temperature")
    # 订阅客厅所有传感器
    client.subscribe("home/living_room/#")

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}, Payload: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
```

### Topic 设计最佳实践

```
# 推荐的命名规范
{project}/{device_type}/{device_id}/{data_type}

# 示例
smarthome/sensor/TH001/temperature
smarthome/sensor/TH001/humidity
smarthome/actuator/LIGHT001/status
smarthome/gateway/GW01/$online
```

---

## QoS（服务质量等级）

MQTT 定义了三个 QoS 级别来保证消息的可靠投递：

| QoS | 名称 | 交互次数 | 可靠性 | 开销 |
|-----|------|----------|--------|------|
| **0** | At most once（最多一次） | 1 | ⭐ | 最低 |
| **1** | At least once（至少一次） | 2 | ⭐⭐⭐ | 中等 |
| **2** | Exactly once（恰好一次） | 4 | ⭐⭐⭐⭐⭐ | 最高 |

### QoS 0 — Fire and Forget

```
Sender ──── PUBLISH ────→ Receiver
```
消息发送一次，不确认。适用于高频低价值数据（如实时温度）。

### QoS 1 — At Least Once

```
Sender ──── PUBLISH ────→ Receiver
Sender ←── PUBACK ──────  Receiver
```
保证消息至少到达一次，可能重复。适用于告警、状态变更。

### QoS 2 — Exactly Once

```
Sender ──── PUBLISH ────→ Receiver
Sender ←── PUBREC ──────  Receiver
Sender ──── PUBREL ────→ Receiver
Sender ←── PUBCOMP ─────  Receiver
```
确保消息恰好到达一次。适用于计费、控制指令。

```python
# 不同 QoS 的使用场景
client.publish("device/sensor/temp", payload="25.5", qos=0)  # 高频遥测
client.publish("device/alarm/fire", payload="ALERT", qos=1)   # 告警事件
client.publish("device/control/relay", payload="ON", qos=2)   # 控制指令
```

---

## 保留消息（Retained Message）

Broker 会保留最后一条设置了 `retain=True` 的消息。当新订阅者连接时，会立即收到这条保留消息。

```python
# 发布保留消息 - 设备当前状态
client.publish(
    "device/sensor/TH001/status",
    payload='{"online": true, "battery": 87}',
    qos=1,
    retain=True
)

# 清除保留消息 - 发布一个空消息
client.publish("device/sensor/TH001/status", payload="", retain=True)
```

### 适用场景

- ✅ 设备状态同步（开关状态、当前配置）
- ✅ 最近一条传感器读数
- ❌ 高频遥测数据（会导致 Broker 频繁写入）

---

## 遗嘱消息（Last Will & Testament）

客户端连接时可以注册一条"遗嘱消息"。当客户端异常断开（如网络中断）时，Broker 自动发布这条消息。

```python
import json
import paho.mqtt.client as mqtt

will_payload = json.dumps({
    "device_id": "ESP32_001",
    "status": "offline",
    "timestamp": "2026-06-28T10:00:00Z"
})

client = mqtt.Client(client_id="ESP32_001")
client.will_set(
    topic="device/status/ESP32_001",
    payload=will_payload,
    qos=1,
    retain=True  # 保留遗嘱，让新订阅者也能看到离线状态
)

client.connect("broker.example.com", 1883, 60)
```

### 遗嘱消息注意事项

1. **遗嘱仅在连接时注册**，之后不能修改
2. 正常断开（`disconnect()`）不会触发遗嘱
3. 结合 `retain=True` 可实现设备在线/离线状态管理

---

## Python实战示例

### 完整的设备模拟器

```python
"""
IoT 设备模拟器 - 模拟温度传感器，通过 MQTT 上报数据
"""
import json
import time
import random
import signal
import sys
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
DEVICE_ID = "SENSOR_TH001"
BASE_TOPIC = f"iot/sensor/{DEVICE_ID}"

class IoTSensor:
    def __init__(self):
        self.client = mqtt.Client(client_id=DEVICE_ID)
        self.running = True
        self._setup_client()

    def _setup_client(self):
        # 设置遗嘱消息
        will = json.dumps({
            "device_id": DEVICE_ID,
            "status": "offline",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.client.will_set(f"{BASE_TOPIC}/status", will, qos=1, retain=True)

        # 注册回调
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{DEVICE_ID}] Connected to broker")
            # 发布在线状态（保留）
            status = json.dumps({
                "device_id": DEVICE_ID,
                "status": "online",
                "firmware": "v1.2.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            client.publish(f"{BASE_TOPIC}/status", status, qos=1, retain=True)
            # 订阅控制命令
            client.subscribe(f"{BASE_TOPIC}/cmd/#", qos=1)
        else:
            print(f"Connection failed with code {rc}")

    def _on_message(self, client, userdata, msg):
        """处理下行控制命令"""
        topic_parts = msg.topic.split("/")
        cmd = topic_parts[-1]
        payload = msg.payload.decode()
        print(f"[CMD] {cmd}: {payload}")

        if cmd == "set_interval":
            new_interval = int(payload)
            print(f"Report interval changed to {new_interval}s")

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Unexpected disconnection, rc={rc}")

    def run(self):
        self.client.connect(BROKER, PORT, keepalive=60)
        self.client.loop_start()

        try:
            while self.running:
                data = {
                    "device_id": DEVICE_ID,
                    "temperature": round(random.uniform(20.0, 28.0), 2),
                    "humidity": round(random.uniform(40.0, 70.0), 2),
                    "battery": random.randint(60, 100),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                # QoS 0 上报遥测数据（高频，无需确认）
                self.client.publish(
                    f"{BASE_TOPIC}/telemetry",
                    payload=json.dumps(data),
                    qos=0
                )
                print(f"[TELEMETRY] {data['temperature']}°C, {data['humidity']}%")
                time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    sensor = IoTSensor()
    sensor.run()
```

### 订阅端（数据消费）

```python
"""
MQTT 数据订阅器 - 接收并处理传感器数据
"""
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected: {rc}")
    client.subscribe("iot/sensor/+/telemetry", qos=0)
    client.subscribe("iot/sensor/+/status", qos=1)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    topic = msg.topic
    if "/status" in topic:
        print(f"[STATUS] {data['device_id']}: {data['status']}")
    elif "/telemetry" in topic:
        print(f"[DATA] {data['device_id']}: {data['temperature']}°C, "
              f"{data['humidity']}%, battery={data['battery']}%")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# TLS/SSL 配置（生产环境）
# client.tls_set(ca_certs="/path/to/ca.crt", certfile="client.crt", keyfile="client.key")

client.connect("localhost", 1883, 60)
client.loop_forever()
```

---

## 安全与认证

### 用户名/密码认证

```python
client.username_pw_set("device_user", "secure_password_123")
```

### TLS/SSL 加密

```python
# mosquitto.conf 配置
# listener 8883
# certfile /mosquitto/certs/server.crt
# keyfile /mosquitto/certs/server.key
# cafile /mosquitto/certs/ca.crt
# require_certificate true

# Python 客户端
client.tls_set(
    ca_certs="/path/to/ca.crt",
    certfile="/path/to/client.crt",
    keyfile="/path/to/client.key",
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.connect("broker.example.com", 8883, 60)
```

### 基于证书的双向认证（mTLS）

```python
import ssl

client = mqtt.Client()
client.tls_set(
    ca_certs="ca.crt",
    certfile="device.crt",
    keyfile="device.key",
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
# 证书中 CN 作为设备身份
client.connect("broker.example.com", 8883, keepalive=60)
```

---

## 最佳实践

### 1. Topic 设计原则
- 使用 `device_type/device_id/data_type` 三段式命名
- 保留 `$` 前缀给系统主题（如 `$SYS/broker/uptime`）
- 避免过深的层级（建议不超过5层）

### 2. QoS 选择策略
| 场景 | 推荐QoS | 原因 |
|------|---------|------|
| 实时遥测（温度、位置） | QoS 0 | 高频数据，偶尔丢失可接受 |
| 告警/事件 | QoS 1 | 确保到达，可容忍重复 |
| 控制指令/计费 | QoS 2 | 必须精确执行一次 |

### 3. 性能调优
```python
# 批量发送时减少 flush
client = mqtt.Client()
client.max_queued_messages_set(1000)  # 队列上限
client.connect("broker", 1883, 60)
client.loop_start()

for i in range(100):
    client.publish(f"batch/data/{i}", payload=str(i), qos=1)
    # QoS 1/2 会自动排队等待 ACK

client.loop_stop()
client.disconnect()
```

### 4. 客户端 ID 管理
- 每个设备使用唯一的 `client_id`（如设备序列号）
- Broker 会踢掉相同 ID 的旧连接
- 临时调试客户端可使用随机 ID

### 5. 心跳与重连
```python
# 设置遗嘱延迟
client = mqtt.Client()
# keepalive=60 表示60秒内没有消息则发送 PINGREQ
client.connect("broker", 1883, keepalive=60)

# 自动重连
client.reconnect_delay_set(min_delay=1, max_delay=120)
client.connect("broker", 1883, 60)
```

### 6. 安全检查清单
- [ ] 生产环境关闭匿名访问
- [ ] 启用 TLS/SSL（端口 8883）
- [ ] 使用强密码或证书认证
- [ ] 限制 Topic ACL（设备只能发布自己的主题）
- [ ] 设置 `clean_session` 策略
- [ ] 定期更换凭据

---

## 相关页面

- [[时序数据库]] — MQTT 数据的持久化存储
- [[设备管理平台]] — 基于 MQTT 的设备生命周期管理
- [[工业网关开发]] — MQTT 作为网关上行协议
- [[LoRaWAN开发]] — LoRaWAN 后端集成 MQTT

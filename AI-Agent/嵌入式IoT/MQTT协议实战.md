---
title: "MQTT协议实战"
aliases:
  - MQTT Protocol
  - MQTT实战
  - MQTT消息队列遥测传输
tags:
  - mqtt
  - iot
  - networking
  - protocol
  - broker
  - emqx
  - mosquitto
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: "原创整理 + MQTT v5.0 规范"
difficulty: intermediate
project: "嵌入式IoT知识库"
---

# MQTT协议实战

> MQTT（Message Queuing Telemetry Transport）是物联网领域最常用的轻量级发布/订阅消息协议。本页涵盖 Broker 配置、QoS 级别、Retained 消息、主题设计、安全认证等核心实战内容。

---

## 目录

- [1. MQTT 协议基础](#1-mqtt-协议基础)
- [2. Broker 配置](#2-broker-配置)
- [3. QoS 服务质量级别](#3-qos-服务质量级别)
- [4. Retained 消息与 Will 消息](#4-retained-消息与-will-消息)
- [5. 主题设计规范](#5-主题设计规范)
- [6. 安全认证与加密](#6-安全认证与加密)
- [7. 客户端编程实战](#7-客户端编程实战)
- [8. 最佳实践](#8-最佳实践)
- [相关页面](#相关页面)

---

## 1. MQTT 协议基础

### 1.1 发布/订阅模型

```
┌──────────┐    Publish     ┌─────────┐    Push     ┌──────────┐
│ Publisher │ ──────────►   │  Broker  │ ────────►  │ Subscriber│
└──────────┘   topic/data   └─────────┘  topic/data └──────────┘
```

- **Publisher**：发布消息到指定主题（Topic）
- **Broker**：消息代理，负责路由消息
- **Subscriber**：订阅感兴趣的主题

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Topic | 消息主题，层级式路径，如 `home/livingroom/temperature` |
| Payload | 消息负载（二进制数据） |
| QoS | 服务质量等级（0、1、2） |
| Session | 客户端与 Broker 之间的会话 |
| Last Will | 客户端异常断开时的遗嘱消息 |

---

## 2. Broker 配置

### 2.1 Mosquitto 安装与配置

```bash
# Ubuntu / Debian
sudo apt install mosquitto mosquitto-clients

# Docker 快速部署
docker run -d --name mosquitto \
  -p 1883:1883 -p 9001:9001 \
  -v /opt/mosquitto/config:/mosquitto/config \
  -v /opt/mosquitto/data:/mosquitto/data \
  -v /opt/mosquitto/log:/mosquitto/log \
  eclipse-mosquitto
```

```bash
# /etc/mosquitto/mosquitto.conf

# --- 基础配置 ---
pid_file /var/run/mosquitto.pid
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# --- 监听端口 ---
# 无加密，开发环境
listener 1883 0.0.0.0

# TLS 加密端口
listener 8883 0.0.0.0
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
cafile /etc/mosquitto/certs/ca.crt
tls_version tlsv1.2

# WebSocket 端口（Web 客户端）
listener 9001 0.0.0.0
protocol websockets

# --- 认证 ---
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl

# --- 消息限制 ---
message_size_limit 4096
max_inflight_messages 20
max_queued_messages 1000
max_connections 2000

# --- 桥接配置 ---
# connection bridge-to-cloud
# address cloud-broker.example.com:8883
# topic home/# both 1
# bridge_protocol_version mqttv311
# bridge_cafile /etc/mosquitto/certs/cloud_ca.crt
```

### 2.2 用户与 ACL 管理

```bash
# 创建用户密码文件
mosquitto_passwd -c /etc/mosquitto/passwd admin
# 输入密码后自动创建哈希

# 追加用户
mosquitto_passwd -b /etc/mosquitto/passwd device_001 DeviceP@ss123
mosquitto_passwd -b /etc/mosquitto/passwd device_002 DeviceP@ss456

# 重启生效
sudo systemctl restart mosquitto
```

```bash
# /etc/mosquitto/acl — 访问控制列表

# 管理员：全权限
user admin
topic readwrite #

# 设备001：仅能发布/订阅自己的主题
user device_001
topic readwrite devices/device_001/#
topic read commands/device_001/#

# 匿名用户：禁用
topic deny #

# 模式匹配（基于用户名）
pattern readwrite devices/%u/#
pattern read commands/%u/#
```

### 2.3 EMQX Broker 部署

```bash
# Docker 部署 EMQX（企业级 Broker）
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8083:8083 \
  -p 8084:8084 \
  -p 8883:8883 \
  -p 18083:18083 \
  emqx/emqx:latest

# 访问 Dashboard: http://localhost:18083
# 默认账号: admin / public
```

```yaml
# EMQX 配置示例 emqx.conf
listeners.tcp.default {
  bind = "0.0.0.0:1883"
  max_connections = 102400
}

listeners.ssl.default {
  bind = "0.0.0.0:8883"
  ssl_options {
    keyfile  = "/etc/emqx/certs/server.key"
    certfile = "/etc/emqx/certs/server.crt"
    cacertfile = "/etc/emqx/certs/ca.crt"
    verify = verify_peer
    fail_if_no_peer_cert = true
  }
}

authn = [
  {
    mechanism = password_based
    backend = built_in_database
    password_hash_algorithm { name = sha256, salt_position = suffix }
  }
]

rule_engine {
  rules {
    "store_sensor_data" {
      sql = "SELECT * FROM \"devices/+/telemetry\""
      actions = ["bridge_to_influxdb"]
    }
  }
}
```

---

## 3. QoS 服务质量级别

### 3.1 三个 QoS 级别

| QoS | 名称 | 交互次数 | 保证 | 适用场景 |
|-----|------|----------|------|----------|
| 0 | At most once | 1（PUBLISH） | 不保证送达 | 高频遥测数据（温度、加速度） |
| 1 | At least once | 2（PUBLISH → PUBACK） | 至少送达一次 | 告警、事件通知 |
| 2 | Exactly once | 4（PUBLISH→PUBREC→PUBREL→PUBCOMP） | 恰好一次 | 计费、控制指令 |

### 3.2 QoS 选择建议

```
QoS 0  →  传感器数据流（容忍少量丢失）
QoS 1  →  状态更新、告警推送（大多数 IoT 场景）
QoS 2  →  付费操作、关键控制指令
```

### 3.3 订阅 QoS

```bash
# 订阅 QoS 取发布 QoS 和订阅 QoS 中的较小值
mosquitto_sub -h localhost -t "home/temperature" -q 1
mosquitto_pub  -h localhost -t "home/temperature" -m "25.5" -q 1
```

---

## 4. Retained 消息与 Will 消息

### 4.1 Retained 消息

Retained 消息会被 Broker 保存，新订阅者连接后立即收到最后一条 Retained 消息。

```bash
# 发布 Retained 消息（状态数据）
mosquitto_pub -h localhost -t "devices/device_001/status" \
  -m '{"online":true,"ip":"192.168.1.50","fw":"2.1.0"}' \
  -r -q 1

# 新订阅者连接后立即收到
mosquitto_sub -h localhost -t "devices/device_001/status" -q 1

# 清除 Retained 消息（发布空 payload）
mosquitto_pub -h localhost -t "devices/device_001/status" -n -r -q 1
```

```python
import paho.mqtt.client as mqtt
import json

client = mqtt.Client()

# 发布 Retained 消息
payload = json.dumps({
    "device_id": "sensor_001",
    "temperature": 25.6,
    "humidity": 60.2,
    "timestamp": "2026-06-28T10:30:00Z"
})

client.publish(
    "devices/sensor_001/state",
    payload=payload,
    qos=1,
    retain=True
)
```

### 4.2 Last Will 遗嘱消息

```python
import paho.mqtt.client as mqtt
import json
import time

will_payload = json.dumps({
    "device_id": "sensor_001",
    "status": "offline",
    "reason": "unexpected_disconnect",
    "timestamp": time.time()
})

client = mqtt.Client(client_id="sensor_001")
client.will_set(
    topic="devices/sensor_001/status",
    payload=will_payload,
    qos=1,
    retain=True
)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        # 连接成功后，覆盖 Will 消息
        client.publish(
            "devices/sensor_001/status",
            payload=json.dumps({"device_id": "sensor_001", "status": "online"}),
            qos=1, retain=True
        )
    else:
        print(f"Connection failed, rc={rc}")

client.on_connect = on_connect
client.connect("broker.example.com", 1883, 60)
client.loop_forever()
```

---

## 5. 主题设计规范

### 5.1 层级命名约定

```
项目/区域/设备类型/设备ID/数据类型
└── IoT/Building/Floor3/Sensor/Temperature
```

**推荐主题结构：**

```
# 设备遥测数据（设备 → 平台）
devices/{device_id}/telemetry/{metric}
devices/sensor_001/telemetry/temperature
devices/sensor_001/telemetry/humidity

# 设备命令（平台 → 设备）
commands/{device_id}/{action}
commands/sensor_001/set_interval
commands/sensor_001/reboot

# 设备状态
devices/{device_id}/status        (retained)
devices/{device_id}/firmware      (retained)

# 广播/组播
broadcast/firmware_update
broadcast/time_sync

# 事件/告警
events/{device_id}/{severity}
events/sensor_001/warning
events/sensor_001/critical
```

### 5.2 通配符订阅

```bash
# + 匹配单层
# 匹配 devices/sensor_001/telemetry/* (单层)
mosquitto_sub -t "devices/sensor_001/telemetry/+"

# # 匹配多层（必须在末尾）
# 匹配 devices/ 下所有消息
mosquitto_sub -t "devices/#"

# 组合使用
mosquitto_sub -t "devices/+/telemetry/temperature"  # 所有设备的温度
```

### 5.3 主题设计最佳实践

```
✅ 好的设计:
devices/sensor_001/telemetry/temperature
factory/line_a/robot_003/status

❌ 避免的设计:
sensor001temperature        # 无层级
devices/sensor/001/...      # 避免 ID 拆分
my topic with spaces        # 避免空格
devices/sensor_001/../../../etc/passwd  # 避免目录穿越
```

---

## 6. 安全认证与加密

### 6.1 生成 TLS 证书

```bash
#!/bin/bash
# generate_certs.sh — 生成 MQTT TLS 证书链

# 1. 生成 CA 私钥和证书
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
    -subj "/C=CN/O=MyIoT/CN=MyIoT-CA"

# 2. 生成服务器私钥和 CSR
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj "/C=CN/O=MyIoT/CN=broker.myiot.local"

# 3. 签发服务器证书
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out server.crt -days 825 \
    -extfile <(printf "subjectAltName=DNS:broker.myiot.local,IP:192.168.1.100")

# 4. 生成客户端证书（每台设备）
openssl genrsa -out device_001.key 2048
openssl req -new -key device_001.key -out device_001.csr \
    -subj "/C=CN/O=MyIoT/CN=device_001"
openssl x509 -req -in device_001.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out device_001.crt -days 825
```

### 6.2 双向 TLS 认证

```python
import ssl
import paho.mqtt.client as mqtt

client = mqtt.Client(client_id="device_001")

# 配置 TLS
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations("/certs/ca.crt")           # 验证 Broker
context.load_cert_chain(
    certfile="/certs/device_001.crt",                     # 客户端证书
    keyfile="/certs/device_001.key"                       # 客户端私钥
)
context.check_hostname = False  # 生产环境应设为 True
context.verify_mode = ssl.CERT_REQUIRED

client.tls_set_context(context)

# 设置用户名密码（双重认证）
client.username_pw_set("device_001", "SecureP@ss123")

client.connect("broker.myiot.local", 8883, 60)
client.loop_forever()
```

### 6.3 C 语言嵌入式客户端（mbedTLS + Paho MQTT-C）

```c
#include "MQTTClient.h"
#include <stdio.h>
#include <string.h>

#define BROKER_ADDRESS  "ssl://broker.myiot.local:8883"
#define CLIENT_ID       "device_001"
#define TOPIC_PUB       "devices/device_001/telemetry"
#define TOPIC_SUB       "commands/device_001/#"

static Network network;
static MQTTClient client;
static unsigned char sendbuf[512], readbuf[512];

void messageArrived(MessageData* data) {
    printf("Received: %.*s\n",
           (int)data->message->payloadlen,
           (char*)data->message->payload);
}

int mqtt_init(void) {
    NetworkInit(&network);
    // 在嵌入式平台上，此处使用 mbedTLS 配置 SSL
    // NetworkConnect(&network, "broker.myiot.local", 8883);

    MQTTPacket_connectData opts = MQTTPacket_connectData_initializer;
    opts.clientID.cstring = CLIENT_ID;
    opts.username.cstring = "device_001";
    opts.password.cstring = "SecureP@ss123";
    opts.keepAliveInterval = 60;
    opts.cleansession = 0;  // 持久会话

    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf),
                   readbuf, sizeof(readbuf));

    int rc = MQTTConnect(&client, &opts);
    if (rc != SUCCESS) {
        printf("MQTT connect failed: %d\n", rc);
        return -1;
    }

    MQTTSubscribe(&client, TOPIC_SUB, QOS1, messageArrived);
    return 0;
}

void mqtt_publish_telemetry(float temperature, float humidity) {
    MQTTMessage message;
    char payload[128];

    snprintf(payload, sizeof(payload),
             "{\"temp\":%.1f,\"humi\":%.1f}", temperature, humidity);

    message.qos = QOS1;
    message.retained = 0;
    message.payload = payload;
    message.payloadlen = strlen(payload);

    MQTTPublish(&client, TOPIC_PUB, &message);
}
```

---

## 7. 客户端编程实战

### 7.1 Python 异步客户端

```python
import paho.mqtt.client as mqtt
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BROKER = "broker.myiot.local"
PORT = 8883
DEVICE_ID = "sensor_001"

class IoTMQTTClient:
    def __init__(self, device_id, broker, port=1883):
        self.device_id = device_id
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id=device_id, clean_session=False)
        self._setup_callbacks()
        self._setup_will()

    def _setup_callbacks(self):
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish

    def _setup_will(self):
        will = json.dumps({
            "device_id": self.device_id,
            "status": "offline",
            "timestamp": time.time()
        })
        self.client.will_set(
            f"devices/{self.device_id}/status",
            payload=will, qos=1, retain=True
        )

    def _on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected (rc={rc}), session_present={flags.get('session present', False)}")
        # 发布在线状态
        client.publish(
            f"devices/{self.device_id}/status",
            payload=json.dumps({"status": "online", "timestamp": time.time()}),
            qos=1, retain=True
        )
        # 订阅命令主题
        client.subscribe(f"commands/{self.device_id}/#", qos=1)

    def _on_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected (rc={rc}), will retry...")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Command [{msg.topic}]: {payload}")
            self._handle_command(msg.topic, payload)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {msg.payload}")

    def _on_publish(self, client, userdata, mid):
        logger.debug(f"Message {mid} published")

    def _handle_command(self, topic, payload):
        parts = topic.split("/")
        if len(parts) >= 3:
            action = parts[2]
            if action == "set_interval":
                self.interval = payload.get("value", 30)
            elif action == "reboot":
                logger.info("Reboot command received")

    def publish_telemetry(self, data: dict):
        topic = f"devices/{self.device_id}/telemetry"
        payload = json.dumps({
            **data,
            "device_id": self.device_id,
            "timestamp": time.time()
        })
        info = self.client.publish(topic, payload, qos=1)
        return info.rc

    def connect(self, username=None, password=None):
        if username:
            self.client.username_pw_set(username, password)
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


# 使用示例
if __name__ == "__main__":
    client = IoTMQTTClient("sensor_001", "broker.myiot.local", 8883)
    client.connect(username="sensor_001", password="SecureP@ss123")

    try:
        while True:
            telemetry = {
                "temperature": 25.6,
                "humidity": 60.2,
                "battery": 87
            }
            client.publish_telemetry(telemetry)
            time.sleep(30)
    except KeyboardInterrupt:
        client.disconnect()
```

### 7.2 测试与调试命令

```bash
# 终端1：订阅
mosquitto_sub -h broker.myiot.local -p 8883 \
  --cafile ca.crt --cert device_001.crt --key device_001.key \
  -u device_001 -P "SecureP@ss123" \
  -t "devices/#" -q 1 -v

# 终端2：发布
mosquitto_pub -h broker.myiot.local -p 8883 \
  --cafile ca.crt --cert admin.crt --key admin.key \
  -u admin -P "AdminP@ss" \
  -t "devices/sensor_001/telemetry" \
  -m '{"temp":25.6,"humi":60.2}' -q 1

# 查看 Broker 状态
mosquitto_sub -h broker.myiot.local -t '$SYS/#' -v
```

---

## 8. 最佳实践

### 8.1 性能调优

```bash
# Mosquitto 连接数优化
# /etc/security/limits.conf
mosquitto  soft  nofile  65535
mosquitto  hard  nofile  65535

# 系统级
sysctl -w net.core.somaxconn=65535
sysctl -w net.ipv4.tcp_max_syn_backlog=65535
```

### 8.2 安全清单

| 项目 | 措施 | 优先级 |
|------|------|--------|
| 禁用匿名访问 | `allow_anonymous false` | 🔴 高 |
| 强制 TLS 1.2+ | `tls_version tlsv1.2` | 🔴 高 |
| 客户端证书认证 | 双向 mTLS | 🔴 高 |
| ACL 限制主题 | 每个 device 限定自己主题 | 🟡 中 |
| Client ID 规范 | 使用设备唯一 ID | 🟡 中 |
| 密码强度 | 16+ 字符，定期轮换 | 🟡 中 |
| 网络隔离 | Broker 部署在内网 | 🟢 基础 |

### 8.3 消息格式建议

```json
// 推荐：使用 JSON，结构清晰
{
  "device_id": "sensor_001",
  "timestamp": 1719567000,
  "metrics": {
    "temperature": 25.6,
    "humidity": 60.2
  }
}

// 带宽受限场景：使用 Protobuf / CBOR
// 或紧凑 JSON：
{"d":"s001","t":1719567000,"m":{"t":25.6,"h":60.2}}
```

---

## 相关页面

- [[嵌入式Linux开发]] — 在嵌入式设备上运行 MQTT 客户端
- [[单片机开发指南]] — 单片机上的 MQTT 实现方案
- [[IoT平台搭建]] — ThingsBoard / EMQX 平台集成
- [[边缘AI部署]] — MQTT 传输边缘推理结果

---

> **最后更新**：2026-06-28 | **维护者**：嵌入式IoT知识库

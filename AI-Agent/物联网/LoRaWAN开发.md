---
title: LoRaWAN开发
aliases:
  - LoRaWAN
  - LoRa
  - LPWAN
  - 低功耗广域网
tags:
  - IoT
  - LoRaWAN
  - LPWAN
  - 无线通信
  - 低功耗
  - 物联网
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: personal-notes
difficulty: advanced
project: AI-Agent
---

# LoRaWAN开发

> LoRaWAN（Long Range Wide Area Network）是一种低功耗广域网（LPWAN）通信协议，基于 LoRa 调制技术，专为物联网设计，支持远距离通信（城市可达 2-5km，郊区可达 15km+）、低功耗（电池可使用数年）和大规模设备连接。

## 目录

- [LoRaWAN 架构](#lorawan-架构)
- [核心概念](#核心概念)
- [设备类别](#设备类别)
- [Join流程（入网激活）](#join流程入网激活)
- [数据加密与安全](#数据加密与安全)
- [MAC命令](#mac命令)
- [网关开发](#网关开发)
- [终端设备开发](#终端设备开发)
- [网络服务器集成](#网络服务器集成)
- [最佳实践](#最佳实践)
- [相关页面](#相关页面)

---

## LoRaWAN 架构

```
                         ┌──────────────────────┐
                         │   Application Server  │
                         │   (应用服务器)         │
                         └──────────┬───────────┘
                                    │ HTTPS / MQTT
                         ┌──────────┴───────────┐
                         │   Network Server     │
                         │   (网络服务器)         │
                         │   - 设备管理          │
                         │   - MAC层管理         │
                         │   - 消息去重          │
                         │   - 速率自适应 (ADR)  │
                         └──────────┬───────────┘
                                    │ UDP/HTTPS (Packet Forwarder)
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
   ┌──────┴──────┐          ┌──────┴──────┐          ┌──────┴──────┐
   │  Gateway 1  │          │  Gateway 2  │          │  Gateway 3  │
   │  (网关)     │          │  (网关)     │          │  (网关)     │
   │  仅转发     │          │             │          │             │
   └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
          │  LoRa Radio            │                        │
     ┌────┴────────┐         ┌────┴────┐              ┌────┴────┐
     │ End Device  │         │ End Dev │   ...        │ End Dev │
     │ (终端设备)   │         │         │              │         │
     └─────────────┘         └─────────┘              └─────────┘
```

### LoRaWAN vs 其他无线协议

| 特性 | LoRaWAN | NB-IoT | Wi-Fi | BLE | Zigbee |
|------|---------|--------|-------|-----|--------|
| **距离** | 2-15 km | 1-10 km | 50-100 m | 10-50 m | 10-100 m |
| **功耗** | 极低 | 低 | 高 | 低 | 低 |
| **数据率** | 0.3-50 kbps | 20-250 kbps | 600 Mbps+ | 1-2 Mbps | 250 kbps |
| **连接数** | 万级 | 万级 | 数十 | 数十 | 数百 |
| **频段** | 免授权 | 授权频段 | 2.4/5GHz | 2.4GHz | 2.4GHz |
| **电池寿命** | 5-10年 | 5-10年 | 数小时 | 数月 | 数月 |
| **成本** | 低 | 中 | 低 | 低 | 低 |

---

## 核心概念

### 频段

```
频段分配（中国）:
├── CN470 (470-510 MHz)   — 中国主要频段
├── EU868 (863-870 MHz)   — 欧洲
├── US915 (902-928 MHz)   — 美国
└── AS923 (920-923 MHz)   — 亚洲其他地区
```

### 调制参数

| 参数 | 说明 | 影响 |
|------|------|------|
| **SF (Spreading Factor)** | 扩频因子 (7-12) | SF越大→距离越远→速率越低→功耗越高 |
| **BW (Bandwidth)** | 带宽 (125/250/500 kHz) | BW越大→速率越高→灵敏度降低 |
| **CR (Coding Rate)** | 编码率 (4/5 ~ 4/8) | CR越高→抗干扰越强→有效速率降低 |

### 数据速率与距离的关系

```
SF7  → 最快速率 (≈5469 bps) → 距离 ≈ 2 km
SF8  → 快速     (≈3125 bps) → 距离 ≈ 3.5 km
SF9  → 中速     (≈1760 bps) → 距离 ≈ 5 km
SF10 → 慢速     (≈980 bps)  → 距离 ≈ 8 km
SF11 → 很慢     (≈540 bps)  → 距离 ≈ 11 km
SF12 → 最慢     (≈293 bps)  → 距离 ≈ 15 km
```

### ADR（自适应数据速率）

```
设备 ──── 上行 (多次, 不同 SF) ────→ 网关
网络服务器分析所有网关接收到的 SNR 和 RSSI:
    ↓
最优 SF 选择:
    SNR 高 → 降低 SF (提高速率)
    SNR 低 → 提高 SF (增加可靠性)
    ↓
网络服务器 ──── LinkADRReq (MAC命令) ────→ 设备
```

---

## 设备类别

LoRaWAN 定义了三种设备类别，适用于不同场景：

### Class A（所有终端的默认模式）

```
终端                         网关
  │                            │
  ├── Uplink ─────────────────→│    发送上行数据
  │                            │
  │   RX1 (1s after uplink)    │
  │←────────── Downlink ───────┤    接收窗口1
  │                            │
  │   RX2 (2s after uplink)    │
  │←────────── Downlink ───────┤    接收窗口2
  │                            │
  ├── SLEEP (最低功耗) ─────────│    睡眠直到下次上行
  │                            │
  (周期性重复)
```

| 特性 | 说明 |
|------|------|
| **功耗** | 最低（大部分时间睡眠） |
| **下行延迟** | 等待下次上行后才接收下行 |
| **适用场景** | 温湿度传感器、智能水表 |
| **电池寿命** | 5-10年 |

### Class B（定时接收窗口）

```
终端                           网关
  │                              │
  │←──── Beacon (128s周期) ──────│    时间同步信标
  │                              │
  │   在 Beacon 后的固定时隙     │
  │   开启 ping slot            │
  │←──── Downlink (ping slot) ───│    定时接收窗口
  │                              │
  ├── Uplink ──────────────────→│
  │   RX1 / RX2 (同 Class A)    │
  │←──── Downlink ───────────────│
```

| 特性 | 说明 |
|------|------|
| **下行延迟** | 最多 128 秒 |
| **功耗** | 略高于 Class A |
| **适用场景** | 需要定时下行的应用 |

### Class C（持续接收）

```
终端                           网关
  │                              │
  ├── Uplink ──────────────────→│
  │                              │
  │  RX1 (1s后)                  │
  │←──── Downlink ───────────────│
  │                              │
  │  RX2 (持续接收!)              │    除发送外几乎持续监听
  │←──── Downlink ───────────────│
  │←──── Downlink ───────────────│
  │                              │
```

| 特性 | 说明 |
|------|------|
| **下行延迟** | 几乎为 0 |
| **功耗** | 最高 |
| **适用场景** | 常供电设备、执行器 |
| **电池** | 不适合电池供电 |

### 三类对比

| 特性 | Class A | Class B | Class C |
|------|---------|---------|---------|
| 功耗 | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 下行延迟 | 高 | 中 | 极低 |
| 复杂度 | 低 | 高 | 中 |
| 适用场景 | 传感器 | 混合 | 执行器 |

---

## Join流程（入网激活）

### OTAA（Over-The-Air Activation，空中激活）

OTAA 是推荐的入网方式，设备在每次连接时协商会话密钥。

```
设备 (End Device)                      网络服务器 (Network Server)
    │                                            │
    │  已知:                                      │  已知:
    │  - DevEUI (设备唯一ID)                      │  - 所有设备的 DevEUI
    │  - AppEUI (应用唯一ID)                      │  - AppKey (每个设备)
    │  - AppKey (应用密钥)                        │
    │                                            │
    │  ─── JoinRequest ──────────────────────→   │
    │  { DevEUI, AppEUI, DevNonce, MIC }         │
    │                                            │
    │                          验证设备          │
    │                          生成 DevAddr       │
    │                          生成会话密钥:       │
    │                          - AppSKey          │
    │                          - NwkSKey         │
    │                                            │
    │  ←──── JoinAccept ──────────────────────   │
    │  { AppNonce, NetID, DevAddr, DLSettings,   │
    │    RxDelay, CFList, MIC }                  │
    │                                            │
    │  设备计算会话密钥:                           │
    │  AppSKey = f(AppKey, AppNonce)             │
    │  NwkSKey = f(AppKey, AppNonce)             │
    │                                            │
    │  保存 DevAddr 和会话密钥                    │
    │                                            │
    │  ═══ 入网成功, 可收发数据 ═══               │
```

#### JoinRequest 消息解析

```
┌─────────────────────────────────────────────┐
│ JoinRequest (23 bytes)                      │
├─────────────────────────────────────────────┤
│ AppEUI    │ 8 bytes │ 小端序                │
│ DevEUI    │ 8 bytes │ 小端序                │
│ DevNonce  │ 2 bytes │ 随机数 (防重放攻击)     │
│ MIC       │ 4 bytes │ 消息完整性码 (CMAC)    │
└─────────────────────────────────────────────┘
```

#### JoinAccept 消息解析

```
┌─────────────────────────────────────────────┐
│ JoinAccept (17-33 bytes, 加密)              │
├─────────────────────────────────────────────┤
│ AppNonce   │ 3 bytes │ 网络服务器随机数       │
│ NetID      │ 3 bytes │ 网络ID                │
│ DevAddr    │ 4 bytes │ 分配的设备地址         │
│ DLSettings │ 1 byte  │ 下行设置              │
│ RxDelay    │ 1 byte  │ RX1 延迟              │
│ CFList     │ 16 bytes│ 信道列表 (可选)       │
│ MIC        │ 4 bytes │ 消息完整性码           │
└─────────────────────────────────────────────┘
```

### ABP（Activation By Personalization，个性化激活）

```
设备出厂时预置:
├── DevAddr   (设备地址, 4 bytes)
├── NwkSKey   (网络会话密钥, 16 bytes) ← 用于 MAC 层认证
└── AppSKey   (应用会话密钥, 16 bytes) ← 用于应用数据加密

无需 Join 流程, 直接收发数据
```

### OTAA vs ABP 对比

| 特性 | OTAA | ABP |
|------|------|-----|
| **安全性** | ⭐⭐⭐⭐⭐ 每次连接协商密钥 | ⭐⭐⭐ 密钥固定 |
| **部署** | 需要网络服务器支持 | 简单直接 |
| **灵活性** | 高（可漫游） | 低 |
| **推荐** | ✅ 生产环境 | 开发/测试 |

---

## 数据加密与安全

### 双层加密

```
上行数据帧:
┌──────────────────────────────────────────────┐
│ MAC Payload                                    │
│  ┌──────────┬───────────────────────────────┐ │
│  │ FHDR     │  DevAddr + FCtrl + FCnt + FOpts│ │ ← NwkSKey 保护 (MIC)
│  ├──────────┼───────────────────────────────┤ │
│  │ FPort    │  端口号 (0=MAC命令)             │ │
│  ├──────────┼───────────────────────────────┤ │
│  │ FRMPayload │  ←── AppSKey 加密 ──→       │ │ ← AppSKey 加密
│  └──────────┴───────────────────────────────┘ │
│ MIC (4 bytes) ←── NwkSKey 计算               │
└──────────────────────────────────────────────┘
```

| 密钥 | 用途 | 保护范围 |
|------|------|----------|
| **AppKey** | 入网密钥，用于 OTAA | JoinRequest/Accept 加密 |
| **NwkSKey** | 网络会话密钥 | MAC 层完整性校验 (MIC) |
| **AppSKey** | 应用会话密钥 | 应用层数据加密 (AES-128) |

### AES-128 加密流程

```python
"""
LoRaWAN 数据加解密示例 (简化版)
pip install cryptography
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import struct

def lorawan_encrypt(payload: bytes, key: bytes, dev_addr: bytes,
                    direction: int, fcnt: int) -> bytes:
    """
    LoRaWAN AES-128 CTR 模式加密
    direction: 0=uplink, 1=downlink
    """
    # 构建 Ai 序列块
    encrypted = bytearray()
    blocks = (len(payload) + 15) // 16

    for i in range(blocks):
        a = bytearray(16)
        a[0] = 0x01
        a[1:5] = bytes(4)  # placeholder
        a[5] = direction & 0xFF
        a[6:10] = dev_addr
        a[10:13] = struct.pack('<I', fcnt)[:3]  # FCntUp (3 bytes, little-endian)
        a[13] = i & 0xFF
        a[14] = 0
        a[15] = 0

        # 加密 Ai → Si
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        s = encryptor.update(bytes(a)) + encryptor.finalize()

        # XOR payload block with Si
        start = i * 16
        end = min(start + 16, len(payload))
        for j in range(start, end):
            encrypted.append(payload[j] ^ s[j - start])

    return bytes(encrypted)


# ─── 使用示例 ───
app_skey = bytes.fromhex("2B7E151628AED2A6ABF7158809CF4F3C")
dev_addr = bytes.fromhex("26041D88")
fcnt = 1

# 加密应用数据
payload = b'{"temp": 25.3}'
encrypted = lorawan_encrypt(payload, app_skey, dev_addr, direction=0, fcnt=fcnt)
print(f"Encrypted: {encrypted.hex()}")

# 解密（相同操作，CTR 模式对称）
decrypted = lorawan_encrypt(encrypted, app_skey, dev_addr, direction=0, fcnt=fcnt)
print(f"Decrypted: {decrypted.decode()}")
```

---

## MAC命令

MAC 命令用于网络服务器与设备之间的网络层管理通信。

| MAC命令 | 名称 | 说明 |
|---------|------|------|
| `LinkCheckReq/Ans` | 链路检查 | 设备请求链路质量 |
| `LinkADRReq/Ans` | 速率自适应 | 调整 SF、功率、信道 |
| `DutyCycleReq/Ans` | 占空比控制 | 限制发送占空比 |
| `RxParamSetupReq/Ans` | 接收参数设置 | 配置 RX2 参数 |
| `DevStatusReq/Ans` | 设备状态查询 | 获取电池电量和SNR |
| `NewChannelReq/Ans` | 新信道配置 | 添加/修改信道 |
| `RXTimingSetupReq/Ans` | 接收时序 | 配置 RX1 延迟 |
| `RejoinReq` | 重加入请求 | OTAA 重新入网 |

### 设备状态上报示例

```
DevStatusReq (Network Server → Device)
    ↓
DevStatusAns (Device → Network Server)
┌─────────────────────────────┐
│ Battery (1 byte)             │
│   0:     设备接外部电源       │
│   1-254: 电池电量 (1/(254))*100%│
│   255:   无法测量             │
├─────────────────────────────┤
│ Margin (1 byte)              │
│   SNR = Margin / 4 (dB)      │
│   范围: -32 ~ +31.75 dB      │
└─────────────────────────────┘
```

---

## 网关开发

### 网关硬件

| 组件 | 说明 |
|------|------|
| **LoRa Concentrator** | LoRa 射频前端 (如 SX1302/SX1303) |
| **主机** | 树莓派 / Linux 主板 |
| **回传网络** | Ethernet / 4G / Wi-Fi |
| **GPS** | (可选) 精确时间同步 |

### Packet Forwarder 配置

```json
// local_conf.json — 网关配置
{
    "gateway_conf": {
        "gateway_ID": "AA555A0000000001",
        "servers": [
            {
                "server_address": "router.cn.thethings.network",
                "serv_port_up": 1700,
                "serv_port_down": 1700,
                "serv_enabled": true
            }
        ],
        "ref_latitude": 31.2304,
        "ref_longitude": 121.4737,
        "ref_altitude": 10,
        "contact_email": "admin@example.com",
        "description": "上海浦东LoRaWAN网关"
    }
}
```

```json
// global_conf.json — 射频配置 (CN470)
{
    "SX130x_conf": {
        "radio_0": {
            "enable": true,
            "freq": 470600000
        },
        "radio_1": {
            "enable": true,
            "freq": 490600000
        },
        "chan_multiSF_0": { "enable": true, "radio": 0, "if": -300000 },
        "chan_multiSF_1": { "enable": true, "radio": 0, "if": -100000 },
        "chan_multiSF_2": { "enable": true, "radio": 0, "if":  100000 },
        "chan_multiSF_3": { "enable": true, "radio": 0, "if":  300000 },
        "chan_multiSF_4": { "enable": true, "radio": 1, "if": -300000 },
        "chan_multiSF_5": { "enable": true, "radio": 1, "if": -100000 },
        "chan_multiSF_6": { "enable": true, "radio": 1, "if":  100000 },
        "chan_multiSF_7": { "enable": true, "radio": 1, "if":  300000 }
    }
}
```

### 网关数据格式（Packet Forwarder Protocol）

```json
// 上行数据 (网关 → 网络服务器)
{
    "rxpk": [{
        "time": "2026-06-28T10:00:00.000000Z",
        "tmst": 1234567890,
        "chan": 2,
        "rfch": 0,
        "freq": 470.3,
        "stat": 1,
        "modu": "LORA",
        "datr": "SF7BW125",
        "codr": "4/5",
        "rssi": -75,
        "lsnr": 8.5,
        "size": 25,
        "data": "gAJ...base64..."
    }]
}
```

### 基于 Python 的网关模拟器

```python
"""
LoRaWAN 网关模拟器 — 模拟 Packet Forwarder 行为
用于开发测试，不依赖真实硬件
"""
import socket
import json
import base64
import time
import threading
from datetime import datetime, timezone


class LoRaGatewaySimulator:
    """模拟 LoRaWAN 网关的 Packet Forwarder"""

    def __init__(self, gateway_id: str, network_server: str, port: int = 1700):
        self.gateway_id = gateway_id
        self.ns_host = network_server
        self.ns_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.token = 0
        self._running = False

    def _next_token(self) -> bytes:
        """生成消息令牌"""
        self.token = (self.token + 1) & 0xFFFF
        return bytes([(self.token >> 8) & 0xFF, self.token & 0xFF])

    def send_uplink(self, dev_addr: str, data: bytes, freq: float = 470.3,
                    datr: str = "SF7BW125", rssi: int = -75, lsnr: float = 8.5):
        """模拟上行数据包"""
        timestamp = int(time.time())
        tmst = timestamp & 0xFFFFFFFF

        rxpk = {
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "tmst": tmst,
            "chan": 2,
            "rfch": 0,
            "freq": freq,
            "stat": 1,
            "modu": "LORA",
            "datr": datr,
            "codr": "4/5",
            "rssi": rssi,
            "lsnr": lsnr,
            "size": len(data),
            "data": base64.b64encode(data).decode()
        }

        # 构建消息: token(2) + identifier(1) + gateway_id(8) + payload
        message = bytes.fromhex(self.gateway_id)
        payload = json.dumps({"rxpk": [rxpk]}).encode()

        packet = self._next_token()
        packet += bytes([0x00])  # PUSH_DATA identifier
        packet += bytes.fromhex(self.gateway_id)
        packet += payload

        self.sock.sendto(packet, (self.ns_host, self.ns_port))
        print(f"[TX] Uplink: freq={freq}MHz, datr={datr}, "
              f"rssi={rssi}, lsnr={lsnr}, size={len(data)}")

    def listen_downlink(self):
        """监听网络服务器下发的数据"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 1700))

        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                identifier = data[2]
                payload = data[3:]

                if identifier == 0x01:  # PUSH_ACK
                    pass
                elif identifier == 0x03:  # PULL_RESP (下行数据)
                    resp = json.loads(payload)
                    txpk = resp.get("txpk", {})
                    tx_data = base64.b64decode(txpk.get("data", ""))
                    print(f"[RX] Downlink from NS: {tx_data.hex()}")
            except Exception as e:
                if self._running:
                    print(f"[ERROR] Listen: {e}")

    def start(self):
        self._running = True
        t = threading.Thread(target=self.listen_downlink, daemon=True)
        t.start()
        print(f"[GW] Gateway {self.gateway_id} started")

    def stop(self):
        self._running = False
        self.sock.close()


# 使用示例
gw = LoRaGatewaySimulator("AA555A0000000001", "localhost")
gw.start()

# 模拟终端设备上行
# 构建一个简单的 LoRaWAN 数据帧 (简化)
# PHyPayload = MHDR(1) + MACPayload(变量) + MIC(4)
mhdr = bytes([0x40])  # Unconfirmed Data Up
dev_addr = bytes.fromhex("26041D88")
fctrl = bytes([0x00])
fcnt = bytes([0x01, 0x00])
fport = bytes([0x01])
frm_payload = b"25.3C,60%"  # 应用数据
mic = bytes([0x12, 0x34, 0x56, 0x78])
data_frame = mhdr + dev_addr + fctrl + fcnt + fport + frm_payload + mic

gw.send_uplink(dev_addr="26041D88", data=data_frame)
```

---

## 终端设备开发

### 基于 LMIC 库的终端 (Arduino/C++)

```cpp
// LoRaWAN 终端设备示例 (Arduino + LMIC 库)
// 硬件: TTGO LoRa32 / Heltec WiFi LoRa 32
#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

// ─── OTAA 凭证 (从网络服务器获取) ───
static const u1_t PROGMEM APPEUI[8] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
static const u1_t PROGMEM DEVEUI[8] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08 };
static const u1_t PROGMEM APPKEY[16] = { 
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C 
};

// LMIC 回调函数
void os_getArtEui(u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
void os_getDevEui(u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
void os_getDevKey(u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

// ─── 上行数据发送任务 ───
static osjob_t sendjob;

void do_send(osjob_t* j) {
    // 检查是否可以发送 (避免占空比违规)
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, not sending"));
    } else {
        // 读取传感器数据
        float temperature = readTemperature();
        float humidity = readHumidity();
        uint8_t battery = readBattery();

        // 编码数据 (CayenneLPP 格式)
        uint8_t payload[11];
        int idx = 0;

        // 温度传感器 (通道 1)
        payload[idx++] = 0x01;  // Channel
        payload[idx++] = 0x67;  // Type = Temperature
        int16_t temp = temperature * 10;
        payload[idx++] = (temp >> 8) & 0xFF;
        payload[idx++] = temp & 0xFF;

        // 湿度传感器 (通道 2)
        payload[idx++] = 0x02;
        payload[idx++] = 0x68;  // Type = Humidity
        payload[idx++] = (uint8_t)(humidity * 2);

        // 电池 (通道 3)
        payload[idx++] = 0x03;
        payload[idx++] = 0x02;  // Type = Digital Input
        payload[idx++] = battery;

        // 准备发送
        LMIC_setTxData2(1, payload, idx, 0);  // Port 1, unconfirmed
        Serial.println(F("Packet queued"));
    }
    // 调度下一次发送 (60秒后)
    os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(60), do_send);
}

// ─── LMIC 事件回调 ───
void onEvent(ev_t ev) {
    switch(ev) {
        case EV_TXSTART:
            Serial.println(F("TX started"));
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("TX complete"));
            if (LMIC.txrxFlags & TXRX_ACK) {
                Serial.println(F("Received ack"));
            }
            if (LMIC.dataLen) {
                Serial.print(F("Received "));
                Serial.print(LMIC.dataLen);
                Serial.println(F(" bytes of payload"));
                // 处理下行数据...
            }
            break;
        case EV_JOINED:
            Serial.println(F("OTAA Joined!"));
            // 关闭 ADR (可选, 根据场景)
            // LMIC_setAdrMode(false);
            // 设置数据速率
            LMIC_setDrTxpow(DR_SF7, 14);
            break;
        case EV_JOINING:
            Serial.println(F("OTAA Joining..."));
            break;
        case EV_JOIN_FAILED:
            Serial.println(F("OTAA Join failed"));
            break;
        case EV_RESET:
            Serial.println(F("Module reset"));
            break;
        default:
            Serial.printf("Event: %d\n", ev);
            break;
    }
}

void setup() {
    Serial.begin(115200);
    delay(100);
    Serial.println(F("LoRaWAN Device Starting..."));

    // LMIC 初始化
    os_init();
    LMIC_reset();

    // 中国频段配置
    LMIC_setFrequency(CN470);
    LMIC_setupChannel(0, 470300000, DR_RANGE_MAP(DR_SF12, DR_SF7));

    // 启动 Join
    LMIC_startJoining();

    // 启动发送任务
    do_send(&sendjob);
}

void loop() {
    os_runloop_once();
}

// ─── 传感器读取函数 ───
float readTemperature() { return 25.3; }
float readHumidity() { return 60.0; }
uint8_t readBattery() { return 87; }
```

### CayenneLPP 数据格式

```python
"""
CayenneLPP — LoRaWAN 标准的有效载荷编码格式
pip install cayennelpp
"""
from cayennelpp import LPPFrame

# 创建数据帧
frame = LPPFrame()

# 添加传感器数据
frame.add_temperature(1, 25.3)     # 通道1: 温度 25.3°C
frame.add_humidity(2, 60.0)        # 通道2: 湿度 60%
frame.add_barometric_pressure(3, 1013.25)  # 通道3: 气压
frame.add_gps(4, 31.2304, 121.4737, 10)    # 通道4: GPS位置
frame.add_digital_input(5, 1)      # 通道5: 数字输入 (电池)
frame.add_analog_input(6, 2.7)     # 通道6: 模拟输入 (电压)

# 编码为字节 (用于 LoRaWAN 发送)
payload = frame.bytes()
print(f"Payload ({len(payload)} bytes): {payload.hex()}")

# 解码
decoded = LPPFrame().bytes_to_payload(payload)
for item in decoded:
    print(f"Channel {item.channel}: {item.type} = {item.value}")
```

### 基于 Python 的终端模拟器

```python
"""
LoRaWAN 终端设备模拟器 (Class A)
用于开发测试，模拟传感器数据上报
"""
import time
import random
from dataclasses import dataclass
from enum import IntEnum


class DataRate(IntEnum):
    SF7BW125 = 7
    SF8BW125 = 8
    SF9BW125 = 9
    SF10BW125 = 10
    SF11BW125 = 11
    SF12BW125 = 12


@dataclass
class LoRaWANConfig:
    dev_eui: str
    app_eui: str
    app_key: str
    class_type: str = "A"
    data_rate: DataRate = DataRate.SF7BW125
    tx_interval: int = 60  # 上行间隔 (秒)


class LoRaWANDevice:
    def __init__(self, config: LoRaWANConfig):
        self.config = config
        self.dev_addr = None
        self.joined = False
        self.fcnt_up = 0
        self.fcnt_down = 0
        self.battery = 100
        self.adr_enabled = True

    def join(self) -> bool:
        """OTAA 入网流程"""
        print(f"[JOIN] DevEUI={self.config.dev_eui}")
        print(f"[JOIN] Sending JoinRequest (SF{12})...")

        # 模拟入网过程
        time.sleep(0.5)
        self.dev_addr = "26041D88"
        self.joined = True
        print(f"[JOIN] ✅ Joined! DevAddr={self.dev_addr}")
        return True

    def send_uplink(self, port: int, payload: bytes, confirmed: bool = False):
        """发送上行数据"""
        if not self.joined:
            print("[ERROR] Not joined yet")
            return

        self.fcnt_up += 1
        msg_type = "Confirmed" if confirmed else "Unconfirmed"
        print(f"[TX] {msg_type} Data Up | Port={port} | FCnt={self.fcnt_up} "
              f"| DR=SF{self.config.data_rate} | {len(payload)} bytes")
        print(f"     Payload: {payload.hex()}")

        # Class A: 等待接收窗口
        if self.config.class_type == "A":
            self._wait_rx_window()

    def _wait_rx_window(self):
        """等待 Class A 接收窗口"""
        print("[RX1] Opening RX1 window (1s)...")
        time.sleep(0.1)  # 模拟
        # 模拟可能的下行
        if random.random() < 0.3:
            self._handle_downlink()

        print("[RX2] Opening RX2 window (2s)...")
        time.sleep(0.1)

    def _handle_downlink(self):
        """处理下行数据"""
        self.fcnt_down += 1
        print(f"[RX] Downlink received! FCnt={self.fcnt_down}")

    def run_sensor_loop(self, duration: int = 300):
        """运行传感器数据上报循环"""
        self.join()

        start = time.time()
        while time.time() - start < duration:
            # 模拟传感器数据
            temp = round(random.uniform(20.0, 28.0), 1)
            hum = round(random.uniform(40.0, 70.0), 1)
            self.battery = max(0, self.battery - random.randint(0, 1))

            # 编码 (简化)
            payload = f"T={temp};H={hum};B={self.battery}".encode()
            self.send_uplink(port=1, payload=payload, confirmed=False)

            time.sleep(self.config.tx_interval)


# ─── 使用示例 ───
config = LoRaWANConfig(
    dev_eui="0102030405060708",
    app_eui="0000000000000000",
    app_key="2B7E151628AED2A6ABF7158809CF4F3C",
    class_type="A",
    data_rate=DataRate.SF7BW125,
    tx_interval=5  # 测试用短间隔
)

device = LoRaWANDevice(config)
device.run_sensor_loop(duration=30)
```

---

## 网络服务器集成

### 与 ChirpStack 集成

```python
"""
ChirpStack Network Server REST API 集成
pip install requests
"""
import requests
import json
from datetime import datetime, timezone

CHIRPSTACK_URL = "http://localhost:8080"
API_TOKEN = "your...n

headers = {"Authorization": f"Bearer {API_TOKEN}"}


class ChirpStackIntegration:
    """ChirpStack 网络服务器 API 封装"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}", "Grpc-Metadata-Auth": token}

    # ─── 设备管理 ───

    def create_device(self, dev_eui: str, name: str, application_id: str,
                     device_profile_id: str, app_key: str):
        """注册新设备"""
        payload = {
            "device": {
                "devEui": dev_eui,
                "name": name,
                "applicationId": application_id,
                "deviceProfileId": device_profile_id,
                "description": f"LoRaWAN Device {dev_eui}"
            },
            "deviceKeys": {
                "devEui": dev_eui,
                "nwkKey": app_key,
                "joinEui": "0000000000000000",
                "appKey": app_key
            }
        }
        resp = requests.post(
            f"{self.base_url}/api/devices",
            json=payload,
            headers=self.headers
        )
        return resp.json()

    def get_device(self, dev_eui: str) -> dict:
        """获取设备信息"""
        resp = requests.get(
            f"{self.base_url}/api/devices/{dev_eui}",
            headers=self.headers
        )
        return resp.json()

    def delete_device(self, dev_eui: str):
        """删除设备"""
        resp = requests.delete(
            f"{self.base_url}/api/devices/{dev_eui}",
            headers=self.headers
        )
        return resp.status_code == 204

    # ─── 设备队列 (下行) ───

    def enqueue_downlink(self, dev_eui: str, f_port: int, data: bytes,
                         confirmed: bool = False):
        """下发数据到设备队列"""
        import base64
        payload = {
            "deviceQueueItem": {
                "devEui": dev_eui,
                "fPort": f_port,
                "confirmed": confirmed,
                "data": base64.b64encode(data).decode(),
            }
        }
        resp = requests.post(
            f"{self.base_url}/api/devices/{dev_eui}/queue",
            json=payload,
            headers=self.headers
        )
        return resp.json()

    # ─── 设备激活状态 ───

    def get_activation(self, dev_eui: str) -> dict:
        """获取设备激活状态"""
        resp = requests.get(
            f"{self.base_url}/api/devices/{dev_eui}/activation",
            headers=self.headers
        )
        return resp.json()

    # ─── 事件订阅 ───

    def get_events(self, dev_eui: str, limit: int = 10):
        """获取设备事件"""
        resp = requests.get(
            f"{self.base_url}/api/devices/{dev_eui}/events",
            params={"limit": limit},
            headers=self.headers
        )
        return resp.json()


# ─── 使用示例 ───
cs = ChirpStackIntegration("http://localhost:8080", API_TOKEN)

# 注册设备
cs.create_device(
    dev_eui="0102030405060708",
    name="温度传感器-01",
    application_id="app-uuid-here",
    device_profile_id="profile-uuid-here",
    app_key="2B7E151628AED2A6ABF7158809CF4F3C"
)

# 下发控制命令
cs.enqueue_downlink(
    dev_eui="0102030405060708",
    f_port=2,
    data=bytes([0x01, 0x02, 0x03]),
    confirmed=True
)
```

### MQTT 数据订阅

```python
"""
订阅 ChirpStack 的 MQTT 事件流
接收上行数据、Join 事件等
"""
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected to ChirpStack MQTT: {rc}")
    # 订阅应用的所有设备事件
    client.subscribe("application/+/device/+/event/up", qos=0)
    client.subscribe("application/+/device/+/event/join", qos=0)
    client.subscribe("application/+/device/+/event/status", qos=0)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    if msg.topic.endswith("/event/up"):
        # 上行数据
        dev_eui = data["devEui"]
        f_port = data["fPort"]
        payload_b64 = data["data"]
        object_data = data.get("object", {})

        import base64
        raw = base64.b64decode(payload_b64)

        print(f"[UPLINK] {dev_eui} | Port={f_port} | "
              f"RSSI={data.get('rxInfo', [{}])[0].get('rssi', 'N/A')} | "
              f"Data={object_data}")

    elif msg.topic.endswith("/event/join"):
        dev_eui = data["devEui"]
        print(f"[JOIN] {dev_eui} joined the network")

    elif msg.topic.endswith("/event/status"):
        dev_eui = data["devEui"]
        margin = data.get("margin")
        battery = data.get("batteryLevel", "N/A")
        print(f"[STATUS] {dev_eui} | Battery={battery}% | Margin={margin}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# ChirpStack 内置 MQTT broker
client.connect("localhost", 1883, 60)
client.loop_forever()
```

---

## 最佳实践

### 1. 频段与合规
- ⚠️ **中国**: 使用 CN470 频段，需符合《微功率短距离无线电设备管理》规定
- ⚠️ **占空比限制**: 免授权频段通常有 1% 占空比限制
- ⚠️ **发射功率**: 不超过法规限制（如中国 50mW / 17dBm）

### 2. 功耗优化
```
优化策略:
1. 使用 Class A 模式
2. 启用 ADR (网络服务器自动优化 SF)
3. 降低上行频率 (周期从 60s → 300s)
4. 使用 CayenneLPP 压缩数据
5. 只在数据变化时上报 (事件驱动)
6. 关闭不必要的 LED 和调试串口
```

### 3. 数据传输优化

| 策略 | 说明 | 节省 |
|------|------|------|
| **二进制编码** | CayenneLPP 替代 JSON | ~60% |
| **变化上报** | 仅在数据变化时发送 | ~80% |
| **批量上报** | 积累多条数据一次发送 | ~30% |
| **确认机制** | 非关键数据用 Unconfirmed | 减少下行窗口 |

### 4. 网络规划
```
网关部署原则:
├── 覆盖优先: 网关安装在制高点 (楼顶/塔顶)
├── 冗余覆盖: 每个区域至少 2 个网关可见
├── 回传可靠: Ethernet > 4G > Wi-Fi
├── 容量规划:
│   ├── 单网关支持 ~5000 设备 (低频上报)
│   └── 高密度区域需要更多网关
└── 信道规划: CN470 使用 8 信道模式
```

### 5. 安全最佳实践
- ✅ 生产环境使用 OTAA，不使用 ABP
- ✅ AppKey 安全存储（安全芯片 / OTP）
- ✅ 定期更新会话密钥（通过 Rejoin）
- ✅ 应用层额外加密（敏感数据）
- ❌ 不要在固件中硬编码 AppKey

### 6. 部署 Checklist

```markdown
## 部署前检查
- [ ] 频段配置正确 (CN470)
- [ ] 网关 GPS 位置已校准
- [ ] 设备 OTAA 凭证已注册到网络服务器
- [ ] ADR 已启用
- [ ] 数据上报频率符合占空比要求
- [ ] 备用网关已部署
- [ ] 监控告警已配置

## 部署后验证
- [ ] 所有设备成功 Join
- [ ] 数据到达率 > 95%
- [ ] 下行命令可达
- [ ] 电池消耗符合预期
- [ ] 无频段干扰
```

### 7. 故障排查

| 问题 | 可能原因 | 排查方法 |
|------|----------|----------|
| 设备无法 Join | AppKey 错误 / 频段不匹配 | 检查凭证和频段 |
| 数据丢失 | SF 不够高 / 网关距离远 | 提高 SF / 增加网关 |
| 电池消耗快 | 上行太频繁 / Class C | 降低频率 / 改用 Class A |
| 下行不可达 | 设备在睡眠 | 使用 Class B/C 或等上行后下发 |
| 高丢包率 | 同频干扰 | 检查附近其他 LoRa 设备 |

---

## 相关页面

- [[MQTT协议指南]] — LoRaWAN 后端集成 MQTT 订阅
- [[时序数据库]] — LoRaWAN 传感器数据的持久化
- [[设备管理平台]] — LoRaWAN 设备的注册与管理
- [[工业网关开发]] — LoRaWAN 网关也是一种工业网关

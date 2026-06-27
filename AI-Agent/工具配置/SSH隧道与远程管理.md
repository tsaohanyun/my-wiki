project: hermes
---
title: SSH隧道与远程管理
aliases: [SSH配置, 远程管理, 跳板机]
tags: [ssh, 网络, 运维]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: session-history
difficulty: advanced
---
# SSH 隧道与远程管理

## 架构概述

```
用户PC (Windows)
    ↓ SSH 2222端口
服务器 (Linux)
    ↓ SSH 2223端口
跳板机
    ↓
内网资源
```

## 端口映射

| 端口 | 用途 | 认证方式 |
|------|------|----------|
| 22222 | SSH服务 | 密钥认证 |
| 2222 | 用户PC反向隧道 | 私钥认证 |
| 2223 | 跳板机 | 密码认证 |
| 13306 | PROD只读数据库 | 通过跳板机 |
| 13307 | UAT读写数据库 | 通过跳板机 |

## Windows远程命令

```bash
# 通过SSH执行Windows命令
ssh -p 2222 -i ~/.ssh/hermes_dashboard/hermesdashborad.pem ThinkPad@localhost "powershell -Command "Get-Process""

# 传输文件
scp -P 2222 -i ~/.ssh/hermes_dashboard/hermesdashborad.pem file.txt ThinkPad@localhost:C:/temp/
```

## 常见问题

### 1. 连接超时

**原因**：Windows SSH服务未运行或防火墙阻止

**解决**：
```powershell
# Windows端启动SSH服务
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

### 2. 公钥认证失败

**解决**：将服务器公钥添加到Windows的`C:\ProgramData\sshdministrators_authorized_keys`

## 相关页面

- [[Hermes-常见问题排查]]
- [[网络连接拓扑]]
project: hermes
---
title: Hermes WebUI配置与管理
aliases: [WebUI配置, hermes-webui, Dashboard管理]
tags: [hermes, webui, 配置]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: session-20260626_155131
difficulty: beginner
---
# Hermes WebUI 配置与管理

## 重要区分

**hermes-webui 和 hermes dashboard 是两个独立应用！**

| 应用 | 路径 | 端口 | 用途 |
|------|------|------|------|
| hermes-webui | `/home/agentuser/hermes-webui/server.py` | 21434 | 独立Web界面 |
| hermes dashboard | Hermes内置 | 50503 | 管理面板 |

## WebUI 启动

```bash
# 启动WebUI（使用hermes-agent的venv）
cd /home/agentuser/hermes-webui
source /home/agentuser/.hermes/bin/activate
python server.py

# 或使用systemd服务
sudo systemctl start hermes-webui
```

## 常见问题

### 1. web_dist缺失导致500错误

**症状**：页面返回500错误，日志显示`FileNotFoundError: web_dist/index.html`

**原因**：`web_dist/`是前端build产物，在`.gitignore`中，不会被git同步

**解决**：
```bash
cd /home/agentuser/hermes-webui
npm install --workspace web
npm run --workspace web build
```

### 2. 端口配置

WebUI端口在`.env`文件中配置：
```bash
HERMES_WEBUI_PORT=21434
```

## 账号密码

默认配置在`~/.hermes/config.yaml`的`basic_auth`部分。

## 相关页面

- [[Hermes-Agent架构总览]]
- [[Hermes-常见问题排查]]
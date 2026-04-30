---
title: MCP 服务器开发
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [工具, MCP, 协议, 集成]
sources: [raw/articles/mcp-builder.md]
---

# MCP 服务器开发

## 概述
Model Context Protocol (MCP) 服务器开发指南，使 LLM 能够通过标准化工具接口与外部服务交互。
## 核心概念
1. **工具 (Tools)** - 暴露给 LLM 的可调用函数
2. **资源 (Resources)** - 可读取的数据源
3. **提示 (Prompts)** - 预定义的提示模板
4. **传输层** - stdio 或 HTTP 传输
## 实现方式
| 语言 | 框架 | 特点 |
|------|------|------|
| Python | FastMCP | 装饰器风格，快速开发 |
| TypeScript | MCP SDK | 官方 SDK，类型安全 |
## 使用模式
- **本地 stdio** - 作为子进程运行
- **HTTP 服务** - 独立服务部署
- **认证集成** - OAuth2/API Key 认证
## 交叉引用
- [[claude-api-development]] - Claude API 集成
- [[hermes-agent]] - Agent 平台工具注册

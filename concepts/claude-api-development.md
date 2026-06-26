---
author: Hermes Wiki Agent
created: 2026-04-30
description: '构建 Claude API 应用的开发模式，包括 SDK 选择、prompt caching、流式输出等最佳实践。 1. 使用官方 SDK
  - 优先使用 Anthropic 官方 SDK（Python/TypeScript/Java）

  '
project: 通用知识
sources:
- raw/articles/claude-api.md
status: published
tags:
- tool
- api
title: Claude API 开发模式
type: concept
updated: 2026-04-30
version: 1.0.20260530
---



# Claude API 开发模式

## 概述
构建 Claude API 应用的开发模式，包括 SDK 选择、prompt caching、流式输出等最佳实践。
## 核心原则
1. **使用官方 SDK** - 优先使用 Anthropic 官方 SDK（Python/TypeScript/Java）
2. **启用 Prompt Caching** - 对长上下文启用缓存以降低成本
3. **流式输出** - 对长响应使用流式传输避免超时
4. **自适应思考** - 复杂任务启用 `thinking: {type: "adaptive"}`
## SDK 语言支持
| 语言 | 包名 | 安装命令 |
|------|------|----------|
| Python | `anthropic` | `pip install anthropic` |
| TypeScript | `@anthropic-ai/sdk` | `npm install @anthropic-ai/sdk` |
| Java | `com.anthropic` | Maven/Gradle |
## 使用模式
- **SDK 调用** - 标准 API 调用流程
- **流式处理** - 处理长响应
- **批处理** - Batch API 批量处理请求
- **文件处理** - 上传和处理文件
## 交叉引用
- [[concepts/mcp-server-development|mcp-server-development]] - MCP 协议集成
- [[entities/hermes-agent|hermes-agent]] - Agent 平台集成
- [[concepts/systematic-debugging|systematic-debugging]] - API 调试方法

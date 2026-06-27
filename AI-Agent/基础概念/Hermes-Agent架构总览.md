project: hermes
---
title: Hermes Agent架构总览
aliases: [Hermes架构, AI Agent框架, Agent系统]
tags: [ai-agent, hermes, 架构]
type: concept
status: published
created: 2026-06-27
updated: 2026-06-27
source: session-history
difficulty: intermediate
---
# Hermes Agent 架构总览

## 概述

Hermes Agent 是一个开源的 AI 代理框架，支持多种 LLM 提供商和工具集成。

## 核心组件

### 1. 核心引擎
- **Agent Loop**：消息处理和工具调用的主循环
- **Tool Registry**：工具注册和管理
- **Memory System**：持久化记忆存储

### 2. 配置系统
- `config.yaml`：主配置文件
- `~/.hermes/`：用户数据目录
- `skills/`：技能库目录

### 3. 通信层
- **CLI Mode**：命令行交互
- **Gateway Mode**：消息平台集成（Telegram、Discord等）
- **WebUI**：浏览器界面

## 相关页面

- [[Hermes-WebUI配置与管理]]
- [[Hermes-Skills开发指南]]
- [[Hermes-常见问题排查]]
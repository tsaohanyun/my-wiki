---
title: Harness Engineering
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [architecture, pattern, design-principle, ai-agent]
sources: [raw/articles/harness-engineering-methodology.md]
---

# Harness Engineering

## 定义

**Harness（驾驭层）** 是介于 LLM 和用户之间的工程系统。它不是简单的 API 调用封装，而是一整套**控制、引导、约束、增强** LLM 行为的运行时框架。

```
优秀的 AI Agent = 强大的 LLM × 精密的 Harness
```

Harness 控制的五个维度：
1. LLM **能做什么** — Tool 注册与权限
2. LLM **怎么做** — System Prompt 工程
3. LLM **在什么约束下做** — Permission / Sandbox / Hooks
4. **用户如何感知和控制** — Progress / UI / Interrupts
5. **系统如何从经验中学习** — Memory / Context

## 五层架构 ^[raw/articles/harness-engineering-methodology.md]

```
┌─────────────────────────────────┐
│     Memory 层 — 学习积累        │  ← 跨会话记忆 / 纠错学习
├─────────────────────────────────┤
│  Orchestration 层 — 流程编排    │  ← 主循环 / 多Agent / 任务管理
├─────────────────────────────────┤
│    Permission 层 — 安全控制     │  ← 规则 / 分类器 / 用户确认
├─────────────────────────────────┤
│     Prompt 层 — 行为引导        │  ← 分层组装 / 动态注入 / 缓存
├─────────────────────────────────┤
│      Tool 层 — 能力定义         │  ← 自描述 / 按需发现 / 输出管控
└─────────────────────────────────┘
```

### 第一层：Tool 层 ^[raw/articles/harness-engineering-methodology.md]

**核心洞见**：LLM 不直接操作世界，它通过调用 Tools 来行动。

| 维度 | 设计要点 |
|------|----------|
| 能力注册 | 每个 Tool 自包含 schema/validation/permission |
| 能力发现 | 不一次暴露所有能力，按需发现（ToolSearch） |
| 输出管控 | 限制输出大小，超限落盘为文件 |
| 并发标记 | 标记哪些 Tool 可并行执行 |
| 中断策略 | 定义用户中断时的行为（cancel / block） |

**Tool 定义核心字段**：name、inputSchema、call()、description()、validateInput()、hasPermission()、isReadOnly()、isDestructive()、isConcurrencySafe()、interruptBehavior()、maxResultSizeChars

关键设计：
- **每个 Tool 都是自描述的**：包含校验、权限、安全标记，不依赖外部全局配置
- **Deferred Loading（延迟加载）**：50+ Tools 不全部塞进 System Prompt，按需发现
- **Tool 结果有大小管控**：超出限制的结果落盘，模型只看到摘要+文件路径

### 第二层：Prompt 层 ^[raw/articles/harness-engineering-methodology.md]

System Prompt 是**多层动态组装**的，非静态字符串：

```
Static Layer（全局缓存）
├ 身份声明 / 安全指令 / 行为准则 / 工具使用指南 / 行动谨慎原则
├── 缓存边界 ──
Dynamic Layer（每轮重算）
├ 环境信息 / 项目级指令 / 记忆注入 / MCP工具说明 / Skill列表 / 系统提醒
```

关键设计：
- **缓存边界**：静态部分跨对话缓存，动态部分每轮刷新，节省 Token
- **严格区分**：可缓存 vs 必须刷新的 Prompt 片段
- **按需注入**：MCP 指令、Skill 列表、Memory 只在相关时注入

### 第三层：Permission 层 ^[raw/articles/harness-engineering-methodology.md]

**三层门控流程**：

```
请求 → validateInput() → hasPermission() → Classifier → User Prompt
         输入校验         静态规则匹配      AI风险评估    用户手动确认
```

关键设计：
- **Permission Mode 模式切换**：default → auto → bypass
- **工具级权限粒度**：逐工具配置 alwaysAllow / alwaysDeny / alwaysAsk
- **读写分离**：isReadOnly() 标记决定是否需确认
- **破坏性标记**：isDestructive() 让系统知道 rm 等操作需额外谨慎

### 第四层：Orchestration 层 ^[raw/articles/harness-engineering-methodology.md]

**Coordinator-Worker 模式**：

```
Coordinator Agent（主线程）
├── 理解用户意图 / 分解任务
├── 分派 Worker Agent（并行）
│   ├── Worker A / Worker B / Worker C
├── 汇总结果 / 向用户汇报
```

关键约束：
- Coordinator 不直接操作文件，只做调度
- Worker 通过 task-notification 汇报结果
- Worker 之间不直接通信，只通过 Coordinator 协调
- SendMessage 可继续已完成的 Worker（复用上下文）

### 第五层：Memory 层 ^[raw/articles/harness-engineering-methodology.md]

| 记忆类型 | 说明 | 示例 |
|----------|------|------|
| user | 用户画像 | 角色/知识/偏好 |
| feedback | 行为纠正 | 交互反馈记录 |
| project | 项目动态 | 项目上下文信息 |
| reference | 外部资源 | 资源指引 |

关键原则：
- **记忆 ≠ 日志**：只存对未来对话有价值的非显而易见信息
- **不存可推导信息**：代码结构读代码就知道、git历史用git log
- **使用前验证**：记忆可能过时，必须验证当前状态

## Hooks 事件系统 ^[raw/articles/harness-engineering-methodology.md]

```
PreToolUse Hook → 拦截/修改 Tool 输入
    ↓
Tool 执行
    ↓
PostToolUse Hook → 拦截/修改 Tool 输出
    ↓
Notification Hook → 通知用户/外部系统
```

Hooks 使 Harness 行为可被外部扩展而不需要修改代码。

## 设计原则总结

| 原则 | 核心思想 |
|------|----------|
| Tool-First | LLM 通过 Tools 行动，不直接操作世界 |
| 分层 Prompt | 静态缓存 + 动态注入，缓存边界节省 Token |
| 三层门控 | 静态规则 → AI分类 → 用户确认，逐层过滤 |
| Hooks 扩展 | 事件驱动的可插拔扩展，不修改核心代码 |
| Coordinator-Worker | 调度与执行分离，Worker 间不直接通信 |
| 持久化记忆 | 只存非显而易见信息，使用前验证 |

## 相关概念

- [[mcp-server-development]] — MCP 协议是 Tool 层的一种实现方式
- [[systematic-debugging]] — Harness 的 Permission 层是系统调试的保障
- [[hermes-agent]] — Hermes Agent 本身是 Harness 的一个实现实例
- [[text2kpi-optimization]] — Harness 方法论在 Text2KPI 项目中的应用

---
title: Text2KPI 优化方案
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [architecture, pattern, ai-agent, design-principle]
sources: [raw/articles/harness-engineering-methodology.md]
---

# Text2KPI 优化方案

## 概述

Text2KPI 是一个 NL2API（自然语言转 API 调用）系统，用户通过自然语言查询业务指标，系统自动路由到对应 API 并返回结果。基于 [[harness-engineering]] 方法论，对其人机交互体验提出六项优化方案。

## 当前架构痛点 ^[raw/articles/harness-engineering-methodology.md]

```
当前 Pipeline：
用户问题 → ScopeGuard → Intent → CompositeDetect → [PlanReview]
         → Route → [HumanApprove] → ParamFill → Result
```

| # | 痛点 | 对应 Harness 缺陷层 |
|---|------|---------------------|
| 1 | 无事后纠错机制 — 结果错了只能重新问 | Memory 层缺失 |
| 2 | 参数补全低效 — 缺多个参数时逐个询问 | Tool 层粗粒度 |
| 3 | ScopeGuard 不够精准 — 仅关键字匹配 | Prompt 层注入不足 |
| 4 | 指标置信度不透明 | Orchestration 层可视化缺失 |
| 5 | 无跨会话学习 — 每次对话从零开始 | Memory 层缺失 |
| 6 | Pipeline 过于刚性 — 步骤固定 | Orchestration 层缺灵活跳转 |

## 优化方案一：Feedback Loop ^[raw/articles/harness-engineering-methodology.md]

**对标**：Claude Code 的 feedback 类型 Memory + 权限拒绝追踪

```
用户提问 → Pipeline → 结果 → 反馈收集
                            ├ "结果正确"   → 正向记录
                            ├ "API选错了"  → 路由纠错 → 从 RouteStep 重跑
                            ├ "参数不对"   → 参数纠错 → 从 ParamFill 重跑
                            └ "指标理解错" → 意图纠错 → 从 IntentStep 重跑
```

实现要点：
- ResultCard 增加"这个结果对吗？"反馈按钮
- 支持**断点续跑**：用户指出某步有问题，从该步重新执行
- 纠错记录存入 FeedbackStore，影响后续同类查询的置信度

## 优化方案二：Tool-Based API 建模 ^[raw/articles/harness-engineering-methodology.md]

**对标**：Claude Code 的 Tool 抽象 + ToolSearch 按需发现

将每个 BSC API 建模为 Tool，利用 LLM 原生 Tool-Use 能力：

```python
class BSCTool:
    name: str             # "implant_performance"
    description: str      # 动态生成，包含可用指标、参数说明
    input_schema: dict    # JSON Schema，从 metadata 自动生成
    required_params: list # ["bu", "year"]
    risk_level: str       # "read" | "write_low" | "write_high"
```

优势：
- LLM 原生支持 Tool-Use，路由准确率更高
- 参数校验自动化，减少 ParamFill 中的人工补全
- 新 API 上线只需注册 Tool，无需修改 Pipeline

## 优化方案三：智能参数批量收集 ^[raw/articles/harness-engineering-methodology.md]

**对标**：Claude Code 的 AskUserQuestion Tool 结构化交互

```
当前：缺bu → 问bu → 缺year → 问year → 缺region → 问region（3轮）
优化：一次性识别所有缺失参数，生成结构化表单
```

实现要点：
- ParamFillStep 一次性收集所有缺失参数
- 前端渲染为结构化表单（非纯文本对话）
- 可选参数提供默认值，减少用户操作

## 优化方案四：分层上下文管理 ^[raw/articles/harness-engineering-methodology.md]

**对标**：Claude Code 的 systemPromptSection() 分层 + 缓存边界

```
ScopeGuard Step 上下文：tenant_profile + blocked_entities（轻量）
IntentStep 上下文：metric 名称/别名列表 + dimension 枚举值
RouteStep 上下文：匹配到的 API 完整定义 + 参数要求
ResultStep 上下文：API 返回的数据结构 + 计算公式说明
```

优势：
- 每步只注入必要信息，减少 Token 消耗
- 提高 LLM 专注度，减少幻觉
- 支持更大规模的 API 目录（当前 113+ API 全注入会爆 context）

## 优化方案五：跨会话记忆系统 ^[raw/articles/harness-engineering-methodology.md]

**对标**：Claude Code 的 memdir/ 持久化记忆

```
memory/
├── MEMORY.md              # 索引
├── user_preferences.md    # 用户偏好（常查指标、常用维度）
├── feedback_routing.md    # 路由纠错记录
├── feedback_params.md     # 参数纠错记录
├── project_metrics.md     # 新增/变更指标记录
└── reference_aliases.md   # 用户自定义别名
```

应用场景：
1. **个性化默认值**：用户经常查华东+A BU → 缺省参数自动填充
2. **纠错学习**：上次"达成率"被错误路由 → 这次优先选择正确 API
3. **别名记忆**：用户说"小王的指标" → 记住"小王 = 华东区域经理"

## 优化方案六：实时推理可视化 ^[raw/articles/harness-engineering-methodology.md]

**对标**：Claude Code 的 ToolCallProgress + SpinnerMode

将步骤级状态（✓ / ? / ✗）优化为步骤内实时推理流：

```
┌─ 意图解析 ─────────────────────────────────┐
│  [规则匹配] 命中维度: BU=A, Year=2026      │ ← 实时
│  [规则匹配] 命中指标: 植入达成率 (0.95)     │ ← 实时
│  [LLM分析] 跳过（规则引擎已高置信度匹配）   │ ← 实时
│  ✓ 完成（耗时 120ms）                       │
└────────────────────────────────────────────┘
```

## 实施优先级 ^[raw/articles/harness-engineering-methodology.md]

| 优先级 | 优化项 | 价值 | 成本 | 依赖 |
|--------|--------|------|------|------|
| P0 | 参数批量收集 | 直接减少交互轮次 | 低 | 前端表单组件 |
| P0 | 分层上下文管理 | 降本+提质 | 中 | Pipeline 改造 |
| P1 | Feedback Loop | 用户体验质变 | 中 | 断点续跑机制 |
| P1 | 实时推理可视化 | 透明度提升 | 低 | SSE 事件细化 |
| P2 | 跨会话记忆 | 长期价值 | 高 | 记忆存储+注入 |
| P3 | Tool-Based API 建模 | 架构升级 | 高 | LLM 原生 Tool-Use |

## 关键结论 ^[raw/articles/harness-engineering-methodology.md]

Text2KPI 已在 Permission 层（HumanApproveStep）和 Orchestration 层（Pipeline + CompositeDetect）有良好基础，最大提升空间：

1. **Memory 层的缺失** — 没有跨会话学习能力
2. **Tool 层的粗粒度** — API 路由还是传统匹配而非 Tool-Use
3. **交互效率** — 参数收集、反馈纠错的闭环尚未建立

这三个方向是将 Text2KPI 从"NL2API 工具"进化为"智能业务助手"的关键路径。

## 相关概念

- [[harness-engineering]] — 本方案的理论基础
- [[mcp-server-development]] — Tool-Based API 建模可借鉴 MCP 协议
- [[systematic-debugging]] — Feedback Loop 是系统级调试的闭环机制

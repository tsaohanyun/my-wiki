---
title: Text2KPI 优化方案
created: 2026-04-30
updated: 2026-05-02
type: concept
tags: [architecture, pattern, ai-agent, design-principle, nl2api]
sources:
  - raw/articles/harness-engineering-methodology.md
  - raw/articles/text2kpi-demo-design-v2.md
---

# Text2KPI 优化方案

## 概述

Text2KPI 是一个 **NL2API**（自然语言转 API 调用）系统，用户通过自然语言查询业务指标，系统自动路由到对应 API 并返回结果。基于 [[harness-engineering]] 方法论，对其人机交互体验提出六项优化方案，并在 V2 设计中完成了分层架构重构。

> **本系统不是 NL2SQL**。自然语言 → 理解意图 → 匹配已注册 API → 填充参数 → 调用取数 → 展示结果。不生成 SQL，不直接查数据库。与 [[nl2sql-precise-mapping]] 是不同路线。

---

## V1：六项优化方案 ^[raw/articles/harness-engineering-methodology.md]

### 当前架构痛点

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

### 优化方案一：Feedback Loop

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

### 优化方案二：Tool-Based API 建模

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

### 优化方案三：智能参数批量收集

**对标**：Claude Code 的 AskUserQuestion Tool 结构化交互

```
当前：缺bu → 问bu → 缺year → 问year → 缺region → 问region（3轮）
优化：一次性识别所有缺失参数，生成结构化表单
```

### 优化方案四：分层上下文管理

**对标**：Claude Code 的 systemPromptSection() 分层 + 缓存边界

每步只注入必要信息：ScopeGuard 用轻量 tenant_profile；IntentStep 用指标名+别名；RouteStep 用完整 API 定义；ResultStep 用返回数据结构+计算公式。

### 优化方案五：跨会话记忆系统

记忆维度：用户偏好（常查指标）、路由纠错记录、参数纠错记录、用户自定义别名。

### 优化方案六：实时推理可视化

将步骤级状态优化为步骤内实时推理流，展示规则匹配/LLM分析的实时过程。

### V1 实施优先级

| 优先级 | 优化项 | 价值 | 成本 |
|--------|--------|------|------|
| P0 | 参数批量收集 | 直接减少交互轮次 | 低 |
| P0 | 分层上下文管理 | 降本+提质 | 中 |
| P1 | Feedback Loop | 用户体验质变 | 中 |
| P1 | 实时推理可视化 | 透明度提升 | 低 |
| P2 | 跨会话记忆 | 长期价值 | 高 |
| P3 | Tool-Based API 建模 | 架构升级 | 高 |

---

## V2：分层架构重构 ^[raw/articles/text2kpi-demo-design-v2.md]

### 设计原则

1. **每一步是独立的 Step 类** — 统一接口 `run() → output`、`validate()`、`on_error()`
2. **规则是绝对权威** — LLM 只处理规则覆盖不到的部分
3. **LLM 是可插拔的** — Protocol 接口，支持重试和降级
4. **计算是受约束的** — 枚举化计算类型，确定性代码执行，不做 eval
5. **每一步都有结构化输入输出** — Pydantic schema 严格定义
6. **全过程必须可回放** — 候选 API、参数绑定、淘汰原因、调用顺序、计算公式

### 四层架构

```
Layer 4: Pipeline 编排层
  职责：步骤编排、上下文传递、错误路由、澄清流程控制
  实现：PipelineOrchestrator

Layer 3: Step 执行层
  职责：每步的具体业务逻辑
  实现：IntentStep, QueryPlanStep, RouteStep, ParamBindStep, ResultStep

Layer 2: 能力服务层
  职责：提供可复用的原子能力，被 Step 层调用
  实现：RuleEngine, LLMClient, MetadataCenter, CalcEngine, TraceCollector

Layer 1: 基础设施层
  职责：配置、日志、缓存、HTTP 客户端
  实现：Settings, Logger(structlog), Cache, HttpClient
```

依赖方向：Layer 4 → Layer 3 → Layer 2 → Layer 1，禁止反向依赖。

### 五步 Pipeline

#### Step 1：意图解析（IntentStep）

分层处理：规则引擎抽取确定性信息 → LLM 处理剩余文本 → 归一化 + 消歧 → 合法性校验。

关键改动：
- `remaining_text`：去掉已识别部分后的文本，LLM 任务大幅简化
- 规则参数**绝对不被 LLM 覆盖**（`if dim_key not in merged_params`）
- LLM 不可用时**降级为纯规则模式**，不崩溃
- 消歧和模糊是分开的两个检查

#### Step 1.5：查询编排计划（QueryPlanStep）

从"复合计算识别"升级为统一的查询编排计划生成。五种计划类型：

| 计划类型 | 场景 |
|----------|------|
| `single_api_package` | 多个指标在同一指标包 API 内，调用一次 |
| `multi_api_parallel` | 多 API 无依赖，并行调用后合并展示 |
| `multi_api_sequential` | 后 API 依赖前 API 的结果或参数转换 |
| `multi_api_merge` | 多 API 结果按共同维度拼接展示（不做运算） |
| `composite_calc` | 多 API/子查询返回后做同比、占比、差值等计算 |

新增约束：
- 优先判断单 API 是否已能返回所需指标，避免过度拆分
- 计划生成必须输出节点依赖关系
- 每个节点带 `reason`，说明为什么调这个 API

#### Step 2：API 路由与候选裁决（RouteStep）

输出候选 API 清单和淘汰原因，而非只给最终答案。路由评分维度：

1. **指标匹配度** — 指标名、别名、业务词典是否命中
2. **维度支持度** — 用户指定的维度是否被该 API 支持
3. **粒度兼容度** — "到人"/"到团队"/"到产线"是否兼容
4. **参数适用度** — 哪些参数可用、哪些被忽略、哪些导致不适用
5. **包内覆盖度** — 同一 API 是否同时包含多个用户关心指标
6. **内置比较能力** — API 本身能否返回 CY/PY、同比、环比

写入 ReasonTrace：为什么选 A 不选 B、哪些 API 因粒度被淘汰、哪些 API 内置了今年/去年两个指标。

#### Step 3：参数绑定与执行链（ParamBindStep）

从"缺没缺参"升级为"参数是怎么绑定到每个 API 上的"。

ParamBindingTrace 字段：param_name / source / source_text / canonical_value / target_api_id / applicable / ignored_reason / transform_rule / final_value

执行链支持：parallel_group / depends_on / response_selector / fallback_policy

#### Step 4：结果处理（ResultStep）

职责：从 API 返回中筛选指标 → 编排计算节点执行 → 生成数据解读 → 推荐图表 → 获取下钻推荐。

数据解读约束：纯事实描述，不做预测，不给建议。LLM 不可用时降级为简单数据摘要。

### 核心数据模型

```
OrchestrationPlan
  ├ plan_type: single_api_package | multi_api_* | composite_calc
  ├ nodes: [QueryNode]
  │   ├ node_type: api_call | merge | calc | filter
  │   ├ depends_on / parallel_group
  │   └ reason
  ├ calculation: Calculation
  │   ├ type: subtract | ratio | compare | filter | rank_then_lookup | aggregate
  │   └ operands / result_label / formula
  └ fallback_policy: fail_fast | partial_return | skip_failed

ReasonTrace（全过程推理留痕）
  ├ intent_trace / clarification_trace
  ├ plan_summary / route_candidates
  ├ param_bindings: [ParamBindingTrace]
  ├ execution_nodes: [ExecutionNodeResult]
  └ merge_trace / calc_trace / result_lineage

ChatResponse（API 响应）
  ├ need_clarification / clarification
  ├ steps: [ProcessStep]
  ├ final_result: ResultDisplay
  └ reason_trace: ReasonTrace
```

### 前端设计要点

| 功能 | 优先级 | 要点 |
|------|--------|------|
| 输入引导层 | P0 | 热门问题点选 + 输入联想补全 + 快捷标签 |
| 图表渲染 | P0 | ECharts 固定样式，AI 只返回 chart_recommendation |
| 推理抽屉 | P0 | 默认简化版时间线，展开版含指标消歧/候选列表/参数绑定表/执行链 DAG/结果血缘 |
| 澄清流程 | P0 | 多轮澄清 + 上下文保持 |
| 下钻切换 | P1 | Tab 维度切换，保持上下文不重新提问 |
| BI 跳转 | P1 | 结果卡片加带参数跳转链接 |

### 元数据增强

V2 在元数据中新增：
- `granularity` — API 支持的粒度层级
- `merge_keys` — 多 API 结果拼接的对齐键
- `param_transform_rules` — 参数上卷/转换规则（如 person → team）
- `supports_compare_in_api` — API 内置比较能力
- 指标新增 `type`（rate/amount/count/growth）和 `value_range`（异常检测）
- 消歧规则增强为结构化 options

### Phase 规划

**Phase 1（Demo MVP）** — 15 项：
- P0：Pipeline 分层重构、查询编排计划、规则引擎修正、LLM 可插拔、推理 Trace、参数绑定引擎、前端图表/输入引导/推理抽屉/澄清流程、结构化日志
- P1：下钻切换、BI 跳转、Backend DTO 契约、Backend 持久化、管理后台

**Phase 2** — 6 项：
- P0：高级复合计算、多指标拆分优化
- P1：自定义洞察报告、数据解读增强
- P2：AI 生成图表、会话持久化增强

### 代码结构对照

```
当前结构:                          新设计结构:
app/                               app/
├── core/                          ├── infra/              ← Layer 1
│   ├── pipeline.py (上帝函数)     │   ├── llm_client.py
│   ├── intent_parser.py           │   ├── http_client.py
│   └── ...                        │   └── logger.py
├── models/                        ├── services/            ← Layer 2
│   └── schemas.py                 │   ├── rule_engine.py   (重写)
└── api/                           │   ├── metadata_center.py (增强)
    └── routes.py                  │   ├── trace_collector.py (新增)
                                   │   └── calc_engine.py   (新增)
                                   ├── steps/               ← Layer 3
                                   │   ├── base.py
                                   │   ├── intent_step.py   (重写)
                                   │   ├── query_plan_step.py (新增)
                                   │   ├── route_step.py    (重写)
                                   │   ├── param_bind_step.py (重写)
                                   │   └── result_step.py   (重写)
                                   ├── pipeline/            ← Layer 4
                                   │   └── orchestrator.py
                                   └── di.py                (依赖注入)
```

### 九项关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| Pipeline 架构 | Step 基类 + Context + Orchestrator | 每步独立可测试、可重试、可替换 |
| 规则 vs LLM | 规则抽取后移除文本，LLM 只看剩余 | 规则 >99% 准确率，LLM ~85-90% |
| LLM 集成 | Protocol + json_mode + 重试 + 降级 | 不依赖特定供应商，故障不崩溃 |
| 查询编排 | OrchestrationPlan + 节点依赖 + fallback | 统一覆盖单 API 到多 API 计算全场景 |
| 复合计算 | 枚举化类型 + 确定性 Python 执行 | 不做 eval，安全可控 |
| 推理可观测 | ReasonTrace + ParamBindingTrace + Lineage | 参数匹配、候选裁决、执行链和血缘全部可见 |
| 图表渲染 | 前端固定样式，AI 只推荐类型 | 展示质量一致性 |
| 元数据管理 | Phase1:YAML+热更新, Phase2:DB+后台 | 先快速验证，再持久化 |
| 编排层 | Spring Boot 总控 + DTO 契约 | 企业级稳定性，接口不裸传 Map |

---

## 关键结论

Text2KPI 已在 Permission 层（HumanApproveStep）和 Orchestration 层（Pipeline + CompositeDetect）有良好基础，最大提升空间：

1. **Memory 层的缺失** — 没有跨会话学习能力
2. **Tool 层的粗粒度** — API 路由还是传统匹配而非 Tool-Use
3. **交互效率** — 参数收集、反馈纠错的闭环尚未建立

V2 通过分层架构重构 + 查询编排计划 + 推理可观测，将 Text2KPI 从"NL2API 工具"进化为"智能业务助手"。

## 相关概念

- [[harness-engineering]] — V1 优化方案的理论基础
- [[nl2sql-precise-mapping]] — NL2SQL 路线（对比参考：本系统走 NL2API 而非 NL2SQL）
- [[text2kpi-reference-code]] — V2 架构的核心参考代码实现
- [[text2kpi-prompt-and-config]] — Prompt 分层模板与工程化配置清单

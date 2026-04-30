---
source_url: 用户提供文档
ingested: 2026-04-30
sha256: 30d89e639b50906ca02ba386c089d924054a48e8c56d3ca3caa6996182d2bff7
---

# Harness Engineering 方法论

> 基于 Claude Code 架构逆向分析，提炼 AI Agent 人机交互系统的工程方法论，并结合 Text2KPI 项目提出优化方案。

---

## 一、什么是 Harness Engineering

**Harness（驾驭层）** 是介于 LLM 和用户之间的工程系统。它不是简单的 API 调用封装，而是一整套 **控制、引导、约束、增强** LLM 行为的运行时框架。

Claude Code 的核心思想可以总结为一个公式：

```
优秀的 AI Agent = 强大的 LLM × 精密的 Harness
```

Harness 决定了：
- LLM **能做什么**（Tool 注册与权限）
- LLM **怎么做**（System Prompt 工程）
- LLM **在什么约束下做**（Permission / Sandbox / Hooks）
- **用户如何感知和控制** 过程（Progress / UI / Interrupts）
- **系统如何从经验中学习**（Memory / Context / CLAUDE.md）

---

## 二、核心设计原则（从 Claude Code 源码提炼）

### 原则 1：Tool-First 架构

**核心洞见**：LLM 不直接操作世界，它通过调用 Tools 来行动。Tools 是 Harness 最核心的抽象。

```
Claude Code 的 Tool 定义（src/Tool.ts）：

Tool = {
  name           // 身份
  inputSchema    // 参数约束（Zod schema）
  call()         // 执行逻辑
  description()  // 动态描述（上下文相关）
  validateInput()  // 输入校验
  hasPermission()  // 权限判定
  isReadOnly()     // 读写分类
  isDestructive()  // 破坏性标记
  isConcurrencySafe() // 并发安全
  interruptBehavior() // 中断策略
  maxResultSizeChars  // 输出限制
}
```

**关键设计**：
- **每个 Tool 都是自描述的**：包含校验、权限、安全标记，不依赖外部全局配置
- **Tool 有 Deferred Loading（延迟加载）**：50+ 个 Tools 不全部塞进 System Prompt，而是通过 `ToolSearch` 工具按需发现
- **Tool 结果有大小管控**：超出 `maxResultSizeChars` 的结果会落盘，模型只看到摘要 + 文件路径

**Text2KPI 启示**：当前 API 路由就是一种 Tool 选择。可以把每个 BSC API 建模为一个 Tool，让 AI 用统一的 Tool 调用机制来路由。

### 原则 2：分层 System Prompt 工程

Claude Code 的 System Prompt 不是一个静态字符串，而是 **多层动态组装** 的：

```
System Prompt 组装流程（src/constants/prompts.ts）：

┌─────────────────────────────────────────┐
│  Static Layer（全局缓存）               │
│  ├ 身份声明（You are Claude Code...）   │
│  ├ 安全指令（Cyber Risk Instructions）  │
│  ├ 行为准则（Doing Tasks Section）      │
│  ├ 工具使用指南（Using Tools Section）  │
│  └ 行动谨慎原则（Actions with Care）   │
├─────────────── 缓存边界 ────────────────┤
│  Dynamic Layer（每轮重算）              │
│  ├ 环境信息（OS / Shell / Git 状态）    │
│  ├ CLAUDE.md 项目级指令                  │
│  ├ Memory 记忆注入                      │
│  ├ MCP Server 工具说明                  │
│  ├ Skill 可用列表                       │
│  └ System Reminders（上下文提醒）        │
└─────────────────────────────────────────┘
```

**关键设计**：
- **缓存边界（`SYSTEM_PROMPT_DYNAMIC_BOUNDARY`）**：静态部分跨对话缓存，动态部分每轮刷新，节省 Token 成本
- **`systemPromptSection()` vs `DANGEROUS_uncachedSystemPromptSection()`**：严格区分可缓存和必须刷新的 Prompt 片段
- **按需注入**：MCP 指令、Skill 列表、Memory 内容只在相关时才注入

**Text2KPI 启示**：当前 metadata.yaml 中的元数据应该动态注入到 LLM 的上下文中，而不是固定硬编码在 prompt template 里。不同 step 应该有不同的上下文注入策略。

### 原则 3：三层权限门控

```
Claude Code 权限模型（src/hooks/useCanUseTool.tsx）：

用户请求 → [Tool 调用]
            ↓
    ┌── validateInput() ──── 输入合法性校验
    │         ↓ pass
    ├── hasPermission() ──── 静态权限规则匹配
    │     ├ always_allow ──→ 直接执行
    │     ├ always_deny ───→ 拒绝 + 反馈
    │     └ ask ───────────→ 进入交互确认
    │         ↓ need_ask
    ├── Classifier ────────── AI 分类器判断风险
    │     ├ safe ──────────→ 自动放行
    │     └ risky ─────────→ 用户确认
    │         ↓ need_confirm
    └── User Prompt ───────── 用户手动批准/拒绝
              ↓
         [执行 / 拒绝]
```

**关键设计**：
- **Permission Mode 模式切换**：`default`（每次确认）→ `auto`（AI 分类放行）→ `bypass`（全部放行）
- **工具级权限粒度**：不是对所有 Tool 统一权限，而是 `alwaysAllowRules / alwaysDenyRules / alwaysAskRules` 逐工具配置
- **读写分离**：`isReadOnly()` 标记决定是否需要确认，读操作默认放行
- **破坏性标记**：`isDestructive()` 让系统知道 rm、force-push 等操作需要额外谨慎

**Text2KPI 启示**：当前 HumanApproveStep（写操作确认）是正确方向，但可以更精细化 —— 不仅按 HTTP Method 分级，还可以按具体 API + 参数组合做风险评估。

### 原则 4：Hooks 事件系统

```
Claude Code Hooks 架构：

PreToolUse Hook ──→ [拦截/修改 Tool 输入]
    ↓
Tool 执行
    ↓
PostToolUse Hook ──→ [拦截/修改 Tool 输出]
    ↓
Notification Hook ──→ [通知用户/外部系统]
```

Hooks 是用户（或系统管理员）在 `settings.json` 中配置的 shell 命令，在特定事件触发时自动执行。这使得 Harness 的行为可以被 **外部扩展** 而不需要修改代码。

**Text2KPI 启示**：Pipeline 的每个 Step 可以加入 pre/post hook，允许管理员：
- 在 IntentStep 之前注入上下文（如当前销售季节）
- 在 RouteStep 之后记录审计日志
- 在 ResultStep 之后触发 BI 系统更新

### 原则 5：Coordinator-Worker 多 Agent 协作

```
Claude Code 协调模式（src/coordinator/coordinatorMode.ts）：

Coordinator Agent（主线程）
├── 理解用户意图
├── 分解任务
├── 分派 Worker Agent（并行）
│   ├── Worker A: 调研代码
│   ├── Worker B: 实现修改
│   └── Worker C: 运行测试
├── 汇总结果
└── 向用户汇报

关键约束：
- Coordinator 不直接操作文件，只做调度
- Worker 通过 task-notification XML 汇报结果
- SendMessage 可以继续已完成的 Worker（复用上下文）
- Worker 之间不直接通信，只通过 Coordinator 协调
```

**Text2KPI 启示**：复合查询（CompositeDetectStep）的多子查询执行可以用 Coordinator-Worker 模式重构，让主 Agent 负责计划，子 Agent 并行执行各子查询。

### 原则 6：持久化记忆系统

```
Claude Code Memory 架构（src/memdir/）：

MEMORY.md（索引文件，≤200 行）
├── [user_role.md] — 用户角色与偏好
├── [feedback_testing.md] — 交互反馈记录
├── [project_auth.md] — 项目上下文
└── [reference_linear.md] — 外部资源指引

记忆类型：
- user: 用户画像（角色/知识/偏好）
- feedback: 行为纠正与确认
- project: 项目动态信息
- reference: 外部资源指针

注入时机：
- 每次对话开始时加载 MEMORY.md 到 System Prompt
- 按相关性选择性注入具体 memory 文件
- 记忆随时可增/改/删
```

**关键设计**：
- **记忆 ≠ 日志**：只存储对未来对话有价值的非显而易见的信息
- **What NOT to save**：不存代码结构（读代码就知道）、不存 git 历史（git log 就知道）
- **Verify before recommend**：记忆可能过时，使用前必须验证当前状态

**Text2KPI 启示**：这是当前项目 **最缺乏的能力** —— 没有跨会话学习机制。用户纠正过的错误路由、确认过的正确理解，都没有被系统记住。

---

## 三、Harness Engineering 方法论框架

将以上原则归纳为一套可操作的方法论：

### 第一层：Tool 层（能力定义）

| 维度 | 设计要点 | Claude Code 实现 |
|------|----------|-----------------|
| 能力注册 | 每个能力独立为 Tool，自包含 schema/validation/permission | `buildTool()` 工厂函数 |
| 能力发现 | 不一次性暴露所有能力，按需发现 | `ToolSearch` + `shouldDefer` |
| 输出管控 | 限制 Tool 输出大小，超限降级 | `maxResultSizeChars` + 落盘机制 |
| 并发标记 | 标记哪些 Tool 可并行执行 | `isConcurrencySafe()` |
| 中断策略 | 定义用户中断时的行为 | `interruptBehavior(): 'cancel' \| 'block'` |

### 第二层：Prompt 层（行为引导）

| 维度 | 设计要点 | Claude Code 实现 |
|------|----------|-----------------|
| 分层组装 | 静态 + 动态两层，缓存友好 | `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` |
| 上下文注入 | 环境、项目、记忆按需注入 | `getUserContext()` / `getSystemContext()` |
| 角色设定 | 根据场景切换身份 | `getCLISyspromptPrefix()` |
| 行为约束 | 在 prompt 中嵌入安全/风格规则 | `getActionsSection()` / `CYBER_RISK_INSTRUCTION` |
| Reminder 机制 | 在 tool result 中插入系统提醒 | `<system-reminder>` 标签 |

### 第三层：Permission 层（安全控制）

| 维度 | 设计要点 | Claude Code 实现 |
|------|----------|-----------------|
| 静态规则 | 基于 Tool 名 + 参数的白名单/黑名单 | `alwaysAllow / alwaysDeny / alwaysAsk` |
| 动态分类 | AI Classifier 实时评估风险 | `classifierApprovals` |
| 用户确认 | 高风险操作交由用户决策 | `PermissionRequest` UI 组件 |
| 模式切换 | 支持不同安全级别 | `PermissionMode` |
| 审计追踪 | 记录所有权限决策 | `logPermissionDecision()` |

### 第四层：Orchestration 层（流程编排）

| 维度 | 设计要点 | Claude Code 实现 |
|------|----------|-----------------|
| 主循环 | LLM 调用 → Tool 执行 → 结果注入 → 继续 | `QueryEngine.submitMessage()` |
| 多 Agent | Coordinator 调度 + Worker 执行 | `coordinatorMode.ts` |
| 任务管理 | 可追踪、可取消的后台任务 | `TaskCreate / TaskStop / TaskUpdate` |
| 流式输出 | 实时展示中间状态 | `ToolCallProgress` + `SpinnerMode` |
| 上下文压缩 | 长对话自动摘要 | Compact 机制 + context limit 管理 |

### 第五层：Memory 层（学习积累）

| 维度 | 设计要点 | Claude Code 实现 |
|------|----------|-----------------|
| 记忆分类 | user / feedback / project / reference | `memoryTypes.ts` |
| 索引机制 | MEMORY.md 索引 + 独立文件存储 | `ENTRYPOINT_NAME = 'MEMORY.md'` |
| 注入策略 | 按相关性注入到 System Prompt | `loadMemoryPrompt()` |
| 过期机制 | 使用前验证，过时则更新/删除 | "Verify before recommend" 原则 |
| 排除机制 | 不存可从代码/git 推导的信息 | "What NOT to save" 规则 |

---

## 四、Text2KPI 项目优化方案

基于以上方法论，对当前 Text2KPI 的人机交互体验提出优化：

### 4.1 当前架构痛点诊断

```
当前 Text2KPI Pipeline：

用户问题 → ScopeGuard → Intent → CompositeDetect → [PlanReview]
         → Route → [HumanApprove] → ParamFill → Result

痛点：
❌ 1. 无事后纠错机制 — 结果错了只能重新问
❌ 2. 参数补全低效 — 缺多个参数时逐个询问
❌ 3. ScopeGuard 不够精准 — 仅关键字匹配，非真实可回答性判断
❌ 4. 指标置信度不透明 — 用户不知道 AI 有多确定
❌ 5. 无跨会话学习 — 每次对话从零开始
❌ 6. Pipeline 过于刚性 — 步骤固定，无法灵活跳转
```

### 4.2 优化方案一：引入 Feedback Loop（反馈闭环）

**对标 Claude Code**：`feedback` 类型 Memory + 权限拒绝追踪

```
当前流程：
用户提问 → Pipeline → 结果 → （结束）

优化后：
用户提问 → Pipeline → 结果 → 反馈收集
                                ├ "结果正确" → 正向记录
                                ├ "API选错了" → 路由纠错 → 从 RouteStep 重跑
                                ├ "参数不对" → 参数纠错 → 从 ParamFill 重跑
                                └ "指标理解错" → 意图纠错 → 从 IntentStep 重跑
```

**实现要点**：
- 在 ResultCard 中增加 **"这个结果对吗？"** 反馈按钮
- 支持 **断点续跑**：用户指出某步有问题，从该步重新执行
- 纠错记录存入 **FeedbackStore**，影响后续同类查询的置信度

### 4.3 优化方案二：Tool-Based API 建模

**对标 Claude Code**：`Tool` 抽象 + `ToolSearch` 按需发现

```python
# 当前：API 路由是元数据匹配 + LLM 评分
# 优化：每个 BSC API 建模为 Tool，利用 LLM 原生 Tool-Use 能力

class BSCTool:
    name: str             # "implant_performance"
    description: str      # 动态生成，包含可用指标、参数说明
    input_schema: dict    # JSON Schema，从 metadata 自动生成
    required_params: list # ["bu", "year"]
    risk_level: str       # "read" | "write_low" | "write_high"

    def validate(self, input):
        # 参数校验 + 枚举值验证
        ...

    def execute(self, input, mode="real"):
        # 调用实际 API（支持 mock/sandbox/real）
        ...
```

**优势**：
- LLM 原生支持 Tool-Use，路由准确率更高
- 参数校验自动化，减少 ParamFill 中的人工补全
- 新 API 上线只需注册 Tool，无需修改 Pipeline

### 4.4 优化方案三：智能参数批量收集

**对标 Claude Code**：`AskUserQuestion` Tool 的结构化交互

```
当前：缺 bu → 问 bu → 缺 year → 问 year → 缺 region → 问 region（3轮）

优化：一次性识别所有缺失参数，生成结构化表单
┌────────────────────────────────┐
│  请补充以下信息：               │
│                                │
│  事业部：[A BU ▼]             │ ← 下拉选择（从 enum_values 生成）
│  年份：  [2026  ▼]            │ ← 默认当前年
│  区域：  [全部  ▼]（可选）     │ ← 标注可选
│                                │
│  [确认] [取消]                 │
└────────────────────────────────┘
```

**实现要点**：
- ParamFillStep 一次性收集所有缺失参数
- 前端渲染为结构化表单（非纯文本对话）
- 可选参数提供默认值，减少用户操作

### 4.5 优化方案四：分层上下文管理

**对标 Claude Code**：`systemPromptSection()` 分层 + 缓存边界

```
当前：所有 metadata 一次性塞进 LLM prompt
优化：按 Step 动态注入相关上下文

ScopeGuard Step 上下文：
  └ tenant_profile + blocked_entities（轻量）

IntentStep 上下文：
  └ metric 名称/别名列表 + dimension 枚举值

RouteStep 上下文：
  └ 匹配到的 API 完整定义 + 参数要求

ResultStep 上下文：
  └ API 返回的数据结构 + 计算公式说明
```

**优势**：
- 每步只注入必要信息，减少 Token 消耗
- 提高 LLM 专注度，减少幻觉
- 支持更大规模的 API 目录（当前 113+ API 全注入会爆 context）

### 4.6 优化方案五：跨会话记忆系统

**对标 Claude Code**：`memdir/` 持久化记忆

```
Text2KPI Memory 设计：

memory/
├── MEMORY.md              # 索引
├── user_preferences.md    # 用户偏好（常查指标、常用维度）
├── feedback_routing.md    # 路由纠错记录
├── feedback_params.md     # 参数纠错记录
├── project_metrics.md     # 新增/变更指标记录
└── reference_aliases.md   # 用户自定义别名

记忆类型映射：
- user → 用户的查询偏好、常用维度组合、角色权限
- feedback → "上次问XX被路由到API-A，用户纠正为API-B"
- project → "2026-Q2 新增了API-C，覆盖供应链指标"
- reference → "华东区域包含哪些省份的定义见 metadata.yaml"
```

**应用场景**：
1. **个性化默认值**：用户经常查华东+A BU → 缺省参数自动填充
2. **纠错学习**：上次"达成率"被错误路由 → 这次优先选择正确 API
3. **别名记忆**：用户说"小王的指标"→ 记住"小王 = 华东区域经理，关注植入达成率"

### 4.7 优化方案六：实时推理可视化

**对标 Claude Code**：`ToolCallProgress` + `SpinnerMode` 实时状态

```
当前 ProcessTimeline：步骤级（✓ / ? / ✗）
优化为：步骤内实时推理流

┌─ 意图解析 ─────────────────────────────────┐
│  [规则匹配] 命中维度: BU=A, Year=2026      │ ← 实时
│  [规则匹配] 命中指标: 植入达成率 (0.95)     │ ← 实时
│  [LLM分析] 跳过（规则引擎已高置信度匹配）   │ ← 实时
│  ✓ 完成（耗时 120ms）                       │
└────────────────────────────────────────────┘
┌─ API路由 ──────────────────────────────────┐
│  [候选] implant_performance (0.92) ✓       │ ← 展开可看评分细节
│  [候选] sales_overview (0.31) ✗            │
│  ✓ 选择: implant_performance               │
└────────────────────────────────────────────┘
```

---

## 五、实施优先级建议

| 优先级 | 优化项 | 价值 | 成本 | 依赖 |
|--------|--------|------|------|------|
| P0 | 参数批量收集 | 直接减少交互轮次 | 低 | 前端表单组件 |
| P0 | 分层上下文管理 | 降本 + 提质 | 中 | Pipeline 改造 |
| P1 | Feedback Loop | 用户体验质变 | 中 | 断点续跑机制 |
| P1 | 实时推理可视化 | 透明度提升 | 低 | SSE 事件细化 |
| P2 | 跨会话记忆 | 长期价值 | 高 | 记忆存储 + 注入 |
| P3 | Tool-Based API 建模 | 架构升级 | 高 | LLM 原生 Tool-Use |

---

## 六、总结

Claude Code 的 Harness 工程实践揭示了一个核心理念：

> **AI Agent 的质量不仅取决于模型本身，更取决于围绕模型构建的控制系统。**

五层 Harness 架构：

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

Text2KPI 已经在 Permission 层（HumanApproveStep）和 Orchestration 层（Pipeline + CompositeDetect）有了良好基础。最大的提升空间在于：
1. **Memory 层的缺失** — 没有跨会话学习能力
2. **Tool 层的粗粒度** — API 路由还是传统匹配而非 Tool-Use
3. **交互效率** — 参数收集、反馈纠错的闭环尚未建立

这三个方向是将 Text2KPI 从 "NL2API 工具" 进化为 "智能业务助手" 的关键路径。

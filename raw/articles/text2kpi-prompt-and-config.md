---
ingested: 2026-04-30
sha256: 3c32e76dff8b6d44d034894c9b46f8f1aa9cf60d634061091845031811ecdb6c
source_url: file://trans-import/04_Prompt模板与工程化配置清单.md
title: 课程同款 · Prompt 模板 + 工程化配置清单
---

# 课程同款 · Prompt 模板 + 工程化配置清单

> 配套公开课《Harness Engineering × 企业级 AI Agent》
> 用于在你自己的项目里快速复刻 Text2KPI 同款工程结构

---

## 目录

1. [System Prompt 分层模板](#1-system-prompt-分层模板)
2. [四步链路 Prompt 模板](#2-四步链路-prompt-模板)
3. [澄清 / 消歧 Prompt 模板](#3-澄清--消歧-prompt-模板)
4. [Tool（API）自描述模板](#4-toolapi-自描述模板)
5. [元数据中心 · 配置 Schema](#5-元数据中心--配置-schema)
6. [置信度 & 校验阈值清单](#6-置信度--校验阈值清单)
7. [工程化落地 Checklist（可直接对照交付）](#7-工程化落地-checklist可直接对照交付)
8. [上线前 Go / No-Go 评审清单](#8-上线前-go--no-go-评审清单)

---

## 1. System Prompt 分层模板

> Harness 原则：**静态层走缓存（不变 / 业务规则）·  动态层走拼接（会话上下文）**

### 1.1 静态层（系统级，cacheable）

```text
# 角色
你是企业级数据问答 Agent，唯一职责是把用户的自然语言问题
转化为结构化意图，再交由下游引擎调用业务 API。

# 严格不要
- 不要直接回答业务结论（除非来自 API 返回）
- 不要自由生成 SQL
- 不要自由选择 API（你只输出"指标词 + 维度词"，由引擎匹配）
- 不要做预测、推荐、建议性表述
- 不要在结果解读里出现 API 返回中没有的数字

# 输出格式
始终输出合法 JSON，遵循下游 schema。任何文字解读放在指定字段。

# 业务术语标准
{{INJECT: business_glossary}}

# 已注册的指标列表
{{INJECT: registered_metrics_brief}}
```

> 💡 把 `{{INJECT}}` 占位的部分通过分层 Prompt 工具拼到上面，
> 占位之外的文字保持稳定 → 命中 prompt cache。

### 1.2 动态层（会话级）

```text
# 当前会话
- session_id: {{session_id}}
- user_role: {{role}}              # 影响可见 API 范围
- locale: {{locale}}                # 中文 / 英文输出风格
- now: {{iso_datetime}}

# 最近 N 轮对话（仅保留 user / assistant 摘要）
{{conversation_summary}}

# 当前用户原话
"{{user_query}}"
```

---

## 2. 四步链路 Prompt 模板

### Step 1 · 意图解析

```text
任务：从用户提问中抽取「指标词 + 维度词 + 时间词 + 排序/对比词」。

输出 JSON：
{
  "intent_type": "metric_query | drill_down | compare | unknown",
  "metrics":      [{"raw": "...", "confidence": 0.0~1.0}],
  "dimensions":   {"<dim_name>": {"raw": "...", "confidence": 0.0~1.0}},
  "time":         {"raw": "...", "normalized": null, "confidence": 0.0~1.0},
  "compare":      null | "YoY" | "MoM" | "vs_<x>",
  "rank":         null | {"order": "asc|desc", "limit": int},
  "need_clarify": bool,
  "clarify_reason": "<只有 need_clarify=true 时填>"
}

约束：
- 不要在 JSON 之外输出任何字符
- 任何字段不确定 → 写 null + 降低 confidence
- "今年/去年/Q1/上半年" 等时间词不要自己换算，原样填 raw，由规则层处理
```

### Step 2 · 指标 → API 路由（仅候选打分，最终由引擎决策）

```text
任务：在以下候选 API 中，为每个候选给出"是否覆盖用户需求"的判断。

候选：
{{candidate_apis_with_metrics}}

输出 JSON：
{
  "ranking": [
    {"api_id": "...", "score": 0.0~1.0, "reason": "..."},
    ...
  ]
}

约束：
- 只在给出的候选里选，不要发明 api_id
- score >= 0.7 才算"高置信"
```

### Step 3 · 参数补全（仅在规则未抽全时调用）

```text
任务：根据用户原话和已抽取参数，补全缺失参数，但不要替用户假设。

已知参数：
{{known_params}}

API 必填参数：
{{required_params_with_enum}}

输出 JSON：
{
  "filled": {"<param>": {"value": "...", "confidence": 0.0~1.0, "source": "user_text|default|inferred"}},
  "still_missing": ["<param>", ...]
}

约束：
- enum 类参数的 value 必须在 enum 里，否则填 null
- "默认值"只能取下游配置中显式标注的 default
```

### Step 4 · 结果解读（事实化）

```text
任务：基于下方 API 返回 JSON，撰写不超过 80 字的中文事实摘要。

API 返回：
{{api_response_json}}

用户原话：
"{{user_query}}"

约束：
- 只描述返回中已有的数字与维度
- 不做趋势预测、不给行动建议
- 不要在文字里出现"建议/可能/或许/预计"等推测词
- 数字保留与返回字段相同的小数位
```

---

## 3. 澄清 / 消歧 Prompt 模板

```text
任务：当下游判定 need_clarify = true 时，生成一段不超过 30 字的中文澄清提问，
并给出 2~4 个可点选的选项。

上下文：
- 用户原话："{{user_query}}"
- 缺失/歧义信息："{{clarify_reason}}"
- 候选选项（来自元数据中心）：
{{disambiguation_options}}

输出 JSON：
{
  "question": "...",
  "options": [
    {"label": "...", "value": "...", "hint": "..."}
  ]
}

约束：
- 不要用"您是想…"这种过度礼貌的废话开头
- options.value 必须能直接喂回 Step1 重新解析
```

---

## 4. Tool（API）自描述模板

> 把每个业务 API 写成下面这个结构，注册到元数据中心。
> AI 不直接读这个，但**引擎读它来做路由 / 校验 / 渲染**。

```yaml
- id: implant_performance
  name: 植入表现
  endpoint: POST /api/implant-performance
  description: 查询各产线 / 团队的植入业绩表现
  visibility:                    # 谁能用
    roles: [bu_lead, sales_ops, exec]

  required_params:
    - name: bu
      type: enum
      enum: [A, B]
      aliases: { A: ["A BU", "大器械"], B: ["B BU", "小器械"] }
    - name: year
      type: int
      range: [2020, 2030]

  optional_params:
    - name: product_line
      type: enum
      enum: [心血管, 骨科, 影像]
    - name: period
      type: enum
      enum: [YTD, Q1, Q2, Q3, Q4, H1, H2, FY]
      default: YTD

  output_metrics:
    - id: implant_achievement_rate
      name: 植入达成率
      aliases: ["达成", "达成率", "植入达成"]
      unit: "%"
      visualization: { default: bar, allow: [bar, line] }
    - id: implant_amount
      name: 植入金额
      aliases: ["植入金额", "金额"]
      unit: "万元"

  related_drilldown:
    - { dimension: team,          api: implant_by_team }
    - { dimension: hospital_type, api: implant_by_hospital }

  validation_rules:
    - "year >= 2020"
    - "if product_line in [心血管] then bu must = A"
```

---

## 5. 元数据中心 · 配置 Schema

### 5.1 业务语义字典

```yaml
synonyms:
  达成:    ["达成率", "完成率", "做得怎么样"]
  销量:    ["销售数量", "卖了多少"]
  销售额:  ["销售金额", "金额", "卖了多少钱", "revenue"]
  增长:    ["同比增长", "增长率", "growth"]
  覆盖:    ["覆盖率", "覆盖了多少", "coverage"]

dimension_aliases:
  BU:    ["事业部", "业务单元", "business unit"]
  产线:  ["产品线", "product line"]
  团队:  ["team", "销售团队"]

disambiguation:
  销量:
    hint: "您说的"销量"是指："
    options:
      - { label: "植入数量",        metric: implant_qty }
      - { label: "经销商发货数量",  metric: dealer_sales_qty }
      - { label: "销售金额",        metric: sales_amount }
```

### 5.2 时间表达式规则（不进 LLM）

```yaml
time_rules:
  - { pattern: "^今年$",       map: { year: "$now.year" } }
  - { pattern: "^去年$",       map: { year: "$now.year-1" } }
  - { pattern: "^前年$",       map: { year: "$now.year-2" } }
  - { pattern: "^(\\d{4})年$", map: { year: "$1" } }
  - { pattern: "^(Q[1-4])$",   map: { period: "$1" } }
  - { pattern: "^上半年$",      map: { period: "H1" } }
  - { pattern: "^下半年$",      map: { period: "H2" } }
  - { pattern: "^近(\\d+)个月$", map: { period: "L${1}M" } }
```

---

## 6. 置信度 & 校验阈值清单

| 阈值 | 默认值 | 行为 |
|------|--------|------|
| `auto_proceed` | ≥ 0.85 | 直接进入下一步 |
| `confirm`      | 0.60–0.85 | 展示理解，等用户点「确认」 |
| `clarify`      | < 0.60 | 主动反问 |
| `route_high`   | ≥ 0.70 | API 路由判定为高置信 |
| `route_tie`    | top1 - top2 < 0.05 | 触发维度消歧 |

> ⚠️ 这些阈值**必须**配置化（DB / YAML），不要硬编码进 Prompt 或代码。

---

## 7. 工程化落地 Checklist（可直接对照交付）

### 7.1 元数据中心

- [ ] API 注册表（id / endpoint / params / output_metrics / aliases）
- [ ] 业务语义字典（synonyms / aliases / disambiguation）
- [ ] 时间 / 排序 / 比较 规则表
- [ ] 维度枚举值表（含别名）
- [ ] 下钻关系（dim → api）
- [ ] 阈值配置表（auto_proceed / confirm / clarify…）
- [ ] 全部支持**热更新**（管理后台改 → 次秒生效）

### 7.2 AI 能力层（Python / FastAPI）

- [ ] Step1 意图解析（带 confidence）
- [ ] Step2 路由（**引擎决策，LLM 仅打分**）
- [ ] Step3 参数补全（规则优先 → LLM 兜底）
- [ ] Step4 解读（事实化、限字、禁预测）
- [ ] 澄清生成器
- [ ] 五层约束执行器（L1–L5 各自有可观测性）
- [ ] 流式推送（每步 event 推前端）
- [ ] Prompt cache 命中率 ≥ 70%

### 7.3 编排层（Spring Boot）

- [ ] 会话 / 鉴权 / 审计
- [ ] 调用业务 API 的网关代理
- [ ] 全链路 trace（traceId 贯穿前端 → 编排 → AI → API）
- [ ] 超时 / 熔断 / 重试
- [ ] 调用记录入库（用于运营回放）

### 7.4 前端

- [ ] 四步过程实时展示（流式）
- [ ] 澄清卡片
- [ ] 结果区 + BI 图表 + 下钻锚点 + 跳转 BI 页
- [ ] 可中断（用户可在任一步打断）
- [ ] 错误态友好降级

### 7.5 持续运营

- [ ] 用户提问日志 + 命中率看板
- [ ] 未命中 case 周度聚合 + 责任人
- [ ] 词典 / 规则 / 枚举值 周更新流水
- [ ] AB 测试通道（不同 Prompt / 阈值）

---

## 8. 上线前 Go / No-Go 评审清单

> 任何一项**未通过**，不得上线生产。

### 安全 / 合规

- [ ] LLM 不直接落数据库
- [ ] 全部 API 调用走编排层网关，带身份
- [ ] 用户提问 + 返回**全量审计**，可按 traceId 回放
- [ ] PII / 敏感字段在前端 / 日志双脱敏

### 准确性

- [ ] 测试集 ≥ 200 条，覆盖：精确 / 模糊 / 多指标 / 下钻
- [ ] 综合命中率 ≥ 90%
- [ ] 澄清准确率（澄清后能解决）≥ 85%
- [ ] 解读不含预测 / 推测词（lint 规则强制）

### 可用性

- [ ] P95 端到端响应 ≤ 5 s
- [ ] 任一步失败可降级（至少返回错误说明 + 联系入口）
- [ ] 用户可中断 + 重试

### 运营

- [ ] 命中率看板上线
- [ ] 未命中 case 入工单
- [ ] 元数据热更新通道有评审 + 回滚

---

> 📮 若你在自己项目落地时遇到具体问题，欢迎在课程社群里发出来一起讨论。
> 本清单会随实战持续更新。

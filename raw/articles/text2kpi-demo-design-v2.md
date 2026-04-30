---
source_url: file://trans-import/02_Text2KPI_Demo设计方案.md
ingested: 2026-04-30
sha256: be03fcbe99cabbed4a35808daedaf86debc93f44bd94e746e0ff8c686be67cc5
---

# Text2KPI AI 问数系统 — 设计方案 V2

---

## 一、项目定位与核心需求

### 客户核心诉求（会议纪要 + 字幕提炼）

> "这个API里面无论包了什么指标（不要原子化API），需要清晰展示判断API、参数、调取的过程；然后可以支持灵活提问，把这个技术路线走通。"

| 编号 | 需求 | 说明 |
|------|------|------|
| R1 | 不要原子化API | 使用现有"指标包"API，AI从返回结果中筛选用户需要的指标 |
| R2 | 清晰展示判断过程 | 用户能看到：AI理解 → 匹配API → 传参 → 取数 的全过程 |
| R3 | 灵活提问 | 支持模糊问题（"今年做得怎么样"）和精确问题（"A BU B产线的植入达成"） |
| R4 | 意图澄清 | 模糊问题引导收敛，精确问题直接查询 |
| R5 | 结果可信 | 展示数据来源、API调用链、参数列表 |
| R6 | 指标复合计算 | 复杂问题拆解为多指标查询+运算（如同比、占比、对比） |
| R7 | BI图表 + 下钻 | 前端固定样式渲染图表，支持维度下钻切换 |
| R8 | 管理后台 | 业务语义字典、API注册表、知识库的可视化配置 |
| R9 | 多API编排 | 自然语言不一定一对一映射单个KPI或单个API，可能需要多个API顺序/并行/拼接调用 |
| R10 | 全量推理过程可见 | 不只展示最终命中的API，还要展示指标消歧、参数匹配、路由淘汰、调用链和计算过程 |

### 本系统不是 NL2SQL

本系统是 **NL2API**：自然语言 → 理解意图 → 匹配已注册API → 填充参数 → 调用取数 → 展示结果。不生成SQL，不直接查数据库。

---

## 二、系统架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                         前端展示层 (React)                           │
│                                                                       │
│  ┌───────────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │    对话界面         │  │    管理后台       │  │   报告查看       │   │
│  │  ├ 输入引导层       │  │  ├ API注册管理    │  │  ├ 报告列表      │   │
│  │  │ ├ 热门问题(点选) │  │  ├ 语义字典管理   │  │  └ 报告详情      │   │
│  │  │ ├ 输入联想/补全  │  │  └ 报告规则配置   │  │                 │   │
│  │  │ └ 快捷标签       │  │                   │  │                 │   │
│  │  ├ 过程时间线       │  │                   │  │                 │   │
│  │  ├ 澄清交互卡片    │  │                   │  │                 │   │
│  │  ├ 结果卡片         │  │                   │  │                 │   │
│  │  ├ 图表渲染(ECharts)│  │                   │  │                 │   │
│  │  ├ 下钻维度切换     │  │                   │  │                 │   │
│  │  └ BI页面跳转       │  │                   │  │                 │   │
│  └───────────────────┘  └──────────────────┘  └─────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      编排层 (Spring Boot)                            │
│                                                                       │
│  ┌────────────┐ ┌──────────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ 会话管理    │ │ 请求路由      │ │ 审计日志  │ │ 报告调度(定时) │   │
│  │ (Redis)     │ │ (DTO契约)    │ │ (DB持久) │ │                │   │
│  └────────────┘ └──────────────┘ └──────────┘ └────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              元数据管理服务 (CRUD + 热更新)                    │   │
│  │    API注册表 │ 业务语义字典 │ 维度枚举 │ 消歧规则 │ 报告模板  │   │
│  │                      持久化到 DB                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      AI 能力层 (Python/FastAPI)                      │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Pipeline 编排器                             │   │
│  │          按 Step 接口组织，每步独立、可测试、可重试            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐ │
│  │ Step 1    │ │ Step 1.5     │ │ Step 2   │ │ Step 3        │ │ Step 4   │ │
│  │ 意图解析  │ │ 查询编排计划 │ │ API路由  │ │ 参数绑定      │ │ 结果处理 │ │
│  │ & 澄清   │ │ & 复合识别   │ │ & 候选裁决│ │ & 执行链      │ │ & 展示   │ │
│  └──────────┘ └──────────────┘ └──────────┘ └──────────────┘ └──────────┘ │
│       │                                                              │
│  ┌────▼─────────────────────────────────────────────────────────┐   │
│  │                    基础能力层                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│   │
│  │  │ 规则引擎  │ │ LLM客户端│ │ 元数据中心│ │ 计算执行引擎│ │ Trace服务 ││   │
│  │  │(确定性)   │ │(可插拔)  │ │(缓存+热更)│ │(受约束运算)│ │(全过程留痕)││   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘│   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      业务数据层                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │     客户 Workstation API（指标包形式）                         │   │
│  │     /api/implant-performance  → 返回10+指标                   │   │
│  │     /api/hospital-coverage    → 返回8+指标                    │   │
│  │     /api/dealer-sales         → 返回12+指标                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、AI能力层分层设计（核心）

### 设计原则

1. **每一步是独立的 Step 类**，有统一接口 `run(input) → output`、`validate()`、`on_error()`
2. **规则是绝对权威**，LLM只处理规则覆盖不到的部分
3. **LLM是可插拔的**，通过统一接口调用，支持重试和降级
4. **计算是受约束的**，枚举化的计算类型，确定性代码执行，不做 eval
5. **每一步都有结构化的输入输出**，用 Pydantic schema 严格定义
6. **全过程必须可回放**，包括候选API、参数绑定、淘汰原因、调用顺序、计算公式

### 3.1 分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Pipeline 编排层                                        │
│  职责：步骤编排、上下文传递、错误路由、澄清流程控制               │
│  实现：PipelineOrchestrator 类                                   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Step 执行层                                            │
│  职责：每步的具体业务逻辑                                        │
│  实现：IntentStep, QueryPlanStep, RouteStep,                     │
│        ParamBindStep, ResultStep — 每个是独立类                  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: 能力服务层                                             │
│  职责：提供可复用的原子能力，被 Step 层调用                      │
│  实现：RuleEngine, LLMClient, MetadataCenter, CalcEngine,        │
│        TraceCollector                                            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: 基础设施层                                             │
│  职责：配置、日志、缓存、HTTP客户端                              │
│  实现：Settings, Logger, Cache, HttpClient                       │
└─────────────────────────────────────────────────────────────────┘
```

依赖方向：Layer 4 → Layer 3 → Layer 2 → Layer 1，禁止反向依赖。

### 3.2 Layer 1: 基础设施层

#### 3.2.1 LLM客户端（可插拔）

```python
# 接口定义
class LLMClient(Protocol):
    def chat(self, system: str, user: str, json_mode: bool = False) -> LLMResponse: ...

@dataclass
class LLMResponse:
    content: str
    parsed_json: dict | None   # json_mode=True 时自动解析
    usage: TokenUsage
    latency_ms: int

# 实现
class OpenAILLMClient(LLMClient):
    """OpenAI/兼容API实现，带重试和降级"""
    def __init__(self, api_key, base_url, model, max_retries=2, timeout=10):
        ...

    def chat(self, system, user, json_mode=False) -> LLMResponse:
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}],
                    response_format={"type": "json_object"} if json_mode else NOT_GIVEN,
                    temperature=0.1,
                    timeout=self.timeout,
                )
                content = response.choices[0].message.content
                parsed = json.loads(content) if json_mode else None
                return LLMResponse(content=content, parsed_json=parsed, ...)
            except (APITimeoutError, RateLimitError) as e:
                if attempt == self.max_retries:
                    raise LLMUnavailableError(f"LLM调用失败: {e}") from e
                logger.warning(f"LLM重试 {attempt+1}/{self.max_retries}: {e}")
```

**关键改动**：
- 使用 Protocol 定义接口，支持替换为 Claude/本地模型
- json_mode 由 API 原生支持，不再手动剥离 markdown code block
- 内置重试逻辑，超时控制
- 返回结构化的 LLMResponse，含 latency 和 token 用量

#### 3.2.2 日志与可观测性

```python
import structlog

logger = structlog.get_logger()

# 每个步骤内部调用
logger.info("step.intent.rule_extract", extracted_params={"year": 2026, "bu": "A"})
logger.info("step.intent.llm_parse", metrics=["植入达成"], confidence=0.92, latency_ms=320)
logger.warning("step.route.multi_match", matched_apis=["implant_performance", "dealer_sales"])
logger.error("step.api_call.failed", api="/api/implant-performance", error="timeout")
```

### 3.3 Layer 2: 能力服务层

#### 3.3.1 规则引擎（RuleEngine）

规则引擎是**系统中最高优先级的处理层**，其输出是绝对可信的。

```python
class RuleEngine:
    """确定性规则抽取器，准确率 >99%，优先于 LLM"""

    def __init__(self, metadata: MetadataCenter):
        self.metadata = metadata
        self._compile_patterns()

    def extract(self, query: str) -> RuleResult:
        """
        从用户原文中抽取所有能确定性识别的信息。

        返回:
          - extracted_params: 已抽取的参数（绝对可信）
          - remaining_text:  移除已抽取部分后的剩余文本（交给LLM）
          - sources:         每个参数的来源记录
        """
        params = {}
        sources = {}
        text = query

        # 第一优先：枚举值精确匹配（从元数据加载）
        text, enum_params = self._extract_enum_values(text)
        params.update(enum_params)
        for k in enum_params:
            sources[k] = ParamSource(type="rule_enum", confidence=0.99)

        # 第二优先：时间表达式
        text, time_params = self._extract_time(text)
        params.update(time_params)
        for k in time_params:
            sources[k] = ParamSource(type="rule_time", confidence=0.99)

        # 第三优先：排序/TopN
        text, rank_params = self._extract_rank(text)
        params.update(rank_params)
        for k in rank_params:
            sources[k] = ParamSource(type="rule_rank", confidence=0.99)

        # 第四优先：对比类型
        text, compare_params = self._extract_compare(text)
        params.update(compare_params)
        for k in compare_params:
            sources[k] = ParamSource(type="rule_compare", confidence=0.99)

        return RuleResult(
            extracted_params=params,
            remaining_text=text.strip(),
            sources=sources,
        )

    def _extract_enum_values(self, text: str) -> tuple[str, dict]:
        """
        从元数据中加载所有维度的枚举值，做最长匹配。

        关键：最长匹配优先，避免 "A BU" 匹配到 "A" 而非 "A BU"。
        匹配后从原文中移除已匹配的部分。
        """
        params = {}
        # 按匹配文本长度降序排列，确保最长匹配优先
        all_aliases = []  # [(alias_text, dim_key, canonical_value)]
        for dim_key, dim_cfg in self.metadata.get_dimensions().items():
            for canonical, aliases in dim_cfg["enum_values"].items():
                for alias in [canonical] + aliases:
                    all_aliases.append((alias, dim_key, canonical))
        all_aliases.sort(key=lambda x: len(x[0]), reverse=True)

        for alias, dim_key, canonical in all_aliases:
            if alias.lower() in text.lower() and dim_key not in params:
                params[dim_key] = canonical
                # 从原文中移除已匹配的部分
                idx = text.lower().index(alias.lower())
                text = text[:idx] + text[idx + len(alias):]
        return text, params
```

**关键改动 vs 当前实现**：
- 抽取后**从原文中移除已匹配部分**，LLM只看剩余文本
- 枚举值匹配使用**最长匹配优先**，避免短匹配覆盖长匹配
- 每个参数都带 `ParamSource`，标明来源和置信度
- 返回 `remaining_text`，这是传给LLM的唯一输入

#### 3.3.2 元数据中心（MetadataCenter）

```python
class MetadataCenter:
    """
    元数据中心 — 系统的核心配置源。

    数据来源：
    - Phase 1: metadata.yaml 文件（启动加载 + 热更新API）
    - Phase 2: 数据库（管理后台CRUD → DB → 热更新通知）

    职责：
    - 维护 API注册表、语义字典、维度枚举、消歧规则
    - 提供高效的查询接口（预构建索引）
    - 支持热更新（不重启服务）
    """

    def __init__(self, config_path: str):
        self._raw = {}
        self._metric_index: dict[str, list[tuple[str, str]]] = {}  # keyword → [(api_id, metric_id)]
        self._enum_index: dict[str, dict[str, str]] = {}           # dim_key → {alias → canonical}
        self._synonym_index: dict[str, str] = {}                    # synonym → standard_keyword
        self.load(config_path)

    def load(self, path: str):
        """加载并验证元数据，构建索引"""
        raw = yaml.safe_load(open(path))
        self._validate_schema(raw)  # 启动时验证，不合法则拒绝加载
        self._raw = raw
        self._build_indices()

    def _validate_schema(self, raw: dict):
        """验证元数据结构完整性"""
        required_sections = ["apis", "synonyms", "dimensions"]
        for section in required_sections:
            if section not in raw:
                raise MetadataValidationError(f"元数据缺少必要节: {section}")
        for api in raw["apis"]:
            if not api.get("id") or not api.get("endpoint"):
                raise MetadataValidationError(f"API定义不完整: {api}")
            for metric in api.get("output_metrics", []):
                if not metric.get("id") or not metric.get("name"):
                    raise MetadataValidationError(f"指标定义不完整: {metric}")

    def _build_indices(self):
        """预构建所有查询索引"""
        self._metric_index.clear()
        self._enum_index.clear()
        self._synonym_index.clear()

        # 指标索引：keyword → [(api_id, metric_id)]
        for api in self._raw["apis"]:
            for metric in api["output_metrics"]:
                keys = [metric["name"].lower()] + [a.lower() for a in metric.get("aliases", [])]
                for key in keys:
                    self._metric_index.setdefault(key, []).append((api["id"], metric["id"]))

        # 同义词索引：synonym → standard_keyword
        for standard, syn_list in self._raw.get("synonyms", {}).items():
            for syn in syn_list:
                self._synonym_index[syn.lower()] = standard.lower()

        # 枚举值索引：dim_key → {alias_lower → canonical_value}
        for dim_key, dim_cfg in self._raw.get("dimensions", {}).items():
            alias_map = {}
            for canonical, aliases in dim_cfg.get("enum_values", {}).items():
                alias_map[canonical.lower()] = canonical
                for alias in aliases:
                    alias_map[alias.lower()] = canonical
            self._enum_index[dim_key] = alias_map

    def match_metrics(self, keyword: str) -> list[tuple[str, str]]:
        """
        匹配指标关键词 → [(api_id, metric_id)]

        查找顺序：
        1. 直接匹配指标名/别名
        2. 通过同义词展开后匹配
        """
        keyword_lower = keyword.lower()
        # 直接匹配
        if keyword_lower in self._metric_index:
            return self._metric_index[keyword_lower]
        # 同义词展开
        if keyword_lower in self._synonym_index:
            standard = self._synonym_index[keyword_lower]
            if standard in self._metric_index:
                return self._metric_index[standard]
        return []

    def get_api(self, api_id: str) -> dict | None:
        for api in self._raw["apis"]:
            if api["id"] == api_id:
                return api
        return None

    def get_dimensions(self) -> dict:
        return self._raw.get("dimensions", {})

    def get_disambiguation(self, keyword: str) -> dict | None:
        return self._raw.get("disambiguation", {}).get(keyword)

    def get_hot_questions(self) -> list[str]:
        return self._raw.get("hot_questions", [])

    def get_metric_info(self, api_id: str, metric_id: str) -> dict | None:
        """获取指标详情（名称、单位、类型等）"""
        api = self.get_api(api_id)
        if api:
            for m in api["output_metrics"]:
                if m["id"] == metric_id:
                    return m
        return None
```

**关键改动**：
- 加载时**验证元数据结构**，不合法则拒绝启动
- **预构建三个索引**（指标索引、同义词索引、枚举索引），查询 O(1)
- 匹配指标时**自动走同义词展开**，调用方无需关心

#### 3.3.3 计算执行引擎（CalcEngine）

```python
class CalcEngine:
    """
    受约束的指标计算引擎。

    只执行枚举化的计算类型，不做 eval，不执行任意表达式。
    每种计算类型对应确定性的 Python 函数。
    """

    CALC_HANDLERS = {
        "subtract": "_calc_subtract",
        "ratio": "_calc_ratio",
        "compare": "_calc_compare",
        "filter": "_calc_filter",
        "rank_then_lookup": "_calc_rank_then_lookup",
        "aggregate": "_calc_aggregate",
    }

    def execute(self, plan: OrchestrationPlan, step_results: dict[str, dict]) -> CalcResult:
        """
        执行编排计划中的计算节点。

        Args:
            plan: 已校验的编排计划
            step_results: 每个执行节点的API返回结果 {"n1": {...}, "n2": {...}}

        Returns:
            CalcResult: 计算结果 + 计算过程说明
        """
        calc_type = plan.calculation.type
        if calc_type not in self.CALC_HANDLERS:
            raise UnsupportedCalcError(f"不支持的计算类型: {calc_type}")

        handler = getattr(self, self.CALC_HANDLERS[calc_type])
        return handler(plan, step_results)

    def _calc_subtract(self, plan: OrchestrationPlan, results: dict) -> CalcResult:
        """两个指标相减（同比增幅、差值等）"""
        op = plan.calculation
        val_a = self._extract_value(results, op.operands[0])
        val_b = self._extract_value(results, op.operands[1])
        result_value = val_a - val_b

        return CalcResult(
            value=result_value,
            label=op.result_label,
            unit=op.result_unit,
            formula=f"{val_a} - {val_b} = {result_value}",
            detail={
                "operand_a": {"ref": op.operands[0], "value": val_a},
                "operand_b": {"ref": op.operands[1], "value": val_b},
            },
        )

    def _calc_ratio(self, plan: OrchestrationPlan, results: dict) -> CalcResult:
        """除法求比例（占比、份额等）"""
        op = plan.calculation
        numerator = self._extract_value(results, op.operands[0])
        denominator = self._extract_value(results, op.operands[1])
        if denominator == 0:
            return CalcResult(value=None, label=op.result_label, unit=op.result_unit,
                              formula="分母为0，无法计算", detail={})
        result_value = round(numerator / denominator * 100, 2)
        return CalcResult(
            value=result_value,
            label=op.result_label,
            unit=op.result_unit,
            formula=f"{numerator} / {denominator} × 100% = {result_value}%",
            detail={"numerator": numerator, "denominator": denominator},
        )

    def _calc_compare(self, plan: OrchestrationPlan, results: dict) -> CalcResult:
        """多值并列对比"""
        op = plan.calculation
        values = {}
        for operand in op.operands:
            values[operand] = self._extract_value(results, operand)
        return CalcResult(
            value=values,
            label=op.result_label,
            unit=op.result_unit,
            formula="对比展示",
            detail={"values": values},
        )

    def _calc_filter(self, plan: OrchestrationPlan, results: dict) -> CalcResult:
        """多条件筛选"""
        op = plan.calculation
        # op.conditions: [{"field": "q1.rate", "op": ">", "value": 80}, ...]
        all_items = self._extract_grouped_values(results, op.operands)
        filtered = []
        for item in all_items:
            if all(self._eval_condition(item, cond) for cond in op.conditions):
                filtered.append(item)
        return CalcResult(
            value=filtered,
            label=op.result_label,
            unit=op.result_unit,
            formula=f"筛选条件: {op.conditions}",
            detail={"total": len(all_items), "matched": len(filtered)},
        )

    def _extract_value(self, results: dict, ref: str) -> float:
        """
        从步骤结果中提取值。ref 格式: "q1.metric_id"
        """
        step_id, metric_id = ref.split(".", 1)
        step_data = results.get(step_id, {})
        value = step_data.get(metric_id)
        if value is None:
            raise CalcDataMissingError(f"计算数据缺失: {ref}")
        return float(value)
```

**设计要点**：
- **枚举化计算类型**，每种对应一个确定性方法
- **不做 eval**，不执行任意表达式
- `_extract_value` 用 `"q1.metric_id"` 格式引用子查询结果
- 计算过程（formula）也记录，用于前端展示

### 3.4 Layer 3: Step 执行层

#### 3.4.1 Step 统一接口

```python
class StepResult(BaseModel):
    """每一步的标准输出"""
    step: str           # 步骤标识
    title: str          # 步骤标题（展示用）
    status: str         # "success" | "need_clarification" | "error"
    data: dict          # 步骤特定的输出数据
    latency_ms: int     # 本步骤耗时

class BaseStep(ABC):
    """Step 基类 — 所有步骤实现此接口"""

    @abstractmethod
    def run(self, context: PipelineContext) -> StepResult:
        """执行本步骤"""
        ...

    @abstractmethod
    def validate_input(self, context: PipelineContext) -> list[str]:
        """校验输入是否满足本步骤的前置条件，返回错误列表"""
        ...

    def on_error(self, error: Exception, context: PipelineContext) -> StepResult:
        """错误处理钩子，子类可覆盖实现降级策略"""
        logger.error(f"step.{self.step_name}.error", error=str(error))
        return StepResult(
            step=self.step_name, title=self.step_title,
            status="error", data={"error": str(error)}, latency_ms=0,
        )
```

```python
class PipelineContext:
    """
    Pipeline 上下文 — 步骤间的数据传递通道。

    每一步从 context 读取上一步的输出，写入自己的输出。
    禁止步骤之间直接调用。
    """
    def __init__(self, session_id: str, query: str, user_context: dict | None = None):
        self.session_id = session_id
        self.original_query = query
        self.user_context = user_context or {}

        # 步骤间传递的数据
        self.rule_result: RuleResult | None = None
        self.intent: IntentOutput | None = None
        self.orchestration_plan: OrchestrationPlan | None = None
        self.api_routes: list[APIRouteResult] | None = None
        self.param_bind: ParamBindOutput | None = None
        self.api_responses: dict[str, dict] | None = None  # 多API调用结果
        self.calc_result: CalcResult | None = None
        self.final_result: ResultDisplay | None = None
        self.reason_trace: ReasonTrace = ReasonTrace()

        # 澄清状态
        self.need_clarification: bool = False
        self.clarification: ClarificationOutput | None = None

        # 步骤结果收集
        self.step_results: list[StepResult] = []
```

#### 3.4.2 Step 1: 意图解析步骤

```python
class IntentStep(BaseStep):
    """
    Step 1: 意图解析

    分层处理：
    1. 规则引擎抽取确定性信息（最高优先）
    2. LLM处理剩余文本（只做指标识别 + 模糊判断）
    3. 归一化 + 消歧
    4. 合法性校验
    """
    step_name = "intent"
    step_title = "意图解析"

    def __init__(self, rule_engine: RuleEngine, llm: LLMClient, metadata: MetadataCenter):
        self.rule_engine = rule_engine
        self.llm = llm
        self.metadata = metadata

    def validate_input(self, ctx: PipelineContext) -> list[str]:
        if not ctx.original_query or not ctx.original_query.strip():
            return ["用户查询不能为空"]
        return []

    def run(self, ctx: PipelineContext) -> StepResult:
        start = time.time()

        # === 层1: 规则抽取（绝对权威） ===
        rule_result = self.rule_engine.extract(ctx.original_query)
        ctx.rule_result = rule_result
        logger.info("step.intent.rule", params=rule_result.extracted_params,
                     remaining=rule_result.remaining_text)

        # === 层2: LLM语义理解（只看剩余文本） ===
        llm_output = self._llm_parse(rule_result.remaining_text, rule_result.extracted_params)
        logger.info("step.intent.llm", metrics=llm_output.metrics, is_vague=llm_output.is_vague)

        # === 层3: 合并 + 归一化 ===
        # 规则参数是权威的，LLM参数只补充规则未覆盖的维度
        merged_params = dict(rule_result.extracted_params)  # 规则优先
        merged_sources = dict(rule_result.sources)

        for dim_key, dim_val in llm_output.dimensions.items():
            if dim_key not in merged_params:  # 只在规则未覆盖时才采用LLM
                resolved = self.metadata.resolve_dimension_value(dim_key, dim_val)
                if resolved:
                    merged_params[dim_key] = resolved
                    merged_sources[dim_key] = ParamSource(type="llm", confidence=0.75)

        # 指标归一化
        normalized_metrics = self._normalize_metrics(llm_output.metrics)

        # === 层4: 消歧检查 ===
        disambiguation = self._check_disambiguation(normalized_metrics)
        if disambiguation:
            ctx.need_clarification = True
            ctx.clarification = disambiguation
            return self._build_result(ctx, normalized_metrics, merged_params,
                                      merged_sources, "need_clarification", start)

        # === 层5: 模糊检查 ===
        if llm_output.is_vague or not normalized_metrics:
            vague_clarification = self._build_vague_clarification(ctx.original_query)
            ctx.need_clarification = True
            ctx.clarification = vague_clarification
            return self._build_result(ctx, normalized_metrics, merged_params,
                                      merged_sources, "need_clarification", start)

        # === 写入上下文 ===
        ctx.intent = IntentOutput(
            metrics=normalized_metrics,
            params=merged_params,
            sources=merged_sources,
        )
        return self._build_result(ctx, normalized_metrics, merged_params,
                                  merged_sources, "success", start)

    def _llm_parse(self, remaining_text: str, known_params: dict) -> LLMIntentOutput:
        """
        LLM只处理规则未覆盖的部分。

        输入：remaining_text（已移除时间/BU等已识别部分的文本）
        任务：识别指标关键词 + 判断是否模糊
        """
        if not remaining_text.strip():
            # 规则已经抽取了所有信息，无需调LLM
            return LLMIntentOutput(metrics=[], dimensions={}, is_vague=False)

        system_prompt = self._build_system_prompt()
        user_prompt = f"""已知信息（规则已识别）：{json.dumps(known_params, ensure_ascii=False)}
剩余待理解的文本："{remaining_text}"

请识别文本中的指标关键词和剩余维度信息。"""

        try:
            resp = self.llm.chat(system_prompt, user_prompt, json_mode=True)
            return LLMIntentOutput(**resp.parsed_json)
        except LLMUnavailableError:
            logger.warning("step.intent.llm_unavailable, 降级为纯规则模式")
            return LLMIntentOutput(metrics=[], dimensions={}, is_vague=True)

    def _normalize_metrics(self, raw_metrics: list[str]) -> list[NormalizedMetric]:
        """将LLM返回的指标关键词归一化到标准指标ID"""
        results = []
        for keyword in raw_metrics:
            matches = self.metadata.match_metrics(keyword)
            if matches:
                api_id, metric_id = matches[0]
                info = self.metadata.get_metric_info(api_id, metric_id)
                results.append(NormalizedMetric(
                    id=metric_id, name=info["name"] if info else keyword,
                    keyword=keyword, api_id=api_id, confidence=0.9,
                ))
            else:
                results.append(NormalizedMetric(
                    id=keyword, name=keyword, keyword=keyword,
                    api_id=None, confidence=0.4,
                ))
        return results
```

**关键改动 vs 当前实现**：
- `remaining_text` 是去掉已识别部分后的文本，LLM的任务大幅简化
- 规则参数**绝对不被LLM覆盖**（`if dim_key not in merged_params`）
- LLM不可用时**降级为纯规则模式**，不崩溃
- 使用 json_mode，不再手动剥离 markdown
- 消歧和模糊是分开的两个检查

#### 3.4.3 Step 1.5: 查询编排计划

`Step 1.5` 不应再只做“复合计算识别”，而要升级为统一的 `QueryPlanStep`，负责把自然语言问题归入可执行的编排类型。

支持的计划类型：

- `single_api_package`：用户问多个指标，但它们都在同一个指标包API里，调用一次即可
- `multi_api_parallel`：多个API之间无依赖，可并行调用后合并展示
- `multi_api_sequential`：后一个API依赖前一个API的结果或参数转换
- `multi_api_merge`：多个API结果不做运算，但要按共同维度拼接展示
- `composite_calc`：多个API或多个子查询返回后，再做同比、占比、差值等计算

```python
class QueryPlanStep(BaseStep):
    """
    Step 1.5: 查询编排计划

    目标不是只识别“是否复合计算”，而是生成一个可执行、可展示、
    可审计的 OrchestrationPlan。
    """
    step_name = "query_plan"
    step_title = "查询编排计划"

    def run(self, ctx: PipelineContext) -> StepResult:
        plan = self._build_plan(ctx)
        errors = self._validate_plan(plan)

        if errors:
            return StepResult(
                step=self.step_name,
                title=self.step_title,
                status="error",
                data={"error": "查询计划校验失败", "details": errors},
            )

        ctx.orchestration_plan = plan
        ctx.reason_trace.plan_summary = {
            "plan_type": plan.plan_type,
            "node_count": len(plan.nodes),
            "merge_strategy": plan.merge_strategy,
        }

        return StepResult(
            step=self.step_name,
            title=self.step_title,
            status="success",
            data=plan.model_dump(),
        )
```

新增约束：

- 优先判断“现有单个API是否已能返回用户要的多个指标”，避免过度拆分
- 只有当一个API包内无法满足时，才进入多API编排
- 计划生成必须输出节点依赖关系，而不是只有子查询列表
- 计划中每个节点都要带 `reason`，说明为什么要调这个API

#### 3.4.4 Step 2: API路由与候选裁决

当前只按“指标命中”路由是不够的。升级后，`RouteStep` 需要输出候选API清单和淘汰原因，而不是只给最终答案。

路由评分维度：

1. 指标匹配度：指标名、别名、业务词典是否命中
2. 维度支持度：用户指定的维度是否被该API支持
3. 粒度兼容度：例如“到人”/“到团队”/“到产线”是否兼容
4. 参数适用度：用户给的参数中，哪些可用、哪些会被忽略、哪些会导致不适用
5. 包内覆盖度：同一API是否已经同时包含多个用户关心指标
6. 内置比较能力：是否一个API本身就能返回 CY/PY、同比、环比等结果

```python
class RouteStep(BaseStep):
    """
    Step 2: API路由与候选裁决

    输出：
    - winner route
    - candidate routes
    - rejected reasons
    """
    step_name = "api_route"
    step_title = "API路由决策"
```

这一层要把以下信息写入 `ReasonTrace`：

- 为什么优先选择 `API A` 而不是 `API B`
- 哪些API虽然命中指标，但因粒度不支持被淘汰
- 哪些API本身可返回今年/去年两个指标，因此不需要拆成两个节点

#### 3.4.5 Step 3: 参数绑定、执行链与Trace采集

`Step 3` 的重点不应只是“缺没缺参”，而是“参数是怎么绑定到每个API上的”。

```python
class ParamBindStep(BaseStep):
    """
    Step 3: 参数绑定 & API执行链

    职责：
    1. 为每个执行节点做参数绑定（而不是简单 copy intent.params）
    2. 校验参数是否适用于目标API
    3. 对不可适用的参数做忽略、上卷或转换
    4. 记录完整参数来源、覆盖、默认值和转换链
    5. 按计划顺序/并行策略执行API
    """
    step_name = "param_bind"
    step_title = "参数绑定 & API调用"
```

参数绑定输出需要细化为 `ParamBindingTrace`：

- `param_name`：参数名
- `source`：rule / llm / clarification / default / upstream_result
- `source_text`：命中的原文片段
- `canonical_value`：标准化后的值
- `target_api_id`
- `applicable`：是否适用于该API
- `ignored_reason`：不适用时的原因
- `transform_rule`：如果做了“人 → 团队”“团队 → 经销商”上卷，要记录规则
- `final_value`：最终传给API的值

执行链输出需要支持：

- `parallel_group`：可并行的节点
- `depends_on`：顺序依赖
- `response_selector`：从API返回中提取哪些字段
- `fallback_policy`：失败时是终止、跳过还是降级

**关键改动**：

- “参数校验”升级为“参数绑定 + 参数适用性判断”
- “复合计算”升级为“多API编排 + 合并/计算”
- Step 结果不仅给前端展示，也同时写入结构化 `ReasonTrace`

#### 3.4.6 Step 4: 结果处理

```python
class ResultStep(BaseStep):
    """
    Step 4: 结果处理与展示

    职责：
    1. 从API返回中筛选用户需要的指标
    2. 如果是编排中的计算节点 → 执行计算
    3. 生成数据解读（LLM，纯事实描述）
    4. 推荐图表类型 + 指定XY轴
    5. 获取下钻推荐
    """
    step_name = "result"
    step_title = "查询结果"

    def __init__(self, metadata: MetadataCenter, llm: LLMClient, calc_engine: CalcEngine):
        self.metadata = metadata
        self.llm = llm
        self.calc_engine = calc_engine

    def run(self, ctx: PipelineContext) -> StepResult:
        start = time.time()

        # === 编排中的计算节点执行 ===
        if ctx.orchestration_plan and ctx.orchestration_plan.plan_type == "composite_calc":
            try:
                calc_result = self.calc_engine.execute(ctx.orchestration_plan, ctx.api_responses)
                ctx.calc_result = calc_result
            except (UnsupportedCalcError, CalcDataMissingError) as e:
                logger.error("step.result.calc_failed", error=str(e))
                return StepResult(
                    step=self.step_name, title=self.step_title, status="error",
                    data={"error": f"计算失败: {e}"}, latency_ms=0,
                )

        # === 指标筛选 ===
        if ctx.calc_result:
            display_data = {
                ctx.calc_result.label: ctx.calc_result.value
            }
            display_data["_calc_detail"] = {
                "formula": ctx.calc_result.formula,
                "detail": ctx.calc_result.detail,
            }
        else:
            main_response = ctx.api_responses.get("main", {})
            route = ctx.api_routes[0] if ctx.api_routes else None
            requested_ids = route.matched_metrics if route else []
            display_data = {k: v for k, v in main_response.items() if k in requested_ids}
            if not display_data:
                display_data = main_response  # 降级：返回全部

        # === 数据解读 ===
        insight = self._generate_insight(ctx, display_data)

        # === 图表推荐 ===
        chart = self._recommend_chart(ctx, display_data)

        # === 下钻推荐 ===
        drill_downs = self._get_drill_downs(ctx)

        # === BI页面链接 ===
        bi_url = self._get_bi_url(ctx)

        ctx.final_result = ResultDisplay(
            display_data=display_data,
            insight_text=insight,
            chart_recommendation=chart,
            drill_down_options=drill_downs,
            bi_page_url=bi_url,
        )

        return StepResult(
            step=self.step_name, title=self.step_title, status="success",
            data=ctx.final_result.model_dump(),
            latency_ms=int((time.time() - start) * 1000),
        )

    def _generate_insight(self, ctx: PipelineContext, data: dict) -> str:
        """
        生成数据解读。

        约束：纯事实描述，不做预测，不给建议。
        降级：LLM不可用时返回简单的数据摘要。
        """
        try:
            prompt = f"""基于以下查询结果，生成2-3句纯事实性的数据解读。

要求：
- 只描述事实，不做预测、不给建议
- 提及具体数值
- 如果有对比（同比/环比），说明变化方向和幅度

用户问题：{ctx.original_query}
查询参数：{json.dumps(ctx.intent.params, ensure_ascii=False)}
查询结果：{json.dumps(data, ensure_ascii=False)}"""

            resp = self.llm.chat("你是一个数据解读助手，只做事实描述。", prompt)
            return resp.content
        except LLMUnavailableError:
            # 降级：简单数据摘要
            items = [f"{k}: {v}" for k, v in data.items() if not k.startswith("_")]
            return f"查询结果：{'，'.join(items)}"

    def _recommend_chart(self, ctx: PipelineContext, data: dict) -> dict:
        """
        推荐图表类型。

        基于元数据中的指标类型和数据结构做启发式推荐。
        前端使用固定样式渲染，AI只决定类型和字段映射。
        """
        # 编排中的计算结果推荐
        if ctx.calc_result:
            if ctx.orchestration_plan.calculation.type == "compare":
                return {"chart_type": "bar", "data": data}
            elif ctx.orchestration_plan.calculation.type == "ratio":
                return {"chart_type": "pie", "data": data}
            else:
                return {"chart_type": "kpi_card", "data": data}

        # 单值 → KPI卡片
        clean_data = {k: v for k, v in data.items() if not k.startswith("_")}
        if len(clean_data) == 1:
            return {
                "chart_type": "kpi_card",
                "metric": list(clean_data.keys())[0],
                "value": list(clean_data.values())[0],
            }

        # 分组数据（list values）→ 柱状图
        has_list = any(isinstance(v, list) for v in clean_data.values())
        if has_list:
            # 找到list字段作为数据源
            for k, v in clean_data.items():
                if isinstance(v, list):
                    return {
                        "chart_type": "bar",
                        "x_field": "name",  # 假设list中每项有name字段
                        "y_field": "value",
                        "data": v,
                    }

        # 多指标 → 表格
        return {
            "chart_type": "table",
            "columns": list(clean_data.keys()),
            "data": [clean_data],
        }

    def _get_drill_downs(self, ctx: PipelineContext) -> list[dict]:
        """获取下钻推荐维度"""
        if not ctx.api_routes:
            return []
        route = ctx.api_routes[0]
        api_cfg = self.metadata.get_api(route.api_id)
        if not api_cfg:
            return []
        return api_cfg.get("related_dimensions", [])

    def _get_bi_url(self, ctx: PipelineContext) -> str | None:
        """构建BI页面跳转链接（带参数筛选）"""
        if not ctx.api_routes:
            return None
        route = ctx.api_routes[0]
        api_cfg = self.metadata.get_api(route.api_id)
        if not api_cfg or "bi_page" not in api_cfg:
            return None

        bi_page = api_cfg["bi_page"]
        params = ctx.intent.params
        # 构建带筛选参数的URL
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{bi_page}?{param_str}" if param_str else bi_page
```

### 3.5 Layer 4: Pipeline 编排层

```python
class PipelineOrchestrator:
    """
    Pipeline编排器 — 控制步骤执行顺序和错误路由。

    职责：
    1. 按顺序执行各Step
    2. 在step之间传递PipelineContext
    3. 遇到 need_clarification 时中断并返回
    4. 遇到 error 时调用 step.on_error() 尝试恢复
    5. 收集所有 StepResult 组装最终 ChatResponse
    """

    def __init__(self, steps: list[BaseStep]):
        self.steps = steps

    def process(self, session_id: str, query: str,
                context: dict | None = None) -> ChatResponse:
        ctx = PipelineContext(session_id=session_id, query=query, user_context=context)

        # 处理澄清回复：合并上一轮的上下文
        if context and context.get("clarification_response"):
            self._merge_clarification_context(ctx)

        for step in self.steps:
            # 输入校验
            errors = step.validate_input(ctx)
            if errors:
                logger.error(f"pipeline.{step.step_name}.validation_failed", errors=errors)
                return self._build_error_response(ctx, step.step_name, errors)

            # 执行
            try:
                result = step.run(ctx)
            except Exception as e:
                result = step.on_error(e, ctx)

            ctx.step_results.append(result)

            # 需要澄清 → 中断Pipeline，返回给用户
            if result.status == "need_clarification":
                return self._build_clarification_response(ctx)

            # 步骤失败 → 中断Pipeline，返回错误
            if result.status == "error":
                return self._build_error_response(ctx, step.step_name, [result.data.get("error")])

        # 所有步骤完成 → 组装最终响应
        return self._build_success_response(ctx)

    def _merge_clarification_context(self, ctx: PipelineContext):
        """
        处理澄清回复：将上一轮的已识别参数和指标合并到当前上下文。

        前端发送的 context 包含：
        - clarification_response: true
        - original_query: 原始问题
        - previous_params: 上一轮已识别的参数
        - previous_metrics: 上一轮已识别的指标
        """
        prev = ctx.user_context
        if prev.get("previous_params"):
            # 预填充意图，后续 IntentStep 会在此基础上补充
            ctx.intent = IntentOutput(
                metrics=[],  # 会被IntentStep补充
                params=prev["previous_params"],
                sources={k: ParamSource(type="context", confidence=0.95)
                         for k in prev["previous_params"]},
            )

    def _build_success_response(self, ctx: PipelineContext) -> ChatResponse:
        return ChatResponse(
            session_id=ctx.session_id,
            query=ctx.original_query,
            need_clarification=False,
            steps=[ProcessStep(step=r.step, title=r.title, data=r.data)
                   for r in ctx.step_results],
            final_result=ctx.final_result,
        )

    def _build_clarification_response(self, ctx: PipelineContext) -> ChatResponse:
        return ChatResponse(
            session_id=ctx.session_id,
            query=ctx.original_query,
            need_clarification=True,
            clarification=ctx.clarification,
            steps=[ProcessStep(step=r.step, title=r.title, data=r.data)
                   for r in ctx.step_results],
        )

    def _build_error_response(self, ctx: PipelineContext, step_name: str,
                               errors: list[str]) -> ChatResponse:
        return ChatResponse(
            session_id=ctx.session_id,
            query=ctx.original_query,
            need_clarification=False,
            steps=[ProcessStep(step=r.step, title=r.title, data=r.data)
                   for r in ctx.step_results],
            final_result=ResultDisplay(
                display_data={},
                insight_text=f"查询失败（{step_name}）：{'；'.join(errors)}",
            ),
        )
```

### 3.6 依赖注入与初始化

```python
# app/di.py — 依赖注入配置

def create_pipeline(settings: Settings) -> PipelineOrchestrator:
    """创建Pipeline实例，组装所有依赖"""

    # Layer 1: 基础设施
    llm = OpenAILLMClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        max_retries=2,
        timeout=10,
    )
    http = HttpClient(base_url=settings.business_api_base_url, timeout=10)

    # Layer 2: 能力服务
    metadata = MetadataCenter(settings.metadata_path)
    rule_engine = RuleEngine(metadata)
    calc_engine = CalcEngine()
    trace_collector = TraceCollector()

    # Layer 3: 步骤实例
    steps = [
        IntentStep(rule_engine, llm, metadata),
        QueryPlanStep(llm, metadata, trace_collector),
        RouteStep(metadata),
        ParamBindStep(metadata, llm, http, trace_collector),
        ResultStep(metadata, llm, calc_engine),
    ]

    # Layer 4: 编排器
    return PipelineOrchestrator(steps)
```

---

## 四、Pydantic 数据模型定义

```python
# === 基础模型 ===

class ParamSource(BaseModel):
    """参数来源追踪"""
    type: Literal["rule_enum", "rule_time", "rule_rank", "rule_compare",
                  "llm", "llm_dynamic", "context", "default"]
    confidence: float  # 0.0 ~ 1.0

class NormalizedMetric(BaseModel):
    """归一化后的指标"""
    id: str           # 标准指标ID
    name: str         # 指标中文名
    keyword: str      # 用户原文关键词
    api_id: str | None
    confidence: float

# === 规则引擎输出 ===

class RuleResult(BaseModel):
    extracted_params: dict[str, Any]
    remaining_text: str
    sources: dict[str, ParamSource]

# === 意图解析输出 ===

class IntentOutput(BaseModel):
    metrics: list[NormalizedMetric]
    params: dict[str, Any]
    sources: dict[str, ParamSource]

class LLMIntentOutput(BaseModel):
    """LLM返回的原始解析结果"""
    metrics: list[str] = []
    dimensions: dict[str, str] = {}
    is_vague: bool = False

# === 查询编排模型 ===

class QueryNode(BaseModel):
    node_id: str
    node_type: Literal["api_call", "merge", "calc", "filter"]
    description: str
    metric: str | None = None
    api_id: str | None = None
    params: dict[str, Any] = {}
    depends_on: list[str] = []
    parallel_group: str | None = None
    response_selector: list[str] = []
    reason: str = ""

class Calculation(BaseModel):
    type: Literal["subtract", "ratio", "compare", "filter", "rank_then_lookup", "aggregate"]
    operands: list[str]
    result_label: str
    result_unit: str = ""
    conditions: list[dict] | None = None
    formula: str | None = None

class OrchestrationPlan(BaseModel):
    plan_type: Literal[
        "single_api_package",
        "multi_api_parallel",
        "multi_api_sequential",
        "multi_api_merge",
        "composite_calc",
    ]
    nodes: list[QueryNode] = []
    merge_strategy: str | None = None
    calculation: Calculation | None = None
    fallback_policy: Literal["fail_fast", "partial_return", "skip_failed"] = "fail_fast"

class CalcResult(BaseModel):
    value: Any
    label: str
    unit: str
    formula: str
    detail: dict

# === API路由输出 ===

class APICandidate(BaseModel):
    api_id: str
    api_name: str
    score: float
    matched_metrics: list[str] = []
    matched_dimensions: list[str] = []
    rejected_reasons: list[str] = []

class APIRouteResult(BaseModel):
    node_id: str | None = None
    api_id: str | None
    api_name: str
    endpoint: str
    matched_metrics: list[str]
    all_metrics: list[str] = []
    candidates: list[APICandidate] = []
    error: str | None = None

# === 参数绑定与执行输出 ===

class APICallResult(BaseModel):
    success: bool
    data: dict
    duration_ms: int
    error: str | None = None

class ParamBindingTrace(BaseModel):
    param_name: str
    source: Literal["rule", "llm", "clarification", "default", "upstream_result"]
    source_text: str | None = None
    canonical_value: Any = None
    target_api_id: str
    applicable: bool = True
    ignored_reason: str | None = None
    transform_rule: str | None = None
    final_value: Any = None
    confidence: float = 1.0

class ExecutionNodeResult(BaseModel):
    node_id: str
    api_id: str | None = None
    endpoint: str | None = None
    status: Literal["success", "failed", "skipped"]
    params: dict = {}
    duration_ms: int = 0
    response_excerpt: dict = {}
    error: str | None = None

class ParamBindOutput(BaseModel):
    bindings: list[ParamBindingTrace] = []
    execution_chain: list[ExecutionNodeResult] = []

# === 结果展示 ===

class ResultDisplay(BaseModel):
    display_data: dict
    insight_text: str = ""
    chart_recommendation: dict = {}
    drill_down_options: list[dict] = []
    bi_page_url: str | None = None
    result_lineage: dict = {}

# === 澄清 ===

class ClarificationOutput(BaseModel):
    message: str
    options: list[dict] = []  # [{"label": "植入达成率", "value": "implant_achievement_rate"}]

# === Trace ===

class ReasonTrace(BaseModel):
    intent_trace: dict = {}
    clarification_trace: list[dict] = []
    plan_summary: dict = {}
    route_candidates: list[dict] = []
    param_bindings: list[ParamBindingTrace] = []
    execution_nodes: list[ExecutionNodeResult] = []
    merge_trace: dict = {}
    calc_trace: dict = {}
    result_lineage: dict = {}

# === API响应 ===

class ProcessStep(BaseModel):
    step: str
    title: str
    data: dict

class ChatResponse(BaseModel):
    session_id: str
    query: str
    need_clarification: bool = False
    clarification: ClarificationOutput | None = None
    steps: list[ProcessStep] = []
    final_result: ResultDisplay | None = None
    reason_trace: ReasonTrace | None = None
```

---

## 五、前端设计要点

### 5.1 输入引导层（当前缺失，P0）

```
┌───────────────────────────────────────────────────────┐
│  输入框 + 联想                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 请输入问题...        [植入_]  ← 用户正在输入      │  │
│  ├─────────────────────────────────────────────────┤  │
│  │ 💡 植入达成率                                    │  │
│  │ 💡 植入金额                                      │  │
│  │ 💡 植入数量                                      │  │
│  │ 💡 植入增长率                                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  热门问题（首次对话时展示）：                           │
│  [A BU各产线植入达成] [医院覆盖率] [经销商销售排名]     │
│                                                        │
│  快捷标签：                                            │
│  [达成] [增长] [覆盖] [销售] [库存]                    │
└───────────────────────────────────────────────────────┘
```

实现要点：
- 联想数据来源：从元数据中心获取所有指标名+别名，前端缓存
- 输入时做前缀匹配，显示下拉候选
- 热门问题通过 `/api/hot-questions` 获取
- 快捷标签对应指标大类，点击后插入到输入框

### 5.2 图表渲染（当前缺失，P0）

使用 ECharts（或 AntV G2），前端固定样式渲染，AI只返回 chart_recommendation：

```typescript
// 图表类型到渲染组件的映射
const CHART_RENDERERS = {
  kpi_card: KPICardChart,    // 单值大数字展示
  bar: BarChart,             // 柱状图
  line: LineChart,           // 折线图
  pie: PieChart,             // 饼图
  table: DataTable,          // 表格
  grouped_bar: GroupedBar,   // 分组柱状图
};

function ChartRenderer({ recommendation }: { recommendation: ChartRecommendation }) {
  const Component = CHART_RENDERERS[recommendation.chart_type];
  if (!Component) return <DataTable data={recommendation.data} />;  // 降级为表格
  return <Component {...recommendation} />;
}
```

### 5.3 下钻交互（修正设计）

```
当前问题：下钻 = 发送新查询，丢失上下文
修正为：下钻 = 保持上下文，只切换维度

用户查了"A BU各产线植入达成"
  → 结果下方展示 Tab: [按产线▼] [按团队] [按医院类型] [按经销商]
  → 用户点击[按团队]
  → 前端构造请求：
    {
      "query": "[下钻] 按团队查看",
      "context": {
        "drill_down": true,
        "base_api_id": "implant_performance",
        "base_params": {"bu": "A", "year": 2026},
        "group_by": "team"
      }
    }
  → Pipeline 识别为下钻请求，跳过 Step 1/1.5/2，直接走 Step 3+4
```

### 5.4 查询编排前端展示

```
┌─────────────────────────────────────────────────┐
│ 🔍 Step 1 - 意图解析                              │
│  识别指标: 达成 / 增长 / 覆盖                        │
│  维度: A BU, 2026年, 产线                            │
├─────────────────────────────────────────────────┤
│ 🧮 Step 1.5 - 查询计划                            │
│  识别为：多API编排（并行 + 合并）                    │
│  ① 植入表现 API → 达成                              │
│  ② 增长表现 API → 增长                              │
│  ③ 覆盖表现 API → 覆盖                              │
│  ④ 合并展示：按产线对齐                              │
├─────────────────────────────────────────────────┤
│ 🔗 Step 2 - API路由                               │
│  候选1 implant-performance  得分 0.95              │
│  候选2 dealer-sales          因粒度不支持被淘汰      │
├─────────────────────────────────────────────────┤
│ 📡 Step 3 - 参数绑定 & API调用                      │
│  bu = "A"      来源: 原文规则命中                   │
│  year = 2026   来源: 时间规则命中                   │
│  person = 张三  对库存API不适用 → 上卷到 team=华东一组 │
├─────────────────────────────────────────────────┤
│ 📊 Step 4 - 结果                                   │
│  达成 87.3% | 增长 12.4% | 覆盖 76.1%              │
│  合并键: product_line                              │
│  数据来源: 3个API，均带参数与调用耗时               │
└─────────────────────────────────────────────────┘
```

### 5.5 推理过程抽屉（新增，P0）

前端不能只展示“时间线摘要”，还要有一个可展开的 `Reason Trace Drawer`：

- 默认态：给业务用户看简化版时间线
- 展开态：给实施/运营/客户方技术同学看结构化过程

抽屉中展示：

- `指标消歧`
- `API候选列表 + 淘汰原因`
- `参数绑定表`
- `执行链DAG`
- `结果血缘`

参数绑定表建议样式：

| 参数 | 来源 | 标准值 | 目标API | 是否生效 | 说明 |
|------|------|--------|----------|----------|------|
| bu | 规则抽取 | A BU | implant_performance | 是 | 原文直接命中 |
| person | 规则抽取 | 张三 | inventory_status | 否 | API不支持到人粒度 |
| team | 上游转换 | 华东一组 | inventory_status | 是 | 从person上卷得到 |

---

## 六、元数据增强

```yaml
# metadata.yaml 增强字段

apis:
  - id: implant_performance
    name: 植入表现
    endpoint: /api/implant-performance
    description: 查询各产线/团队的植入业绩表现
    granularity: ["product_line", "team", "hospital_type"]
    supports_multi_metric: true
    supports_compare_in_api: true
    merge_keys: ["product_line"]
    required_params: [bu, year]
    optional_params_config:
      - name: product_line
        label: 产线
        default: null
      - name: team
        label: 团队
        default: null
      - name: period
        label: 时间段
        default: "YTD"
    unsupported_dimensions:
      - person
    param_transform_rules:
      - from: person
        to: team
        rule: "若库存API不支持person，则按人员映射到所属team上卷"
    output_metrics:
      - id: implant_achievement_rate
        name: 植入达成率
        aliases: ["达成", "达成率", "完成率", "植入达成"]
        unit: "%"
        type: rate          # ← 新增：指标类型（rate/amount/count/growth）
        value_range: [0, 200]  # ← 新增：合理值范围（用于异常检测）
      - id: implant_amount_cy
        name: 植入金额(当年)
        aliases: ["植入金额", "今年植入"]
        unit: "万元"
        type: amount
    related_dimensions:
      - { dimension: "team", label: "按团队", api: "implant_by_team" }
      - { dimension: "hospital_type", label: "按医院类型", api: "implant_by_hospital" }
    bi_page: "https://bi.example.com/implant-analysis"  # ← 新增：BI页面链接

# 消歧规则增强
disambiguation:
  "销量":
    hint: "您说的销量是指："
    options:
      - { label: "植入数量（终端植入）", metric_id: "implant_qty", api_id: "implant_performance" }
      - { label: "经销商发货数量", metric_id: "dealer_sales_qty", api_id: "dealer_sales" }
      - { label: "销售金额", metric_id: "sales_amount", api_id: "dealer_sales" }
  "金额":
    hint: "您说的金额是指："
    options:
      - { label: "植入金额", metric_id: "implant_amount_cy", api_id: "implant_performance" }
      - { label: "经销商销售金额", metric_id: "dealer_sales_amount", api_id: "dealer_sales" }
```

---

## 七、Phase 规划

### Phase 1（Demo MVP）

| 功能 | 优先级 | 状态 | 要做的事 |
|------|--------|------|---------|
| Pipeline分层重构 | P0 | 需重写 | Step基类 + 5个Step类 + Context + Orchestrator |
| 查询编排计划 | P0 | ❌缺失 | QueryPlanStep + OrchestrationPlan，覆盖单API/多API并行/顺序/拼接/计算 |
| 规则引擎修正 | P0 | 需修正 | remaining_text、最长匹配、绝对优先 |
| LLM客户端可插拔 | P0 | 需重写 | Protocol接口、json_mode、重试、降级 |
| 推理Trace | P0 | ❌缺失 | ReasonTrace + TraceCollector，记录候选API、参数绑定、执行链、结果血缘 |
| 参数绑定引擎 | P0 | ❌缺失 | ParamBindingTrace + applicable/ignored/transform_rule |
| 前端图表渲染 | P0 | ❌缺失 | ECharts集成，5种固定图表模板 |
| 前端输入引导 | P0 | ❌缺失 | 热门问题点选 + 输入联想补全 |
| 前端澄清流程完善 | P0 | ⚠️部分 | 多轮澄清、上下文保持 |
| 推理过程抽屉 | P0 | ❌缺失 | 展示候选API、参数绑定表、执行链DAG、结果血缘 |
| 下钻维度切换 | P1 | ⚠️部分 | 保持上下文的Tab切换，非重新提问 |
| BI页面跳转 | P1 | ❌缺失 | 结果卡片加带参数跳转链接 |
| Backend DTO契约 | P1 | 需修正 | Python响应用Pydantic定义，Java用DTO接收 |
| Backend持久化 | P1 | 需修正 | Session→Redis, AuditLog→DB |
| 管理后台(API+语义字典) | P1 | ❌缺失 | CRUD界面 + DB持久化 + 热更新 |
| 结构化日志 | P0 | ❌缺失 | structlog，每步记录耗时和关键数据，并和Trace关联 |

### Phase 2

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 高级复合计算 | P0 | 在编排基础上补 rank_then_lookup、aggregate、复杂条件过滤 |
| 多指标拆分优化 | P0 | 多个独立指标 → 自动判定单API包内返回 or 多API合并展示 |
| 自定义洞察报告 | P1 | 管理层报告模板 + 规则配置 + 定时生成 |
| 数据解读增强 | P1 | 同比/环比对比、异常标注（红绿色） |
| AI生成图表 | P2 | ECharts动态配置，补充固定图表不满足的场景 |
| 会话持久化增强 | P2 | DB存储完整对话历史 |

---

## 八、当前代码与新设计的对照路线

```
当前结构:                          新设计结构:
app/                               app/
├── core/                          ├── infra/              ← Layer 1
│   ├── pipeline.py (上帝函数)     │   ├── llm_client.py   (可插拔LLM)
│   ├── intent_parser.py           │   ├── http_client.py   (带超时)
│   ├── api_router.py              │   └── logger.py        (structlog)
│   ├── rule_extractor.py          ├── services/            ← Layer 2
│   ├── metadata_center.py         │   ├── rule_engine.py   (重写: remaining_text)
│   └── result_processor.py        │   ├── metadata_center.py (增强: 索引+校验+能力约束)
├── trace/                         │   ├── trace_collector.py (新增: 推理链采集)
├── models/                        │   └── calc_engine.py   (新增: 复合计算)
│   └── schemas.py                 ├── steps/               ← Layer 3
├── api/                           │   ├── base.py          (Step接口+Context)
│   └── routes.py                  │   ├── intent_step.py   (重写: 分层处理)
└── config/                        │   ├── query_plan_step.py (新增: 多API编排计划)
    ├── metadata.yaml              │   ├── route_step.py    (重写: 候选裁决)
    └── settings.py                │   ├── param_bind_step.py (重写: 参数绑定+执行链)
                                   │   └── result_step.py   (重写: 合并/计算+图表+血缘)
                                   ├── pipeline/            ← Layer 4
                                   │   └── orchestrator.py  (编排器)
                                   ├── models/
                                   │   └── schemas.py       (完整Pydantic定义 + ReasonTrace)
                                   ├── api/
                                   │   └── routes.py
                                   ├── di.py                (依赖注入)
                                   └── config/
                                       ├── metadata.yaml    (增强)
                                       └── settings.py
```

---

## 九、关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| Pipeline架构 | Step基类 + Context传递 + Orchestrator编排 | 每步独立可测试、可重试、可替换 |
| 规则 vs LLM | 规则抽取后移除文本，LLM只看剩余部分 | 规则>99%准确率，LLM~85-90% |
| LLM集成 | Protocol接口 + json_mode + 重试 + 降级 | 不依赖特定供应商，故障时不崩溃 |
| 查询编排 | OrchestrationPlan + 节点依赖 + fallback policy | 统一覆盖单API包内、多API并行/顺序/拼接/计算 |
| 复合计算 | 枚举化计算类型 + 确定性Python执行 | 不做eval，安全可控 |
| 推理可观测 | ReasonTrace + ParamBindingTrace + Result Lineage | 让参数匹配、候选裁决、执行链和血缘全部可见 |
| 图表渲染 | 前端ECharts固定样式，AI只推荐类型 | 保证展示质量一致性 |
| 元数据管理 | Phase1:YAML+热更新, Phase2:DB+管理后台 | 先快速验证，再持久化 |
| 编排层 | Spring Boot总控 + DTO契约 | 企业级稳定性，接口不裸传Map |

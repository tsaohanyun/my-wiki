---
title: Text2KPI 参考代码节选
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [architecture, pattern, ai-agent, api]
sources: [raw/articles/text2kpi-reference-code.md]
---

# Text2KPI 参考代码节选

## 概述

从 Text2KPI 完整工程（Spring Boot + Python，约 5 MB / 数百文件）中精选 **7 段最能体现方法论的核心代码**，每段配有方法论映射讲解。这些代码是 [[text2kpi-optimization]] V2 架构的工程实现参考。 ^[raw/articles/text2kpi-reference-code.md]

## 代码片段索引

| # | 片段 | 语言 | 体现的方法论 |
|---|------|------|-------------|
| 1 | API 注册表样例 | JSON | Tool 自描述结构，元数据驱动 |
| 2 | 时间/排序/对比规则表 | Python | 规则化抽取优先，绝不交给 LLM |
| 3 | 规则抽取主流程 | Python | 最长匹配 + 移除已匹配 span |
| 4 | 意图解析 System Prompt | Python | 动态拼接元数据，静态走 cache |
| 5 | LLM 输出归一化与降级 | Python | LLM 是软依赖，生产必须有降级 |
| 6 | 流式对话端点 | Java | SSE 推流 + 审计异步落库 |
| 7 | application.yml | YAML | 双层架构配置，AI 层独立部署 |

---

## 片段一：API 注册表（自描述结构）

每个业务 API 被建模为「**自描述**」结构——名字、参数、必填、自然语言示例、风险等级。AI 不直接调它，**引擎读它做路由 / 校验 / 渲染**。

```json
{
  "version": "2.0",
  "base_url": "/api/v1",
  "domains": [
    {
      "domain_id": 1,
      "domain_name": "销售销量",
      "apis": [
        {
          "id": "SAL-001",
          "name": "查询销售总额",
          "method": "GET",
          "path": "/sales/revenue/summary",
          "params": ["period", "granularity", "region_id", "product_line", "rep_id"],
          "required_params": [],
          "nl_example": "上个月华东区总销售额是多少？同比增长了多少？",
          "operation": "read"
        },
        {
          "id": "SAL-007",
          "name": "设置销售配额",
          "method": "POST",
          "path": "/sales/quota",
          "params": ["rep_id", "team_id", "region_id", "period", "quota_amount"],
          "required_params": ["period", "quota_amount"],
          "nl_example": "给李代表设置 Q4 EP 产品线配额 500 万。",
          "operation": "write",
          "risk_level": "medium"
        }
      ]
    }
  ]
}
```

**方法论映射**：
- `nl_example` 让 LLM 看得懂这个 API 是干嘛的（few-shot 示例）
- `required_params` 决定澄清逻辑（缺哪个就问哪个）
- `operation: write / risk_level` 决定是否走 Human-in-the-Loop

---

## 片段二：规则表（时间/排序/对比）

能用正则抽的，**绝不交给 LLM**。规则抽取准确率 99%+，纯 LLM 解析 ~85%。

```python
_TIME_PATTERNS = [
    (r"今年",            lambda _m: {"year": _current_year()},            "year"),
    (r"去年",            lambda _m: {"year": _current_year() - 1},        "year"),
    (r"前年",            lambda _m: {"year": _current_year() - 2},        "year"),
    # 复合优先："2025-Q1" / "2025/Q2" / "2025Q3"
    (r"(\d{4})[-/]?[Qq]([1-4])",
        lambda m: {"year": int(m.group(1)), "period": f"Q{m.group(2)}"},  "year"),
    (r"(\d{4})\s*年",    lambda m: {"year": int(m.group(1))},             "year"),
    (r"[Qq]([1-4])",     lambda m: {"period": f"Q{m.group(1)}"},          "period"),
    (r"上半年",          lambda _m: {"period": "H1"},                     "period"),
    (r"下半年",          lambda _m: {"period": "H2"},                     "period"),
    (r"近(\d+)个?月",    lambda m: {"period": f"L{m.group(1)}M"},         "period"),
]

_RANK_PATTERNS = [
    (r"前(\d+)",         lambda m: {"limit": int(m.group(1)), "order": "desc"}, "limit"),
    (r"[Tt][Oo][Pp]\s*(\d+)",
                         lambda m: {"limit": int(m.group(1)), "order": "desc"}, "limit"),
    (r"最高",            lambda _m: {"order": "desc", "limit": 1},               "limit"),
    (r"最低",            lambda _m: {"order": "asc",  "limit": 1},               "limit"),
]

_COMPARE_PATTERNS = [
    (r"同比",            lambda _m: {"compare": "YoY"}, "compare"),
    (r"环比",            lambda _m: {"compare": "MoM"}, "compare"),
]
```

**方法论映射**：
- 复合 pattern 排在简单 pattern **前面**（`2025Q1` 必须早于 `Q1`），否则会被吞
- 这是 [[harness-engineering]] 五层约束中的 L2 — 规则化预处理

---

## 片段三：规则抽取主流程

抽完一个，就把**已匹配的 span 从原文里删掉**，LLM 只看剩下的 → 任务大幅简化。

```python
class RuleEngine:
    def extract(self, query: str) -> RuleResult:
        params = {}
        matches = []
        text = query

        # P1 枚举值（最长匹配优先）
        text, p, m = self._extract_enum_values(text)
        params.update(p); matches.extend(m)

        # P2 时间表达式
        text, p, m = self._extract_patterns(text, _TIME_PATTERNS, "rule_time")
        params.update(p); matches.extend(m)

        # P3 排序 / TopN
        text, p, m = self._extract_patterns(text, _RANK_PATTERNS, "rule_rank")
        params.update(p); matches.extend(m)

        # P4 对比类型
        text, p, m = self._extract_patterns(text, _COMPARE_PATTERNS, "rule_compare")
        params.update(p); matches.extend(m)

        return RuleResult(
            extracted_params=params,
            remaining_text=text.strip(),    # ← 喂给 LLM 的是这个，不是原文
            param_matches=matches,          # ← 给前端展示"哪个词被抽成什么"
        )
```

**方法论映射**：
- 「最长匹配优先」是踩坑后改的：早期 `A` 会从 `A BU` 里被错抽出来
- `ParamMatch` 把每一次抽取**记录在案** → 前端可以告诉用户「'今年' 解析成 year=2026」，**透明可追溯**

---

## 片段四：意图解析 System Prompt

System Prompt 极简，**业务上下文从元数据中心动态拼接**。不写废话，让 LLM 输出严格 JSON。

```python
class IntentStep(BaseStep):
    def _build_system_prompt(self) -> str:
        metadata_context = self.ctx_builder.for_intent()

        return f"""\
你是一个企业数据分析意图解析助手。

从用户文本中提取:
1. metrics: 指标关键词列表（业务中文名）
2. dimensions: 维度条件
3. is_vague: 问题是否模糊

{metadata_context}

只输出 JSON:
{{"metrics": ["..."], "dimensions": {{"...": "..."}}, "is_vague": true/false, "vague_reason": ""}}"""
```

**方法论映射**：
- 静态部分（角色 + 输出格式）走 prompt cache
- 动态部分（业务术语）从 `ContextBuilder` 拼接，业务一变只改元数据，**不改代码**
- 严格限定 JSON 输出 → 下游解析不用兜底兜得太复杂

---

## 片段五：LLM 输出归一化与降级

LLM 输出**永远不要直接相信**。归一化 + 降级是工程化必修。

```python
def _normalize_llm_payload(self, payload: dict) -> dict:
    """LLM 可能返回各种奇怪结构，全部砸成约定的 schema。"""
    metrics = payload.get("metrics", [])
    if not isinstance(metrics, list):
        metrics = [metrics] if metrics else []

    dimensions = payload.get("dimensions", {})
    if not isinstance(dimensions, dict):
        dimensions = {}

    normalized = {}
    for k, v in dimensions.items():
        if k is None or v in (None, ""):
            continue
        normalized[str(k).strip()] = v

    return {
        "metrics":      [str(x).strip() for x in metrics if str(x).strip()],
        "dimensions":   normalized,
        "is_vague":     bool(payload.get("is_vague", False)),
        "vague_reason": str(payload.get("vague_reason", "") or ""),
    }


def _deterministic_metric_match(self, remaining_text: str) -> LLMIntentOutput:
    """LLM 不可用时的降级：纯字符串匹配指标名/别名"""
    text_lower = remaining_text.strip().lower()
    matched = []
    for name in sorted(self.metadata.get_all_metric_names(), key=len, reverse=True):
        if len(name) >= 2 and name.lower() in text_lower:
            matched.append(name)
    return LLMIntentOutput(metrics=matched, dimensions={}, is_vague=not matched)
```

**方法论映射**：
- LLM 是「软依赖」，**生产系统必须有降级路径**
- 即使没有 LLM，规则 + 字符串匹配也能撑住 60%+ 的查询
- 这就是 [[harness-engineering]] 「Harness 决定 LLM 在什么约束下做」的工程含义

---

## 片段六：流式对话端点（Spring Boot）

四步链路实时推流，用户**看着 AI 工作**；审计 + 会话落库**与流分离**，客户端断了也不影响。

```java
@PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public ResponseEntity<StreamingResponseBody> chatStream(
        @Valid @RequestBody ChatRequest request,
        @RequestHeader(value = AUTH_TOKEN_HEADER, required = false) String token) {

    String sessionId = request.getSessionId();
    AccountProfile account = resolveAccount(token);
    sessionService.addMessage(account, sessionId, "user",
                              request.getQuery(), request.getContext(), null);

    Map<String, Object> context = resolveContinuationContext(
            account, sessionId, request.getQuery(), request.getContext());

    StreamingResponseBody body = outputStream -> {
        long start = System.currentTimeMillis();
        AiChatResponse result = null;
        try {
            result = aiServiceClient.streamChat(
                    sessionId, request.getQuery(), context, outputStream);
        } catch (Exception e) {
            log.warn("stream chat failed: {}", e.getMessage());
        }

        // 流结束之后：审计 + 会话落库（即使客户端断开也要做完）
        if (result != null) {
            sessionService.addMessage(account, sessionId, "assistant", ...);
            auditService.record(AuditLog.builder()
                    .sessionId(sessionId)
                    .userId(account.getUserKey())
                    .query(request.getQuery())
                    .matchedApi(result.extractMatchedApi())
                    .success(!result.isNeedClarification() && result.getFinalResult() != null)
                    .durationMs((int) (System.currentTimeMillis() - start))
                    .build());
        }
    };

    return ResponseEntity.ok()
            .cacheControl(CacheControl.noCache())
            .header("X-Accel-Buffering", "no")    // ← Nginx 不缓冲
            .header("Connection", "keep-alive")
            .contentType(MediaType.TEXT_EVENT_STREAM)
            .body(body);
}
```

**方法论映射**：
- `text/event-stream` + `X-Accel-Buffering: no` 是流式必备
- 审计**永远不能阻塞主流程**：流先返回给用户，后台再落库
- `traceId / sessionId` 全链路串联，出问题能精确回放

---

## 片段七：application.yml（双层架构配置）

编排层和 AI 能力层的对接配置——极简，但**信号量都在**。

```yaml
server:
  port: 8080

spring:
  application:
    name: text2kpi-backend
  datasource:
    primary:
      url: jdbc:mysql://localhost:3306/text2kpi
      username: ${DB_USER}
      password: ${DB_PASSWORD}

ai-service:
  base-url: http://localhost:8000
  timeout-ms: 30000
  stream-timeout-ms: 120000
  retry:
    max-attempts: 1            # ← 流式接口不重试，避免重复推送

business-gateway:
  base-url: ${BSC_GATEWAY_URL}
  registry-file: classpath:bsc-api-registry.json

audit:
  enabled: true
  async: true                  # ← 审计走异步线程池

session:
  storage: mysql
  ttl-days: 30
```

**方法论映射**：
- **AI 服务地址独立配置** → AI 能力层可独立部署、独立扩容、独立灰度
- **registry-file** 显式声明元数据来源 → 切环境就切文件，不动代码
- **audit.async = true** 是性能必备：审计不该卡用户响应

---

## 相关概念

- [[text2kpi-optimization]] — V2 分层架构设计（本文代码是其实现参考）
- [[text2kpi-prompt-and-config]] — Prompt 分层模板与工程化配置清单
- [[nl2sql-precise-mapping]] — NL2SQL 路线的精确映射方案（对比参考）
- [[harness-engineering]] — AI Agent 驾驭层方法论（本文代码的理论基础）

---
source_url: file://trans-import/03_参考代码节选.md
ingested: 2026-04-30
sha256: e5ff71271d7c5c76b6482545d7caf73776556ec8fa24705edb606c6d1da56381
---

# 参考代码 · 精选片段

> ⚠️ 这不是完整工程代码。完整 Spring Boot + Python 工程约 5 MB / 数百文件，
> 超出"课后教材"边界。这里只挑 **7 段最能体现方法论的核心代码**，配旁白讲解。
> 完整代码可在课程社群按需领取。

---

## 目录

1. [元数据中心 · API 注册表样例（JSON）](#1-元数据中心--api-注册表样例json)
2. [规则引擎 · 时间/排序/对比规则表（Python）](#2-规则引擎--时间排序对比规则表python)
3. [规则引擎 · 抽取主流程（Python）](#3-规则引擎--抽取主流程python)
4. [意图解析 · System Prompt 构造（Python）](#4-意图解析--system-prompt-构造python)
5. [意图解析 · LLM 输出归一化与降级（Python）](#5-意图解析--llm-输出归一化与降级python)
6. [Spring Boot · 流式对话端点（Java）](#6-spring-boot--流式对话端点java)
7. [Spring Boot · application.yml（双层架构配置）](#7-spring-boot--applicationyml双层架构配置)

---

## 1. 元数据中心 · API 注册表样例（JSON）

> **🎯 看点**：每个业务 API 都被建模为「**自描述**」结构 ——
> 名字、参数、必填、自然语言示例、风险等级。
> AI 不直接调它，**引擎读它做路由 / 校验 / 渲染**。

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

> 💡 **方法论映射**：
> - `nl_example` 让 LLM 看得懂这个 API 是干嘛的（few-shot 示例）
> - `required_params` 决定澄清逻辑（缺哪个就问哪个）
> - `operation: write / risk_level` 决定是否走 Human-in-the-Loop

---

## 2. 规则引擎 · 时间/排序/对比规则表（Python）

> **🎯 看点**：能用正则抽的，**绝不交给 LLM**。
> 规则抽取准确率 99%+，纯 LLM 解析 ~85%。

```python
from datetime import datetime
from typing import Callable

def _current_year() -> int:
    return datetime.now().year

# (pattern, handler, param_key_hint)
_TIME_PATTERNS: list[tuple[str, Callable, str]] = [
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

> 💡 **方法论映射**：
> - 这是「五层约束」中的 L2 — 规则化预处理
> - 复合 pattern 排在简单 pattern **前面**（`2025Q1` 必须早于 `Q1`），否则会被吞
> - `Q1` 这种短词只匹配独立位置，避免吃掉 `Q12` 的前缀（实际代码里有词边界处理）

---

## 3. 规则引擎 · 抽取主流程（Python）

> **🎯 看点**：抽完一个，就把**已匹配的 span 从原文里删掉**，
> LLM 只看剩下的 → 任务大幅简化。

```python
class RuleEngine:
    def extract(self, query: str) -> RuleResult:
        params: dict[str, Any] = {}
        matches: list[ParamMatch] = []
        text = query

        # P1  枚举值（最长匹配优先，从元数据中心读）
        text, p, m = self._extract_enum_values(text)
        params.update(p); matches.extend(m)

        # P2  时间表达式
        text, p, m = self._extract_patterns(text, _TIME_PATTERNS, "rule_time")
        params.update(p); matches.extend(m)

        # P3  排序 / TopN
        text, p, m = self._extract_patterns(text, _RANK_PATTERNS, "rule_rank")
        params.update(p); matches.extend(m)

        # P4  对比类型
        text, p, m = self._extract_patterns(text, _COMPARE_PATTERNS, "rule_compare")
        params.update(p); matches.extend(m)

        return RuleResult(
            extracted_params=params,
            remaining_text=text.strip(),    # ← 喂给 LLM 的是这个，不是原文
            param_matches=matches,          # ← 给前端展示"哪个词被抽成什么"
        )

    def _extract_enum_values(self, text):
        """维度枚举值：长串优先，避免 'A' 偷走 'A BU'"""
        candidates = []
        for dim_key, cfg in self.metadata.get_dimensions().items():
            for canonical, aliases in cfg.get("enum_values", {}).items():
                for alias in [canonical] + aliases:
                    candidates.append((alias, dim_key, canonical))

        candidates.sort(key=lambda c: len(c[0]), reverse=True)  # 长串优先

        params, matches = {}, []
        for alias, dim_key, canonical in candidates:
            if dim_key in params:
                continue
            start, end = self._find_alias_span(text, alias)
            if start >= 0:
                params[dim_key] = canonical
                matches.append(ParamMatch(
                    key=dim_key, value=canonical,
                    source=ParamSource(type="rule_enum", confidence=0.99,
                                       raw_input=text[start:end],
                                       matched_to=canonical)
                ))
                text = text[:start] + text[end:]   # ← 移除已匹配 span
        return text, params, matches
```

> 💡 **方法论映射**：
> - 「最长匹配优先」是踩坑后改的：早期 `A` 会从 `A BU` 里被错抽出来
> - `ParamMatch` 把每一次抽取**记录在案** → 前端可以告诉用户「'今年' 解析成 year=2026」，**透明可追溯**

---

## 4. 意图解析 · System Prompt 构造（Python）

> **🎯 看点**：System Prompt 极简，**业务上下文从元数据中心动态拼接**。
> 不写废话，让 LLM 输出严格 JSON。

```python
class IntentStep(BaseStep):
    def _build_system_prompt(self) -> str:
        # 从元数据中心动态拼上下文（指标列表、维度枚举、消歧词典）
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

> 💡 **方法论映射**：
> - 静态部分（角色 + 输出格式）走 prompt cache
> - 动态部分（业务术语）从 `ContextBuilder` 拼接，业务一变只改元数据，**不改代码**
> - 严格限定 JSON 输出 → 下游解析不用兜底兜得太复杂

---

## 5. 意图解析 · LLM 输出归一化与降级（Python）

> **🎯 看点**：LLM 输出**永远不要直接相信**。归一化 + 降级是工程化必修。

```python
def _normalize_llm_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
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
    matched: list[str] = []
    # 长串优先匹配，避免短指标偷走长指标的字
    for name in sorted(self.metadata.get_all_metric_names(), key=len, reverse=True):
        if len(name) >= 2 and name.lower() in text_lower:
            matched.append(name)
    return LLMIntentOutput(metrics=matched, dimensions={}, is_vague=not matched)
```

> 💡 **方法论映射**：
> - LLM 是「软依赖」，**生产系统必须有降级路径**
> - 即使没有 LLM，规则 + 字符串匹配也能撑住 60%+ 的查询
> - 这就是「Harness 决定 LLM 在什么约束下做」的工程含义

---

## 6. Spring Boot · 流式对话端点（Java）

> **🎯 看点**：四步链路实时推流，用户**看着 AI 工作**；
> 同时审计 + 会话落库**与流分离**，客户端断了也不影响。

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
            // 调下游 Python AI 服务，边推边返
            result = aiServiceClient.streamChat(
                    sessionId, request.getQuery(), context, outputStream);
        } catch (Exception e) {
            log.warn("stream chat failed: {}", e.getMessage());
        }

        // 流结束之后的工作：审计 + 会话落库
        // 即使客户端断开了也要做完
        if (result != null) {
            sessionService.addMessage(account, sessionId, "assistant",
                                      summarizeAssistantContent(result),
                                      context, result);

            auditService.record(AuditLog.builder()
                    .sessionId(sessionId)
                    .userId(account.getUserKey())
                    .query(request.getQuery())
                    .matchedApi(result.extractMatchedApi())
                    .requestParams(context)
                    .success(!result.isNeedClarification()
                             && result.getFinalResult() != null)
                    .durationMs((int) (System.currentTimeMillis() - start))
                    .timestamp(LocalDateTime.now())
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

> 💡 **方法论映射**：
> - `text/event-stream` + `X-Accel-Buffering: no` 是流式必备
> - 审计**永远不能阻塞主流程**：流先返回给用户，后台再落库
> - `traceId / sessionId` 全链路串联，出问题能精确回放

---

## 7. Spring Boot · application.yml（双层架构配置）

> **🎯 看点**：编排层和 AI 能力层的对接配置 —— 极简，但**信号量都在**。

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

# 下游 Python AI 能力层
ai-service:
  base-url: http://localhost:8000
  timeout-ms: 30000
  stream-timeout-ms: 120000
  retry:
    max-attempts: 1            # ← 流式接口不重试，避免重复推送

# 业务网关（被 AI 路由后调用的真实 API）
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

> 💡 **方法论映射**：
> - **AI 服务地址独立配置** → AI 能力层可独立部署、独立扩容、独立灰度
> - **registry-file** 显式声明元数据来源 → 切环境就切文件，不动代码
> - **audit.async = true** 是性能必备：审计不该卡用户响应

---

## 完整代码索取

如需完整工程代码（含测试 / 数据库 schema / 全部 Step 实现 / 前端等），
请在课程社群发**「全量代码」**口令，会发腾讯文档 / 网盘链接。

> ⚠️ 完整代码 ~5 MB，仅作教学参考，**不可直接用于生产环境**。
> 真实落地必须按你公司的鉴权 / 限流 / 数据合规要求进行二次加固。

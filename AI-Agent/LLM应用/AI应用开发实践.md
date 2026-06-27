---
title: AI应用开发实践
aliases:
  - AI应用开发
  - LLM工程化
  - AI部署
tags:
  - AI应用
  - LLM
  - API
  - 部署
  - 安全
type: guide
status: active
created: 2026-06-27
updated: 2026-06-27
source: internal
difficulty: intermediate
project: AI-Agent
---

# AI应用开发实践

> 从原型到生产的AI应用开发全链路实践，涵盖API集成、成本优化、安全防护和部署策略。

## 1. API集成

### 1.1 统一LLM客户端

```python
from typing import Optional, Dict, List
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    provider: str  # openai, anthropic, local
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_retries: int = 3
    timeout: int = 60
    temperature: float = 0.7
    max_tokens: int = 2048

class UnifiedLLMClient:
    """统一的LLM客户端，支持多provider切换"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = self._create_client()

    def _create_client(self):
        if self.config.provider == "openai":
            from openai import OpenAI
            return OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
        elif self.config.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=self.config.api_key)
        else:
            raise ValueError(f"不支持的provider: {self.config.provider}")

    def chat(self, messages: List[Dict], **kwargs) -> str:
        """统一的聊天接口"""
        for attempt in range(self.config.max_retries):
            try:
                if self.config.provider == "openai":
                    response = self._client.chat.completions.create(
                        model=self.config.model,
                        messages=messages,
                        temperature=kwargs.get("temperature", self.config.temperature),
                        max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    )
                    return response.choices[0].message.content

                elif self.config.provider == "anthropic":
                    # 将messages格式转换为Anthropic格式
                    system = ""
                    claude_messages = []
                    for msg in messages:
                        if msg["role"] == "system":
                            system = msg["content"]
                        else:
                            claude_messages.append(msg)

                    response = self._client.messages.create(
                        model=self.config.model,
                        system=system,
                        messages=claude_messages,
                        max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                        temperature=kwargs.get("temperature", self.config.temperature),
                    )
                    return response.content[0].text

            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt+1}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise
```

### 1.2 流式响应

```python
from typing import AsyncIterator, Iterator

class StreamingLLMClient(UnifiedLLMClient):
    """支持流式输出的客户端"""

    def chat_stream(self, messages: List[Dict], **kwargs) -> Iterator[str]:
        """流式输出"""
        if self.config.provider == "openai":
            stream = self._client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        elif self.config.provider == "anthropic":
            system = ""
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    claude_messages.append(msg)

            with self._client.messages.stream(
                model=self.config.model,
                system=system,
                messages=claude_messages,
                max_tokens=kwargs.get("max_tokens", 2048),
            ) as stream:
                for text in stream.text_stream:
                    yield text

    async def chat_stream_async(self, messages: List[Dict], **kwargs) -> AsyncIterator[str]:
        """异步流式输出（用于FastAPI等）"""
        from openai import AsyncOpenAI
        async_client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
        stream = await async_client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 1.3 FastAPI集成

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

app = FastAPI(title="AI应用API")

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: str = "gpt-4"
    stream: bool = False

class ChatResponse(BaseModel):
    reply: str
    usage: Dict
    conversation_id: str

# 初始化客户端
client = StreamingLLMClient(LLMConfig(
    provider="openai",
    model="gpt-4",
    max_retries=3
))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """非流式聊天接口"""
    messages = [{"role": "user", "content": request.message}]

    try:
        reply = client.chat(messages)
        return ChatResponse(
            reply=reply,
            usage={"prompt_tokens": 0, "completion_tokens": 0},
            conversation_id=request.conversation_id or "new"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    messages = [{"role": "user", "content": request.message}]

    async def generate():
        async for chunk in client.chat_stream_async(messages):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## 2. 成本优化

### 2.1 Token计数与成本追踪

```python
import tiktoken
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CostRecord:
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    request_id: str
    metadata: Dict

class CostTracker:
    """API成本追踪器"""

    # 定价（每1000 token，美元）
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }

    def __init__(self):
        self.records: List[CostRecord] = []
        self.encoders = {}

    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """计算token数"""
        if model not in self.encoders:
            try:
                self.encoders[model] = tiktoken.encoding_for_model(model)
            except:
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        return len(self.encoders[model].encode(text))

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """计算费用"""
        pricing = self.PRICING.get(model, self.PRICING["gpt-4"])
        input_cost = prompt_tokens / 1000 * pricing["input"]
        output_cost = completion_tokens / 1000 * pricing["output"]
        return input_cost + output_cost

    def record(self, model: str, prompt_tokens: int, completion_tokens: int, **metadata):
        """记录一次API调用"""
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        self.records.append(CostRecord(
            timestamp=datetime.now(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            request_id=metadata.get("request_id", ""),
            metadata=metadata
        ))
        return cost

    def get_summary(self, period: str = "day") -> Dict:
        """获取成本汇总"""
        from collections import defaultdict
        summary = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0})

        for record in self.records:
            key = record.model
            summary[key]["calls"] += 1
            summary[key]["tokens"] += record.prompt_tokens + record.completion_tokens
            summary[key]["cost"] += record.cost_usd

        total_cost = sum(v["cost"] for v in summary.values())
        return {"by_model": dict(summary), "total_cost_usd": total_cost}
```

### 2.2 智能缓存

```python
import hashlib
import json
from functools import lru_cache

class LLMCache:
    """LLM响应缓存"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.ttl = ttl_seconds

    def _make_key(self, messages: List[Dict], model: str, **kwargs) -> str:
        """生成缓存键"""
        content = json.dumps({
            "messages": messages,
            "model": model,
            **kwargs
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, messages: List[Dict], model: str, **kwargs) -> Optional[str]:
        """查询缓存"""
        key = self._make_key(messages, model, **kwargs)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["response"]
            else:
                del self.cache[key]
        return None

    def set(self, messages: List[Dict], model: str, response: str, **kwargs):
        """设置缓存"""
        key = self._make_key(messages, model, **kwargs)
        self.cache[key] = {
            "response": response,
            "timestamp": time.time()
        }

    def clear(self):
        self.cache.clear()

# 带缓存的客户端
class CachedLLMClient(UnifiedLLMClient):
    def __init__(self, config: LLMConfig, cache_ttl: int = 3600):
        super().__init__(config)
        self.cache = LLMCache(ttl_seconds=cache_ttl)
        self.cache_hits = 0
        self.cache_misses = 0

    def chat(self, messages: List[Dict], **kwargs) -> str:
        # 检查缓存
        cached = self.cache.get(messages, self.config.model, **kwargs)
        if cached:
            self.cache_hits += 1
            return cached

        self.cache_misses += 1
        response = super().chat(messages, **kwargs)
        self.cache.set(messages, self.config.model, response, **kwargs)
        return response

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0
```

### 2.3 模型路由（成本优化）

```python
class ModelRouter:
    """智能模型路由：根据任务复杂度选择模型"""

    def __init__(self):
        self.models = {
            "simple": LLMConfig(provider="openai", model="gpt-3.5-turbo"),
            "medium": LLMConfig(provider="openai", model="gpt-4-turbo"),
            "complex": LLMConfig(provider="openai", model="gpt-4"),
        }
        self.clients = {k: UnifiedLLMClient(v) for k, v in self.models.items()}

    def classify_complexity(self, query: str) -> str:
        """判断任务复杂度"""
        # 简单规则（生产中可用小模型分类）
        if len(query) < 50 and "?" in query:
            return "simple"
        elif any(kw in query for kw in ["分析", "比较", "总结", "写一篇"]):
            return "complex"
        return "medium"

    def chat(self, messages: List[Dict], **kwargs) -> str:
        query = messages[-1]["content"] if messages else ""
        complexity = self.classify_complexity(query)
        logger.info(f"路由到 {complexity} 模型")
        return self.clients[complexity].chat(messages, **kwargs)
```

## 3. 安全考虑

### 3.1 输入验证与过滤

```python
import re
from typing import Tuple

class SecurityFilter:
    """输入安全过滤器"""

    # 敏感信息模式
    PII_PATTERNS = {
        "phone": r'1[3-9]\d{9}',
        "id_card": r'\d{17}[\dXx]',
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "bank_card": r'\d{16,19}',
    }

    # 注入模式
    INJECTION_PATTERNS = [
        r'(?i)ignore\s+(all\s+)?previous\s+instructions',
        r'(?i)忽略.{0,10}(之前的|上面的|所有).{0,10}(指令|规则|提示)',
        r'(?i)you\s+are\s+now\s+',
        r'(?i)你现在是',
        r'(?i)system\s*:\s*you',
        r'(?i)new\s+instructions',
    ]

    @classmethod
    def check_pii(cls, text: str) -> Tuple[bool, List[str]]:
        """检查PII（个人身份信息）"""
        found = []
        for pii_type, pattern in cls.PII_PATTERNS.items():
            if re.search(pattern, text):
                found.append(pii_type)
        return len(found) > 0, found

    @classmethod
    def redact_pii(cls, text: str) -> str:
        """脱敏处理"""
        result = text
        for pii_type, pattern in cls.PII_PATTERNS.items():
            result = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', result)
        return result

    @classmethod
    def check_injection(cls, text: str) -> bool:
        """检测提示注入"""
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text):
                return True
        return False

    @classmethod
    def sanitize(cls, user_input: str) -> Tuple[str, Dict]:
        """综合安全检查"""
        report = {"safe": True, "warnings": []}

        # 注入检测
        if cls.check_injection(user_input):
            report["safe"] = False
            report["warnings"].append("检测到潜在的提示注入")
            return "[输入被安全过滤器拦截]", report

        # PII检测与脱敏
        has_pii, pii_types = cls.check_pii(user_input)
        if has_pii:
            report["warnings"].append(f"检测到敏感信息: {pii_types}")
            user_input = cls.redact_pii(user_input)

        return user_input, report
```

### 3.2 输出审核

```python
class OutputGuard:
    """输出内容审核"""

    def __init__(self, client: UnifiedLLMClient):
        self.client = client
        self.blocked_categories = [
            "violence", "sexual", "hate", "self-harm",
            "illegal", "malware", "fraud"
        ]

    def moderate(self, text: str) -> Dict:
        """内容审核"""
        # 使用OpenAI Moderation API
        from openai import OpenAI
        openai_client = OpenAI()
        response = openai_client.moderations.create(input=text)
        result = response.results[0]

        return {
            "flagged": result.flagged,
            "categories": {
                k: v for k, v in result.categories.model_dump().items() if v
            },
            "safe": not result.flagged
        }

    def check_hallucination(self, answer: str, context: str) -> Dict:
        """幻觉检测"""
        response = self.client.chat([{
            "role": "user",
            "content": f"""请判断以下回答是否基于提供的上下文。检查是否有编造的信息。

上下文：{context}

回答：{answer}

返回JSON：
{{"grounded": true/false, "hallucinated_claims": ["声明1"], "confidence": 0-1}}"""
        }], temperature=0)

        try:
            return json.loads(response)
        except:
            return {"grounded": True, "hallucinated_claims": [], "confidence": 0.5}
```

### 3.3 速率限制

```python
from collections import defaultdict
import asyncio

class RateLimiter:
    """速率限制器"""

    def __init__(self, requests_per_minute: int = 60, tokens_per_minute: int = 100000):
        self.rpm_limit = requests_per_minute
        self.tpm_limit = tokens_per_minute
        self.request_times: List[float] = []
        self.token_usage: List[Tuple[float, int]] = []

    def check(self, estimated_tokens: int = 1000) -> Tuple[bool, str]:
        """检查是否超出限制"""
        now = time.time()
        window = 60  # 1分钟窗口

        # 清理过期记录
        self.request_times = [t for t in self.request_times if now - t < window]
        self.token_usage = [(t, tk) for t, tk in self.token_usage if now - t < window]

        # RPM检查
        if len(self.request_times) >= self.rpm_limit:
            wait_time = self.request_times[0] + window - now
            return False, f"请求频率超限，请等待 {wait_time:.1f} 秒"

        # TPM检查
        total_tokens = sum(tk for _, tk in self.token_usage)
        if total_tokens + estimated_tokens > self.tpm_limit:
            return False, f"Token用量超限"

        return True, "OK"

    def record(self, tokens_used: int):
        """记录一次请求"""
        now = time.time()
        self.request_times.append(now)
        self.token_usage.append((now, tokens_used))
```

## 4. 部署策略

### 4.1 Docker部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY . .

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV MODEL_NAME=gpt-4

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  ai-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@db:5432/aidb
    depends_on:
      - redis
      - db
    deploy:
      resources:
        limits:
          memory: 4G

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: aidb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### 4.2 监控与告警

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Prometheus指标
REQUEST_COUNT = Counter('llm_requests_total', 'Total LLM requests', ['model', 'status'])
REQUEST_LATENCY = Histogram('llm_request_duration_seconds', 'Request duration', ['model'])
TOKEN_USAGE = Counter('llm_tokens_total', 'Total tokens used', ['model', 'type'])
ACTIVE_REQUESTS = Gauge('llm_active_requests', 'Currently active requests')
COST_TOTAL = Counter('llm_cost_usd_total', 'Total cost in USD', ['model'])

class MetricsMiddleware:
    """Prometheus监控中间件"""

    def __init__(self, client: UnifiedLLMClient):
        self.client = client

    def chat_with_metrics(self, messages: List[Dict], **kwargs) -> str:
        model = self.client.config.model
        ACTIVE_REQUESTS.inc()

        start_time = time.time()
        try:
            response = self.client.chat(messages, **kwargs)
            REQUEST_COUNT.labels(model=model, status="success").inc()
            return response
        except Exception as e:
            REQUEST_COUNT.labels(model=model, status="error").inc()
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(model=model).observe(duration)
            ACTIVE_REQUESTS.dec()
```

## 5. 最佳实践总结

| 类别 | 实践 | 说明 |
|------|------|------|
| **API集成** | 统一客户端 | 封装多provider，便于切换 |
| | 流式输出 | 提升用户体验 |
| | 重试机制 | 指数退避，处理临时故障 |
| **成本优化** | 智能缓存 | 相同请求返回缓存结果 |
| | 模型路由 | 简单任务用小模型 |
| | Token追踪 | 实时监控成本 |
| | 压缩提示 | 减少不必要的token消耗 |
| **安全** | 输入过滤 | 检测注入和PII |
| | 输出审核 | 内容安全检查 |
| | 速率限制 | 防止滥用 |
| | 幻觉检测 | 确保输出可靠性 |
| **部署** | 容器化 | Docker + Compose |
| | 监控告警 | Prometheus + Grafana |
| | 日志记录 | 结构化日志，便于排查 |
| | 灰度发布 | 新版本先小流量验证 |

## 6. 相关页面

- [[Prompt Engineering指南]] - API调用中的提示词管理
- [[RAG系统设计]] - AI应用的知识检索层
- [[LLM微调指南]] - 自定义模型的部署
- [[Agent架构模式]] - Agent系统的应用集成

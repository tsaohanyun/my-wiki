---
title: LangChain开发指南
aliases:
  - LangChain Guide
  - LangChain教程
  - LLM应用开发
  - LangServe
tags:
  - AI
  - ML
  - LLM
  - LangChain
  - Agent
  - RAG
type: wiki
status: published
created: 2026-06-28
updated: 2026-06-28
source: "LangChain Documentation (https://python.langchain.com)"
difficulty: advanced
project: AI-Agent
---

# LangChain 开发指南

> LangChain 是构建 LLM（大语言模型）应用最流行的框架，提供了从 **Prompt 编排**、**记忆管理**、**工具调用** 到 **Agent 自主推理** 的全栈能力。本文涵盖 LangChain 的核心组件：Chains、Agents、Memory、Tools、Callbacks 及 LangServe 部署。

---

## 1. 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    LangChain 生态                        │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ LangChain│  │LangGraph │  │LangSmith │             │
│  │ (核心框架)│  │(Agent图) │  │(监控调试)│             │
│  └────┬─────┘  └────┬─────┘  └──────────┘             │
│       │              │                                  │
│  ┌────┴──────────────┴────┐  ┌──────────┐              │
│  │  LangServe (API部署)   │  │LangChain │              │
│  │  FastAPI + Pydantic    │  │ Expression│              │
│  └─────────────────────────┘  │ (LCEL)   │              │
│                               └──────────┘              │
└─────────────────────────────────────────────────────────┘

核心抽象：
  Prompt → LLM/ChatModel → OutputParser → [Chain]
  Memory + Tools + Agent Executor
```

---

## 2. LCEL（LangChain Expression Language）

LCEL 是 LangChain 的声明式编排语法，所有组件都是 **Runnable**。

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# 基本 Chain
prompt = ChatPromptTemplate.from_template(
    "你是一个{role}专家，请解释{topic}。"
)
model = ChatOpenAI(model="gpt-4", temperature=0.7)
parser = StrOutputParser()

chain = prompt | model | parser

result = chain.invoke({"role": "机器学习", "topic": "Transformer"})
print(result)

# 流式输出
for chunk in chain.stream({"role": "数据科学", "topic": "RAG"}):
    print(chunk, end="", flush=True)

# 批量处理
results = chain.batch([
    {"role": "Python", "topic": "异步编程"},
    {"role": "数据库", "topic": "向量检索"},
    {"role": "安全", "topic": "RLHF"},
])

# 异步调用
import asyncio
async def main():
    result = await chain.ainvoke({"role": "AI", "topic": "Agent"})
    print(result)
asyncio.run(main())

# 并行 Runnable
parallel_chain = RunnableParallel(
    original=RunnablePassthrough(),
    explanation=chain,
)
result = parallel_chain.invoke({"role": "ML", "topic": "Attention"})
```

---

## 3. Chains（链）

### 3.1 LLM Chain

```python
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "Translate the following {source_lang} text to {target_lang}:\n\n{text}\n\nTranslation:"
)

llm = ChatOpenAI(model="gpt-4", temperature=0.3)
chain = prompt | llm | StrOutputParser()

translation = chain.invoke({
    "source_lang": "English",
    "target_lang": "Chinese",
    "text": "The Transformer architecture revolutionized NLP.",
})
```

### 3.2 顺序链（Sequential Chain）

```python
from langchain.chains import SequentialChain

# Step 1: 提取关键信息
extract_prompt = ChatPromptTemplate.from_template(
    "从以下文本中提取3个关键技术概念：\n{text}\n\n概念："
)
extract_chain = extract_prompt | model | StrOutputParser()

# Step 2: 为每个概念生成解释
explain_prompt = ChatPromptTemplate.from_template(
    "为以下每个概念写一段简短解释（每个2-3句话）：\n{concepts}\n\n解释："
)

# 组合成顺序链
full_chain = (
    {"concepts": extract_chain}
    | explain_prompt
    | model
    | StrOutputParser()
)

result = full_chain.invoke({
    "text": "BERT uses bidirectional attention. GPT uses causal attention. "
            "T5 combines both with an encoder-decoder architecture.",
})
```

### 3.3 Router Chain（路由链）

```python
from langchain.utils.math import cosine_similarity
from langchain_openai import OpenAIEmbeddings

# 根据查询内容自动路由到不同的处理链
physics_template = ChatPromptTemplate.from_template(
    "你是一个物理学家。回答：{query}"
)
math_template = ChatPromptTemplate.from_template(
    "你是一个数学家。回答：{query}"
)
history_template = ChatPromptTemplate.from_template(
    "你是一个历史学家。回答：{query}"
)

prompt_templates = [physics_template, math_template, history_template]
prompt_embeddings = embeddings.embed_documents(
    [str(p) for p in prompt_templates]
)

def route(input):
    query_embedding = embeddings.embed_query(input["query"])
    similarity = cosine_similarity([query_embedding], prompt_embeddings)[0]
    most_similar = similarity.argmax()
    return prompt_templates[most_similar] | model | StrOutputParser()

router_chain = {"query": RunnablePassthrough()} | route
```

---

## 4. Memory（记忆）

### 4.1 对话记忆

```python
from langchain.chains import ConversationChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationTokenBufferMemory,
)

# 1. 完整缓冲记忆
buffer_memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="history",
)

# 2. 窗口记忆（只保留最近 K 轮）
window_memory = ConversationBufferWindowMemory(
    k=5,  # 保留最近 5 轮对话
    return_messages=True,
)

# 3. 摘要记忆（压缩历史）
summary_memory = ConversationSummaryMemory(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    return_messages=True,
)

# 4. Token 限制记忆（按 token 数截断）
token_memory = ConversationTokenBufferMemory(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    max_token_limit=2000,
)

# 使用记忆链
conversation = ConversationChain(
    llm=ChatOpenAI(model="gpt-4", temperature=0.7),
    memory=window_memory,
    verbose=True,
)

response = conversation.predict(input="我叫张三，我喜欢Python编程。")
response = conversation.predict(input="我喜欢用什么编程语言？")
# LLM 会记得 "张三" 和 "Python"
```

### 4.2 自定义 Memory（向量检索记忆）

```python
from langchain_community.vectorstores import Chroma
from langchain.memory import VectorStoreRetrieverMemory
from langchain_openai import OpenAIEmbeddings

# 使用向量数据库存储长期记忆
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(),
    collection_name="conversation_memory",
)

memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    memory_key="history",
    input_key="input",
    return_messages=True,
)

# 保存对话
memory.save_context(
    {"input": "我上周部署了一个RAG系统。"},
    {"output": "太好了！RAG系统的性能如何？"},
)

# 检索时自动找到相关历史
chain = ConversationChain(llm=model, memory=memory, verbose=True)
response = chain.predict(input="告诉我关于我之前部署的系统。")
```

---

## 5. Tools（工具）

### 5.1 定义工具

```python
from langchain_core.tools import tool, Tool
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import requests

# 方式1: 使用 @tool 装饰器
@tool
def search_web(query: str) -> str:
    """Search the web for information.

    Args:
        query: The search query string.
    """
    # 实际实现使用搜索 API
    return f"Search results for: {query}"

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression like '2 + 3 * 4'.
    """
    try:
        result = eval(expression)  # 注意: 生产环境应使用安全的 eval
        return str(result)
    except Exception as e:
        return f"Error: {e}"

# 方式2: 使用 Pydantic Schema 定义参数
class WeatherInput(BaseModel):
    city: str = Field(description="The city to get weather for")
    units: Optional[str] = Field(default="celsius", description="Temperature units")

@tool(args_schema=WeatherInput)
def get_weather(city: str, units: str = "celsius") -> str:
    """Get the current weather for a city."""
    return f"Weather in {city}: 22°{units[0].upper()}"

# 方式3: 使用 Tool 类
def search_database(query: str) -> str:
    return f"Database results for: {query}"

db_tool = Tool(
    name="DatabaseSearch",
    func=search_database,
    description="Search the internal database for information.",
)

tools = [search_web, calculator, get_weather]
```

### 5.2 使用 LangChain 内置工具

```python
from langchain_community.tools import (
    DuckDuckGoSearchRun,
    WikipediaQueryRun,
    PythonREPLTool,
)
from langchain_community.utilities import WikipediaAPIWrapper

# Web 搜索
search = DuckDuckGoSearchRun()

# Wikipedia 搜索
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2))

# Python 代码执行
python_tool = PythonREPLTool()

builtin_tools = [search, wiki, python_tool]
```

---

## 6. Agents（智能体）

### 6.1 ReAct Agent（推理+行动）

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

# 拉取 ReAct prompt 模板
react_prompt = hub.pull("hwchase17/react")

# 创建 Agent
agent = create_react_agent(
    llm=ChatOpenAI(model="gpt-4", temperature=0),
    tools=tools,
    prompt=react_prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)

# 运行 Agent
result = agent_executor.invoke({
    "input": "What is the square root of the distance between Beijing and Shanghai?"
})
print(result["output"])
```

### 6.2 Tool Calling Agent（原生工具调用）

```python
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的AI助手。使用提供的工具来回答问题。"),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(
    llm=ChatOpenAI(model="gpt-4"),
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
)

result = agent_executor.invoke({
    "input": "What's the weather in Tokyo, and calculate 15 * 23?"
})
```

### 6.3 使用 LangGraph 构建 Agent（推荐）

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# LangGraph 是新一代 Agent 框架
model = ChatOpenAI(model="gpt-4")

# 创建带记忆的 Agent
agent = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=MemorySaver(),
)

# 带线程 ID 的多轮对话
config = {"configurable": {"thread_id": "conversation_1"}}

response = agent.invoke(
    {"messages": [("user", "My name is Alice.")]},
    config=config,
)

response = agent.invoke(
    {"messages": [("user", "What's my name?")]},
    config=config,  # 通过 thread_id 恢复上下文
)
print(response["messages"][-1].content)  # "Your name is Alice."
```

---

## 7. Callbacks（回调）

```python
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List, Optional, Union
from langchain_core.outputs import LLMResult

# 自定义 Callback Handler
class MonitoringCallbackHandler(BaseCallbackHandler):
    """监控 LLM 调用的回调"""

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        print(f"\n🚀 LLM Call Start: {serialized.get('name', 'unknown')}")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        usage = response.llm_output.get("token_usage", {})
        print(f"✅ LLM Call End - Tokens: {usage}")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """流式 token 回调"""
        print(token, end="", flush=True)

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs
    ) -> None:
        print(f"\n🔧 Tool Start: {serialized.get('name')}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        print(f"🔧 Tool End: {output[:100]}")

    def on_tool_error(self, error: Exception, **kwargs) -> None:
        print(f"❌ Tool Error: {error}")

    def on_chain_error(self, error: Exception, **kwargs) -> None:
        print(f"❌ Chain Error: {error}")


# 使用 Callback
chain = prompt | model.bind(callbacks=[MonitoringCallbackHandler()]) | parser

# 或在 invoke 时传入
result = chain.invoke(
    {"role": "ML", "topic": "Attention"},
    config={"callbacks": [MonitoringCallbackHandler()]},
)

# 使用 LangSmith 进行生产级监控
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"
# 所有链调用将自动上报到 LangSmith
```

---

## 8. LangServe（API 部署）

```python
"""
使用 LangServe 将 LangChain 应用部署为 REST API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="LangChain-powered API server",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 基本 Chain
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
chain = prompt | ChatOpenAI(model="gpt-4") | StrOutputParser()

add_routes(app, chain, path="/joke")

# 2. RAG Chain
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma(embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

rag_prompt = ChatPromptTemplate.from_template(
    "Answer based on this context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | ChatOpenAI(model="gpt-4")
    | StrOutputParser()
)

add_routes(app, rag_chain, path="/rag")

# 3. 自定义请求/响应 Schema
class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7

class ChatResponse(BaseModel):
    reply: str
    tokens_used: int

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    llm = ChatOpenAI(model="gpt-4", temperature=request.temperature)
    response = await llm.ainvoke(request.message)
    return ChatResponse(
        reply=response.content,
        tokens_used=response.usage_metadata.get("total_tokens", 0),
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 8.1 LangServe 客户端调用

```python
# 远程调用
from langserve import RemoteRunnable

remote_chain = RemoteRunnable("http://localhost:8000/joke/")

# 同步调用
result = remote_chain.invoke({"topic": "programmers"})
print(result)

# 流式调用
for chunk in remote_chain.stream({"topic": "cats"}):
    print(chunk, end="", flush=True)
```

---

## 9. 完整 RAG Agent 示例

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 准备知识库
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="wiki",
    persist_directory="./chroma_db",
)

# 2. 定义 RAG 工具
@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for relevant information.

    Args:
        query: The search query.
    """
    docs = vectorstore.similarity_search(query, k=3)
    if not docs:
        return "No relevant information found."
    results = []
    for i, doc in enumerate(docs):
        results.append(f"[{i+1}] {doc.page_content[:200]}...")
    return "\n\n".join(results)

# 3. 定义其他工具
@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate.
    """
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

# 4. 创建 Agent
tools = [search_knowledge_base, calculate]

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a knowledgeable AI assistant. "
     "Use the search_knowledge_base tool to find information, "
     "and the calculate tool for math. "
     "Always cite your sources from the knowledge base."
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(
    llm=ChatOpenAI(model="gpt-4", temperature=0),
    tools=tools,
    prompt=prompt,
)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True,
)

# 5. 运行
result = executor.invoke({
    "input": "What is the Transformer architecture, "
             "and how many parameters does it typically have?"
})
print(result["output"])
```

---

## 10. 最佳实践

1. **LCEL 优先**：新项目使用 LCEL (`|` 管道语法) 而非旧的 `LLMChain` 类。
2. **结构化输出**：使用 `with_structured_output()` 确保 LLM 输出可解析。
3. **异步优先**：生产环境使用 `ainvoke/aistream/aibatch` 异步接口。
4. **Token 管理**：使用 `ConversationTokenBufferMemory` 控制上下文长度。
5. **错误处理**：Agent 设置 `handle_parsing_errors=True` 和合理的 `max_iterations`。
6. **LangSmith 监控**：开发阶段开启 tracing，分析每步推理和工具调用。
7. **Prompt 版本管理**：使用 LangSmith Hub 管理和版本化 Prompt。
8. **安全考虑**：对用户输入做清理，防止 Prompt Injection。

```python
# 结构化输出示例
from pydantic import BaseModel, Field

class ExtractionResult(BaseModel):
    """Structured output for information extraction."""
    entities: list[str] = Field(description="Named entities found")
    sentiment: str = Field(description="Sentiment: positive/negative/neutral")
    summary: str = Field(description="One-sentence summary")

structured_llm = ChatOpenAI(model="gpt-4").with_structured_output(ExtractionResult)

result = structured_llm.invoke(
    "Apple announced record profits. Tim Cook was very optimistic."
)
print(result.entities)    # ['Apple', 'Tim Cook']
print(result.sentiment)   # 'positive'
print(result.summary)
```

---

## 11. 相关页面

- [[Transformer架构详解]] — LLM 底层架构
- [[向量数据库实战]] — LangChain 的向量存储后端
- [[大模型训练工程]] — 训练 LangChain 使用的模型
- [[AI安全与对齐]] — LLM 安全与对齐技术

---

## 12. 参考文献

1. LangChain Documentation: https://python.langchain.com/docs
2. LangGraph Documentation: https://langchain-ai.github.io/langgraph/
3. LangServe Documentation: https://github.com/langchain-ai/langserve
4. LangSmith: https://smith.langchain.com
5. Yao, S. et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models.* arXiv.

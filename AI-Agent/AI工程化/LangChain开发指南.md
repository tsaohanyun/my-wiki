---
title: LangChain开发指南
aliases:
  - LangChain
  - LLM应用开发
  - Chain开发
  - AI Agent框架
tags:
  - AI
  - LangChain
  - LLM
  - Agent
  - Chain
  - Memory
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: 实践总结
difficulty: advanced
project: AI-Agent
---

# LangChain开发指南

> LangChain是构建LLM应用最流行的开源框架，提供从**提示词管理、链式调用、记忆系统、工具集成到智能体编排**的全栈抽象。本指南基于LangChain v0.3（LCEL架构）。

## 1 核心架构

```
┌──────────────────────────────────────────────────────┐
│                   LangChain 生态                      │
│                                                      │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐             │
│  │ Models  │  │ Prompts  │  │ Output  │             │
│  │ LLM/Chat│  │ Templates│  │ Parsers │             │
│  └────┬────┘  └────┬─────┘  └────┬────┘             │
│       └───────────┼┴─────────────┘                   │
│              ┌────▼────┐                              │
│              │  Chains  │  ← LCEL (LangChain          │
│              │ (LCEL)   │     Expression Language)    │
│              └────┬────┘                              │
│       ┌──────────┼──────────────┐                    │
│  ┌────▼───┐ ┌────▼───┐ ┌───────▼──┐                 │
│  │ Memory │ │ Agents │ │  Tools   │                 │
│  │ 记忆   │ │ 智能体  │ │ 工具集   │                 │
│  └────────┘ └────────┘ └──────────┘                 │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  LangSmith (Tracing) / LangServe (Deploy)    │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## 2 LCEL（LangChain Expression Language）

LCEL是LangChain的核心范式，使用管道符 `|` 将组件组合为链。

### 2.1 基础链

```python
# pip install langchain langchain-openai
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建LLM实例
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=2048,
)

# 创建Prompt模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}，请用简洁、准确的语言回答问题。"),
    ("human", "{question}"),
])

# 创建输出解析器
parser = StrOutputParser()

# 使用LCEL管道组合
chain = prompt | llm | parser

# 调用
result = chain.invoke({
    "role": "Python工程师",
    "question": "解释Python中的GIL是什么？",
})
print(result)

# 流式输出
for chunk in chain.stream({
    "role": "技术作家",
    "question": "什么是微服务架构？",
}):
    print(chunk, end="", flush=True)
```

### 2.2 LCEL 核心接口

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# RunnablePassthrough: 直接传递输入
# RunnableLambda: 将普通函数包装为Runnable

# 1. 基本调用
result = chain.invoke({"question": "什么是RAG？"})

# 2. 批量调用
results = chain.batch([
    {"role": "工程师", "question": "什么是Docker？"},
    {"role": "工程师", "question": "什么是Kubernetes？"},
    {"role": "工程师", "question": "什么是Redis？"},
])

# 3. 异步调用
import asyncio

async def async_call():
    result = await chain.ainvoke({"question": "异步编程"})
    return result

# 4. 流式输出
async def stream_call():
    async for chunk in chain.astream({"question": "流式输出"}):
        print(chunk, end="")

# 5. 带步骤的流式输出（包含中间结果）
async def stream_events():
    async for event in chain.astream_events(
        {"question": "事件流"},
        version="v2",
    ):
        print(f"Event: {event['event']} | Name: {event['name']}")
```

### 2.3 RunnableParallel — 并行执行

```python
from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# 定义多个并行链
summary_chain = (
    ChatPromptTemplate.from_template("请用一句话总结以下内容：\n{text}")
    | llm
    | StrOutputParser()
)

translation_chain = (
    ChatPromptTemplate.from_template("请将以下内容翻译为英文：\n{text}")
    | llm
    | StrOutputParser()
)

keywords_chain = (
    ChatPromptTemplate.from_template("请提取以下内容的3个关键词，用逗号分隔：\n{text}")
    | llm
    | StrOutputParser()
)

# 并行执行
parallel_chain = RunnableParallel(
    summary=summary_chain,
    translation=translation_chain,
    keywords=keywords_chain,
)

result = parallel_chain.invoke({
    "text": "LangChain是一个用于构建LLM应用的开源框架，支持链式调用、记忆系统和工具集成。"
})
print(f"Summary: {result['summary']}")
print(f"Translation: {result['translation']}")
print(f"Keywords: {result['keywords']}")
```

## 3 Prompt Engineering

### 3.1 Few-Shot Prompting

```python
from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate

# 示例数据
examples = [
    {"input": "我今天很开心", "output": "正面 😊"},
    {"input": "这个产品太差了", "output": "负面 😠"},
    {"input": "天气还可以", "output": "中性 😐"},
    {"input": "太棒了！强烈推荐！", "output": "正面 😊"},
]

# 示例模板
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

# Few-Shot模板
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

# 最终Prompt = 系统消息 + Few-Shot示例 + 用户输入
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个情感分析助手。请对用户输入进行情感分类，并附上表情符号。"),
    few_shot_prompt,
    ("human", "{input}"),
])

# 组装链
chain = final_prompt | llm | StrOutputParser()
result = chain.invoke({"input": "这部电影真的很一般"})
print(result)  # 中性 😐
```

### 3.2 动态Few-Shot（基于语义相似度选择示例）

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector

# 创建基于语义相似度的示例选择器
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=examples,
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
    vectorstore_cls=Chroma,
    k=2,  # 选择最相似的2个示例
)

dynamic_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    example_selector=example_selector,  # 动态选择
)

# 输入"这个服务太差了"时，会自动选择负面情感的示例
chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是情感分析助手。"),
        dynamic_prompt,
        ("human", "{input}"),
    ])
    | llm
    | StrOutputParser()
)
```

### 3.3 结构化输出

```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# 定义输出Schema
class BookReview(BaseModel):
    title: str = Field(description="书名")
    rating: float = Field(description="评分1-10")
    summary: str = Field(description="一句话评价")
    pros: List[str] = Field(description="优点列表")
    cons: List[str] = Field(description="缺点列表")
    recommended: bool = Field(description="是否推荐")

# 使用结构化输出
structured_llm = llm.with_structured_output(BookReview)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的书评人。请对以下书籍进行评价。"),
    ("human", "书名：{book_name}\n作者：{author}\n简介：{description}"),
])

chain = prompt | structured_llm
result = chain.invoke({
    "book_name": "深度学习",
    "author": "Ian Goodfellow",
    "description": "深度学习领域的经典教材",
})

print(f"Title: {result.title}")
print(f"Rating: {result.rating}")
print(f"Pros: {result.pros}")
print(f"Recommended: {result.recommended}")
```

## 4 Memory（记忆系统）

### 4.1 对话记忆

```python
from langchain.chains import ConversationChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
)
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# --- 方式1: 完整对话历史 ---
memory_full = ConversationBufferMemory(
    return_messages=True,
)

# --- 方式2: 滑动窗口（只保留最近N轮） ---
memory_window = ConversationBufferWindowMemory(
    k=5,  # 保留最近5轮对话
    return_messages=True,
)

# --- 方式3: 摘要记忆（用LLM总结历史对话） ---
memory_summary = ConversationSummaryMemory(
    llm=llm,
    return_messages=True,
)

conversation = ConversationChain(
    llm=llm,
    memory=memory_window,
    verbose=True,
)

# 多轮对话
print(conversation.predict(input="我叫张三，我是一名数据科学家。"))
print(conversation.predict(input="我擅长使用Python和TensorFlow。"))
print(conversation.predict(input="你知道我叫什么名字吗？"))  # 能记住"张三"
```

### 4.2 LCEL 中的记忆管理

```python
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

# 会话历史存储
session_store: dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

# 创建带记忆的Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的AI助手。"),
    ("placeholder", "{history}"),  # 历史消息占位符
    ("human", "{input}"),
])

chain = prompt | llm

# 包装为带历史记录的链
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 使用session_id管理不同用户的对话
config = {"configurable": {"session_id": "user_001"}}

response1 = chain_with_history.invoke(
    {"input": "我叫李四，今年28岁。"},
    config=config,
)
print(response1.content)

response2 = chain_with_history.invoke(
    {"input": "我叫什么名字？"},
    config=config,
)
print(response2.content)  # "你叫李四"

# 查看历史记录
history = get_session_history("user_001")
for msg in history.messages:
    print(f"{msg.type}: {msg.content}")
```

### 4.3 Redis 持久化记忆

```python
from langchain_redis import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import redis

# Redis连接
redis_client = redis.Redis(host="localhost", port=6379, db=0)

def get_redis_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        redis_client=redis_client,
        ttl=86400,  # 历史记录过期时间：24小时
    )

chain_with_redis = RunnableWithMessageHistory(
    chain,
    get_redis_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 多用户独立会话
for user_id in ["user_001", "user_002", "user_003"]:
    config = {"configurable": {"session_id": user_id}}
    chain_with_redis.invoke(
        {"input": f"你好，我是{user_id}"},
        config=config,
    )
```

## 5 Tools（工具集成）

### 5.1 使用 @tool 装饰器

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import requests
import datetime

@tool
def get_current_weather(city: str) -> str:
    """获取指定城市的当前天气信息。

    Args:
        city: 城市名称，例如 "北京"、"上海"

    Returns:
        天气描述字符串
    """
    # 实际实现应调用天气API
    # 这里用模拟数据
    weather_data = {
        "北京": "晴天，温度25°C，湿度40%",
        "上海": "多云，温度28°C，湿度65%",
        "广州": "雷阵雨，温度30°C，湿度80%",
    }
    return weather_data.get(city, "暂无该城市的天气数据")

@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    Args:
        expression: 数学表达式，例如 "2 + 3 * 4"

    Returns:
        计算结果
    """
    try:
        result = eval(expression)  # 生产环境应使用安全的表达式解析器
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

@tool
def search_web(query: str) -> str:
    """搜索互联网获取信息。

    Args:
        query: 搜索关键词

    Returns:
        搜索结果摘要
    """
    # 实际实现应调用搜索API（如SerpAPI、Tavily等）
    return f"搜索'{query}'的结果：这里是模拟搜索结果..."

@tool
def get_current_time() -> str:
    """获取当前日期和时间。

    Returns:
        当前时间的格式化字符串
    """
    now = datetime.datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")

# 查看工具信息
print(get_current_weather.name)
print(get_current_weather.description)
print(get_current_weather.args)
```

### 5.2 使用 Pydantic 定义工具

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import requests

class SearchInput(BaseModel):
    query: str = Field(description="搜索查询词")
    num_results: int = Field(default=5, description="返回结果数量", ge=1, le=20)
    language: str = Field(default="zh", description="搜索语言")

def search_api(query: str, num_results: int = 5, language: str = "zh") -> str:
    """通过API搜索互联网"""
    # 实际调用搜索API
    return f"搜索 '{query}' 返回 {num_results} 条结果（语言: {language}）"

search_tool = StructuredTool.from_function(
    func=search_api,
    name="internet_search",
    description="在互联网上搜索信息",
    args_schema=SearchInput,
)
```

## 6 Agents（智能体）

### 6.1 Tool Calling Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# 创建LLM（需要支持tool calling）
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 工具列表
tools = [get_current_weather, calculate, search_web, get_current_time]

# 创建Agent Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能助手，可以使用以下工具来回答用户问题。

可用工具：
- get_current_weather: 获取城市天气
- calculate: 计算数学表达式
- search_web: 搜索互联网
- get_current_time: 获取当前时间

请根据用户问题选择合适的工具。如果不需要工具，直接回答即可。"""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 创建Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 创建Agent执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True,
)

# 执行
result = agent_executor.invoke({
    "input": "北京今天天气怎么样？另外帮我算一下 123 * 456 等于多少？",
})
print(result["output"])
```

### 6.2 LangGraph 高级Agent

```python
# pip install langgraph
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

# 使用LangGraph创建ReAct Agent
model = ChatOpenAI(model="gpt-4o", temperature=0)

tools = [get_current_weather, calculate, search_web, get_current_time]

# LangGraph的ReAct Agent（内置reasoning + acting循环）
agent = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=MemorySaver(),  # 持久化Agent状态
)

# 带线程ID的调用（支持多轮对话记忆）
config = {"configurable": {"thread_id": "conversation_001"}}

# 多步推理
result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "帮我查一下北京和上海的天气，然后比较哪个城市更热。"}
        ]
    },
    config=config,
)

# 打印Agent的推理过程
for msg in result["messages"]:
    msg.pretty_print()
```

### 6.3 自定义LangGraph工作流

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage
import operator

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    current_step: str
    research_results: str

# 定义节点
def research_node(state: AgentState):
    """研究节点：搜索信息"""
    query = state["messages"][-1].content
    result = search_web.invoke({"query": query})
    return {
        "research_results": result,
        "current_step": "analysis",
    }

def analysis_node(state: AgentState):
    """分析节点：LLM分析研究结果"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    analysis = llm.invoke([
        HumanMessage(content=f"基于以下研究结果进行分析：\n{state['research_results']}")
    ])
    return {
        "messages": [analysis],
        "current_step": "output",
    }

def output_node(state: AgentState):
    """输出节点：格式化最终结果"""
    return {"current_step": "done"}

# 构建工作流
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("research", research_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("output", output_node)

# 设置入口
workflow.set_entry_point("research")

# 添加边
workflow.add_edge("research", "analysis")
workflow.add_edge("analysis", "output")
workflow.add_edge("output", END)

# 编译
app = workflow.compile()

# 执行
result = app.invoke({
    "messages": [HumanMessage(content="分析2024年AI行业的发展趋势")],
    "current_step": "start",
    "research_results": "",
})
```

## 7 RAG 集成

### 7.1 文档加载与分块

```python
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    WebBaseLoader,
    DirectoryLoader,
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)

# 加载文档
loader = DirectoryLoader(
    "./docs",
    glob="**/*.md",
    loader_cls=TextLoader,
    show_progress=True,
)
documents = loader.load()
print(f"Loaded {len(documents)} documents")

# 递归字符分块（推荐）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    length_function=len,
)

chunks = text_splitter.split_documents(documents)
print(f"Split into {len(chunks)} chunks")

# Markdown标题分块（保持结构）
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ],
)
md_chunks = md_splitter.split_text(documents[0].page_content)
```

### 7.2 向量存储与检索

```python
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient

# 创建嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 连接Qdrant
client = QdrantClient(host="localhost", port=6333)

# 创建向量存储
vectorstore = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    client=client,
    collection_name="knowledge_base",
)

# 创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",  # "mmr" 或 "similarity_score_threshold"
    search_kwargs={
        "k": 5,
        # "fetch_k": 20,          # MMR: 候选数
        # "lambda_mult": 0.7,     # MMR: 多样性权重
        # "score_threshold": 0.5, # 相似度阈值
    },
)

# 检索
docs = retriever.invoke("什么是向量数据库？")
for doc in docs:
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:100]}...")
```

### 7.3 完整 RAG 链

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# RAG Prompt
rag_prompt = ChatPromptTemplate.from_template("""
你是一个专业的知识库问答助手。请根据以下参考资料回答问题。

参考资料：
{context}

问题：{question}

回答要求：
1. 仅基于参考资料回答，不要编造信息
2. 如果参考资料中没有相关信息，请说明
3. 回答要简洁、准确
""")

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# 格式化检索结果
def format_docs(docs):
    return "\n\n".join([
        f"[来源: {d.metadata.get('source', 'unknown')}]\n{d.page_content}"
        for d in docs
    ])

# 构建RAG链
rag_chain = (
    RunnableParallel(
        context=retriever | format_docs,
        question=RunnablePassthrough(),
    )
    | rag_prompt
    | llm
    | StrOutputParser()
)

# 调用
answer = rag_chain.invoke("Milvus支持哪些索引算法？")
print(answer)

# 流式输出
for chunk in rag_chain.stream("什么是HNSW索引？"):
    print(chunk, end="", flush=True)
```

### 7.4 带引用来源的RAG

```python
from langchain_core.runnables import RunnableLambda

def rag_with_sources(question: str):
    """RAG + 返回引用来源"""
    # 1. 检索
    docs = retriever.invoke(question)

    # 2. 格式化上下文
    context = format_docs(docs)

    # 3. 生成
    answer = rag_chain.invoke(question)

    # 4. 返回带来源的结果
    return {
        "answer": answer,
        "sources": [
            {
                "source": d.metadata.get("source"),
                "content": d.page_content[:200],
            }
            for d in docs
        ],
    }

result = rag_with_sources("什么是向量数据库？")
print(f"Answer: {result['answer']}")
print(f"\nSources:")
for s in result["sources"]:
    print(f"  - {s['source']}")
```

## 8 Callbacks（回调系统）

### 8.1 内置回调

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import time
import json
from typing import Any, Dict, List, Optional

class LoggingCallbackHandler(BaseCallbackHandler):
    """自定义日志回调处理器"""

    def __init__(self):
        self.token_count = 0
        self.start_time = None

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        self.start_time = time.time()
        model_name = serialized.get("name", "unknown")
        print(f"\n[LLM Start] Model: {model_name}")
        print(f"[LLM Start] Prompts: {prompts[0][:100]}...")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        elapsed = time.time() - self.start_time
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.token_count += usage.get("total_tokens", 0)
            print(f"[LLM End] Tokens: {usage}")
        print(f"[LLM End] Latency: {elapsed:.2f}s")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """流式输出时每个token触发"""
        pass  # 可用于实时UI更新

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs
    ) -> None:
        chain_name = serialized.get("name", "unknown")
        print(f"\n[Chain Start] {chain_name}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        print(f"[Chain End] Output keys: {list(outputs.keys())}")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs
    ) -> None:
        tool_name = serialized.get("name", "unknown")
        print(f"\n[Tool Start] {tool_name}: {input_str}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        print(f"[Tool End] Output: {output[:200]}")

    def on_tool_error(self, error: Exception, **kwargs) -> None:
        print(f"[Tool Error] {error}")


# 使用回调
callback = LoggingCallbackHandler()

chain = (
    ChatPromptTemplate.from_template("解释{concept}")
    | ChatOpenAI(model="gpt-4o", temperature=0, callbacks=[callback])
    | StrOutputParser()
)

result = chain.invoke(
    {"concept": "梯度下降"},
    config={"callbacks": [callback]},
)
```

### 8.2 LangSmith 追踪

```python
import os

# 设置LangSmith环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-rag-app"

# 之后所有的chain调用都会自动被追踪
# 可在LangSmith UI中查看完整的调用链路、延迟、token用量

# 带元数据的调用（便于在LangSmith中过滤）
result = chain.invoke(
    {"concept": "注意力机制"},
    config={
        "metadata": {
            "user_id": "user_001",
            "session_id": "session_abc",
            "environment": "production",
        },
        "tags": ["rag", "v2"],
    },
)
```

## 9 最佳实践

### 9.1 Prompt设计规范

| 原则 | 说明 |
|------|------|
| **角色明确** | System消息定义清晰角色和约束 |
| **Few-Shot** | 提供2-5个高质量示例 |
| **结构化** | 使用XML/Markdown标签分隔指令和内容 |
| **链式思维** | 复杂推理使用 "Let's think step by step" |
| **输出格式** | 明确指定输出格式（JSON/列表等） |

### 9.2 性能优化

```python
# 1. 缓存LLM响应（避免重复调用）
from langchain_core.globals import set_llm_cache
from langchain_community.cache import RedisCache
import redis

redis_client = redis.Redis(host="localhost", port=6379)
set_llm_cache(RedisCache(redis_=redis_client))

# 2. 并行化独立调用
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    a=chain1,
    b=chain2,
    c=chain3,
)
# 三个chain会并发执行

# 3. 批量化
results = chain.batch([{"input": f"question {i}"} for i in range(100)])
```

### 9.3 错误处理与重试

```python
from langchain_core.runnables import RunnableConfig
import asyncio

# 重试配置
config = RunnableConfig(
    max_concurrency=4,    # 最大并发数
    recursion_limit=25,   # 递归深度限制（Agent用）
    tags=["production"],
)

# 带重试的调用
@retry(max_attempts=3, delay=1.0)
async def safe_invoke(chain, input_data):
    try:
        return await chain.ainvoke(input_data, config=config)
    except Exception as e:
        print(f"Error: {e}, retrying...")
        raise

# 优雅降级
def robust_chain(question: str) -> str:
    try:
        # 尝试使用GPT-4o
        return gpt4_chain.invoke(question)
    except Exception:
        try:
            # 降级到GPT-4o-mini
            return gpt4_mini_chain.invoke(question)
        except Exception:
            return "抱歉，服务暂时不可用。"
```

### 9.4 生产部署检查清单

- [ ] **API密钥安全**：密钥存储在Secret Manager，不硬编码
- [ ] **速率限制**：实施请求速率限制和排队机制
- [ ] **超时设置**：LLM调用设置合理超时（如30s）
- [ ] **错误处理**：所有外部调用有try-catch和重试
- [ ] **缓存策略**：对幂等请求启用响应缓存
- [ ] **监控**：LangSmith/Prometheus追踪延迟和错误率
- [ ] **成本控制**：设置token用量上限和告警
- [ ] **内容安全**：输入/输出过滤（参见 [[AI安全与对齐]]）
- [ ] **A/B测试**：新旧Prompt版本并行对比
- [ ] **评估管线**：自动化评估生成质量

## 相关页面

- [[向量数据库实战]] — 向量存储与检索详解
- [[模型部署指南]] — LLM模型部署与推理优化
- [[MLOps实践指南]] — LLM应用的MLOps实践
- [[AI安全与对齐]] — Prompt注入防护与安全策略

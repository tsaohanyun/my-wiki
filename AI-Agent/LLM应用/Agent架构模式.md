---
title: Agent架构模式
aliases:
  - AI Agent
  - ReAct
  - Tool Use
  - Multi-Agent
tags:
  - agent
  - LLM
  - ReAct
  - tool-use
  - multi-agent
type: guide
status: active
created: 2026-06-27
updated: 2026-06-27
source: internal
difficulty: advanced
project: AI-Agent
---

# Agent架构模式

> AI Agent是能够感知环境、自主决策并执行行动的智能系统。LLM作为核心推理引擎，赋予Agent理解和规划能力。

## 1. ReAct模式（Reasoning + Acting）

ReAct交替进行推理（Thought）和行动（Action），是Agent最基础的架构。

### 1.1 基础ReAct实现

```python
import json
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field
from openai import OpenAI

@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    parameters: dict

    def execute(self, **kwargs) -> str:
        try:
            return str(self.function(**kwargs))
        except Exception as e:
            return f"工具执行错误: {str(e)}"


class ReActAgent:
    """ReAct模式Agent"""

    def __init__(self, model: str = "gpt-4"):
        self.client = OpenAI()
        self.model = model
        self.tools: Dict[str, Tool] = {}
        self.max_iterations = 10

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def _build_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            f"- {t.name}: {t.description}" for t in self.tools.values()
        )
        return f"""你是一个ReAct Agent。通过交替使用Thought和Action来解决问题。

可用工具：
{tool_descriptions}

请严格按照以下格式回答：

Thought: [分析当前状态，思考下一步]
Action: [工具名称]
Action Input: [工具参数，JSON格式]
Observation: [工具返回结果，由系统填入]

... (可重复多次)

Thought: [最终分析]
Final Answer: [最终回答]

注意：
- 每次只能执行一个Action
- 必须等待Observation后再继续
- 如果不需要工具，直接给出Final Answer"""

    def run(self, query: str, verbose: bool = True) -> str:
        """执行ReAct循环"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": query}
        ]

        for iteration in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                stop=["Observation:"]
            )
            assistant_msg = response.choices[0].message.content

            if verbose:
                print(f"\n--- 迭代 {iteration + 1} ---")
                print(assistant_msg)

            messages.append({"role": "assistant", "content": assistant_msg})

            # 检查是否有Final Answer
            if "Final Answer:" in assistant_msg:
                final_answer = assistant_msg.split("Final Answer:")[-1].strip()
                return final_answer

            # 解析Action
            action_result = self._execute_action(assistant_msg)
            if action_result is None:
                # 无法解析action，让模型继续
                messages.append({"role": "user", "content":
                    "请继续思考并给出Action，或给出Final Answer。"})
                continue

            # 添加Observation
            if verbose:
                print(f"Observation: {action_result}")
            messages.append({"role": "user", "content": f"Observation: {action_result}"})

        return "达到最大迭代次数，未能得出最终答案。"

    def _execute_action(self, text: str) -> Optional[str]:
        """从文本中解析并执行Action"""
        if "Action:" not in text:
            return None

        try:
            action_line = text.split("Action:")[-1].split("\n")[0].strip()
            input_line = text.split("Action Input:")[-1].split("\n")[0].strip()

            if action_line not in self.tools:
                return f"未知工具: {action_line}"

            params = json.loads(input_line) if input_line else {}
            return self.tools[action_line].execute(**params)
        except json.JSONDecodeError:
            return "参数格式错误，请使用JSON格式"
        except Exception as e:
            return f"执行错误: {str(e)}"


# 使用示例
def search_web(query: str) -> str:
    # 模拟搜索
    return f"搜索结果: 关于'{query}'的相关信息..."

def calculator(expression: str) -> str:
    try:
        result = eval(expression)  # 仅作演示，生产环境应使用安全的计算库
        return str(result)
    except:
        return "计算错误"

agent = ReActAgent()
agent.register_tool(Tool("search", "搜索互联网信息", search_web,
                          {"query": {"type": "string"}}))
agent.register_tool(Tool("calculate", "执行数学计算", calculator,
                          {"expression": {"type": "string"}}))

result = agent.run("2024年中国GDP是多少？换算成美元是多少？")
```

## 2. Function Calling（工具调用）

### 2.1 OpenAI Function Calling

```python
class FunctionCallingAgent:
    """基于Function Calling的Agent"""

    def __init__(self, model: str = "gpt-4"):
        self.client = OpenAI()
        self.model = model
        self.functions = []
        self.function_map = {}

    def register_function(self, name: str, description: str,
                          parameters: dict, func: Callable):
        """注册工具函数"""
        self.functions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        })
        self.function_map[name] = func

    def run(self, query: str, system_prompt: str = "你是一个有用的助手。") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        for _ in range(5):  # 最多5轮工具调用
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.functions if self.functions else None,
                tool_choice="auto",
            )

            msg = response.choices[0].message
            messages.append(msg)

            # 检查是否有工具调用
            if not msg.tool_calls:
                return msg.content

            # 执行所有工具调用
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                if func_name in self.function_map:
                    result = self.function_map[func_name](**func_args)
                else:
                    result = f"未知函数: {func_name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        return "超过最大工具调用轮次"


# 使用示例
def get_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的天气信息"""
    weather_data = {"北京": "晴，25°C", "上海": "多云，28°C"}
    return weather_data.get(city, f"未找到{city}的天气信息")

def get_stock_price(symbol: str) -> str:
    """获取股票价格"""
    stocks = {"AAPL": "$178.52", "GOOGL": "$141.80"}
    return stocks.get(symbol, f"未找到{symbol}的价格")

agent = FunctionCallingAgent()
agent.register_function(
    name="get_weather",
    description="获取指定城市的当前天气",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
        },
        "required": ["city"]
    },
    func=get_weather
)
agent.register_function(
    name="get_stock_price",
    description="获取股票的当前价格",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {"type": "string", "description": "股票代码，如AAPL"}
        },
        "required": ["symbol"]
    },
    func=get_stock_price
)

result = agent.run("北京今天天气怎么样？苹果公司的股价是多少？")
```

## 3. Memory系统

### 3.1 短期记忆（对话历史）

```python
class ShortTermMemory:
    """短期记忆：管理对话上下文窗口"""

    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.messages: List[Dict] = []
        self.total_tokens = 0

    def add(self, role: str, content: str):
        """添加消息"""
        tokens = self._estimate_tokens(content)
        self.messages.append({"role": role, "content": content, "tokens": tokens})
        self.total_tokens += tokens
        self._trim()

    def get_messages(self) -> List[Dict]:
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

    def _trim(self):
        """超出窗口时裁剪早期消息（保留system消息）"""
        while self.total_tokens > self.max_tokens and len(self.messages) > 1:
            if self.messages[0]["role"] == "system":
                removed = self.messages.pop(1)
            else:
                removed = self.messages.pop(0)
            self.total_tokens -= removed["tokens"]

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return len(text) // 2  # 粗略估计
```

### 3.2 长期记忆（向量存储）

```python
import time

class LongTermMemory:
    """长期记忆：基于向量检索的持久化记忆"""

    def __init__(self, embedding_service, vector_store):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def store(self, content: str, metadata: Dict = None):
        """存储记忆"""
        doc = Document(
            content=content,
            metadata={
                **(metadata or {}),
                "timestamp": time.time(),
                "type": "memory"
            }
        )
        embedding = self.embedding_service.embed([content])
        self.vector_store.add(embedding, [doc])

    def recall(self, query: str, top_k: int = 5) -> List[str]:
        """检索相关记忆"""
        query_emb = self.embedding_service.embed_query(query)
        results = self.vector_store.search(query_emb, top_k=top_k)
        return [r["document"].content for r in results]

    def store_conversation(self, messages: List[Dict]):
        """将对话摘要存入长期记忆"""
        # 生成对话摘要
        client = OpenAI()
        conversation_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"请用一句话总结以下对话的关键信息：\n{conversation_text}"
            }],
            temperature=0
        )
        summary = response.choices[0].message.content
        self.store(summary, {"type": "conversation_summary"})
```

### 3.3 工作记忆

```python
class WorkingMemory:
    """工作记忆：当前任务的暂存区"""

    def __init__(self):
        self.scratchpad: Dict[str, any] = {}  # 临时变量
        self.task_stack: List[str] = []        # 任务栈
        self.context: Dict[str, any] = {}      # 当前上下文

    def set_variable(self, key: str, value):
        self.scratchpad[key] = value

    def get_variable(self, key: str, default=None):
        return self.scratchpad.get(key, default)

    def push_task(self, task: str):
        self.task_stack.append(task)

    def pop_task(self) -> Optional[str]:
        return self.task_stack.pop() if self.task_stack else None

    def current_task(self) -> Optional[str]:
        return self.task_stack[-1] if self.task_stack else None

    def update_context(self, **kwargs):
        self.context.update(kwargs)

    def clear(self):
        self.scratchpad.clear()
        self.task_stack.clear()
        self.context.clear()
```

## 4. Multi-Agent系统

### 4.1 基础Multi-Agent框架

```python
from enum import Enum
from abc import ABC, abstractmethod

class AgentRole(Enum):
    PLANNER = "planner"        # 规划者
    EXECUTOR = "executor"      # 执行者
    CRITIC = "critic"          # 评审者
    COORDINATOR = "coordinator" # 协调者

class BaseAgent(ABC):
    def __init__(self, name: str, role: AgentRole, model: str = "gpt-4"):
        self.name = name
        self.role = role
        self.client = OpenAI()
        self.model = model

    @abstractmethod
    def system_prompt(self) -> str: ...

    def act(self, context: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": context}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Planner", AgentRole.PLANNER)

    def system_prompt(self) -> str:
        return """你是一个任务规划者。将复杂任务分解为可执行的子任务。

输出格式（JSON）：
{
    "plan": [
        {"id": 1, "task": "子任务描述", "assigned_to": "executor/critic", "dependencies": []},
        ...
    ]
}"""

    def create_plan(self, task: str) -> Dict:
        result = self.act(f"请为以下任务制定执行计划：\n{task}")
        return json.loads(result)


class ExecutorAgent(BaseAgent):
    def __init__(self, tools: List[Tool] = None):
        super().__init__("Executor", AgentRole.EXECUTOR)
        self.tools = tools or []

    def system_prompt(self) -> str:
        return "你是一个任务执行者。按照计划执行子任务，给出详细的结果。"

    def execute(self, task: str, context: str = "") -> str:
        return self.act(f"任务：{task}\n上下文：{context}")


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("Critic", AgentRole.CRITIC)

    def system_prompt(self) -> str:
        return """你是一个质量评审者。评估执行结果的质量。

输出格式（JSON）：
{
    "score": 0-10,
    "passed": true/false,
    "feedback": "改进建议",
    "issues": ["问题1", "问题2"]
}"""

    def evaluate(self, task: str, result: str) -> Dict:
        response = self.act(f"任务：{task}\n执行结果：{result}\n请评估质量。")
        return json.loads(response)


class MultiAgentSystem:
    """多Agent协作系统"""

    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.critic = CriticAgent()

    def run(self, task: str, max_retries: int = 2) -> str:
        # 1. 规划
        print("📋 规划阶段...")
        plan = self.planner.create_plan(task)
        print(f"计划: {json.dumps(plan, ensure_ascii=False, indent=2)}")

        results = {}

        # 2. 执行每个子任务
        for step in plan["plan"]:
            step_id = step["id"]
            print(f"\n⚡ 执行任务 {step_id}: {step['task']}")

            # 收集依赖的上下文
            dep_context = "\n".join(
                f"任务{dep}结果: {results.get(dep, '无')}"
                for dep in step.get("dependencies", [])
            )

            # 执行（带重试）
            for attempt in range(max_retries + 1):
                result = self.executor.execute(step["task"], dep_context)

                # 3. 评审
                evaluation = self.critic.evaluate(step["task"], result)
                print(f"评审: 分数={evaluation['score']}, 通过={evaluation['passed']}")

                if evaluation["passed"]:
                    results[step_id] = result
                    break
                elif attempt < max_retries:
                    dep_context += f"\n评审反馈: {evaluation['feedback']}"
                    print(f"重试 ({attempt + 1}/{max_retries})...")

        # 4. 汇总最终结果
        final_context = "\n".join(
            f"子任务{id}: {result}" for id, result in results.items()
        )
        return self.executor.execute("请汇总以下所有子任务结果，给出最终答案", final_context)
```

### 4.2 Agent通信协议

```python
from dataclasses import dataclass
from enum import Enum
import uuid

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ERROR = "error"

@dataclass
class AgentMessage:
    id: str
    sender: str
    receiver: str
    type: MessageType
    content: str
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class MessageBus:
    """Agent间消息总线"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    def send(self, message: AgentMessage):
        self.message_history.append(message)

        if message.type == MessageType.BROADCAST:
            for name, agent in self.agents.items():
                if name != message.sender:
                    self.message_queue.append(
                        AgentMessage(**{**message.__dict__, "receiver": name})
                    )
        else:
            self.message_queue.append(message)

    def process_queue(self):
        while self.message_queue:
            msg = self.message_queue.pop(0)
            if msg.receiver in self.agents:
                response = self.agents[msg.receiver].act(
                    f"收到来自 {msg.sender} 的消息:\n{msg.content}"
                )
                print(f"[{msg.receiver}] 收到消息并回复")
```

## 5. 最佳实践

| 实践 | 说明 |
|------|------|
| **明确工具边界** | 每个工具职责单一，输入输出格式明确 |
| **错误处理** | 工具失败时Agent应能优雅降级 |
| **最大迭代限制** | 防止Agent进入无限循环 |
| **记忆管理** | 短期记忆做窗口限制，长期记忆做重要信息持久化 |
| **人机协作** | 关键决策点加入人工确认环节 |
| **日志记录** | 记录每一步的Thought/Action/Observation |
| **工具安全** | 限制危险操作，如文件删除、数据库DROP |
| **渐进信任** | 从低风险操作开始，逐步授权 |

## 6. 相关页面

- [[Prompt Engineering指南]] - Agent的系统提示词设计
- [[RAG系统设计]] - Agent的知识检索能力
- [[LLM微调指南]] - 为Agent定制推理模型
- [[AI应用开发实践]] - Agent系统的工程化部署

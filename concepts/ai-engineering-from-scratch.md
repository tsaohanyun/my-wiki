---
author: Hermes Wiki Agent
created: 2026-06-19
description: 开源AI工程完整课程体系：503节实战课、20个递进阶段、4种编程语言，从线性代数手搓到自主Agent集群的端到端学习路径。涵盖数学基础、机器学习、深度学习、计算机视觉、NLP、Transformer、生成式AI、强化学习、LLM工程、多模态AI、Agent工程、生产基础设施、安全伦理、毕设项目。每节课均产出可复用的Prompt/Skill/Agent/MCP
  Server。MIT协议，全部完成。
project: 通用
sources:
- https://github.com/rohitg00/ai-engineering-from-scratch
- https://aiengineeringfromscratch.com
status: published
tags:
- ai-engineering
- machine-learning
- deep-learning
- llm
- agent
- curriculum
- open-source
- learning-path
title: AI Engineering from Scratch
type: concept
updated: 2026-06-19
version: 1.0.20260619
aliases:
  - "AI工程"
  - "从零构建AI"
---



# AI Engineering from Scratch

> 503节实战课 × 20个递进阶段 × 4种语言，从线性代数到自主Agent集群，每节课手搓算法+产出可复用工具。

## 概述

**AI Engineering from Scratch** 是一个完全开源（MIT协议）的AI工程系统课程，目标是弥合"84%的学生已在用AI工具，但仅18%觉得自己准备好专业使用"的认知鸿沟。

核心理念：**先手搓，再用框架**。每一个算法（反向传播、Tokenizer、注意力机制、Agent Loop）都从原始数学公式开始手写实现，然后才用PyTorch等生产框架完成同样的事。你理解框架在做什么，因为你已经亲手写过精简版了。

| 指标 | 数据 |
|------|------|
| 课程总量 | **503节课** |
| 阶段数 | **20个阶段** |
| 预估总时长 | ~320小时（核心路径）/ ~1,050小时（含毕设） |
| 编程语言 | Python、TypeScript、Rust、Julia |
| 协议 | MIT（自由fork、教学、商用） |
| 完成度 | 503/503 全部完成 ✅ |
| 产出物 | 388个Skills + 99个Prompts + Agents + MCP Servers |
| 网站 | [aiengineeringfromscratch.com](https://aiengineeringfromscratch.com) |

## 核心内容

### 课程架构：三层金字塔

课程采用严格依赖关系的三层架构，底层是上层的地基：

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3：LLM与应用AI (Phase 10-19)                      │
│  LLM从零构建 → LLM工程 → 多模态 → 工具协议 →            │
│  Agent工程 → 自主系统 → 多Agent → 生产基础设施 →         │
│  安全伦理 → 毕设项目                                      │
├─────────────────────────────────────────────────────────┤
│  Layer 2：深度学习核心 (Phase 3-9)                        │
│  DL基础 → 计算机视觉 → NLP → 语音 →                      │
│  Transformer → 生成式AI → 强化学习                        │
├─────────────────────────────────────────────────────────┤
│  Layer 1：数学与ML基础 (Phase 0-2)                        │
│  环境配置 → 数学基础 → 经典机器学习                       │
└─────────────────────────────────────────────────────────┘
```

### 20个阶段总览

| 阶段 | 主题 | 课时 | 时长 | 核心内容 |
|:---:|------|:---:|:---:|----------|
| 0 | 环境配置与工具链 | 12 | ~14h | Docker、Jupyter、GPU、调试、Shell、数据管理 |
| 1 | 数学基础 | 22 | ~23h | 线性代数→微积分→概率→信息论→傅里叶→图论 |
| 2 | 经典机器学习 | 18 | ~21h | 线性回归→SVM→决策树→集成方法→时间序列→异常检测 |
| 3 | 深度学习核心 | 13 | ~15h | 感知机→反向传播→激活函数→优化器→**手搓Mini框架**→PyTorch/JAX |
| 4 | 计算机视觉 | 28 | ~27h | CNN→YOLO→U-Net→扩散模型→SAM3→世界模型 |
| 5 | NLP | 29 | ~30h | Word2Vec→注意力机制→知识图谱→长上下文评估 |
| 6 | 语音与音频 | 17 | ~18h | FFT→Whisper→TTS→语音克隆→流式语音对话(Moshi) |
| 7 | Transformer深度解析 | 16 | ~14h | 自注意力→MoE→Flash Attention→KV Cache→投机解码 |
| 8 | 生成式AI | 15 | ~14h | VAE/GAN→DDPM→Stable Diffusion→ControlNet→Flow Matching |
| 9 | 强化学习 | 12 | ~13h | MDP→DQN→PPO→RLHF |
| 10 | 从零构建LLM | 25 | ~26h | Tokenizer→预训练124M GPT→SFT→DPO→量化→DeepSeek-V3架构 |
| 11 | LLM工程化 | 17 | ~17h | Prompt工程→RAG→LoRA/QLoRA→MCP→LangGraph |
| 12 | 多模态AI | 25 | ~65h | CLIP→LLaVA→InternVL3→具身VLA(π0/GR00T)→Computer Use |
| 13 | 工具与协议 | 23 | ~24h | Function Calling→**MCP全栈**(Server/Client/Auth/Security)→A2A→OpenTelemetry |
| 14 | **Agent工程** | 42 | ~42h | Agent Loop→MemGPT→LangGraph→CrewAI→**Agent Workbench** |
| 15 | 自主系统 | 22 | ~20h | 长时程Agent→自改进→Kill Switch→安全框架(RSP/PF/FSF) |
| 16 | 多Agent与群体智能 | 25 | ~28h | Supervisor模式→群智涌现→MARL→Agent经济学 |
| 17 | 生产基础设施 | 28 | ~32h | vLLM→SGLang→TensorRT-LLM→FinOps→合规(SOC2/HIPAA/GDPR) |
| 18 | 伦理、安全与对齐 | 30 | ~31h | 越狱攻防→水印→差分隐私→EU AI Act→红队工具 |
| 19 | **毕设项目** | 85 | ~620h | 17个端到端产品 + 9条深度构建链 |

### 课程依赖图

```
Phase 0 (环境) → Phase 1 (数学) → Phase 2 (ML基础)
                                      ↓
                    Phase 3 (深度学习核心)
                    ↓    ↓    ↓    ↓
                  P4   P5   P6   P9
                 视觉  NLP  语音  RL
                       ↓
                  P7 (Transformer) → P8 (生成式AI)
                       ↓
                  P10 (LLM从零) → P11 (LLM工程) → P12 (多模态)
                       ↓                ↓
                  P13 (工具协议) ← ← ← ↑
                       ↓
                  P14 (Agent工程) → P15 (自主系统) → P16 (多Agent)
                       ↓                ↓              ↓
                  P17 (基础设施) → P18 (安全伦理) → P19 (毕设)
```

### 每节课的结构

每节课遵循统一的**六拍结构**，"手搓/使用"是核心分水岭：

| 步骤 | 名称 | 内容 |
|:---:|------|------|
| 1 | **MOTTO** | 一句话核心理念 |
| 2 | **PROBLEM** | 具体痛点：没有这个知识你做不到什么 |
| 3 | **CONCEPT** | 图解与直觉，先建心智模型 |
| 4 | **BUILD IT** | 从原始数学手写实现，零框架依赖 |
| 5 | **USE IT** | 用PyTorch/sklearn等生产框架做同样的事 |
| 6 | **SHIP IT** | 产出可复用的Prompt/Skill/Agent/MCP Server |

**文件结构**（每节课一致）：
```
phases/NN-phase-name/NN-lesson-name/
├── code/      可运行实现（Python/TypeScript/Rust/Julia）
├── docs/
│   └── en.md  课程叙事文档
├── quiz.json  6道测验题（1前测+3中测+2后测）
└── outputs/   Prompt、Skill、Agent或MCP Server
```

### 核心产出物

每节课不仅教你，还给你一个**可直接使用的工具**：

| 产出类型 | 说明 | 数量 |
|----------|------|:---:|
| **Prompts** | 粘贴到任何AI助手的专家级Prompt模板 | 99 |
| **Skills** | Claude/Cursor/Codex/Hermes等Agent可识别的SKILL.md | 388 |
| **Agents** | 自主工作者（Phase 14的Agent Loop自己写的） | 多个 |
| **MCP Servers** | 任何MCP兼容客户端可接入的工具服务器 | 多个 |

一键安装到你的Agent：
```bash
# 安装全部技能
npx skills add rohitg00/ai-engineering-from-scratch

# 只安装某个阶段
npx skills add rohitg00/ai-engineering-from-scratch --phase 14

# 安装单个技能
npx skills add rohitg00/ai-engineering-from-scratch --skill agent-loop
```

### 课程内置Agent技能

课程本身支持Claude、Cursor、Codex、OpenClaw、Hermes等AI Agent读取：

| 技能 | 功能 |
|------|------|
| `/find-your-level` | 10道题定位测试，映射你的知识到起始阶段，生成个性化路径和时间估算 |
| `/check-understanding <phase>` | 按阶段自测，8道题+反馈+需复习的具体课程 |

## 方法论

### "Build It / Use It"教学法

这是课程的脊柱——先手搓理解原理，再用框架掌握实践：

| 阶段 | 做什么 | 为什么 |
|------|--------|--------|
| BUILD IT | 用纯数学/基础代码手写算法 | 理解底层原理，打破框架黑箱 |
| USE IT | 用PyTorch/sklearn等框架实现相同功能 | 掌握生产级工具和最佳实践 |
| SHIP IT | 输出可复用工具（Prompt/Skill/Agent） | 学以致用，积累可交付成果 |

**核心案例**：Agent Loop（Phase 14第1课）

```python
# BUILD IT — 约120行纯Python，零依赖
def run(query, tools):
    history = [user(query)]
    for step in range(MAX_STEPS):
        msg = llm(history)
        if msg.tool_calls:
            for call in msg.tool_calls:
                result = tools[call.name](**call.args)
                history.append(tool_result(call.id, result))
            continue
        return msg.content
    raise StepLimitExceeded
```

```markdown
# SHIP IT — 产出Skill文件
---
name: agent-loop
description: ReAct-style loop for any tool list
phase: 14
lesson: 01
---
Implement a minimal agent loop that...
```

### 课程贡献规范

| 规则 | 说明 |
|------|------|
| 每节课一个Git提交 | 10节课的PR = 10个提交 |
| Conventional Commits | `feat(phase-NN/MM): <slug>`，≤72字符 |
| 图表用Mermaid/SVG | 禁用ASCII/Unicode字符画 |
| 代码块必须有语言标签 | python/typescript/rust/bash等 |
| 原创实现优先 | 引用RFC和论文，不引用外部课程仓库 |
| 依赖白名单 | Python: numpy/torch/h5py/zstandard/safetensors + stdlib；Rust: 仅stdlib |

### 每节课的验证标准

| 检查项 | 要求 |
|--------|------|
| 代码运行 | 退出码0，无错误 |
| 自终止 | 不卡在stdin等待，不因缺API Key挂起 |
| 头部注释 | 4-6行，引用docs/en.md路径和RFC/论文来源 |
| 单元测试 | ≥5个测试用例 |
| quiz.json | 恰好6题：1 pre + 3 check + 2 post，correct字段零索引 |
| 文档格式 | frontmatter包含Title/Motto/Type/Languages/Prerequisites/Time |

### 课程审计脚本

```bash
# 完整课程审计
python3 scripts/audit_lessons.py

# 单个阶段审计
python3 scripts/audit_lessons.py --phase 14

# CI格式输出
python3 scripts/audit_lessons.py --json
```

审计规则L001-L010覆盖：目录结构、docs/en.md存在性与H1、code/非空、quiz.json schema、相对链接检查。

### 实施流程：从零到完成的学习路径

| 阶段 | 路径选择 | 预估时长 | 交付物 |
|------|----------|----------|--------|
| 定位 | `/find-your-level` 10题定位测试 | 15分钟 | 个性化起始Phase+路径 |
| 基础层 | Phase 0→2（环境+数学+ML） | ~58h | 数学直觉+经典ML实现能力 |
| 深度学习层 | Phase 3→9（DL/视觉/NLP/Transformer/RL） | ~121h | 神经网络从零实现+框架熟练 |
| LLM工程层 | Phase 10→13（LLM/工程/多模态/工具） | ~132h | LLM全栈能力+MCP/RAG/LoRA |
| Agent层 | Phase 14→16（Agent/自主/多Agent） | ~90h | Agent系统设计与实现能力 |
| 生产层 | Phase 17→18（基础设施/安全） | ~63h | 生产部署+安全合规 |
| 实战 | Phase 19（毕设） | ~620h | 17个可交付产品/9条深度链 |

### 入门建议矩阵

| 你的背景 | 建议起点 | 预估时长 |
|----------|----------|----------|
| 编程+AI零基础 | Phase 0 | ~306h |
| 会Python，ML新手 | Phase 1 | ~270h |
| 懂ML，想学深度学习 | Phase 3 | ~200h |
| 懂深度学习，想搞LLM和Agent | Phase 10 | ~100h |
| 资深工程师，只学Agent工程 | Phase 14 | ~60h |

## 毕设项目体系（Phase 19）

### 17个端到端产品

| # | 项目 | 综合阶段 | 预估时长 |
|---|------|----------|----------|
| 01 | 终端原生编码Agent | P0/P5/P7/P10/P11/P13/P14/P15/P17/P18 | ~35h |
| 02 | 代码库RAG（跨仓库语义搜索） | P5/P7/P11/P13/P17 | ~30h |
| 03 | 实时语音助手（ASR→LLM→TTS） | P6/P7/P11/P13/P14/P17 | ~30h |
| 04 | 多模态文档QA（Vision-First） | P4/P5/P7/P11/P12/P17 | ~30h |
| 05 | 自主科研Agent（AI-Scientist级别） | P0/P2/P3/P7/P10/P14/P15/P16/P18 | ~40h |
| 06 | K8s运维排障Agent | P11/P13/P14/P15/P17/P18 | ~30h |
| 07 | 端到端微调流水线 | P2/P3/P7/P10/P11/P17/P18 | ~35h |
| 08 | 生产级RAG聊天机器人（合规行业） | P5/P7/P11/P12/P17/P18 | ~30h |
| 09 | 代码迁移Agent（仓库级升级） | P5/P7/P11/P13/P14/P15/P17 | ~30h |
| 10 | 多Agent软件开发团队 | P11/P13/P14/P15/P16/P17 | ~40h |
| 11 | LLM可观测性与评估仪表盘 | P11/P13/P17/P18 | ~25h |
| 12 | 视频理解流水线（场景→QA） | P4/P6/P7/P11/P12/P17 | ~30h |
| 13 | 带注册中心的MCP Server | P11/P13/P14/P17/P18 | ~25h |
| 14 | 投机解码推理服务器 | P3/P7/P10/P17 | ~30h |
| 15 | 宪法安全框架 + 红队靶场 | P10/P11/P13/P14/P18 | ~25h |
| 16 | GitHub Issue→PR自主Agent | P11/P13/P14/P15/P17 | ~30h |
| 17 | 个人AI导师（自适应、多模态） | P5/P6/P11/P12/P14/P17/P18 | ~30h |

### 9条深度构建链

| # | 系列 | 子课数 | 核心组件 |
|---|------|:---:|----------|
| A | Agent Harness | 10 | Loop Contract → Tool Registry → JSON-RPC → Dispatcher → Plan-Execute → Verification Gates → Sandbox → Eval Harness → Observability → 端到端Demo |
| B | NLP/LLM从零 | 12 | BPE Tokenizer → 滑动窗口数据集 → Token/Position Embedding → Multi-Head Attention → Transformer Block → GPT组装 → 训练循环 → 权重加载 → SFT → DPO → 评估 |
| C | 端到端训练 | 7 | 语料下载 → HDF5分词 → Cosine LR → 混合精度 → 梯度累积 → Checkpoint → DDP/FSDP → LM Eval Harness |
| D | 自动科研 | 8 | 假设生成 → 文献检索 → 实验运行 → 结果评估 → 论文写作 → 批评循环 → 迭代调度 → 端到端Demo |
| E | 多模态VLM | 6 | Vision Encoder → ViT → 投影层 → Cross-Attention → 视觉-语言预训练 → 评估 |
| F | 高级RAG | 6 | Chunking策略 → BM25+Dense混合检索 → Cross-Encoder重排 → HyDE查询改写 → RAG评估 → 端到端RAG |
| G | 评估框架 | 6 | Task Spec → 经典指标 → Code Exec指标 → Perplexity → Leaderboard聚合 → 端到端Eval Runner |
| H | 分布式训练 | 6 | Collective Ops → DDP → ZeRO分片 → Pipeline Parallel → Checkpoint → 端到端分布式训练 |
| I | 安全护栏 | 6 | 越狱分类学 → Prompt注入检测 → 拒绝评估 → 内容分类器 → 宪法规则引擎 → 端到端安全门 |

## 关键术语表

课程配套完整术语表（glossary/terms.md），以下是核心术语精选：

| 术语 | 通俗说法 | 实际含义 |
|------|----------|----------|
| **Agent** | "自主AI" | 一个while循环：LLM决定调用哪个工具→执行→看结果→重复 |
| **Attention** | "AI聚焦重点" | 每个token计算所有其他token的值的加权和，权重由Q/K向量点积决定 |
| **RAG** | "AI能搜索" | 检索相关文档→塞进Prompt→LLM基于上下文回答 |
| **LoRA** | "高效微调" | 插入低秩矩阵旁路，只训练小矩阵，内存减少10-100x |
| **DPO** | "简化版RLHF" | 跳过奖励模型，直接优化LLM偏好更好的回答 |
| **KV Cache** | "推理加速" | 缓存历史token的Key/Value矩阵，避免重复计算 |
| **MCP** | "AI工具协议" | JSON-RPC over stdio/HTTP，标准化AI连接外部工具的开放协议 |
| **Temperature** | "创造力设置" | 缩放logits再softmax。高=更随机，低=更确定，不是"创造力" |
| **Fine-tuning** | "用你的数据训练AI" | 调整模型使用已有知识的方式，不是添加新知识（新知识用RAG） |
| **Hallucination** | "AI在编造" | 模型基于统计模式完成文本，不是在检索事实 |

## AI常见误解澄清

课程配套专门的"AI Myths Busted"文档，核心纠正如下：

| 误解 | 真相 |
|------|------|
| AI理解语言 | LLM是统计模式匹配器，不是推理引擎 |
| 参数越多越聪明 | 2.7B的Phi-2在很多基准上超过10倍大的模型，数据质量更关键 |
| 神经网络是黑箱 | 注意力可视化、探测分类器、机械可解释性都在进步 |
| AI会取代程序员 | AI写样板代码，人类设计系统+审查+架构，角色转变了 |
| 需要数学博士 | 高中数学+Phase 1的具体主题就够了 |
| 温度=创造力 | 温度是随机性旋钮，高温度不等于"想得更深" |
| 微调=教新知识 | 微调改变行为模式，新知识要用RAG |
| 越大越好 | Scaling Law显示边际递减，好的工程比盲目扩大模型更有效 |
| RLHF对齐人类价值观 | RLHF对齐的是标注员的偏好，不是普世价值 |
| 开源=开放权重 | 大多数"开源"只开放权重，不开放训练数据/代码/管线 |
| Prompt工程不是工程 | Prompt工程是系统设计——理解tokenization、注意力模式、上下文窗口、输出解析 |

## 风险与注意事项

| 风险 | 说明 | 缓解措施 |
|------|------|----------|
| **Bus Factor = 1** | 核心维护者仅一人，项目持续性风险 | MIT协议允许自由fork；社区贡献者数量在增长 |
| **AI辅助写作** | 课程内容为AI辅助生成+人工审查，非所有领域都有专家手工撰写 | 每节课有quiz.json验证理解，代码可运行测试 |
| **时间投入巨大** | 完整路径1050+小时，容易中途放弃 | `/find-your-level`精准定位起点，按需跳过已知阶段 |
| **GPU资源需求** | 部分高级课程（Phase 10/12/17）需要GPU | 课程设计含Colab链接和CPU fallback |
| **信息密度极高** | 503节课涵盖范围极广，从线性代数到EU AI Act | 严格依赖关系设计，可按需取用子路径 |
| **版本滞后风险** | AI领域迭代极快，部分内容可能较快过时 | 课程持续更新中（2026年仍在活跃维护） |

## 方案价值

### ROI分析

| 维度 | 价值 |
|------|------|
| **成本** | 全部免费（MIT协议），仅需时间投入+少量GPU费用 |
| **覆盖广度** | 从线性代数到生产部署，单一体系覆盖传统需要5-10本书+多门课的知识 |
| **实战产出** | 503个可直接使用的工具（Prompt/Skill/Agent/MCP Server），而非空洞的"恭喜你学会了" |
| **AI Agent兼容** | 388个Skills可直接安装到Claude/Cursor/Codex/Hermes等主流Agent |
| **企业内训适用** | MIT协议允许自由fork、定制、用于内部培训和商业课程 |
| **求职竞争力** | 17个毕设项目（端到端产品）可直接作为作品集 |
| **时间效率** | `/find-your-level`跳过已知内容，资深工程师Phase 14起仅需~60h |

### 与主流AI课程对比

| 特性 | 本课程 | 典型MOOC | 大学课程 |
|------|--------|----------|----------|
| 手搓优先 | ✅ 每个算法从零实现 | ❌ 通常直接用框架 | 部分 |
| 可复用产出物 | ✅ 503个工具 | ❌ 作业=一次性 | ❌ 论文/考试 |
| Agent工程深度 | ✅ 42课+毕设 | ❌ 较少涉及 | ❌ 极少 |
| MCP/RAG/LoRA工程 | ✅ 25+课 | 部分涉及 | ❌ |
| 生产部署 | ✅ 28课（vLLM/SGLang等） | 极少 | 极少 |
| 安全与伦理 | ✅ 30课 | 部分 | 部分 |
| AI Agent技能输出 | ✅ 388个Skills | ❌ | ❌ |
| 价格 | 免费 | $50-$5000 | 学费 |
| 完成度 | 503/503 ✅ | 多数不完整 | 完整 |

## 适用场景

### 个人学习
- AI/ML零基础想系统入门的开发者
- 会用API但想理解底层原理的工程师
- 需要Agent/RAG/MCP实战能力的AI应用开发者

### 企业内训
- MIT协议允许自由fork和定制
- 可删除不需要的阶段，添加公司特定示例
- 可映射到学期/培训周期，添加评分标准
- 可添加内部工具集成到outputs

### 二次开发
- 可fork后翻译为其他语言版本
- 可重写代码示例为目标编程语言
- 保持课程结构和文档格式不变
- 通过PR链接回主仓库形成生态

## 相关页面

- [[concepts/harness-engineering|Agent Harness工程方法论]] — 五层架构（Tool/Prompt/Permission/Orchestration/Memory），与Phase 14互补
- [[concepts/claude-api-development|Claude API开发]] — Anthropic SDK最佳实践，Phase 11的实践延伸
- [[concepts/mcp-server-development|MCP Server开发]] — Model Context Protocol开发指南，Phase 13的深度参考
- [[concepts/smart-manufacturing|智能制造]] — AI在制造业的应用背景
- [[entities/hermes-agent|Hermes Agent]] — CLI AI Agent平台，支持本课程的Skills安装
- [[concepts/text2kpi-optimization|Text2KPI优化]] — NL2API系统的工程实践，LLM工程化的应用案例

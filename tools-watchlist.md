---
created: 2026-06-01
tags:
- tool
- bookmark
- GitHub
title: 工具收藏清单
updated: 2026-06-19
---


# 工具收藏清单

> 收录有用但暂未安装的 GitHub 开源工具，按需取用。已安装的工具标注 ✅。

---

## 📄 文档处理

### MarkItDown ✅（已安装 v0.1.6）
- **仓库**：[microsoft/markitdown](https://github.com/microsoft/markitdown)
- **功能**：将任意文件（PDF/DOCX/PPTX/XLSX/HTML/CSV/JSON等）转换为 Markdown，专供 LLM 消费
- **适用场景**：Wiki 文档导入（doc-coauthoring wiki-document-ingest）、批量文件内容提取
- **安装状态**：已安装 CLI + MCP Server，全格式支持
- **评估**：⭐⭐⭐⭐（4/5）—— 与 OfficeCLI 互补（读取 vs 编辑）

---

## 🧠 代码理解

### Understand-Anything
- **仓库**：[Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything)
- **Stars**：46k+
- **功能**：将代码仓库自动转化为知识图谱，支持自然语言提问和交互式探索
- **适用场景**：接手不熟悉的代码库时快速理解架构；项目交接、新人 onboarding
- **安装命令**：`install.sh hermes --language zh`（原生支持 Hermes 平台）
- **依赖**：Node.js / pnpm / TypeScript 生态
- **评估**：⭐⭐⭐（3/5）—— 功能强大但主人的角色偏技术协调，直接读代码场景较少
- **备注**：如果后续需要深入某个代码库（如 Hermes Agent 本体源码），再装不迟

### codebase-memory-mcp
- **仓库**：[DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)
- **功能**：纯C编写的MCP Server，将代码仓库索引为带标签属性图（SQLite持久化），支持Cypher查询、调用链追踪、影响分析、跨服务HTTP调用检测等14个MCP工具
- **适用场景**：大规模代码库的结构化查询；变更影响分析；跨服务依赖追踪；死代码检测
- **核心优势**：
  - 纯C零依赖，单静态二进制（macOS/Linux/Windows）
  - 155种语言（内置tree-sitter语法）
  - 性能极强：Linux内核2800万行3分钟索引，Cypher查询<1ms
  - 不内嵌LLM，靠MCP Agent翻译查询，Token消耗极低（减少99.2%）
  - 有学术论文背书（arXiv:2603.27277），2812个测试，SLSA L3安全审计
- **依赖**：无运行时依赖，下载即用
- **评估**：⭐⭐⭐⭐（4/5）—— 工程极致主义，大规模结构化分析能力远超Understand-Anything
- **备注**：与Understand-Anything设计哲学不同——CBM是"赛车引擎"（快而精准），UA是"带导航的轿车"（慢但好懂）。CBM强在跨服务HTTP/消息队列追踪、死代码检测、Cypher查询、LSP级类型解析；UA强在自然语言问答、新人onboarding、业务域分析、引导式学习。主人角色偏技术协调，直接读代码场景较少，如需深入某个代码库再装不迟

---

## 🎨 设计系统

### DESIGN.md（Google Labs）
- **仓库**：[google-labs-code/design.md](https://github.com/google-labs-code/design.md)
- **功能**：为 AI 编码代理提供设计系统描述格式规范，用结构化文件定义视觉身份
- **核心特性**：
  - 双层结构：YAML 前置数据（机器可读的设计令牌）+ Markdown 正文（人类可读的设计说明）
  - CLI 工具 `@google/design.md`：lint 检查、版本 diff、导出 Tailwind/DTCG 格式
  - 8 个标准章节：概述→颜色→排版→布局→深度→形状→组件→注意事项
  - 支持组件令牌引用：`{colors.primary}`、`{typography.body-md}` 等
- **适用场景**：
  - 将 Apple Design Language / SIE-IIDP 企业风格固化为可复用设计规范
  - 多页面产品原型需要统一设计语言时
  - 给客户交付设计规范文档时
- **评估**：⭐⭐⭐（3/5）—— 格式规范有价值，但当前工作模式（默认 Apple + 偶尔切换）还未到需要规范化设计系统的程度
- **状态**：alpha 版本，活跃开发中
- **备注**：根目录无 DESIGN.md 文件，完整规范在 `docs/spec.md`，示例在 `examples/` 目录（含 Atmospheric Glass、Totality Festival、Paws and Paths 三个设计系统）

---

## 相关页面

- [[index]] — Wiki 总览

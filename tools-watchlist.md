---
title: 工具收藏清单
created: 2026-06-01
updated: 2026-06-01
tags: [工具, 收藏, GitHub]
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

---

## 相关页面

- [[index]] — Wiki 总览

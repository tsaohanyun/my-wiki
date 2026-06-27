project: hermes
---
title: Token消耗策略
aliases: [Token优化, 额度管理, 成本控制]
tags: [token, 优化, 策略]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: session-20260626_134548
difficulty: beginner
---
# Token 消耗策略

## 高消耗场景

### 1. 知识资产沉淀
- Wiki知识库构建
- 文档批量处理
- 深度研究主题

### 2. 代码开发
- 项目代码生成
- 代码审查和优化
- 技术方案设计

### 3. 内容创作
- 文章撰写
- 翻译工作
- 报告生成

### 4. 学习探索
- 技术学习
- 概念理解
- 案例分析

## 优化策略

### 1. 批量处理
```python
# 使用execute_code批量处理
# 比多次单独调用更节省token
```

### 2. 上下文管理
- 保持对话简洁
- 及时清理无用上下文
- 使用session隔离不同任务

### 3. 工具选择
- 简单任务用terminal
- 复杂推理用LLM
- 批量处理用execute_code

## Token即将过期时的建议

1. **优先做知识沉淀**：把经验转化为wiki
2. **批量处理文档**：一次性处理多个文件
3. **深度研究主题**：充分利用长上下文
4. **代码项目**：生成完整项目代码

## 相关页面

- [[Hermes-Agent架构总览]]
- [[Wiki管理最佳实践]]
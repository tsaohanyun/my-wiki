project: hermes
---
title: SillyTavern配置与使用
aliases: [SillyTavern, 角色卡, ST配置]
tags: [sillytavern, 角色扮演, 配置]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: creative/sillytavern-character-editor
difficulty: intermediate
---
# SillyTavern 配置与使用

## 概述

SillyTavern 是一个前端界面，支持多种LLM后端，用于角色扮演对话。

## API配置

### 主要Provider

| Provider | 模型 | API Key |
|----------|------|---------|
| z.ai | GLM-5.2 | GLM_API_KEY |
| 腾讯云 | GLM-4-plus | GLM_FALLBACK_KEY |

### 回退链

DeepSeek → GLM-5.2 → GLM-4-plus

## 角色卡汉化

### 翻译陷阱

1. **验证CJK内容**：`.bak`文件存在≠翻译成功
2. **V2卡顶层字段**：需同步翻译
3. **NSFW内容过滤**：GLM-4-plus约10%内容被过滤
4. **推理token**：GLM-5.2需`max_tokens≥500`

### 批量翻译流程

```python
# 1. 读取角色卡
# 2. 调用翻译API
# 3. 验证翻译结果
# 4. 保存并备份
```

## 世界书管理

- 按主题分类组织
- 定期备份到GitHub
- 使用标签系统管理

## 相关页面

- [[Hermes-Agent架构总览]]
- [[Token消耗策略]]
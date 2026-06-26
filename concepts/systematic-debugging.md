---
author: Hermes Wiki Agent
created: 2026-04-30
description: '系统化调试的4阶段方法论，强调在修复前必须先理解问题根因。 - test-driven-development - 测试预防缺陷

  '
project: 通用
sources:
- raw/articles/systematic-debugging.md
status: published
tags:
- best-practice
title: 系统化调试方法论
type: concept
updated: 2026-04-30
version: 1.0.20260530
---




# 系统化调试方法论

## 概述
系统化调试的4阶段方法论，强调在修复前必须先理解问题根因。
## 4阶段流程
1. **问题复现** - 稳定复现问题
2. **假设验证** - 提出并验证假设
3. **根因定位** - 定位根本原因
4. **修复验证** - 验证修复方案
## 核心原则
- **不要急于修复** - 先理解问题
- **最小化复现** - 找到最小复现路径
- **二分定位** - 使用二分法缩小范围
- **记录过程** - 记录调试过程和发现
## 交叉引用
- [[concepts/test-driven-development|test-driven-development]] - 测试预防缺陷
- [[concepts/requesting-code-review|requesting-code-review]] - 代码审查发现问题
- [[concepts/writing-plans|writing-plans]] - 计划中考虑边界情况

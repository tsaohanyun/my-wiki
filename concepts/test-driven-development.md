---
title: 测试驱动开发
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [实践, 测试, TDD, 质量]
sources: [raw/articles/test-driven-development.md]
---

# 测试驱动开发

## 概述
测试驱动开发 (TDD) 的实践指南，强调先写测试、再写实现、最后重构的开发循环。
## TDD 循环
1. **RED** - 编写失败的测试
2. **GREEN** - 编写最少代码使测试通过
3. **REFACTOR** - 重构代码保持测试通过
## 核心原则
- **测试先行** - 在实现前编写测试
- **小步前进** - 每次只实现一个小功能
- **保持测试通过** - 重构时确保测试不失败
- **测试即文档** - 测试描述了代码行为
## 交叉引用
- [[systematic-debugging]] - 调试失败的测试
- [[requesting-code-review]] - 审查测试覆盖率
- [[writing-plans]] - 计划测试策略

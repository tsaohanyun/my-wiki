# Wiki 模式定义

## 领域
软件工程 — 技术栈、架构模式、工具、框架、最佳实践、设计原则与工程文化。

## 约定
- 文件名：小写、连字符、无空格（如 `react-server-components.md`）
- 每个 wiki 页面以 YAML 前置元数据开头（见下方）
- 使用 `[[wikilinks]]` 链接页面（每页至少2个出站链接）
- 更新页面时，务必更新 `updated` 日期
- 每个新页面必须添加到 `index.md` 对应的分类下
- 每个操作必须追加到 `log.md`
- **溯源标记：** 综合了3个及以上来源的页面，在段末追加 `^[raw/articles/source-file.md]`
  标记该段落的论断来自特定来源。

## 前置元数据
```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [来自下方分类法]
sources: [raw/articles/source-name.md]
# 可选质量信号：
confidence: high | medium | low        # 论断的支持程度
contested: true                        # 页面存在未解决的矛盾时设置
contradictions: [other-page-slug]      # 与此页面冲突的其他页面
---
```

`confidence` 和 `contested` 为可选项，但在观点密集或快速变化的主题中推荐使用。Lint 会标记 `contested: true` 和 `confidence: low` 的页面供审阅，防止弱论断悄然固化为公认的 wiki 事实。

### raw/ 前置元数据

原始来源也需要一小段前置元数据，以便重新摄入时检测变化：

```yaml
---
source_url: https://example.com/article   # 原始 URL（如适用）
ingested: YYYY-MM-DD
sha256: <原始内容（前端元数据下方）的十六进制摘要>
---
```

`sha256:` 让未来对同一 URL 的重新摄入可以在内容未变时跳过处理，在内容变化时标记漂移。摘要仅计算正文（闭合 `---` 之后的所有内容），不包含前置元数据本身。

## 标签分类法
- 语言与运行时：language, runtime, compiler, type-system
- 框架与库：framework, library, sdk, api
- 架构与设计：architecture, pattern, design-principle, ddd, microservices
- 基础设施与 DevOps：infra, containerization, orchestration, ci-cd, monitoring, cloud
- 数据库与存储：database, cache, message-queue, storage
- 测试与质量：testing, quality, linting, code-review
- 安全：security, auth, encryption
- 工具与效率：tool, editor, cli, productivity
- 实践与文化：best-practice, agile, team-process, documentation
- 元信息：comparison, timeline, controversy, prediction, trend

规则：页面上的每个标签必须出现在此分类法中。如需新标签，先在此添加，再使用。

## 页面阈值
- **创建页面** 当某个实体/概念出现在2个及以上来源中，或在某个来源中处于核心地位
- **添加到已有页面** 当来源提及已有内容覆盖的内容
- **不要创建页面** 用于附带提及、次要细节或领域外的内容
- **拆分页面** 当页面超过约200行 — 拆分为子主题并添加交叉链接
- **归档页面** 当内容已完全过时 — 移至 `_archive/`，从 index 中移除

## 实体页面
每个值得关注的实体（工具、框架、语言、公司）一个页面。包含：
- 概述 / 是什么
- 关键事实和日期
- 与其他实体的关系（[[wikilinks]]）
- 来源参考

## 概念页面
每个概念或主题（模式、原则、实践）一个页面。包含：
- 定义 / 解释
- 当前知识状态
- 开放问题或争议
- 相关概念（[[wikilinks]]）

## 对比页面
并排分析。包含：
- 对比什么以及为什么对比
- 对比维度（表格格式优先）
- 结论或综合
- 来源

## 更新策略
当新信息与现有内容冲突时：
1. 检查日期 — 较新的来源通常优先
2. 如果确实矛盾，同时记录两种立场，附日期和来源
3. 在前置元数据中标记矛盾：`contradictions: [page-name]`
4. 在 lint 报告中标记供用户审阅

# Wiki 日志

> 所有 wiki 操作的按时间顺序记录。仅追加。
> 格式：`## [YYYY-MM-DD] 操作 | 主题`
> 操作类型：ingest, update, query, lint, create, archive, delete
> 当此文件超过500条记录时，轮转：重命名为 log-YYYY.md，重新开始。

## [2026-04-30] create | Wiki 初始化
- 领域：软件工程
- 创建了 SCHEMA.md、index.md、log.md 结构
- 标签分类法：10个类别，涵盖语言、框架、架构、基础设施、数据库、测试、安全、工具、实践、元信息

## [2026-04-30] ingest | 7个 Hermes 技能（FineReport + Web 生成）
- 来源：fine-report-cpt、apple-prototype-html、product-prototype-html、frontend-design、retro-futuristic-html、popular-web-designs、frontend-slides
- 保存的原始文件：7个文件在 raw/articles/
- 创建的实体：fine-report-cpt.md、popular-web-design-templates.md
- 创建的概念：html-prototype-generation.md、frontend-design-system.md、retro-futuristic-html-design.md、frontend-slides-presentation.md
- 创建的对比：html-generation-styles.md
- 交叉引用：所有页面共15+个 wikilink
- apple-prototype-html 和 product-prototype-html 合并为单个概念（html-prototype-generation），因为它们共享同一设计系统

## [2026-04-30] update | Wiki 中文化
- 将 SCHEMA.md、index.md、log.md 中所有英文内容翻译为简体中文
- 内容页面（entities、concepts、comparisons）已经是中文，无需修改
- raw/ 目录按约定保持不变（原始来源不可修改）

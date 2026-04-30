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
## [2026-04-30] ingest | 14个技能（核心开发 + 文档处理）
- 来源：claude-api、mcp-builder、hermes-agent、systematic-debugging、test-driven-development、writing-plans、requesting-code-review、plan、skill-creator、docx、xlsx、pptx、pdf、doc-coauthoring
- 保存的原始文件：14个文件在 raw/articles/
- 创建的实体：hermes-agent.md、word-document-processing.md、excel-spreadsheet-processing.md、powerpoint-presentation-processing.md、pdf-document-processing.md
- 创建的概念：claude-api-development.md、mcp-server-development.md、systematic-debugging.md、test-driven-development.md、writing-plans.md、requesting-code-review.md、plan-mode.md、skill-creator.md、doc-coauthoring.md
- 交叉引用：所有页面共 40+ 个 wikilink
- 总页面数：20（原有6 + 新增14）

## [2026-05-01] update | Wiki 英文内容中文化
- 更新 frontend-design-system.md：设计思维框架标签 Purpose→目的、Tone→调性、Constraints→约束、Differentiation→差异化
- 更新 frontend-slides-presentation.md：Phase→阶段、心情名称 Impressed→震撼、Excited→兴奋、Calm→平静、Inspired→灵感
- 更新 html-prototype-generation.md：布局图中英文标签翻译为中文（Top Nav→顶部导航栏、Side bar nav→侧边导航、Content Area→内容区域、Func Panel→功能面板、Bottom Tab Bar→底部标签栏、FAB→悬浮按钮）
- 其余21个页面已全部为中文，无需修改

## [2026-04-30] ingest | 幕布文档10篇（大数据治理/智能制造/政策/可视化等）
- 来源：trans-import 目录下10个幕布文档导出的 HTML 文件
- 保存的原始文件：9个文件在 raw/articles/（big-data-governance-day1~3、smart-manufacturing-overview、smart-factory-planning、manufacturing-digital-policy、data-visualization-selection、consensus-management、tianwei-food-pain-points）
- 创建的概念：big-data-governance.md、smart-manufacturing.md、smart-factory-planning.md、manufacturing-digital-policy.md、data-visualization-selection.md、consensus-management.md
- 创建的实体：tianwei-food-digital-status.md
- 合并策略：大数据治理3天内容合并为1个概念页面，"技术驱动"并入"智能制造"概念页面
- 新增标签分类：数据治理（6个标签）、智能制造（5个标签）、可视化（3个标签）、产业政策（2个标签），consensus 加入实践与文化
- 交叉引用：7个页面共 20+ 个 wikilink
- 总页面数：27（原有20 + 新增7）

## [2026-04-30] ingest | Harness Engineering 方法论
- 来源：用户提供文档"01_Harness_Engineering方法论.md"
- 保存的原始文件：raw/articles/harness-engineering-methodology.md
- 创建的概念：harness-engineering.md、text2kpi-optimization.md
- 同步创建 SKILL：software-development/harness-engineering（五层架构方法论提炼为可操作指南）
- 交叉引用：2个页面共 6 个 wikilink
- 总页面数：29（原有27 + 新增2）

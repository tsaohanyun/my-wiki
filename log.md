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

## [2026-05-02] ingest | Text2KPI V2 + NL2SQL 方案4篇
- 来源：trans-import 目录下4个 Markdown 文件（02b_NL2SQL精确映射方案、02_Text2KPI_Demo设计方案V2、text2kpi-reference-code、text2kpi-prompt-and-config）
- 保存的原始文件：4个文件在 raw/articles/
- 创建的概念：nl2sql-precise-mapping.md（7879 bytes）、text2kpi-reference-code.md（12370 bytes）、text2kpi-prompt-and-config.md（9981 bytes）
- 更新的概念：text2kpi-optimization.md（6908→14221 bytes，补充V2四层架构/五步Pipeline/查询编排/推理可观测设计）
- 合并策略：V2设计方案与已有text2kpi-optimization属同项目演进，更新而非另建
- 新增标签：架构与设计新增 nl2sql、nl2api；实践与文化新增 prompt-engineering；工具与效率新增 config
- 交叉引用：4个页面共 12+ 个 wikilink，形成 Text2KPI 系列知识网络
- 总页面数：32（原有29 + 新增3）

## [2026-05-03] ingest | SIE-IIDP 设计风格分析
- 来源：/home/agentuser/trans-import/ 目录下的10个 DIM 系统 HTML 页面及其配套 CSS/JS/SVG 资产
- 来源实体：SIE-IIDP 工业互联网数据平台，DIM 制造执行系统
- 保存的原始文件：raw/articles/sie-iidp-design-analysis.md
- 创建的概念：sie-iidp-design-style.md（5272 bytes）
- 新增标签：架构与设计新增 design-system、ui-design、css-variables、frontend-design、component-library
- 分析维度：色彩系统（含CSS变量体系）、排版（100px根字号）、布局架构、图标系统、组件设计语言、间距规范、设计哲学、与主流系统对比
- 核心发现：#AC2A48 贯穿全部组件、2px 极小圆角、100px 根字号 rem 缩放、白色 SVG 圆形徽章图标系统
- 交叉引用：5个 wikilink（frontend-design-system、html-generation-styles、retro-futuristic-html-design、smart-manufacturing、apple-prototype-html）
- 总页面数：33（原有32 + 新增1）

## [2026-05-04] ingest | 6份文档（制造业运营管理方向）
- 来源：trans-import 目录下6个文件（中小企业数字化模式创新研究报告2023.pdf、制造业数据指标体系.pdf、指标中台建设方法与实践.pdf、效率与效率改善方法.pdf、VSM.pptx、APQC流程绩效指标库.pdf）
- 跳过文件：AIGC产业发展及应用白皮书-2023.pdf（扫描版，无有效文本）
- 保存的原始文件：7个文件在 raw/articles/（含1个补充分段文件）
- 创建的概念（5个）：sme-digital-innovation.md（2457 bytes）、manufacturing-kpi-system.md（2391 bytes）、metric-platform-construction.md（2926 bytes）、efficiency-improvement-methods.md（2449 bytes）、value-stream-mapping.md（1867 bytes）
- 创建的实体（1个）：apqc-process-metrics.md（2235 bytes）
- 新增标签：智能制造新增 lean-manufacturing, vsm, efficiency；工具与效率新增 kpi, process-management
- 合并策略：中小企业数字化报告2个分段原文件合并为1个wiki页面；APQC作为实体（标准框架），其余5个作为概念
- 交叉引用：6个页面共 12+ 个 wikilink，连接智能制造知识网络
- 总页面数：42（原有36 + 新增6）

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

## [2026-05-04] update | manufacturing-kpi-system 方法论扩展
- 来源：trans-import/【搭建标准】制造业指标体系搭建指导(26页).pdf
- 保存的原始文件：raw/articles/manufacturing-kpi-guide.md
- 更新页面：manufacturing-kpi-system.md（2341 → 6909 bytes）
- 新增内容：指标体系搭建4大原则、指标金字塔（核心/业务/操作三层）、搭建4大关键步骤、指标拆解4步流程、指标命名公式（限定词+业务主题+指标名称+量化词）、指标字典五要素、设备/质量/出入库/库存/采购/财务分析等详细KPI参考
- 新增wikilink：value-stream-mapping（与VSM建立连接）

## [2026-05-04] ingest+update | 数据治理补充 + 大数据技术体系新建
- 来源：trans-import/数据治理的全貌.pdf、大数据治理训练营-一大数据治理的解读.pdf、大数据开发基础知识.pdf
- 保存的原始文件：raw/articles/data-governance-overview.md、raw/articles/bigdata-development-basics.md
- 更新概念：big-data-governance.md（补充消息队列Kafka & Flink流批一体、数据湖、数据API服务、数据资产监控、Apache Atlas详解）
- 新建概念：big-data-development-basics.md（4021 bytes）——企业级大数据技术六层框架、Hadoop/Spark技术栈、HDFS分布式文件系统、Lambda Architecture
- 新增wikilink：big-data-development-basics 链接 big-data-governance、data-visualization-selection
- 总页面数：43（原有42 + 新增1）

## [2026-05-04] update | SCHEMA.md 新增"去除编著信息"标准
- 来源：用户要求
- 更新 SCHEMA.md 约定章节，新增"去除编著信息"规则：原始文件和 wiki 页面中不得保留作者、编著者、出品机构、研究团队等署名信息
- 该规则已应用于本次编辑的 6 个文件

## [2026-05-04] ingest | 数据中台 + 指标中台补充 + 白酒行业分析
- 来源：trans-import/数据中台解决方案.pdf、FI指标中台产品介绍V4.pdf、白酒Ⅲ行业深度报告：酱酒专题.pdf
- 保存的原始文件：raw/articles/data-mid-platform-solution.md、raw/articles/fi-metric-platform-intro.md、raw/articles/baijiu-industry-report.md（均去除编著信息）
- 新建概念（2个）：data-mid-platform.md（3154 bytes）——数据中台全链路架构与产品能力、baijiu-industry-analysis.md（2271 bytes）——酱香型白酒市场分析
- 更新概念：metric-platform-construction.md（2868 → 5297 bytes）——补充需求驱动vs数据驱动理念、产品功能/技术架构、指标PDCA闭环、预警与目标管理、零代码配置等产品实践内容
- 交叉引用：data-mid-platform 链接 metric-platform-construction、big-data-governance、big-data-development-basics
- 总页面数：45（原有43 + 新增2）

## [2026-05-04] delete | 去除天味食品相关描述
- 删除实体页面：entities/tianwei-food-digital-status.md
- 删除原始文件：raw/articles/tianwei-food-pain-points.md
- 去除 wikilink 引用：smart-manufacturing.md、manufacturing-digital-policy.md、smart-factory-planning.md
- 更新 index.md 移除条目
- 总页面数：44（原有45 - 删除1）

## [2026-05-05] ingest | 10份文档批量纳入（数字孪生/数据治理/企业信息化/智能制造）
- 来源：trans-import目录下12个有效文件（含4个ISA-95标准合并为1个）
- 跳过7个图片型文件（数据治理及数据资产化创新实践-京东.pdf、企业智能制造解决方案.pdf、京东物流数字孪生白皮书.pdf、数据仓库架构落地版.pptx、华为APS系统总体架构介绍.ppt、华为内训绩效管理.ppt、数据中台解决方案.pdf（已处理过））
- 原始文件：raw/articles/ 下12个文件（已去除华为/编著/品牌等信息）
- 新建概念（10个）：
  - digital-twin.md — 数字孪生技术架构与应用
  - data-asset-management-standard.md — 数据资产管理标准化
  - data-element-valuation.md — 数据要素价值评估
  - data-security-governance.md — 数据安全治理体系
  - enterprise-info-flow-planning.md — 企业信息流规划
  - enterprise-architecture-planning.md — 企业架构与信息化规划
  - isa-95-integration.md — ISA-95企业控制系统集成（4部分合并）
  - aps-advanced-planning-scheduling.md — APS高级计划与排程
  - data-governance-two-phase.md — 数据治理两阶段实践
  - logistics-transport-solution.md — 物流与运输解决方案
- 交叉引用：10个页面共 20+ 个wikilink
- 总页面数：54（原有44 + 新增10）

## [2026-05-05] ingest | 智能工厂详细设计-精益文档
- 来源：trans-import/TWAD_IF_智能工厂生产业务平台详细设计-精益.docx
- 文档编号：TWAD_IF_302 V1.4，共4846行，涵盖9大精益管理业务模块
- 原始文件：raw/articles/smart-factory-lean-detail-design.md（已去除品牌/编著信息）
- 新建概念（1个）：detail-design-specification.md — 详细设计文档编写规范
  - 提炼通用编写规范而非仅精益管理业务内容
  - 包含：功能描述7要素模板、三区字段定义、审批流/定时任务/多终端设计模式
- Skill创建：consulting/detail-design-specification
  - SKILL.md：详细设计文档编写规范（通用方法论）
  - references/lean-module-functions.md：精益管理9大模块功能清单与设计要点
  - templates/function-design-template.md：功能描述空白模板
- SCHEMA.md新增标签：occupational-health, safety-management, kpi-indicator
- 交叉引用：6个wikilink（feed-industry-solution, feed-industry-knowledge, smart-factory-planning, efficiency-improvement-methods, manufacturing-kpi-system, blueprint-writing-methodology）
- 总页面数：55（原有54 + 新增1）

## [2026-05-07] ingest | 通威农发数据库表结构
- 来源：/home/agentuser/trans-import/snest.sql（24MB，3785条CREATE TABLE语句）
- 分析：过滤1418个分区表、55个备份表后，提取1407张核心业务表，按108个模块前缀分组
- 新建目录：databases/，共创建18个wiki页面
- 总页面数：73

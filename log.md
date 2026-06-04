---
title: Wiki 日志
project: 通用
created: '2026-05-27'
updated: '2026-05-27'
---

## 2026-05-26 (重构)

### 久立项目Wiki知识库重构（10页→6页，1.4MB→620KB）

**重构目标**：从"原文搬运"转为"知识库"结构，按知识维度而非文件维度组织。

**主要改动**：
1. 合并同类页面：调研纪要+调研报告+痛点需求 → 单一「业务调研」页面
2. 合并蓝图页面：一期蓝图+三四期蓝图 → 按PPF功能模块编码组织的单一页面
3. 合并治理页面：章程+范围+里程碑 → 「项目治理」
4. 清洗噪音：去除文档封面/签字页/变更记录等非知识性内容
5. 去重：痛点需求xlsx多个版本只保留最新版
6. 结构化：用表格/列表替代原文段落堆砌

**旧版问题**：
- 文件名做标题（f31.txt）
- 文档头/签字页未清除
- 同一模块在多个页面重复出现
- xlsx管道符表格直接转储
- 按文件来源组织而非按知识主题

**新版结构**：
- [[久立项目/久立项目-项目总览]] — 架构图、模块体系表、分期时间线
- [[久立项目/久立项目-蓝图方案]] — 按PPF编码（WM/ME-2xx~7xx）功能域组织
- [[久立项目/久立项目-业务调研]] — 按车间/仓储业务领域组织，痛点去重
- [[久立项目/久立项目-系统接口]] — 接口总览表+详细规范
- [[久立项目/久立项目-操作手册]] — 按IPC/PC/PDA终端分类
- [[久立项目/久立项目-项目治理]] — 章程核心条款+里程碑

## 2026-05-26 (续)

### 久立项目详细调研报告导入（+1页）

从Windows端 `C:\temp\jiuli3\large\` 传输并提取6个超大调研报告文档。

**处理方式**：
- 10个大文件（50-183MB）通过SCP压缩传输到服务器
- .doc文件使用antiword提取文字（6个成功）
- .pptx文件（MES车间亮点总结162MB）python-pptx未安装，跳过
- 冷轧一厂V20/V30/V50为重复版本（仅保留V40最新版）

**新增页面**：
- [[久立项目/久立项目-业务调研]] — 详细版调研报告（273KB）
  - 一期：冷轧一厂车间（64,774字）、JCO分厂（40,016字）、辅料仓库（61,888字）
  - 四期：成品&废料仓储（60,930字）、管件板材（40,692字）、管件管制（117,219字）
  - 共提取385,519字符

**跳过**：
- f21.doc (冷轧一厂V20) — 重复，已有V40
- f22.doc (冷轧一厂V30) — 重复，已有V40
- f24.doc (冷轧一厂V50) — 重复，已有V40
- f37.pptx (MES亮点总结162MB) — python-pptx未安装

## 2026-05-26

### 久立特材数字化平台项目导入（+9页）

从Windows远程目录 `D:\前归档\JIULI交付` 导入久立特材MES项目交付文档。

**处理范围**：
- 扫描四期交付文档（8000+文件），筛选93个关键文档
- 提取文本内容92个文件（315万字符），跳过图片型/视频型文件
- 脱敏处理：移除个人姓名和实施方公司名

**新增页面**：
- [[久立项目/久立项目-项目总览]] — 四期项目概述
- [[久立项目/久立项目-项目治理]] — 项目章程+范围定义
- [[久立项目/久立项目-业务调研]] — 各期调研纪要汇总（197KB）
- [[久立项目/久立项目-业务调研]] — 痛点需求汇总（121KB）
- [[久立项目/久立项目-蓝图方案]] — 一期蓝图（冷轧/JCO/仓储，193KB）
- [[久立项目/久立项目-蓝图方案]] — 三四期蓝图（319KB）
- [[久立项目/久立项目-系统接口]] — SAP/MES/OA接口（33KB）
- [[久立项目/久立项目-操作手册]] — 18个功能操作手册（26KB）
- [[久立项目/久立项目-项目治理]] — 里程碑确认报告（39KB）

**跳过的文件**：
- 10个超大.doc/.pptx文件（100-183MB，图片型调研报告/总结PPT）
- 1个.doc文件antiword提取失败
- Visio流程图(.vsdx)、开发文档、源码、压缩包

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

## [2026-05-15] ingest | 方法论知识总览（trans-import文件夹15套方法论）
- 来源：trans-import/ 下27个方法论文件（含重复），涵盖企业架构、数字化转型、实施交付、咨询销售四大类别
- 实际有效方法论约15套，提取核心框架和步骤
- 创建的概念：
  - [[concepts/methodologies-overview|methodologies-overview]] — 方法论知识总览（四大类别全景）
  - [[concepts/enterprise-it-planning-methodology|enterprise-it-planning-methodology]] — 企业架构与IT规划方法论（EA四视图+四步法）
  - [[concepts/digital-transformation-methodology|digital-transformation-methodology]] — 数字化转型方法论（12367+三段论+五步法）
  - [[concepts/implementation-methodology|implementation-methodology]] — 实施方法论（IPM五阶段+六步法+汉得中台）
  - [[concepts/consulting-sales-methodology|consulting-sales-methodology]] — 咨询与销售方法论（麦肯锡七步法+金蝶售前+MEDDIC）
- 索引更新：84 → 89页
- PDF扫描件/图片型文件跳过（系统工程方法论、华为白皮书等）

## [2026-05-02] ingest | Text2KPI V2 + NL2SQL 方案4篇
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

## [2026-05-07] update | 通威农发数据库结构调整
- 新增页面：[[通威农发/技术架构/通威农发-报表预处理中间表|通威农发-报表预处理中间表]]（ST 42张 + LM_ST 42张，共84张统计中间表）
- 分离调整：ST与MI → 拆分为 MI制造智能 (38张) + 报表预处理中间表 (84张)
- LM精益管理：移除 lm_st_* 42张统计中间表，更新计数为154张
- 更新：数据库总览、index.md
- 总页面数：74

## [2026-05-11] ingest | 采购管理（百度百科）
- 来源：https://baike.baidu.com/item/采购管理/3925
- 保存的原始文件：raw/articles/procurement-management-baike.md
- 创建的概念：[[concepts/procurement-management|procurement-management]] — 采购管理概念页面
- 更新：SCHEMA.md — 新增"企业管理与供应链"标签分类（enterprise-management, supply-chain, procurement, purchasing, logistics, inventory, supplier）
- 交叉引用：4个wikilink（smart-manufacturing, feed-industry-solution, logistics-transport-solution, manufacturing-kpi-system）
- 总页面数：76（原有75 + 新增1）

## [2026-05-14] create | 天然气处理厂 — 生产组织与质量管理
- 新建 wiki 页面：[[queries/natural-gas-processing/06-生产组织|06-生产组织]] — 组织架构、岗位体系、倒班制度、设备管理、HSE、环保、信息化（12.6KB）
- 新建 wiki 页面：[[queries/natural-gas-processing/07-质量管理|07-质量管理]] — 质量管理体系、产品标准、在线监测、化验分析、不合格品管理、计量管理（13.4KB）
- 更新 index.md：新增06/07页面条目，总页面数 82→84
- 新建综合研究报告：天然气处理厂_研究报告.md（18KB，覆盖工艺制程/生产组织/质量管理/数字化展望）
- 说明：网络搜索受限（GFW阻断），内容基于行业标准、技术文献和工程实践知识库编写

## [2026-05-15] create | 行业分析独立结构 industry-analysis
- 创建目录：queries/industry-analysis/
- 创建页面：index.md — 行业分析总览目录
- 目的：为行业/公司研究提供独立空间，与天然气工艺技术页面分离，避免命名混淆
- 命名规范：queries/industry-analysis/公司名-研究维度.md
- 索引更新：89 → 90页

## [2026-05-15] restructure | WIKI目录结构大整理
- ① natural-gas-processing 整目录从根目录移至 queries/ 下
- ② 合并 concepts/ 下2个天然气概念页入 queries/natural-gas-processing/（00-工厂概述 + 08-工艺流程详解）
- ③ 白酒行业分析从 concepts/ 移至 queries/industry-analysis/
- ④ 7个根目录散落文件移入 concepts/（apqc-process-metrics, efficiency-improvement-methods等）
- ⑤ 修复内部断链：工厂概述页3个失效引用→正确指向系列内页面
- ⑥ 更新 index.md：天然气路径统一为 queries/xxx，白酒移至查询节
- 关键原则：queries/ 放行业分析+专题研究，concepts/ 放通用概念，不再混放

## [2026-05-15] ingest | trans-import 制造业方案文档批量导入
- 来源: /home/agentuser/trans-import/ (109个文件: PPTX/PDF/DOCX/PPT/DOC)
- 成功提取: 95个文件, 14个损坏/无法读取
- 按行业分类为25个类别, 整合为10个wiki页面 + 1个索引页
- 创建页面:
  - queries/manufacturing-solutions/index.md — 制造业数字化解决方案总览
  - queries/manufacturing-solutions/离散制造行业方案.md — 注塑/汽配/机加工/钣金/铸造/新材料/电梯/钢铁(23份)
  - queries/manufacturing-solutions/流程与新能源行业方案.md — 化工/光伏/光纤光缆(12份)
  - queries/manufacturing-solutions/消费与医疗行业方案.md — 医药/食品/酒类(4份)
  - queries/manufacturing-solutions/汽车与交通行业方案.md — 汽车/ANDON/电子(8份)
  - queries/manufacturing-solutions/智能制造通用方案.md — 通用方案(16份)
  - queries/manufacturing-solutions/WMS仓储与SRM供应链.md — WMS/SRM(7份)
  - queries/manufacturing-solutions/物联网与设备管理.md — IIoT/设备(7份)
  - queries/manufacturing-solutions/数据与指标体系.md — 数据/指标(7份)
  - queries/manufacturing-solutions/IT战略与数字化规划.md — IT战略(3份)
  - queries/manufacturing-solutions/厂商与案例汇编.md — 厂商/案例(8份)
- 更新: index.md (新增制造业方案分类, 页面数90→101)

## [2026-05-15] update | 制造业方案Wiki结构优化
- 原因: 3个页面超过200行阈值, 内容含原始slide标记和未脱敏公司名
- 优化内容:
  1. 清洗所有页面: 去除 === /slide[N] ===, #OCLI_NOTEVAL!, 公司名称脱敏
  2. 拆分3个大页面:
     - 离散制造行业方案(379行) → 离散制造-注塑汽配机加工钣金(113行) + 离散制造-铸造新材料电梯钢铁(103行)
     - 智能制造通用方案(265行) → 智能制造-智能工厂规划(92行) + 智能制造-产品方案体系(77行)
     - 流程与新能源行业方案(212行) → 流程制造-化工行业(72行) + 流程制造-光伏光纤光缆(64行)
  3. 总页面数: 11 → 13 (拆分6个新页面, 删除5个旧页面)
  4. 更新 index.md 和主索引
- 结果: 所有页面均在200行以内, 内容清洁度提升

## [2026-05-26] create | 天味家园B栋MES详细设计方案
- 来源: /tmp/tianwei_extracted/ f001~f013.docx.txt（13份详细设计文档）
- 新建概念页: concepts/tianwei-mes-detailed-design.md（17,496 bytes）
- 内容组织: 按三大模块共13个子模块，每模块含功能概述/业务流程/关键规则
  - 生产执行（6个）：大料配料、大料预处理、小料预处理、炒料炒制、内外包装、返工品拆解
  - 基础配置（6个）：工艺配方单、工单管理、委外物料配置、工序产品配置、返工品投料配置、小料干料配料方式
  - 车间备料（1个）：自动备料/手工备料/审核流程
- 脱敏处理: 博依特 → [已脱敏]
- 交叉引用: 4个wikilink（smart-manufacturing, smart-factory-planning, detail-design-specification, isa-95-integration）
- 标签: [mes, smart-manufacturing, architecture]
- 更新: index.md（新增条目，总页面数109→110）

## [2026-05-26] create | 天味家园B栋MES测试方案
- 来源: /tmp/tianwei_extracted/ f040.docx.txt（UAT测试方案, 188行）、f041.docx.txt（炒锅联调测试方案, 91行）
- 新建概念页: concepts/tianwei-mes-testing.md（~11,000 bytes）
- 内容组织:
  - UAT测试方案: 测试目标/测试规划/测试准备/测试计划与人员/测试步骤（13步）/测试用数据/问题清单管控/测试结论
  - 炒锅联调测试方案: 联调范围/测试准备/测试步骤（8步）/3个特殊场景验证/测试结果记录
  - 对比总结表: UAT vs 炒锅联调六大维度对比
- 脱敏处理: 博依特 → [已脱敏]
- 交叉引用: 3个wikilink（tianwei-mes-project-overview, tianwei-mes-detailed-design, tianwei-mes-interface-integration）
- 标签: [mes, testing, quality]
- 更新: index.md（新增条目，总页面数110→111）

## [2026-05-26] create | 天味家园B栋MES上线策略
- 来源: /tmp/tianwei_extracted/ f036~f039.doc.txt（4份上线策略报告，版本I/II/III/V1.6）
- 新建概念页: concepts/tianwei-mes-go-live-strategy.md（~10,789 bytes）
- 内容组织:
  - 上线策略总述: 单机上线 vs SAP联调上线的路径选择与迭代
  - 上线范围与版本演进: V1.0(9月30日)→V2.0(10月30日)→V2.1(10月30日)→V1.6(11月17日)
  - 关键风险与应对: 7大风险（临时工、油污操作、基础数据、炒锅通讯、打印机、SAP对接、合并计量）+ 灾备方案
  - 上线步骤与时间表: 分步联机上线策略（11/17~12/05）、准备时间线、培训计划
- 脱敏处理: 博依特 → [已脱敏]，移除所有公司/人名
- 交叉引用: 4个wikilink（tianwei-mes-project-overview, mes-risk-management, mes-implementation-phases, tianwei-mes-functional-design）
- 标签: [mes, process-management, best-practice]
- 更新: index.md（新增条目，总页面数111→112）

## [2026-05-26] create | 天味家园B栋MES会议纪要
- 来源: /tmp/tianwei_extracted/ f015~f030.docx.txt（16份会议纪要）+ f046.pdf.txt（6月度汇报）
- 新建概念页: concepts/tianwei-mes-meeting-minutes.md（14,658 bytes）
- 内容组织: 按会议类型分为7大类，组内按时间排列
  - 项目月度汇报（0630×2）
  - 详设评审会（0703~0706，共4天）
  - 部署/方案评审会（0707×2）
  - UI评审（0711小料UI、0714 UI）
  - 内部盘点（0712）
  - 接口/SAP集成（0718接口边界、0725 SAP方向、0726 BOM业务）
  - 项目推进（0920×2）
- 每场会议含：日期、主题、关键决策、待办事项
- 附时间线总览表
- 脱敏处理: 所有人名 → [已脱敏]，公司名移除
- 交叉引用: 5个wikilink（tianwei-mes-project-overview, tianwei-mes-detailed-design, tianwei-mes-interface-integration, smart-manufacturing, consensus-management）
- 标签: [mes, documentation]
- 更新: index.md（新增条目）

## 2026-05-26 天味家园B栋MES项目文件入库

### 操作
批量入库天味家园B栋MES项目核心文件，从 D:\前归档\交付\天味家园B栋 目录提取。

### 处理文件
47个核心文件（详设评审15 + 会议纪要16 + 接口说明5 + 上线策略4 + 测试方案2 + 培训材料2 + 部署文档1 + 验收报告1 + PDF 2）

### 新建页面（已合并为4个）
- [[concepts/tianwei-mes-project|天味家园B栋MES项目]] — 项目概览
- [[concepts/tianwei-mes-production-flow|天味MES-生产流程与业务规则]] — 详细设计方案（13个功能模块）+ 上线策略 + 测试方案
- [[concepts/tianwei-mes-integration-delivery|天味MES-系统集成与交付]] — 接口集成方案 + 培训与系统部署
- [[concepts/tianwei-mes-chronicle|天味MES-项目纪事]] — 会议纪要（16次会议）

### 跳过文件
图片(.jpg/.png)、视频(无)、.rar压缩包、.vsdx流程图、.xmind思维导图、重复版本文件、日报(53个)、周报(61个)均按计划跳过

### 原始文件
47个raw articles保存至 wiki/raw/articles/tianwei-mes-*.md

### 脱敏处理
所有公司名称（博依特等）已替换为[已脱敏]，人员姓名已替换为[已脱敏]


## 2026-06-03 — 通威农发SVN项目文档编订（Phase 1：前期资料）

**操作**：从Windows SVN目录 `D:\赛意交付\通威\SVN\01工作区\00前期资料` 提取关键文档，创建3个Wiki页面

**创建页面**：
1. `通威农发/通威农发-项目总览.md` — 项目全景概览（战略背景/目标/67家公司范围/9大业务模块/12+系统集成/文档编码体系）
2. `通威农发/项目管理/通威农发-项目治理.md` — 项目治理体系（章程/SOW/7层组织架构/滚动计划/3类会议/34份受控文档/人员管理/验收标准）
3. `通威农发/业务蓝图/通威农发-业务调研.md` — 6大业务域调研汇总（计划管理3流程/生产管理10流程/设备管理13流程+质量/仓库/EBS待补充）

**更新页面**：
- `index.md` — 通威农发项目section新增3个项目交付文档链接，重组为"项目交付文档"+"数据库与技术"两组

**数据源**：
- TWAD_IF_103_项目章程_v1.0.docx（2024-01-09）
- 通威农发智能工厂生产业务平台项目工作说明书-终稿（SOW，2023-12-22）
- TWAD_IF_107.PLN_调研报告.计划管理_V1.0_20231206.docx
- TWAD_IF_107.PRO_调研报告.生产管理_V1.0_20231206.docx
- TWAD_IF_107.EAM_调研报告.设备管理_V1.0_20231214.docx

**待办**：
- 读取剩余3份调研报告（质量/仓库/EBS解耦），补充业务调研Wiki
- Phase 2：01通威项目-跟WPS同步/10实施管理/20规划设计（蓝图方案）
- Phase 3：06项目方案/06.5开发管理
- Phase 4：07系统测试/08上线文档/11项目验收
- Phase 5：15培训文档/16操作手册/10系统运维
- Phase 6：09项目管理/12项目总结/13外围系统

## 2026-06-03 — 通威农发SVN项目文档编订（Phase 1补充：仓库+EBS解耦）

**操作**：读取剩余2份调研报告，补充业务调研Wiki页面

**更新页面**：
- `通威农发/业务蓝图/通威农发-业务调研.md` — 补充仓库管理14流程（CK001-CK014）+ EBS解耦11流程（ERP01-ERP11）+ 主数据管理现状 + 生产完工入库关键流程 + EBS解耦优化需求

**数据源**：
- TWAD_IF_107.INV_调研报告.仓库管理_V1.0_20231207.docx
- TWAD_IF_107.ERP_调研报告.EBS解耦_V1.0_20231214.docx

**待办**：
- 质量管理调研（QA报告23MB，文件较大，待处理）
- Phase 2：蓝图方案
- 2026-06-03: 创建 [[通威农发/业务蓝图/蓝图方案-仓储与EBS集成]] — 从物资管理V1.0和EBS集成V0.1蓝图文档提取，覆盖26个MA子流程和55个EBS解耦接口
- 2026-06-04: 创建 [[通威农发/详细设计/详细设计-功能设计]] — 从8份详细设计源文件提取，覆盖生产执行（人员/班制/任务/批组/交接班共20+功能）、仓储4功能（定包接收/散装销售/紧急放行/采购退货）、EBS改造（16项改造+销售提货计划）、开发规范（通用/代码/数据库/平台/单元测试/版本管理）
- 2026-06-04: 创建 [[通威农发/详细设计/详细设计-接口总览]] — 从8份接口文档提取，7个业务组160个系统接口摘要级总览（计划组22/生产组46/质量组24/设备组13/仓储组46/配方组7/公共查询2），含接口汇总统计表和相关页面链接

### 2026-06-04 09:07
- **操作**：新建页面
- **页面**：[[通威农发/详细设计/EBS接口详表]]
- **来源**：EBS_接口卡.md (194KB) + EBS_接口服务文档.md (820KB) + EBS_技术接口文档.md (138KB)
- **摘要**：汇总EBS与DIM/一点通/智链通全部76个接口，按主数据(12)/采购(7)/生产(14)/库存(17)/销售(19)/成本(7)六大域分组，含接口卡片汇总表、关键请求/响应字段、统计概览。已脱敏。
- **相关**：更新 index.md

### 2026-06-04 10:30
- **操作**：新建页面
- **页面**：[[通威农发/测试施工/测试与施工]]
- **来源**：EBS_基础数据.md + EBS_库存杂项.md + EBS_配方生产批.md + EBS_采购结算.md + EBS_销售发运.md + 无人过磅施工方案V1.1.md + MES硬件清单.md + 37个TWAD_IF_307_EBS接口测试报告
- **摘要**：汇总测试验收阶段全部文档：EBS功能测试5个拉通流程验证结果（基础数据/库存杂项/配方生产批/采购结算7场景/销售发运2类型）、37个EBS接口Postman测试汇总表（33个通过+4个部分通过，总通过率89.2%）、无人过磅施工方案（设备布局+安装要求+20项设备清单+实施计划）、MES硬件清单（重庆37项+揭阳26项部署任务）。已脱敏。376行/18KB。
- **相关**：更新 index.md

### 2026-06-04 09:41
- **操作**：新建页面
- **页面**：[[通威农发/项目管理/通威农发-项目管理]]
- **来源**：双周计划-W22.md (297K) + 日计划-20240220.md (255K) + 周例会会议纪要.md (2K) + 业务域依赖关系.md (12K) + 流程角色清单.md (7K)
- **摘要**：从5类项目管理文档提取方法论与模式，含5大H2章节：项目计划体系（WBS功能分解150+功能项+接口分解190+条+双周滚动W05→W22共18轮迭代的阶段演进）+ 日常管理（日计划偏差记录+问题跟踪看板20+条典型问题闭环+健康度评估高风险项）+ 会议机制（双周例会8项跟进事项）+ 业务域依赖关系（跨域依赖矩阵+核心依赖链+依赖方向模式）+ 角色与流程（6域111支流程+交叉角色映射+标准化实践），末尾提炼项目管理方法论（计划3层递进+协调3法+风险5类对策）。全部脱敏去除人名（替换为岗位）。291行/13.8KB。
- **相关**：更新 index.md

## 2026-06-04 — 通威农发Wiki知识结构重编

**操作类型**：结构重组

**背景**：通威农发项目的50个Wiki页面散落在5个不同目录（databases/、integrations/、entities/、concepts/、kpi/），与本次新编的12个SVN交付页面无法形成统一知识体系。

**操作内容**：
1. 方案B彻底重编：所有通威相关页面迁入 `通威农发/` 子目录
2. 按8个知识维度重组：项目管理、业务蓝图、详细设计、测试施工、技术架构、EBS-DIM接口、KPI指标、行业知识
3. 全局wikilink修复：221处wikilink替换 + 14处markdown链接修复 + 11处断链修复
4. index.md重写：合并通威农发section（原散落在4个section），移除数据库section（20条归入通威）
5. 清理空目录：databases/、integrations/ebs-dim/、kpi/ 等

**迁移映射**：
- databases/ (20页) → 通威农发/技术架构/
- integrations/ebs-dim/ (8页) → 通威农发/技术架构/ebs-dim/
- entities/ (3页) → 通威农发/行业知识/ (2) + 通威农发/技术架构/ (1)
- concepts/ (2页) → 通威农发/行业知识/
- kpi/ (5页) → 通威农发/KPI指标/
- SVN交付 (11页) → 对应子目录（项目总览保留根目录）

**最终结构**（50个页面，共757KB）：
- 通威农发/通威农发-项目总览.md (枢纽页)
- 通威农发/项目管理/ (2页)
- 通威农发/业务蓝图/ (5页)
- 通威农发/详细设计/ (3页)
- 通威农发/测试施工/ (1页)
- 通威农发/技术架构/ (21页) + ebs-dim/ (8页)
- 通威农发/KPI指标/ (5页)
- 通威农发/行业知识/ (4页)

**验证结果**：零断链，所有wikilink指向的文件均存在

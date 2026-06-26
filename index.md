---
created: '2026-05-27'
project: 通用
tags:
- mes
- digital-transformation
- index
title: Wiki 索引
type: reference
updated: '2026-06-26'
status: published
description: 'Wiki内容索引，按类型组织所有页面'
author: Hermes Wiki Agent
version: '1.0.0'
---


# Wiki 索引

> 内容目录。每个 wiki 页面按类型列出，附一行摘要。
> 查询时先读此文件找到相关页面。
> 最后更新：2026-06-26 | 总页面数：350+

## 通威农发项目

> **项目：通威农发**（通威股份农业发展有限公司）
> 智能工厂生产业务平台项目，覆盖67家饲料分子公司，9大业务模块，12+外围系统集成
> 共50个Wiki页面，按项目阶段+知识维度组织

**项目总览**
- [[通威农发/通威农发-项目总览|项目总览]] — 战略背景/目标/范围/9大模块/系统集成/实施阶段

**项目管理**
- [[通威农发/项目管理/通威农发-项目治理|项目治理]] — 项目章程/SOW/组织架构/计划管理/沟通管理/文档管理/验收标准
- [[通威农发/项目管理/通威农发-项目管理|项目管理]] — WBS分解+双周滚动18轮迭代+日计划偏差跟踪+问题看板+跨域依赖矩阵

**业务蓝图**
- [[通威农发/业务蓝图/通威农发-业务调研|业务调研]] — 6大业务域调研报告（计划/生产/设备/质量/仓库/EBS解耦）
- [[通威农发/业务蓝图/蓝图方案-计划生产配方|蓝图：计划生产配方]] — 计划管理+生产管理+配方管理+施耐德工厂MES蓝图
- [[通威农发/业务蓝图/蓝图方案-质量管理|蓝图：质量管理]] — 来料/过程/成品检验+留样管理+质量追溯蓝图
- [[通威农发/业务蓝图/蓝图方案-设备管理|蓝图：设备管理]] — 设备全生命周期+点巡检维保+SCADA监控蓝图
- [[通威农发/业务蓝图/蓝图方案-仓储与EBS集成|蓝图：仓储与EBS集成]] — 仓储全流程+EBS业务解耦+无人过磅蓝图

**详细设计**
- [[通威农发/详细设计/详细设计-功能设计|功能设计]] — 生产执行+仓储4功能+EBS改造+开发规范
- [[通威农发/详细设计/详细设计-接口总览|接口总览]] — 7个业务组160个系统接口
- [[通威农发/详细设计/EBS接口详表|EBS接口详表]] — EBS与DIM/一点通76个接口完整定义，按6大业务域分组

**测试与施工**
- [[通威农发/测试施工/测试与施工|测试与施工]] — EBS功能测试+接口测试(37个Postman)+无人过磅施工方案+MES硬件清单

**数据库结构**（1,572张核心业务表，19个模块）
- [[通威农发/技术架构/通威农发-数据库总览|数据库总览]] — 全库结构总览，19模块索引
- [[通威农发/技术架构/通威农发-公共与基础模块|公共与基础模块]] — Common/RBAC/工作流/国际化/多租户，127张表
- [[通威农发/技术架构/通威农发-报表预处理中间表|报表预处理中间表]] — ST+LM_ST统计中间表+FineReport配置，84张表
- [[通威农发/技术架构/通威农发-技术参数与其他|技术参数与其他]] — 技术参数/报表/流程/数据交换，90张表
- [[通威农发/技术架构/通威农发-LM精益管理|LM精益管理]] — 8D问题解决/安环/标准化，154张表
- [[通威农发/技术架构/通威农发-WMS仓储管理|WMS仓储管理]] — 入库/出库/库存/拣货/盘点，167张表
- [[通威农发/技术架构/通威农发-MES生产执行|MES生产执行]] — 配料/工单/报工/清洗/打包，158张表
- [[通威农发/技术架构/通威农发-QMS质量管理|QMS质量管理]] — 检验/质检/不合格品/追溯，120张表
- [[通威农发/技术架构/通威农发-EDO设备管理|EDO设备管理]] — 设备全生命周期/维保/故障，119张表
- [[通威农发/技术架构/通威农发-IIoT工业物联网|IIoT工业物联网]] — 设备数据采集/监控，76张表
- [[通威农发/技术架构/通威农发-产能利用率|产能利用率]] — 产能分析相关数据表，201张表
- [[通威农发/技术架构/通威农发-基础数据与主数据|基础数据与主数据]] — 物料/包装/配件/资源/客商等，53张表
- [[通威农发/技术架构/通威农发-MBM物料BOM与配方|MBM物料BOM与配方]] — 物料BOM与配方管理，36张表
- [[通威农发/技术架构/通威农发-APS计划排程|APS计划排程]] — 高级计划排程，35张表
- [[通威农发/技术架构/通威农发-MI制造智能|MI制造智能]] — 预警/测点/数据填报/IDA，38张表
- [[通威农发/技术架构/通威农发-E2D与数据同步|E2D与数据同步]] — EBS与外围系统数据交换，28张表
- [[通威农发/技术架构/通威农发-Measure计量管理|Measure计量管理]] — 称重/计量/校准，25张表
- [[通威农发/技术架构/通威农发-物流执行LES与WHM|物流执行LES与WHM]] — 物流执行与仓库辅助，19张表
- [[通威农发/技术架构/通威农发-资产管理EAM与设备|资产管理EAM与设备]] — 资产管理与设备维护，15张表
- [[通威农发/技术架构/通威农发-其他小模块|其他小模块]] — 小型功能模块汇总，61张表

**EBS-DIM接口**（83个系统间接口）
- [[通威农发/技术架构/ebs-dim/README|EBS-DIM接口总览]] — 接口架构与分组索引
- [[通威农发/技术架构/ebs-dim/采购管理|采购管理接口]] — 采购申请/订单/退货接口
- [[通威农发/技术架构/ebs-dim/生产管理|生产管理接口]] — 工单/报工/领料/退料接口
- [[通威农发/技术架构/ebs-dim/仓储库存|仓储库存接口]] — 入库/出库/调拨/盘点接口
- [[通威农发/技术架构/ebs-dim/销售管理|销售管理接口]] — 销售订单/发货/退货接口
- [[通威农发/技术架构/ebs-dim/成本财务|成本财务接口]] — 成本核算/凭证/总账接口
- [[通威农发/技术架构/ebs-dim/过磅管理|过磅管理接口]] — 称重/过磅/回皮接口
- [[通威农发/技术架构/ebs-dim/批次质量|批次质量接口]] — 批次/质检/留样接口

**KPI指标体系**（167个运营指标）
- [[通威农发/KPI指标/README|指标体系总览]] — 指标分类与计算公式索引
- [[通威农发/KPI指标/内部管理指标|内部管理指标]] — 生产效率/设备OEE/质量合格率等核心运营指标
- [[通威农发/KPI指标/财务指标|财务指标]] — 成本/收入/利润/资金等财务指标
- [[通威农发/KPI指标/客户指标|客户指标]] — 交付率/满意度/投诉率等客户指标
- [[通威农发/KPI指标/员工发展指标|员工发展指标]] — 培训/安全/离职率等人员指标

**行业知识与工具**
- [[通威农发/行业知识/饲料行业知识|饲料行业知识]] — 工艺/配方/仓储/质量/设备管理完整体系
- [[通威农发/行业知识/饲料行业解决方案|饲料行业解决方案]] — 六大模块业务蓝图与数字化升级策略
- [[通威农发/行业知识/蓝图编写方法论|蓝图编写方法论]] — 企业智能制造蓝图解决方案编写方法论
- [[通威农发/行业知识/饲料-通威知识映射|饲料-通威知识映射]] — 行业知识↔项目模块↔数据库三层映射
- [[通威农发/技术架构/CPT报表分析|CPT报表分析]] — 30张CPT绩效报表分析经验与指标编码体系

## 久立特材项目

> **项目：久立特材**（浙江久立特材科技股份有限公司）
> 数字化制造平台（MES）四期实施项目，按功能模块组织知识体系

- [[久立项目/久立项目-项目总览]] — 项目分期、系统架构、PPF功能模块体系、覆盖厂区
- [[久立项目/久立项目-蓝图方案]] — 按功能模块（工艺/执行/仓储/质量）组织的各期蓝图设计
- [[久立项目/久立项目-业务调研]] — 调研纪要+报告+痛点需求（按业务领域合并去重）
- [[久立项目/久立项目-系统接口]] — MES↔SAP/OA接口技术规范
- [[久立项目/久立项目-操作手册]] — IPC/PC/PDA端操作指南（按终端分类）
- [[久立项目/久立项目-项目治理]] — 项目章程、范围定义、里程碑确认报告
- [[久立项目/久立项目-功能设计说明书]] — MES/WMS/QMS三大模块366个功能点的详细设计文档
- [[久立项目/久立项目-功能清单与开发计划]] — 按建设阶段列出的功能开发优先级、排期和分工
- [[久立项目/久立项目-技术架构]] — 系统环境部署、数据库设计、Greenplum数据仓库、开发规范
- [[久立项目/久立项目-测试体系]] — 单元/集成/UAT测试计划与问题跟踪，覆盖一/三/四期

## DAMA-DMBOK2 数据管理知识体系

> **DAMA-DMBOK2（原书第2版修订版）** — 国际数据管理协会（DAMA International）发布的全球最权威数据管理知识体系框架
> 涵盖全部17个知识领域，共18个Wiki页面

**框架总览**
- [[DAMA-DMBOK2/00-框架总览]] — DAMA框架总览：DAMA车轮、DMBOK金字塔、战略一致性模型、10项数据管理原则、CDMP认证体系

**参考工具**
- [[DAMA-DMBOK2/术语表]] — DAMA-DMBOK2专业术语表（中英对照+缩写+定义，120+术语，按字母和知识领域分组）
- [[DAMA-DMBOK2/精读笔记/00-精读笔记索引]] — 全书精读笔记索引（每章3000字精炼摘要+学习路径建议）
- [[DAMA-DMBOK2/工具箱/成熟度自评模板]] — 数据管理成熟度自评模板（12领域×5级，含评分汇总和改进优先级矩阵）
- [[DAMA-DMBOK2/工具箱/数据治理实施检查清单]] — 数据治理4阶段实施检查清单（启动→制度→试点→推广）
- [[DAMA-DMBOK2/工具箱/数据管理工具选型指南]] — 按知识领域的工具选型参考（6大领域，代表产品+评估维度）

**核心知识领域（1-13）**
- [[DAMA-DMBOK2/01-数据管理]] — 总纲：定义、原则、框架、业务驱动因素、数据管理挑战
- [[DAMA-DMBOK2/02-数据处理伦理]] — 数据伦理原则、隐私法律合规、在线伦理环境、伦理文化
- [[DAMA-DMBOK2/03-数据治理]] — 数据治理定义、制度标准、FAIR原则、治理委员会、CDO角色
- [[DAMA-DMBOK2/04-数据架构]] — 数据架构定义、企业架构关系、架构框架(Zachman/TOGAF)、数据流
- [[DAMA-DMBOK2/05-数据建模和设计]] — 概念/逻辑/物理模型、ER图、范式化、维度建模
- [[DAMA-DMBOK2/06-数据存储和运营]] — 数据库类型、存储架构、数据生命周期、备份恢复
- [[DAMA-DMBOK2/07-数据安全]] — 访问控制、加密脱敏、安全分类、威胁模型、ISO27001
- [[DAMA-DMBOK2/08-数据集成和互操作]] — ETL/ELT、数据虚拟化、消息队列、API、语义互操作
- [[DAMA-DMBOK2/09-文档和内容管理]] — ECMS、非结构化数据、文档生命周期、知识管理
- [[DAMA-DMBOK2/10-参考数据和主数据管理]] — MDM架构、黄金记录、数据实体解析、数据匹配合并
- [[DAMA-DMBOK2/11-数据仓库和商务智能]] — 多维建模、星型/雪花型、Kimball/Inmon方法论、OLAP
- [[DAMA-DMBOK2/12-元数据管理]] — 技术/业务/操作元数据、数据目录、数据血缘、影响分析
- [[DAMA-DMBOK2/13-数据质量管理]] — 质量维度、数据剖析、PDCA持续改进、DQI指标

**支撑知识领域（14-17）**
- [[DAMA-DMBOK2/14-大数据和数据科学]] — 大数据5V、数据湖、Lambda/Kappa架构、CRISP-DM
- [[DAMA-DMBOK2/15-数据管理成熟度评估]] — CMMI/DCAM/DMM模型对比、评估实施流程
- [[DAMA-DMBOK2/16-数据管理组织和角色期望]] — CDO角色、数据团队模型、数据职业路径
- [[DAMA-DMBOK2/17-数据管理和组织变革管理]] — ADKAR模型、Kotter8步法、变革实施流程

## 培训

> **项目：培训归档** | 内部培训资料整理

- [[培训/培训-总览]] — 培训资料总索引（80个文件，含售前调研、课件、表格等）
- [[培训/培训-WMS与MES测试方法论]] — WMS/MES用户验收测试方法论：场景化测试设计、数据集成要点
- [[培训/培训-售前调研与行业报告]] — 售前调研纪要、行业知识讲义、技术趋势报告
- [[培训/培训-实施方法论与课件体系]] — 实施方法论课件、培训课程体系、签到表模板
- [[培训/培训-数字化转型周读-第一周]] — 从工具革命到决策革命：智能制造转型之路
- [[培训/培训-数字化转型周读-第二周]] — 德国工业4.0、美国AMP、中国制造2025对比研究
- [[培训/培训-数字化转型周读-第三至六周]] — 制造业数字化转型案例集与学习方法论
- [[培训/培训-数据分析入门]] — 数据分析方法、业务数据案例、图表选型指南
- [[培训/培训-欧软云MES产品介绍]] — 面向零散制造行业的云MES系统产品介绍
- [[培训/培训-管件原材料检验功能说明书]] — 管件原材料检验全流程信息化管理功能设计
- [[培训/培训-精益生产-标准化工作手册]] — 丰田TPS标准化工作理论框架与TWI核心技能
- [[培训/培训-金蝶Cloud同步对照表]] — ERP与WMS数据同步字段映射关系
- [[培训/功能设计快速上手培训]] — 从业务需求到功能设计的5步快速上手培训
- [[培训/培训-飞书Aily智能体平台]] — 飞书Aily企业级AI智能体平台：产品矩阵、选型、MCP集成、7个业务案例

## 实体
- [[entities/fine-report-cpt|fine-report-cpt]] — 帆软 FineReport CPT 报表模板文件，XML 结构、属性、单位系统与修改模式
- [[entities/popular-web-design-templates|popular-web-design-templates]] — 54种真实网站设计模板，含 AI/开发工具/基础设施/设计/金融/企业类
- [[entities/document-processing-tools|document-processing-tools]] — 文档处理工具汇总：Excel/PDF/Word/PPT，OfficeCLI一站式处理
- [[entities/hermes-agent|hermes-agent]] — CLI AI Agent 平台，支持技能系统、多平台网关、子代理、语音交互
- [[entities/powerpoint-presentation-processing|powerpoint-presentation-processing]] — 使用 python-pptx 创建和编辑 PowerPoint 演示文稿
- [[concepts/apqc-process-metrics|apqc-process-metrics]] — APQC 流程绩效指标库：跨企业流程的标准化度量指标体系


## 概念
- [[concepts/tianwei-mes-project|tianwei-mes-project]] — 天味家园B栋MES项目入口：概述、时间线、功能矩阵、重大决策
- [[concepts/tianwei-mes-production-flow|tianwei-mes-production-flow]] — 天味MES生产流程与业务规则：一颗火锅底料的完整旅程
- [[concepts/tianwei-mes-integration-delivery|tianwei-mes-integration-delivery]] — 天味MES系统集成与交付：WMS/SAP接口、上线策略、测试、部署
- [[concepts/tianwei-mes-chronicle|tianwei-mes-chronicle]] — 天味MES项目纪事：16场会议时间线与关键决策
- [[concepts/html-prototype-generation|html-prototype-generation]] — Apple Design Language 产品原型 HTML 生成，Web+Mobile 布局与功能说明面板
- [[concepts/frontend-design-system|frontend-design-system]] — 前端设计方法论，避免 AI 泛风格，追求有意图的设计方向
- [[concepts/retro-futuristic-html-design|retro-futuristic-html-design]] — CRT 终端 × 太空仪表盘设计系统，琥珀/青色霓虹美学
- [[concepts/frontend-slides-presentation|frontend-slides-presentation]] — 零依赖 HTML 演示文稿生成，100vh 适配与动画丰富
- [[concepts/claude-api-development|claude-api-development]] — 使用 Anthropic SDK 构建 Claude API 应用的最佳实践
- [[concepts/mcp-server-development|mcp-server-development]] — Model Context Protocol 服务器开发指南
- [[concepts/ai-engineering-from-scratch|ai-engineering-from-scratch]] — 开源AI工程课程：503课/20阶段/4语言，从线性代数到Agent集群的端到端学习路径，产出388个Skills+99个Prompts
- [[concepts/systematic-debugging|systematic-debugging]] — 4阶段根因分析方法论：问题复现、假设验证、根因定位、修复验证
- [[concepts/test-driven-development|test-driven-development]] — RED-GREEN-REFACTOR 循环的 TDD 实践
- [[concepts/writing-plans|writing-plans]] — 创建全面的实现计划，包含小任务、精确文件路径和完整代码示例
- [[concepts/requesting-code-review|requesting-code-review]] — 提交前验证管道：静态扫描、质量门禁、独立审查、自动修复循环
- [[concepts/plan-mode|plan-mode]] — Hermes Agent 的计划模式，检查上下文并创建 markdown 计划
- [[concepts/procurement-management|procurement-management]] — 采购管理：核心职能、采购模式演进、采购流程、采购分类、ERP集成
- [[concepts/skill-creator|skill-creator]] — 创建、修改、优化 Hermes Agent 技能的指南
- [[concepts/doc-coauthoring|doc-coauthoring]] — 结构化文档协作工作流，高效转移上下文、迭代优化内容
- [[concepts/big-data-governance|big-data-governance]] — 大数据治理：全链路平台/数据湖/Flink流批一体/Atlas元数据管理/成本治理/模型治理
- [[concepts/smart-manufacturing|smart-manufacturing]] — 智能制造：数据+算力+算法驱动，从工具革命到决策革命
- [[concepts/smart-factory-planning|smart-factory-planning]] — 智能工厂规划：MES 15大模块、五大层次、行业案例与交付保障
- [[concepts/sie-iidp-design-style|sie-iidp-design-style]] — SIE-IIDP 工业互联网平台设计风格：#AC2A48、2px极小圆角、功能主义美学、100px根字号rem体系
- [[concepts/manufacturing-digital-policy|manufacturing-digital-policy]] — 制造业数字化转型政策：美/欧/德/日/东盟政策对比
- [[concepts/data-visualization-selection|data-visualization-selection]] — 数据可视化选型：比较/联系/分布/构成四类图表选择指南
- [[concepts/consensus-management|consensus-management]] — 共识管理：书面/口头共识分类、层级选择、固化与范围演进
- [[concepts/harness-engineering|harness-engineering]] — AI Agent 驾驭层工程方法论：五层架构（Tool/Prompt/Permission/Orchestration/Memory）
- [[concepts/text2kpi-optimization|text2kpi-optimization]] — Text2KPI NL2API 系统：V1六项优化方案 + V2四层架构/五步Pipeline/查询编排/推理可观测
- [[concepts/nl2sql-precise-mapping|nl2sql-precise-mapping]] — NL2SQL 六层受约束架构：Schema映射→意图分类→SQL生成→自校验→护栏→执行
- [[concepts/text2kpi-reference-code|text2kpi-reference-code]] — Text2KPI 核心参考代码节选：7段体现方法论的实现片段（Python+Java+YAML）
- [[concepts/text2kpi-prompt-and-config|text2kpi-prompt-and-config]] — Text2KPI Prompt分层模板与工程化配置清单：8个模板/清单
- [[concepts/sme-digital-innovation|sme-digital-innovation]] — 中小企业数字化模式创新：业务/管理/技术三维创新路径与服务商生态
- [[concepts/manufacturing-kpi-system|manufacturing-kpi-system]] — 制造业数据指标体系：搭建方法论（指标金字塔/四大步骤/指标字典）+六大类业务KPI详细参考
- [[concepts/metric-platform-construction|metric-platform-construction]] — 指标中台建设方法与实践：需求驱动vs数据驱动、指标PDCA闭环、产品功能/技术架构
- [[concepts/efficiency-improvement-methods|efficiency-improvement-methods]] — 效率与效率改善方法：OPE架构、精益改善十大精神、效率损失结构
- [[concepts/value-stream-mapping|value-stream-mapping]] — 价值流图VSM：绘制现状/未来价值流图、增值比分析与改善框架
- [[concepts/big-data-development-basics|big-data-development-basics]] — 企业级大数据技术体系：六层技术框架、Hadoop/Spark技术栈、HDFS分布式文件系统
- [[concepts/data-mid-platform|data-mid-platform]] — 数据中台解决方案：全链路数据集成/存储/计算/治理/服务一体化平台架构
- [[concepts/digital-twin|digital-twin]] — 数字孪生技术：物理空间与数字空间交互映射的通用技术架构与应用场景
- [[concepts/data-asset-management-standard|data-asset-management-standard]] — 数据资产管理标准化：数据资源→资产→资本的转化路径与标准体系
- [[concepts/data-element-valuation|data-element-valuation]] — 数据要素价值评估：市场/社会双视角的数据价值评估方法论
- [[concepts/data-security-governance|data-security-governance]] — 数据安全治理：全生命周期数据安全防护体系与流程
- [[concepts/enterprise-info-flow-planning|enterprise-info-flow-planning]] — 企业信息流规划：信源/信道/信宿四要素方法论与重组方案
- [[concepts/enterprise-architecture-planning|enterprise-architecture-planning]] — 企业架构与信息化规划：业务架构/IT架构/实施落地三部分
- [[concepts/isa-95-integration|isa-95-integration]] — ISA-95企业控制系统集成：Purdue层级模型与MES/ERP接口标准
- [[concepts/aps-advanced-planning-scheduling|aps-advanced-planning-scheduling]] — APS高级计划与排程：物料+能力双重约束下的生产计划优化
- [[concepts/data-governance-two-phase|data-governance-two-phase]] — 数据治理两阶段实践：从数据清洁到数据服务化的演进路径
- [[concepts/logistics-transport-solution|logistics-transport-solution]] — 物流与运输解决方案：基于RTLS实时定位的供应链可视化
- [[concepts/detail-design-specification|detail-design-specification]] — 详细设计文档编写规范：功能描述7要素模板、三区字段定义、审批流/定时任务/多终端设计模式
- [[concepts/methodologies-overview|methodologies-overview]] — 方法论知识总览：企业架构、数字化转型、实施交付、咨询销售四大类别方法论体系汇编
- [[concepts/enterprise-it-planning-methodology|enterprise-it-planning-methodology]] — 企业架构与IT规划方法论：EA四视图（业务/信息/应用/技术架构）与IT规划四步法
- [[concepts/digital-transformation-methodology|digital-transformation-methodology]] — 数字化转型方法论：用友12367框架、数字化三段论、智能制造五步法
- [[concepts/implementation-methodology|implementation-methodology]] — 实施方法论：IPM五阶段、六步法、汉得中台实施方法论体系
- [[concepts/consulting-sales-methodology|consulting-sales-methodology]] — 咨询与销售方法论：麦肯锡七步法、金蝶售前四阶段、MEDDIC销售方法论
- [[concepts/飞书Aily-自定义智能体配置|飞书Aily自定义智能体配置]] — 飞书Aily自定义智能体创建全流程：Prompt设计、知识空间、MCP集成、技能编排、渠道发布


## 对比
- [[comparisons/html-generation-styles|html-generation-styles]] — 五种 HTML 生成风格横向对比：Apple/复古未来/通用/模板/演示

## 查询

- [[queries/natural-gas-processing/index]] — 天然气处理厂（Natural Gas Processing Plant）完整知识库：定义、工艺流程、设备、标准、行业现状
- [[queries/natural-gas-processing/00-工厂概述]] — 天然气处理厂定位、功能、分类与关键指标总览
- [[queries/natural-gas-processing/01-概述与定义]] — 天然气处理厂定义、分类、产品标准、安全环保
- [[queries/natural-gas-processing/02-工艺流程]] — 入口分离、脱硫脱碳、脱水、NGL回收、硫磺回收等全流程
- [[queries/natural-gas-processing/03-主要设备]] — 分离器、塔器、换热器、压缩机、膨胀机、脱水与硫磺回收设备
- [[queries/natural-gas-processing/04-行业标准]] — GB/SY中国标准、ISO/ASME/API/NACE/GPA国际标准
- [[queries/natural-gas-processing/05-行业现状]] — 全球与中国行业格局、主要企业（PetroChina/Sinopec/Shell等）、重大项目
- [[queries/natural-gas-processing/06-生产组织]] — 组织架构、岗位体系、倒班制度、设备管理、HSE管理、环保管理、信息化数字化
- [[queries/natural-gas-processing/07-质量管理]] — 质量管理体系、产品标准（GB 17820等）、在线监测、化验分析、不合格品管理、计量管理
- [[queries/natural-gas-processing/08-工艺流程详解]] — 天然气处理完整工艺路线详解：入口分离、胺法脱硫、TEG脱水、深冷NGL回收、Claus硫磺回收
- [[queries/industry-analysis/index]] — 行业分析总览（企业研究、行业格局、市场分析等深度研究产出）
- [[queries/industry-analysis/baijiu-industry-analysis]] — 酱香型白酒行业分析：市场格局、竞争阵营、周期复盘与发展趋势
- [[queries/飞书Aily-企业智能客服案例]] — 飞书Aily企业智能客服/AI情报/制造业巡检三个案例：完整Prompt+表结构+MCP+工作流+对话
- [[queries/飞书Aily-销售客户回款管理案例]] — 飞书Aily销售管理/客户管理/回款管理/一体化管理四个案例：完整Prompt+表结构+对话

## 制造业方案
- [[queries/manufacturing-solutions/index]] — 制造业数字化解决方案总览（109份行业方案，13个分类页面）
- [[queries/manufacturing-solutions/离散制造-注塑汽配机加工钣金]] — 注塑/汽配/机加工/钣金（14份）
- [[queries/manufacturing-solutions/离散制造-铸造新材料电梯钢铁]] — 铸造/新材料/电梯/钢铁（12份）
- [[queries/manufacturing-solutions/流程制造-化工行业]] — 化工行业（7份）
- [[queries/manufacturing-solutions/流程制造-光伏光纤光缆]] — 光伏/光纤光缆（5份）
- [[queries/manufacturing-solutions/消费与医疗行业方案]] — 医药/食品/酒类（6份）
- [[queries/manufacturing-solutions/汽车与交通行业方案]] — 汽车/ANDON/电子制造（10份）
- [[queries/manufacturing-solutions/智能制造-智能工厂规划]] — 智能工厂规划方法论（11份）
- [[queries/manufacturing-solutions/智能制造-产品方案体系]] — MES/QMS/APS产品体系（8份）
- [[queries/manufacturing-solutions/WMS仓储与SRM供应链]] — WMS/SRM方案（8份）
- [[queries/manufacturing-solutions/物联网与设备管理]] — IIoT/设备管理（8份）
- [[queries/manufacturing-solutions/数据与指标体系]] — 数据治理/指标体系（7份）
- [[queries/manufacturing-solutions/IT战略与数字化规划]] — IT战略/数字化升级（4份）
- [[queries/manufacturing-solutions/厂商与案例汇编]] — 厂商/案例汇编（9份）

## 售前方案集

> 整理自售前方案集（4,283个文件，34GB），42个结构化Wiki页面

- [[方案集/方案集知识库-总览]] — 方案集知识库总览：42个页面覆盖4129个有效文件

**系统与平台（B类）**
- [[方案集/B01-MES制造执行系统]] — MES基础知识、行业方案、产品对比（292文件）
- [[方案集/B02-ERP企业资源规划]] — ERP解决方案、SAP/Oracle产品体系（52文件）
- [[方案集/B03-PLM产品生命周期]] — PLM系统方案与产品选型（41文件）
- [[方案集/B04-WMS仓储物流]] — WMS仓储、智慧物流、自动化立体仓库方案
- [[方案集/B05-APS计划排程]] — APS高级排程与生产计划优化（44文件）
- [[方案集/B06-QMS质量管理]] — QMS/LIMS/SPC/TQM质量管理方案集
- [[方案集/B07-CRM与营销]] — CRM客户管理与数字化营销方案
- [[方案集/B08-数据治理与BI]] — 数据治理、BI、数据仓库、主数据管理（89文件）
- [[方案集/B09-IT架构与中台]] — 企业IT架构、中台战略、微服务架构
- [[方案集/B10-数字孪生]] — 数字孪生技术方案与应用案例（44文件）
- [[方案集/B11-5G与物联网]] — 5G技术、IIoT工业物联网、边缘计算（137文件）
- [[方案集/B12-自动化与机器人]] — 工业机器人、AGV、DCS、PLC/SCADA方案（138文件）
- [[方案集/B13-网络安全与工控]] — 工控安全、网络安全防护方案（45文件）
- [[方案集/B14-CADCAMCAE仿真]] — CAD/CAM/CAE仿真、工厂仿真、增材制造
- [[方案集/B15-数字化转型方法论]] — 数字化转型方法论与战略规划（338文件）
- [[方案集/B16-智能制造与智能工厂]] — 智能制造体系、智能工厂规划（605文件）
- [[方案集/B17-工业互联网]] — 工业互联网平台、边缘计算、标识解析（99文件）
- [[方案集/B18-精益生产]] — 精益生产方法论与实践案例（45文件）

**行业方案（C类）**
- [[方案集/C01-汽车行业]] — 整车/零部件/新能源/智能网联方案
- [[方案集/C02-电子半导体]] — SMT/PCB/半导体/显示面板方案（63文件）
- [[方案集/C03-食品饮料]] — 乳制品/白酒/快消品数字化方案（20文件）
- [[方案集/C04-医药医疗器械]] — 医药制造/医疗器械MES/ERP实施案例
- [[方案集/C05-化工行业]] — 炼油石化/化工数字化/安全管控方案（128文件）
- [[方案集/C06-钢铁冶金]] — 钢铁冶金行业智能制造方案（16文件）
- [[方案集/C07-能源电力]] — 能源数字化转型、电力企业管理方案（78文件）
- [[方案集/C08-航空航天军工]] — 航空航天/军工数字化方案（20文件）
- [[方案集/C09-矿山矿业]] — 数字矿山/智能矿山/无人驾驶方案（16文件）
- [[方案集/C10-建材家居]] — 定制家具/智能家居/水泥制造方案（27文件）
- [[方案集/C11-新能源电池]] — 新能源电池行业数字化方案（37文件）
- [[方案集/C12-零售与消费品]] — 零售消费品行业方案（40文件）
- [[方案集/C13-烟草行业]] — 烟草行业方案（3文件）
- [[方案集/C14-其他行业]] — 智慧园区/水务/农业/金融等综合方案

**厂商方案集（D类）**
- [[方案集/D01-西门子方案集]] — 西门子PLM/MES/MOM/仿真/自动化方案
- [[方案集/D02-SAP方案集]] — SAP S/4HANA/MES/MDM/供应链方案（36文件）
- [[方案集/D03-华为方案集]] — 华为数字化转型/云计算/工业互联网方案（60文件）
- [[方案集/D04-金蝶用友鼎捷]] — 国产ERP企业管理方案集（56文件）
- [[方案集/D05-罗克韦尔施耐德ABB]] — 工业自动化厂商方案（49文件）
- [[方案集/D06-阿里腾讯百度]] — 互联网科技企业数字化转型方案（26文件）
- [[方案集/D07-GE方案集]] — GE通用电气工业方案（5文件）

**白皮书与培训（E类）**
- [[方案集/E01-白皮书与行业报告]] — 智能制造白皮书/产业报告（135文件）
- [[方案集/E02-咨询方法论]] — 咨询方法论与工具体系（44文件）
- [[方案集/E03-管理培训]] — 管理培训与能力提升资料（47文件）


## 项目经验

> **制造业信息化项目交付经验汇总**
> 包含多个行业（半导体、化工、汽配、食品等）的WMS/MES/MOM项目交付案例
> 经验内容可跨组织复用，不限于特定实施商

**项目交付经验**
- [[项目经验/制造业项目交付经验库]] — 多行业项目交付案例：亭江新材(化工)、英思嘉(半导体)、吉豪(汽配)等

**项目实战经验**
- [[通威农发/实战踩坑经验]] — 通威农发项目实施过程中的真实踩坑案例与解决方案

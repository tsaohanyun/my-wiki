---
source_url: 详设评审\1-【生产管理】【生产执行】小料预处理.docx
ingested: 2026-05-26
project: 天味家园B栋MES
---

SOURCE: 详设评审\1-【生产管理】【生产执行】小料预处理.docx
DESC: 详设评审-小料预处理
============================================================
[/body/p[@paraId=1D366EB5]] 【天味】【生产管理】【生产执行】小料预处理
[/body/p[@paraId=0944E6D3]] 一、需求目的
[/body/p[@paraId=3357E84C]] 1、支持工序类型为小料预处理的生产执行单PC端可视化投料作业操作、PDA报工作业操作
[/body/p[@paraId=4E777590]] 2、按生产执行单自动归集 原材料投料、半成品报工数据并自动触发线边出入库
[/body/p[@paraId=57E5F9DD]] 
[/body/p[@paraId=2CAF8A59]] 二、需求描述
[/body/p[@paraId=655B43DC]] （一）业务流程
[/body/p[@paraId=79472C5B]] 
[/body/p[@paraId=3A7D8C4E]] 
[/body/p[@paraId=7D7C5FE1]] （二）系统流程
[/body/p[@paraId=277728E2]] 
[/body/p[@paraId=2168408B]] （三）需求描述
[/body/p[@paraId=3780D130]]   1）界面1说明——小料预处理
[/body/p[@paraId=63E5FD38]] • 功能概述
[/body/p[@paraId=093044EF]] 对 工序类型为 小料预处理 生产执行单进行投料、报工作业（应用平台PC端作业界面，无APP端）
[/body/p[@paraId=1BD13468]] • 功能路径
[/body/p[@paraId=43D43A5F]] 【生产管理】>【生产执行】>【小料预处理】
[/body/p[@paraId=3FD01804]] • UI交互稿
[/body/p[@paraId=2D363290]] https://www.figma.com/file/lk4Ux3GSVoVS7L61DPOJzU/%E5%A4%A9%E5%91%B3?type=design&node-id=632%3A28286&t=H5DXvEiZWuD93EBn-1
[/body/p[@paraId=133E8160]] 产品草图：
[/body/p[@paraId=5FF60927]] 
[/body/p[@paraId=7CCA0FBB]] • 界面字段与操作
[/body/p[@paraId=6ECA6EB8]] >【小料预处理】列表字段
小料预处理列表取数来源【生产执行单】
[/body/p[@paraId=6706775C]] 根据 生产执行单.工序 + 生产执行单.物料编码 取 工序产品配置.工序
[/body/p[@paraId=7E1E01A0]] 默认加载：
[/body/p[@paraId=603144F8]] “工序”筛选：下拉单选进行筛选，筛选列表为当前账号拥有的“工厂单元”下的所有类型为“小料”的工序（根据【工序产品配置】），默认第一个；
[/body/p[@paraId=5D2FC305]] 
[/body/p[@paraId=0C598A5C]] >【查询】字段
[/body/tbl[1]] [Table: 6 rows]
[/body/p[@paraId=24088702]] >操作说明
[/body/tbl[2]] [Table: 4 rows]
[/body/p[@paraId=68CC4512]] 
[/body/p[@paraId=7F82BE45]] 
[/body/p[@paraId=55CA4B23]] 2）界面2说明 ——小料投料
[/body/p[@paraId=4CB1511C]] • 功能概述
[/body/p[@paraId=49817F61]] 对 工序=小料 的生产执行单 进行投料作业（应用平台-PC端操作界面）
[/body/p[@paraId=08008EC6]] 根据 小料半成品编码+BOM版本，带出 产品BOM 信息，指引投料作业
[/body/p[@paraId=1871EFF0]] 业务场景：
[/body/p[@paraId=660E91E4]] 1、面向 半成品-小料 投料，支持扫码物料标签条码 or 手工选择 物料编码、批次号 方式投料，支持同个原料物料多次投料并自动产生物料线边仓库位投料记录、出库
[/body/p[@paraId=57FFD183]] 2、面向 半成品-小料下阶半成品-溶液（如A04溶液）投料&报工，支持扫码物料标签条码 or 手工选择 物料编码、批次号 方式投料，支持同个原料物料多次投料并自动产生物料在制仓库位投料出库；同时支持 溶液生产执行单整批快速报工
[/body/p[@paraId=0C1567D5]] 
[/body/p[@paraId=2C3D16AB]] • 功能路径
[/body/p[@paraId=3E9B721E]] 【生产管理】>【生产执行】>【小料预处理】>选择 生产执行单，点击 投料 >【投料】
[/body/p[@paraId=6C75B420]] 
[/body/p[@paraId=7A8C178C]] • UI交互稿
[/body/p[@paraId=6B7053A9]] 产品草图：
[/body/p[@paraId=4F4679B2]] 
[/body/p[@paraId=5DB792E1]] 如：部分干料、A04溶液 不需投料在小料混合池，溶液通过 物料特征值 区分，干料通过 《小料干料配料方式配置》区分
[/body/p[@paraId=668AAD2F]] 
[/body/p[@paraId=7122D00B]] • 界面字段与操作
[/body/p[@paraId=5F942C62]] 
[/body/p[@paraId=52778524]] >【投料】主界面字段数据来源
[/body/p[@paraId=4E3B923D]] 
[/body/p[@paraId=5E661808]] 1、【生产订单执行信息】区域数据来自生产执行单：
[/body/p[@paraId=0DB4DE00]] 根据【小料预处理】列表【投料】按钮点击进入自动带出，不可编辑
[/body/p[@paraId=6EB55979]] 2、【配方信息】数据来自 产品BOM、生产投料记录：
[/body/p[@paraId=3E366EFE]] 根据【生产执行单-物料编码】+【生产执行单-BOM版本】取对应【产品BOM】
[/body/p[@paraId=494CDFD0]] 根据【生产执行单号】取对应【生产投料记录】
[/body/p[@paraId=25330ABA]] 字段明细：
[/body/tbl[3]] [Table: 10 rows]
[/body/p[@paraId=389C05F0]] 3、【设备信息】区域 扫码自动带出
[/body/p[@paraId=549C8B79]] 字段明细：
[/body/tbl[4]] [Table: 2 rows]
[/body/p[@paraId=6926FEF5]] 
[/body/p[@paraId=180FE143]] 4、【物料信息】区域 数据来源手工录入、选择或扫码自动带出
[/body/p[@paraId=34417C2A]] 字段明细：
[/body/tbl[5]] [Table: 7 rows]
[/body/p[@paraId=6BA423B3]] 5、【称重信息】区域 数据来源电子秤接口、手工录入
[/body/p[@paraId=12FA7A20]] 字段明细：
[/body/tbl[6]] [Table: 6 rows]
[/body/p[@paraId=0C3C601D]] 6、【溶液报工】区域 数据来源电子秤接口、手工录入（只有当【生产执行单信息-物料-物料类别】= 【溶液】，且 【生产执行单信息-物料-特征值-溶液配料方式】!= 【单配】 时，该区域才需要显示。业务上即为除A04溶液之外的溶液生产执行单，投完料之后马上进行整单报工）
[/body/p[@paraId=033FF5C1]] 字段明细：
[/body/tbl[7]] [Table: 2 rows]
[/body/p[@paraId=3C08FF6B]] 
[/body/p[@paraId=403B71DB]] >【投料】主界面操作说明
[/body/tbl[8]] [Table: 10 rows]
[/body/p[@paraId=009C61B3]] >【投料】主界面操作说明
[/body/p[@paraId=0A5CB6C5]] 整体进度（进度条说明）：投料进度=已完成的物料条数 / 物料总条数（不含 投料进度= 无需投料 的记录行）
[/body/p[@paraId=21DC5386]] 
[/body/p[@paraId=1C7D0440]] 3）界面3说明 ——小料报工
[/body/p[@paraId=0318CECD]] • 功能概述
[/body/p[@paraId=69C24B80]] 对 工序类型=小料 的生产执行单 进行报工作业。根据 小料半成品 执行单号，带出对应报工批次、容器编码等信息，指引小料半成品分装下线报工作业。
[/body/p[@paraId=5DD75876]] 业务场景：
[/body/p[@paraId=29698FB2]] 1、面向 半成品-小料 报工，支持绑定容器、分多容器 多次分装下线报工
[/body/p[@paraId=51BA578F]] 2、半成品-小料 装桶同时，支持 同步执行 投料作业（投干料、投溶液等）
[/body/p[@paraId=74BDF61E]] 3、根据 分装下线的容器报工、投料，自动产生后台 投料记录、报工记录，并触发对应原材料物料、半成品在小料线边仓/库位 出入库
[/body/p[@paraId=3697CFB1]] 
[/body/p[@paraId=79077743]] • 功能路径
[/body/p[@paraId=2E774DDC]] 【小博智造】>【生产管理】>【小料预处理】>选择 生产执行单，点击 【报工】
[/body/p[@paraId=31F2C8F7]] • UI交互稿
[/body/p[@paraId=4A146F9D]] 产品草图：
[/body/p[@paraId=0D0AC99B]] 
[/body/p[@paraId=71E5048A]] • 界面字段与操作
[/body/p[@paraId=79EC1C0A]] >【小料预处理】界面说明
[/body/p[@paraId=71FC99DA]] >>“未完成”标签页显示的是状态为“未开始”及“生产中”的生产执行单；
[/body/p[@paraId=02A72188]] >>“已完成”标签页显示的是状态为“已完成”的生产执行单；
[/body/p[@paraId=60BE1015]] >>“工序”筛选：下拉单选进行筛选，筛选列表为当前账号拥有的“工厂单元”下的所有类型为“小料”的工序（根据【工序产品配置】），默认第一个；
[/body/p[@paraId=767BDFE0]] >>根据筛选结果显示生产执行单列表，字段有：
[/body/tbl[9]] [Table: 9 rows]
[/body/p[@paraId=772124F5]] >>界面操作有
[/body/tbl[10]] [Table: 4 rows]
[/body/p[@paraId=6B534DC5]] 
[/body/p[@paraId=75DB7360]] >【报工】界面说明
[/body/p[@paraId=7EE630F8]] >>“报工信息”标签页列表字段有：
[/body/tbl[11]] [Table: 10 rows]
[/body/p[@paraId=33B5DC67]] >>“报工信息”标签页的操作有：
[/body/tbl[12]] [Table: 10 rows]
[/body/p[@paraId=03E6D92B]] 
[/body/p[@paraId=4A26088F]] >【干料投料】界面说明
[/body/p[@paraId=302329CC]] >>“物料需求”标签页显示的是根据生产执行单的“BOM版本查询到的 单配的干料物料（每一锅） 及其 数量”；
[/body/p[@paraId=50073466]] >>“物料需求”标签页列表字段有：
[/body/tbl[13]] [Table: 12 rows]
[/body/p[@paraId=3BF09006]] >>“物料需求”标签页的操作有：
[/body/tbl[14]] [Table: 9 rows]
[/body/p[@paraId=636FC708]] 
[/body/p[@paraId=52336B3A]] 
[/body/p[@paraId=19A56A70]] 
[/body/p[@paraId=79F10068]] 
[/body/p[@paraId=2DA99F0D]] 
[/body/p[@paraId=5F478692]] 
[/body/p[@paraId=56026881]] >>“报工明细”标签页显示当前生产执行单的所有报工记录，列表字段有（按创建时间倒序排序）：
[/body/tbl[15]] [Table: 5 rows]
[/body/p[@paraId=4380CE32]] >>“报工明细”标签页的操作有：
[/body/tbl[16]] [Table: 2 rows]
[/body/p[@paraId=2AE7B726]] 
[/body/p[@paraId=1669E7A0]] 
[/body/p[@paraId=77E7AF27]] 
[/body/p[@paraId=0E3756B2]] 
[/body/p[@paraId=7C0590F3]] 
[/body/p[@paraId=7C96B382]] ----------
[/body/p[@paraId=3C717E88]] 
[/body/p[@paraId=69100E6E]] • 界面字段与操作
[/body/p[@paraId=280688CD]] >【报工】主界面字段数据来源
[/body/p[@paraId=1DBAD719]] 1、【生产订单执行信息】区域数据来自生产执行单：
[/body/p[@paraId=23DA9D85]] 根据【小料预处理】列表【报工】按钮点击进入自动带出，不可编辑
[/body/p[@paraId=14D9BD14]] 
[/body/p[@paraId=00375FDE]] 2、【已下线容器】区域数据来自 生产完工记录、容器管理：
[/body/p[@paraId=67657295]] 根据【生产执行单号】取对应【报工记录】
[/body/p[@paraId=39E99B0B]] 
[/body/p[@paraId=51EDBFD9]] 根据【生产执行单号】+【报工记录.批次号】取对应【容器－编码】待Jimi确定逻辑
[/body/p[@paraId=28E5D348]] 字段明细：
[/body/tbl[17]] [Table: 7 rows]
[/body/p[@paraId=447CC07E]] 3、【容器物料绑定】区域数据来源手工录入、选择或扫码自动带出：
[/body/p[@paraId=00F17446]] 字段明细：
[/body/tbl[18]] [Table: 8 rows]
[/body/p[@paraId=239E2CEE]] 4、【溶液投料】区域 数据来源手工录入、选择带出
[/body/p[@paraId=062E7A89]] 字段明细：
[/body/tbl[19]] [Table: 7 rows]
[/body/p[@paraId=5BC659E1]] 5、【称重信息】区域 数据来源电子秤接口、手工录入
[/body/p[@paraId=6372F124]] 字段明细：
[/body/tbl[20]] [Table: 5 rows]
[/body/p[@paraId=11812C33]] >【报工】主界面操作说明
[/body/tbl[21]] [Table: 5 rows]
[/body/p[@paraId=4D353FCE]] >【报工】主界面操作说明
[/body/p[@paraId=0EDD98AE]] 整体进度（进度条说明）：投料进度=完成锅数 / 计划锅数
[/body/p[@paraId=663712B1]] 
[/body/p[@paraId=463550AC]] 
[/body/p[@paraId=0664BC51]] 
[/body/p[@paraId=61991D21]]

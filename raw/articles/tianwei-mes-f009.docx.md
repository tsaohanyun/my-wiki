---
source_url: 详设评审\2-【生产管理】【生产执行】返工品拆解.docx
ingested: 2026-05-26
project: 天味家园B栋MES
---

SOURCE: 详设评审\2-【生产管理】【生产执行】返工品拆解.docx
DESC: 详设评审-返工品拆解
============================================================
[/body/p[@paraId=672B28F6]] 【天味】【生产管理】【生产执行】返工品拆解
[/body/p[@paraId=1A09BB90]] 一、需求目的
[/body/p[@paraId=026D403C]] 1、支持生产工人选择返工品进行拆解，还原出部分原材料。
[/body/p[@paraId=3445E4C3]] 2、拆解完成之后，产生MOM端生产执行单、投料记录、报工记录。并自动对接SAP生产订单、生产订单投料、生产订单入库等。
[/body/p[@paraId=7865D1B3]] 
[/body/p[@paraId=752AAE18]] 三、需求描述
[/body/p[@paraId=0165C87B]] （一）系统流程
[/body/p[@paraId=38C8D09B]] 
[/body/p[@paraId=0AF78D73]] （二）需求描述
[/body/p[@paraId=55FA2A20]]   1）界面1说明——返工品拆解
[/body/p[@paraId=792EF40C]] • 功能概述
[/body/p[@paraId=19557C2E]] 针对返工品进行拆解，还原成原材料
[/body/p[@paraId=7F89A216]] • 功能路径
[/body/p[@paraId=5E1C1ABB]] 【小博智造】>【生产管理】>【返工品拆解】
[/body/p[@paraId=773A51C5]] • UI交互稿
[/body/p[@paraId=135FEA9B]] 产品草图：
[/body/p[@paraId=61B7EF7C]] 
[/body/p[@paraId=686B4435]] • 界面字段与操作
[/body/p[@paraId=76248F20]] >【小料预处理】列表字段
小料预处理列表取数来源【生产执行单】
[/body/p[@paraId=7393B1B6]] 根据 生产执行单.工序 + 生产执行单.物料编码 取 工序产品配置.工序类型
[/body/p[@paraId=04159353]] 默认加载：
[/body/p[@paraId=4AC18289]] 工序类型=小料预处理 的生产执行单
[/body/p[@paraId=7CB9A220]] 
[/body/p[@paraId=788D9617]] >【查询】字段
[/body/tbl[1]] [Table: 6 rows]
[/body/p[@paraId=2BA5AC9D]] >操作说明
[/body/tbl[2]] [Table: 4 rows]
[/body/p[@paraId=70D87DBE]] 
[/body/p[@paraId=3C5CC2D5]]

---
source_url: 详设评审\1-【生产管理】【生产执行】大料配料.docx
ingested: 2026-05-26
project: 天味家园B栋MES
---

SOURCE: 详设评审\1-【生产管理】【生产执行】大料配料.docx
DESC: 详设评审-大料配料
============================================================
[/body/p[@paraId=6F0AC9E3]] 【天味】【生产管理】【生产执行】大料配料
[/body/p[@paraId=73D7B663]] 一、需求背景
[/body/p[@paraId=13CFDCE5]] 大料配料是指在对火锅底料炒制前，将原料（如盐、糖）及经过预处理生产出的半成品（如姜粒、蒜粒）等按照火锅底料炒制的工艺要求，分装到不同大小的容器中。客户希望系统可以指导操作配料，同时校验配料数量是否符合工艺要求。
[/body/p[@paraId=2859EDE6]] 
[/body/p[@paraId=1D084695]] 二、需求目的
[/body/p[@paraId=6188742E]] 支持生产工人按配料任务单进行配料操作。
[/body/p[@paraId=4ADDEF70]] 三、需求描述
[/body/p[@paraId=3F3776A7]] （一）系统流程
[/body/p[@paraId=4DCFABC6]] 
[/body/p[@paraId=32FDB33B]] （二）需求描述
[/body/p[@paraId=49D1B247]]   1）界面1说明——大料配料
[/body/p[@paraId=0CB13173]] • 功能概述
[/body/p[@paraId=04C2D296]] 支持生产工人按配料任务单进行配料操作。
[/body/p[@paraId=411574BF]] • 功能路径
[/body/p[@paraId=6F2C9C53]] 【小博智造】>【生产管理】>【大料配料】
[/body/p[@paraId=1D760D4C]] • UI交互稿
[/body/p[@paraId=04219B0C]] 产品草图：
[/body/p[@paraId=1845BC68]] 
[/body/p[@paraId=4659993A]] • 界面字段与操作
[/body/p[@paraId=76582FCB]] >【大料配料】界面说明
[/body/p[@paraId=302E63E7]] >>“未完成”标签页显示的是状态为“未开始”及“执行中”的配料任务单；
[/body/p[@paraId=7EBB50C8]] >>“已完成”标签页显示的是状态为“已完成”的配料任务单；
[/body/p[@paraId=73170DE0]] >>“车间”筛选：下拉单选进行筛选，筛选列表为当前账号拥有的“工厂单元”下的所有“车间”，默认第一个；
[/body/p[@paraId=567C4914]] >>根据筛选结果显示配料任务单列表，字段有：
[/body/p[@paraId=790C6419]] 
[/body/tbl[1]] [Table: 6 rows]
[/body/p[@paraId=0795C0D4]] >>界面操作有
[/body/tbl[2]] [Table: 3 rows]
[/body/p[@paraId=51452E7E]] 
[/body/p[@paraId=66156ADE]] >【物料筛选】界面说明
[/body/p[@paraId=5EB1B158]] >>“炒制半成品”为下拉一级单选，选项为当前“车间”下类型为“炒制”的工序下，当前所有状态为“未开始”的生产工单的“物料名称”；
[/body/p[@paraId=61ED6FFB]] >>根据选择的“炒制半成品”，查询出炒制半成品物料所有工艺单主版本中，“投料类型”为“容器投料”的投料物料信息，按物料取并集；
[/body/p[@paraId=6CEDE96A]] 
[/body/p[@paraId=7E2083A9]] >【配料】界面说明
[/body/p[@paraId=4067E9D9]] >>列表字段有：
[/body/tbl[3]] [Table: 12 rows]
[/body/p[@paraId=7A6ED2C3]] >>操作有：
[/body/tbl[4]] [Table: 10 rows]
[/body/p[@paraId=2B8E6BFC]] 
[/body/p[@paraId=11D16A1B]] >【配料明细】界面说明
[/body/p[@paraId=29E05332]] >>列表字段有：
[/body/tbl[5]] [Table: 6 rows]
[/body/p[@paraId=5A31DEE9]] 
[/body/p[@paraId=464183CF]] 
[/body/p[@paraId=02CAC414]] 
[/body/p[@paraId=37D0EBEA]]

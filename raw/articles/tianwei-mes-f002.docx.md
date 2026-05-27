---
source_url: 详设评审\1-【生产管理】【生产执行】大料预处理.docx
ingested: 2026-05-26
project: 天味家园B栋MES
tags:
- MES
- 原始资料
- 天味
---

SOURCE: 详设评审\1-【生产管理】【生产执行】大料预处理.docx
DESC: 详设评审-大料预处理
============================================================
[/body/p[@paraId=7C9F080F]] 【天味】【生产管理】【生产执行】大料预处理
[/body/p[@paraId=14C0130D]] 一、需求背景
[/body/p[@paraId=63E617EB]] 大料预处理是指在对火锅底料炒制前，对姜、蒜、辣椒等原材料进行切碎、蒸煮等加工处理，客户需要对在对预处理过程中的投料、产出进行记录，统计。
[/body/p[@paraId=0D30853D]] 
[/body/p[@paraId=19743A19]] 二、需求目的
[/body/p[@paraId=1AE588C2]] 支持记录大料预处理生产执行单投料、报工数据。
[/body/p[@paraId=72BC2C60]] 三、需求描述
[/body/p[@paraId=37FF5E07]] （一）业务流程
[/body/p[@paraId=5AC715D2]] （二）系统流程
[/body/p[@paraId=7E07BE0A]] （三）需求描述
[/body/p[@paraId=0A128311]]   1）界面1说明——大料预处理
[/body/p[@paraId=033AD95A]] • 功能概述
[/body/p[@paraId=03B111B0]] 支持记录大料预处理生产执行单投料、报工数据。
[/body/p[@paraId=3B004510]] • 功能路径
[/body/p[@paraId=14664328]] 【小博智造】>【生产管理】>【大料预处理】
[/body/p[@paraId=322B239C]] • UI交互稿
[/body/p[@paraId=2D67F0A2]] 产品草图：
[/body/p[@paraId=078730A0]] 
[/body/p[@paraId=68611F52]] • 界面字段与操作
[/body/p[@paraId=70FB8BA4]] >【大料预处理】界面说明
[/body/p[@paraId=7D290045]] >>“未完成”标签页显示的是状态为“未开始”及“生产中”的生产执行单；
[/body/p[@paraId=28FC5446]] >>“已完成”标签页显示的是状态为“已完成”的生产执行单；
[/body/p[@paraId=7339C8FC]] >>“工序”筛选：下拉单选进行筛选，筛选列表为当前账号拥有的“工厂单元”下的所有类型为“大料”或“煮椒”的工序（根据【工序产品配置】），默认第一个；
[/body/p[@paraId=0AE0574C]] >>根据筛选结果显示生产执行单列表，字段有：
[/body/tbl[1]] [Table: 8 rows]
[/body/p[@paraId=587E390D]] >>界面操作有
[/body/tbl[2]] [Table: 6 rows]
[/body/p[@paraId=78466EB5]] 
[/body/p[@paraId=41121E80]] >【投料】界面说明
[/body/p[@paraId=6F28DB01]] >>“物料需求”标签页显示的是根据生产执行单的“BOM版本查询到的每一种子物料及其数量”；
[/body/p[@paraId=0D66B2A6]] >>“投料明细”标签页显示的是每一次投料的记录；
[/body/p[@paraId=37E03264]] >>“物料需求”标签页列表字段有：
[/body/tbl[3]] [Table: 12 rows]
[/body/p[@paraId=4AA5D4FA]] >>“物料需求”标签页的操作有：
[/body/tbl[4]] [Table: 9 rows]
[/body/p[@paraId=53ECDDE3]] >>“投料明细”标签页显示当前生产执行单的所有投料记录，列表字段有（按创建时间倒序排序）：
[/body/tbl[5]] [Table: 6 rows]
[/body/p[@paraId=22E837B9]] >>“投料明细”标签页的操作有：
[/body/tbl[6]] [Table: 2 rows]
[/body/p[@paraId=6B15245F]] 
[/body/p[@paraId=25215270]] >【报工】界面说明
[/body/p[@paraId=0A646B55]] >>“报工信息”标签页列表字段有：
[/body/tbl[7]] [Table: 7 rows]
[/body/p[@paraId=27D040E0]] >>“报工信息”标签页的操作有：
[/body/tbl[8]] [Table: 9 rows]
[/body/p[@paraId=7D2904D7]] >>“报工明细”标签页显示当前生产执行单的所有报工记录，列表字段有（按创建时间倒序排序）：
[/body/tbl[9]] [Table: 5 rows]
[/body/p[@paraId=4C6A3FD2]] >>“报工明细”标签页的操作有：
[/body/tbl[10]] [Table: 2 rows]
[/body/p[@paraId=0326EF0C]] 
[/body/p[@paraId=07AD4A72]] • 状态流转图
[/body/p[@paraId=1E0DBBE7]] 大料预处理生产执行单及生产工单状态流转图：
[/body/p[@paraId=0FEE5824]] 
[/body/p[@paraId=45B80F64]] 
[/body/p[@paraId=3B25AF1B]]


## 相关页面

- [[tianwei-mes-f000.xlsx]]
- [[tianwei-mes-f001.docx]]
- [[tianwei-mes-f003.docx]]
- [[tianwei-mes-f004.docx]]
- [[tianwei-mes-f005.docx]]

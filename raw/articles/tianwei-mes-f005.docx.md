---
source_url: 详设评审\1-【生产管理】工单管理.docx
ingested: 2026-05-26
project: 天味家园B栋MES
---

SOURCE: 详设评审\1-【生产管理】工单管理.docx
DESC: 详设评审-工单管理
============================================================
[/body/p[@paraId=5306B7DA]] 【天味】【生产管理】工单管理
[/body/p[@paraId=56106FAC]] 一、需求背景
[/body/p[@paraId=4F98FABE]] 名称解释：
[/body/tbl[1]] [Table: 5 rows]
[/body/p[@paraId=6911CAC1]] 二、需求目的
[/body/p[@paraId=6A9C4AB7]] 支持用户按实际生产需求新增/导入生产订单，系统自动根据物料的BOM，调用SAP接口生成生产工单；用户可审核确认、下发生产工单，系统按照配置自动生成生产执行单。
[/body/p[@paraId=08EB514F]] 
[/body/p[@paraId=469AFCB8]] 三、需求描述
[/body/p[@paraId=42DE0173]] （一）业务流程
[/body/p[@paraId=59EA741D]] 
[/body/p[@paraId=3CE976BE]] （二）系统流程 
[/body/p[@paraId=637D2CBD]] （三）需求描述
[/body/p[@paraId=542A4712]]   1）界面1说明——生产订单
[/body/p[@paraId=74F55367]] • 功能概述
[/body/p[@paraId=028D9CC5]] 新增/导入成品生产需求订单；选择生产订单生成生产工单。
[/body/p[@paraId=0DC3D8E8]] • 功能路径
[/body/p[@paraId=2D64FD9F]] 【生产管理】>【工单管理】>【生产订单】
[/body/p[@paraId=1662963B]] • UI交互稿
[/body/p[@paraId=5F2A0443]] 产品草图：
[/body/p[@paraId=69F26C55]] 
[/body/p[@paraId=1432EB99]] • 界面字段与操作
[/body/p[@paraId=00850395]] >【新增/编辑】弹窗字段
[/body/tbl[2]] [Table: 10 rows]
[/body/p[@paraId=5598E629]] >【新增/编辑】弹窗操作
[/body/tbl[3]] [Table: 3 rows]
[/body/p[@paraId=2A0F4A18]] >【订单类型配置】弹窗字段
[/body/tbl[4]] [Table: 2 rows]
[/body/p[@paraId=52426C04]] >【订单类型配置】弹窗操作
[/body/tbl[5]] [Table: 5 rows]
[/body/p[@paraId=6B1659FE]] >【生产订单】主页面列表字段
[/body/tbl[6]] [Table: 17 rows]
[/body/p[@paraId=686AFDFD]] >【生产订单】主界面操作
[/body/tbl[7]] [Table: 6 rows]
[/body/p[@paraId=1C64B803]] >【生成工单】弹窗列表字段
[/body/tbl[8]] [Table: 13 rows]
[/body/p[@paraId=42AC38AB]] >【生成工单】弹窗操作
[/body/tbl[9]] [Table: 3 rows]
[/body/p[@paraId=309CF20A]] 
[/body/p[@paraId=6F4EA2BB]] 
[/body/p[@paraId=36C5D26D]] 2）界面2说明 ——生产工单
[/body/p[@paraId=5E26680D]] • 功能概述
[/body/p[@paraId=0272AD5E]] 对生成的“生成工单”进行[审核确认]，然后生成“生产执行单”。
[/body/p[@paraId=04719F2E]] • 功能路径
[/body/p[@paraId=15F46BC0]] 【生产管理】>【工单管理】>【生产工单】
[/body/p[@paraId=5CD66C85]] • UI交互稿
[/body/p[@paraId=290E1BB9]] 产品草图：
[/body/p[@paraId=1D4A4B7F]] 
[/body/p[@paraId=463EFEF5]] • 界面字段与操作
[/body/p[@paraId=79C7E334]] >【生产工单】主页面列表的数据来源有两种，一种是来自【生产订单】生成的“生产工单”，另外一种是由车间内勤直接创建生成，列表字段说明如下：
[/body/tbl[10]] [Table: 27 rows]
[/body/p[@paraId=799AC921]] >【生产工单】主界面操作
[/body/tbl[11]] [Table: 6 rows]
[/body/p[@paraId=4A452070]] >【新增/编辑】弹窗字段
[/body/tbl[12]] [Table: 10 rows]
[/body/p[@paraId=2BB75DB4]] >【新增/编辑】弹窗操作
[/body/tbl[13]] [Table: 3 rows]
[/body/p[@paraId=1AA144FF]] >【生成执行单】弹窗列表字段
[/body/tbl[14]] [Table: 22 rows]
[/body/p[@paraId=7F7480D4]] >【下发执行单】弹窗操作
[/body/tbl[15]] [Table: 3 rows]
[/body/p[@paraId=1A9391C9]] 
[/body/p[@paraId=2A4C9261]] • 后台逻辑
[/body/p[@paraId=56985C38]] >“生产工单”生成“生产执行单”的逻辑如下：
[/body/p[@paraId=2E16A70A]] [该类型的内容暂不支持下载]
[/body/p[@paraId=3612E42E]] 
[/body/p[@paraId=0DC87F5F]] 3）界面3说明 ——生产执行单
[/body/p[@paraId=5FCB1E00]] • 功能概述
[/body/p[@paraId=0E4AD293]] 承接由“生产工单”生成的生产执行单。
[/body/p[@paraId=677D0C72]] • 功能路径
[/body/p[@paraId=43535059]] 【生产管理】>【工单管理】>【生产执行单】
[/body/p[@paraId=6E3E457D]] • UI交互稿
[/body/p[@paraId=65FCC079]] 产品草图：
[/body/p[@paraId=2C70C9BC]] 
[/body/p[@paraId=7DF7FAB9]] • 界面字段与操作
[/body/p[@paraId=2D5A8BB6]] >【生产执行单】主页面列表字段说明如下（“生产执行”单相当于现有系统的“工序生产任务”，与生产任务字段的对应关系见最后一列说明，生成任务模板为“火锅底料-生产任务模板”）：
[/body/tbl[16]] [Table: 17 rows]
[/body/p[@paraId=460E2AF1]] 
[/body/p[@paraId=28924861]] 4）界面4说明 ——配料任务单
[/body/p[@paraId=0EEF6923]] • 功能概述
[/body/p[@paraId=11A12A86]] “炒制半品”物料在生成“生产执行单”（一锅一个执行单）的时候，会按炒锅工艺单同步生成配料任务单。
[/body/p[@paraId=6EE9231B]] • 功能路径
[/body/p[@paraId=00F4A724]] 【生产管理】>【工单管理】>【配料任务单】
[/body/p[@paraId=44BCCBF2]] • UI交互稿
[/body/p[@paraId=19E8E1C7]] 产品草图：
[/body/p[@paraId=162A4C96]] 
[/body/p[@paraId=6FC8E04B]] • 界面字段与操作
[/body/p[@paraId=08519A3B]] >【配料任务单】主页面列表字段说明如下：
[/body/tbl[17]] [Table: 11 rows]
[/body/p[@paraId=7AEEDBF4]] 
[/body/p[@paraId=38792709]]

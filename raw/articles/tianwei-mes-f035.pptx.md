---
source_url: 接口说明\集成接口会议材料.pptx
ingested: 2026-05-26
project: 天味家园B栋MES
---

SOURCE: 接口说明\集成接口会议材料.pptx
DESC: 接口-集成会议材料
============================================================
=== /slide[1] ===
天味家园MES集成简述

2023年07月18日

=== /slide[2] ===
目录
01 旧SAP
02 新SAP
03 一物一码
04 WMS

=== /slide[3] ===
旧SAP对接 共计17个接口
MES
ES_SAP
MES向旧SAP 推送订单创建与执行，提交物料消耗
MES向旧SAP  拉取工艺工时、跨车间物流、预留信息
接口均为MES调用旧SAP接口

=== /slide[4] ===
新SAP对接  共计26个接口
MES
PCE_SAP
MES向新SAP 推送订单创建与执行，提交物料消耗
                        返工、盘点等在MES发生的业务
MES向旧新SAP  拉取BOM、工艺、客商等主数据
个别成本、跨工厂业务由SAP调用MES，其余均为MES调用SAP

=== /slide[5] ===
新SAP接口清单

=== /slide[6] ===
一物一码系统 共1个接口
MES
一物一码
MES向一物一码系统推送工单数据

=== /slide[7] ===
WMS系统对接 共10个接口
MES
WMS
涉及出入库、退货等业务
发生业务需要通知对方系统时调用对方借口

=== /slide[8] ===
WMS系统接口清单

=== /slide[9] ===
 THANKS
一起折腾未来

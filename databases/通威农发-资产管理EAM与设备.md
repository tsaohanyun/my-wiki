---
title: 资产管理EAM与设备
created: 2026-05-07
updated: 2026-05-14
type: concept
description: >
  > 相关Wiki：数据库总览 | EBS-DIM接口 | 运营指标体系 EAM（Enterprise Asset Management）企业资产管理模块，管理通威农发的固定资产和设备资产。涵盖资产台账、资产折旧、资产变动、设备台账、设备维修工单、备件管理等功能。
tags: [smart-manufacturing]
sources: [raw/]
confidence: high
---


# 资产管理EAM与设备


> 项目：**通威农发**（通威股份农业发展有限公司）
>
> 相关Wiki：[数据库总览](通威农发-数据库总览.md) | [EBS-DIM接口](../integrations/ebs-dim/README.md) | [运营指标体系](../kpi/README.md)
## 模块简介

EAM（Enterprise Asset Management）企业资产管理模块，管理通威农发的固定资产和设备资产。涵盖资产台账、资产折旧、资产变动、设备台账、设备维修工单、备件管理等功能。

## 表清单（共15张表）

| 表名 | 说明 |
|------|------|
| eam_accident_report | 设备事故报告 |
| eam_accident_report_document | 附件 |
| eam_equipment_allocation | 设备调拨 |
| eam_equipment_allocation_detail | 设备调拨清单 |
| eam_equipment_allocation_document | 设备调拨文档 |
| eam_equipment_idle_or_enable | 设备闲置启用 |
| eam_equipment_idle_or_enable_detail | 闲置启用清单 |
| eam_equipment_idle_or_enable_document | 设备闲置启用文档 |
| eam_equipment_scrap | 设备报废 |
| eam_equipment_scrap_detail | 报废清单 |
| eam_equipment_scrap_document | 设备报废文档 |
| eam_equipment_scrap_score | 评分指标 |
| equip_location | 设备位置 |
| equipment_account_product_name | 设备台账物料品名配置 |
| equipment_change | 设备变更记录 |

## 业务域概览

- **eam** (12张表)：资产台账/资产折旧/设备维修/备件管理

---

[[通威农发-数据库总览]]

## 相关页面
- [[通威农发-APS计划排程]]
- [[通威农发-E2D与数据同步]]
- [[通威农发-EDO设备管理]]
- [[通威农发-IIoT工业物联网]]
- [[通威农发-LM精益管理]]

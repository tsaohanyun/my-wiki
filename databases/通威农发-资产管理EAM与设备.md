---
title: 通威农发-资产管理EAM与设备
created: 2026-05-07
updated: 2026-05-07
type: concept
tags: [数据库, 通威农发, eam, 资产管理, 设备]
confidence: high
---

# 通威农发-资产管理EAM与设备

## 模块简介

EAM（Enterprise Asset Management）企业资产管理模块与设备管理相关的数据表集合。涵盖设备资产全生命周期管理，包括设备台账配置、设备调拨、设备闲置/启用、设备报废管理、设备事故报告、设备位置及设备变更记录等功能，支撑企业对生产设备从入库到报废的全过程数字化管理。

## EAM企业资产管理模块

EAM模块以 `eam_` 为前缀，共12张表，覆盖设备资产从调拨、闲置/启用、报废到事故报告的全流程。

| 表名 | COMMENT注释 |
|------|------------|
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

子模块说明：

- **设备调拨**（eam_equipment_allocation）：管理设备在不同部门或工厂之间的调拨流程，含调拨清单与调拨文档子表。
- **设备闲置/启用**（eam_equipment_idle_or_enable）：记录设备闲置与重新启用的审批流程及清单。
- **设备报废**（eam_equipment_scrap）：管理设备报废审批，含报废清单、报废文档及评分指标表。
- **设备事故报告**（eam_accident_report）：记录设备安全事故信息及附件文档。

## 设备基础配置模块

以 `equipment_` 为前缀，共2张表，提供设备台账的基础配置数据。

| 表名 | COMMENT注释 |
|------|------------|
| equipment_account_product_name | 设备台账物料品名配置 |
| equipment_change | 设备变更记录 |

子模块说明：

- **设备台账配置**（equipment_account_product_name）：定义设备台账中使用的物料品名标准，用于统一设备分类与命名。
- **设备变更记录**（equipment_change）：追踪设备信息的变更历史，确保设备台账数据的可追溯性。

## 设备位置模块

| 表名 | COMMENT注释 |
|------|------------|
| equip_location | 设备位置 |

定义设备安装或存放的地理位置信息，为设备分布管理提供基础数据支持。

---

## 表清单汇总

所有涉及按表名字母顺序排列如下：

| 表名 | COMMENT注释 | 所属模块 |
|------|------------|---------|
| eam_accident_report | 设备事故报告 | EAM |
| eam_accident_report_document | 附件 | EAM |
| eam_equipment_allocation | 设备调拨 | EAM |
| eam_equipment_allocation_detail | 设备调拨清单 | EAM |
| eam_equipment_allocation_document | 设备调拨文档 | EAM |
| eam_equipment_idle_or_enable | 设备闲置启用 | EAM |
| eam_equipment_idle_or_enable_detail | 闲置启用清单 | EAM |
| eam_equipment_idle_or_enable_document | 设备闲置启用文档 | EAM |
| eam_equipment_scrap | 设备报废 | EAM |
| eam_equipment_scrap_detail | 报废清单 | EAM |
| eam_equipment_scrap_document | 设备报废文档 | EAM |
| eam_equipment_scrap_score | 评分指标 | EAM |
| equip_location | 设备位置 | 设备位置 |
| equipment_account_product_name | 设备台账物料品名配置 | 设备基础配置 |
| equipment_change | 设备变更记录 | 设备基础配置 |

---

[[通威农发-数据库总览]]

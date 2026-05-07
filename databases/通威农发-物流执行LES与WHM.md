---
title: 通威农发-物流执行LES与WHM
created: 2026-05-07
updated: 2026-05-07
type: concept
tags: [数据库, 通威农发, les, whm, 物流执行, 仓库]
confidence: high
---

# 通威农发-物流执行LES与WHM

## 模块简介

**LES（Logistics Execution System，物流执行系统）**：通威农发物流执行系统，负责工厂物流环节的车辆排队、车辆登记、承运商管理、自助终端及工厂队列配置等业务，实现从车辆进厂到装货出厂的全流程物流管控。

**WHM（Warehouse Management，仓库管理辅助模块）**：仓库管理辅助模块，提供仓库基础数据维护，包括仓库信息、库区管理、库位管理、工作区管理及库位混放规则等，为仓储作业提供基础配置支撑。

---

## LES 物流执行系统

该模块共 8 张表。

| 表名 | COMMENT注释 |
|------|------------|
| les_application_item_t | 微信端与自助终端车辆登记信息子表，记录合同、订单、申请信息 |
| les_application_line | 车辆排队表 |
| les_application_t | 微信端与自助终端车辆登记信息主表 |
| les_carrier_t | 承运商 |
| les_device_config | 自助终端 |
| les_factory_operatype | 工厂业务 |
| les_factory_queue | 工厂队列 |
| les_factory_queue_info | 工厂队列配置明细 |

---

## WHM 仓库管理辅助模块

该模块共 11 张表。

| 表名 | COMMENT注释 |
|------|------------|
| whm_operate_management | 操作管理 |
| whm_reservoir_area | 库区管理 |
| whm_warehouse | 仓库管理 |
| whm_warehouse_area | 仓库地址管理 |
| whm_warehouse_location | 库位管理 |
| whm_warehouse_location_freeze_release_reason | 库位管理-冻结/释放原因 |
| whm_warehouse_location_info | 库位管理-基本信息 |
| whm_warehouse_location_materials | 库位管理-仓储资料 |
| whm_warehouse_location_mixed_rules | 库位管理-混放规则 |
| whm_warehouse_location_operate | 库位管理-操作管理 |
| whm_workspace_manage | 工作区管理 |

---

引用：[[通威农发-数据库总览]]

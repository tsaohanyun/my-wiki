---
title: 物流执行LES与WHM
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, les, 物流执行]
confidence: high
---

# 物流执行LES与WHM

## 模块简介

LES（Logistics Execution System）物流执行系统和WHM（Warehouse Helper Module）仓库辅助模块。涵盖物流运输管理（运输计划/运输单/运输跟踪）、仓库辅助（库位管理/搬运设备/叉车管理）等功能。

## 表清单（共25张表）

| 表名 | 说明 |
|------|------|
| cargo_owner | 货主管理表 |
| cargo_owner_org_rel | cargo_owner_org_rel 与 cargo_owner 的关联表 |
| les_application_item_t | 微信端与自助终端车辆登记信息子表，记录合同、订单、申请信息 |
| les_application_line | 车辆排队表 |
| les_application_t | 微信端与自助终端车辆登记信息主表 |
| les_carrier_t | 承运商 |
| les_device_config | 自助终端 |
| les_factory_operatype | 工厂业务 |
| les_factory_queue | 工厂队列 |
| les_factory_queue_info | 工厂队列配置明细 |
| loading_account | loading_account |
| loading_account_part_detail | loading_account_part_detail |
| vehicle_type | 载具型号 |
| vehicle_type_items | 载具型号-专用物料清单 |
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

## 业务域概览

- **les** (8张表)：物流运输管理
- **whm** (11张表)：仓库辅助管理

---

[[通威农发-数据库总览]]

---
title: APS计划排程
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, aps, 计划排程]
confidence: high
---

# APS计划排程

## 模块简介

APS（Advanced Planning and Scheduling）高级计划排程模块，管理通威农发的生产计划、需求预测和排程优化。涵盖需求管理、主生产计划、车间作业排程、产能规划、排程约束、能源预算等功能。

## 表清单（共37张表）

| 表名 | 说明 |
|------|------|
| aps_base_cost | ApsBaseCost |
| aps_base_energy_price | 能源价格 |
| aps_base_energy_type | 能源类型 |
| aps_base_power_num | 最小开机数量 |
| aps_budget_energy | ApsBudgetEnergy |
| aps_daily_plan | 日计划 |
| aps_daily_plan_0402 | 日计划 |
| aps_daily_plan_0412 | 日计划 |
| aps_daily_plan_hb | 日计划 |
| aps_demand_manage | 需求管理 |
| aps_demand_management | 年/月计划需求管理 |
| aps_inspect_checklist | 齐套检查 |
| aps_kpwth_ebs | 开票未提货 |
| aps_lack_material_detail | 缺料详情 |
| aps_mark_demand_submit | 年/月计划市场需求提报 |
| aps_mark_req_submit | 市场需求提报 |
| aps_mark_req_submit_audit | 市场需求提报审核表 |
| aps_mark_req_submit_cycle | 市场需求提报-销售周期设置 |
| aps_material_needs_plan | 物料需求计划汇总表 |
| aps_monthly_check | 月度检查 |
| aps_monthly_material_demand | 月度物料需求 |
| aps_monthly_material_needs_plan | 月度物料需求计划结果展示表 |
| aps_plan_scheduling | 计划排程 |
| aps_production_budget | 期间生产预算 |
| aps_relative_plan | 预混料计划 |
| aps_season_allocation | 调料分配 |
| aps_season_audit | 调料审核 |
| aps_season_audit_datas | 调料数据审核表 |
| aps_selftesting_explanation | 自测因素说明 |
| aps_supply_class | 供应分类 |
| aps_supply_class_item | 供应分类-明细 |
| aps_supply_classify | 供应分类明细 |
| aps_tech_param_cate | 工艺参数分类 |
| aps_unplanned_order | 未排计划单 |
| aps_year_demand_management | 年计划需求管理 |
| aps_year_demand_submit | 年/月计划市场需求提报 |
| aps_year_season_allocation_detail | 年调料计划 |

## 业务域概览

- **aps** (37张表)：需求管理/主生产计划/车间排程/产能规划/能源预算

---

[[通威农发-数据库总览]]

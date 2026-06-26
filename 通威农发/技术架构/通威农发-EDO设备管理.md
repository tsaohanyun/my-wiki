---
author: Hermes Wiki Agent
confidence: high
created: 2026-05-07
description: EDO（Equipment & Device Operation）设备管理模块，涵盖设备全生命周期管理，包括设备台账、故障维修、预防性维护、点检巡检、备件管理、特种设备管理等功能。
project: 通威农发
sources:
- raw/
status: published
tags:
- smart-manufacturing
title: EDO设备管理
type: concept
updated: 2026-05-28
version: 1.0.20260529
---




# EDO设备管理


> 项目：**通威农发**（通威股份农业发展有限公司）
>
> 相关Wiki：[数据库总览](通威农发-数据库总览.md) | [资产管理EAM与设备](通威农发-资产管理EAM与设备.md) | [IIoT工业物联网](通威农发-IIoT工业物联网.md) | [产能利用率](通威农发-产能利用率.md)
## 模块简介

EDO（Equipment & Device Operation）设备管理模块，涵盖设备全生命周期管理，包括设备台账、故障维修、预防性维护、点检巡检、备件管理、特种设备管理等功能。

## 表清单（共119张表）

| 表名 | 说明 |
|------|------|
| edo_api_account_extend |  |
| edo_api_account_extend_details |  |
| edo_approval_role_configuration |  |
| edo_base |  |
| edo_cc_role_configuration |  |
| edo_daily_for_mes_log |  |
| edo_daily_maintenance_calibration |  |
| edo_daily_maintenance_calibration_details |  |
| edo_daily_maintenance_calibration_operate |  |
| edo_daily_maintenance_plan |  |
| edo_daily_maintenance_plan_details |  |
| edo_daily_maintenance_plan_operate |  |
| edo_daily_maintenance_record |  |
| edo_daily_maintenance_record_attach |  |
| edo_daily_maintenance_record_details |  |
| edo_daily_maintenance_record_operate |  |
| edo_data_assembler_service |  |
| edo_equip_account | 设备台账主表，含核定产能(t/h)、设计产能(t/h)、核定时产量等产能参数 |
| edo_equip_account_bom |  |
| edo_equip_att |  |
| edo_equip_bom |  |
| edo_equip_change |  |
| edo_equip_funct_location |  |
| edo_equip_logo |  |
| edo_equip_model_bom |  |
| edo_equip_param |  |
| edo_equip_record |  |
| edo_equipment_account_tree |  |
| edo_equipment_product_name |  |
| edo_equipment_record |  |
| edo_equipment_standard_name |  |
| edo_fault_knowledge_base |  |
| edo_fault_knowledge_base_attach |  |
| edo_fault_maintenance_order |  |
| edo_fault_maintenance_order_attach |  |
| edo_fault_maintenance_order_item |  |
| edo_fault_phenomenon |  |
| edo_fault_phenomenon_details |  |
| edo_fault_reason |  |
| edo_fault_type |  |
| edo_file_management |  |
| edo_file_management_tree |  |
| edo_filing_accessories_management |  |
| edo_filing_accessories_management_record |  |
| edo_filing_accessories_management_work_order |  |
| edo_filing_accessories_warning_days_unused |  |
| edo_fixed_asset_account |  |
| edo_machine_and_material_procurement_plan |  |
| edo_machine_and_material_procurement_plan_details |  |
| edo_machine_and_material_procurement_plan_summary |  |
| edo_machine_material_master_data |  |
| edo_machine_material_master_data_attr |  |
| edo_management_weekly_meeting |  |
| edo_management_weekly_meeting_details |  |
| edo_management_weekly_meeting_plan |  |
| edo_measuring_equipment_account_calibration |  |
| edo_measuring_equipment_account_record |  |
| edo_measuring_equipment_account_record_attach |  |
| edo_month_maintenance_calibration |  |
| edo_month_maintenance_calibration_details |  |
| edo_month_maintenance_calibration_details_item |  |
| edo_month_maintenance_calibration_operate |  |
| edo_month_maintenance_plan |  |
| edo_month_maintenance_plan_details |  |
| edo_month_maintenance_plan_item |  |
| edo_month_maintenance_plan_operate |  |
| edo_month_maintenance_record |  |
| edo_month_maintenance_record_attach |  |
| edo_month_maintenance_record_details |  |
| edo_month_maintenance_record_item |  |
| edo_month_maintenance_record_item_use |  |
| edo_month_maintenance_record_operate |  |
| edo_performance_testing |  |
| edo_performance_testing_attach |  |
| edo_performance_testing_details |  |
| edo_performance_testing_details_gl |  |
| edo_personnel_ledger |  |
| edo_personnel_ledger_order |  |
| edo_personnel_ledger_order_attach |  |
| edo_procurement_demand_resource_pool |  |
| edo_procurement_demand_resource_pool_details |  |
| edo_requirement_task_pool |  |
| edo_requirement_task_pool_item |  |
| edo_requisition_attach |  |
| edo_requisition_from |  |
| edo_requisition_materials |  |
| edo_return_order_record |  |
| edo_save_equip_account_info |  |
| edo_section |  |
| edo_service_procurement_demand_plan |  |
| edo_service_procurement_demand_plan_details |  |
| edo_service_procurement_demand_plan_document |  |
| edo_special_equipment_account_calibration |  |
| edo_special_equipment_account_record |  |
| edo_special_equipment_account_record_attach |  |
| edo_special_equipment_safe_account |  |
| edo_special_person_config |  |
| edo_station_stop_plan |  |
| edo_station_stop_plan_time |  |
| edo_station_stop_plan_tree |  |
| edo_storage_log |  |
| edo_tpm_maintenance_standards |  |
| edo_tpm_maintenance_standards_attach |  |
| edo_tpm_maintenance_standards_details |  |
| edo_work_flow |  |
| edo_year_maintenance_calibration |  |
| edo_year_maintenance_calibration_details |  |
| edo_year_maintenance_calibration_details_item |  |
| edo_year_maintenance_calibration_operate |  |
| edo_year_maintenance_plan |  |
| edo_year_maintenance_plan_details |  |
| edo_year_maintenance_plan_item |  |
| edo_year_maintenance_plan_operate |  |
| edo_year_maintenance_record |  |
| edo_year_maintenance_record_attach |  |
| edo_year_maintenance_record_details |  |
| edo_year_maintenance_record_item |  |
| edo_year_maintenance_record_item_use |  |
| edo_year_maintenance_record_operate |  |

## 相关页面

- [数据库总览](通威农发-数据库总览.md) — 数据库总览
- [产能利用率](通威农发-产能利用率.md) — 跨模块专题：设备产能参数分析与利用率统计

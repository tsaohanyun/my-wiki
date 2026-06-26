---
author: Hermes Wiki Agent
confidence: high
created: 2026-05-07
description: MES（Manufacturing Execution System）生产执行模块，涵盖配料管理（配料单/配盘/投料）、工单管理（生产工单/报工/清洗工单）、生产过程控制（工序流转/状态跟踪）、打包管理（打包工单/称重）、领料管理、生产退料等功能。
project: 通威
sources:
- raw/
status: published
tags:
- smart-manufacturing
title: MES生产执行
type: concept
updated: 2026-05-28
version: 1.0.20260528
---



# MES生产执行


> 项目：**通威农发**（通威股份农业发展有限公司）
>
> 相关Wiki：[数据库总览](通威农发-数据库总览.md) | [QMS质量管理](通威农发-QMS质量管理.md) | [WMS仓储管理](通威农发-WMS仓储管理.md) | [APS计划排程](通威农发-APS计划排程.md)
## 模块简介

MES（Manufacturing Execution System）生产执行模块，涵盖配料管理（配料单/配盘/投料）、工单管理（生产工单/报工/清洗工单）、生产过程控制（工序流转/状态跟踪）、打包管理（打包工单/称重）、领料管理、生产退料等功能。

## 表清单（共158张表）

| 表名 | 说明 |
|------|------|
| mes_base_batching |  |
| mes_base_check_config |  |
| mes_base_classes |  |
| mes_base_classes_rest |  |
| mes_base_conaming |  |
| mes_base_conaming_item |  |
| mes_base_config_op |  |
| mes_base_crenel |  |
| mes_base_crenel_line |  |
| mes_base_ebs_config |  |
| mes_base_formula_rule |  |
| mes_base_material_feeder |  |
| mes_base_material_sa |  |
| mes_base_material_sac |  |
| mes_base_material_special |  |
| mes_base_performance_standard |  |
| mes_base_position |  |
| mes_base_post |  |
| mes_base_post_operation |  |
| mes_base_premix_config |  |
| mes_base_process_molding |  |
| mes_base_product_line |  |
| mes_base_record_code |  |
| mes_base_scale |  |
| mes_base_scheduling |  |
| mes_base_scheduling_item |  |
| mes_base_scheduling_person |  |
| mes_base_schneider_section_association_equipment |  |
| mes_base_shift |  |
| mes_base_show_point |  |
| mes_base_standard |  |
| mes_base_steam_convert |  |
| mes_base_task |  |
| mes_base_team |  |
| mes_base_tech |  |
| mes_base_tech_premix |  |
| mes_base_unscheduing |  |
| mes_base_warehouse_config |  |
| mes_base_warehouse_item |  |
| mes_base_weighing_attr |  |
| mes_base_workshop_area |  |
| mes_base_workshop_silo |  |
| mes_base_workshop_warehouse |  |
| mes_base_workshop_wp |  |
| mes_batching_store_snd |  |
| mes_bom_adjust_audit_role |  |
| mes_bom_adjust_audit_t |  |
| mes_bom_adjust_record |  |
| mes_bom_adjust_record_item |  |
| mes_calibration_record |  |
| mes_clean_mateial |  |
| mes_clean_processdesc |  |
| mes_clean_record |  |
| mes_clean_record_usage |  |
| mes_config_area |  |
| mes_config_distributing |  |
| mes_distributing_abn |  |
| mes_distributing_item |  |
| mes_distributing_item_0411 |  |
| mes_distributing_t |  |
| mes_distributing_t_0411 |  |
| mes_energy_team_use |  |
| mes_energy_team_use_item |  |
| mes_equipment_exception_log |  |
| mes_exe_factory_db_config |  |
| mes_exe_sync_record |  |
| mes_iot_machine_record |  |
| mes_iot_machine_t |  |
| mes_iot_property_value_record |  |
| mes_iot_subscribe_config |  |
| mes_iot_subscribe_property |  |
| mes_iot_tech_t |  |
| mes_iot_web_socket_message |  |
| mes_monthly_calibrate_abn |  |
| mes_picking_apply |  |
| mes_picking_apply1 |  |
| mes_picking_apply_0411 |  |
| mes_picking_apply_item |  |
| mes_picking_record |  |
| mes_picking_record1 |  |
| mes_picking_record_0411 |  |
| mes_produce_standard_setup |  |
| mes_product_process |  |
| mes_product_process_basic |  |
| mes_product_process_hour |  |
| mes_product_process_mold |  |
| mes_product_process_param |  |
| mes_product_process_routing |  |
| mes_product_process_task |  |
| mes_production_manage |  |
| mes_production_plan |  |
| mes_production_plan_item |  |
| mes_scheduling_energy_consume |  |
| mes_shift_note |  |
| mes_shift_record |  |
| mes_shift_submit |  |
| mes_shift_view_records |  |
| mes_shift_workorder |  |
| mes_subpackage_item |  |
| mes_subpackage_t |  |
| mes_task_feeding |  |
| mes_task_feeding_item |  |
| mes_task_pool |  |
| mes_task_record |  |
| mes_task_todo |  |
| mes_tech_feeder |  |
| mes_tech_feeder_define |  |
| mes_tech_feeder_snd |  |
| mes_tech_process |  |
| mes_tech_process_hour |  |
| mes_tech_process_mold |  |
| mes_tech_process_param |  |
| mes_tech_process_routing |  |
| mes_tech_process_snd |  |
| mes_tech_process_task |  |
| mes_tech_process_version |  |
| mes_tech_standard_item |  |
| mes_tech_standard_temp |  |
| mes_tech_worksection |  |
| mes_use_desc |  |
| mes_workorder_batch |  |
| mes_workorder_batching |  |
| mes_workorder_batching_record |  |
| mes_workorder_bom |  |
| mes_workorder_bom_0411 |  |
| mes_workorder_bom_bl |  |
| mes_workorder_bom_item |  |
| mes_workorder_cancel_record |  |
| mes_workorder_consume |  |
| mes_workorder_correspondence |  |
| mes_workorder_energy |  |
| mes_workorder_energy_consume |  |
| mes_workorder_feeding |  |
| mes_workorder_feeding_0411 |  |
| mes_workorder_feeding_batch |  |
| mes_workorder_feeding_batch_0411 |  |
| mes_workorder_mold |  |
| mes_workorder_occupy |  |
| mes_workorder_output |  |
| mes_workorder_output_0411 |  |
| mes_workorder_pack_rule |  |
| mes_workorder_process_basic |  |
| mes_workorder_process_energy |  |
| mes_workorder_process_energy_son |  |
| mes_workorder_process_hour |  |
| mes_workorder_process_mold |  |
| mes_workorder_process_param |  |
| mes_workorder_process_routing |  |
| mes_workorder_process_task |  |
| mes_workorder_resource_consume |  |
| mes_workorder_resource_item |  |
| mes_workorder_reworkhf |  |
| mes_workorder_sa_version |  |
| mes_workorder_status |  |
| mes_workorder_status_compare |  |
| mes_workorder_t |  |
| mes_workorder_water |  |
| mes_workorder_workrecord |  |

## 相关页面

- [MES生产执行](通威农发-数据库总览.md) — 数据库总览

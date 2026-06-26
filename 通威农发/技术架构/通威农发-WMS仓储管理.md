---
author: Hermes Wiki Agent
confidence: high
created: 2026-05-07
description: WMS（Warehouse Management System）仓储管理模块，负责通威农发各工厂/公司的仓库全流程管理。涵盖入库管理（ASN送货单/收货单/验收）、出库管理（发运单/计划销售单/装车）、库存管理（库存原子结构/库存批次/库存移动/调整/预警）、拣货管理（拣货明细/波次）、盘点管理（盘点计划/盘点单/盘点配置）、投料退料（投料任务/生产退料/消耗退料）、不合格品管理（NG库存/不合格
project: 通威
sources:
- raw/
status: published
tags:
- smart-manufacturing
title: WMS仓储管理
type: concept
updated: 2026-05-28
version: 1.0.20260528
---



# WMS仓储管理


> 项目：**通威农发**（通威股份农业发展有限公司）
>
> 相关Wiki：[数据库总览](通威农发-数据库总览.md) | [物流执行LES与WHM](通威农发-物流执行LES与WHM.md) | [MES生产执行](通威农发-MES生产执行.md)
## 模块简介

WMS（Warehouse Management System）仓储管理模块，负责通威农发各工厂/公司的仓库全流程管理。涵盖入库管理（ASN送货单/收货单/验收）、出库管理（发运单/计划销售单/装车）、库存管理（库存原子结构/库存批次/库存移动/调整/预警）、拣货管理（拣货明细/波次）、盘点管理（盘点计划/盘点单/盘点配置）、投料退料（投料任务/生产退料/消耗退料）、不合格品管理（NG库存/不合格品处置）、以及上架策略、地标设置、调拨管理、数据归档等基础配置功能。

## 表清单（共183张表）

| 表名 | 说明 |
|------|------|
| wms_asn_order |  |
| wms_asn_order2024 |  |
| wms_asn_order_detail |  |
| wms_asn_order_detail2024 |  |
| wms_asn_order_detail_image |  |
| wms_asn_order_oc |  |
| wms_asn_receive_detail_code_disk |  |
| wms_asn_receive_detail_code_disk2024 |  |
| wms_asn_receive_order_detail |  |
| wms_asn_receive_order_detail2024 |  |
| wms_bulk_material_scheduling |  |
| wms_bulk_material_scheduling_stock_record |  |
| wms_bulk_material_scheduling_submit_record |  |
| wms_data_assembler_service |  |
| wms_dispatch_order |  |
| wms_dispatch_order2025 |  |
| wms_dispatch_order_detail |  |
| wms_dispatch_order_detail2025 |  |
| wms_ext_acceptance_order |  |
| wms_ext_account |  |
| wms_ext_account_alias |  |
| wms_ext_account_alias_detail |  |
| wms_ext_account_alias_detail_stock |  |
| wms_ext_adjust_ebs_stock |  |
| wms_ext_adjustment |  |
| wms_ext_adjustment_attr |  |
| wms_ext_adjustment_attr_detail |  |
| wms_ext_adjustment_detail |  |
| wms_ext_alias_config |  |
| wms_ext_allot_factory_config |  |
| wms_ext_antenna |  |
| wms_ext_app_config |  |
| wms_ext_app_menus_config |  |
| wms_ext_app_role_menus_config |  |
| wms_ext_apply_order |  |
| wms_ext_apply_order_detail |  |
| wms_ext_archiving_allow_truncate_table |  |
| wms_ext_archiving_process |  |
| wms_ext_archiving_process_detail |  |
| wms_ext_archiving_process_detail_task |  |
| wms_ext_archiving_process_task |  |
| wms_ext_archiving_table_config |  |
| wms_ext_archiving_table_detail_record |  |
| wms_ext_archiving_table_detail_record_process |  |
| wms_ext_archiving_table_detail_step_record |  |
| wms_ext_archiving_table_param_config |  |
| wms_ext_archiving_table_step_config |  |
| wms_ext_asn_disk_op_log |  |
| wms_ext_asn_dock_task |  |
| wms_ext_asn_loc_dx |  |
| wms_ext_asn_pounds_rule |  |
| wms_ext_attendance_user |  |
| wms_ext_card_reader |  |
| wms_ext_child_wave |  |
| wms_ext_common_config_record |  |
| wms_ext_copy_common_config |  |
| wms_ext_dim_record_log |  |
| wms_ext_dim_record_log_before_one_month |  |
| wms_ext_duplicate_item |  |
| wms_ext_ebs_push_retry_api |  |
| wms_ext_ebs_stock_atom |  |
| wms_ext_ebs_stock_atom_zzk |  |
| wms_ext_ebs_vehicle |  |
| wms_ext_emergency |  |
| wms_ext_emergency_detail |  |
| wms_ext_erp_lot_update_record |  |
| wms_ext_factory_allot_order |  |
| wms_ext_factory_allot_order_detail |  |
| wms_ext_factory_allot_stock_detail |  |
| wms_ext_feed_return_order |  |
| wms_ext_feed_return_order_detail |  |
| wms_ext_feed_task |  |
| wms_ext_feed_task_detail |  |
| wms_ext_filter_sync_ou_code |  |
| wms_ext_forklift |  |
| wms_ext_hold_order |  |
| wms_ext_hold_order_detail |  |
| wms_ext_inbound_data_import_temp |  |
| wms_ext_inbound_exception_reg |  |
| wms_ext_interface_control |  |
| wms_ext_interface_control_record |  |
| wms_ext_inventory |  |
| wms_ext_inventory_bulk_materials_detail |  |
| wms_ext_inventory_detail |  |
| wms_ext_inventory_detail_stock_record |  |
| wms_ext_inventory_param_config |  |
| wms_ext_inventory_plan |  |
| wms_ext_inventory_plan_area |  |
| wms_ext_inventory_plan_loc |  |
| wms_ext_inventory_plan_sku |  |
| wms_ext_inventory_plan_sub_library |  |
| wms_ext_inventory_workshop_detail |  |
| wms_ext_landmark |  |
| wms_ext_lock_id |  |
| wms_ext_loss_record |  |
| wms_ext_machinery_order_assist_info |  |
| wms_ext_material_process |  |
| wms_ext_material_process_detail |  |
| wms_ext_move_order |  |
| wms_ext_move_order_detail |  |
| wms_ext_ncounter |  |
| wms_ext_ng_import_temp |  |
| wms_ext_ng_order_disposal_middle |  |
| wms_ext_ng_order_disposal_record |  |
| wms_ext_ng_order_stock_op_log |  |
| wms_ext_ng_order_xh_disposal_middle |  |
| wms_ext_ng_stock_order |  |
| wms_ext_ng_stock_order_detail |  |
| wms_ext_ng_stock_order_fix1125 |  |
| wms_ext_ng_stock_problem_record |  |
| wms_ext_ng_sub_library |  |
| wms_ext_org |  |
| wms_ext_part_md |  |
| wms_ext_plan_order |  |
| wms_ext_plan_order_detail |  |
| wms_ext_plan_order_detail_label |  |
| wms_ext_plan_order_detail_pounds |  |
| wms_ext_plate_number_led |  |
| wms_ext_purchase_returns_plan |  |
| wms_ext_qms_pound_record |  |
| wms_ext_rec_team_record |  |
| wms_ext_refer_all_invalid_date |  |
| wms_ext_region |  |
| wms_ext_req_custom_param |  |
| wms_ext_req_last_time |  |
| wms_ext_return_order_apply |  |
| wms_ext_sale_vehicle |  |
| wms_ext_sale_vehicle_order_detail |  |
| wms_ext_scene_setting |  |
| wms_ext_scrap_record |  |
| wms_ext_shelf_strategy |  |
| wms_ext_shelf_strategy_step |  |
| wms_ext_shelf_strategy_step_rule |  |
| wms_ext_split_table |  |
| wms_ext_stack_log |  |
| wms_ext_stock_equals |  |
| wms_ext_stock_equals_zzk |  |
| wms_ext_system_config_model |  |
| wms_ext_task_controls |  |
| wms_ext_transaction |  |
| wms_ext_transaction2024 |  |
| wms_ext_transaction2025 |  |
| wms_ext_translate |  |
| wms_ext_unit_convert |  |
| wms_ext_update_stock_state_apply |  |
| wms_ext_update_stock_state_apply_detail |  |
| wms_ext_w2t_api_interface_data |  |
| wms_ext_w2t_api_interface_data2025 |  |
| wms_ext_waring_scan_fail_log |  |
| wms_ext_wave |  |
| wms_ext_wave_deliver |  |
| wms_ext_work_shop_ng_item_transaction |  |
| wms_ext_work_shop_report_work_record |  |
| wms_ext_xhth_config |  |
| wms_ext_xxjob_task_record |  |
| wms_iface_log |  |
| wms_iface_log2024 |  |
| wms_iface_log2025 |  |
| wms_iface_log_temp |  |
| wms_lot_delay |  |
| wms_materialbatch_workorder_all |  |
| wms_materialbatch_workorder_fg |  |
| wms_order_attendance_info |  |
| wms_period |  |
| wms_period_detail |  |
| wms_period_out |  |
| wms_pick_detail |  |
| wms_pick_detail2025 |  |
| wms_purchase_order |  |
| wms_purchase_order_detail |  |
| wms_sales_count |  |
| wms_stock_atom |  |
| wms_stock_atom2024 |  |
| wms_stock_atom2025 |  |
| wms_stock_attr |  |
| wms_stock_attr2024 |  |
| wms_stock_attr2025 |  |
| wms_stock_config |  |
| wms_stock_warn |  |
| wms_stock_warn_temp |  |
| wms_sub_library_transfer_detail_request |  |
| wms_sub_library_transfer_request |  |
| wms_user_sub_library |  |

## 相关页面

- [WMS仓储管理](通威农发-数据库总览.md) — 数据库总览

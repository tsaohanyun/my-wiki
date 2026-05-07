---
title: 通威农发-ST与MI
created: 2026-05-07
updated: 2026-05-07
type: concept
tags: [数据库, 通威农发, st, mi, 统计, 制造智能]
confidence: high
---

# 通威农发-ST与MI

## 模块简介

ST（Statistics）统计分析与 MI（Manufacturing Intelligence）制造智能模块，是通威农发智能制造平台中面向数据分析与智能决策的核心模块。

- **ST 模块**（统计分析）：负责质量检验统计、投入产出分析、批次质量跟踪、设备运行分析、库存跟踪等统计分析功能，涵盖 QMS 质量管理系统相关的统计报表和中间计算表。
- **MI 模块**（制造智能）：提供制造智能基础能力，包括预警规则与任务管理、设备测点与监控、数据填报模型、数据集与数据源管理、IDA（智能设计分析）2D/3D 设计器、文件管理等基础设施。

---

## 一、ST 模块数据表

共 42 张表，按表名字母顺序排列。

| 表名 | COMMENT注释 |
|------|-------------|
| st_batcth_quality_result_fg | 物料批检验结果表 |
| st_batcth_quality_result_fg_1 | 报表_物料批检验结果表1 |
| st_batcth_quality_result_process | 质量批次过程结果 |
| st_batcth_quality_result_raw | 原料批次结果 |
| st_crudeprotein_pct | 批次蛋白 |
| st_enterprise_online | 上线企业ID表游标用 |
| st_equip_quantity_count | 设备数量统计 |
| st_equipment_reliability_count | 设备可靠性统计 |
| st_materialbatch_manufacture_in | 投入产出比计算成品产出数量表 |
| st_materialbatch_manufacture_in2 | 投入产出比计算成品产出数量补充表 |
| st_materialbatch_manufacture_out | 投入产出比计算投入数量表 |
| st_materialbatch_manufacture_out2 | 投入产出比消耗计算表 |
| st_materialbatch_manufacture_out_1 | 报表_投入产出比计算投入数量表1 |
| st_materialbatch_manufacture_period | 投入产出比计算投入数量上线月 |
| st_materialbatch_workorder_fg | 物料批工单 |
| st_materialbatch_workorder_fg_1 | 报表_WMS成品产出物料批与工单关联关系表1 |
| st_mes_distributing | 配盘明细中间表 |
| st_ng_disposal_code | 不合格品处置记录 |
| st_proc_inspect_check_summary | 工序检验点检汇总 |
| st_qms_completion_rate_item | 质量检验项统计 |
| st_qms_concent_item_qc | qms项目QC |
| st_qms_inventory_c | QMS库存统计表 |
| st_qms_inventory_track | 在库库存跟踪查询表 |
| st_qms_inventory_track_outdate | 在库库存最大出库日期表 |
| st_qms_inventory_track_outdate_detail | 在库库存最大出库日期明细表 |
| st_qms_inventory_y | 原料批次对应采购入库量 |
| st_qms_inventory_y_detail | 原料批次对应采购入库量明细表 |
| st_qms_output_c | 成品物料批生产产量表-班组 |
| st_qms_receive_order | 收料单 |
| st_qms_receive_order_1 | 报表_质量表1 |
| st_qms_receive_sampling | 抽样情况查询表-LPN |
| st_qms_receive_sampling_count | 质检抽样统计分析报表 |
| st_rework_material_in | 完工入出库统计 |
| st_runtime_analysis_headquarters | 运行时间分析-总部 |
| st_runtime_analysis_team | 运行时间分析-班组 |
| st_water_pct | 物料批水分结果 |
| st_water_pct_1 | 报表_批次水分表1 |
| st_water_pct_code | 物料批次水分报表 |
| st_wms_enterprise_year_online | wms业务表游标用 |
| st_wms_incoming_batch | 来料批次表--汇总 |
| st_wms_inout_inventory_c | 成品收支存中间表 |
| st_wms_receive_firstime | 原料批次最早入库时间 |

---

## 二、MI 模块数据表

共 38 张表，按表名字母顺序排列。

| 表名 | COMMENT注释 |
|------|-------------|
| mi_alarm_msg | 预警消息 |
| mi_alarm_rule | 预警规则 |
| mi_alarm_rule_tag | mi_alarm_rule_tag 与 mi_base_equipment_tag 的关联表 |
| mi_alarm_task | 预警任务 |
| mi_base_asset_ref | 资源引用 |
| mi_base_business_process | 业务流程 |
| mi_base_code_table | 码表 |
| mi_base_code_table_data | 码表数据 |
| mi_base_code_table_metadata | 键值设置 |
| mi_base_data_set | 数据集 |
| mi_base_data_set_meta | mi_base_data_set_meta |
| mi_base_data_source | 数据源 |
| mi_base_datafiller_model | mi_base_datafiller_model |
| mi_base_datafiller_model_user | mi_base_datafiller_model_user 与 rbac_user 的关联表 |
| mi_base_datafiller_temp | mi_base_datafiller_temp |
| mi_base_datafiller_view | mi_base_datafiller_view |
| mi_base_datafiller_view_user | mi_base_datafiller_view_user 与 rbac_user 的关联表 |
| mi_base_equipment_group | 测点分组 |
| mi_base_equipment_monitor | mi_base_equipment_monitor |
| mi_base_equipment_status | mi_base_equipment_status |
| mi_base_equipment_tag | 标签 |
| mi_base_equipment_testpoint | 测点 |
| mi_base_equipment_testpoint_tag | mi_base_equipment_testpoint_tag 与 mi_base_equipment_testpoint 的关联表 |
| mi_base_equipment_virtual_testpoint | 虚拟测点 |
| mi_base_file | 文件 |
| mi_base_file_history | 文件操作历史 |
| mi_base_file_usage | 文件使用情况 |
| mi_base_folder | 文件目录 |
| mi_base_group | mi_base_group |
| mi_base_parameter | 全局参数 |
| mi_ida_designer_data_source | 2D3D设计器本地数据源 |
| mi_ida_historical_attachment | IDA历史附件 |
| mi_ida_resource | 3d设计器 |
| mi_ida_resource_data_set | mi_ida_resource_data_set 与 mi_base_data_set 的关联表 |
| mi_ida_resource_free_view | mi_ida_resource_free_view |
| mi_ida_resource_quote | mi_ida_resource_quote 与 mi_ida_resource 的关联表 |
| mi_ida_resource_role | mi_ida_resource_role 与 rbac_role 的关联表 |
| mi_ida_resource_user | mi_ida_resource_user 与 rbac_user 的关联表 |

---

## 关联页面

[[通威农发-数据库总览]]

---
title: QMS质量管理
created: 2026-05-07
updated: 2026-05-28
type: concept
description: 'QMS（Quality Management System）质量管理模块，涵盖检验管理（来料检验/制程检验/成品检验/出厂检验）、不合格品管理（不合格品审理/处置）、质量追溯（批次追溯/物料追踪）、取样管理、样品检测、质量标准配置等功能。'
tags:
- smart-manufacturing
sources:
- raw/
confidence: high
project: 通威
---


# QMS质量管理


> 项目：**通威农发**（通威股份农业发展有限公司）
>
> 相关Wiki：[数据库总览](通威农发-数据库总览.md) | [MES生产执行](通威农发-MES生产执行.md) | [报表预处理中间表](通威农发-报表预处理中间表.md)
## 模块简介

QMS（Quality Management System）质量管理模块，涵盖检验管理（来料检验/制程检验/成品检验/出厂检验）、不合格品管理（不合格品审理/处置）、质量追溯（批次追溯/物料追踪）、取样管理、样品检测、质量标准配置等功能。

## 表清单（共147张表）

| 表名 | 说明 |
|------|------|
| qms_apply_batch_status |  |
| qms_apply_cancel |  |
| qms_apply_config |  |
| qms_apply_inspection |  |
| qms_apply_inspection_element |  |
| qms_apply_point |  |
| qms_apply_point_item |  |
| qms_apply_process_element |  |
| qms_apply_process_record |  |
| qms_apply_push |  |
| qms_apply_reject |  |
| qms_apply_reject_parent |  |
| qms_apply_reject_parent_20250327 |  |
| qms_apply_reject_record |  |
| qms_apply_reject_record_20250327 |  |
| qms_apply_reject_son |  |
| qms_apply_reject_son_20250327 |  |
| qms_apply_rule_parent |  |
| qms_apply_rule_product |  |
| qms_apply_rule_son |  |
| qms_apply_sampling |  |
| qms_apply_sampling_20250522 |  |
| qms_apply_security |  |
| qms_apply_security_report |  |
| qms_apply_staysample |  |
| qms_apply_storage |  |
| qms_apply_t |  |
| qms_apply_t_20250806 |  |
| qms_apply_t_250314 |  |
| qms_apply_track_record |  |
| qms_apply_validity_record |  |
| qms_base_checkfactory |  |
| qms_base_degree_attribute |  |
| qms_base_degree_type |  |
| qms_base_element |  |
| qms_base_element_capacity |  |
| qms_base_element_lims |  |
| qms_base_element_lims_relation |  |
| qms_base_element_lims_unit |  |
| qms_base_element_price |  |
| qms_base_element_relation |  |
| qms_base_element_relation_250303 |  |
| qms_base_element_targettype |  |
| qms_base_elementtext |  |
| qms_base_elementtype |  |
| qms_base_judgetype |  |
| qms_base_material_producedate |  |
| qms_base_method |  |
| qms_base_operatype |  |
| qms_base_operatype_large |  |
| qms_base_post_track |  |
| qms_base_print_template |  |
| qms_base_record_config_t |  |
| qms_base_reviewtype |  |
| qms_base_standard_file |  |
| qms_base_standard_moisture_analysis |  |
| qms_base_standard_type |  |
| qms_base_unit |  |
| qms_base_usage_attribute |  |
| qms_base_usage_class |  |
| qms_base_usage_classification |  |
| qms_base_usage_material |  |
| qms_base_validity_period |  |
| qms_base_validity_period_2025016 |  |
| qms_base_validity_period_20250421 |  |
| qms_base_work_element |  |
| qms_base_work_section |  |
| qms_batc_dispose |  |
| qms_batc_dispose_0627 |  |
| qms_batc_dispose_2025_2_24 |  |
| qms_batc_dispose_duty |  |
| qms_batc_dispose_rule |  |
| qms_batc_expiration_record |  |
| qms_batc_material |  |
| qms_batc_material_20250522 |  |
| qms_batc_material_20250603 |  |
| qms_batc_material_20250902 |  |
| qms_batc_material_element |  |
| qms_batc_status |  |
| qms_batc_workorder |  |
| qms_contract_t |  |
| qms_data_assembler_service |  |
| qms_inventory_c |  |
| qms_plan_security_item |  |
| qms_plan_security_t |  |
| qms_programe_business_standard |  |
| qms_programe_element |  |
| qms_programe_element_20250421 |  |
| qms_programe_element_20250804 |  |
| qms_programe_element_num |  |
| qms_programe_element_period |  |
| qms_programe_element_record |  |
| qms_programe_element_standard |  |
| qms_programe_element_standard_20250421 |  |
| qms_programe_element_standard_20250804 |  |
| qms_programe_import_config |  |
| qms_programe_inspection |  |
| qms_programe_inspection_element |  |
| qms_programe_material |  |
| qms_programe_period |  |
| qms_programe_point |  |
| qms_programe_point_element |  |
| qms_programe_price_standard |  |
| qms_programe_process |  |
| qms_programe_process_element |  |
| qms_programe_process_element_standrad |  |
| qms_programe_relation_parent |  |
| qms_programe_relation_parent_20250421 |  |
| qms_programe_relation_parent_20250804 |  |
| qms_programe_relation_son |  |
| qms_programe_relation_son_20250421 |  |
| qms_programe_relation_son_20250804 |  |
| qms_programe_review_standard |  |
| qms_programe_source_standard |  |
| qms_programe_version |  |
| qms_programe_version_20250421 |  |
| qms_programe_version_20250804 |  |
| qms_programe_version_name |  |
| qms_review_options |  |
| qms_review_record_element |  |
| qms_review_res_department |  |
| qms_review_unqualified_assort |  |
| qms_review_unqualified_duty |  |
| qms_review_unqualified_reason |  |
| qms_review_use_programe |  |
| qms_sampleassay_parent |  |
| qms_sampleassay_security_plan |  |
| qms_sampleassay_security_plan_item |  |
| qms_sampleassay_son |  |
| qms_sampleassay_son_0411 |  |
| qms_sampleassay_son_collect |  |
| qms_sampleassay_son_collect_0411 |  |
| qms_sampleassay_son_item |  |
| qms_sampleassay_son_item_0411 |  |
| qms_sampleassay_son_standard |  |
| qms_sampleassay_son_standard_0411 |  |
| qms_sampleassay_son_standard_20250427 |  |
| qms_sampleassay_stay |  |
| qms_sampleassay_stay_record |  |
| qms_sampling_parent |  |
| qms_sampling_son |  |
| qms_standard_duty |  |
| qms_standard_rework |  |
| qms_task_track |  |
| qms_task_track_no |  |
| qms_task_track_record |  |
| qms_task_track_timeout |  |

## 相关页面

- [QMS质量管理](通威农发-数据库总览.md) — 数据库总览

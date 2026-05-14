---
title: MI制造智能
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, mi, 制造智能]
confidence: high
---

# MI制造智能

## 模块简介

MI（Manufacturing Intelligence）制造智能模块，提供通威农发工厂级的智能分析和数据可视化能力。涵盖预警管理（预警规则/预警记录/预警推送）、测点管理（测点配置/测点数据）、数据填报（填报模板/填报记录）、IDA设计器（数据采集分析/报表配置）等功能。

## 表清单（共38张表）

| 表名 | 说明 |
|------|------|
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

## 业务域概览

- **mi** (38张表)：预警管理/测点管理/数据填报/IDA设计器

---

[[通威农发-数据库总览]]

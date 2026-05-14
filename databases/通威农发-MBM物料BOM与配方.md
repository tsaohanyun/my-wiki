---
title: MBM物料BOM与配方
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, mbm, 物料BOM]
confidence: high
---

# MBM物料BOM与配方

## 模块简介

MBM（Material & BOM Management）物料BOM与配方管理模块。涵盖物料主数据维护、BOM（Bill of Materials）配方结构管理、配方版本控制、配方审批流程、物料替代关系、BOM成本核算等功能。

## 表清单（共26张表）

| 表名 | 说明 |
|------|------|
| mbm_custom_field | 自定义数据字段 |
| mbm_custom_option | 自定义选项 |
| mbm_equip_account_custom_field | 设备台账自定义数据字段 |
| mbm_equip_custom_field | 设备自定义数据字段 |
| mbm_equip_custom_field_conf | mbm_equip_custom_field_conf 与 mbm_equip_custom_field 的关联表 |
| mbm_qms_base_statistical_coefficient | 统计系数主表 |
| mbm_qms_base_statistical_coefficient_detail | 统计系数子表 |
| mbm_qms_data_work_flow_config | 流程配置 |
| mbm_qms_data_workflow_message_policy | 流程配置-消息推送策略 |
| mbm_qms_spc_control_chart_alert_record | SPC预警记录 |
| mbm_qms_spc_control_chart_alert_record_chart_info | 关联数据 |
| mbm_qms_spc_control_chart_db | SPC数据源 |
| mbm_qms_spc_control_chart_db_cfg | SPC数据源配置 |
| mbm_qms_spc_control_chart_def | SPC控制图定义 |
| mbm_qms_spc_control_chart_group_fid | SPC控制图定义-分组维度 |
| mbm_qms_spc_control_chart_layer_condition | SPC-控制图定义-层别条件 |
| mbm_qms_spc_control_chart_log_record | SPC日志记录 |
| mbm_qms_spc_control_chart_monitor_item | SPC监控项目 |
| mbm_qms_spc_control_chart_platform | SPC检验站台和定义的关联表 |
| mbm_qms_spc_control_chart_rule | SPC控制图规则 |
| mbm_qms_spc_control_chart_run | SPC控制图运行 |
| mbm_qms_spc_control_chart_samp_counting_mock | SPC实时抽样模拟 |
| mbm_qms_spc_control_chart_samp_mock | SPC实时抽样模拟 |
| mbm_qms_spc_platform | SPC站台 |
| mbm_qms_spc_platform_message_policy | SPC站台-消息推送配置 |
| mbm_qms_spc_platform_user_config | SPC站台-用户配置 |

## 业务域概览

- **mbm** (26张表)：物料BOM/配方结构/配方版本/配方审批

---

[[通威农发-数据库总览]]

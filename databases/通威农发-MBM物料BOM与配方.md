---
title: 通威农发-MBM物料BOM与配方
created: 2026-05-07
updated: 2026-05-07
type: concept
tags: [数据库, 通威农发, mbm, formula, 物料, bom, 配方]
confidence: high
---

# 通威农发-MBM物料BOM与配方

## 模块简介

MBM物料BOM与配方管理模块涵盖通威农发智能制造体系中的物料基础数据管理（MBM）和配方管理（Formula）两大子模块。

**MBM（Material BOM Management）子模块**：负责物料BOM相关的基础数据管理，包括自定义字段配置、设备台账管理，以及SPC（统计过程控制）相关的控制图定义、数据源、预警规则、站台配置等功能，为生产过程的质量管控提供数据支撑。

**Formula（配方管理）子模块**：负责饲料配方的管理，包含营养配方定义、配方BOM表、配方自动分解规则配置（载体清单、预处理混合物配料、成品半成品关系维护、小料重量上限等），以及配方导入配置等功能。

---

## MBM 模块（物料BOM管理）

| 表名 | 注释 |
|------|------|
| mbm_custom_field | 自定义数据字段 |
| mbm_custom_option | 自定义选项 |
| mbm_equip_account_custom_field | 设备台账自定义数据字段 |
| mbm_equip_custom_field | 设备自定义数据字段 |
| mbm_equip_custom_field_conf | 与 mbm_equip_custom_field 的关联表 |
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

> MBM模块共包含 **26** 张数据表。

---

## Formula 模块（配方管理）

| 表名 | 注释 |
|------|------|
| formula_base_carrier | 配方自动分解：载体清单 |
| formula_base_mixture | 配方自动分解：预处理混合物配料 |
| formula_base_relation | 配方自动分解：成品半成品关系维护 |
| formula_base_special_material | 配方自动分解：预混料特殊配料清单 |
| formula_base_weight | 配方自动分解：小料重量上限 |
| formula_base_weight_material | 配方自动分解：小于重量上限特殊物料 |
| formula_bom_item | 配方BOM表 |
| formula_import_config | 配方导入配置 |
| formula_nutritional_multiproduct | 营养配方-多产出 |
| formula_nutritional_t | 营养配方表 |

> Formula模块共包含 **10** 张数据表。

---

[[通威农发-数据库总览]]

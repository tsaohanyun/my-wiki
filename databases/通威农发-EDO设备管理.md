---
title: EDO设备管理
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, edo, 设备管理]
confidence: high
---

# EDO设备管理

## 模块简介

EDO（Equipment & Device Operations）设备全生命周期管理模块。涵盖设备台账（设备基本信息/设备分类/设备参数）、设备维保（保养计划/保养工单/保养记录）、设备故障（故障报修/故障处理/故障分析）、设备巡检（巡检计划/巡检记录/巡检标准）、备品备件（备件库存/备件领用/备件采购）、设备能效、设备改造、计量器具等完整设备管理功能。

## 表清单（共119张表）

| 表名 | 说明 |
|------|------|
| edo_api_account_extend | 科目代码 |
| edo_api_account_extend_details | 科目代码用途 |
| edo_approval_role_configuration | 设备审批角色配置 |
| edo_base | edo_base |
| edo_cc_role_configuration | 设备审批抄送角色配置 |
| edo_daily_for_mes_log | 生产发送定标数据日志 |
| edo_daily_maintenance_calibration | 日常维保定标 |
| edo_daily_maintenance_calibration_details | 日常维保定标明细 |
| edo_daily_maintenance_calibration_operate | 日常维保定标操作记录 |
| edo_daily_maintenance_plan | 日常维保计划 |
| edo_daily_maintenance_plan_details | 日常维保计划明细 |
| edo_daily_maintenance_plan_operate | 日常维保计划操作记录 |
| edo_daily_maintenance_record | 日常维保记录 |
| edo_daily_maintenance_record_attach | 日常维保记录附件 |
| edo_daily_maintenance_record_details | 日常维保记录明细 |
| edo_daily_maintenance_record_operate | 日常维保记录操作记录 |
| edo_data_assembler_service | EDO抽取数据 |
| edo_equip_account | 设备管理VO |
| edo_equip_account_bom | 设备台账BOM |
| edo_equip_att | 设备附件 |
| edo_equip_bom | 设备型号BOM清单 |
| edo_equip_change | 设备修改记录 |
| edo_equip_funct_location | 设备功能位置 |
| edo_equip_logo | 设备台账二维码logo |
| edo_equip_model_bom | 设备BOM |
| edo_equip_param | 设备型号技术参数 |
| edo_equip_record | equipment_record |
| edo_equipment_account_tree | 设备台账组织树 |
| edo_equipment_product_name | 设备与机物料品名 |
| edo_equipment_record | edo_equipment_record |
| edo_equipment_standard_name | 设备标准名称 |
| edo_fault_knowledge_base | 故障知识库 |
| edo_fault_knowledge_base_attach | 故障知识库附件 |
| edo_fault_maintenance_order | 故障工单 |
| edo_fault_maintenance_order_attach | 故障工单附件 |
| edo_fault_maintenance_order_item | 故障工单机物料消耗记录 |
| edo_fault_phenomenon | 故障现象 |
| edo_fault_phenomenon_details | 故障类别明细 |
| edo_fault_reason | 故障原因 |
| edo_fault_type | 故障类别 |
| edo_file_management | 文档管理 |
| edo_file_management_tree | 文档管理目录 |
| edo_filing_accessories_management | 在用配件建档管理 |
| edo_filing_accessories_management_record | 配件产量记录 |
| edo_filing_accessories_management_work_order | 工单数据详情 |
| edo_filing_accessories_warning_days_unused | 配件未使用预警天数配置 |
| edo_fixed_asset_account | 固定资产台账 |
| edo_machine_and_material_procurement_plan | 机物料采购需求计划 |
| edo_machine_and_material_procurement_plan_details | 需求明细 |
| edo_machine_and_material_procurement_plan_summary | 采购明细 |
| edo_machine_material_master_data | 机物料主数据 |
| edo_machine_material_master_data_attr | 机物料主数据参数属性 |
| edo_management_weekly_meeting | 设备管理周会 |
| edo_management_weekly_meeting_details | 设备管理周会-维修明细 |
| edo_management_weekly_meeting_plan | 设备管理周会-工作计划 |
| edo_measuring_equipment_account_calibration | edo_measuring_equipment_account_calibration |
| edo_measuring_equipment_account_record | edo_measuring_equipment_account_record |
| edo_measuring_equipment_account_record_attach | 计量器具校验执行附件 |
| edo_month_maintenance_calibration | 月度维保定标 |
| edo_month_maintenance_calibration_details | 月度维保定标明细 |
| edo_month_maintenance_calibration_details_item | 月度维保定标机物料需求清单 |
| edo_month_maintenance_calibration_operate | 月度维保定标操作记录 |
| edo_month_maintenance_plan | 月度维保计划 |
| edo_month_maintenance_plan_details | 月度维保计划明细 |
| edo_month_maintenance_plan_item | 月度维保计划机物料需求清单 |
| edo_month_maintenance_plan_operate | 月度维保计划操作记录 |
| edo_month_maintenance_record | 维保执行记录 |
| edo_month_maintenance_record_attach | 月度维保记录附件 |
| edo_month_maintenance_record_details | 月度维保记录明细 |
| edo_month_maintenance_record_item | 月度维保工单机物料需求清单 |
| edo_month_maintenance_record_item_use | 月度维保工单机物料耗用记录 |
| edo_month_maintenance_record_operate | 月度维保记录操作记录 |
| edo_performance_testing | 性能测试记录 |
| edo_performance_testing_attach | 性能测试记录_附件 |
| edo_performance_testing_details | 性能测试记录_详情 |
| edo_performance_testing_details_gl | 性能测试记录_锅炉测试明细 |
| edo_personnel_ledger |  人员证件台帐 |
| edo_personnel_ledger_order |  人员证件检验记录 |
| edo_personnel_ledger_order_attach |  人员证件检验记录附件 |
| edo_procurement_demand_resource_pool | 采购需求资源池 |
| edo_procurement_demand_resource_pool_details | 采购需求资源池-来源详情 |
| edo_requirement_task_pool | 采购需求资源池 |
| edo_requirement_task_pool_item | 采购需求资源池来源明细 |
| edo_requisition_attach | 领用申请附件 |
| edo_requisition_from | 领用单 |
| edo_requisition_materials | 申请单明细 |
| edo_return_order_record | 退单记录 |
| edo_save_equip_account_info | 保存导入的设备信息 |
| edo_section | edo_section |
| edo_service_procurement_demand_plan | 服务采购需求计划 |
| edo_service_procurement_demand_plan_details | 需求明细 |
| edo_service_procurement_demand_plan_document | 附件 |
| edo_special_equipment_account_calibration | edo_special_equipment_account_calibration |
| edo_special_equipment_account_record | edo_special_equipment_account_record |
| edo_special_equipment_account_record_attach | 特种设备检验执行附件 |
| edo_special_equipment_safe_account |  特种设备及其安全附件 |
| edo_special_person_config |  特种设备及人员证件配置 |
| edo_station_stop_plan | 工段状态明细 |
| edo_station_stop_plan_time | 工段状态维护 |
| edo_station_stop_plan_tree | 工段目录 |
| edo_storage_log | 仓储修改领料单状态日志 |
| edo_tpm_maintenance_standards | TPM维保标准 |
| edo_tpm_maintenance_standards_attach | TPM维保标准附件 |
| edo_tpm_maintenance_standards_details | 维保明细 |
| edo_work_flow | 设备审批流程 |
| edo_year_maintenance_calibration | 年度维保定标 |
| edo_year_maintenance_calibration_details | 月度维保定标明细 |
| edo_year_maintenance_calibration_details_item | 年度维保定标机物料需求清单 |
| edo_year_maintenance_calibration_operate | 年度维保定标操作记录 |
| edo_year_maintenance_plan | 年度维保计划 |
| edo_year_maintenance_plan_details | 年度维保计划明细 |
| edo_year_maintenance_plan_item | 年度维保计划机物料需求清单 |
| edo_year_maintenance_plan_operate | 年度维保计划操作记录 |
| edo_year_maintenance_record | 年度维保记录 |
| edo_year_maintenance_record_attach | 年度维保记录附件 |
| edo_year_maintenance_record_details | 年度维保记录明细 |
| edo_year_maintenance_record_item | 年度维保工单机物料需求清单 |
| edo_year_maintenance_record_item_use | 年度维保工单机物料耗用记录 |
| edo_year_maintenance_record_operate | 年度维保记录操作记录 |

## 业务域概览

- **edo** (119张表)：设备台账/维保管理/故障管理/巡检管理/备品备件/设备能效

---

[[通威农发-数据库总览]]

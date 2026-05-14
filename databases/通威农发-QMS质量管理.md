---
title: QMS质量管理
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, qms, 质量管理]
confidence: high
---

# QMS质量管理

## 模块简介

QMS（Quality Management System）质量管理模块，覆盖通威农发从原料进厂到成品出厂的全流程质量管理。涵盖来料检验（IQC/进货检验/抽样方案）、过程检验（IPQC/过程巡检）、成品检验（OQC/出货检验）、不合格品管理（不合格品处置/让步接收/报废/返工）、质量追溯（批次追溯/质量档案）、质量指标统计、以及质量体系管理、客户投诉、供应商质量等扩展功能。

## 表清单（共147张表）

| 表名 | 说明 |
|------|------|
| qms_apply_batch_status | 物料批状态申请表 |
| qms_apply_cancel | 取消任务配置表 |
| qms_apply_config | 申请类型配置表 |
| qms_apply_inspection | 质量点检台账表 |
| qms_apply_inspection_element | 质量点检台账项目表 |
| qms_apply_point | 固定点位检验台账 |
| qms_apply_point_item | 固定点位检验子表 |
| qms_apply_process_element | 工序项目任务管理 |
| qms_apply_process_record | 工序任务记录表 |
| qms_apply_push | 任务推送管理 |
| qms_apply_reject | 退货检验台账表 |
| qms_apply_reject_parent | 退货单主表 |
| qms_apply_reject_parent_20250327 | 退货单主表 |
| qms_apply_reject_record | 退货单操作记录表 |
| qms_apply_reject_record_20250327 | 退货单操作记录表 |
| qms_apply_reject_son | 退货申请单子表 |
| qms_apply_reject_son_20250327 | 退货申请单子表 |
| qms_apply_rule_parent | 任务规则配置子表 |
| qms_apply_rule_product | 成品任务规则配置 |
| qms_apply_rule_son | 任务规则配置子表 |
| qms_apply_sampling | 检验台账表 |
| qms_apply_sampling_20250522 | 检验台账表 |
| qms_apply_security | 安全验证任务表 |
| qms_apply_security_report | 安全验证评价表 |
| qms_apply_staysample | 留样台账表 |
| qms_apply_storage | 库房紧急放行申请表 |
| qms_apply_t | 申请表 |
| qms_apply_t_20250806 | 申请表 |
| qms_apply_t_250314 | 申请表 |
| qms_apply_track_record | 任务跟踪记录表 |
| qms_apply_validity_record | 超期预警申请记录 |
| qms_base_checkfactory | 检验机构 |
| qms_base_degree_attribute | 用途维度-对应属性 |
| qms_base_degree_type | 用途维度 |
| qms_base_element | 检验项目 |
| qms_base_element_capacity | 检验项目检测能力 |
| qms_base_element_lims | lims检验项目 |
| qms_base_element_lims_relation | lims与dim对应关系维护 |
| qms_base_element_lims_unit | lims与dim单位转换 |
| qms_base_element_price | QmsBaseElementPrice |
| qms_base_element_relation | lims项目对应关系表 |
| qms_base_element_relation_250303 | lims项目对应关系表 |
| qms_base_element_targettype | 质量指标类型 |
| qms_base_elementtext | 检验项目对应文本值 |
| qms_base_elementtype | 检验项目类型 |
| qms_base_judgetype | 判定方式 |
| qms_base_material_producedate | 物料生产日期维护表 |
| qms_base_method | 检验方法 |
| qms_base_operatype | 检验业务类型 |
| qms_base_operatype_large | 检验业务大类 |
| qms_base_post_track | 岗位任务管理 |
| qms_base_print_template | 打印模板 |
| qms_base_record_config_t | 质量记录配置 |
| qms_base_reviewtype | 不合格类型 |
| qms_base_standard_file | 检验标准文件 |
| qms_base_standard_moisture_analysis | 标准水分分析表 |
| qms_base_standard_type | 检验标准类型 |
| qms_base_unit | 计量单位 |
| qms_base_usage_attribute | 用途分类对应扩展属性 |
| qms_base_usage_class | 用途分类 |
| qms_base_usage_classification | 用途分类 |
| qms_base_usage_material | 用途分类-物料 |
| qms_base_validity_period | 物料效期管理 |
| qms_base_validity_period_2025016 | 物料效期管理 |
| qms_base_validity_period_20250421 | (未注释) |
| qms_base_work_element | 工段项目信息 |
| qms_base_work_section | 工段信息 |
| qms_batc_dispose | 物料批不合格评审 |
| qms_batc_dispose_0627 | 物料批不合格评审 |
| qms_batc_dispose_2025_2_24 | 物料批不合格评审 |
| qms_batc_dispose_duty | 物料批-成品返工责任分摊 |
| qms_batc_dispose_rule | 物料批-成品返工评审配置 |
| qms_batc_expiration_record | 物料批质保期修改记录表 |
| qms_batc_material | 物料批次表 |
| qms_batc_material_20250522 | 物料批次表 |
| qms_batc_material_20250603 | 物料批次表 |
| qms_batc_material_20250902 | 物料批次表 |
| qms_batc_material_element | 物料批项目表 |
| qms_batc_status | QmsBatcStatus |
| qms_batc_workorder | QmsBatcWorkorder |
| qms_contract_t | 合同信息维护 |
| qms_data_assembler_service | QMS抽取数据 |
| qms_inventory_c | 成品检验批次对应入库量 |
| qms_plan_security_item | 安全验证计划子表 |
| qms_plan_security_t | 安全验证计划主表 |
| qms_programe_business_standard | 标准项目企业标准 |
| qms_programe_element | 检验标准项目 |
| qms_programe_element_20250421 | (未注释) |
| qms_programe_element_20250804 | (未注释) |
| qms_programe_element_num | 检验项目计数累计表 |
| qms_programe_element_period | 检验标准项目周期 |
| qms_programe_element_record | 标准项目周期记录表 |
| qms_programe_element_standard | 检验项目标准 |
| qms_programe_element_standard_20250421 | (未注释) |
| qms_programe_element_standard_20250804 | (未注释) |
| qms_programe_import_config | 工厂测方案权限配置 |
| qms_programe_inspection | 质量点检周期维护表 |
| qms_programe_inspection_element | 质量点检周期维护项目表 |
| qms_programe_material | 物料检验标准 |
| qms_programe_period | 原料库存检周期方案 |
| qms_programe_point | 固定点位方案 |
| qms_programe_point_element | 固定点位方案项目表 |
| qms_programe_price_standard | 扣价标准维护 |
| qms_programe_process | 工序周期检方案 |
| qms_programe_process_element | 集团工序方案项目表 |
| qms_programe_process_element_standrad | 集团工序方案项目标准表 |
| qms_programe_relation_parent | 方案关系主表 |
| qms_programe_relation_parent_20250421 | (未注释) |
| qms_programe_relation_parent_20250804 | (未注释) |
| qms_programe_relation_son | 方案关系子表 |
| qms_programe_relation_son_20250421 | (未注释) |
| qms_programe_relation_son_20250804 | (未注释) |
| qms_programe_review_standard | 不合格评审标准 |
| qms_programe_source_standard | 检验项目供应商标准 |
| qms_programe_version | 检验方案版本 |
| qms_programe_version_20250421 | (未注释) |
| qms_programe_version_20250804 | (未注释) |
| qms_programe_version_name | 检验方案名称维护 |
| qms_review_options | 不合格评审意见 |
| qms_review_record_element | 不合格评审-指标 |
| qms_review_res_department | 责任部门 |
| qms_review_unqualified_assort | 不合格分类 |
| qms_review_unqualified_duty | 责任分摊 |
| qms_review_unqualified_reason | 不合格原因 |
| qms_review_use_programe | 不合格使用方案 |
| qms_sampleassay_parent | 检验主表 |
| qms_sampleassay_security_plan | 安全验证计划主表 |
| qms_sampleassay_security_plan_item | 安全验证计划子表 |
| qms_sampleassay_son | 检验项目表 |
| qms_sampleassay_son_0411 | 检验项目表 |
| qms_sampleassay_son_collect | 检验项目采集记录表 |
| qms_sampleassay_son_collect_0411 | 检验项目采集记录表 |
| qms_sampleassay_son_item | 检验结果详情表 |
| qms_sampleassay_son_item_0411 | 检验结果详情表 |
| qms_sampleassay_son_standard | 检验项目对应标准表 |
| qms_sampleassay_son_standard_0411 | 检验项目对应标准表 |
| qms_sampleassay_son_standard_20250427 | 检验项目对应标准表 |
| qms_sampleassay_stay | 留样表 |
| qms_sampleassay_stay_record | 留样观察记录表 |
| qms_sampling_parent | 抽检登记 |
| qms_sampling_son | 抽样登记项目 |
| qms_standard_duty | 责任分摊标准 |
| qms_standard_rework | 成品返工损失标准 |
| qms_task_track | 任务跟踪表 |
| qms_task_track_no | 不统计标准检验时间物料 |
| qms_task_track_record | 任务跟踪记录表 |
| qms_task_track_timeout | 任务超时记录表 |

## 业务域概览

- **qms** (147张表)：来料检验/过程检验/成品检验/不合格品管理/质量追溯/质量体系

---

[[通威农发-数据库总览]]

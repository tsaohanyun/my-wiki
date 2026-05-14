---
title: MES生产执行
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, mes, 生产执行]
confidence: high
---

# MES生产执行

## 模块简介

MES（Manufacturing Execution System）生产执行模块，管理通威农发各工厂的生产全流程。涵盖配方管理（配方/配方版本/配方审批）、配料作业（配料任务/配料明细/物料消耗）、生产工单（生产计划/工单/报工）、清洗作业（CIP清洗计划/清洗记录）、打包作业（打包任务/装车/码垛）、以及生产领退料、生产日报、模具管理、电子看板等辅助功能。

## 表清单（共158张表）

| 表名 | 说明 |
|------|------|
| mes_base_batching | 配料仓基础信息 |
| mes_base_check_config | 环模修复时间设置表 |
| mes_base_classes | 班次表 |
| mes_base_classes_rest | 班次休息表 |
| mes_base_conaming | MesBaseConaming |
| mes_base_conaming_item | MesBaseConamingItem |
| mes_base_config_op | 加工费添加规则配置 |
| mes_base_crenel | mes-打包线维护 |
| mes_base_crenel_line | mes-打包线仓号关系 |
| mes_base_ebs_config | mes-ebs对应参数配置表 |
| mes_base_formula_rule | MesBaseFormulaRule |
| mes_base_material_feeder | 车间特殊物料 |
| mes_base_material_sa | 特殊半成品清单 |
| mes_base_material_sac | ABC类物料清单 |
| mes_base_material_special | 特殊物料表 |
| mes_base_performance_standard | 作业标准表 |
| mes_base_position | mes-职位 |
| mes_base_post | mes-岗位 |
| mes_base_post_operation | mes-岗位-作业标准 |
| mes_base_premix_config | 稀释预混线设置 |
| mes_base_process_molding | 工艺成型设置 |
| mes_base_product_line | MesBaseProductLine |
| mes_base_record_code | MesBaseRecordCode |
| mes_base_scale | 配料秤维护 |
| mes_base_scheduling | 生产排班 |
| mes_base_scheduling_item | 生产排班-明细表 |
| mes_base_scheduling_person | 生产排班-人员表 |
| mes_base_schneider_section_association_equipment | 施耐德工段与设备关联关系 |
| mes_base_shift | 班制表 |
| mes_base_show_point | 显示点位 |
| mes_base_standard | 标准设定 |
| mes_base_steam_convert | 燃料与吨蒸汽转换关系 |
| mes_base_task | mes-任务管理 |
| mes_base_team | mes-班组 |
| mes_base_tech | 工艺类别设置 |
| mes_base_tech_premix | 工艺类别与混合机配置 |
| mes_base_unscheduing | 生产排班-未排明细 |
| mes_base_warehouse_config | 生产类别车间 |
| mes_base_warehouse_item | 生产车间 子库配置 |
| mes_base_weighing_attr | 物料称重属性 |
| mes_base_workshop_area | 车间子库管理 |
| mes_base_workshop_silo | 车间配料仓管理 |
| mes_base_workshop_warehouse | 成品仓维护 |
| mes_base_workshop_wp | 车间微配属性设置 |
| mes_batching_store_snd | MesBatchingStoreSnd |
| mes_bom_adjust_audit_role | 工单配方调整角色审核配置表 |
| mes_bom_adjust_audit_t | 工单配方调整审核配置表 |
| mes_bom_adjust_record | 工单配方调整记录表 |
| mes_bom_adjust_record_item | 工单配方调整记录表明细 |
| mes_calibration_record | 校准记录表 |
| mes_clean_mateial | 清洗记录-清洗物料 |
| mes_clean_processdesc | 清洗记录-清洗过程描述 |
| mes_clean_record | 清洗记录-主表 |
| mes_clean_record_usage | 清洗记录-使用情况 |
| mes_config_area | 工厂合格库不合格品库 |
| mes_config_distributing | 预混料批次确认配置 |
| mes_distributing_abn | 配盘表-异常记录表 |
| mes_distributing_item | 配盘计量明细表 |
| mes_distributing_item_0411 | 配盘计量明细表 |
| mes_distributing_t | 配盘记录表 |
| mes_distributing_t_0411 | 配盘记录表 |
| mes_energy_team_use | MesEnergyTeamUse |
| mes_energy_team_use_item | MesEnergyTeamUseItem |
| mes_equipment_exception_log | IOT数采指标异常推精益 |
| mes_exe_factory_db_config | 中控工厂数据源配置表 |
| mes_exe_sync_record | 中控生产执行同步记录表 |
| mes_iot_machine_record | 设备停机记录表 |
| mes_iot_machine_t | 物实体设备关联 |
| mes_iot_property_value_record | IOT上报数据属性值记录 |
| mes_iot_subscribe_config | 对接IOT消息订阅配置 |
| mes_iot_subscribe_property | 对接IOT消息订阅属性 |
| mes_iot_tech_t | 物模型指标参数关联 |
| mes_iot_web_socket_message | 接收IOT推送的消息 |
| mes_monthly_calibrate_abn | 月度定标异常 |
| mes_picking_apply | 领料申请表 |
| mes_picking_apply1 | 领料申请表 |
| mes_picking_apply_0411 | 领料申请表 |
| mes_picking_apply_item | 领料申请子表 |
| mes_picking_record | 领料申请-移库记录表 |
| mes_picking_record1 | 领料申请-移库记录表 |
| mes_picking_record_0411 | 领料申请-移库记录表 |
| mes_produce_standard_setup | mes-生产标准设置 |
| mes_product_process | 产品工艺路线 |
| mes_product_process_basic | 产品工艺路线-基础信息 |
| mes_product_process_hour | 产品工艺路线-工时 |
| mes_product_process_mold | 产品工艺路线-模具 |
| mes_product_process_param | 产品工艺路线-工艺参数 |
| mes_product_process_routing | 产品工艺路线-路线 |
| mes_product_process_task | 产品工艺路线-生产任务 |
| mes_production_manage | 生产管理 |
| mes_production_plan | mes-特殊生产计划 |
| mes_production_plan_item | mes-特殊生产计划-明细 |
| mes_scheduling_energy_consume | 排班能耗 |
| mes_shift_note | 注意事项 |
| mes_shift_record | 班前人员检查 |
| mes_shift_submit | 班组提交 |
| mes_shift_view_records | 查看上一班组记录 |
| mes_shift_workorder | 交接班-工单详情 |
| mes_subpackage_item | 分装任务明细 |
| mes_subpackage_t | 分装任务 |
| mes_task_feeding | mes-小料投料任务 |
| mes_task_feeding_item | mes-小料投料任务明细 |
| mes_task_pool | mes-任务池 |
| mes_task_record | mes-任务已办 |
| mes_task_todo | mes-任务待办 |
| mes_tech_feeder | mes-投料口 |
| mes_tech_feeder_define | mes-投料口定义 |
| mes_tech_feeder_snd | mes-投料口外部编码 |
| mes_tech_process | 工段 |
| mes_tech_process_hour | mes-工艺路线-工时 |
| mes_tech_process_mold | mes-工艺路线-模具 |
| mes_tech_process_param | mes-工艺路线-工艺参数 |
| mes_tech_process_routing | mes-工艺路线 |
| mes_tech_process_snd | mes-工段外部编码 |
| mes_tech_process_task | mes-工艺路线-生产任务 |
| mes_tech_process_version | mes-工艺路线-版本 |
| mes_tech_standard_item | mes-生产工艺标准-对标明细 |
| mes_tech_standard_temp | mes-生产工艺标准-模板 |
| mes_tech_worksection | 工段 |
| mes_use_desc | 使用记录-使用过程描述 |
| mes_workorder_batch | mes-工单批次表 |
| mes_workorder_batching | mes-生产批组调整审批表 |
| mes_workorder_batching_record | mes-生产批组操作记录表 |
| mes_workorder_bom | mes-工单BOM表 |
| mes_workorder_bom_0411 | mes-工单BOM表 |
| mes_workorder_bom_bl | mes-工单BOM-布勒投料口 |
| mes_workorder_bom_item | mes-工单BOM表批次表 |
| mes_workorder_cancel_record | mes-工单取消审核表 |
| mes_workorder_consume | 投料表 |
| mes_workorder_correspondence | 工单外部对应 |
| mes_workorder_energy | 工单能耗表 |
| mes_workorder_energy_consume | 生产批能耗 |
| mes_workorder_feeding | 投料表 |
| mes_workorder_feeding_0411 | 投料表 |
| mes_workorder_feeding_batch | 投料表-消耗批次表 |
| mes_workorder_feeding_batch_0411 | 投料表-消耗批次表 |
| mes_workorder_mold | MesWorkorderMold |
| mes_workorder_occupy | MesWorkorderOccupy |
| mes_workorder_output | 工单完工入库记录表 |
| mes_workorder_output_0411 | 工单完工入库记录表 |
| mes_workorder_pack_rule | mes-工单包装规则 |
| mes_workorder_process_basic | mes-工单工艺路线-基础信息 |
| mes_workorder_process_energy | 生产批工段能耗 |
| mes_workorder_process_energy_son | 生产批工段能耗子表 |
| mes_workorder_process_hour | mes-工单工艺路线-工时 |
| mes_workorder_process_mold | mes-工单工艺路线-模具 |
| mes_workorder_process_param | mes-工单工艺路线-工艺参数 |
| mes_workorder_process_routing | mes-工单工艺路线 |
| mes_workorder_process_task | mes-工单工艺路线-生产任务 |
| mes_workorder_resource_consume | 生产资源消耗表 |
| mes_workorder_resource_item | 生产资源消耗子表 |
| mes_workorder_reworkhf | mes-生产工单表-回粉表 |
| mes_workorder_sa_version | 工单消耗半成品版本 |
| mes_workorder_status | mes-工单状态切换记录表 |
| mes_workorder_status_compare | 工单状态对比 |
| mes_workorder_t | mes-生产工单表 |
| mes_workorder_water | 工单水分记录表 |
| mes_workorder_workrecord | 工单作业记录 |

## 业务域概览

- **mes** (158张表)：配料作业/生产工单/报工/清洗/打包/领退料/模具/电子看板

---

[[通威农发-数据库总览]]

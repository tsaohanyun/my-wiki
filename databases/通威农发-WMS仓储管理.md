---
title: 通威农发-WMS仓储管理
created: 2026-05-07
updated: 2026-05-07
type: concept
tags: [数据库, 通威农发, wms, 仓储管理]
confidence: high
---

# 通威农发-WMS仓储管理

## 模块简介

WMS（Warehouse Management System）仓储管理模块，负责通威农发各工厂/公司的仓库全流程管理。涵盖入库管理（ASN送货单/收货单/验收）、出库管理（发运单/计划销售单/装车）、库存管理（库存原子结构/库存批次/库存移动/调整/预警）、拣货管理（拣货明细/波次）、盘点管理（盘点计划/盘点单/盘点配置）、投料退料（投料任务/生产退料/消耗退料）、不合格品管理（NG库存/不合格品处置）、以及上架策略、地标设置、调拨管理、数据归档等基础配置功能。

## 表清单（共167张表）

| 表名 | 说明 |
|------|------|
| wms_asn_order | asn送货单 |
| wms_asn_order2024 | asn送货单 |
| wms_asn_order_detail | ASN明细 |
| wms_asn_order_detail_image | ASN明细收货图片 |
| wms_asn_order_oc | 收货单柜号信息 |
| wms_asn_receive_detail_code_disk | LPN码盘 |
| wms_asn_receive_order_detail | 收货单明细 |
| wms_bulk_material_scheduling | 排程单 |
| wms_bulk_material_scheduling_stock_record | 排程单库存记录VO |
| wms_bulk_material_scheduling_submit_record | 排程单提交记录 |
| wms_data_assembler_service | WMS抽取数据 |
| wms_dispatch_order | 发运单主表信息 |
| wms_dispatch_order_detail | 发运单明细表信息 |
| wms_ext_acceptance_order | 验收单 |
| wms_ext_account | 账户 |
| wms_ext_account_alias | 账户别名（未注释） |
| wms_ext_account_alias_detail | 账户别名明细（未注释） |
| wms_ext_account_alias_detail_stock | 账户别名明细库存（未注释） |
| wms_ext_adjust_ebs_stock | wms调整ebs库存 |
| wms_ext_adjustment | 扩展调整单 |
| wms_ext_adjustment_attr | 库存批属性调整主表 |
| wms_ext_adjustment_attr_detail | 批属性调整主单 |
| wms_ext_adjustment_detail | 调整单明细 |
| wms_ext_alias_config | 别名配置（未注释） |
| wms_ext_allot_factory_config | 调拨工厂配置 |
| wms_ext_antenna | 读卡器天线 |
| wms_ext_app_config | 仓库系统app应用管理 |
| wms_ext_app_menus_config | 仓库移动端菜单配置 |
| wms_ext_app_role_menus_config | 仓库移动端角色菜单配置 |
| wms_ext_apply_order | 申请单 |
| wms_ext_apply_order_detail | 申请单明细 |
| wms_ext_archiving_allow_truncate_table | 数据归档策略步骤 |
| wms_ext_archiving_process_detail | 数据归档策略步骤 |
| wms_ext_archiving_process_detail_task | 数据归档策略步骤 |
| wms_ext_archiving_process_task | 数据归档策略步骤 |
| wms_ext_archiving_table_config | 数据归档表配置 |
| wms_ext_archiving_table_detail_record | 数据归档表记录 |
| wms_ext_archiving_table_detail_record_process | 数据归档表记录过程 |
| wms_ext_archiving_table_detail_step_record | 数据归档表步骤记录 |
| wms_ext_archiving_table_param_config | 数据归档表参数配置 |
| wms_ext_archiving_table_step_config | 数据归档策略步骤 |
| wms_ext_asn_disk_op_log | ASN码盘操作日志 |
| wms_ext_asn_dock_task | 垛口任务模型信息 |
| wms_ext_asn_loc_dx | ASN库位定向（未注释） |
| wms_ext_asn_pounds_rule | 规则单重实模型信息 |
| wms_ext_attendance_user | 仓储出勤人员情况 |
| wms_ext_card_reader | 读卡器 |
| wms_ext_child_wave | 子波次 |
| wms_ext_common_config_record | 通用配置记录（未注释） |
| wms_ext_dim_record_log | 称重记录日志（未注释） |
| wms_ext_dim_record_log_before_one_month | 称重记录日志（一个月前） |
| wms_ext_duplicate_item | 物料重名信息 |
| wms_ext_ebs_push_retry_api | EBS推送重试API（未注释） |
| wms_ext_ebs_stock_atom | EBS库存原子（未注释） |
| wms_ext_ebs_stock_atom_zzk | EBS库存原子（中控） |
| wms_ext_ebs_vehicle | EBS车辆信息列表 |
| wms_ext_emergency | 紧急释放 |
| wms_ext_emergency_detail | 紧急释放明细 |
| wms_ext_erp_lot_update_record | ERP批次更新记录 |
| wms_ext_factory_allot_order | 调拨主单 |
| wms_ext_factory_allot_order_detail | 调拨主单明细 |
| wms_ext_factory_allot_stock_detail | 调拨库存明细 |
| wms_ext_feed_return_order | 生产退料单 |
| wms_ext_feed_return_order_detail | 生产退料单明细 |
| wms_ext_feed_task | 投料任务 |
| wms_ext_feed_task_detail | 投料任务分配库存明细 |
| wms_ext_filter_sync_ou_code | 叉车设置 |
| wms_ext_hold_order | 挂起单据（未注释） |
| wms_ext_hold_order_detail | 挂起单据明细（未注释） |
| wms_ext_inbound_data_import_temp | 入库异常登记中间表 |
| wms_ext_interface_control | 接口回传管控 |
| wms_ext_interface_control_record | 接口回传管控记录 |
| wms_ext_inventory | 盘点单 |
| wms_ext_inventory_bulk_materials_detail | 散料盘点抄账记录 |
| wms_ext_inventory_detail | 盘点单明细 |
| wms_ext_inventory_detail_stock_record | 盘点的快照库存 |
| wms_ext_inventory_param_config | 盘点配置 |
| wms_ext_inventory_plan | 盘点计划 |
| wms_ext_inventory_plan_area | 盘点计划区域 |
| wms_ext_inventory_plan_loc | 盘点计划库位 |
| wms_ext_inventory_plan_sku | 盘点计划物料 |
| wms_ext_inventory_plan_sub_library | 盘点计划子库 |
| wms_ext_inventory_workshop_detail | 车间盘点明细 |
| wms_ext_landmark | 地标设置 |
| wms_ext_lock_id | 锁定ID |
| wms_ext_loss_record | 损耗记录 |
| wms_ext_material_process | 来料加工维护 |
| wms_ext_material_process_detail | 来料加工明细维护 |
| wms_ext_move_order | 库存移动单据 |
| wms_ext_move_order_detail | 库存移动单据明细 |
| wms_ext_ncounter | 计数器（未注释） |
| wms_ext_ng_import_temp | 不合格入库处置记录单据中间表 |
| wms_ext_ng_order_disposal_record | 不合格品处置记录 |
| wms_ext_ng_order_stock_op_log | NG单据库存操作日志 |
| wms_ext_ng_order_xh_disposal_middle | 不合格入库处置记录单据中间表 |
| wms_ext_ng_stock_order | NG库存单据 |
| wms_ext_ng_stock_order_detail | NG单据库存明细 |
| wms_ext_ng_stock_order_fix1125 | 修复表 |
| wms_ext_ng_stock_problem_record | NG库存问题预警记录 |
| wms_ext_ng_sub_library | NG子库（未注释） |
| wms_ext_part_md | 物料扩展表 |
| wms_ext_plan_order | 计划销售单 |
| wms_ext_plan_order_detail | 计划销售单明细 |
| wms_ext_plan_order_detail_label | 计划销售单明细标签号 |
| wms_ext_plan_order_detail_pounds | 计划销售单磅单记录 |
| wms_ext_plate_number_led | led屏展示 |
| wms_ext_purchase_returns_plan | 采购退货计划单 |
| wms_ext_qms_pound_record | QMS磅单记录（未注释） |
| wms_ext_rec_team_record | 收货班组记录 |
| wms_ext_refer_all_invalid_date | 波次维护（无效日期参照） |
| wms_ext_region | 区域表 |
| wms_ext_req_custom_param | 请求自定义参数（未注释） |
| wms_ext_req_last_time | EBS接口请求配置 |
| wms_ext_return_order_apply | 消耗退料申请 |
| wms_ext_sale_vehicle | 销售车辆（未注释） |
| wms_ext_sale_vehicle_order_detail | 销售车辆订单明细（未注释） |
| wms_ext_scene_setting | 场景设置 |
| wms_ext_scrap_record | 报废记录 |
| wms_ext_shelf_strategy | 上架策略主表 |
| wms_ext_shelf_strategy_step | 上架策略步骤 |
| wms_ext_shelf_strategy_step_rule | 上架策略步骤规则 |
| wms_ext_split_table | 分表配置（未注释） |
| wms_ext_stack_log | 堆垛日志（未注释） |
| wms_ext_stock_equals | 库存对账（未注释） |
| wms_ext_stock_equals_zzk | 库存对账（中控） |
| wms_ext_system_config_model | 参数配置 |
| wms_ext_task_controls | 任务控制 |
| wms_ext_transaction | 交易事务 |
| wms_ext_translate | 仓库翻译表 |
| wms_ext_unit_convert | 单位转换（未注释） |
| wms_ext_update_stock_state_apply | 变更申请 |
| wms_ext_update_stock_state_apply_detail | 变更申请明细 |
| wms_ext_w2t_api_interface_data | W2T接口数据（未注释） |
| wms_ext_waring_scan_fail_log | 扫描失败预警日志 |
| wms_ext_wave | 波次维护 |
| wms_ext_wave_deliver | 装车顺序模型信息 |
| wms_ext_work_shop_ng_item_transaction | 不合格品管理流水报表 |
| wms_ext_work_shop_report_work_record | 车间报工记录（未注释） |
| wms_ext_xhth_config | 协同互通配置（未注释） |
| wms_ext_xxjob_task_record | xxjob调用记录 |
| wms_iface_log | 接口日志 |
| wms_iface_log2024 | 接口日志 |
| wms_iface_log2025 | 接口日志 |
| wms_iface_log_temp | 接口日志（临时） |
| wms_lot_delay | 批次延期记录 |
| wms_materialbatch_workorder_all | WMS成品产出物料批与工单关联关系表全量 |
| wms_materialbatch_workorder_fg | WMS成品产出物料批与工单关联关系表 |
| wms_order_attendance_info | 订单装卸效率表 |
| wms_period | 期间（未注释） |
| wms_period_detail | 期间明细（未注释） |
| wms_period_out | 期间出库（未注释） |
| wms_pick_detail | 拣货明细 |
| wms_pick_detail2025 | 拣货明细 |
| wms_purchase_order | 采购订单 |
| wms_purchase_order_detail | 采购订单明细 |
| wms_sales_count | 销售统计 |
| wms_stock_atom | 库存原子结构 |
| wms_stock_atom2024 | 库存原子结构 |
| wms_stock_atom2025 | 库存原子结构 |
| wms_stock_attr | 库存批次 |
| wms_stock_attr2024 | 库存批次 |
| wms_stock_attr2025 | 库存批次 |
| wms_stock_config | 库存配置 |
| wms_stock_warn | 库存预警信息 |
| wms_stock_warn_temp | 子库转移申请明细 |
| wms_sub_library_transfer_request | 子库转移申请 |
| wms_user_sub_library | 用户子库关联 |

## 业务域概览

- **入库管理**：ASN送货单 → 收货单 → 码盘 → 验收 → 上架
- **出库管理**：发运单/计划销售单 → 波次作业 → 拣货 → 装车 → 磅单
- **库存管理**：库存原子结构、库存批次、库存移动、库存调整、库存预警、库存对账
- **盘点管理**：盘点计划 → 盘点单 → 盘点明细 → 盘盈盘亏
- **波次与拣货**：波次维护、子波次、拣货明细、装车顺序
- **投料与退料**：投料任务分配、生产退料、消耗退料申请
- **不合格品管理**：NG库存单据、不合格品处置、不合格品流水报表
- **调拨管理**：调拨主单、调拨明细、调拨工厂配置
- **基础配置**：上架策略、地标设置、区域表、物料扩展、场景设置、参数配置
- **接口与集成**：EBS接口、接口日志、接口回传管控、WMS数据抽取
- **数据归档**：数据归档表配置、策略步骤、归档记录
- **移动端**：仓储APP菜单配置、角色菜单、PDA扫码

---

[[通威农发-数据库总览]]

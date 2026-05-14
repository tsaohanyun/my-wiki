---
title: LM精益管理
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, lm, 精益管理]
confidence: high
---

# LM精益管理

## 模块简介

LM（Lean Management）精益管理模块，涵盖8D问题解决、标准化作业、安环管理、变动生产费用、指标标准等精益管理核心流程。

## 表清单（共154张表）

| 表名 | 说明 |
|------|------|
| lm_8d_d1_item | D1成立多功能小组子表 |
| lm_8d_d2_measure | D2紧急措施 |
| lm_8d_d2_measure_wd | D2围堵策略 |
| lm_8d_d2_problem | D2问题描述及紧急措施 |
| lm_8d_d3_measure_tem | D3临时措施 |
| lm_8d_d4_root_cause | D4根本原因 |
| lm_8d_d5_countermeasure | D5对策制定 |
| lm_8d_d6_verifier | D6措施有效性验证 |
| lm_8d_d7_standard | D7措施(永久对策)标准化 |
| lm_8d_d8_summary | D8经验教训总结 |
| lm_8d_problem_level | 问题等级定义 |
| lm_8d_problem_source | 问题反馈来源 |
| lm_8d_problem_type | 问题类型 |
| lm_8d_report | 8D表单 |
| lm_8d_report_stage | 8D阶段节点配置 |
| lm_area_supervisor | 标准化基础数据-点检区域管理(分公司)-责任岗位 |
| lm_area_supervisor_export_vm | 区域责任人 |
| lm_attachment | 附件业务表 |
| lm_audit_type | 分层审核基础数据-审核类型 |
| lm_branch_inspection_areas | 标准化基础数据-(分公司)点检区域 |
| lm_checkup_agency | 体检机构 |
| lm_checkup_element | 体检项目 |
| lm_checkup_health_records | 体检记录表 |
| lm_checkup_plan | 健康体检计划表 |
| lm_checkup_plan_detail | 健康体检计划明细表VO |
| lm_checkup_plan_item | 健康体检计划子表-体检标准 |
| lm_checkup_standard | 健康体检标准 |
| lm_checkup_task | 定期体检任务表 |
| lm_checkup_type | 体检类型 |
| lm_clean_area_supervisor | 清洁管理-责任岗位 |
| lm_clean_audit_type | 清洁检查基础数据-审核类型 |
| lm_clean_check_standard | 清洁管理-点检标准 |
| lm_clean_check_standard_sub | 清洁管理-点检标准-子公司停用启用 |
| lm_clean_equipment | 清洁管理-点检设备 |
| lm_clean_equipment_manage | 清洁管理-点检设备维护 |
| lm_clean_plan | 清洁检查-稽查计划 |
| lm_clean_plan_detail | 清洁检查-稽查计划(稽查明细) |
| lm_clean_plan_dispatch_detail | 清洁检查-稽查计划(下发明细) |
| lm_clean_point | 清洁管理-清洁点 |
| lm_clean_responsibility_team | 清洁检查基础数据-(总部)责任班组 |
| lm_clean_role_manage | 清洁检查基础数据-分层审核角色 |
| lm_clean_task | 清洁检查-任务 |
| lm_clean_task_detail | 清洁检查-任务详情 |
| lm_clean_task_trigger_record | 清洁检查-任务触发记录 |
| lm_correction_manager | 标准化任务管理-整改项目管理 |
| lm_energy_electrovalency | 分时电价主表 |
| lm_energy_electrovalency_item | 分时电价子表 |
| lm_energy_team_use | LmEnergyTeamUse |
| lm_energy_team_use_item | LmEnergyTeamUseItem |
| lm_env_standard | 环保标准 |
| lm_env_standard_plan | 计划模型 |
| lm_env_standard_plan_detail | 环境标准下发明细 |
| lm_env_standard_task | 环境任务模型 |
| lm_env_standard_task_detail | 环保标准任务明细 |
| lm_equipment_exception_log | 设备异常管理 |
| lm_exception_archive | 异常档案 |
| lm_factor_manage | 因素分类管理 |
| lm_host_energy_consume_daily_report | 主机能耗日统计表 |
| lm_host_energy_consume_daily_son | 主机能耗日统计子表 |
| lm_id_delete | id删除中间表 |
| lm_ind_alarm_grade | 异常级别 |
| lm_ind_alarm_log_table | 报警日志 |
| lm_ind_alarm_point | 报警点 |
| lm_ind_alarm_point_record | 报警记录 |
| lm_ind_alarm_point_threshold | 报警点阈值配置 |
| lm_ind_alarm_rule | 预警规则表 |
| lm_indicator_record | 指标档案表 |
| lm_indicator_record_table_property | 指标档案表-数据表字段 |
| lm_indicator_report | 指标报表关系表 |
| lm_indicator_reporting | 指标提报 |
| lm_indicator_result | 指标计算结果表 |
| lm_indicator_standard | 指标执行标准档案表 |
| lm_indicator_standard_detail | 指标执行标准档案指标明细表 |
| lm_indicator_standard_detail_range | 标准档案指标作用范围明细表 |
| lm_indicator_standard_detail_value | 指标执行标准档案指标数值明细表 |
| lm_indicator_table_model | 数据表名 |
| lm_indicator_table_property | 数据表字段 |
| lm_inspection_area | 标准化基础数据-(总部)点检区域 |
| lm_inspection_location | 标准化-楼层位置 |
| lm_inspection_plan | 标准化管理-稽查计划 |
| lm_inspection_plan_detail | 标准化管理-稽查计划(稽查明细) |
| lm_inspection_projects | 标准化基础数据-点检项目 |
| lm_inspection_standard | 标准化基础数据-点检标准 |
| lm_inspection_standard_detail | 标准化基础数据-点检标准详情 |
| lm_inspection_task | 标准化-标准化任务 |
| lm_inspection_task_detail | 标准化-标准化任务详情 |
| lm_inventory_inspect_report | 库存养护检验报告 |
| lm_inventory_quality_monitor_record | 库存原料质量监控记录 |
| lm_judge_regulation | 标准化基础数据-判定规则 |
| lm_odha_hazard | 危害因素配置 |
| lm_odha_inspection_plan | 检査计划 |
| lm_odha_inspection_plan_item | 检査计划子表 |
| lm_odha_inspection_plan_item_factory | 职业危害分布-公司 |
| lm_odha_inspection_task | 检测任务主表 |
| lm_odha_inspection_task_item | 检测任务子表 |
| lm_peak_valley_power_consume | 峰平谷电耗统计表 |
| lm_plan_dispatch_detail | 标准化管理-稽查计划(下发明细) |
| lm_points_detail | 积分明细 |
| lm_points_detail_count | 积分明细统计 |
| lm_points_employee | 员工积分管理 |
| lm_points_employee_reward | 优秀行为点赞记录子表 |
| lm_points_level | 等级设置 |
| lm_points_like_category | 点赞类别 |
| lm_points_type | 积分类型 |
| lm_problem_record | 质量整改-问题登记 |
| lm_prod_performance_rectification | 生产分析绩效整改措施 |
| lm_product_sample_observe_record | 产品留样观察记录 |
| lm_qc_check_standard | 标准化基础数据-点检标准(V2版) |
| lm_qc_check_standard_sub | 标准化基础数据-点检标准-子公司停用启用 |
| lm_qc_score | 标准化基础数据-点检标准-分值(V2版) |
| lm_qrcode_maintenance | 标准化基础数据-(分公司)点检区域二维码维护 |
| lm_rectification_action | 标准化-标准化任务-整改措施 |
| lm_rectification_action_sa | 安环事故-整改 |
| lm_report_config | 报表配置 |
| lm_responsibility_team | 准化基础数据-(总部)责任班组 |
| lm_role_manage | 分层审核基础数据-分层审核角色 |
| lm_safety_violation | 安全违规 |
| lm_security_knowledge | 安环事故-经验教训库 |
| lm_security_knowledge_vo | 安环事故-经验教训库-VO |
| lm_security_performance | 安环事故-绩效考核 |
| lm_security_register | 安环事故登记 |
| lm_security_register_annex | 安环事故登记附件 |
| lm_security_register_detail | 安环事故(下发明细) |
| lm_security_register_people | 安环事故登记-人员表 |
| lm_security_verify_complete_rate | 安全验证完成率 |
| lm_security_verify_details | 安全验证明细 |
| lm_ssue_standard | 标准下发关系表 |
| lm_stp_protein_moisture | 蛋白水分 |
| lm_suggest_enforce | 合理化建议-实施 |
| lm_suggest_enforce_confirm | 合理化建议-实施确认 |
| lm_suggest_examine | 合理化建议-审批 |
| lm_suggest_input | 合理化建议模版导入 |
| lm_suggest_level | 合理化建议级别 |
| lm_suggest_promotion | 合理化建议推广 |
| lm_suggest_propose | 合理化建议提议 |
| lm_suggest_re_evaluation | 合理化建议-生产经理复批 |
| lm_suggest_re_evaluation_area | 合理化建议-片区总监复评 |
| lm_suggest_re_evaluation_company | 合理化建议-总经理复评 |
| lm_suggest_re_evaluation_head | 合理化建议-总部审批 |
| lm_suggest_type | 合理化建议类型 |
| lm_supplies_item | 劳保防护用品基础数据 |
| lm_supplies_plan | 劳保防护用品发放计划 |
| lm_supplies_plan_item | 发放计划-人员明细 |
| lm_supplies_standard_detail | 劳保用品管理标准(下发明细) |
| lm_supplies_standards | 劳保防护用品管理标准 |
| lm_system_file_directory | 体系文件目录 |
| lm_task_trigger_record | 标准化-任务触发记录 |
| lm_test_table_1 | 指标测试用表1 |
| lm_test_table_2 | 指标测试用表2 |
| lm_test_table_3 | 指标测试用表3 |
| lm_workflow_role | 审批流权限主表 |
| lm_workflow_role_item | 审批流权限子表 |
| lm_workshop_branch_daily_energy | 车间支路能耗统计表 |
| lm_workshop_daily_energy_consume | 车间日能耗记录表 |

## 业务域概览

- **lm** (154张表)：8D问题解决/标准化作业/安环管理/精益指标/变动费用

---

[[通威农发-数据库总览]]

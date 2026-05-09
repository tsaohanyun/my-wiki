---
title: "通威农发-LM精益管理"
---
     1|---
     2|title: 通威农发-LM精益管理
     3|created: 2026-05-07
     4|updated: 2026-05-07
     5|type: concept
     6|tags: [数据库, 通威农发, lm, 物流管理]
     7|confidence: high
     8|---
     9|
    10|# 通威农发-LM精益管理
    11|
    12|## 模块简介
    13|
    14|LM精益管理模块（前缀 `lm`）是通威农发智能制造体系的核心管理模块之一，涵盖**8D问题解决、质量整改、标准化管理、安环事故管理、清洁检查、合理化建议、健康体检、能源管理、库存养护、积分管理、指标管理、报警预警、职业危害检测、劳保用品管理、体系文件管理**等业务领域。共包含 **154** 张数据表。
    15|
    16|模块整体支撑了从问题发现（8D、报警、异常登记）到分析改进（根本原因、对策制定）、再到标准化落地（点检标准、稽查计划、整改跟踪）的闭环管理流程，同时涵盖员工健康、安全环保、能源监控、积分激励等配套管理功能。
    17|
    18|### 主要业务子域
    19|
    20|| 子域 | 说明 |
    21||------|------|
    22|| 8D问题解决 | D1~D8完整8D流程：成立小组、紧急措施、问题描述、临时措施、根本原因、对策制定、验证、标准化、总结 |
    23|| 质量整改 | 问题登记、整改措施、异常档案、经验教训库 |
    24|| 标准化管理 | 点检区域、点检标准、点检项目、稽查计划、标准化任务、判定规则 |
    25|| 安环管理 | 安全违规、事故登记、事故整改、绩效考核、经验教训库、安全验证 |
    26|| 清洁检查 | 清洁点、清洁设备、清洁标准、清洁计划、清洁任务 |
    27|| 合理化建议 | 提议、审批、实施、确认、推广、复评 |
    28|| 指标管理 | 指标档案、执行标准、计算结果、报表关系 |
    29|| 报警预警 | 报警点、报警日志、报警记录、阈值配置、预警规则 |
    30|| 能源管理 | 分时电价、峰平谷电耗、主机能耗日统计、车间日能耗 |
    31|| 健康体检 | 体检机构、体检项目、体检标准、体检计划、体检任务 |
    32|| 积分管理 | 员工积分、积分类型、等级设置、点赞类别、积分明细 |
    33|| 库存养护 | 库存养护检验报告、库存原料质量监控记录、产品留样观察记录 |
    34|| 职业危害 | 危害因素配置、检查计划、检测任务 |
    35|| 劳保用品 | 劳保用品管理标准、发放计划、人员明细 |
    36|
    37|## 表清单
    38|
    39|| 表名 | COMMENT注释 |
    40||------|------------|
    41|| lm_8d_d1_item | D1成立多功能小组子表 |
    42|| lm_8d_d2_measure | D2紧急措施 |
    43|| lm_8d_d2_measure_wd | D2围堵策略 |
    44|| lm_8d_d2_problem | D2问题描述及紧急措施 |
    45|| lm_8d_d3_measure_tem | D3临时措施 |
    46|| lm_8d_d4_root_cause | D4根本原因 |
    47|| lm_8d_d5_countermeasure | D5对策制定 |
    48|| lm_8d_d6_verifier | D6措施有效性验证 |
    49|| lm_8d_d7_standard | D7措施(永久对策)标准化 |
    50|| lm_8d_d8_summary | D8经验教训总结 |
    51|| lm_8d_problem_level | 问题等级定义 |
    52|| lm_8d_problem_source | 问题反馈来源 |
    53|| lm_8d_problem_type | 问题类型 |
    54|| lm_8d_report | 8D表单 |
    55|| lm_8d_report_stage | 8D阶段节点配置 |
    56|| lm_area_supervisor | 标准化基础数据-点检区域管理(分公司)-责任岗位 |
    57|| lm_area_supervisor_export_vm | 区域责任人 |
    58|| lm_attachment | 附件业务表 |
    59|| lm_audit_type | 分层审核基础数据-审核类型 |
    60|| lm_branch_inspection_areas | 标准化基础数据-(分公司)点检区域 |
    61|| lm_checkup_agency | 体检机构 |
    62|| lm_checkup_element | 体检项目 |
    63|| lm_checkup_health_records | 体检记录表 |
    64|| lm_checkup_plan | 健康体检计划表 |
    65|| lm_checkup_plan_detail | 健康体检计划明细表VO |
    66|| lm_checkup_plan_item | 健康体检计划子表-体检标准 |
    67|| lm_checkup_standard | 健康体检标准 |
    68|| lm_checkup_task | 定期体检任务表 |
    69|| lm_checkup_type | 体检类型 |
    70|| lm_clean_area_supervisor | 清洁管理-责任岗位 |
    71|| lm_clean_audit_type | 清洁检查基础数据-审核类型 |
    72|| lm_clean_check_standard | 清洁管理-点检标准 |
    73|| lm_clean_check_standard_sub | 清洁管理-点检标准-子公司停用启用 |
    74|| lm_clean_equipment | 清洁管理-点检设备 |
    75|| lm_clean_equipment_manage | 清洁管理-点检设备维护 |
    76|| lm_clean_plan | 清洁检查-稽查计划 |
    77|| lm_clean_plan_detail | 清洁检查-稽查计划(稽查明细) |
    78|| lm_clean_plan_dispatch_detail | 清洁检查-稽查计划(下发明细) |
    79|| lm_clean_point | 清洁管理-清洁点 |
    80|| lm_clean_responsibility_team | 清洁检查基础数据-(总部)责任班组 |
    81|| lm_clean_role_manage | 清洁检查基础数据-分层审核角色 |
    82|| lm_clean_task | 清洁检查-任务 |
    83|| lm_clean_task_detail | 清洁检查-任务详情 |
    84|| lm_clean_task_trigger_record | 清洁检查-任务触发记录 |
    85|| lm_correction_manager | 标准化任务管理-整改项目管理 |
    86|| lm_energy_electrovalency | 分时电价主表 |
    87|| lm_energy_electrovalency_item | 分时电价子表 |
    88|| lm_energy_team_use | LmEnergyTeamUse |
    89|| lm_energy_team_use_item | LmEnergyTeamUseItem |
    90|| lm_env_standard | 环保标准 |
    91|| lm_env_standard_plan | 计划模型 |
    92|| lm_env_standard_plan_detail | 环境标准下发明细 |
    93|| lm_env_standard_task | 环境任务模型 |
    94|| lm_env_standard_task_detail | 环保标准任务明细 |
    95|| lm_equipment_exception_log | 设备异常管理 |
    96|| lm_exception_archive | 异常档案 |
    97|| lm_factor_manage | 因素分类管理 |
    98|| lm_host_energy_consume_daily_report | 主机能耗日统计表 |
    99|| lm_host_energy_consume_daily_son | 主机能耗日统计子表 |
   100|| lm_id_delete | id删除中间表 |
   101|| lm_ind_alarm_grade | 异常级别 |
   102|| lm_ind_alarm_log_table | 报警日志 |
   103|| lm_ind_alarm_point | 报警点 |
   104|| lm_ind_alarm_point_record | 报警记录 |
   105|| lm_ind_alarm_point_threshold | 报警点阈值配置 |
   106|| lm_ind_alarm_rule | 预警规则表 |
   107|| lm_indicator_record | 指标档案表 |
   108|| lm_indicator_record_table_property | 指标档案表-数据表字段 |
   109|| lm_indicator_report | 指标报表关系表 |
   110|| lm_indicator_reporting | 指标提报 |
   111|| lm_indicator_result | 指标计算结果表 |
   112|| lm_indicator_standard | 指标执行标准档案表 |
   113|| lm_indicator_standard_detail | 指标执行标准档案指标明细表 |
   114|| lm_indicator_standard_detail_range | 标准档案指标作用范围明细表 |
   115|| lm_indicator_standard_detail_value | 指标执行标准档案指标数值明细表 |
   116|| lm_indicator_table_model | 数据表名 |
   117|| lm_indicator_table_property | 数据表字段 |
   118|| lm_inspection_area | 标准化基础数据-(总部)点检区域 |
   119|| lm_inspection_location | 标准化-楼层位置 |
   120|| lm_inspection_plan | 标准化管理-稽查计划 |
   121|| lm_inspection_plan_detail | 标准化管理-稽查计划(稽查明细) |
   122|| lm_inspection_projects | 标准化基础数据-点检项目 |
   123|| lm_inspection_standard | 标准化基础数据-点检标准 |
   124|| lm_inspection_standard_detail | 标准化基础数据-点检标准详情 |
   125|| lm_inspection_task | 标准化-标准化任务 |
   126|| lm_inspection_task_detail | 标准化-标准化任务详情 |
   127|| lm_inventory_inspect_report | 库存养护检验报告 |
   128|| lm_inventory_quality_monitor_record | 库存原料质量监控记录 |
   129|| lm_judge_regulation | 标准化基础数据-判定规则 |
   130|| lm_odha_hazard | 危害因素配置 |
   131|| lm_odha_inspection_plan | 检査计划 |
   132|| lm_odha_inspection_plan_item | 检査计划子表 |
   133|| lm_odha_inspection_plan_item_factory | 职业危害分布-公司 |
   134|| lm_odha_inspection_task | 检测任务主表 |
   135|| lm_odha_inspection_task_item | 检测任务子表 |
   136|| lm_peak_valley_power_consume | 峰平谷电耗统计表 |
   137|| lm_plan_dispatch_detail | 标准化管理-稽查计划(下发明细) |
   138|| lm_points_detail | 积分明细 |
   139|| lm_points_detail_count | 积分明细统计 |
   140|| lm_points_employee | 员工积分管理 |
   141|| lm_points_employee_reward | 优秀行为点赞记录子表 |
   142|| lm_points_level | 等级设置 |
   143|| lm_points_like_category | 点赞类别 |
   144|| lm_points_type | 积分类型 |
   145|| lm_problem_record | 质量整改-问题登记 |
   146|| lm_problem_record_bak1231 | 质量整改-问题登记 |
   147|| lm_product_sample_observe_record | 产品留样观察记录 |
   148|| lm_qc_check_standard | 标准化基础数据-点检标准(V2版) |
   149|| lm_qc_check_standard_sub | 标准化基础数据-点检标准-子公司停用启用 |
   150|| lm_qc_score | 标准化基础数据-点检标准-分值(V2版) |
   151|| lm_qrcode_maintenance | 标准化基础数据-(分公司)点检区域二维码维护 |
   152|| lm_rectification_action | 标准化-标准化任务-整改措施 |
   153|| lm_rectification_action_bak1231 | 标准化-标准化任务-整改措施 |
   154|| lm_rectification_action_sa | 安环事故-整改 |
   155|| lm_report_config | 报表配置 |
   156|| lm_responsibility_team | 准化基础数据-(总部)责任班组 |
   157|| lm_role_manage | 分层审核基础数据-分层审核角色 |
   158|| lm_safety_violation | 安全违规 |
   159|| lm_security_knowledge | 安环事故-经验教训库 |
   160|| lm_security_knowledge_vo | 安环事故-经验教训库-VO |
   161|| lm_security_performance | 安环事故-绩效考核 |
   162|| lm_security_register | 安环事故登记 |
   163|| lm_security_register_annex | 安环事故登记附件 |
   164|| lm_security_register_detail | 安环事故(下发明细) |
   165|| lm_security_register_people | 安环事故登记-人员表 |
   166|| lm_security_verify_complete_rate | 安全验证完成率 |
   167|| lm_security_verify_details | 安全验证明细 |
   168|| lm_ssue_standard | 标准下发关系表 |
   211|| lm_suggest_enforce | 合理化建议-实施 |
   212|| lm_suggest_enforce_confirm | 合理化建议-实施确认 |
   213|| lm_suggest_examine | 合理化建议-审批 |
   214|| lm_suggest_input | 合理化建议模版导入 |
   215|| lm_suggest_level | 合理化建议级别 |
   216|| lm_suggest_promotion | 合理化建议推广 |
   217|| lm_suggest_propose | 合理化建议提议 |
   218|| lm_suggest_re_evaluation | 合理化建议-生产经理复批 |
   219|| lm_suggest_re_evaluation_area | 合理化建议-片区总监复评 |
   220|| lm_suggest_re_evaluation_company | 合理化建议-总经理复评 |
   221|| lm_suggest_re_evaluation_head | 合理化建议-总部审批 |
   222|| lm_suggest_type | 合理化建议类型 |
   223|| lm_supplies_item | 劳保防护用品基础数据 |
   224|| lm_supplies_plan | 劳保防护用品发放计划 |
   225|| lm_supplies_plan_item | 发放计划-人员明细 |
   226|| lm_supplies_standard_detail | 劳保用品管理标准(下发明细) |
   227|| lm_supplies_standards | 劳保防护用品管理标准 |
   228|| lm_system_file_directory | 体系文件目录 |
   229|| lm_task_trigger_record | 标准化-任务触发记录 |
   230|| lm_test_table_1 | 指标测试用表1 |
   231|| lm_test_table_2 | 指标测试用表2 |
   232|| lm_test_table_3 | 指标测试用表3 |
   233|| lm_workflow_role | 审批流权限主表 |
   234|| lm_workflow_role_item | 审批流权限子表 |
   235|| lm_workshop_branch_daily_energy | 车间支路能耗统计表 |
   236|| lm_workshop_daily_energy_consume | 车间日能耗记录表 |
   237|
   238|## 关联模块
   239|
   240|- [[通威农发-数据库总览]] — 通威农发数据库整体概览
   241|
   242|## 备注
   243|
   244|- 模块前缀：`lm`
   245|- 数据表总数：196
   246|- 物流管理(LM)模块不仅涵盖传统物流跟踪与仓储管理，还整合了质量管理（8D、指标）、安全管理（安环、职业危害）、标准化执行、能源监控、员工健康与激励等众多管理子域，是通威农发智能制造体系中覆盖面最广的综合管理模块之一。
   247|
---
title: IIoT工业物联网
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, iiot, 工业物联网]
confidence: high
---

# IIoT工业物联网

## 模块简介

IIoT（Industrial Internet of Things）工业物联网模块，负责通威农发各工厂的设备数据采集、实时监控和智能分析。涵盖设备连接管理、数据采集（PLC/DCS/传感器）、实时数据存储、报警管理、数据可视化、边缘计算、协议转换等功能。

## 表清单（共84张表）

| 表名 | 说明 |
|------|------|
| iiot_agg_0558xlgnhfl5u_boolean | (未注释) |
| iiot_agg_10_integer | (未注释) |
| iiot_aggregation_rule | 聚合规则 |
| iiot_alarm_rules | 报警规则 |
| iiot_base_group | 分组 |
| iiot_category | 分类 |
| iiot_cold_expire_archive_instance | 冷数据过期归档实例 |
| iiot_cold_expire_archive_record | 冷数据过期归档记录 |
| iiot_cold_tag_value_expire_archive_record | 历史工况冷数据过期归档记录 |
| iiot_config_address_info | 地址位 |
| iiot_config_address_info_package | 地址位 |
| iiot_config_base_iotags | 集中式配置测点模型 |
| iiot_config_device_type | 设备类型 |
| iiot_config_iolink_device | 集中式配置的设备配置 |
| iiot_config_iot_service_property | iotService属性 |
| iiot_config_log | 工程配置操作日志 |
| iiot_config_smdc_cache | 工程配置-smdc的缓存配置 |
| iiot_config_tag_variable | 变量词典 |
| iiot_dataflow | 连接流管理 |
| iiot_dataflow_draft | 连接流管理草稿 |
| iiot_dataservice_type | 数据服务协议配置信息 |
| iiot_db_config | 数据库管理配置 |
| iiot_edge_drive | 驱动管理 |
| iiot_edge_drive_job | 驱动任务模型 |
| iiot_edge_drive_job_detail | 驱动任务详情模型 |
| iiot_edge_drive_job_history | 驱动任务升级历史详情 |
| iiot_edge_firmware | 固件升级模型 |
| iiot_edge_firmware_job | 固件升级任务明细 |
| iiot_edge_firmware_job_detail | 固件升级实体明细 |
| iiot_edge_node_manage | 边缘节点管理 |
| iiot_edgesync | 工程协同聚合根模型 |
| iiot_edgesync_binding_rule | 绑定规则 |
| iiot_edgesync_engintag | 工程Tag |
| iiot_edgesync_engintag_detail | 工程Tag |
| iiot_edgesync_iotag | IoTag |
| iiot_edgesync_iotag_detail | IoTag详情 |
| iiot_edgesync_log | 工程协同操作日志 |
| iiot_edgesync_script | 工程脚本 |
| iiot_entity_order | 物实体指令 |
| iiot_factory_entity_deploy | 工厂实体部署物实体信息 |
| iiot_forward_api | Api转发协议 |
| iiot_forward_mqtt | Mqtt转发协议 |
| iiot_forward_opcua | OPCUA转发协议 |
| iiot_forward_rabbitmq | RabbitMQ转发协议 |
| iiot_forwardconfig_api | API转发配置 |
| iiot_forwardconfig_mqtt | Mqtt转发配置 |
| iiot_forwardconfig_opcua | OPCUA转发配置 |
| iiot_forwardconfig_rabbitmq | RabbitMQ转发配置 |
| iiot_import_error | Excel导入异常模型 |
| iiot_kwh | (未注释) |
| iiot_kwh_20251124 | (未注释) |
| iiot_message_sendpolicy_alarm | 报警发送策略模型 |
| iiot_message_sendpolicy_ruleengine | 规则引擎发送策略模型 |
| iiot_message_sendpolicy_storemanagement | 存储告警规则发送策略模型 |
| iiot_messagepush_email_channel | 邮件消息渠道模型 |
| iiot_messagepush_email_template | 邮件消息模板模型 |
| iiot_messagepush_enterprisewechat_channel | 企业微信消息渠道模型 |
| iiot_messagepush_enterprisewechat_template | 企业微信消息模板模型 |
| iiot_messagepush_receive_group | 消息接收组模型 |
| iiot_messagepush_receive_group_detail | 消息接收组详情 |
| iiot_messagepush_record | 请求记录模型 |
| iiot_messagepush_webhook_channel | 机器人消息渠道模型 |
| iiot_messagepush_webhook_template | 机器人消息模板模型 |
| iiot_multiisomerism | 多源异构 |
| iiot_online_time | (未注释) |
| iiot_program_user_program | 用户编程 |
| iiot_project | 项目管理 |
| iiot_ruleengine | 规则引擎 |
| iiot_ruleengine_adjacent | 规则引擎-相邻和、差、积、变化率等存储 |
| iiot_smdc_rddc | SMDC冗余配置 |
| iiot_steamkg | (未注释) |
| iiot_steamkg_20251124 | (未注释) |
| iiot_store_alarm_history | 归档存储配置 |
| iiot_system_configuration | IIOT系统配置 |
| iiot_text | (未注释) |
| iiot_thing_entity | 物实体 |
| iiot_thing_model | 物模型 |
| iiot_thing_order | 指令模型 |
| iiot_thing_order_history | 指令执行历史 |
| iiot_thing_property | iiot_thing_property |
| iiot_warm_expire_archive_instance | 温数据过期归档实例 |
| iiot_warm_expire_archive_record | 温数据过期归档记录 |
| iiot_warm_tag_value_expire_archive_record | 历史工况温数据过期归档记录 |
| iiot_zhilionline | (未注释) |

## 业务域概览

- **iiot** (84张表)：设备连接/数据采集/实时监控/报警管理/边缘计算

---

[[通威农发-数据库总览]]

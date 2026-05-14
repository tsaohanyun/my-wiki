---
title: Measure计量管理
created: 2026-05-07
updated: 2026-05-14
type: concept
tags: [数据库, 通威农发, measure, 计量管理]
confidence: high
---

# Measure计量管理

## 模块简介

Measure计量管理模块，负责通威农发各工厂的称重、计量和校准管理。涵盖秤管理（秤配置/秤校准/秤维护）、称重记录（毛重/皮重/净重）、计量器具管理、计量标准、校准记录等功能。

## 表清单（共25张表）

| 表名 | 说明 |
|------|------|
| measure_apply | 计量信息申请表 |
| measure_base_enforce_reason | 强制放行原因 |
| measure_equipment_t | 计量设备台账 |
| measure_flow_node | 计量流程节点 |
| measure_flow_script | 计量功能清单 |
| measure_handing_order_apply | 挂单申请 |
| measure_hardware | 计量硬件配置信息 |
| measure_hardware_type | 通讯方式维护 |
| measure_interface_receive | 计量接口接收数据 |
| measure_level_code_config | 计量level编码code的相关配置 |
| measure_operaconfig_ebs | ebs业务类型对应 |
| measure_operaconfig_level | 业务类型层级配置 |
| measure_operaconfig_point | 业务类型节点配置 |
| measure_operaconfig_t | 业务类型 |
| measure_operatype_config | 计量业务类型配置信息 |
| measure_position_config | 工厂电子围栏配置 |
| measure_registration_no | 排队号 |
| measure_rule_config | 任务规则配置 |
| measure_rule_item_t | 任务规则-执行顺序 |
| measure_station | 计量磅秤字典表 |
| measure_station_config | 计量磅秤信息配置信息表 |
| measure_weight | 计量重量信息表 |
| measure_weight_detail | 计量信息明细表 |
| measure_weight_one | 一检计量重量信息表 |
| measure_weight_two | 二检计量重量信息表 |

## 业务域概览

- **measure** (25张表)：秤管理/称重记录/计量器具/校准管理

---

[[通威农发-数据库总览]]

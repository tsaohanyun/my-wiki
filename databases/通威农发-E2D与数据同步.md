---
title: E2D与数据同步
created: 2026-05-07
updated: 2026-05-14
type: concept
description: >
  > 相关Wiki：数据库总览 | EBS-DIM接口 | 运营指标体系 E2D（Enterprise to Data）数据同步模块，负责通威农发与Oracle EBS ERP系统及其他外围系统的数据交换。涵盖EBS接口配置、数据同步任务、数据映射转换、同步日志、异常处理等功能。
tags: [smart-manufacturing]
sources: [raw/]
confidence: high
---


# E2D与数据同步


> 项目：**通威农发**（通威股份农业发展有限公司）
>
> 相关Wiki：[数据库总览](通威农发-数据库总览.md) | [EBS-DIM接口](../integrations/ebs-dim/README.md) | [运营指标体系](../kpi/README.md)
## 模块简介

E2D（Enterprise to Data）数据同步模块，负责通威农发与Oracle EBS ERP系统及其他外围系统的数据交换。涵盖EBS接口配置、数据同步任务、数据映射转换、同步日志、异常处理等功能。

## 表清单（共28张表）

| 表名 | 说明 |
|------|------|
| e2d_api_account | 通威非原料领用科目及用途数据表 |
| e2d_api_account_alias | 通威账户别名数据表 |
| e2d_api_balance | 通威期初库存数据表 |
| e2d_api_balances | 通威制造科目余额表 |
| e2d_api_bi_pe_ratio | 杂项分摊比例 |
| e2d_api_cost | 通威物料成本数据表 |
| e2d_api_cost_exp | 通威成本分摊数据表 |
| e2d_api_currency_rate | 各国费率转换表 |
| e2d_api_descr | 通威弹性域描述数据表 |
| e2d_api_energy_settle | 通威能源结算价数据表 |
| e2d_api_flexv | 通威值集数据表 |
| e2d_api_gme_prod_line | DIM产线产能数据表 |
| e2d_api_input_output_summary | 投入产出汇总查询表 |
| e2d_api_intpr | 通威内部采购数据表 |
| e2d_api_invuom | 通威单位换算数据表 |
| e2d_api_item_line | DIM品名与产线数据表 |
| e2d_api_jcylimit | 通威机物料库存额度数据表 |
| e2d_api_lookup | 从EBS获取的物料水分数据表 |
| e2d_api_main_product_index_standard | 通威产品指标标准主表 |
| e2d_api_order | 通威销售订单提货计划数据表 |
| e2d_api_org | 通威组织数据表 |
| e2d_api_potarget | 通威采购质检指标数据表 |
| e2d_api_product_index_standard | 通威产品指标标准 |
| e2d_api_purchase_order | 通威采购订单数据表 |
| e2d_api_sub | 通威子库数据表 |
| e2d_api_weigh_no | 通威磅单对应数据表 |
| e2d_api_weith_po | 通威进取磅单与采购单对应数据表 |
| e2d_flexv_level | 物料值集层级表 |

## 业务域概览

- **e2d** (28张表)：EBS接口/数据同步/映射转换/同步日志

---

[[通威农发-数据库总览]]

## 相关页面
- [[通威农发-APS计划排程]]
- [[通威农发-EDO设备管理]]
- [[通威农发-IIoT工业物联网]]
- [[通威农发-LM精益管理]]
- [[通威农发-MBM物料BOM与配方]]

---
author: Hermes Wiki Agent
confidence: high
created: 2026-05-07
description: E2D（Enterprise to Digital）数据同步模块，负责EBS系统与MES系统之间的数据接口和同步，包括接口配置、数据映射、同步日志等功能。
project: 通威农发
sources:
- raw/
status: published
tags:
- smart-manufacturing
title: E2D与数据同步
type: concept
updated: 2026-05-28
version: 1.0.20260529
---




# E2D与数据同步


> 项目：**通威农发**（通威股份农业发展有限公司）
>
> 相关Wiki：[数据库总览](通威农发-数据库总览.md) | [公共与基础模块](通威农发-公共与基础模块.md) | [产能利用率](通威农发-产能利用率.md)
## 模块简介

E2D（Enterprise to Digital）数据同步模块，负责EBS系统与MES系统之间的数据接口和同步，包括接口配置、数据映射、同步日志等功能。

## 表清单（共28张表）

| 表名 | 说明 |
|------|------|
| e2d_api_account |  |
| e2d_api_account_alias |  |
| e2d_api_balance |  |
| e2d_api_balances |  |
| e2d_api_bi_pe_ratio |  |
| e2d_api_cost |  |
| e2d_api_cost_exp |  |
| e2d_api_currency_rate |  |
| e2d_api_descr |  |
| e2d_api_energy_settle |  |
| e2d_api_flexv |  |
| e2d_api_gme_prod_line | DIM产线产能基准数据表，含设计产能、核定产能、极限产能、沉料产能多层级 |
| e2d_api_input_output_summary |  |
| e2d_api_intpr |  |
| e2d_api_invuom |  |
| e2d_api_item_line |  |
| e2d_api_jcylimit |  |
| e2d_api_lookup |  |
| e2d_api_main_product_index_standard |  |
| e2d_api_order |  |
| e2d_api_org |  |
| e2d_api_potarget |  |
| e2d_api_product_index_standard |  |
| e2d_api_purchase_order |  |
| e2d_api_sub |  |
| e2d_api_weigh_no |  |
| e2d_api_weith_po |  |
| e2d_flexv_level |  |

## 相关页面

- [数据库总览](通威农发-数据库总览.md) — 数据库总览
- [产能利用率](通威农发-产能利用率.md) — 跨模块专题：DIM产线产能基准数据

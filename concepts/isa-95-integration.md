---
title: ISA-95 企业控制系统集成
created: 2026-05-05
updated: 2026-05-05
type: concept
tags: [smart-manufacturing, mes, iot, architecture]
sources: [raw/articles/enterprise-control-system-integration.md]
---

# ISA-95 企业控制系统集成

ISA-95（IEC 62264）是**企业控制系统集成**的国际标准，定义了业务系统与制造控制系统之间的接口规范，是企业 IT/OT 融合的核心参考架构。

## 标准结构

### 第1部分：模型和术语
定义企业控制系统集成的通用术语和层级模型（Level 0-4），即 Purdue 层级模型：
- Level 4 — 业务规划与物流（ERP）
- Level 3 — 制造运行管理（MES/MOM）
- Level 2 — 过程控制（SCADA）
- Level 1 — 传感与执行
- Level 0 — 生产过程

### 第2部分：对象模型属性
定义各层级对象模型的详细属性结构，包括资源、能力、产品定义、生产调度等对象。

### 第3部分：制造运行管理活动模型
描述四大制造运行管理活动的模型：
- **生产运行管理**
- **维护运行管理**
- **质量运行管理**
- **库存运行管理**

### 第5部分：业务与制造间事务
定义业务层（ERP）与制造层（MES）之间的事务交互，包括工单下发、物料消耗、生产报告等。

## 应用价值

- MES/MOM 系统设计的国际标准基础
- 企业信息化与自动化融合的架构指南
- 智能制造标准体系的核心组成部分

相关概念：[[smart-manufacturing]]、[[smart-factory-planning]]、[[aps-advanced-planning-scheduling]]

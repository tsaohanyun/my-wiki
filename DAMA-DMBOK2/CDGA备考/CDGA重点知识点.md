---
title: CDGA重点知识点
aliases: [CDGA重点, 考试重点, 核心知识点]
tags: [cdga, 知识点, 考试]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: DAMA-DMBOK2
difficulty: intermediate
project: DAMA
---
# CDGA 重点知识点

## 数据治理核心概念

### 数据治理定义

**DAMA定义**：数据治理是对数据资产管理行使权力、控制和共同决策（规划、监控和执行）的系统。

**核心要素**：
- 战略一致性
- 风险管理
- 价值创造
- 合规性

### 数据治理vs数据管理

| 维度 | 数据治理 | 数据管理 |
|------|----------|----------|
| 关注点 | 决策权、政策、标准 | 技术实施、操作执行 |
| 层级 | 战略层 | 执行层 |
| 主体 | 治理委员会 | 数据管理专员 |
| 产出 | 政策、标准、流程 | 系统、工具、报告 |

## 数据质量维度

### DAMA数据质量维度

1. **准确性**（Accuracy）：数据是否正确反映现实
2. **完整性**（Completeness）：数据是否完整无缺失
3. **一致性**（Consistency）：数据在不同系统中是否一致
4. **及时性**（Timeliness）：数据是否及时更新
5. **唯一性**（Uniqueness）：数据是否重复
6. **有效性**（Validity）：数据是否符合业务规则

### 质量评估方法

```sql
-- 完整性检查
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN field_name IS NULL THEN 1 ELSE 0 END) as null_count,
    ROUND(SUM(CASE WHEN field_name IS NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as null_rate
FROM table_name;

-- 唯一性检查
SELECT 
    field_name,
    COUNT(*) as duplicate_count
FROM table_name
GROUP BY field_name
HAVING COUNT(*) > 1;
```

## 数据架构关键概念

### 企业数据架构组成

1. **数据模型**：概念模型、逻辑模型、物理模型
2. **数据流**：数据在系统间的流动
3. **数据标准**：命名规范、格式规范
4. **元数据**：数据的数据

### 数据仓库分层

```
ODS（操作数据层）：原始数据，保持原貌
DWD（明细数据层）：清洗后的明细数据
DWS（汇总数据层）：按主题汇总
ADS（应用数据层）：面向应用的数据集市
```

## 数据安全关键点

### 数据分类分级

| 级别 | 描述 | 示例 |
|------|------|------|
| 公开 | 可公开发布 | 产品宣传资料 |
| 内部 | 仅限内部使用 | 内部通讯录 |
| 机密 | 受限访问 | 财务报表 |
| 绝密 | 严格控制 | 核心配方 |

### 访问控制模型

1. **DAC**（自主访问控制）：数据所有者决定权限
2. **MAC**（强制访问控制）：基于安全标签
3. **RBAC**（基于角色的访问控制）：基于角色分配权限

## 元数据管理

### 元数据类型

1. **技术元数据**：表结构、字段类型、索引
2. **业务元数据**：业务定义、数据标准、数据血缘
3. **操作元数据**：数据量、更新时间、数据质量

### 数据血缘

数据血缘描述了数据的来源、转换过程和去向。

```
源系统 → ETL → ODS → DWD → DWS → ADS → 报表
```

## 相关页面

- [[CDGA考试概述]]
- [[CDGA模拟试题]]
- [[DAMA-DMBOK2数据管理知识体系]]
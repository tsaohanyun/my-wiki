---
author: Hermes Wiki Agent
created: '2026-06-26'
description: '> 适用数据库：MySQL 8.0.32 > 业务系统：通威农发 MES / WMS / QMS / APS > 创建日期：2026-06-26
  1. [数据质量检查](#1-数据质量检查) 2. [业务分析](#2-业务分析) 3. [窗口函数实战](#3-窗口函数实战) 4. [递归 CTE](#4-递归-cte)
  5. [动态 SQL](#5-动态-sql) 6. [性能优化](#6-性能优...'
project: 通用
status: published
tags:
- workflow
- template
- exception
- database
- sql
title: SQL 查询模板库
type: concept
updated: '2026-06-26'
version: 1.0.20260626
---


# SQL 查询模板库

> 适用数据库：MySQL 8.0.32  
> 业务系统：通威农发 MES / WMS / QMS / APS  
> 创建日期：2026-06-26

---

## 目录

1. [数据质量检查](#1-数据质量检查)
2. [业务分析](#2-业务分析)
3. [窗口函数实战](#3-窗口函数实战)
4. [递归 CTE](#4-递归-cte)
5. [动态 SQL](#5-动态-sql)
6. [性能优化](#6-性能优化)

---

## 1. 数据质量检查

### 1.1 重复检测 — 工单产出记录重复

**场景说明**：`mes_workorder_output` 记录每个工单的产出明细，同一工单+物料批次+包装口不应出现重复记录。

```sql
-- 查找重复的工单产出记录
SELECT 
    workorder_no,
    material_batch,
    packing_port,
    COUNT(*) AS dup_count,
    GROUP_CONCAT(id ORDER BY create_date) AS dup_ids
FROM mes_workorder_output
WHERE validflag = '1'
GROUP BY workorder_no, material_batch, packing_port
HAVING COUNT(*) > 1
ORDER BY dup_count DESC;
```

**关键点注释**：
- `GROUP_CONCAT(id)` 可以快速拿到重复记录的 ID，方便后续清理
- 通常结合 `create_date` 排序，保留最新记录、删除旧记录

**常见陷阱**：
- `stored_date` 或 `packing_date` 可能为 NULL，导致看起来"重复"的记录实际是时序不同
- 多租户环境务必加上 `tenant_id` 过滤条件

---

### 1.2 空值检查 — 发运单关键字段缺失

**场景说明**：`wms_dispatch_order` 中发运单的关键字段（如客户、车牌号、发货日期）不应为空。

```sql
-- 发运单关键字段空值检查
SELECT 
    order_no,
    customer_name,
    plate_number,
    dispatch_date,
    CASE 
        WHEN customer_name IS NULL OR customer_name = '' THEN '客户名称缺失'
        WHEN plate_number IS NULL OR plate_number = '' THEN '车牌号缺失'
        WHEN dispatch_date IS NULL THEN '发货日期缺失'
    END AS missing_field
FROM wms_dispatch_order
WHERE state != '9'  -- 排除已取消
  AND (
      customer_name IS NULL OR customer_name = ''
      OR plate_number IS NULL OR plate_number = ''
      OR dispatch_date IS NULL
  )
ORDER BY create_date DESC
LIMIT 100;
```

**关键点注释**：
- 通威系统中很多 VARCHAR 字段用空字符串 `''` 而非 NULL 表示缺失，两种都要检查
- `state = '9'` 通常代表已取消/作废，应排除

**常见陷阱**：
- 有些字段虽然 NOT NULL，但默认值是空字符串，不能只用 `IS NULL` 判断
- 多表关联时，JOIN 会过滤掉 NULL 匹配行，改用 `LEFT JOIN + WHERE ... IS NULL` 模式找不一致数据

---

### 1.3 一致性校验 — 投料重量 vs 理论用量

**场景说明**：`mes_workorder_feeding` 记录实际投料，应与配方理论用量保持一致。

```sql
-- 投料偏差检测：实际投料 vs 理论用量偏差超过 5%
SELECT 
    f.workorder_no,
    f.material_code,
    f.material_spec,
    f.theory_weight,
    f.measure_weight,
    ROUND(
        ABS(CAST(f.measure_weight AS DECIMAL(18,4)) 
          - CAST(f.theory_weight AS DECIMAL(18,4))) 
        / NULLIF(CAST(f.theory_weight AS DECIMAL(18,4)), 0) * 100, 
        2
    ) AS deviation_pct
FROM mes_workorder_feeding f
WHERE f.validflag = '1'
  AND f.theory_weight IS NOT NULL
  AND f.theory_weight != '0'
  AND ABS(
      CAST(f.measure_weight AS DECIMAL(18,4)) 
    - CAST(f.theory_weight AS DECIMAL(18,4))
  ) / NULLIF(CAST(f.theory_weight AS DECIMAL(18,4)), 0) > 0.05
ORDER BY deviation_pct DESC;
```

**关键点注释**：
- `NULLIF(..., 0)` 防止除零错误
- 很多数值字段在表中定义为 `VARCHAR`，需要显式 `CAST`
- 5% 阈值可根据实际业务调整

**常见陷阱**：
- VARCHAR 存数字时，`CAST('' AS DECIMAL)` 会报错，需要先过滤空字符串
- `theory_weight` 单位可能是吨或千克，需确认单位统一

---

### 1.4 跨表一致性 — 采购订单 vs 到货单

**场景说明**：`wms_purchase_order` 采购订单的到货数量应与 `wms_asn_order` 到货单汇总一致。

```sql
-- 采购订单与到货单数量比对
SELECT 
    po.code AS purchase_order_no,
    po.state,
    po.con_quantity AS plan_qty,
    IFNULL(asn.total_received, 0) AS received_qty,
    po.con_quantity - IFNULL(asn.total_received, 0) AS diff_qty
FROM wms_purchase_order po
LEFT JOIN (
    SELECT 
        source_code,
        SUM(qty) AS total_received
    FROM wms_asn_order
    WHERE state != '9'
    GROUP BY source_code
) asn ON asn.source_code = po.code
WHERE po.state NOT IN ('9', '10')  -- 排除已取消/已完成
  AND ABS(CAST(po.con_quantity AS DECIMAL(18,4)) 
        - IFNULL(asn.total_received, 0)) > 0.01
ORDER BY diff_qty DESC;
```

**关键点注释**：
- 子查询先聚合 `wms_asn_order`，避免外层直接 JOIN 导致笛卡尔积
- `IFNULL` 处理完全没有到货记录的情况

**常见陷阱**：
- `wms_asn_order` 有大量按年份分表（如 `wms_asn_order2024`、`wms_asn_order2025`），查询时注意是否需要 UNION ALL 历史表
- `source_code` 字段格式不统一时（如前缀差异），需先做标准化

---

## 2. 业务分析

### 2.1 同比环比 — 工厂月度产出分析

**场景说明**：对比各工厂成品月度入库量的同比增长和环比变化。

```sql
-- 工厂月度成品产出同比环比分析
WITH monthly_output AS (
    SELECT 
        factory_id,
        DATE_FORMAT(stored_date, '%Y-%m') AS month_key,
        SUM(CAST(stored_num AS DECIMAL(18,4))) AS total_output
    FROM mes_workorder_output
    WHERE validflag = '1'
      AND stored_date >= DATE_SUB(CURDATE(), INTERVAL 14 MONTH)
    GROUP BY factory_id, DATE_FORMAT(stored_date, '%Y-%m')
)
SELECT 
    a.factory_id,
    a.month_key,
    a.total_output AS current_output,
    b.total_output AS last_month_output,
    c.total_output AS last_year_output,
    -- 环比增长率
    ROUND(
        (a.total_output - IFNULL(b.total_output, 0)) 
        / NULLIF(b.total_output, 0) * 100, 2
    ) AS mom_growth_pct,
    -- 同比增长率
    ROUND(
        (a.total_output - IFNULL(c.total_output, 0)) 
        / NULLIF(c.total_output, 0) * 100, 2
    ) AS yoy_growth_pct
FROM monthly_output a
LEFT JOIN monthly_output b 
    ON a.factory_id = b.factory_id 
   AND b.month_key = DATE_FORMAT(DATE_SUB(STR_TO_DATE(CONCAT(a.month_key, '-01'), '%Y-%m-%d'), INTERVAL 1 MONTH), '%Y-%m')
LEFT JOIN monthly_output c 
    ON a.factory_id = c.factory_id 
   AND c.month_key = DATE_FORMAT(DATE_SUB(STR_TO_DATE(CONCAT(a.month_key, '-01'), '%Y-%m-%d'), INTERVAL 1 YEAR), '%Y-%m')
ORDER BY a.factory_id, a.month_key DESC;
```

**关键点注释**：
- CTE `monthly_output` 先按月汇总，避免重复计算
- `DATE_FORMAT` + `STR_TO_DATE` 组合实现月份偏移
- `NULLIF` 防止除零，`IFNULL` 处理缺失月份

**常见陷阱**：
- `stored_num` 是 VARCHAR 类型，必须 CAST
- 环比计算中，上月数据缺失时结果为 NULL 而非 0，注意业务含义

---

### 2.2 排名 TopN — 发货量 Top 10 客户

**场景说明**：按发货重量统计客户排名，用于客户价值分析。

```sql
-- 月度发货量 Top 10 客户
SELECT 
    customer_name,
    COUNT(DISTINCT order_no) AS order_count,
    SUM(CAST(net_weight AS DECIMAL(18,4))) AS total_net_weight,
    SUM(CAST(gross_weight AS DECIMAL(18,4))) AS total_gross_weight,
    ROW_NUMBER() OVER (ORDER BY SUM(CAST(net_weight AS DECIMAL(18,4))) DESC) AS ranking
FROM wms_dispatch_order
WHERE state NOT IN ('9', '0')  -- 排除取消和草稿
  AND dispatch_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')  -- 本月
GROUP BY customer_name
ORDER BY total_net_weight DESC
LIMIT 10;
```

**关键点注释**：
- `ROW_NUMBER()` 在 `ORDER BY` 之后才计算，这里直接用 `LIMIT 10` 即可
- 如果需要"并列排名"效果，改用 `RANK()` 或 `DENSE_RANK()`

**常见陷阱**：
- `customer_name` 可能存在同一客户多种写法（如空格、全半角），需先做数据清洗
- `net_weight` 可能为负值（退货场景），需确认业务是否需要排除

---

### 2.3 漏斗分析 — 生产订单到入库全流程

**场景说明**：追踪生产订单从下发→投料→产出→入库的转化漏斗。

```sql
-- 生产订单全链路漏斗分析
SELECT 
    DATE_FORMAT(t.actual_begin_date, '%Y-%m') AS month_key,
    COUNT(DISTINCT t.workorder_no) AS total_workorders,           -- 工单总数
    COUNT(DISTINCT f.workorder_no) AS feeding_workorders,         -- 已投料工单数
    COUNT(DISTINCT o.workorder_no) AS output_workorders,          -- 已产出工单数
    COUNT(DISTINCT CASE WHEN t.workorder_status = '4' THEN t.workorder_no END) AS completed_workorders,  -- 已完工工单数
    -- 各阶段转化率
    ROUND(COUNT(DISTINCT f.workorder_no) / NULLIF(COUNT(DISTINCT t.workorder_no), 0) * 100, 2) AS feeding_rate,
    ROUND(COUNT(DISTINCT o.workorder_no) / NULLIF(COUNT(DISTINCT f.workorder_no), 0) * 100, 2) AS output_rate,
    ROUND(COUNT(DISTINCT CASE WHEN t.workorder_status = '4' THEN t.workorder_no END) 
        / NULLIF(COUNT(DISTINCT o.workorder_no), 0) * 100, 2) AS completion_rate
FROM mes_workorder_t t
LEFT JOIN (
    SELECT DISTINCT workorder_no 
    FROM mes_workorder_feeding 
    WHERE validflag = '1'
) f ON f.workorder_no = t.workorder_no
LEFT JOIN (
    SELECT DISTINCT workorder_no 
    FROM mes_workorder_output 
    WHERE validflag = '1'
) o ON o.workorder_no = t.workorder_no
WHERE t.actual_begin_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
  AND t.validflag = '1'
GROUP BY DATE_FORMAT(t.actual_begin_date, '%Y-%m')
ORDER BY month_key DESC;
```

**关键点注释**：
- `COUNT(DISTINCT workorder_no)` 避免同一个工单多条投料/产出记录被重复计数
- 漏斗各阶段用 LEFT JOIN 串联，确保不会丢掉未进入下一阶段的工单
- `workorder_status = '4'` 表示已完工，具体值需根据字典确认

**常见陷阱**：
- 投料和产出可能同一天发生，时间范围过滤不当会导致数据截断
- 某些工单可能跳过投料直接领料，逻辑需根据实际流程调整

---

### 2.4 物料消耗对比 — 实际 vs 配方标准

**场景说明**：对比实际投料量与 BOM 配方标准用量，发现异常消耗。

```sql
-- 工单物料实际消耗 vs 配方标准对比
WITH bom_standard AS (
    SELECT 
        pb.code AS bom_code,
        pb.bom_version,
        pbcl.material_id,
        pbcl.quantity_per,
        pbcl.loss_rate,
        ROUND(pbcl.quantity_per * (1 + IFNULL(pbcl.loss_rate, 0) / 100), 4) AS standard_qty_with_loss
    FROM product_bom pb
    JOIN product_bom_component_line pbcl ON pbcl.product_bom_id = pb.id
    WHERE pb.is_default = '1'
      AND pbcl.delete_flag = '0'
)
SELECT 
    t.workorder_no,
    t.material_code AS product_code,
    t.material_spec AS product_spec,
    t.workorder_num AS plan_num,
    f.material_code AS feeding_material,
    f.measure_weight AS actual_weight,
    bs.standard_qty_with_loss,
    ROUND(
        (CAST(f.measure_weight AS DECIMAL(18,4)) 
         - CAST(t.workorder_num AS DECIMAL(18,4)) * bs.standard_qty_with_loss)
        / NULLIF(CAST(t.workorder_num AS DECIMAL(18,4)) * bs.standard_qty_with_loss, 0) * 100,
        2
    ) AS deviation_pct
FROM mes_workorder_t t
JOIN mes_workorder_feeding f ON f.workorder_no = t.workorder_no AND f.validflag = '1'
LEFT JOIN bom_standard bs ON bs.material_id = f.material_id
WHERE t.actual_begin_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
  AND t.validflag = '1'
HAVING ABS(deviation_pct) > 3  -- 偏差超过 3%
ORDER BY ABS(deviation_pct) DESC;
```

**关键点注释**：
- CTE 预计算带损耗率的标准用量
- `HAVING` 直接对计算字段过滤，避免嵌套子查询
- 用 `material_id` 关联 BOM，而非 `material_code`，因为编码可能有版本差异

**常见陷阱**：
- `loss_rate` 单位是百分比还是小数，需确认（此处按百分比处理）
- 同一物料可能有多个 BOM 版本，务必用 `is_default = '1'` 过滤默认版本

---

## 3. 窗口函数实战

### 3.1 累计求和 — 日产量累计趋势

**场景说明**：按日期计算工厂成品入库的累计量，用于观察生产进度是否符合预期。

```sql
-- 工厂日产量累计求和（本月）
SELECT 
    factory_id,
    DATE(stored_date) AS prod_date,
    SUM(CAST(stored_num AS DECIMAL(18,4))) AS daily_output,
    SUM(SUM(CAST(stored_num AS DECIMAL(18,4)))) 
        OVER (PARTITION BY factory_id ORDER BY DATE(stored_date)) AS cumulative_output
FROM mes_workorder_output
WHERE validflag = '1'
  AND stored_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY factory_id, DATE(stored_date)
ORDER BY factory_id, prod_date;
```

**关键点注释**：
- `SUM(...) OVER (ORDER BY ...)` 实现累计求和，无需自连接
- 外层 `SUM` 是按日聚合，内层窗口函数是累计
- `PARTITION BY factory_id` 让每个工厂独立累计

**常见陷阱**：
- 窗口函数中的 `ORDER BY` 必须保证排序字段唯一，否则结果不确定
- 大数据量下累计求和可能较慢，可考虑物化视图或定时任务预计算

---

### 3.2 移动平均 — 投料量 7 日移动平均

**场景说明**：计算每日投料量的 7 日移动平均，平滑日间波动，观察趋势。

```sql
-- 每日投料量 7 日移动平均
WITH daily_feeding AS (
    SELECT 
        factory_id,
        DATE(feeding_date) AS feed_date,
        SUM(CAST(measure_weight AS DECIMAL(18,4))) AS daily_weight
    FROM mes_workorder_feeding
    WHERE validflag = '1'
      AND feeding_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    GROUP BY factory_id, DATE(feeding_date)
)
SELECT 
    factory_id,
    feed_date,
    daily_weight,
    ROUND(
        AVG(daily_weight) OVER (
            PARTITION BY factory_id 
            ORDER BY feed_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS ma_7d,
    -- 对比前一日
    LAG(daily_weight, 1) OVER (PARTITION BY factory_id ORDER BY feed_date) AS prev_day_weight,
    ROUND(
        (daily_weight - LAG(daily_weight, 1) OVER (PARTITION BY factory_id ORDER BY feed_date))
        / NULLIF(LAG(daily_weight, 1) OVER (PARTITION BY factory_id ORDER BY feed_date), 0) * 100,
        2
    ) AS day_over_day_pct
FROM daily_feeding
ORDER BY factory_id, feed_date;
```

**关键点注释**：
- `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` 定义 7 行窗口（含当前行）
- 如果是 `RANGE` 而非 `ROWS`，则按值范围而非行数计算，可能包含更多行
- `LAG(..., 1)` 取前一行的值

**常见陷阱**：
- 前 6 天的移动平均不足 7 日，业务上可能需要标记为"不完整"
- 缺少某天数据时，移动平均会跳过该天而非补零，需用日历表 LEFT JOIN 补齐

---

### 3.3 分组排名 — 各工厂产量 Top 3 产品

**场景说明**：找出每个工厂产量最高的 3 个产品。

```sql
-- 各工厂月度产量 Top 3 产品
WITH product_ranking AS (
    SELECT 
        factory_id,
        material_code,
        material_spec,
        SUM(CAST(stored_num AS DECIMAL(18,4))) AS total_output,
        DENSE_RANK() OVER (
            PARTITION BY factory_id 
            ORDER BY SUM(CAST(stored_num AS DECIMAL(18,4))) DESC
        ) AS rank_in_factory
    FROM mes_workorder_output
    WHERE validflag = '1'
      AND stored_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    GROUP BY factory_id, material_code, material_spec
)
SELECT *
FROM product_ranking
WHERE rank_in_factory <= 3
ORDER BY factory_id, rank_in_factory;
```

**关键点注释**：
- `DENSE_RANK()` 并列排名不跳号（如 1,1,2,3）
- 如果需要跳号并列，用 `RANK()`（如 1,1,3,4）
- 如果需要唯一排名，用 `ROW_NUMBER()`（如 1,2,3,4）

**常见陷阱**：
- 窗口函数不能直接在 `WHERE` 中使用，必须放在 CTE 或子查询中
- `DENSE_RANK` 在并列较多时，Top 3 可能返回超过 3 行

---

### 3.4 分组内偏移 — 同产品上批次 vs 当前批次

**场景说明**：对比同一产品连续两个生产批次的产出数量差异。

```sql
-- 同一产品相邻批次产出对比
SELECT 
    material_code,
    material_batch,
    workorder_no,
    CAST(stored_num AS DECIMAL(18,4)) AS current_output,
    LAG(material_batch) OVER (PARTITION BY material_code ORDER BY stored_date) AS prev_batch,
    LAG(CAST(stored_num AS DECIMAL(18,4))) OVER (PARTITION BY material_code ORDER BY stored_date) AS prev_output,
    ROUND(
        (CAST(stored_num AS DECIMAL(18,4)) 
         - LAG(CAST(stored_num AS DECIMAL(18,4))) OVER (PARTITION BY material_code ORDER BY stored_date))
        / NULLIF(LAG(CAST(stored_num AS DECIMAL(18,4))) OVER (PARTITION BY material_code ORDER BY stored_date), 0) * 100,
        2
    ) AS batch_diff_pct
FROM mes_workorder_output
WHERE validflag = '1'
  AND stored_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
ORDER BY material_code, stored_date DESC;
```

**关键点注释**：
- `LAG(...)` 默认取前一行，`LEAD(...)` 取后一行
- `PARTITION BY material_code` 保证在同产品内比较
- `ORDER BY stored_date` 决定"相邻"的逻辑

**常见陷阱**：
- `stored_date` 相同时排序不确定，建议加 `id` 作为 tiebreaker
- 第一批次的 `LAG` 结果为 NULL，业务上应标记为"首个批次"

---

## 4. 递归 CTE

### 4.1 层级遍历 — 组织架构树

**场景说明**：从某个部门节点开始，递归展开所有下属部门。

```sql
-- 递归展开组织架构（示例：从某工厂出发）
WITH RECURSIVE org_tree AS (
    -- 锚点：起始节点
    SELECT 
        id,
        parent_id,
        org_name,
        org_code,
        0 AS depth,
        CAST(org_code AS CHAR(1000)) AS path
    FROM sys_org  -- 组织表（根据实际表名调整）
    WHERE org_code = 'FACTORY001'  -- 起始工厂编码
    
    UNION ALL
    
    -- 递归：子节点
    SELECT 
        c.id,
        c.parent_id,
        c.org_name,
        c.org_code,
        p.depth + 1,
        CONCAT(p.path, ' > ', c.org_code)
    FROM sys_org c
    JOIN org_tree p ON c.parent_id = p.id
    WHERE c.delete_flag = '0'
)
SELECT 
    CONCAT(REPEAT('  ', depth), org_name) AS tree_display,
    org_code,
    depth,
    path
FROM org_tree
ORDER BY path;
```

**关键点注释**：
- `WITH RECURSIVE` 是 MySQL 8.0 的特性，8.0.32 完全支持
- 锚点（anchor）是递归起点，递归部分通过 `JOIN` 引用自身
- `depth` 字段追踪层级深度，`path` 记录完整路径

**常见陷阱**：
- 必须有终止条件，否则无限递归。MySQL 默认 `cte_max_recursion_depth = 1000`
- 父子关系中如果有环（数据异常），会导致无限递归，可加 `WHERE depth < 20` 防护
- `CAST(... AS CHAR(1000))` 是必须的，否则 path 字段类型不兼容

---

### 4.2 物料 BOM 展开 — 产品配方层级

**场景说明**：从成品出发，递归展开其 BOM 配方的完整物料层级结构。

```sql
-- BOM 多层级展开（成品→半成品→原料）
WITH RECURSIVE bom_explosion AS (
    -- 锚点：成品
    SELECT 
        pb.id AS bom_id,
        pb.code AS bom_code,
        pb.product_id AS parent_material_id,
        pbcl.material_id AS component_material_id,
        pbcl.quantity_per,
        pbcl.loss_rate,
        1 AS level,
        CAST(pb.code AS CHAR(1000)) AS bom_path
    FROM product_bom pb
    JOIN product_bom_component_line pbcl ON pbcl.product_bom_id = pb.id
    WHERE pb.product_id = :target_product_id  -- 目标成品物料ID
      AND pb.is_default = '1'
      AND pbcl.delete_flag = '0'
    
    UNION ALL
    
    -- 递归：如果子组件自身也有 BOM，继续展开
    SELECT 
        pb2.id,
        pb2.code,
        pb2.product_id,
        pbcl2.material_id,
        pbcl2.quantity_per,
        pbcl2.loss_rate,
        be.level + 1,
        CONCAT(be.bom_path, ' → ', pb2.code)
    FROM bom_explosion be
    JOIN product_bom pb2 ON pb2.product_id = be.component_material_id 
                         AND pb2.is_default = '1'
    JOIN product_bom_component_line pbcl2 ON pbcl2.product_bom_id = pb2.id
    WHERE pbcl2.delete_flag = '0'
      AND be.level < 10  -- 防止无限递归
)
SELECT 
    level,
    bom_code,
    parent_material_id,
    component_material_id,
    quantity_per,
    loss_rate,
    ROUND(quantity_per * (1 + IFNULL(loss_rate, 0) / 100), 4) AS qty_with_loss,
    bom_path
FROM bom_explosion
ORDER BY bom_path;
```

**关键点注释**：
- 通威的 BOM 是两级表：`product_bom`（BOM 头）+ `product_bom_component_line`（BOM 行）
- `:target_product_id` 是参数化占位符，实际使用时替换
- `level < 10` 是安全防护，饲料行业 BOM 通常不超过 3-4 层

**常见陷阱**：
- 如果同一物料出现在多个 BOM 版本中，务必用 `is_default = '1'` 过滤
- `quantity_per` 是每单位产品的用量，最终需求需要乘以计划产量
- 环形引用（A→B→A）在实际数据中可能出现，需要死循环防护

---

### 4.3 工单父子关系 — 拆单追溯

**场景说明**：通威系统中工单可拆分为子工单，通过 `parent_workorder_id` 关联。追溯某个工单的所有子工单。

```sql
-- 工单拆单链追溯
WITH RECURSIVE workorder_chain AS (
    -- 锚点：根工单
    SELECT 
        id,
        workorder_no,
        parent_workorder_no,
        workorder_status,
        material_code,
        workorder_num,
        0 AS split_depth,
        CAST(workorder_no AS CHAR(500)) AS chain_path
    FROM mes_workorder_t
    WHERE workorder_no = :root_workorder_no  -- 起始工单号
      AND validflag = '1'
    
    UNION ALL
    
    -- 递归：子工单
    SELECT 
        child.id,
        child.workorder_no,
        child.parent_workorder_no,
        child.workorder_status,
        child.material_code,
        child.workorder_num,
        wc.split_depth + 1,
        CONCAT(wc.chain_path, ' → ', child.workorder_no)
    FROM mes_workorder_t child
    JOIN workorder_chain wc ON child.parent_workorder_no = wc.workorder_no
    WHERE child.validflag = '1'
      AND wc.split_depth < 20
)
SELECT 
    CONCAT(REPEAT('  ', split_depth), workorder_no) AS tree_view,
    workorder_status,
    material_code,
    workorder_num,
    chain_path
FROM workorder_chain
ORDER BY chain_path;
```

**关键点注释**：
- `parent_workorder_no` 关联父子工单
- `has_child = '1'` 字段可预判是否有子工单
- 通威的工单拆单通常用于：计划变更、产能分配、分批生产

**常见陷阱**：
- 某些历史数据中 `parent_workorder_no` 可能为空字符串而非 NULL
- 拆单后原工单状态可能变更，追溯时注意 `validflag` 过滤

---

## 5. 动态 SQL

### 5.1 存储过程模板 — 动态条件查询发运单

**场景说明**：根据不同条件动态拼接查询发运单，适用于报表查询界面。

```sql
-- 存储过程：动态查询发运单
DELIMITER $$

CREATE PROCEDURE sp_query_dispatch_orders(
    IN p_factory_id     VARCHAR(64),   -- 工厂ID（可选）
    IN p_customer_name  VARCHAR(256),  -- 客户名称（可选，支持模糊）
    IN p_state          VARCHAR(4),    -- 状态（可选）
    IN p_date_from      VARCHAR(10),   -- 开始日期
    IN p_date_to        VARCHAR(10),   -- 结束日期
    IN p_page_size      INT,           -- 每页条数
    IN p_page_num       INT            -- 页码
)
BEGIN
    SET @sql = 'SELECT 
                    do.order_no,
                    do.customer_name,
                    do.dispatch_date,
                    do.plate_number,
                    do.net_weight,
                    do.state,
                    do.create_date
                FROM wms_dispatch_order do
                WHERE 1=1';
    
    -- 工厂过滤
    IF p_factory_id IS NOT NULL AND p_factory_id != '' THEN
        SET @sql = CONCAT(@sql, ' AND do.production_department = ''', p_factory_id, '''');
    END IF;
    
    -- 客户名称模糊查询
    IF p_customer_name IS NOT NULL AND p_customer_name != '' THEN
        SET @sql = CONCAT(@sql, ' AND do.customer_name LIKE ''%', p_customer_name, '%''');
    END IF;
    
    -- 状态过滤
    IF p_state IS NOT NULL AND p_state != '' THEN
        SET @sql = CONCAT(@sql, ' AND do.state = ''', p_state, '''');
    END IF;
    
    -- 日期范围
    SET @sql = CONCAT(@sql, ' AND do.dispatch_date BETWEEN ''', p_date_from, ''' AND ''', p_date_to, '''');
    
    -- 排序和分页
    SET @offset = (p_page_num - 1) * p_page_size;
    SET @sql = CONCAT(@sql, ' ORDER BY do.dispatch_date DESC LIMIT ', p_page_size, ' OFFSET ', @offset);
    
    -- 执行
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

-- 调用示例
CALL sp_query_dispatch_orders('FACTORY001', '饲料', '3', '2026-01-01', '2026-06-30', 20, 1);
```

**关键点注释**：
- `SET @sql = CONCAT(...)` 动态拼接 SQL 字符串
- `PREPARE stmt FROM @sql; EXECUTE stmt;` 是 MySQL 动态 SQL 的标准写法
- `WHERE 1=1` 是常见技巧，方便后续追加 AND 条件

**常见陷阱**：
- 字符串拼接有 SQL 注入风险，生产环境应限制输入参数
- 存储过程调试困难，建议先在普通 SQL 中验证逻辑
- `LIMIT` 参数不能用 `?` 占位符，必须直接拼接整数值

---

### 5.2 使用 ? 占位符的安全查询模板（应用程序侧）

**场景说明**：在 Java/Python 应用中使用参数化查询，防止 SQL 注入。

```sql
-- 模板：按条件查询工单产出（使用 :param 占位符）
-- 适用于 SQLAlchemy / MyBatis / PreparedStatement
SELECT 
    o.workorder_no,
    o.material_code,
    o.material_spec,
    o.material_batch,
    o.stored_num,
    o.stored_date,
    o.packing_line
FROM mes_workorder_output o
WHERE o.validflag = '1'
  AND o.factory_id = :factory_id
  AND o.material_code LIKE CONCAT('%', :material_keyword, '%')
  AND o.stored_date >= :start_date
  AND o.stored_date < DATE_ADD(:end_date, INTERVAL 1 DAY)
ORDER BY o.stored_date DESC
LIMIT :limit_count OFFSET :offset_count;
```

**关键点注释**：
- `:param` 是命名参数占位符（MyBatis 用 `#{param}`，JDBC 用 `?`）
- 日期用 `< DATE_ADD(:end_date, INTERVAL 1 DAY)` 确保包含结束日期当天
- `LIKE CONCAT('%', :keyword, '%')` 防止关键字注入

**常见陷阱**：
- MyBatis 中 `${param}` 是直接拼接，`#{param}` 才是预编译参数
- `LIMIT` 的参数必须是正整数，应用层要做校验

---

### 5.3 批量更新模板 — 批次状态批量刷新

**场景说明**：批量更新物料批次的质检状态。

```sql
-- 使用临时表批量更新（推荐方式，避免逐条 UPDATE）
-- 第1步：创建临时表
CREATE TEMPORARY TABLE tmp_batch_update (
    material_batch VARCHAR(64) PRIMARY KEY,
    new_status VARCHAR(16),
    update_user VARCHAR(64)
);

-- 第2步：插入待更新数据（从应用层批量 INSERT）
INSERT INTO tmp_batch_update (material_batch, new_status, update_user) VALUES
('BATCH001', '3', 'system'),
('BATCH002', '3', 'system'),
('BATCH003', '4', 'system');

-- 第3步：使用 JOIN 批量更新
UPDATE qms_batc_material qm
JOIN tmp_batch_update tmp ON qm.material_batch = tmp.material_batch
SET 
    qm.material_batch_status = tmp.new_status,
    qm.update_user = tmp.update_user,
    qm.update_date = NOW()
WHERE qm.validflag = '1';

-- 第4步：清理临时表
DROP TEMPORARY TABLE tmp_batch_update;
```

**关键点注释**：
- `UPDATE ... JOIN` 比逐条 UPDATE 效率高得多
- 临时表只在当前会话有效，不会影响其他连接
- 使用 `CREATE TEMPORARY TABLE` 避免命名冲突

**常见陷阱**：
- 批量更新前务必备份或在事务中执行，方便回滚
- `UPDATE ... JOIN` 在大数据量下可能锁表，建议分批执行（每批 1000-5000 条）

---

## 6. 性能优化

### 6.1 EXPLAIN 解读 — 发运单查询执行计划

**场景说明**：使用 EXPLAIN 分析查询性能瓶颈。

```sql
-- 查看执行计划
EXPLAIN ANALYZE
SELECT 
    do.order_no,
    do.customer_name,
    do.dispatch_date,
    do.net_weight,
    dod.item_code,
    dod.qty,
    dod.pick_qty
FROM wms_dispatch_order do
JOIN wms_dispatch_order_detail dod ON dod.dispatch_order_no = do.order_no
WHERE do.state = '3'
  AND do.dispatch_date >= '2026-06-01'
  AND do.dispatch_date < '2026-07-01'
  AND do.customer_name LIKE '%通威%'
ORDER BY do.dispatch_date DESC
LIMIT 100;

-- 简化版 EXPLAIN（不实际执行）
EXPLAIN FORMAT=JSON
SELECT ... -- 同上
```

**EXPLAIN 结果关键字段解读**：

| 字段 | 含义 | 优化方向 |
|------|------|---------|
| `type` | 访问类型 | `ALL`(全表扫描) → `index` → `range` → `ref` → `eq_ref` → `const`，越往后越好 |
| `key` | 实际使用的索引 | NULL 表示没有使用索引 |
| `rows` | 预估扫描行数 | 越小越好 |
| `filtered` | 过滤比例 | 越高越好（100% 最好） |
| `Extra` | 额外信息 | `Using filesort`(需排序优化)、`Using temporary`(需临时表优化) |

**关键点注释**：
- `EXPLAIN ANALYZE` 会实际执行查询并返回真实耗时（MySQL 8.0+）
- `FORMAT=JSON` 提供更详细的信息，包括 `cost` 估算
- 关注 `rows` 列，如果预估行数远大于实际行数，说明统计信息过时

**常见陷阱**：
- `EXPLAIN` 的预估行数可能不准确，实际优化要看 `EXPLAIN ANALYZE`
- `Using filesort` 不一定是坏的，小结果集排序很快

---

### 6.2 索引建议 — 高频查询索引设计

**场景说明**：为通威系统高频查询场景设计索引。

```sql
-- 发运单表：按状态+日期范围查询（最高频）
CREATE INDEX idx_dispatch_state_date 
ON wms_dispatch_order (state, dispatch_date, customer_name);

-- 发运单明细：按发运单号关联
CREATE INDEX idx_dispatch_detail_order_no 
ON wms_dispatch_order_detail (dispatch_order_no, item_code);

-- 工单产出：按工厂+日期+物料查询
CREATE INDEX idx_output_factory_date_material 
ON mes_workorder_output (factory_id, stored_date, material_code, validflag);

-- 工单投料：按工单号查询
CREATE INDEX idx_feeding_workorder 
ON mes_workorder_feeding (workorder_no, validflag, material_code);

-- 质检批次：按批次号+物料查询
CREATE INDEX idx_batc_material_batch 
ON qms_batc_material (material_batch, material_code, validflag);

-- 采购订单：按状态+日期查询
CREATE INDEX idx_purchase_state_date 
ON wms_purchase_order (state, bill_date, supplier_code);
```

**索引设计原则**：

1. **最左前缀**：复合索引 `(A, B, C)` 可以加速 `A`、`(A,B)`、`(A,B,C)` 查询
2. **选择性高的列放前面**：`state` 枚举值少，放在 `(state, date)` 的前面
3. **覆盖索引**：如果查询只需要索引中的列，无需回表
4. **避免过度索引**：每个额外索引都会降低写入性能

**查看已有索引**：
```sql
-- 查看表的索引
SHOW INDEX FROM wms_dispatch_order;

-- 查看索引使用情况（需要开启 performance_schema）
SELECT 
    object_name AS table_name,
    index_name,
    count_read,
    count_fetch,
    count_insert,
    count_update
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'snest'
  AND object_name IN ('wms_dispatch_order', 'mes_workorder_output', 'mes_workorder_feeding')
ORDER BY count_read DESC;
```

**常见陷阱**：
- 索引不是越多越好，每个索引约增加 5-10% 的写入开销
- `LIKE '%keyword%'` 左模糊查询无法使用索引
- 字段类型不匹配（如 VARCHAR 列用数字查询）会导致索引失效
- `OR` 条件可能导致索引失效，考虑改写为 `UNION ALL`

---

### 6.3 慢查询排查模板

```sql
-- 开启慢查询日志（需要 SUPER 权限，通常在配置文件中设置）
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- 超过 2 秒记录
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 查看当前正在执行的查询（排查锁等待）
SELECT 
    id,
    user,
    host,
    db,
    command,
    time AS running_seconds,
    state,
    LEFT(info, 200) AS query_preview
FROM information_schema.processlist
WHERE command != 'Sleep'
  AND time > 5
ORDER BY time DESC;

-- 查看表大小（判断是否需要分区或归档）
SELECT 
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb,
    table_rows,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS total_mb
FROM information_schema.tables
WHERE table_schema = 'snest'
ORDER BY (data_length + index_length) DESC
LIMIT 20;
```

**关键点注释**：
- `information_schema.processlist` 可以实时查看正在执行的查询
- 大表（如 `wms_asn_order2024` 的分表）查询前确认是否需要加日期过滤
- 表大小超过 1GB 时，考虑是否需要分表或归档历史数据

**常见陷阱**：
- `SHOW PROCESSLIST` 只显示前 100 条，`information_schema.processlist` 显示全部
- `table_rows` 是估算值，`InnoDB` 下可能不准确，用 `SELECT COUNT(*)` 确认

---

## 附录：常用表速查

| 业务域 | 核心表 | 说明 |
|--------|--------|------|
| 生产工单 | `mes_workorder_t` | 工单主表 |
| 工单产出 | `mes_workorder_output` | 成品入库记录 |
| 工单投料 | `mes_workorder_feeding` | 原料投入记录 |
| 生产计划 | `mes_production_plan` | 生产计划表 |
| BOM 配方 | `product_bom` + `product_bom_component_line` | 产品配方主表+行表 |
| 发运单 | `wms_dispatch_order` + `wms_dispatch_order_detail` | 出库发运主表+明细 |
| 采购到货 | `wms_purchase_order` + `wms_asn_order` | 采购订单+到货单 |
| 质检批次 | `qms_batc_material` | 物料质检批次 |
| 物料出入库 | `st_materialbatch_manufacture_in/out` | 生产领料/入库 |
| 物料主数据 | `material_inspect_calculate` | 物料检验计算 |

---

> 💡 **使用建议**：
> 1. 所有模板中的表名和字段名已与通威农发系统实际结构对齐
> 2. VARCHAR 类型的数值字段使用前务必 CAST
> 3. 多租户查询始终带 `tenant_id` 过滤
> 4. 大表查询始终带日期范围过滤，避免全表扫描
> 5. 生产环境的写操作务必在事务中执行，并先在测试环境验证

---

**相关页面**：
- [[制造业术语与业务逻辑知识库]] — SQL模板中的核心术语
- [[通威农发-项目总览]] — SQL模板的实战来源
- [[通威农发/实战踩坑经验]] — SQL相关的踩坑案例
- [[通威农发/项目知识备忘]] — 数据表结构和业务逻辑

---
title: 通威农发-常见SQL优化
aliases: [SQL优化, 查询优化, 性能优化]
tags: [sql, 性能优化, 通威农发]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 通威农发
difficulty: advanced
project: 通威农发
---
# 通威农发-常见SQL优化

## 概述

本文档整理了通威农发项目中常见的SQL优化技巧和最佳实践。

## 1. 查询优化

### 慢查询识别

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- 查看慢查询
SELECT 
    query_time,
    lock_time,
    rows_sent,
    rows_examined,
    sql_text
FROM mysql.slow_log
ORDER BY query_time DESC
LIMIT 10;
```

### EXPLAIN分析

```sql
-- 分析查询计划
EXPLAIN SELECT 
    o.order_id,
    o.order_status,
    p.product_name
FROM mes_work_order o
JOIN mes_product p ON o.product_id = p.product_id
WHERE o.order_status = 'IN_PROGRESS'
    AND o.create_time >= '2026-06-01';

-- 关注指标
-- type: ALL(全表扫描) → index → range → ref → eq_ref → const
-- rows: 扫描行数
-- Extra: Using index(覆盖索引)、Using filesort(文件排序)
```

## 2. 常见优化场景

### 场景1：分页查询优化

```sql
-- ❌ 低效：OFFSET大时性能差
SELECT * FROM table_name 
WHERE validflag = '1'
ORDER BY create_time DESC
LIMIT 100000, 20;

-- ✅ 高效：使用游标分页
SELECT * FROM table_name 
WHERE validflag = '1'
    AND create_time < '2026-06-01 10:00:00'  -- 上一页最后一条的时间
ORDER BY create_time DESC
LIMIT 20;

-- ✅ 高效：使用延迟关联
SELECT t.* FROM table_name t
INNER JOIN (
    SELECT id FROM table_name 
    WHERE validflag = '1'
    ORDER BY create_time DESC
    LIMIT 100000, 20
) tmp ON t.id = tmp.id;
```

### 场景2：JOIN优化

```sql
-- ❌ 低效：多表JOIN
SELECT 
    o.order_id,
    p.product_name,
    l.line_name,
    e.equipment_name
FROM mes_work_order o
JOIN mes_product p ON o.product_id = p.product_id
JOIN mes_production_line l ON o.line_id = l.line_id
JOIN mes_equipment e ON l.equipment_id = e.equipment_id
WHERE o.order_status = 'IN_PROGRESS';

-- ✅ 高效：减少JOIN表数量
-- 方案1：使用冗余字段
SELECT 
    order_id,
    product_name,  -- 冗余字段
    line_name      -- 冗余字段
FROM mes_work_order
WHERE order_status = 'IN_PROGRESS';

-- 方案2：分步查询
-- 第一步：查询工单
SELECT order_id, product_id, line_id 
FROM mes_work_order 
WHERE order_status = 'IN_PROGRESS';

-- 第二步：根据ID批量查询产品和产线
SELECT product_id, product_name FROM mes_product WHERE product_id IN (...);
SELECT line_id, line_name FROM mes_production_line WHERE line_id IN (...);
```

### 场景3：聚合查询优化

```sql
-- ❌ 低效：全表聚合
SELECT 
    DATE(create_time) as date,
    COUNT(*) as count
FROM mes_work_order
WHERE validflag = '1'
GROUP BY DATE(create_time);

-- ✅ 高效：使用索引
-- 创建索引
CREATE INDEX idx_create_time ON mes_work_order(create_time);

-- 查询时避免函数
SELECT 
    DATE(create_time) as date,
    COUNT(*) as count
FROM mes_work_order
WHERE validflag = '1'
    AND create_time >= '2026-06-01'
    AND create_time < '2026-07-01'
GROUP BY DATE(create_time);

-- ✅ 更高效：预聚合
-- 创建汇总表
CREATE TABLE mes_daily_summary (
    summary_date DATE NOT NULL,
    order_count INT NOT NULL,
    total_qty DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (summary_date)
);

-- 定时任务每日汇总
INSERT INTO mes_daily_summary
SELECT 
    DATE(create_time),
    COUNT(*),
    SUM(actual_qty)
FROM mes_work_order
WHERE validflag = '1'
    AND DATE(create_time) = CURDATE() - INTERVAL 1 DAY
GROUP BY DATE(create_time);
```

## 3. 索引优化

### 覆盖索引

```sql
-- 创建覆盖索引
CREATE INDEX idx_covering ON mes_work_order(
    order_status, 
    create_time, 
    product_id, 
    planned_qty
);

-- 查询只访问索引
SELECT 
    order_status,
    create_time,
    product_id,
    planned_qty
FROM mes_work_order
WHERE order_status = 'IN_PROGRESS'
    AND create_time >= '2026-06-01';
```

### 索引合并

```sql
-- 单列索引合并
CREATE INDEX idx_status ON mes_work_order(order_status);
CREATE INDEX idx_time ON mes_work_order(create_time);

-- 查询可能使用索引合并
SELECT * FROM mes_work_order
WHERE order_status = 'IN_PROGRESS'
    AND create_time >= '2026-06-01';
```

## 4. 表结构优化

### 字段优化

```sql
-- 1. 使用合适的字段类型
-- ❌ 错误：使用VARCHAR存储布尔值
is_deleted VARCHAR(10)
-- ✅ 正确：使用CHAR(1)
is_deleted CHAR(1)

-- 2. 避免NULL
-- ❌ 错误：允许NULL
remark VARCHAR(500) NULL
-- ✅ 正确：使用默认值
remark VARCHAR(500) NOT NULL DEFAULT ''

-- 3. 使用ENUM代替VARCHAR
-- ❌ 错误：使用VARCHAR
order_status VARCHAR(20)
-- ✅ 正确：使用ENUM
order_status ENUM('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
```

### 表拆分

```sql
-- 垂直拆分：将大字段拆分到扩展表
-- 主表
CREATE TABLE mes_work_order (
    order_id VARCHAR(32) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    -- 核心字段
    PRIMARY KEY (order_id)
);

-- 扩展表
CREATE TABLE mes_work_order_ext (
    order_id VARCHAR(32) NOT NULL,
    remark TEXT,
    attachment_url VARCHAR(500),
    -- 大字段
    PRIMARY KEY (order_id)
);
```

## 5. 监控与调优

### 性能监控

```sql
-- 查看表大小
SELECT 
    table_name,
    table_rows,
    data_length,
    index_length,
    ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb
FROM information_schema.tables
WHERE table_schema = 'snest'
ORDER BY data_length DESC
LIMIT 20;

-- 查看索引使用情况
SELECT 
    object_schema,
    object_name,
    index_name,
    count_read,
    count_write
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'snest'
ORDER BY count_read DESC;
```

### 定期维护

```sql
-- 1. 优化表
OPTIMIZE TABLE mes_work_order;

-- 2. 分析表
ANALYZE TABLE mes_work_order;

-- 3. 检查表
CHECK TABLE mes_work_order;

-- 4. 重建索引
ALTER TABLE mes_work_order DROP INDEX idx_name, ADD INDEX idx_name (field);
```

## 相关页面

- [[通威农发-数据库设计规范]]
- [[通威农发-数据库总览]]
- [[生产执行查询模板]]
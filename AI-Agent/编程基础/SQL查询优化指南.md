---
title: SQL查询优化指南
aliases: [SQL优化, 查询优化, 数据库优化]
tags: [sql, 优化, 数据库]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 数据库
---
# SQL 查询优化指南

## 概述

本指南提供SQL查询优化的方法和最佳实践。

## 1. 查询分析

### EXPLAIN分析

```sql
-- 查看执行计划
EXPLAIN SELECT * FROM orders WHERE customer_id = 100;

-- 详细执行计划
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 100;
```

### 执行计划解读

```
+----+-------------+-------+------------+------+---------------+---------+---------+-------+------+----------+-------+
| id | select_type | table | partitions | type | possible_keys | key     | key_len | ref   | rows | filtered | Extra |
+----+-------------+-------+------------+------+---------------+---------+---------+-------+------+----------+-------+
|  1 | SIMPLE      | orders | NULL       | ref  | idx_customer  | idx_customer | 4 | const |   10 |   100.00 | NULL  |
+----+-------------+-------+------------+------+---------------+---------+---------+-------+------+----------+-------+
```

**关键字段**：
- **type**：访问类型（ALL → index → range → ref → eq_ref → const）
- **key**：使用的索引
- **rows**：扫描行数
- **Extra**：额外信息

## 2. 索引优化

### 索引设计原则

```sql
-- 1. 选择性高的字段优先
CREATE INDEX idx_email ON users(email);

-- 2. 组合索引遵循最左前缀
CREATE INDEX idx_status_time ON orders(status, created_at);

-- 3. 覆盖索引
CREATE INDEX idx_covering ON orders(customer_id, status, total);
```

### 索引失效场景

```sql
-- 1. 使用函数
-- ❌ 错误
SELECT * FROM orders WHERE YEAR(created_at) = 2026;
-- ✅ 正确
SELECT * FROM orders WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';

-- 2. 隐式类型转换
-- ❌ 错误（customer_id是INT，传入字符串）
SELECT * FROM orders WHERE customer_id = '100';
-- ✅ 正确
SELECT * FROM orders WHERE customer_id = 100;

-- 3. 使用OR
-- ❌ 错误
SELECT * FROM orders WHERE status = 'pending' OR total > 1000;
-- ✅ 正确（使用UNION）
SELECT * FROM orders WHERE status = 'pending'
UNION
SELECT * FROM orders WHERE total > 1000;
```

## 3. 查询优化

### 避免SELECT *

```sql
-- ❌ 错误
SELECT * FROM orders;

-- ✅ 正确
SELECT order_id, customer_id, status, total FROM orders;
```

### 分页优化

```sql
-- ❌ 低效（OFFSET大时性能差）
SELECT * FROM orders ORDER BY id LIMIT 10 OFFSET 10000;

-- ✅ 高效（使用游标）
SELECT * FROM orders WHERE id > 10000 ORDER BY id LIMIT 10;

-- ✅ 高效（使用延迟关联）
SELECT o.* FROM orders o
INNER JOIN (
    SELECT id FROM orders ORDER BY id LIMIT 10 OFFSET 10000
) t ON o.id = t.id;
```

### JOIN优化

```sql
-- ❌ 低效（多表JOIN）
SELECT o.*, c.name, p.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id;

-- ✅ 高效（减少JOIN）
-- 方案1：使用冗余字段
SELECT order_id, customer_name, product_name, total
FROM orders;

-- 方案2：分步查询
SELECT order_id, customer_id, product_id, total FROM orders;
SELECT id, name FROM customers WHERE id IN (...);
SELECT id, name FROM products WHERE id IN (...);
```

### 子查询优化

```sql
-- ❌ 低效（相关子查询）
SELECT * FROM orders o
WHERE EXISTS (
    SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.quantity > 10
);

-- ✅ 高效（JOIN）
SELECT DISTINCT o.* FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE oi.quantity > 10;
```

## 4. 聚合优化

### GROUP BY优化

```sql
-- ❌ 低效（使用函数）
SELECT DATE(created_at), COUNT(*) FROM orders GROUP BY DATE(created_at);

-- ✅ 高效（使用字段）
SELECT DATE_FORMAT(created_at, '%Y-%m-%d') as date, COUNT(*) 
FROM orders 
GROUP BY date;
```

### 聚合函数优化

```sql
-- ❌ 低效（COUNT(*)）
SELECT COUNT(*) FROM orders;

-- ✅ 高效（使用索引）
SELECT COUNT(1) FROM orders;

-- ✅ 高效（使用近似值）
EXPLAIN SELECT COUNT(*) FROM orders;
```

## 5. 排序优化

### ORDER BY优化

```sql
-- ❌ 低效（文件排序）
SELECT * FROM orders ORDER BY total DESC;

-- ✅ 高效（使用索引）
CREATE INDEX idx_total ON orders(total);
SELECT * FROM orders ORDER BY total DESC;

-- ✅ 高效（覆盖索引）
CREATE INDEX idx_covering ON orders(customer_id, status, total);
SELECT customer_id, status, total FROM orders ORDER BY total DESC;
```

### LIMIT优化

```sql
-- ❌ 低效（全表排序）
SELECT * FROM orders ORDER BY total DESC LIMIT 10;

-- ✅ 高效（使用索引）
SELECT * FROM orders WHERE total IS NOT NULL ORDER BY total DESC LIMIT 10;
```

## 6. 数据类型优化

### 字段类型选择

```sql
-- 1. 使用合适的整数类型
-- ❌ 错误（使用BIGINT存储小数字）
status BIGINT
-- ✅ 正确（使用TINYINT）
status TINYINT

-- 2. 使用VARCHAR代替CHAR
-- ❌ 错误（定长）
name CHAR(100)
-- ✅ 正确（变长）
name VARCHAR(100)

-- 3. 使用DECIMAL代替FLOAT
-- ❌ 错误（精度丢失）
price FLOAT
-- ✅ 正确（精确）
price DECIMAL(10,2)
```

### NULL值处理

```sql
-- ❌ 避免NULL
name VARCHAR(100) NULL

-- ✅ 使用默认值
name VARCHAR(100) NOT NULL DEFAULT ''

-- ✅ 使用NOT NULL
name VARCHAR(100) NOT NULL
```

## 7. 表设计优化

### 规范化

```sql
-- 1NF：字段原子性
-- ❌ 错误
skills VARCHAR(100)  -- "Java,Python,SQL"
-- ✅ 正确
CREATE TABLE user_skills (
    user_id INT,
    skill VARCHAR(50),
    PRIMARY KEY (user_id, skill)
);

-- 2NF：消除部分依赖
-- ❌ 错误
order_items表包含product_name（依赖product_id）
-- ✅ 正确
orders表：order_id, product_id, quantity
products表：product_id, product_name

-- 3NF：消除传递依赖
-- ❌ 错误
employees表包含department_name（依赖department_id）
-- ✅ 正确
employees表：employee_id, department_id
departments表：department_id, department_name
```

### 反规范化

```sql
-- 适当冗余（提高查询性能）
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(100),  -- 冗余字段
    total DECIMAL(10,2),
    created_at TIMESTAMP
);
```

## 8. 分区优化

### 范围分区

```sql
-- 按时间分区
CREATE TABLE orders (
    id INT,
    created_at DATE,
    total DECIMAL(10,2)
) PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027)
);
```

### 列表分区

```sql
-- 按状态分区
CREATE TABLE orders (
    id INT,
    status VARCHAR(20),
    total DECIMAL(10,2)
) PARTITION BY LIST (status) (
    PARTITION p_pending VALUES IN ('pending'),
    PARTITION p_completed VALUES IN ('completed'),
    PARTITION p_cancelled VALUES IN ('cancelled')
);
```

## 9. 查询重写

### 使用EXISTS代替IN

```sql
-- ❌ 低效（IN）
SELECT * FROM customers WHERE id IN (
    SELECT customer_id FROM orders WHERE total > 1000
);

-- ✅ 高效（EXISTS）
SELECT * FROM customers c WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.total > 1000
);
```

### 使用UNION ALL代替UNION

```sql
-- ❌ 低效（去重）
SELECT * FROM orders WHERE status = 'pending'
UNION
SELECT * FROM orders WHERE total > 1000;

-- ✅ 高效（不去重）
SELECT * FROM orders WHERE status = 'pending'
UNION ALL
SELECT * FROM orders WHERE total > 1000;
```

## 10. 性能监控

### 慢查询日志

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- 查看慢查询
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;
```

### 索引使用情况

```sql
-- 查看索引使用情况
SELECT * FROM sys.schema_unused_indexes;
SELECT * FROM sys.schema_redundant_indexes;
```

## 相关页面

- [[MySQL数据库运维指南]]
- [[通威农发-常见SQL优化]]
- [[数据质量工具箱]]

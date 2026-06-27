---
title: PostgreSQL高级指南
aliases:
  - PostgreSQL进阶
  - PostgreSQL高级特性
  - PG高级教程
tags:
  - 数据库
  - PostgreSQL
  - SQL
  - 后端
type: 技术指南
status: 已完成
created: 2026-06-27
updated: 2026-06-27
source: 官方文档 + 实战经验
difficulty: 高级
project: AI-Agent
---

# PostgreSQL高级指南

## 概述

PostgreSQL是功能强大的开源关系型数据库，支持高级查询、丰富的索引类型、分区表和JSON数据类型等高级特性。

## 1. 高级查询技巧

### 1.1 窗口函数

```sql
-- 基本窗口函数：排名
SELECT 
    department_id,
    employee_name,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as salary_rank,
    DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dense_rank,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as row_num
FROM employees;

-- 累计求和
SELECT 
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) as running_total
FROM orders;

-- 移动平均
SELECT 
    date,
    revenue,
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d
FROM daily_sales;
```

### 1.2 CTE (公用表表达式)

```sql
-- 递归CTE：组织架构层级查询
WITH RECURSIVE org_tree AS (
    -- 锚点：顶级管理者
    SELECT id, name, manager_id, 1 as level, 
           ARRAY[id] as path
    FROM employees 
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 递归部分
    SELECT e.id, e.name, e.manager_id, ot.level + 1,
           ot.path || e.id
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree ORDER BY path;

-- 多CTE链式查询
WITH 
active_users AS (
    SELECT user_id, name, email 
    FROM users 
    WHERE status = 'active'
),
recent_orders AS (
    SELECT user_id, COUNT(*) as order_count, SUM(amount) as total_spent
    FROM orders 
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT 
    au.name,
    au.email,
    COALESCE(ro.order_count, 0) as orders,
    COALESCE(ro.total_spent, 0) as spent
FROM active_users au
LEFT JOIN recent_orders ro ON au.user_id = ro.user_id;
```

### 1.3 高级JOIN技巧

```sql
-- LATERAL JOIN：相关子查询优化
SELECT d.department_name, e.*
FROM departments d
CROSS JOIN LATERAL (
    SELECT employee_name, salary
    FROM employees
    WHERE department_id = d.id
    ORDER BY salary DESC
    LIMIT 3
) e;

-- 自连接：查找连续登录用户
SELECT DISTINCT a.user_id
FROM user_logins a
JOIN user_logins b 
    ON a.user_id = b.user_id 
    AND b.login_date = a.login_date + INTERVAL '1 day'
JOIN user_logins c 
    ON a.user_id = c.user_id 
    AND c.login_date = a.login_date + INTERVAL '2 day';
```

## 2. 索引优化

### 2.1 索引类型

```sql
-- B-tree索引（默认）
CREATE INDEX idx_users_email ON users(email);

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 复合索引
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- 部分索引（条件索引）
CREATE INDEX idx_orders_pending ON orders(created_at) 
WHERE status = 'pending';

-- 覆盖索引（INCLUDE）
CREATE INDEX idx_users_covering ON users(email) 
INCLUDE (name, phone);

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

### 2.2 GIN和GiST索引

```sql
-- GIN索引：用于全文搜索、JSON、数组
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_products_metadata ON products USING GIN(metadata jsonb_path_ops);

-- 全文搜索索引
CREATE INDEX idx_articles_search ON articles 
USING GIN(to_tsvector('chinese', title || ' ' || content));

-- GiST索引：用于地理空间、范围类型
CREATE INDEX idx_locations_geo ON locations USING GiST(geom);

-- SP-GiST索引：用于不平衡数据
CREATE INDEX idx_phones_prefix ON phones USING SP_GiST(phone_number text_ops);
```

### 2.3 索引维护

```sql
-- 查看索引使用情况
SELECT 
    indexrelname as index_name,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 查找未使用的索引
SELECT 
    indexrelname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- 重建索引
REINDEX INDEX idx_users_email;
REINDEX TABLE users;
```

## 3. 分区表

### 3.1 范围分区

```sql
-- 创建分区主表
CREATE TABLE orders (
    id BIGSERIAL,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE orders_2024_q3 PARTITION OF orders
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

CREATE TABLE orders_2024_q4 PARTITION OF orders
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

-- 默认分区
CREATE TABLE orders_default PARTITION OF orders DEFAULT;
```

### 3.2 列表分区

```sql
-- 按地区分区
CREATE TABLE users (
    id SERIAL,
    name VARCHAR(100),
    region VARCHAR(20) NOT NULL,
    PRIMARY KEY (id, region)
) PARTITION BY LIST (region);

CREATE TABLE users_asia PARTITION OF users FOR VALUES IN ('CN', 'JP', 'KR');
CREATE TABLE users_europe PARTITION OF users FOR VALUES IN ('UK', 'DE', 'FR');
CREATE TABLE users_americas PARTITION OF users FOR VALUES IN ('US', 'CA', 'BR');
```

### 3.3 哈希分区

```sql
-- 均匀分布数据
CREATE TABLE sessions (
    id UUID DEFAULT gen_random_uuid(),
    user_id INTEGER,
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY HASH (user_id);

CREATE TABLE sessions_0 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessions_1 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessions_2 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessions_3 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### 3.4 自动分区管理

```sql
-- 使用pg_partman扩展自动管理分区
CREATE EXTENSION pg_partman;

-- 配置自动分区
SELECT partman.create_parent(
    p_parent_table := 'public.orders',
    p_control := 'created_at',
    p_type := 'range',
    p_interval := '1 month',
    p_premake := 3
);
```

## 4. JSON支持

### 4.1 JSONB操作

```sql
-- 创建带JSONB的表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    attributes JSONB
);

-- 插入JSON数据
INSERT INTO products (name, attributes) VALUES
('iPhone', '{"color": "black", "storage": 128, "tags": ["phone", "apple"]}'),
('MacBook', '{"color": "silver", "ram": 16, "tags": ["laptop", "apple"]}');

-- JSON查询
SELECT name, attributes->>'color' as color
FROM products;

SELECT name, attributes->'storage' as storage
FROM products
WHERE attributes ? 'storage';

-- JSON数组查询
SELECT name
FROM products
WHERE attributes->'tags' ? 'apple';

-- JSON路径查询
SELECT name
FROM products
WHERE attributes @> '{"color": "black"}';

-- JSON聚合
SELECT jsonb_build_object(
    'total', COUNT(*),
    'colors', jsonb_agg(DISTINCT attributes->>'color')
) FROM products;
```

### 4.2 JSON索引

```sql
-- GIN索引支持 ?, ?|, ?&, @>, @?, @@ 操作符
CREATE INDEX idx_products_attrs ON products USING GIN(attributes);

-- 特定路径索引
CREATE INDEX idx_products_color ON products ((attributes->>'color'));

-- JSON路径索引
CREATE INDEX idx_products_storage ON products USING BTREE ((attributes->>'storage'));
```

## 5. 最佳实践

### 5.1 查询优化

- 使用 `EXPLAIN ANALYZE` 分析查询计划
- 避免在WHERE子句中使用函数，改用表达式索引
- 使用 `LIMIT` 限制结果集大小
- 合理使用CTE和子查询

### 5.2 索引策略

- 为高频查询创建合适的索引
- 使用部分索引减少索引大小
- 定期检查并删除未使用的索引
- 使用覆盖索引减少回表查询

### 5.3 分区建议

- 大表（>100GB）考虑分区
- 选择合适的分区键（通常是时间或地区）
- 定期清理历史分区数据
- 使用pg_partman自动化分区管理

### 5.4 连接池配置

```sql
-- 使用PgBouncer或pgpool-II
-- 配置示例（pgbouncer.ini）
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

## 6. 常用扩展

```sql
-- 安装常用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID生成
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- 模糊搜索
CREATE EXTENSION IF NOT EXISTS "btree_gist";     -- GiST索引支持
CREATE EXTENSION IF NOT EXISTS "hstore";         -- 键值对存储
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- 查询统计
```

## 相关页面

- [[MongoDB实战指南]] - NoSQL文档数据库
- [[Redis高级应用]] - 缓存和内存数据库
- [[数据库迁移策略]] - 数据库版本控制和迁移
- [[数据库性能调优]] - 性能优化综合指南

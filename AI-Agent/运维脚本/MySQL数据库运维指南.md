---
title: MySQL数据库运维指南
aliases: [MySQL运维, 数据库管理, SQL优化]
tags: [mysql, 数据库, 运维]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# MySQL 数据库运维指南

## 概述

本指南提供MySQL数据库运维的常用命令和最佳实践。

## 1. 连接管理

### 连接数据库

```bash
# 本地连接
mysql -u root -p

# 远程连接
mysql -h host -u root -p

# 指定数据库
mysql -u root -p database_name

# 执行SQL文件
mysql -u root -p database_name < script.sql
```

### 用户管理

```sql
-- 创建用户
CREATE USER 'username'@'host' IDENTIFIED BY 'password';

-- 授权
GRANT ALL PRIVILEGES ON database.* TO 'username'@'host';

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看用户
SELECT user, host FROM mysql.user;

-- 删除用户
DROP USER 'username'@'host';
```

## 2. 数据库操作

### 数据库管理

```sql
-- 查看数据库
SHOW DATABASES;

-- 创建数据库
CREATE DATABASE database_name;

-- 删除数据库
DROP DATABASE database_name;

-- 使用数据库
USE database_name;
```

### 表管理

```sql
-- 查看表
SHOW TABLES;

-- 查看表结构
DESCRIBE table_name;
SHOW CREATE TABLE table_name;

-- 创建表
CREATE TABLE table_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 修改表
ALTER TABLE table_name ADD COLUMN new_column INT;
ALTER TABLE table_name MODIFY COLUMN column_name VARCHAR(200);
ALTER TABLE table_name DROP COLUMN column_name;

-- 删除表
DROP TABLE table_name;
```

## 3. 数据操作

### 查询数据

```sql
-- 基本查询
SELECT * FROM table_name;
SELECT column1, column2 FROM table_name;

-- 条件查询
SELECT * FROM table_name WHERE condition;

-- 排序
SELECT * FROM table_name ORDER BY column_name ASC;
SELECT * FROM table_name ORDER BY column_name DESC;

-- 分页
SELECT * FROM table_name LIMIT 10 OFFSET 20;

-- 聚合查询
SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name;
SELECT column_name, SUM(amount) FROM table_name GROUP BY column_name;
```

### 插入数据

```sql
-- 插入单条数据
INSERT INTO table_name (column1, column2) VALUES ('value1', 'value2');

-- 插入多条数据
INSERT INTO table_name (column1, column2) VALUES 
('value1', 'value2'),
('value3', 'value4');

-- 插入查询结果
INSERT INTO table_name (column1, column2)
SELECT column1, column2 FROM other_table;
```

### 更新数据

```sql
-- 更新数据
UPDATE table_name SET column1 = 'new_value' WHERE condition;

-- 批量更新
UPDATE table_name SET column1 = CASE
    WHEN condition1 THEN 'value1'
    WHEN condition2 THEN 'value2'
    ELSE 'default'
END;
```

### 删除数据

```sql
-- 删除数据
DELETE FROM table_name WHERE condition;

-- 清空表
TRUNCATE TABLE table_name;
```

## 4. 索引管理

### 索引操作

```sql
-- 查看索引
SHOW INDEX FROM table_name;

-- 创建索引
CREATE INDEX index_name ON table_name (column_name);

-- 创建唯一索引
CREATE UNIQUE INDEX index_name ON table_name (column_name);

-- 创建组合索引
CREATE INDEX index_name ON table_name (column1, column2);

-- 删除索引
DROP INDEX index_name ON table_name;
```

### 索引优化

```sql
-- 分析查询
EXPLAIN SELECT * FROM table_name WHERE condition;

-- 查看索引使用情况
SELECT * FROM sys.schema_unused_indexes;
SELECT * FROM sys.schema_redundant_indexes;
```

## 5. 性能优化

### 慢查询日志

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query%';
```

### 查询优化

```sql
-- 使用EXPLAIN分析
EXPLAIN SELECT * FROM table_name WHERE condition;

-- 优化建议
-- 1. 避免SELECT *
-- 2. 使用索引字段过滤
-- 3. 避免在WHERE中使用函数
-- 4. 使用LIMIT限制结果集
```

### 表优化

```sql
-- 优化表
OPTIMIZE TABLE table_name;

-- 分析表
ANALYZE TABLE table_name;

-- 检查表
CHECK TABLE table_name;
```

## 6. 备份恢复

### 数据备份

```bash
# 备份单个数据库
mysqldump -u root -p database_name > backup.sql

# 备份多个数据库
mysqldump -u root -p --databases db1 db2 > backup.sql

# 备份所有数据库
mysqldump -u root -p --all-databases > backup.sql

# 备份表
mysqldump -u root -p database_name table_name > backup.sql
```

### 数据恢复

```bash
# 恢复数据库
mysql -u root -p database_name < backup.sql

# 恢复所有数据库
mysql -u root -p < backup.sql
```

## 7. 监控诊断

### 状态监控

```sql
-- 查看状态
SHOW STATUS;

-- 查看进程
SHOW PROCESSLIST;

-- 查看变量
SHOW VARIABLES;

-- 查看innodb状态
SHOW ENGINE INNODB STATUS;
```

### 性能诊断

```sql
-- 查看QPS
SHOW GLOBAL STATUS LIKE 'Questions';

-- 查看TPS
SHOW GLOBAL STATUS LIKE 'Com_commit';

-- 查看连接数
SHOW GLOBAL STATUS LIKE 'Threads_connected';

-- 查看缓冲池命中率
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';
```

## 8. 安全配置

### 安全建议

```sql
-- 修改root密码
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';

-- 删除匿名用户
DELETE FROM mysql.user WHERE User='';

-- 禁止远程root登录
DELETE FROM mysql.user WHERE User='root' AND Host!='localhost';

-- 刷新权限
FLUSH PRIVILEGES;
```

### 备份策略

```
每日全量备份
每小时增量备份
实时binlog备份
```

## 相关页面

- [[通威农发-数据库设计规范]]
- [[通威农发-常见SQL优化]]
- [[SQL查询模板]]

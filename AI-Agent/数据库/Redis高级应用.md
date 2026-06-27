---
title: Redis高级应用
aliases:
  - Redis进阶教程
  - Redis高级特性
  - Redis实战指南
tags:
  - 数据库
  - Redis
  - 缓存
  - 内存数据库
type: 技术指南
status: 已完成
created: 2026-06-27
updated: 2026-06-27
source: 官方文档 + 实战经验
difficulty: 中高级
project: AI-Agent
---

# Redis高级应用

## 概述

Redis是高性能的内存数据结构存储，支持多种数据类型、Lua脚本、集群模式和多种持久化策略。

## 1. 高级数据结构

### 1.1 String类型高级用法

```bash
# 基本操作
SET user:1:name "John Doe"
GET user:1:name

# 设置过期时间
SET session:abc123 "user_data" EX 3600  # 1小时后过期

# 条件设置（原子操作）
SET lock:resource1 "holder1" NX EX 30   # 仅当不存在时设置，30秒过期
SET counter:visits 0 NX                  # 初始化计数器

# 原子递增/递减
INCR counter:visits
INCRBY counter:visits 10
DECR counter:visits

# 批量操作
MSET key1 "value1" key2 "value2" key3 "value3"
MGET key1 key2 key3

# 字符串操作
SET mykey "Hello World"
APPEND mykey " Redis"        # "Hello World Redis"
STRLEN mykey                 # 16
GETRANGE mykey 0 4           # "Hello"
SETRANGE mykey 6 "Redis"     # "Hello Redis"
```

### 1.2 Hash类型（对象存储）

```bash
# 存储用户对象
HSET user:1001 name "John Doe" email "john@example.com" age 30

# 获取单个字段
HGET user:1001 name

# 获取多个字段
HMGET user:1001 name email

# 获取所有字段
HGETALL user:1001

# 原子递增
HINCRBY user:1001 age 1

# 字段存在检查
HEXISTS user:1001 phone

# 删除字段
HDEL user:1001 age

# 获取所有键/值
HKEYS user:1001
HVALS user:1001
HLEN user:1001
```

### 1.3 List类型（消息队列）

```bash
# 左右推入
LPUSH queue:tasks "task1" "task2" "task3"
RPUSH queue:tasks "task4"

# 左右弹出
LPOP queue:tasks
RPOP queue:tasks

# 阻塞弹出（消息队列常用）
BLPOP queue:tasks 30          # 阻塞30秒等待新元素
BRPOP queue:tasks 30

# 列表操作
LLEN queue:tasks               # 列表长度
LRANGE queue:tasks 0 -1        # 获取所有元素
LRANGE queue:tasks 0 9         # 获取前10个元素

# 队列模式：生产者-消费者
# 生产者
LPUSH queue:orders '{"orderId": 123, "amount": 99.99}'

# 消费者
BRPOP queue:orders 0           # 无限阻塞等待

# 固定长度列表
LPUSH recent:searches "keyword1"
LTRIM recent:searches 0 99     # 只保留最近100个搜索
```

### 1.4 Set类型（集合操作）

```bash
# 添加成员
SADD user:1001:tags "python" "redis" "database"
SADD user:1002:tags "python" "javascript" "react"

# 集合运算
SINTER user:1001:tags user:1002:tags    # 交集：共同标签
SUNION user:1001:tags user:1002:tags    # 并集：所有标签
SDIFF user:1001:tags user:1002:tags     # 差集：仅user:1001的标签

# 随机成员
SRANDMEMBER user:1001:tags 2            # 随机获取2个标签
SPOP user:1001:tags                      # 随机移除并返回1个

# 成员检查
SISMEMBER user:1001:tags "python"       # 1
SCARD user:1001:tags                     # 集合大小

# 应用：共同好友
SADD user:1001:friends 1002 1003 1004 1005
SADD user:1002:friends 1001 1003 1006
SINTER user:1001:friends user:1002:friends  # 共同好友
```

### 1.5 Sorted Set类型（排行榜）

```bash
# 添加带分数的成员
ZADD leaderboard 100 "player1"
ZADD leaderboard 85 "player2"
ZADD leaderboard 92 "player3"

# 获取排名（从高到低）
ZREVRANGE leaderboard 0 9 WITHSCORES    # 前10名

# 获取分数
ZSCORE leaderboard "player1"

# 增加分数
ZINCRBY leaderboard 5 "player1"

# 范围查询
ZRANGEBYSCORE leaderboard 80 100 WITHSCORES   # 80-100分的玩家

# 获取排名
ZREVRANK leaderboard "player1"          # 排名（从0开始）
ZCARD leaderboard                        # 总成员数

# 应用：延迟队列
ZADD delay:queue 1624000000 '{"task": "send_email", "data": {...}}'
# 获取到期任务
ZRANGEBYSCORE delay:queue 0 <current_timestamp> LIMIT 0 10
```

### 1.6 Stream类型（消息流）

```bash
# 添加消息
XADD mystream * name "John" action "login" timestamp "2024-01-15T10:30:00"
XADD mystream * name "Jane" action "purchase" amount "99.99"

# 读取消息
XREAD COUNT 10 STREAMS mystream 0           # 从头读取10条
XREAD BLOCK 5000 STREAMS mystream $         # 阻塞等待新消息

# 消费者组
XGROUP CREATE mystream mygroup $ MKSTREAM

# 消费者读取
XREADGROUP GROUP mygroup consumer1 COUNT 1 BLOCK 5000 STREAMS mystream >

# 确认消息
XACK mystream mygroup 1526569495631-0

# 查看流信息
XINFO STREAM mystream
XLEN mystream
XRANGE mystream - +                         # 获取所有消息
```

## 2. Lua脚本

### 2.1 基础Lua脚本

```bash
# 简单脚本：原子递增并检查阈值
EVAL "
    local current = redis.call('INCR', KEYS[1])
    if current > tonumber(ARGV[1]) then
        redis.call('DEL', KEYS[1])
        return 0
    end
    return current
" 1 rate:limit:user1001 100

# 脚本缓存（提高性能）
SCRIPT LOAD "
    local current = redis.call('INCR', KEYS[1])
    if current == 1 then
        redis.call('EXPIRE', KEYS[1], ARGV[2])
    end
    if current > tonumber(ARGV[1]) then
        return 0
    end
    return 1
"
# 返回脚本SHA，后续使用EVALSHA调用
```

### 2.2 限流器实现

```bash
# 滑动窗口限流器
EVAL "
    local key = KEYS[1]
    local window = tonumber(ARGV[1])     -- 窗口大小（秒）
    local limit = tonumber(ARGV[2])      -- 限制次数
    local now = tonumber(ARGV[3])        -- 当前时间戳
    
    -- 移除窗口外的请求
    redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
    
    -- 获取当前窗口内的请求数
    local current = redis.call('ZCARD', key)
    
    if current < limit then
        -- 添加当前请求
        redis.call('ZADD', key, now, now .. ':' .. math.random())
        redis.call('EXPIRE', key, window)
        return 1  -- 允许
    end
    
    return 0  -- 拒绝
" 1 rate:api:user1001 60 100 1624000000
```

### 2.3 分布式锁

```bash
# 加锁脚本
EVAL "
    local key = KEYS[1]
    local value = ARGV[1]
    local ttl = tonumber(ARGV[2])
    
    if redis.call('SET', key, value, 'NX', 'PX', ttl) then
        return 1
    end
    return 0
" 1 lock:resource1 "unique_holder_id" 30000

# 解锁脚本（仅释放自己的锁）
EVAL "
    local key = KEYS[1]
    local value = ARGV[1]
    
    if redis.call('GET', key) == value then
        return redis.call('DEL', key)
    end
    return 0
" 1 lock:resource1 "unique_holder_id"

# 可重入锁
EVAL "
    local key = KEYS[1]
    local field = ARGV[1]
    local ttl = tonumber(ARGV[2])
    
    if redis.call('EXISTS', key) == 0 then
        redis.call('HSET', key, field, 1)
        redis.call('PEXPIRE', key, ttl)
        return 1
    end
    
    if redis.call('HGET', key, field) then
        redis.call('HINCRBY', key, field, 1)
        redis.call('PEXPIRE', key, ttl)
        return 1
    end
    
    return 0
" 1 lock:resource "thread_1" 30000
```

## 3. 集群模式

### 3.1 Redis Cluster配置

```bash
# 创建集群（6个节点：3主3从）
redis-cli --cluster create \
  127.0.0.1:7001 \
  127.0.0.1:7002 \
  127.0.0.1:7003 \
  127.0.0.1:7004 \
  127.0.0.1:7005 \
  127.0.0.1:7006 \
  --cluster-replicas 1

# 查看集群信息
redis-cli -c -p 7001 CLUSTER INFO
redis-cli -c -p 7001 CLUSTER NODES

# 添加节点
redis-cli --cluster add-node 127.0.0.1:7007 127.0.0.1:7001

# 删除节点
redis-cli --cluster del-node 127.0.0.1:7001 <node-id>

# 重新分片
redis-cli --cluster reshard 127.0.0.1:7001
```

### 3.2 集群操作

```bash
# 连接集群
redis-cli -c -p 7001

# 集群会自动路由到正确的节点
SET user:1001 "John"      # 可能路由到7002
GET user:1001              # 自动路由到7002

# Hash Tag（确保相关键在同一分片）
SET {user:1001}:name "John"
SET {user:1001}:email "john@example.com"
# {user:1001} 确保这两个键在同一分片

# 集群故障转移
redis-cli -c -p 7004 CLUSTER FAILOVER

# 集群维护
redis-cli --cluster check 127.0.0.1:7001
redis-cli --cluster fix 127.0.0.1:7001
```

### 3.3 集群注意事项

```bash
# 不支持的操作（跨分片）
# MULTI/EXEC 事务（仅支持同一分片内的键）
# 多键操作（除非使用Hash Tag）

# 使用Hash Tag确保数据局部性
SET {order:123}:items "..."
SET {order:123}:status "pending"
SET {order:123}:amount "99.99"

# 批量操作优化
# 使用Pipeline而非MGET/MSET
PIPELINE_START
GET {user:1001}:name
GET {user:1001}:email
GET {user:1001}:age
PIPELINE_END
```

## 4. 持久化策略

### 4.1 RDB快照

```bash
# redis.conf配置
save 900 1         # 900秒内至少1个key变化则保存
save 300 10        # 300秒内至少10个key变化则保存
save 60 10000      # 60秒内至少10000个key变化则保存

dbfilename dump.rdb
dir /var/lib/redis
rdbcompression yes
rdbchecksum yes

# 手动触发保存
SAVE          # 同步保存（阻塞）
BGSAVE        # 后台保存（非阻塞）

# 查看最后保存时间
LASTSAVE
```

### 4.2 AOF日志

```bash
# redis.conf配置
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec          # 每秒同步（推荐）
# appendfsync always         # 每次写入同步（最安全，最慢）
# appendfsync no             # 由操作系统决定

# AOF重写
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 手动触发重写
BGREWRITEAOF

# AOF文件修复
redis-check-aof --fix appendonly.aof
```

### 4.3 混合持久化

```bash
# Redis 4.0+ 支持混合持久化
aof-use-rdb-preamble yes

# 混合持久化结合了RDB和AOF的优点：
# - AOF重写时，前半部分是RDB格式（快速加载）
# - 后半部分是AOF格式（数据完整性）
```

### 4.4 持久化最佳实践

```bash
# 生产环境推荐配置
# redis.conf

# RDB配置
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes

# AOF配置
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 内存管理
maxmemory 4gb
maxmemory-policy allkeys-lru

# 备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
redis-cli BGSAVE
sleep 5
cp /var/lib/redis/dump.rdb /backup/redis/dump_${DATE}.rdb
find /backup/redis -name "*.rdb" -mtime +7 -delete
```

## 5. 性能优化

### 5.1 内存优化

```bash
# 内存使用分析
redis-cli INFO memory
redis-cli MEMORY USAGE key_name
redis-cli MEMORY DOCTOR

# 内存优化策略
# 1. 使用Hash代替多个String
# 2. 使用ziplist编码优化小数据结构
hash-max-ziplist-entries 128
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# 3. 压缩列表优化
# 4. 使用对象池
```

### 5.2 连接池配置

```python
# Python示例（redis-py）
import redis

# 创建连接池
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)

# 使用连接池
r = redis.Redis(connection_pool=pool)

# Pipeline批量操作
with r.pipeline(transaction=True) as pipe:
    pipe.set('key1', 'value1')
    pipe.set('key2', 'value2')
    pipe.get('key1')
    results = pipe.execute()
```

### 5.3 监控和诊断

```bash
# 实时监控
redis-cli MONITOR              # 监控所有命令（调试用，生产慎用）

# 慢查询日志
CONFIG SET slowlog-log-slower-than 10000  # 10ms
CONFIG SET slowlog-max-len 128
SLOWLOG GET 10
SLOWLOG LEN
SLOWLOG RESET

# 客户端信息
CLIENT LIST
CLIENT GETNAME
CLIENT SETNAME my-app

# 统计信息
INFO stats
INFO clients
INFO memory
INFO replication
```

## 6. 最佳实践

### 6.1 键设计规范

```bash
# 使用冒号分隔的命名空间
user:1001:name
user:1001:email
order:123:items
order:123:status

# 使用Hash Tag确保相关键在同一分片
{user:1001}:name
{user:1001}:email

# 设置合理的过期时间
SET session:abc123 "data" EX 3600
EXPIRE temp:data 300
```

### 6.2 常见陷阱

```bash
# 避免大Key
# 错误：存储大JSON
SET big:key "huge_json_string"  # 可能导致阻塞

# 正确：拆分存储
HSET user:1001 name "John"
HSET user:1001 email "john@example.com"

# 避免热Key
# 使用本地缓存减少Redis访问
# 使用读写分离

# 避免大量Key同时过期
# 添加随机过期时间
EXPIRE key (3600 + random(0, 300))
```

## 相关页面

- [[PostgreSQL高级指南]] - 关系型数据库
- [[MongoDB实战指南]] - 文档数据库
- [[数据库迁移策略]] - 数据库版本控制和迁移
- [[数据库性能调优]] - 性能优化综合指南

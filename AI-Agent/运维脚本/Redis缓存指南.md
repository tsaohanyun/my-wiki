---
title: Redis缓存指南
aliases: [Redis教程, 缓存配置, Redis命令]
tags: [redis, 缓存, 数据库]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# Redis 缓存指南

## 概述

本指南提供Redis缓存的配置方法和最佳实践。

## 1. 基础操作

### 连接Redis

```bash
# 本地连接
redis-cli

# 远程连接
redis-cli -h host -p port -a password

# 选择数据库
SELECT 0
```

### 字符串操作

```bash
# 设置键值
SET key value
SET key value EX 3600  # 设置过期时间（秒）

# 获取值
GET key

# 删除键
DEL key

# 检查键是否存在
EXISTS key

# 设置过期时间
EXPIRE key 3600

# 查看剩余时间
TTL key
```

### 哈希操作

```bash
# 设置哈希
HSET hash field value
HSET hash field1 value1 field2 value2

# 获取哈希字段
HGET hash field
HGETALL hash

# 删除哈希字段
HDEL hash field

# 检查字段是否存在
HEXISTS hash field
```

### 列表操作

```bash
# 左推入
LPUSH list value1 value2

# 右推入
RPUSH list value1 value2

# 获取列表
LRANGE list 0 -1

# 弹出元素
LPOP list
RPOP list

# 列表长度
LLEN list
```

### 集合操作

```bash
# 添加元素
SADD set member1 member2

# 获取集合
SMEMBERS set

# 删除元素
SREM set member

# 集合运算
SUNION set1 set2
SINTER set1 set2
SDIFF set1 set2
```

## 2. 配置优化

### 内存配置

```bash
# redis.conf

# 最大内存
maxmemory 256mb

# 内存淘汰策略
maxmemory-policy allkeys-lru

# 淘汰策略选项
# volatile-lru: 从已设置过期时间的数据集中挑选最近最少使用的数据淘汰
# allkeys-lru: 从数据集中挑选最近最少使用的数据淘汰
# volatile-random: 从已设置过期时间的数据集中任意选择数据淘汰
# allkeys-random: 从数据集中任意选择数据淘汰
# volatile-ttl: 从已设置过期时间的数据集中挑选将要过期的数据淘汰
# noeviction: 禁止驱逐数据
```

### 持久化配置

```bash
# RDB持久化
save 900 1
save 300 10
save 60 10000

dbfilename dump.rdb
dir /var/lib/redis

# AOF持久化
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
```

### 性能配置

```bash
# 最大连接数
maxclients 10000

# 超时时间
timeout 300

# TCP keepalive
tcp-keepalive 300
```

## 3. 缓存策略

### 缓存模式

```python
# Cache-Aside模式
def get_user(user_id):
    # 先查缓存
    cache_key = f"user:{user_id}"
    user = redis.get(cache_key)
    
    if user:
        return json.loads(user)
    
    # 缓存未命中，查数据库
    user = db.get_user(user_id)
    
    # 写入缓存
    redis.setex(cache_key, 3600, json.dumps(user))
    
    return user
```

### 缓存更新

```python
# 更新时删除缓存
def update_user(user_id, data):
    # 更新数据库
    db.update_user(user_id, data)
    
    # 删除缓存
    cache_key = f"user:{user_id}"
    redis.delete(cache_key)
```

### 缓存穿透

```python
# 布隆过滤器
def get_user(user_id):
    # 布隆过滤器判断
    if not bloom_filter.exists(user_id):
        return None
    
    # 查缓存
    cache_key = f"user:{user_id}"
    user = redis.get(cache_key)
    
    if user:
        return json.loads(user)
    
    # 查数据库
    user = db.get_user(user_id)
    
    # 写入缓存（设置空值）
    if user is None:
        redis.setex(cache_key, 300, "null")
    else:
        redis.setex(cache_key, 3600, json.dumps(user))
    
    return user
```

### 缓存击穿

```python
# 互斥锁
def get_user(user_id):
    cache_key = f"user:{user_id}"
    user = redis.get(cache_key)
    
    if user:
        return json.loads(user)
    
    # 获取锁
    lock_key = f"lock:user:{user_id}"
    if redis.set(lock_key, 1, nx=True, ex=10):
        try:
            # 查数据库
            user = db.get_user(user_id)
            redis.setex(cache_key, 3600, json.dumps(user))
            return user
        finally:
            redis.delete(lock_key)
    else:
        # 等待其他进程加载
        time.sleep(0.1)
        return get_user(user_id)
```

## 4. 分布式锁

### 实现分布式锁

```python
import redis
import time

class RedisLock:
    def __init__(self, redis_client, key, timeout=10):
        self.redis = redis_client
        self.key = f"lock:{key}"
        self.timeout = timeout
    
    def acquire(self):
        """获取锁"""
        return self.redis.set(self.key, 1, nx=True, ex=self.timeout)
    
    def release(self):
        """释放锁"""
        self.redis.delete(self.key)
    
    def __enter__(self):
        if not self.acquire():
            raise Exception("获取锁失败")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

# 使用
with RedisLock(redis_client, "my_lock"):
    # 执行需要加锁的操作
    pass
```

## 5. 消息队列

### 发布订阅

```python
# 发布者
import redis

r = redis.Redis()
r.publish('channel', 'message')

# 订阅者
import redis

r = redis.Redis()
pubsub = r.pubsub()
pubsub.subscribe('channel')

for message in pubsub.listen():
    print(message)
```

### 延迟队列

```python
import redis
import time

r = redis.Redis()

def add_to_delay_queue(queue, task, delay):
    """添加到延迟队列"""
    execute_at = time.time() + delay
    r.zadd(queue, {task: execute_at})

def process_delay_queue(queue):
    """处理延迟队列"""
    while True:
        tasks = r.zrangebyscore(queue, 0, time.time(), start=0, num=1)
        if tasks:
            task = tasks[0]
            if r.zrem(queue, task):
                # 处理任务
                process_task(task)
        time.sleep(0.1)
```

## 6. 监控诊断

### 性能监控

```bash
# 查看信息
redis-cli INFO

# 查看内存
redis-cli INFO memory

# 查看连接
redis-cli INFO clients

# 查看统计
redis-cli INFO stats
```

### 慢查询

```bash
# 查看慢查询
redis-cli SLOWLOG GET 10

# 设置慢查询阈值
redis-cli CONFIG SET slowlog-log-slower-than 10000
```

## 7. 集群配置

### 主从复制

```bash
# 从节点配置
replicaof master_ip master_port
masterauth password
```

### 哨兵模式

```bash
# sentinel.conf
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
```

### 集群模式

```bash
# 创建集群
redis-cli --cluster create node1:6379 node2:6379 node3:6379

# 查看集群信息
redis-cli -c CLUSTER INFO
```

## 相关页面

- [[MySQL数据库运维指南]]
- [[Docker容器化指南]]
- [[Python运维脚本库]]

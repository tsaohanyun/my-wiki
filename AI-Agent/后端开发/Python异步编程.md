---
title: Python 异步编程
aliases:
  - Python asyncio
  - Python异步IO
  - aiohttp
  - Python协程
tags:
  - python
  - asyncio
  - async-await
  - aiohttp
  - celery
  - async-orm
  - backend
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: AI-Agent Wiki
difficulty: intermediate
project: AI-Agent
---

# Python 异步编程

## 概述

Python 的 `asyncio` 库提供了基于协程的并发编程模型，非常适合 I/O 密集型任务（HTTP 请求、数据库查询、文件读写）。通过 `async/await` 语法，可以用同步代码的风格编写异步逻辑，避免回调地狱。本页涵盖 asyncio 核心、aiohttp Web 框架、异步 ORM 和异步任务队列。

---

## 1. asyncio 核心概念

### 1.1 协程基础

```python
import asyncio
import time


# 定义协程函数
async def say_hello(name: str, delay: float) -> str:
    await asyncio.sleep(delay)  # 非阻塞等待
    return f"Hello, {name}! (waited {delay}s)"


# 运行协程
async def main():
    # 串行执行：总耗时 = 1 + 2 = 3 秒
    result1 = await say_hello("Alice", 1.0)
    result2 = await say_hello("Bob", 2.0)
    print(result1)
    print(result2)


asyncio.run(main())
```

### 1.2 并发执行

```python
import asyncio
import time


async def fetch_data(source: str, delay: float) -> dict:
    await asyncio.sleep(delay)
    return {"source": source, "data": f"result from {source}"}


async def main():
    start = time.perf_counter()

    # ✅ gather: 并发执行，总耗时 ≈ max(1, 2, 1.5) = 2 秒
    results = await asyncio.gather(
        fetch_data("api1", 1.0),
        fetch_data("api2", 2.0),
        fetch_data("api3", 1.5),
    )

    elapsed = time.perf_counter() - start
    print(f"并发完成，耗时 {elapsed:.2f}s")
    for r in results:
        print(r)


asyncio.run(main())
```

### 1.3 Task 与超时控制

```python
import asyncio


async def slow_operation():
    await asyncio.sleep(10)
    return "完成"


async def main():
    # 创建 Task
    task = asyncio.create_task(slow_operation(), name="slow-task")

    try:
        # 超时控制（Python 3.11+）
        result = await asyncio.wait_for(task, timeout=3.0)
        print(result)
    except asyncio.TimeoutError:
        print("任务超时！取消中...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("任务已取消")


asyncio.run(main())
```

### 1.4 asyncio.wait — 更精细的控制

```python
import asyncio


async def task_with_id(task_id: int, duration: float):
    await asyncio.sleep(duration)
    return f"Task-{task_id} done in {duration}s"


async def main():
    tasks = [
        asyncio.create_task(task_with_id(i, 3.0 - i * 0.5))
        for i in range(5)
    ]

    # FIRST_COMPLETED: 第一个完成时返回
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )
    print(f"第一个完成: {done.pop().result()}")

    # 取消剩余任务
    for t in pending:
        t.cancel()

    # ALL_COMPLETED（默认）: 等待全部完成
    # done, pending = await asyncio.wait(tasks)


asyncio.run(main())
```

### 1.5 异步上下文管理器与迭代器

```python
import asyncio


class AsyncDatabasePool:
    def __init__(self, size: int = 5):
        self.size = size
        self._semaphore = asyncio.Semaphore(size)

    async def __aenter__(self):
        print("初始化连接池...")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("关闭连接池...")
        await asyncio.sleep(0.1)

    async def query(self, sql: str):
        async with self._semaphore:
            print(f"执行查询: {sql}")
            await asyncio.sleep(0.5)  # 模拟查询延迟
            return {"rows": [{"id": 1}], "sql": sql}


async def main():
    async with AsyncDatabasePool(size=3) as pool:
        results = await asyncio.gather(
            pool.query("SELECT * FROM users"),
            pool.query("SELECT * FROM orders"),
            pool.query("SELECT * FROM products"),
            pool.query("SELECT * FROM categories"),
        )
        for r in results:
            print(r)


asyncio.run(main())
```

---

## 2. aiohttp — 异步 HTTP

### 2.1 HTTP 客户端

```python
import asyncio
import aiohttp
import time


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_many(urls: list[str]) -> list[dict]:
    # 连接池配置
    connector = aiohttp.TCPConnector(
        limit=100,           # 总连接数上限
        limit_per_host=10,   # 单 host 连接数上限
        ttl_dns_cache=300,
    )
    timeout = aiohttp.ClientTimeout(total=30, connect=5)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch_json(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 分离成功与失败
        success = []
        failures = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                failures.append((url, str(result)))
            else:
                success.append(result)

        print(f"成功: {len(success)}, 失败: {len(failures)}")
        for url, err in failures:
            print(f"  失败 - {url}: {err}")

        return success


async def main():
    urls = [f"https://jsonplaceholder.typicode.com/posts/{i}" for i in range(1, 21)]
    start = time.perf_counter()
    data = await fetch_many(urls)
    print(f"获取 {len(data)} 条数据，耗时 {time.perf_counter() - start:.2f}s")


asyncio.run(main())
```

### 2.2 HTTP 服务器（Web 框架）

```python
from aiohttp import web
import json


# 中间件
@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        return web.json_response(
            {"error": ex.reason, "status": ex.status},
            status=ex.status,
        )
    except Exception as ex:
        return web.json_response(
            {"error": "Internal Server Error", "detail": str(ex)},
            status=500,
        )


@web.middleware
async def auth_middleware(request, handler):
    # 跳过不需要认证的路由
    if request.path in ["/", "/health", "/login"]:
        return await handler(request)

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return web.json_response({"error": "未授权"}, status=401)

    try:
        # 验证 token（伪代码）
        request["user_id"] = verify_token(token)
        return await handler(request)
    except InvalidTokenError:
        return web.json_response({"error": "Token 无效"}, status=403)


# 路由处理器
async def health_check(request):
    return web.json_response({"status": "healthy", "version": "1.0.0"})


async def get_users(request):
    page = int(request.query.get("page", 1))
    limit = int(request.query.get("limit", 10))
    db = request.app["db"]
    users = await db.fetch(
        "SELECT id, username, email FROM users ORDER BY id LIMIT $1 OFFSET $2",
        limit, (page - 1) * limit
    )
    return web.json_response({"data": [dict(u) for u in users], "page": page})


async def create_user(request):
    data = await request.json()

    # 输入校验
    if not data.get("username") or not data.get("email"):
        return web.json_response(
            {"error": "用户名和邮箱为必填项"}, status=400
        )

    db = request.app["db"]
    # 检查邮箱唯一性
    exists = await db.fetchval(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)", data["email"]
    )
    if exists:
        return web.json_response({"error": "邮箱已被注册"}, status=409)

    user_id = await db.fetchval(
        "INSERT INTO users (username, email) VALUES ($1, $2) RETURNING id",
        data["username"], data["email"]
    )
    return web.json_response({"id": user_id, **data}, status=201)


async def get_user(request):
    user_id = int(request.match_info["id"])
    db = request.app["db"]
    user = await db.fetchrow(
        "SELECT id, username, email FROM users WHERE id = $1", user_id
    )
    if not user:
        return web.json_response({"error": "用户不存在"}, status=404)
    return web.json_response({"data": dict(user)})


# 应用初始化
async def init_app():
    app = web.Application(middlewares=[auth_middleware, error_middleware])

    # 初始化数据库连接池
    app["db"] = await asyncpg.create_pool(
        "postgres://user:pass@localhost/mydb",
        min_size=5, max_size=20,
    )

    # 注册路由
    app.router.add_get("/health", health_check)
    app.router.add_get("/api/users", get_users)
    app.router.add_post("/api/users", create_user)
    app.router.add_get("/api/users/{id}", get_user)

    # 清理
    async def close_db(app):
        await app["db"].close()
    app.on_cleanup.append(close_db)

    return app


if __name__ == "__main__":
    web.run_app(init_app(), host="0.0.0.0", port=8080)
```

---

## 3. 异步 ORM

### 3.1 SQLAlchemy 2.0 异步

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, update, delete
from typing import Optional
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    age: Mapped[Optional[int]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


# 创建异步引擎
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/mydb",
    echo=True,
    pool_size=20,
    max_overflow=10,
)

# 异步 Session 工厂
async_session = async_sessionmaker(engine, expire_on_commit=False)


# CRUD 操作
async def create_user(username: str, email: str, age: int = None) -> User:
    async with async_session() as session:
        user = User(username=username, email=email, age=age)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_user_by_id(user_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


async def get_users_paginated(page: int = 1, limit: int = 10) -> list[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .order_by(User.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        return list(result.scalars().all())


async def update_user_email(user_id: int, new_email: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(email=new_email)
        )
        await session.commit()
        return result.rowcount > 0


async def delete_user(user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            delete(User).where(User.id == user_id)
        )
        await session.commit()
        return result.rowcount > 0


# 建表
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 主函数
async def main():
    await init_db()

    # 创建用户
    user = await create_user("alice", "alice@example.com", 28)
    print(f"创建: {user.username} (ID: {user.id})")

    # 查询
    found = await get_user_by_id(user.id)
    print(f"查询: {found.email}")

    # 分页
    users = await get_users_paginated(page=1, limit=5)
    print(f"列表: {len(users)} 个用户")

    # 更新
    await update_user_email(user.id, "new_alice@example.com")

    # 删除
    await delete_user(user.id)

    await engine.dispose()


import asyncio
asyncio.run(main())
```

### 3.2 Tortoise ORM

```python
from tortoise import Tortoise, fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    posts = fields.ReverseRelation["Post"]
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"


class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField(null=True)
    author = fields.ForeignKeyField("models.User", related_name="posts")
    created_at = fields.DatetimeField(auto_now_add=True)


async def init():
    await Tortoise.init(
        db_url="postgres://user:pass@localhost/mydb",
        modules={"models": ["__main__"]},
    )
    await Tortoise.generate_schemas()


async def demo():
    # 创建
    user = await User.create(username="bob", email="bob@example.com")

    # 关联创建
    await Post.create(title="Hello World", content="My first post", author=user)
    await Post.create(title="Second Post", author=user)

    # 查询（含关联）
    user_with_posts = await User.filter(username="bob").prefetch_related("posts").first()
    print(f"{user_with_posts.username} 有 {len(user_with_posts.posts)} 篇文章")

    await Tortoise.close_connections()


asyncio.run(init())
asyncio.run(demo())
```

---

## 4. 异步任务队列

### 4.1 Celery 异步任务

```python
# tasks.py
from celery import Celery
import time

app = Celery(
    "myapp",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

# 配置
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "tasks.send_email": {"queue": "email"},
        "tasks.process_video": {"queue": "heavy"},
    },
)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(self, to: str, subject: str, body: str):
    """发送邮件任务，支持自动重试"""
    try:
        # 实际发送逻辑
        print(f"发送邮件到 {to}: {subject}")
        time.sleep(2)  # 模拟网络延迟
        return {"status": "sent", "to": to}
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task
def process_video(video_path: str):
    """视频处理任务"""
    print(f"处理视频: {video_path}")
    time.sleep(10)
    return {"status": "processed", "path": video_path}


@app.task
def batch_import(data: list[dict]):
    """批量导入"""
    success = 0
    for item in data:
        try:
            # 导入逻辑
            success += 1
        except Exception:
            pass
    return {"total": len(data), "success": success}
```

```python
# 调用方
from tasks import send_email, process_video, batch_import

# 普通调用（异步）
result = send_email.delay("user@example.com", "欢迎", "你好！")

# 延迟调用
send_email.apply_async(
    args=["user@example.com", "提醒", "别忘了"],
    countdown=3600,  # 1 小时后执行
)

# 获取结果
print(result.ready())  # 是否完成
print(result.result)   # 结果值（需配置 backend）

# 链式任务
from celery import chain
workflow = chain(
    process_video.s("/uploads/video.mp4"),
    send_email.s("admin@example.com", "视频处理完成"),
)
workflow.apply_async()

# 分组
from celery import group
batch = group(
    send_email.s(user["email"], "通知", f"Hi {user['name']}")
    for user in users
)
batch.apply_async()
```

### 4.2 Celery 定时任务

```python
from celery import Celery
from celery.schedules import crontab

app = Celery("myapp", broker="redis://localhost:6379/0")

app.conf.beat_schedule = {
    # 每天凌晨 2 点清理过期数据
    "cleanup-expired-data": {
        "task": "tasks.cleanup_expired",
        "schedule": crontab(hour=2, minute=0),
    },
    # 每 5 分钟同步数据
    "sync-data": {
        "task": "tasks.sync_data",
        "schedule": crontab(minute="*/5"),
    },
    # 每周一上午 9 点生成周报
    "weekly-report": {
        "task": "tasks.generate_report",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
}
```

### 4.3 ARQ — 轻量级异步任务队列

```python
# worker.py — 基于 asyncio 的任务队列
from arq import create_pool
from arq.connections import RedisSettings
import asyncio


async def send_welcome_email(ctx, user_id: int):
    print(f"发送欢迎邮件给用户 {user_id}")
    await asyncio.sleep(1)
    return {"sent": True, "user_id": user_id}


async def process_order(ctx, order_id: int):
    print(f"处理订单 {order_id}")
    await asyncio.sleep(2)
    return {"processed": order_id}


class WorkerSettings:
    functions = [send_welcome_email, process_order]
    redis_settings = RedisSettings(host="localhost", port=6379)
    max_jobs = 10
    job_timeout = 300
    retry_jobs = True
    max_tries = 3


# 客户端调用
async def enqueue():
    redis = await create_pool(RedisSettings())

    # 入队
    await redis.enqueue_job("send_welcome_email", user_id=42)

    # 延迟入队
    await redis.enqueue_job("process_order", order_id=100, _defer_by=60)

asyncio.run(enqueue())
```

---

## 5. 进阶模式

### 5.1 异步信号量（限流）

```python
import asyncio
import aiohttp


class RateLimiter:
    """令牌桶限流器"""
    def __init__(self, rate: int, burst: int = None):
        self.rate = rate          # 每秒允许的请求数
        self.burst = burst or rate
        self._tokens = burst
        self._last_update = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_update
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
            self._last_update = now

            if self._tokens < 1:
                wait_time = (1 - self._tokens) / self.rate
                await asyncio.sleep(wait_time)
                self._tokens = 0
            else:
                self._tokens -= 1


async def fetch_with_limit(urls: list[str], rate: int = 5):
    limiter = RateLimiter(rate=rate)
    sem = asyncio.Semaphore(rate * 2)  # 最大并发数

    async with aiohttp.ClientSession() as session:
        async def fetch(url):
            async with sem:
                await limiter.acquire()
                async with session.get(url) as resp:
                    return await resp.json()

        return await asyncio.gather(*[fetch(url) for url in urls])
```

### 5.2 异步生成器

```python
import asyncio


async def async_paginate(fetch_func, page_size=100):
    """异步分页生成器"""
    page = 1
    while True:
        items = await fetch_func(page, page_size)
        if not items:
            break
        for item in items:
            yield item
        page += 1
        await asyncio.sleep(0.1)  # 礼让事件循环


async def main():
    async def mock_fetch(page, size):
        await asyncio.sleep(0.1)
        if page > 3:
            return []
        return [{"id": page * size + i} for i in range(size)]

    async for item in async_paginate(mock_fetch, page_size=5):
        print(item)


asyncio.run(main())
```

### 5.3 在同步代码中调用异步

```python
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


def run_async_in_thread(coro):
    """在独立线程中运行协程，供同步代码调用"""
    result = None
    error = None

    def runner():
        nonlocal result, error
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(coro)
        except Exception as e:
            error = e
        finally:
            loop.close()

    t = threading.Thread(target=runner)
    t.start()
    t.join()

    if error:
        raise error
    return result


# 或者使用 asgiref.sync（Django / 同步框架中常用）
from asgiref.sync import async_to_sync, sync_to_async

# 同步代码中调用异步函数
result = async_to_sync(async_function)(arg1, arg2)

# 异步代码中调用同步阻塞函数
result = await sync_to_async(blocking_function)(arg1, arg2)
```

---

## 6. 最佳实践

### 6.1 关键原则

- ✅ **永远不要在 async 函数中使用阻塞调用**（`time.sleep`, `requests.get`, 同步文件 I/O）
- ✅ 使用 `aiofiles` 替代同步文件操作
- ✅ 使用 `httpx.AsyncClient` 或 `aiohttp` 替代 `requests`
- ✅ **CPU 密集型任务用 `run_in_executor`** 或多进程
- ✅ **合理设置并发上限**（`Semaphore`），避免打崩下游服务
- ✅ **使用 `asyncio.gather(return_exceptions=True)`** 处理部分失败
- ✅ **数据库连接池**：合理设置 `min_size` 和 `max_size`
- ✅ **使用 `uvloop`** 替代默认事件循环（Linux 下 2-4 倍性能提升）
- ❌ 不要在同一程序中混用多个事件循环
- ❌ 不要 `await` 过多的协程而不限并发（可能耗尽内存）

### 6.2 生产部署

```python
# 使用 uvicorn + FastAPI 示例
# server.py
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="My API", version="1.0.0")

@app.on_event("startup")
async def startup():
    app.state.db = await create_db_pool()

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

# 启动命令（生产）:
# uvicorn server:app --host 0.0.0.0 --port 8000 \
#   --workers 4 --loop uvloop --http httptools
```

```bash
# Gunicorn + Uvicorn workers
gunicorn server:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5
```

### 6.3 调试技巧

```python
import asyncio
import logging

# 开启 asyncio 调试日志
logging.basicConfig(level=logging.DEBUG)
asyncio.get_event_loop().set_debug(True)

# 检测阻塞调用（阻塞超过 100ms 会打印警告）
asyncio.get_event_loop().slow_callback_duration = 0.1

# 使用 aiomonitor 在运行时检查任务
# pip install aiomonitor
import aiomonitor

async def main():
    with aiomonitor.start_monitor(loop=asyncio.get_event_loop()):
        # 应用逻辑
        await my_app()

# 然后通过 telnet localhost 5011 连接查看运行中的任务
```

---

## 7. 相关页面

- [[Java Spring Boot 开发]]
- [[Node.js 后端开发]]
- [[Rust 系统编程]]
- [[gRPC 服务开发]]
- [[FastAPI 框架详解]]
- [[Redis 与缓存策略]]
- [[Celery 任务队列最佳实践]]

---
title: Flink流处理引擎
aliases:
  - Flink
  - Apache Flink
  - 流处理Flink
tags:
  - 数据工程
  - 流处理
  - Flink
  - 实时计算
type: 技术文档
status: 完成
created: 2026-06-28
updated: 2026-06-28
source: 官方文档 + 实践总结
difficulty: 高级
project: AI-Agent
---

# Flink流处理引擎

> Apache Flink 是一个分布式流处理框架，支持高吞吐、低延迟的精确一次语义。与 Spark 的微批处理不同，Flink 是真正的逐条流处理引擎。

## 目录

- [[#核心架构]]
- [[#DataStream API]]
- [[#窗口函数]]
- [[#状态管理]]
- [[#Checkpoint 与容错]]
- [[#Watermark]]
- [[#最佳实践]]
- [[#相关页面]]

---

## 核心架构

| 组件 | 说明 |
|------|------|
| **JobManager** | 协调分布式执行，调度任务，管理 Checkpoint |
| **TaskManager** | 执行具体任务的进程，管理内存、网络和 I/O |
| **Dispatcher** | 提供 REST 接口，提交作业 |
| **ResourceManager** | 管理资源（K8s/YARN/Mesos 上的 slot 分配） |

### 流处理 vs 批处理 vs 微批处理

| 特性 | Flink（流处理） | Spark Streaming（微批） |
|------|-----------------|------------------------|
| 处理模型 | 逐条事件处理 | 微批（RDD 批次） |
| 延迟 | 毫秒级 | 秒级 |
| 语义 | Exact-Once | Exact-Once |
| 状态管理 | 原生强大 | 较弱 |
| 时间语义 | Event Time + Watermark | 有限支持 |

---

## DataStream API

### 初始化与数据源

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction, FilterFunction
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy, RestartStrategies
import json

# 创建执行环境
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)

# 配置 Checkpoint
env.enable_checkpointing(60000)  # 60秒一次
env.get_checkpoint_config().set_min_pause_between_checkpoints(30000)
env.get_checkpoint_config().set_checkpoint_timeout(120000)
env.get_checkpoint_config().set_max_concurrent_checkpoints(1)

# 配置重启策略
env.set_restart_strategy(
    RestartStrategies.fixed_delay_restart(3, 10000)  # 最多重启3次，间隔10秒
)

# ====== 数据源：Kafka ======
kafka_source = KafkaSource.builder() \
    .set_bootstrap_servers("kafka:9092") \
    .set_topics("user_events") \
    .set_group_id("flink_processor") \
    .set_starting_offsets(KafkaSourceOffsets.earliest()) \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

stream = env.from_source(
    kafka_source,
    WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(10)),
    "kafka-source"
)

# ====== 数据源：文件 ======
from pyflink.datastream import FileSource
from pyflink.common import Duration

file_source = FileSource.for_record_stream_format(
    SimpleStringEncoder(),
    "file:///data/stream/"
).monitor_continuously(Duration.of_minutes(1)).build()

file_stream = env.from_source(file_source, WatermarkStrategy.no_watermarks(), "file-source")

# ====== 数据源：Socket（开发调试）======
socket_stream = env.socket_text_stream("localhost", 9999)
```

### Transformation 算子

```python
# map: 一对一转换
mapped = stream.map(lambda x: json.loads(x))

# flatMap: 一对多转换
words = stream.flat_map(lambda line: line.split(" "))

# filter: 过滤
filtered = stream.filter(lambda x: json.loads(x).get("amount", 0) > 100)

# keyBy: 分区（按Key）
keyed = mapped.key_by(lambda event: event["user_id"])

# union: 合并多个流
merged = stream1.union(stream2)

# connect / coMap: 连接不同类型的流
connected = stream1.connect(stream2)
result = connected.map(
    lambda val1: process_type1(val1),   # 处理流1
    lambda val2: process_type2(val2)    # 处理流2
)

# split / select: 分流（按条件路由）
# Python API 中使用 Side Output 实现
from pyflink.datastream import OutputTag

late_events = OutputTag("late-data")
```

### 数据汇（Sink）

```python
# Kafka Sink
kafka_sink = KafkaSink.builder() \
    .set_bootstrap_servers("kafka:9092") \
    .set_record_serializer(
        KafkaRecordSerializationSchema.builder()
        .set_topic("output_topic")
        .set_value_serialization_schema(SimpleStringSchema())
        .build()
    ) \
    .set_delivery_guarantee(KafkaSinkDeliveryGuarantee.EXACTLY_ONCE) \
    .build()

result_stream.sink_to(kafka_sink)

# 文件 Sink（滚动写入）
from pyflink.datastream import FileSink, OutputFileConfig
from pyflink.common import Row

file_sink = FileSink.for_row_format(
    "file:///data/output/",
    SimpleStringEncoder()
).with_rolling_policy(
    RollingPolicies.default_rolling_policy(
        part_size=128 * 1024 * 1024,    # 128MB
        rollover_interval=60 * 1000,     # 60秒
        inactivity_interval=30 * 1000    # 30秒
    )
).with_output_file_config(
    OutputFileConfig.builder()
    .with_part_prefix("events")
    .with_part_suffix(".parquet")
    .build()
).build()

result_stream.sink_to(file_sink)

# 打印（调试）
result_stream.print()

# 执行
env.execute("User Event Processing")
```

---

## 窗口函数

### 窗口类型

```python
from pyflink.datastream.window import (
    TumblingEventTimeWindows,
    SlidingEventTimeWindows,
    SessionEventTimeWindows,
    TimeWindow
)
from pyflink.common import Duration

# ====== 滚动窗口（不重叠）======
# 每5分钟统计一次
tumbling_result = events \
    .key_by(lambda e: e["category"]) \
    .window(TumblingEventTimeWindows.of(Duration.of_minutes(5))) \
    .reduce(lambda a, b: {"category": a["category"], "count": a["count"] + b["count"]})

# ====== 滑动窗口（可重叠）======
# 窗口10分钟，每5分钟滑动一次
sliding_result = events \
    .key_by(lambda e: e["category"]) \
    .window(
        SlidingEventTimeWindows.of(
            Duration.of_minutes(10),  # 窗口大小
            Duration.of_minutes(5)    # 滑动步长
        )
    ) \
    .aggregate(MyAggregateFunction())

# ====== 会话窗口（基于活跃间隔）======
# 30秒不活跃则关闭窗口
session_result = events \
    .key_by(lambda e: e["user_id"]) \
    .window(SessionEventTimeWindows.with_gap(Duration.of_seconds(30))) \
    .process(MyProcessWindowFunction())

# ====== 全局窗口（需要自定义 Trigger）======
# 通常配合 CountTrigger 或自定义 Trigger 使用
```

### 聚合函数

```python
from pyflink.datastream.functions import (
    ReduceFunction,
    AggregateFunction,
    ProcessWindowFunction
)

# ====== ReduceFunction ======
class SumAmount(ReduceFunction):
    def reduce(self, value1, value2):
        return {
            "category": value1["category"],
            "total_amount": value1["amount"] + value2["amount"]
        }

result = keyed_stream \
    .window(TumblingEventTimeWindows.of(Duration.of_minutes(5))) \
    .reduce(SumAmount())

# ====== ProcessWindowFunction ======
# 可访问窗口元信息（窗口起止时间、当前 key 等）
class WindowStats(ProcessWindowFunction):
    def process(self, key, context, elements, out):
        window = context.window()
        count = len(list(elements))
        total = sum(e["amount"] for e in elements)
        out.collect({
            "key": key,
            "window_start": window.start,
            "window_end": window.end,
            "count": count,
            "total": total,
            "avg": total / count if count > 0 else 0
        })

result = keyed_stream \
    .window(TumblingEventTimeWindows.of(Duration.of_minutes(5))) \
    .process(WindowStats())

# ====== 增量聚合 + 全窗口函数组合 ======
# 使用 ProcessWindowFunction 包裹增量聚合，兼顾性能和灵活性
from pyflink.datastream.functions import AggregateFunction

class CountAndSum(AggregateFunction):
    def create_accumulator(self):
        return {"count": 0, "sum": 0.0}

    def add(self, value, accumulator):
        accumulator["count"] += 1
        accumulator["sum"] += value["amount"]
        return accumulator

    def get_result(self, accumulator):
        return accumulator

    def merge(self, a, b):
        return {"count": a["count"] + b["count"], "sum": a["sum"] + b["sum"]}

result = keyed_stream \
    .window(TumblingEventTimeWindows.of(Duration.of_minutes(5))) \
    .aggregate(CountAndSum(), FinalStatsFunction())
```

---

## 状态管理

Flink 的核心优势之一：原生、高效的托管状态。

### 状态类型

```python
from pyflink.datastream import (
    ValueStateDescriptor,
    ListStateDescriptor,
    MapStateDescriptor,
    ReducingStateDescriptor
)
from pyflink.datastream.functions import KeyedProcessFunction
from pyflink.datastream.state import ValueState, ListState

# ====== ValueState: 单值状态 ======
class FraudDetector(KeyedProcessFunction):
    def open(self, runtime_context):
        self.last_transaction = runtime_context.get_state(
            ValueStateDescriptor("last_transaction", Types.PICKLED_BYTE_ARRAY())
        )
        self.flagged = runtime_context.get_state(
            ValueStateDescriptor("flagged", Types.BOOLEAN())
        )

    def process_element(self, value, ctx, out):
        # 获取上次交易时间
        last_time = self.last_transaction.value()
        current_time = value["timestamp"]

        if last_time is not None:
            gap = current_time - last_time
            if gap < 1_000:  # 1秒内连续交易，疑似欺诈
                out.collect({"user_id": value["user_id"], "alert": "rapid_transaction"})

        self.last_transaction.update(current_time)

        # 注册定时器
        ctx.timer_service().register_event_time_timer(current_time + 60_000)

    def on_timer(self, timestamp, ctx, out):
        # 定时器触发
        if self.flagged.value():
            out.collect({"user_id": ctx.get_current_key(), "alert": "timer_triggered"})
            self.flagged.clear()

# ====== MapState: 键值对状态 ======
class UserSession(KeyedProcessFunction):
    def open(self, runtime_context):
        self.page_views = runtime_context.get_map_state(
            MapStateDescriptor("page_views", Types.STRING(), Types.INT())
        )

    def process_element(self, value, ctx, out):
        page = value["page"]
        current = self.page_views.get(page) or 0
        self.page_views.put(page, current + 1)

        total_views = sum(self.page_views.values())
        out.collect({"user_id": value["user_id"], "total_views": total_views})

# ====== ListState: 列表状态 ======
class SlidingWindow(KeyedProcessFunction):
    def open(self, runtime_context):
        self.events = runtime_context.get_list_state(
            ListStateDescriptor("events", Types.PICKLED_BYTE_ARRAY())
        )

    def process_element(self, value, ctx, out):
        self.events.add(value)
        # 滑动窗口逻辑：保留最近100条
        items = list(self.events)
        if len(items) > 100:
            self.events.clear()
            for item in items[-100:]:
                self.events.add(item)
```

### 状态后端（State Backend）

```python
# RocksDB 状态后端（推荐生产环境）
env.set_state_backend("rocksdb")

# 配置增量 Checkpoint（大幅减少 Checkpoint 时间）
config = env.get_config()
config.set("state.backend.incremental", "true")
config.set("state.checkpoints.num-retained", "3")
config.set("state.rocksdb.memory.managed", "true")

# State TTL（自动清理过期状态）
from pyflink.datastream.state import StateTtlConfig

ttl_config = StateTtlConfig.builder(Duration.of_hours(24)) \
    .set_update_type(StateTtlConfig.UpdateType.OnCreateAndWrite) \
    .cleanup_in_background() \
    .build()

state_desc = ValueStateDescriptor("my_state", Types.STRING())
state_desc.enable_time_to_live(ttl_config)
```

---

## Checkpoint 与容错

### Checkpoint 原理

```
JobManager 触发 Checkpoint Barrier → 数据流中插入 Barrier
→ 各算子异步对齐 Barrier → 快照状态 → 存储到持久化存储
→ JobManager 确认完成

屏障对齐模式：
  AT_LEAST_ONCE: 不等齐，可能重复处理
  EXACTLY_ONCE:  等齐，精确一次（默认）
  ALIGNMENT_BARRIER / UNALIGNED: Flink 1.11+ 对齐/非对齐
```

### Checkpoint 配置

```python
from pyflink.datastream import CheckpointingMode, ExternalizedCheckpointCleanup

# 启用 Checkpoint
env.enable_checkpointing(60000)  # 每60秒一次

config = env.get_checkpoint_config()

# 精确一次语义
config.set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)

# Checkpoint 最小间隔（避免连续 Checkpoint）
config.set_min_pause_between_checkpoints(30_000)  # 30秒

# Checkpoint 超时
config.set_checkpoint_timeout(120_000)  # 2分钟

# 最大并发 Checkpoint 数
config.set_max_concurrent_checkpoints(1)

# 外部持久化 Checkpoint（Job 取消后保留）
config.set_externalized_checkpoint_cleanup(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
)

# 非对齐 Checkpoint（解决背压问题）
config.enable_unaligned_checkpoints()

# ====== 从 Checkpoint 恢复 ======
# 命令行：
# flink run -s /checkpoints/savepoint-xxxx -yid application_xxx my_job.jar

# 编程方式：
env.set("execution.savepoint.path", "/checkpoints/savepoint-xxxx")
```

### Savepoint

```bash
# 触发 Savepoint
flink savepoint <jobId> [targetDirectory]

# 从 Savepoint 恢复
flink run -s <savepointPath> -n my_job.jar

# 取消 Job 并创建 Savepoint
flink cancel -s <targetDirectory> <jobId>

# Savepoint vs Checkpoint:
#   Checkpoint: 自动触发，用于容错恢复，轻量级
#   Savepoint:  手动触发，用于版本升级/迁移，重量级但更完整
```

---

## Watermark

Watermark 用于处理事件时间乱序问题，声明"在此之前的事件不应再出现"。

```python
from pyflink.common import WatermarkStrategy
from pyflink.datastream.functions import TimestampAssigner
import datetime

# ====== 策略1：固定延迟 ======
watermark_strategy = WatermarkStrategy \
    .for_bounded_out_of_orderness(Duration.of_seconds(10)) \
    .with_timestamp_assigner(
        lambda event: event["event_time"]  # 提取事件时间字段
    )

events_with_watermark = events.assign_timestamps_and_watermarks(watermark_strategy)

# ====== 策略2：单调递增（无乱序）======
watermark_monotone = WatermarkStrategy \
    .for_monotonous_timestamps() \
    .with_timestamp_assigner(lambda event: event["event_time"])

# ====== 策略3：自定义 Watermark 生成器 ======
from pyflink.datastream.functions import WatermarkGeneratorSupplier, WatermarkGenerator

class CustomWatermarkGenerator(WatermarkGenerator):
    def __init__(self, max_out_of_orderness):
        self.max_out_of_orderness = max_out_of_orderness
        self.max_timestamp = 0

    def on_event(self, event, event_timestamp, output):
        self.max_timestamp = max(self.max_timestamp, event_timestamp)
        # 可以在这里发出 watermark
        # output.emit_watermark(Watermark(self.max_timestamp - self.max_out_of_orderness))

    def on_periodic_emit(self, output):
        output.emit_watermark(self.max_timestamp - self.max_out_of_orderness)

watermark_custom = WatermarkStrategy \
    .for_generator(lambda ctx: CustomWatermarkGenerator(10_000)) \
    .with_timestamp_assigner(lambda event: event["event_time"])
```

### 空闲 Source 处理

```python
# 当某个 Source 长时间没有数据时，Watermark 会卡住
# 配置空闲超时，跳过该 Source 的 Watermark 计算

watermark_strategy = WatermarkStrategy \
    .for_bounded_out_of_orderness(Duration.of_seconds(10)) \
    .with_idleness(Duration.of_minutes(1)) \
    .with_timestamp_assigner(lambda event: event["event_time"])
```

### 迟到数据处理

```python
# Side Output 收集迟到数据
from pyflink.datastream import OutputTag

late_data_tag = OutputTag("late-data")

result = events \
    .key_by(lambda e: e["category"]) \
    .window(TumblingEventTimeWindows.of(Duration.of_minutes(5))) \
    .allowed_lateness(Duration.of_minutes(2))  # 允许2分钟迟到 \
    .side_output_late_data(late_data_tag) \
    .aggregate(MyAggregateFunction())

# 获取迟到数据流
late_stream = result.get_side_output(late_data_tag)
late_stream.sink_to(dead_letter_queue_sink)
```

---

## Table API / SQL

Flink 也提供声明式 API，适合熟悉 SQL 的用户。

```python
from pyflink.table import StreamTableEnvironment
from pyflink.table import EnvironmentSettings

# 创建 Table 环境
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
table_env = StreamTableEnvironment.create(env, settings)

# 注册 Kafka Source 表
table_env.execute_sql("""
    CREATE TABLE source_events (
        user_id STRING,
        event_type STRING,
        amount DOUBLE,
        event_time TIMESTAMP(3),
        WATERMARK FOR event_time AS event_time - INTERVAL '10' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'user_events',
        'properties.bootstrap.servers' = 'kafka:9092',
        'properties.group.id' = 'flink-table',
        'format' = 'json',
        'scan.startup.mode' = 'latest-offset'
    )
""")

# 注册 Sink 表
table_env.execute_sql("""
    CREATE TABLE sink_aggregated (
        window_start TIMESTAMP(3),
        category STRING,
        event_count BIGINT,
        total_amount DOUBLE,
        PRIMARY KEY (window_start, category) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://localhost:5432/mydb',
        'table-name' = 'aggregated_metrics',
        'username' = 'user',
        'password' = 'pass'
    )
""")

# 流式 SQL 查询
table_env.execute_sql("""
    INSERT INTO sink_aggregated
    SELECT
        TUMBLE_START(event_time, INTERVAL '5' MINUTE) as window_start,
        event_type as category,
        COUNT(*) as event_count,
        SUM(amount) as total_amount
    FROM source_events
    GROUP BY
        TUMBLE(event_time, INTERVAL '5' MINUTE),
        event_type
""").wait()
```

---

## 最佳实践

### ✅ 推荐做法

1. **使用 Event Time + Watermark**，保证结果准确性
2. **合理设置 Checkpoint 间隔**，通常为 30秒-5分钟
3. **使用 RocksDB 状态后端**，支持增量 Checkpoint 和大状态
4. **设置 State TTL**，避免状态无限增长
5. **使用 Side Output 处理迟到数据**，不要直接丢弃
6. **监控反压**，`Flink Web UI → BackPressure`
7. **使用增量聚合**，减少窗口内状态大小
8. **合理设置并行度**，一般为 Kafka 分区数的倍数

### ❌ 避免的做法

1. **避免在 `process()` 中做阻塞 I/O**，使用 Async I/O
2. **避免使用 `Processing Time`** 做业务逻辑（时钟漂移导致结果不确定）
3. **避免大 Key 状态**，使用 MapState 替代 ValueState 存储 Map
4. **避免未设 TTL 的状态**，会导致 OOM
5. **避免过多算子链**，适当使用 `disableChaining()` 分离

### 性能调优清单

| 指标 | 目标值 | 说明 |
|------|--------|------|
| Checkpoint Duration | < 60s | 超时说明状态过大或 I/O 瓶颈 |
| BackPressure | < 10% (High) | 高反压说明有瓶颈算子 |
| Records in/sec | 接近 Source 速率 | 下游不丢数据 |
| GC Time | < 5% | 频繁 Full GC 说明内存不足 |
| State Size | 监控趋势 | 增长过快检查 TTL 配置 |

---

## 相关页面

- [[Spark大数据处理]] - Spark Structured Streaming 对比
- [[数据湖架构]] - Flink + 数据湖的流批一体架构
- [[Airflow工作流编排]] - Flink 任务的调度编排
- [[dbt数据转换]] - 数据仓库转换层工具

---
title: Flink流处理指南
aliases:
  - Apache Flink
  - Flink
  - Flink Streaming
  - 流处理
tags:
  - big-data
  - flink
  - stream-processing
  - real-time
  - checkpoint
  - state-management
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: 官方文档整理 + 实践经验
difficulty: advanced
project: AI-Agent知识库
---

# Flink流处理指南

> Apache Flink 是第三代分布式流处理引擎，提供**真正的流式语义**（逐条处理）、**精确一次（Exactly-Once）** 保障和**有状态计算**。适合低延迟、高吞吐的实时数据处理场景。

---

## 一、架构概览

```
┌────────────────────────────┐
│        Client（提交作业）      │
├────────────────────────────┤
│  JobManager                 │
│  ├─ Dispatcher              │  接收作业
│  ├─ ResourceManager         │  资源调度
│  └─ JobMaster               │  作业调度（含 Checkpoint Coordinator）
├────────────────────────────┤
│  TaskManager × N            │
│  └─ Task Slot × M           │  执行具体 Task
├────────────────────────────┤
│  State Backend (RocksDB)    │  状态存储
│  Checkpoint Storage (HDFS)  │  快照持久化
└────────────────────────────┘
```

### 与 Spark Streaming 的核心区别

| 特性 | Spark Structured Streaming | Flink |
|------|--------------------------|-------|
| 处理模型 | 微批（Mini-Batch） | 真正流式（逐条处理） |
| 延迟 | 秒~分钟级 | 毫秒级 |
| 状态管理 | 有限（基于文件） | 完整（Operator State / Keyed State） |
| 时间语义 | Event Time + Watermark | Event Time + Watermark + Ingestion Time |
| 窗口类型 | 滚动、滑动、会话 | 滚动、滑动、会话 + 全局窗口 |
| 精确一次 | 支持 | 支持（Checkpoint 机制更强健） |

---

## 二、DataStream API

### 2.1 流程：Source → Transformation → Sink

```java
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.api.common.functions.MapFunction;

public class WordCountStream {

    public static void main(String[] args) throws Exception {
        final StreamExecutionEnvironment env =
            StreamExecutionEnvironment.getExecutionEnvironment();

        // 并行度
        env.setParallelism(4);

        // Source: 从 Socket 读取
        DataStream<String> text = env.socketTextStream("localhost", 9999);

        // Transformation
        DataStream<WordCount> counts = text
            .flatMap((String line, Collector<WordCount> out) -> {
                for (String word : line.toLowerCase().split("\\W+")) {
                    if (!word.isEmpty()) {
                        out.collect(new WordCount(word, 1));
                    }
                }
            })
            .returns(WordCount.class)
            .keyBy(wc -> wc.word)      // 按 word 分组
            .sum("count");              // 聚合

        // Sink: 输出到标准输出
        counts.print();

        // ⚠️ 流作业必须 execute
        env.execute("WordCount Streaming Job");
    }

    public static class WordCount {
        public String word;
        public int count;
        public WordCount() {}
        public WordCount(String word, int count) {
            this.word = word;
            this.count = count;
        }
        @Override
        public String toString() {
            return word + ": " + count;
        }
    }
}
```

### 2.2 Source 连接器

```java
// Kafka Source（推荐新 API）
KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
    .setBootstrapServers("kafka1:9092,kafka2:9092")
    .setTopics("input-events")
    .setGroupId("flink-consumer-group")
    .setStartingOffsets(OffsetsInitializer.earliest())
    .setValueOnlyDeserializer(new SimpleStringSchema())
    .build();

DataStream<String> stream = env.fromSource(
    kafkaSource,
    WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofSeconds(5)),
    "kafka-source"
);

// File Source（监控目录）
FileSource<String> fileSource = FileSource.forRecordStreamFormat(
    new TextLineInputFormat(),
    new Path("hdfs:///data/input/")
).build();

DataStream<String> fileStream = env.fromSource(
    fileSource,
    WatermarkStrategy.noWatermarks(),
    "file-source"
);
```

### 2.3 Sink 连接器

```java
// Kafka Sink
KafkaSink<String> kafkaSink = KafkaSink.<String>builder()
    .setBootstrapServers("kafka1:9092")
    .setRecordSerializer(KafkaRecordSerializationSchema.builder()
        .setTopic("output-events")
        .setValueSerializationSchema(new SimpleStringSchema())
        .build())
    .setDeliveryGuarantee(DeliveryGuarantee.EXACTLY_ONCE)
    .build();

stream.sinkTo(kafkaSink);

// JDBC Sink（精确一次）
JdbcSink.sink(
    "INSERT INTO user_events (user_id, event_type, event_time) VALUES (?, ?, ?) " +
    "ON DUPLICATE KEY UPDATE event_type = VALUES(event_type)",
    (ps, event) -> {
        ps.setLong(1, event.getUserId());
        ps.setString(2, event.getType());
        ps.setTimestamp(3, Timestamp.from(Instant.ofEpochMilli(event.getTimestamp())));
    },
    JdbcExecutionOptions.builder()
        .withBatchSize(1000)
        .withBatchIntervalMs(200)
        .build(),
    new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
        .withUrl("jdbc:mysql://db:3306/analytics")
        .withDriverName("com.mysql.cj.jdbc.Driver")
        .withUsername("root")
        .withPassword("secret")
        .build()
);
```

---

## 三、Window 窗口

Flink 的窗口机制将无限流切分为有限的数据片段，用于聚合计算。

### 3.1 窗口类型

```
┌─────────────────────────────────────────────────┐
│  Tumbling Window（滚动窗口 - 不重叠）              │
│  |--- 5min ---|--- 5min ---|--- 5min ---|       │
├─────────────────────────────────────────────────┤
│  Sliding Window（滑动窗口 - 可重叠）               │
│  |--- 5min ---|                              │
│      |--- 5min ---|                         │
│           |--- 5min ---|                    │
├─────────────────────────────────────────────────┤
│  Session Window（会话窗口 - 基于活跃间隙）          │
│  |-- session1 --|   gap   |-- session2 --|     │
└─────────────────────────────────────────────────┘
```

### 3.2 代码示例

```java
DataStream<Event> events = ...; // 含 timestamp 字段

// 1. 滚动窗口（5分钟）
events
    .keyBy(e -> e.userId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new MyAggregateFunction());

// 2. 滑动窗口（窗口10分钟，步长2分钟）
events
    .keyBy(e -> e.userId)
    .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(2)))
    .sum("amount");

// 3. 会话窗口（不活跃10分钟则切割）
events
    .keyBy(e -> e.userId)
    .window(EventTimeSessionWindows.withGap(Time.minutes(10)))
    .process(new SessionWindowFunction());

// 4. 全局窗口（需配合自定义 Trigger）
events
    .keyBy(e -> e.userId)
    .window(GlobalWindows.create())
    .trigger(CountTrigger.of(100))  // 每100条触发一次
    .process(new GlobalWindowFunction());
```

### 3.3 WindowFunction vs ProcessWindowFunction

```java
// ProcessWindowFunction：可获取窗口上下文信息
events
    .keyBy(e -> e.userId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .process(new ProcessWindowFunction<Event, Result, Long, TimeWindow>() {
        @Override
        public void process(
                Long userId,
                Context ctx,
                Iterable<Event> events,
                Collector<Result> out) {

            TimeWindow window = ctx.window();
            long count = 0;
            double totalAmount = 0;

            for (Event e : events) {
                count++;
                totalAmount += e.getAmount();
            }

            out.collect(new Result(
                userId,
                window.getStart(),
                window.getEnd(),
                count,
                totalAmount / count  // 平均值
            ));
        }
    });

// AggregateFunction：增量聚合，性能更高（推荐）
events
    .keyBy(e -> e.userId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(
        // 增量聚合器
        new AggregateFunction<Event, Tuple2<Long, Double>, Result>() {
            @Override public Tuple2<Long, Double> createAccumulator() {
                return Tuple2.of(0L, 0.0);
            }
            @Override public Tuple2<Long, Double> add(Event e, Tuple2<Long, Double> acc) {
                return Tuple2.of(acc.f0 + 1, acc.f1 + e.getAmount());
            }
            @Override public Result getResult(Tuple2<Long, Double> acc) {
                return new Result(acc.f0, acc.f1, acc.f1 / acc.f0);
            }
            @Override public Tuple2<Long, Double> merge(
                    Tuple2<Long, Double> a, Tuple2<Long, Double> b) {
                return Tuple2.of(a.f0 + b.f0, a.f1 + b.f1);
            }
        }
    );
```

---

## 四、状态管理

### 4.1 状态类型

| 类型 | 说明 | 适用算子 |
|------|------|----------|
| **ValueState** | 单值状态 | keyBy 后的算子 |
| **ListState** | 列表状态 | keyBy 后的算子 |
| **MapState** | 映射状态 | keyBy 后的算子 |
| **ReducingState** | 自动聚合 | keyBy 后的算子 |
| **BroadcastState** | 广播状态 | 广播流与主流 JOIN |

### 4.2 Keyed State 使用

```java
import org.apache.flink.api.common.state.*;
import org.apache.flink.configuration.Configuration;

public class FraudDetectionFunction
        extends KeyedProcessFunction<Long, Transaction, Alert> {

    private ValueState<Double> totalAmountState;
    private MapState<String, Integer> categoryCountState;
    private ListState<Transaction> recentTransactionsState;

    @Override
    public void open(Configuration parameters) {
        ValueStateDescriptor<Double> totalDesc =
            new ValueStateDescriptor<>("totalAmount", Double.class);
        // 设置 TTL（状态过期自动清除）
        totalDesc.enableTimeToLive(
            StateTtlConfig.newBuilder(Time.hours(24))
                .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
                .setStateVisibility(
                    StateTtlConfig.StateVisibility.NeverReturnExpired)
                .build()
        );
        totalAmountState = getRuntimeContext().getState(totalDesc);

        MapStateDescriptor<String, Integer> categoryDesc =
            new MapStateDescriptor<>("categoryCount", String.class, Integer.class);
        categoryCountState = getRuntimeContext().getMapState(categoryDesc);

        ListStateDescriptor<Transaction> recentDesc =
            new ListStateDescriptor<>("recent", Transaction.class);
        recentTransactionsState = getRuntimeContext().getListState(recentDesc);
    }

    @Override
    public void processElement(
            Transaction txn,
            Context ctx,
            Collector<Alert> out) throws Exception {

        // 1. 更新总金额
        double prevTotal = totalAmountState.value() != null
            ? totalAmountState.value() : 0.0;
        double newTotal = prevTotal + txn.getAmount();
        totalAmountState.update(newTotal);

        // 2. 更新类目计数
        int catCount = categoryCountState.get(txn.getCategory());
        if (catCount == 0) catCount = 0;
        categoryCountState.put(txn.getCategory(), catCount + 1);

        // 3. 添加最近交易（保留最新10条）
        recentTransactionsState.add(txn);
        if (ctx.timerService().currentProcessingTime() % 60000 == 0) {
            // 定时清理旧数据
            cleanupOldTransactions();
        }

        // 4. 欺诈检测逻辑
        if (newTotal > 50000.0) {
            out.collect(new Alert(
                txn.getUserId(),
                "HIGH_TOTAL_AMOUNT",
                newTotal
            ));
        }

        // 5. 注册定时器（1小时后触发）
        long triggerTime = ctx.timerService().currentProcessingTime()
            + 3600_000L;
        ctx.timerService().registerProcessingTimeTimer(triggerTime);
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<Alert> out)
            throws Exception {
        // 定时器触发时执行逻辑
        Double total = totalAmountState.value();
        if (total != null && total < 100.0) {
            out.collect(new Alert(ctx.getCurrentKey(), "LOW_ACTIVITY", total));
        }
    }

    private void cleanupOldTransactions() throws Exception {
        // 自定义清理逻辑
    }
}
```

### 4.3 State Backend 选择

| State Backend | 存储位置 | 特点 |
|---------------|----------|------|
| **HashMapStateBackend** | JVM 堆内存 | 最快，受堆大小限制 |
| **EmbeddedRocksDBStateBackend** | RocksDB（磁盘） | 支持超大状态，有磁盘 I/O 开销 |

```java
// 配置 RocksDB State Backend（生产推荐）
env.setStateBackend(new EmbeddedRocksDBStateBackend());

// Checkpoint 存储
env.getCheckpointConfig().setCheckpointStorage("hdfs:///flink/checkpoints/");

// RocksDB 调优
Configuration rocksDBConfig = new Configuration();
rocksDBConfig.set(
    RocksDBOptions.MAX_OPEN_FILES,
    -1  // 无限制
);
env.configure(rocksDBConfig);
```

---

## 五、Checkpoint 与容错

### 5.1 Checkpoint 原理

Flink 的 Checkpoint 基于 **Chandy-Lamport 算法**，通过向数据流注入 **Checkpoint Barrier** 来实现全局一致性快照。

```
           ┌── Barrier N ──┐
Source1 ──►│    data...     │──► Operator ──► Sink
Source2 ──►│── Barrier N ──┐│
           │    data...     │
```

当算子收到所有输入的 Barrier N 后：
1. 暂停处理新数据
2. 将当前状态写入 State Backend（异步）
3. 向下游广播 Barrier N
4. 恢复数据处理

### 5.2 Checkpoint 配置

```java
StreamExecutionEnvironment env =
    StreamExecutionEnvironment.getExecutionEnvironment();

// 开启 Checkpoint（每60秒一次）
env.enableCheckpointing(60000);

CheckpointConfig config = env.getCheckpointConfig();

// 模式：精确一次
config.setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);

// 两次 Checkpoint 之间的最小间隔（避免堆积）
config.setMinPauseBetweenCheckpoints(30000);

// Checkpoint 超时时间
config.setCheckpointTimeout(300000); // 5分钟

// 最大并发 Checkpoint 数
config.setMaxConcurrentCheckpoints(1);

// Checkpoint 外部化：作业取消后保留
config.setExternalizedCheckpointCleanup(
    CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);

// 不允许有进展的 Checkpoint（调试）
config.setFailOnCheckpointingErrors(false);

// Checkpoint 存储路径
config.setCheckpointStorage("hdfs:///flink/checkpoints/myapp/");
```

### 5.3 Savepoint vs Checkpoint

| 特性 | Checkpoint | Savepoint |
|------|-----------|-----------|
| 触发方式 | 自动周期性 | 手动触发 |
| 目的 | 故障恢复 | 版本升级 / 作业迁移 |
| 格式 | 面向效率（增量） | 面向可移植性（标准化） |
| 取消后 | 默认删除 | 保留 |
| 命令 | 自动 | `flink savepoint :jobId` |

```bash
# 手动创建 Savepoint
flink savepoint <jobId> hdfs:///flink/savepoints/

# 从 Savepoint 恢复
flink run -s hdfs:///flink/savepoints/savepoint-xxxxx -yid <yarnAppId> ./myjob.jar

# 取消作业并创建 Savepoint
flink cancel -s hdfs:///flink/savepoints/ <jobId>
```

---

## 六、Watermark 与时间语义

### 6.1 三种时间

| 时间 | 说明 | 适用场景 |
|------|------|----------|
| **Event Time** | 事件发生的时间 | ✅ 最常用（数据准确性） |
| **Ingestion Time** | 数据进入 Flink 的时间 | 不关心事件真实时间 |
| **Processing Time** | 算子处理的当前时间 | 延迟最低，但不准确 |

### 6.2 Watermark 策略

```java
// 策略1：有界乱序（最常用，允许5秒延迟）
WatermarkStrategy<Event> strategy = WatermarkStrategy
    .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
    .withTimestampAssigner((event, timestamp) -> event.getEventTimestamp());

// 策略2：严格升序（数据天然有序）
WatermarkStrategy<Event> ascendingStrategy = WatermarkStrategy
    .<Event>forMonotonousTimestamps()
    .withTimestampAssigner((event, ts) -> event.getEventTimestamp());

// 策略3：自定义 WatermarkGenerator
WatermarkStrategy<Event> customStrategy = WatermarkStrategy
    .forGenerator(ctx -> new PunctuatedWatermarkGenerator())
    .withTimestampAssigner((event, ts) -> event.getEventTimestamp());

// 应用到流
DataStream<Event> withWatermarks = events.assignTimestampsAndWatermarks(strategy);

// Kafka Source 直接设置
KafkaSource<Event> source = KafkaSource.<Event>builder()
    // ...省略其他配置
    .build();

DataStream<Event> stream = env.fromSource(
    source,
    WatermarkStrategy
        .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
        .withTimestampAssigner((e, ts) -> e.getEventTimestamp()),
    "kafka-events"
);
```

### 6.3 处理迟到数据

```java
events
    .keyBy(e -> e.userId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    // 允许迟到1分钟（Watermark 超出窗口后仍保留窗口1分钟）
    .allowedLateness(Time.minutes(1))
    // 严重迟到的数据发到侧输出
    .sideOutputLateData(lateOutputTag)
    .process(new MyWindowFunction());

// 获取迟到数据
DataStream<Event> lateEvents = result.getSideOutput(lateOutputTag);
```

---

## 七、Flink SQL & Table API

```java
StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);

// 注册 Kafka 源表
tableEnv.executeSql("""
    CREATE TABLE source_events (
        event_id    STRING,
        user_id     BIGINT,
        event_type  STRING,
        amount      DOUBLE,
        event_time  TIMESTAMP(3),
        WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'input-events',
        'properties.bootstrap.servers' = 'kafka1:9092',
        'properties.group.id' = 'flink-sql-group',
        'scan.startup.mode' = 'group-offsets',
        'format' = 'json'
    )
""");

// 注册 JDBC 结果表
tableEnv.executeSql("""
    CREATE TABLE sink_aggregated (
        window_start TIMESTAMP(3),
        window_end   TIMESTAMP(3),
        event_type   STRING,
        cnt          BIGINT,
        total_amount DOUBLE,
        PRIMARY KEY (window_start, window_end, event_type) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:mysql://db:3306/analytics',
        'table-name' = 'event_aggregations',
        'username' = 'root',
        'password' = 'secret'
    )
""");

// SQL 查询（窗口聚合）
tableEnv.executeSql("""
    INSERT INTO sink_aggregated
    SELECT
        TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
        TUMBLE_END(event_time, INTERVAL '5' MINUTE) AS window_end,
        event_type,
        COUNT(*) AS cnt,
        SUM(amount) AS total_amount
    FROM source_events
    GROUP BY
        TUMBLE(event_time, INTERVAL '5' MINUTE),
        event_type
""");
```

---

## 八、生产部署最佳实践

### 8.1 集群部署模式

| 模式 | 说明 | 适用 |
|------|------|------|
| **Session** | 共享 Flink 集群 | 开发测试 |
| **Per-Job** | 每个作业独立集群 | ⚠️ 已弃用（Flink 1.15+） |
| **Application** | 每个应用一个集群 | ✅ 生产推荐（K8s/YARN） |

### 8.2 flink-conf.yaml 关键配置

```yaml
# JobManager
jobmanager.rpc.address: jm-host
jobmanager.rpc.port: 6123
jobmanager.memory.process.size: 4096m

# TaskManager
taskmanager.memory.process.size: 8192m
taskmanager.numberOfTaskSlots: 2

# Checkpoint
execution.checkpointing.interval: 60s
execution.checkpointing.mode: EXACTLY_ONCE
execution.checkpointing.externalized-checkpoint-retention: RETAIN_ON_CANCELLATION
state.backend: rocksdb
state.checkpoints.dir: hdfs:///flink/checkpoints
state.savepoints.dir: hdfs:///flink/savepoints

# Restart Strategy
restart-strategy: exponential-delay
restart-strategy.exponential-delay.initial-backoff: 10s
restart-strategy.exponential-delay.max-backoff: 5min
restart-strategy.exponential-delay.attempts-before-reset-backoff: 10
```

### 8.3 监控指标

| 指标 | 含义 | 告警阈值 |
|------|------|----------|
| `numRecordsInPerSecond` | 输入吞吐 | 持续下降 |
| `numRecordsOutPerSecond` | 输出吞吐 | 持续为 0 |
| `currentEventTimeLag` | 事件时间延迟 | > 60s |
| `checkpointDuration` | Checkpoint 耗时 | > 5min |
| `numberOfFailedCheckpoints` | 失败次数 | > 3 连续失败 |
| `backPressuredTimeMsPerSecond` | 反压时间 | > 500ms/s |

### 8.4 反压排查

```bash
# Flink Web UI → BackPressure 标签页
# High: > 0.5（红色）
# Low: < 0.1（绿色）

# 常见原因：
# 1. 下游 Sink 慢（数据库写入慢、Kafka 分区不均）
# 2. 数据倾斜（某个 Key 数据量过大）
# 3. GC 时间过长（TaskManager 堆内存不足）
# 4. 状态过大导致 Checkpoint 超时
```

---

## 相关页面

- [[Spark核心指南]] - 批处理与微批流处理对比
- [[Hadoop生态系统]] - HDFS 作为 Checkpoint/Savepoint 存储
- [[数据湖架构]] - Flink + Iceberg/Hudi 实时数仓
- [[数据中台架构]] - Flink 在实时数据管道中的角色
- [[Kafka消息队列]] - Flink 最常用的 Source/Sink

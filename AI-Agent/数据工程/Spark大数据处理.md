---
title: Spark大数据处理
aliases:
  - Spark
  - Apache Spark
  - 大数据处理Spark
tags:
  - 数据工程
  - 大数据
  - Spark
  - 分布式计算
type: 技术文档
status: 完成
created: 2026-06-28
updated: 2026-06-28
source: 官方文档 + 实践总结
difficulty: 高级
project: AI-Agent
---

# Spark大数据处理

> Apache Spark 是一个开源的分布式计算框架，支持大规模数据的批处理和流处理。相比 Hadoop MapReduce，Spark 基于内存计算，速度提升了10-100倍。

## 目录

- [[#核心概念]]
- [[#RDD (弹性分布式数据集)]]
- [[#DataFrame API]]
- [[#Spark SQL]]
- [[#Structured Streaming]]
- [[#性能调优]]
- [[#最佳实践]]
- [[#相关页面]]

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **Driver** | 运行 `main()` 函数的进程，创建 `SparkContext`/`SparkSession` |
| **Executor** | 在工作节点上执行任务的进程 |
| **RDD** | Resilient Distributed Dataset，弹性分布式数据集 |
| **DAG** | 有向无环图，Spark 的调度模型 |
| **Partition** | 数据分片，是并行处理的基本单元 |

---

## RDD (弹性分布式数据集)

RDD 是 Spark 最底层的抽象，是一个不可变的、分区的、容错的集合。

### 创建 RDD

```python
from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("RDDExample").setMaster("local[*]")
sc = SparkContext(conf=conf)

# 从集合创建
rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# 从文件创建
text_rdd = sc.textFile("hdfs://namenode:9000/data/input.txt")

# 从其他 RDD 转换
squared_rdd = rdd.map(lambda x: x * x)
```

### Transformation 与 Action

```python
# ====== Transformations（惰性求值）======

# map: 对每个元素应用函数
mapped = rdd.map(lambda x: (x, x * 2))

# filter: 过滤元素
evens = rdd.filter(lambda x: x % 2 == 0)

# flatMap: 展开嵌套结构
words = text_rdd.flatMap(lambda line: line.split(" "))

# reduceByKey: 按key聚合
pairs = words.map(lambda w: (w.lower(), 1))
word_counts = pairs.reduceByKey(lambda a, b: a + b)

# groupByKey: 按key分组（大数据量时性能差，优先用 reduceByKey）
grouped = pairs.groupByKey()

# join: 两个 RDD 连接
rdd1 = sc.parallelize([("a", 1), ("b", 2)])
rdd2 = sc.parallelize([("a", "x"), ("b", "y")])
joined = rdd1.join(rdd2)  # [("a", (1, "x")), ("b", (2, "y"))]

# union: 合并两个RDD
combined = evens.union(odds)

# distinct: 去重
unique = rdd.distinct()

# ====== Actions（触发计算）======

# collect: 收集到Driver（大数据慎用）
result = word_counts.collect()

# count: 计数
cnt = rdd.count()

# reduce: 聚合
total = rdd.reduce(lambda a, b: a + b)

# take: 取前N个
top10 = word_counts.takeOrdered(10, key=lambda x: -x[1])

# saveAsTextFile: 保存到文件
word_counts.saveAsTextFile("hdfs://namenode:9000/output/")
```

### 持久化（缓存）

```python
# 缓存 RDD 以避免重复计算
from pyspark import StorageLevel

word_counts.persist(StorageLevel.MEMORY_AND_DISK)
# 等价于 word_counts.cache()

# 使用完后释放
word_counts.unpersist()

# 自定义存储级别
rdd.persist(StorageLevel(
    useDisk=True,
    useMemory=True,
    useOffHeap=False,
    deserialized=True,
    replication=2
))
```

---

## DataFrame API

DataFrame 是以命名列组织的分布式数据集，类似于关系数据库中的表，是 Spark 2.0+ 的推荐 API。

### 创建 DataFrame

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DataFrameExample") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# 从 Python 列表创建
data = [
    ("Alice", 30, "Engineer", 80000),
    ("Bob", 25, "Designer", 60000),
    ("Charlie", 35, "Manager", 120000),
]
columns = ["name", "age", "role", "salary"]
df = spark.createDataFrame(data, columns)

# 从 JSON/CSV/Parquet 读取
df_json = spark.read.json("data/users.json")
df_csv = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv("data/users.csv")
df_parquet = spark.read.parquet("data/users.parquet")

# 从 JDBC 读取
df_jdbc = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/mydb") \
    .option("dbtable", "employees") \
    .option("user", "user") \
    .option("password", "pass") \
    .load()
```

### DataFrame 操作

```python
# select
df.select("name", "age").show()

# 条件过滤
df.filter(df.age > 25).show()
df.filter("age > 25 AND salary > 70000").show()

# 聚合
from pyspark.sql import functions as F

df.groupBy("role") \
    .agg(
        F.count("*").alias("count"),
        F.avg("salary").alias("avg_salary"),
        F.max("age").alias("max_age")
    ) \
    .orderBy(F.desc("avg_salary")) \
    .show()

# join
employees = spark.read.parquet("data/employees.parquet")
departments = spark.read.parquet("data/departments.parquet")

result = employees.join(departments, "dept_id", "left") \
    .select("name", "dept_name", "salary")

# 窗口函数
from pyspark.sql.window import Window

window_spec = Window.partitionBy("dept_id").orderBy(F.desc("salary"))

ranked = employees \
    .withColumn("rank", F.rank().over(window_spec)) \
    .withColumn("dense_rank", F.dense_rank().over(window_spec)) \
    .withColumn("row_number", F.row_number().over(window_spec)) \
    .filter(F.col("rank") <= 3)

# UDF（用户自定义函数）
@F.udf(returnType="string")
def grade_salary(salary):
    if salary >= 100000:
        return "High"
    elif salary >= 70000:
        return "Medium"
    else:
        return "Low"

df = df.withColumn("grade", grade_salary(df.salary))

# 写入
df.write \
    .mode("overwrite") \
    .partitionBy("year", "month") \
    .parquet("data/output/salary_grades.parquet")
```

---

## Spark SQL

使用标准 SQL 查询 DataFrame 和数据源。

```python
# 注册临时视图
df.createOrReplaceTempView("employees")

# 使用 SQL 查询
result = spark.sql("""
    SELECT 
        role,
        COUNT(*) as emp_count,
        ROUND(AVG(salary), 2) as avg_salary,
        MAX(salary) as max_salary,
        MIN(salary) as min_salary
    FROM employees
    WHERE age > 25
    GROUP BY role
    HAVING COUNT(*) > 1
    ORDER BY avg_salary DESC
""")

# 全局临时视图（跨 Session 共享）
df.createOrReplaceGlobalTempView("global_employees")
spark.sql("SELECT * FROM global_temp.global_employees").show()

# 使用 SQL 读取多种数据源
spark.sql("""
    CREATE OR REPLACE TEMPORARY VIEW sales_view
    USING parquet
    OPTIONS (
        path 'data/sales.parquet'
    )
""")

spark.sql("""
    SELECT 
        date_trunc('month', sale_date) as month,
        SUM(amount) as total_sales
    FROM sales_view
    GROUP BY 1
    ORDER BY 1
""").show()
```

---

## Structured Streaming

基于 DataFrame/SQL API 的流处理引擎，支持端到端的精确一次语义。

```python
from pyspark.sql.functions import (
    col, current_timestamp, window,
    expr, from_json, to_json, struct
)
from pyspark.sql.types import (
    StructType, StructField, StringType,
    IntegerType, DoubleType, TimestampType
)

# 定义输入 schema
schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("event_time", TimestampType(), True),
])

# ====== Kafka 数据源读取 ======
raw_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "user_events") \
    .option("startingOffsets", "latest") \
    .load()

# 解析 JSON 消息
events_stream = raw_stream \
    .selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# ====== 窗口聚合 ======
windowed_counts = events_stream \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        window(col("event_time"), "5 minutes"),
        col("event_type")
    ) \
    .agg(
        F.count("*").alias("event_count"),
        F.sum("amount").alias("total_amount"),
        F.avg("amount").alias("avg_amount")
    )

# ====== 写入 Console（调试用）======
query_console = windowed_counts \
    .writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime="1 minute") \
    .start()

# ====== 写入 Kafka ======
query_kafka = windowed_counts \
    .selectExpr(
        "CAST(event_type AS STRING) as key",
        "to_json(struct(*)) as value"
    ) \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "aggregated_metrics") \
    .option("checkpointLocation", "/checkpoint/agg_metrics") \
    .outputMode("update") \
    .start()

# ====== Foreach Sink（自定义输出）======
def process_row(row):
    # 写入外部系统（如 Elasticsearch, Redis 等）
    print(f"Processing: {row}")

query_foreach = windowed_counts \
    .writeStream \
    .foreach(process_row) \
    .option("checkpointLocation", "/checkpoint/foreach") \
    .start()

# 等待终止
spark.streams.awaitAnyTermination()
```

### 输出模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `append` | 仅输出新增行 | 无聚合查询 |
| `update` | 输出变化的行 | 有聚合查询 |
| `complete` | 输出全量结果 | 结果集较小 |

---

## 性能调优

### 1. 分区优化

```python
# 重新分区
df_repartitioned = df.repartition(200, "dept_id")  # 按列哈希分区
df_coalesced = df.coalesce(10)  # 减少分区数（无shuffle）

# 自动调整分区大小
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "200")

# 广播小表（避免 Shuffle Join）
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10485760)  # 10MB
# 或手动指定
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
```

### 2. 内存与序列化

```python
# SparkSession 配置
spark = SparkSession.builder \
    .appName("TuningExample") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.kryoserializer.buffer.max", "512m") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .config("spark.sql.inMemoryColumnarStorage.compressed", "true") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.memory", "16g") \
    .config("spark.executor.cores", "4") \
    .config("spark.executor.instances", "10") \
    .getOrCreate()
```

### 3. 数据倾斜处理

```python
# 方法1：加盐法打散倾斜key
from pyspark.sql.functions import col, concat, rand, lit, floor

salted = skewed_df.withColumn(
    "salted_key",
    concat(col("skewed_key"), lit("_"), floor(rand() * 100))
)

# 方法2：AQE 自动处理倾斜
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

### 4. 缓存策略

```python
# 缓存策略选择指南：
# - MEMORY_ONLY: 小数据集，频繁使用
# - MEMORY_AND_DISK: 大数据集，能接受磁盘读写
# - DISK_ONLY: 超大数据集
# - MEMORY_ONLY_SER: 内存有限但CPU充足

df.persist(StorageLevel.MEMORY_AND_DISK_SER)

# 监控缓存
print(f"Partition count: {df.rdd.getNumPartitions()}")
print(f"Cache size: {df._jdf.queryExecution().analyzed().stats().sizeInBytes()}")
```

### 5. 资源分配公式

```
executor_memory = total_node_memory - (reserved_memory * num_executors_per_node)
executor_cores  = 4-5（推荐值）
num_executors   = total_cores / executor_cores

# 常见配置示例（16节点集群，每节点16核128G）：
#   executor.memory = 16g（预留给系统和其他进程）
#   executor.cores = 4
#   executor.instances = 16 * (16/4 - 1) = 48
```

---

## 最佳实践

### ✅ 推荐做法

1. **优先使用 DataFrame/SQL API**，而非 RDD（Spark Catalyst 优化器能自动优化执行计划）
2. **使用 Parquet/ORC 列式存储**，压缩率高且支持谓词下推
3. **合理设置分区数**，通常为集群总核心数的 2-3 倍
4. **启用 AQE（自适应查询执行）**，Spark 3.0+ 默认开启
5. **使用 Broadcast Join** 处理小表 Join
6. **监控 Shuffle**，Shuffle 读写是性能瓶颈的主要来源
7. **使用 Checkpoint** 对长血缘链的 RDD 进行截断

### ❌ 避免的做法

1. **避免在 UDF 中做重计算**，尽量用内置函数
2. **避免 `collect()` 大数据集到 Driver**
3. **避免 `groupByKey`**，使用 `reduceByKey` 或 `aggregateByKey`
4. **避免过多小文件**，使用 `coalesce` 或 `repartition` 合并
5. **避免在 map 中创建数据库连接**，使用 `foreachPartition`
6. **避免频繁创建 SparkSession/SparkContext**

---

## 相关页面

- [[数据湖架构]] - 数据存储与表格式选型
- [[Flink流处理引擎]] - 低延迟流处理替代方案
- [[Airflow工作流编排]] - Spark 任务的编排与调度
- [[dbt数据转换]] - 数据仓库层的 SQL 转换工具

---
title: Spark核心指南
aliases:
  - Apache Spark
  - Spark
  - Spark Guide
tags:
  - big-data
  - spark
  - rdd
  - dataframe
  - spark-sql
  - mllib
  - structured-streaming
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: 官方文档整理 + 实践经验
difficulty: intermediate
project: AI-Agent知识库
---

# Spark核心指南

> Apache Spark 是统一的大数据处理引擎，支持批处理、流处理、机器学习和图计算。相比 MapReduce，Spark 基于内存计算，性能提升 10-100 倍。

---

## 一、架构概览

```
┌──────────────────────────────────────┐
│           Spark Application           │
│  (SparkContext / SparkSession)        │
├──────────────────────────────────────┤
│  Spark SQL  │  Streaming  │ MLlib │ GraphX │
├──────────────────────────────────────┤
│         统一引擎 (Catalyst/Tungsten)    │
├──────────────────────────────────────┤
│    Standalone / YARN / K8s / Mesos    │
└──────────────────────────────────────┘
```

| 角色 | 说明 |
|------|------|
| **Driver** | 运行 main()，创建 SparkContext，调度 Task |
| **Cluster Manager** | 分配资源（YARN / K8s / Standalone） |
| **Executor** | 在 Worker 节点上执行 Task，缓存数据 |

---

## 二、RDD（弹性分布式数据集）

RDD 是 Spark 最底层的抽象，是一个不可变、分区的、可并行操作的集合。

### 2.1 创建 RDD

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("RDD Demo") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

sc = spark.sparkContext

# 方式1：从集合创建
rdd1 = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], numSlices=4)

# 方式2：从文件创建
rdd2 = sc.textFile("hdfs:///data/logs/*.log")

# 方式3：从已有 RDD 转换
rdd3 = rdd2.map(lambda line: line.split(","))
```

### 2.2 常用 Transformation 与 Action

```python
# ============ Transformation（懒执行，构建 DAG） ============

# map：一对一映射
squared = rdd1.map(lambda x: x ** 2)

# flatMap：一对多展开
words = sc.textFile("data.txt").flatMap(lambda line: line.split(" "))

# filter：过滤
evens = rdd1.filter(lambda x: x % 2 == 0)

# distinct：去重
unique = rdd1.distinct()

# groupByKey / reduceByKey
pairs = sc.parallelize([("a", 1), ("b", 2), ("a", 3), ("b", 4)])
# ✅ 推荐 reduceByKey（在 Map 端预聚合）
sums = pairs.reduceByKey(lambda x, y: x + y)
# ⚠️ 避免 groupByKey（全量 Shuffle）
grouped = pairs.groupByKey().mapValues(lambda vals: sum(vals))

# join
rdd_a = sc.parallelize([("user1", "Alice"), ("user2", "Bob")])
rdd_b = sc.parallelize([("user1", 25), ("user2", 30)])
joined = rdd_a.join(rdd_b)  # [("user1", ("Alice", 25)), ...]

# ============ Action（触发执行） ============
print(rdd1.collect())         # 收集到 Driver（慎用于大数据）
print(rdd1.count())           # 计数
print(rdd1.reduce(lambda x, y: x + y))  # 聚合
print(rdd1.take(5))           # 取前5个
rdd1.saveAsTextFile("hdfs:///output/result")
```

### 2.3 持久化（缓存）

```python
# 缓存策略选择
rdd_cached = rdd1.persist(StorageLevel.MEMORY_AND_DISK_SER)

# 使用后手动释放
rdd_cached.unpersist()
```

| StorageLevel | 说明 |
|--------------|------|
| MEMORY_ONLY | 仅内存，不序列化（默认） |
| MEMORY_AND_DISK | 内存不足时溢写到磁盘 |
| MEMORY_AND_DISK_SER | 序列化存储，节省空间 |
| DISK_ONLY | 仅磁盘 |

---

## 三、DataFrame / Dataset

DataFrame 是以命名列组织的分布式数据集，等价于关系数据库中的表。Spark 2.0+ 推荐统一使用 SparkSession API。

### 3.1 创建 DataFrame

```python
spark = SparkSession.builder \
    .appName("DataFrame Demo") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# 从 JSON 创建
df = spark.read.json("hdfs:///data/users.json")

# 从 CSV 创建（带 Schema）
df_csv = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("hdfs:///data/events.csv")

# 从 Parquet 创建
df_parquet = spark.read.parquet("hdfs:///data/parquet/")

# 从 Hive 表创建
df_hive = spark.sql("SELECT * FROM analytics.user_events WHERE dt = '2026-06-28'")

# 从 JDBC 创建
df_jdbc = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://db:5432/analytics") \
    .option("dbtable", "users") \
    .option("user", "admin") \
    .option("password", "secret") \
    .option("numPartitions", "10") \
    .option("partitionColumn", "user_id") \
    .option("lowerBound", "1") \
    .option("upperBound", "1000000") \
    .load()

df.printSchema()
df.show(10, truncate=False)
```

### 3.2 DataFrame 操作

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# 选择与过滤
result = df.filter(F.col("age") >= 18) \
           .select("name", "age", F.col("city").alias("location"))

# 聚合
agg_result = df.groupBy("city") \
    .agg(
        F.count("*").alias("user_count"),
        F.avg("age").alias("avg_age"),
        F.expr("percentile_approx(salary, 0.9)").alias("p90_salary")
    ) \
    .orderBy(F.desc("user_count"))

# 窗口函数
w = Window.partitionBy("city").orderBy(F.desc("salary"))
ranked = df.withColumn("salary_rank", F.row_number().over(w)) \
           .filter(F.col("salary_rank") <= 10)  # 每个城市 Top10 薪资

# JOIN
joined = users_df.join(orders_df, "user_id", "left") \
    .groupBy("user_id", "name") \
    .agg(F.sum("amount").alias("total_spent"))

# UDF（用户定义函数）
@F.udf(returnType="string")
def categorize_age(age):
    if age < 25: return "Young"
    elif age < 45: return "Adult"
    else: return "Senior"

df_with_category = df.withColumn("age_group", categorize_age(F.col("age")))

# 保存
df.write \
    .mode("overwrite") \
    .partitionBy("dt") \
    .parquet("hdfs:///output/users_partitioned/")

# 保存为 Hive 表
df.write.saveAsTable("analytics.users_result")
```

### 3.3 DataFrame 性能优于 RDD 的原因

| 优化 | 说明 |
|------|------|
| **Catalyst 优化器** | 对逻辑计划做 RBO + CBO 优化 |
| **Tungsten 引擎** | 堆外内存管理、代码生成（Whole-Stage CodeGen） |
| **序列化** | 使用 Tungsten 二进制格式，高效序列化 |
| **谓词下推** | 自动将过滤条件推到数据源层 |

---

## 四、Spark SQL

Spark SQL 提供了 SQL 接口与 DataFrame API 的统一访问。

### 4.1 混合使用 SQL 与 DataFrame

```python
# 注册临时视图
df.createOrReplaceTempView("temp_users")

# 直接使用 SQL
result = spark.sql("""
    SELECT
        city,
        COUNT(*) AS user_count,
        ROUND(AVG(age), 1) AS avg_age
    FROM temp_users
    WHERE age >= 18
    GROUP BY city
    HAVING COUNT(*) > 100
    ORDER BY user_count DESC
    LIMIT 20
""")

# 全局临时视图（跨 Session 共享）
df.createGlobalTempView("global_users")
spark.sql("SELECT * FROM global_temp.global_users")
```

### 4.2 查询计划分析

```python
# 查看逻辑计划
result.explain(True)

# 输出示例：
# == Parsed Logical Plan ==
# == Analyzed Logical Plan ==
# == Optimized Logical Plan ==
# == Physical Plan ==

# AQE（自适应查询执行）开启
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

---

## 五、MLlib

MLlib 是 Spark 的机器学习库，提供分类、回归、聚类、协同过滤等算法。

### 5.1 Pipeline 示例

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Tokenizer, StopWordsRemover, HashingTF, IDF,
    StringIndexer, VectorAssembler, StandardScaler
)
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator

# 1. 特征工程 Pipeline
tokenizer = Tokenizer(inputCol="text", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
hashingTF = HashingTF(inputCol="filtered_words", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="textFeatures")
labelIndexer = StringIndexer(inputCol="sentiment", outputCol="label")

assembler = VectorAssembler(
    inputCols=["textFeatures", "retweet_count", "like_count"],
    outputCol="features_raw"
)
scaler = StandardScaler(inputCol="features_raw", outputCol="features", withMean=True, withStd=True)

lr = LogisticRegression(featuresCol="features", labelCol="label", maxIter=20, regParam=0.01)

pipeline = Pipeline(stages=[
    tokenizer, remover, hashingTF, idf,
    labelIndexer, assembler, scaler, lr
])

# 2. 数据准备
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# 3. 训练
model = pipeline.fit(train_data)

# 4. 预测
predictions = model.transform(test_data)
predictions.select("text", "sentiment", "label", "prediction", "probability").show(10)

# 5. 评估
evaluator = BinaryClassificationEvaluator(
    labelCol="label",
    rawPredictionCol="prediction",
    metricName="areaUnderROC"
)
auc = evaluator.evaluate(predictions)
print(f"AUC: {auc:.4f}")

# 6. 保存模型
model.save("hdfs:///models/sentiment_lr")
```

### 5.2 常用算法

| 类别 | 算法 | 类名 |
|------|------|------|
| 分类 | 逻辑回归 | `LogisticRegression` |
| 分类 | 随机森林 | `RandomForestClassifier` |
| 分类 | GBT | `GBTClassifier` |
| 回归 | 线性回归 | `LinearRegression` |
| 回归 | 随机森林 | `RandomForestRegressor` |
| 聚类 | K-Means | `KMeans` |
| 推荐 | ALS 协同过滤 | `ALS` |
| 聚类 | LDA 主题模型 | `LDA` |

---

## 六、Structured Streaming

Structured Streaming 是 Spark 2.2+ GA 的流处理引擎，基于 Spark SQL 引擎，将流视为无限增长的表。

### 6.1 核心模型

```
Unbounded Table（无界输入表）
    → 查询（SQL / DataFrame）
    → 持续增量执行
    → 结果输出到 Sink
```

### 6.2 完整示例：Kafka → 处理 → Kafka

```python
spark = SparkSession.builder \
    .appName("StreamingPipeline") \
    .config("spark.sql.shuffle.partitions", "10") \
    .getOrCreate()

# 1. 读取 Kafka 流
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092,kafka2:9092") \
    .option("subscribe", "raw-events") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "true") \
    .load()

# 2. 解析 JSON
from pyspark.sql.functions import col, from_json, window, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType

event_schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("event_ts", StringType(), True),
])

parsed = raw_stream \
    .selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), event_schema).alias("data")) \
    .select("data.*") \
    .withColumn("event_time", col("event_ts").cast("timestamp"))

# 3. 窗口聚合（每5分钟滚动窗口，按 event_type 分组）
windowed_agg = parsed \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        window(col("event_time"), "5 minutes"),
        col("event_type")
    ) \
    .agg(
        F.count("*").alias("event_count"),
        F.sum("amount").alias("total_amount"),
        F.avg("amount").alias("avg_amount")
    ) \
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        "event_type", "event_count", "total_amount", "avg_amount"
    )

# 4. 写入 Kafka
query = windowed_agg.selectExpr(
    "to_json(struct(*)) AS value"
).writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("topic", "aggregated-events") \
    .option("checkpointLocation", "hdfs:///checkpoints/streaming_v1") \
    .outputMode("update") \
    .trigger(processingTime="1 minute") \
    .start()

query.awaitTermination()
```

### 6.3 输出模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `append` | 只输出新行 | 只有追加型查询（如无聚合） |
| `update` | 只输出变更的行 | 聚合查询默认 |
| `complete` | 输出整个结果表 | 结果集较小（如排行榜） |

---

## 七、性能调优

### 7.1 关键参数

```python
spark = SparkSession.builder \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .config("spark.sql.files.maxPartitionBytes", "134217728") \
    .config("spark.locality.wait", "10s") \
    .getOrCreate()
```

### 7.2 常见问题与解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| OOM | 数据倾斜 / 数据膨胀 | 开启 AQE Skew Join；salting 打散 |
| 任务慢 | Shuffle 过多 | 广播小表（`/*+ BROADCAST(t) */`）；减少 shuffle |
| 小文件多 | 分区过多 | `coalesce(n)` 或 AQE 自动合并 |
| Task 数太多 | 文件小 | 调大 `spark.sql.files.maxPartitionBytes` |
| 数据倾斜 | Key 分布不均 | Salt + 两阶段聚合 |

### 7.3 数据倾斜处理

```python
# 方案1：广播 JOIN（小表 < 100MB）
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 104857600)  # 100MB

# 方案2：加盐打散
from pyspark.sql.functions import concat, lit, rand, floor, broadcast

# 给大表 key 加随机前缀
df_large_salted = df_large.withColumn(
    "salted_key",
    concat(col("join_key"), lit("_"), floor(rand() * 10))
)

# 小表膨胀 10 倍
small_rows = []
for i in range(10):
    small_rows.append(df_small.withColumn(
        "salted_key",
        concat(col("join_key"), lit("_"), lit(i))
    ))
df_small_exploded = small_rows[0]
for r in small_rows[1:]:
    df_small_exploded = df_small_exploded.union(r)

result = df_large_salted.join(broadcast(df_small_exploded), "salted_key", "inner")
```

---

## 八、部署模式对比

| 模式 | 说明 | 适用 |
|------|------|------|
| **Local** | 单机调试 | 开发测试 |
| **Standalone** | Spark 自带集群管理器 | 小团队 |
| **YARN** | 与 Hadoop 共享集群资源 | 大多数企业 |
| **Kubernetes** | 容器化部署 | 云原生环境 |

---

## 相关页面

- [[Hadoop生态系统]] - HDFS 存储、YARN 资源管理
- [[Flink流处理指南]] - 对比 Spark Streaming 的低延迟方案
- [[数据湖架构]] - Spark + 数据湖（Delta/Iceberg）读写
- [[数据中台架构]] - Spark 在数据仓库中的 ETL 角色

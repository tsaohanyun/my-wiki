---
title: Hadoop生态系统
aliases:
  - Hadoop
  - Hadoop Ecosystem
  - Hadoop生态
tags:
  - big-data
  - hadoop
  - hdfs
  - mapreduce
  - yarn
  - hive
  - hbase
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: 官方文档整理 + 实践经验
difficulty: intermediate
project: AI-Agent知识库
---

# Hadoop生态系统

> Hadoop 是 Apache 基金会开源的分布式计算框架，为海量数据提供高可靠、高扩展性的存储与计算能力。经过十余年发展，已形成覆盖存储、计算、调度、查询、NoSQL 等领域的完整生态系统。

---

## 一、HDFS 架构

Hadoop Distributed File System（HDFS）是 Hadoop 的分布式存储层，设计目标是在廉价商用服务器集群上存储 PB 级数据，并容忍节点故障。

### 1.1 核心组件

| 组件 | 角色 | 说明 |
|------|------|------|
| **NameNode** | 主节点 | 管理文件系统的命名空间（目录树、文件→块映射），元数据常驻内存 |
| **Secondary NameNode** | 辅助节点 | 定期合并 fsimage 与 editlog，**不是热备** |
| **JournalNode** | 高可用组件 | HA 模式下共享 EditLog，保证两个 NameNode 状态一致 |
| **DataNode** | 从节点 | 实际存储数据块，周期性向 NameNode 发送心跳与块报告 |

### 1.2 数据写入流程

```
Client → NameNode（请求写入）
  NameNode 校验权限 & 返回 DataNode 列表
Client → DataNode1 → DataNode2 → DataNode3（Pipeline 副本写入）
  DataNode3 ACK → DataNode2 ACK → DataNode1 ACK → Client
Client → NameNode（关闭文件）
```

### 1.3 关键配置示例

```xml
<!-- hdfs-site.xml -->
<configuration>
  <!-- 副本数 -->
  <property>
    <name>dfs.replication</name>
    <value>3</value>
  </property>

  <!-- 块大小（默认128MB，大文件场景建议256MB） -->
  <property>
    <name>dfs.blocksize</name>
    <value>268435456</value> <!-- 256MB -->
  </property>

  <!-- NameNode HA -->
  <property>
    <name>dfs.nameservices</name>
    <value>mycluster</value>
  </property>
  <property>
    <name>dfs.ha.namenodes.mycluster</name>
    <value>nn1,nn2</value>
  </property>

  <!-- 自动故障转移 -->
  <property>
    <name>dfs.ha.automatic-failover.enabled</name>
    <value>true</value>
  </property>
</configuration>
```

### 1.4 HDFS 常用命令

```bash
# 上传文件
hdfs dfs -put localfile.txt /user/data/

# 查看目录
hdfs dfs -ls /user/data/

# 查看文件内容
hdfs dfs -cat /user/data/localfile.txt

# 设置副本数
hdfs dfs -setrep -w 5 /user/data/localfile.txt

# 删除文件
hdfs dfs -rm -r /user/data/old_dir/

# 文件校验
hdfs dfs -checksum /user/data/localfile.txt

# 均衡数据节点
hdfs balancer -threshold 10
```

---

## 二、MapReduce

MapReduce 是 Hadoop 的第一代分布式计算引擎，采用 **分而治之** 的思想：将任务拆分为 Map 和 Reduce 两个阶段。

### 2.1 执行流程

```
Input Split → Map（并行）→ Shuffle & Sort → Reduce（汇总）→ Output
```

### 2.2 WordCount 示例（Java）

```java
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;

public class WordCount {

    public static class TokenizerMapper
            extends Mapper<LongWritable, Text, Text, IntWritable> {
        private final static IntWritable one = new IntWritable(1);
        private Text word = new Text();

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String[] tokens = value.toString().split("\\s+");
            for (String token : tokens) {
                word.set(token.toLowerCase());
                context.write(word, one);
            }
        }
    }

    public static class IntSumReducer
            extends Reducer<Text, IntWritable, Text, IntWritable> {
        private IntWritable result = new IntWritable();

        @Override
        protected void reduce(Text key, Iterable<IntWritable> values, Context context)
                throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable val : values) {
                sum += val.get();
            }
            result.set(sum);
            context.write(key, result);
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "word count");
        job.setJarByClass(WordCount.class);
        job.setMapperClass(TokenizerMapper.class);
        job.setCombinerClass(IntSumReducer.class); // Combiner 本地预聚合
        job.setReducerClass(IntSumReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
```

### 2.3 MapReduce 性能优化要点

- **Combiner**：在 Map 端预聚合，减少 Shuffle 数据量
- **压缩**：Map 输出使用 Snappy/LZO 压缩，减少网络 I/O
- **数据倾斜**：对热点 Key 加随机前缀打散
- **小文件合并**：使用 `CombineFileInputFormat` 减少 Map Task 数量
- **调整 Spill**：增大 `io.sort.mb` 减少 Spill 次数

---

## 三、YARN 调度

Yet Another Resource Negotiator（YARN）是 Hadoop 2.x 引入的资源管理器，将资源管理与计算框架解耦，使 Hadoop 集群可同时运行 MapReduce、Spark、Flink 等多种计算引擎。

### 3.1 架构

```
┌──────────────┐
│  ResourceManager  │  全局资源管理
│  ├─ Scheduler     │  调度器（FIFO/Capacity/Fair）
│  └─ AppManager    │  应用管理器
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ NodeManager │ │ NodeManager │  节点级资源管理
│  (Container)│ │  (Container)│  运行具体任务
└────────┘ └────────┘
```

### 3.2 容量调度器配置（capacity-scheduler.xml）

```xml
<configuration>
  <!-- 定义多租户队列 -->
  <property>
    <name>yarn.scheduler.capacity.root.queues</name>
    <value>production,development,streaming</value>
  </property>

  <property>
    <name>yarn.scheduler.capacity.root.production.capacity</name>
    <value>60</value> <!-- 60% 资源 -->
  </property>
  <property>
    <name>yarn.scheduler.capacity.root.development.capacity</name>
    <value>20</value>
  </property>
  <property>
    <name>yarn.scheduler.capacity.root.streaming.capacity</name>
    <value>20</value>
  </property>

  <!-- 允许弹性扩展 -->
  <property>
    <name>yarn.scheduler.capacity.root.production.maximum-capacity</name>
    <value>80</value> <!-- 最多抢占到 80% -->
  </property>
</configuration>
```

### 3.3 调度器对比

| 特性 | FIFO | Capacity | Fair |
|------|------|----------|------|
| 公平性 | 无 | 容量配额保证 | 动态公平分配 |
| 多租户 | 不支持 | 支持 | 支持 |
| 资源利用率 | 低 | 中 | 高 |
| 适用场景 | 小集群 | 生产（多部门） | 交互查询多 |

---

## 四、Hive SQL

Hive 构建在 HDFS 之上，提供类 SQL 查询接口，将 SQL 自动翻译为 MapReduce / Tez / Spark 作业。

### 4.1 数据模型

| 类型 | 说明 | 存储位置 |
|------|------|----------|
| **内部表（MANAGED）** | Hive 管理元数据与数据 | `/user/hive/warehouse/` |
| **外部表（EXTERNAL）** | Hive 只管理元数据 | 自定义 HDFS 路径 |
| **分区表** | 按列值分目录存储 | 提升查询性能 |
| **分桶表** | 按列 Hash 分文件 | 便于采样与 JOIN 优化 |

### 4.2 DDL 示例

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS analytics
COMMENT 'Analytics tables'
LOCATION '/user/hive/analytics';

-- 创建分区外部表
CREATE EXTERNAL TABLE IF NOT EXISTS analytics.user_events (
    event_id     STRING,
    user_id      BIGINT,
    event_type   STRING,
    event_time   TIMESTAMP,
    properties   MAP<STRING, STRING>
)
PARTITIONED BY (dt STRING, hour STRING)
ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    COLLECTION ITEMS TERMINATED BY ','
    MAP KEYS TERMINATED BY ':'
STORED AS ORC
LOCATION '/data/events/user_events'
TBLPROPERTIES ('orc.compress'='SNAPPY');

-- 修复分区
MSCK REPAIR TABLE analytics.user_events;

-- 创建分桶表（用于优化 JOIN）
CREATE TABLE analytics.user_profile_bucketed (
    user_id   BIGINT,
    age       INT,
    gender    STRING,
    country   STRING
)
CLUSTERED BY (user_id) INTO 64 BUCKETS
STORED AS ORC;
```

### 4.3 查询优化示例

```sql
-- 开启向量化执行
SET hive.vectorized.execution.enabled = true;
SET hive.vectorized.execution.reduce.enabled = true;

-- 启用 CBO（基于成本的优化）
SET hive.cbo.enable = true;
SET hive.compute.query.using.stats = true;
SET hive.stats.fetch.column.stats = true;

-- 开启 MapJoin（小表广播到 Map 端）
SET hive.auto.convert.join = true;
SET hive.auto.convert.join.noconditionaltask.size = 100000000; -- 100MB

-- 执行引擎切换到 Tez/Spark
SET hive.execution.engine = tez;

-- 使用窗口函数替代自连接
SELECT
    user_id,
    event_date,
    COUNT(*) OVER (PARTITION BY user_id ORDER BY event_date
                   ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d_events
FROM analytics.user_events
WHERE dt >= '2026-06-01';
```

### 4.4 性能优化最佳实践

1. **分区裁剪**：查询始终带分区条件 `WHERE dt = '2026-06-28'`
2. **列裁剪**：避免 `SELECT *`，只选必要列
3. **文件格式**：使用 ORC + Snappy / Parquet
4. **执行引擎**：生产环境使用 Tez 或 Spark
5. **JOIN 优化**：小表 JOIN 大表用 MapJoin；大表 JOIN 大表用分桶
6. **合理分区粒度**：日分区为主，小时分区为辅，避免过度分区

---

## 五、HBase

HBase 是基于 HDFS 的 NoSQL 列式数据库，支持 PB 级数据的随机实时读写。

### 5.1 数据模型

| 概念 | 说明 |
|------|------|
| **Row Key** | 主键，数据按 RowKey 字典序排序存储 |
| **Column Family** | 列族，定义时声明，一个表一般不超过 3 个 |
| **Column Qualifier** | 列限定符，运行时动态添加 |
| **Cell** | 单元格，由 `RowKey + CF + CQ + Timestamp` 唯一确定 |
| **Region** | 数据分片单位，按 RowKey 范围划分 |

### 5.2 Java API 示例

```java
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.util.Bytes;

import java.io.IOException;

public class HBaseDemo {

    private static Connection connection;

    static {
        Configuration config = HBaseConfiguration.create();
        config.set("hbase.zookeeper.quorum", "zk1:2181,zk2:2181,zk3:2181");
        try {
            connection = ConnectionFactory.createConnection(config);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    /** 建表 */
    public static void createTable() throws IOException {
        Admin admin = connection.getAdmin();
        TableName tableName = TableName.valueOf("user_events");
        if (admin.tableExists(tableName)) return;

        TableDescriptorBuilder tableDesc = TableDescriptorBuilder.newBuilder(tableName);
        ColumnFamilyDescriptor cf = ColumnFamilyDescriptorBuilder
                .newBuilder(Bytes.toBytes("info"))
                .setMaxVersions(3)                    // 保留3个版本
                .setTimeToLive(7776000)               // TTL: 90天
                .setCompressionType(
                    org.apache.hadoop.hbase.io.compress.Compression.Algorithm.SNAPPY)
                .setBloomFilterType(
                    org.apache.hadoop.hbase.regionserver.BloomType.ROW)
                .build();
        tableDesc.setColumnFamily(cf);
        admin.createTable(tableDesc.build());
        admin.close();
    }

    /** 批量写入（BufferedMutator，高性能） */
    public static void batchPut() throws IOException {
        BufferedMutatorParams params = new BufferedMutatorParams(
                TableName.valueOf("user_events"));
        params.writeBufferSize(4 * 1024 * 1024); // 4MB 缓冲

        try (BufferedMutator mutator = connection.getBufferedMutator(params)) {
            for (int i = 0; i < 1000; i++) {
                Put put = new Put(Bytes.toBytes("user_" + i));
                put.addColumn(
                    Bytes.toBytes("info"),
                    Bytes.toBytes("name"),
                    Bytes.toBytes("User" + i));
                mutator.mutate(put);
            }
            mutator.flush();
        }
    }

    /** Scan 查询（范围查询） */
    public static void scanRange() throws IOException {
        Table table = connection.getTable(TableName.valueOf("user_events"));
        Scan scan = new Scan();
        scan.withStartRow(Bytes.toBytes("user_100"));
        scan.withStopRow(Bytes.toBytes("user_200"));
        scan.setCaching(1000);     // 每次 RPC 预取 1000 行
        scan.setCacheBlocks(false); // 大范围扫描关闭缓存

        try (ResultScanner scanner = table.getScanner(scan)) {
            for (Result result : scanner) {
                String rowKey = Bytes.toString(result.getRow());
                String name = Bytes.toString(
                    result.getValue(Bytes.toBytes("info"), Bytes.toBytes("name")));
                System.out.println(rowKey + " => " + name);
            }
        }
    }

    public static void main(String[] args) throws Exception {
        createTable();
        batchPut();
        scanRange();
    }
}
```

### 5.3 RowKey 设计原则

1. **避免热点**：不要使用自增 ID 或时间戳作为 RowKey 前缀
2. **打散策略**：对 RowKey 做 Hash 或反转
3. **预分区**：建表时指定 Split Keys，避免 Region 自动分裂带来的性能抖动
4. **索引设计**：二级索引通过 Phoenix 或自建索引表实现

### 5.4 HBase 与 Hive 协同

| 场景 | 选型 |
|------|------|
| 离线批量分析 | Hive（SQL → MapReduce/Tez） |
| 实时点查/范围扫描 | HBase（毫秒级响应） |
| Hive 查询 HBase 数据 | 建外部表映射 `STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'` |
| 批量写入 HBase | Hive MR 作业 → HBase（Bulk Load） |

---

## 六、最佳实践汇总

### 6.1 集群规划

| 集群规模 | NameNode 内存 | 建议 |
|----------|--------------|------|
| <100 台 DN | 16-32 GB | 单 NameNode |
| 100-500 台 DN | 64-128 GB | HA + Federation |
| >500 台 DN | >128 GB | 必须做 Federation |

### 6.2 监控告警要点

- **NameNode 堆内存使用率** > 80% 告警
- **HDFS Block 丢失**：`dfsadmin -report` 监控 under-replicated blocks
- **YARN 丢心跳 NodeManager**：连续丢失 3 次告警
- **HBase RegionServer**：监控 region 数量、MemStore 大小、flush 频率

### 6.3 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| NameNode SafeMode | 副本不足 | `hdfs dfsadmin -safemode leave` |
| YARN 任务卡在 ACCEPTED | 资源不足 | 检查队列资源、调整分配 |
| Hive 查询慢 | 数据倾斜/未分区 | 查看 Explain，加分区条件 |
| HBase 热点 | RowKey 设计不当 | Salt/Hash 打散 RowKey |

---

## 相关页面

- [[Spark核心指南]] - 内存计算引擎，替代 MapReduce 的高性能方案
- [[Flink流处理指南]] - 实时流处理框架
- [[数据湖架构]] - 基于 HDFS/对象存储的现代数据湖方案
- [[数据中台架构]] - 数据采集与治理的顶层设计
- [[Kafka消息队列]] - 大数据管道核心组件

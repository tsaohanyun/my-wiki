---
title: 企业级大数据技术体系
created: 2026-05-04
updated: 2026-05-04
type: concept
tags: [infra, storage, database, framework, architecture]
sources: [raw/articles/bigdata-development-basics.md]
---

# 企业级大数据技术体系

大数据开发基础技术，涵盖 Hadoop/Spark 技术栈、分布式文件系统 HDFS 等核心技术。^[raw/articles/bigdata-development-basics.md]

## 大数据产生背景

大数据技术源于互联网行业蓬勃发展，用户量和数据量激增。2013年国内互联网公司数据规模：
- **百度**：数据总量近 1000PB，网页数量几千亿
- **腾讯**：约 8 亿用户，总存储数据量约 100PB，日新增 200-300TB
- **阿里巴巴**：总体数据量 100PB，每天活跃数据量超 50TB

## 应用场景

- **互联网**：搜索引擎、推荐系统（亚马逊 35% 销售来自推荐）、广告系统
- **电信**：网络管理优化、精准营销、客户关系管理、企业运营管理、数据商业化
- **医疗**：临床数据对比、药品研发、临床决策支持、远程病人数据分析
- **金融**：客户画像、精准营销、风险管控（反欺诈）、运营优化

## 企业级大数据技术框架（六层）

1. **数据收集层** — 对接数据源，近实时/实时收集。需具备扩展性、可靠性、安全性、低延迟
2. **数据存储层** — 海量结构化与非结构化数据存储，需线性扩展性、容错性、多存储模型支持
3. **资源管理与服务协调层** — 共享集群模式，提高资源利用率、降低运维成本、实现数据共享；服务协调组件（Leader选举、命名、分布式队列/锁等）
4. **计算引擎层** — 批处理（高吞吐率）vs 实时计算（低延迟），不同场景不同引擎
5. **数据分析层** — 数据挖掘、统计分析、机器学习
6. **数据可视化层** — 分析结果的可视化呈现

## 大数据技术栈

### Google 大数据技术栈
- Google File System（GFS）— 分布式文件系统
- MapReduce — 分布式计算框架
- Bigtable — 分布式结构化数据存储
- Spanner — 全球分布式数据库

### Hadoop 与 Spark 开源技术栈
- **HDFS**（Hadoop Distributed File System）— 分布式文件存储
- **YARN**（Yet Another Resource Negotiator）— 资源管理与调度
- **MapReduce** — 分布式批处理计算
- **Spark** — 内存计算引擎，支持批处理、流处理、SQL、ML

## 大数据架构：Lambda Architecture

Lambda Architecture 将数据处理分为**批处理层**（Batch Layer）和**流处理层**（Speed Layer），融合离线与实时数据处理：
- 批处理层：处理全量数据，保证数据准确性
- 流处理层：处理实时增量数据，保证低延迟
- 服务层：合并批处理和流处理结果，对外提供服务

## 分布式文件系统 HDFS

### 概念
- **文件级别分布式系统**：以完整文件为单位分布存储
- **块级别分布式系统**：将文件切分成固定大小的数据块分布存储（如 HDFS 默认 128MB/块）

### HDFS 基本架构
- **NameNode**：管理文件系统元数据（命名空间、文件块映射）
- **DataNode**：存储实际数据块
- **Secondary NameNode**：辅助 NameNode 合并编辑日志

### 关键技术
1. **容错性设计** — 数据块多副本（默认3副本），节点故障自动恢复
2. **副本放置策略** — 机架感知，第一副本本地，第二副本同机架不同节点，第三副本不同机架
3. **异构存储介质** — 支持 RAM_DISK、SSD、DISK、ARCHIVE 等多种存储级别
4. **集中式缓存管理** — 将热点数据缓存在堆外内存中，加速读取

### 访问方式
- **HDFS Shell** — 命令行操作（cat, ls, put, get, mkdir, rm 等）
- **HDFS API** — Java/Python 等编程接口
- **数据收集组件** — Flume、Sqoop 等
- **计算引擎** — MapReduce、Spark 直接读写 HDFS

相关概念：[[big-data-governance]]、[[data-visualization-selection]]

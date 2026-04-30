---
source_url: file://trans-import/02b_NL2SQL精确映射方案.md
ingested: 2026-04-30
sha256: decf4c96f6606a723994f46508165fc8b6c08abcda14e94742064d811df71d38
---

# 自然语言到 SQL 语句的精准映射实现方案

要做“自然语言 → SQL”的**精准映射**，核心不是单纯让大模型直接生成 SQL，而是要把它做成一个**受约束的 Text2SQL 系统**。  
如果你目标是“精准”，重点要放在这四件事：

## 1. 先把问题拆清楚：你要的“精准”到底指什么

通常有 4 层：

1. **语义理解准**  
   用户说“上个月华东区销量最高的前10个客户”，系统能正确理解：
   - 时间：上个月
   - 区域：华东区
   - 指标：销量
   - 排序：降序
   - 数量：前10

2. **字段映射准**  
   “销量”到底映射到 `sales_amt`、`order_amount` 还是 `ship_amount`  
   “客户”到底是 `customer_name` 还是 `cust_id`

3. **SQL语法和方言准**  
   MySQL / PostgreSQL / Hive / SparkSQL / Oracle 的日期函数、limit、group by 都可能不同

4. **结果可执行且可信**  
   生成的 SQL 能跑，结果不歪，不会误查、不漏查

---

## 2. 精准映射的推荐架构

不要直接：

> 用户问题 -> LLM -> SQL

而要改成：

> 用户问题 -> 语义解析 -> Schema召回 -> 字段/指标映射 -> SQL生成 -> SQL校验 -> 执行/反馈

推荐分成 6 层：

### 第一层：语义解析层
把自然语言抽成结构化意图，例如：

用户：

> 查询2025年Q1华南区域销售额前5的产品

解析成：

```json
{
  "metric": "销售额",
  "dimensions": ["产品"],
  "filters": {
    "区域": "华南",
    "时间": "2025Q1"
  },
  "sort": {
    "field": "销售额",
    "order": "desc"
  },
  "limit": 5
}
```

这一步的意义是：  
**先做业务语义理解，再做SQL生成**，准确率会高很多。

### 第二层：Schema 检索层
要让模型知道它只能在“相关表”里选。

比如库里有 300 张表，不要全喂给模型。  
要先做 schema recall：

- 召回相关表
- 召回相关字段
- 召回字段注释
- 召回指标口径说明
- 召回 join 关系

比如对“销售额、产品、区域、Q1”召回：

- `fact_sales_order`
- `dim_product`
- `dim_region`
- `dim_date`

以及字段：

- `fact_sales_order.sales_amount`
- `fact_sales_order.product_id`
- `dim_product.product_name`
- `dim_region.region_name`
- `dim_date.quarter`

这一步本质上是 **RAG for SQL**。

### 第三层：术语映射层
这是“精准”的关键。

因为用户说的是业务词，不是数据库字段名。  
你需要建立一份**业务语义字典**，例如：

| 用户词 | 标准业务词 | 字段/表达式 |
|---|---|---|
| 销量 | 销售数量 | `sum(sale_qty)` |
| 销售额 | 含税销售额 | `sum(sales_amount)` |
| 客户 | 客户名称 | `customer_name` |
| 下单客户数 | 去重客户数 | `count(distinct customer_id)` |
| 上月 | 上个月 | 动态时间表达式 |

这个字典最好包括：

- 同义词
- 别名
- 指标定义
- 过滤维度定义
- 时间口径
- 枚举值映射

例如：

```json
{
  "销售额": {
    "type": "metric",
    "sql": "sum(f.sales_amount)",
    "table": "fact_sales_order"
  },
  "华东": {
    "type": "dimension_value",
    "field": "r.region_name",
    "value": "华东区"
  }
}
```

### 第四层：受约束 SQL 生成层
这一层不要让模型自由发挥，要给它**严格约束**。

#### 约束内容包括：
1. 只允许使用召回到的表和字段
2. 必须遵守 join 路径
3. 指标必须从指标字典里选
4. 时间条件必须标准化
5. 输出固定 JSON 或 SQL 模板

例如要求模型先输出中间结构：

```json
{
  "tables": ["fact_sales_order", "dim_product", "dim_region", "dim_date"],
  "select": [
    {"field": "p.product_name", "alias": "产品"},
    {"expr": "sum(f.sales_amount)", "alias": "销售额"}
  ],
  "joins": [
    "f.product_id = p.product_id",
    "f.region_id = r.region_id",
    "f.date_id = d.date_id"
  ],
  "where": [
    "r.region_name = '华南'",
    "d.year = 2025",
    "d.quarter = 1"
  ],
  "group_by": ["p.product_name"],
  "order_by": ["销售额 desc"],
  "limit": 5
}
```

再由程序把这个 JSON 渲染成 SQL。  
这样比直接让模型吐 SQL 更稳。

### 第五层：SQL 校验层
生成后一定要校验。

校验分 4 类：

#### 1）语法校验
用 SQL parser，比如：

- Apache Calcite
- sqlglot
- JSQLParser

#### 2）Schema 校验
检查：
- 表是否存在
- 字段是否存在
- join 是否合法
- 聚合和 group by 是否匹配

#### 3）业务规则校验
比如：
- “销售额”必须 `sum(sales_amount)`
- “客户数”必须 `count(distinct customer_id)`
- 禁止 `select *`

#### 4）风险校验
比如：
- 没有 where 时禁止全表扫描
- 涉及敏感表要拦截
- delete/update 默认禁用

### 第六层：执行反馈层
精准系统一定要有“纠错回路”。

比如 SQL 执行失败后，不是直接报错，而是把错误回传给模型做修复：

> Unknown column 'region'

模型再基于：
- 错误信息
- 当前 schema
- 原始用户问题

进行第二次修正。

这叫 **self-correction**，Text2SQL 里很常见。

---

## 3. 真正提升精准度的关键手段

### 方法一：不要全靠大模型，先做规则化抽取
比如对这些内容优先规则化：

- 时间表达式：昨天、上月、近7天、2024Q4
- 排序：前10、最高、最低
- TopN：前5、top 20
- 聚合词：总数、平均、最大、最小
- 比较词：大于、小于、介于

因为这些规则很稳定，规则抽取比纯 LLM 更准。

### 方法二：给每个字段补充“业务描述”
比如数据库字段是：

```sql
cust_no
amt
dt
```

模型很难懂。  
你要补一份元数据：

```json
{
  "cust_no": "客户编号",
  "amt": "订单含税金额",
  "dt": "订单日期"
}
```

最好每张表都做：

- 表说明
- 字段中文名
- 字段含义
- 枚举值解释
- 示例数据
- join键说明

这对准确率提升非常明显。

### 方法三：建立“指标层”而不是直接面向原始表
如果你直接让模型操作底层明细表，很容易乱。

更好的做法是先做一层语义模型，类似 BI 的指标层：

- 指标定义
- 维度定义
- 时间口径
- join关系
- 可用过滤条件

例如：

```yaml
metric: 销售额
expr: sum(f.sales_amount)

metric: 客户数
expr: count(distinct f.customer_id)

dimension: 区域
field: r.region_name
```

这样模型其实是在“指标语义层”上生成查询，而不是在裸表上瞎拼。

### 方法四：Few-shot 示例要按领域分类
给模型喂示例时，不要随便给，要按业务域组织：

- 销售分析类
- 库存分析类
- 财务分析类
- 用户分析类

而且每个示例都要包含：

- 用户问题
- 相关表
- 映射理由
- 标准 SQL

示例越像真实业务问法，命中率越高。

### 方法五：把“歧义”显式暴露
比如用户说：

> 查一下本月订单

歧义点可能有：
- 订单数？
- 订单金额？
- 明细还是汇总？
- 按天还是按客户？

精准系统不要默认乱猜。  
可以让模型输出“歧义标记”：

```json
{
  "intent": "订单查询",
  "ambiguities": [
    "指标未明确：订单数/订单金额",
    "粒度未明确：明细/按天汇总"
  ]
}
```

如果你不想每次都追问，也可以配置默认策略：
- “订单”默认指订单数
- “查询订单明细”才返回明细表
- “趋势”默认按天聚合

---

## 4. 一个可落地的工程方案

如果你现在要做系统，我建议你这样设计：

### A. 元数据中心
维护：

- 表名
- 字段名
- 字段中文解释
- 主外键
- join 关系
- 指标定义
- 维度定义
- 同义词词典
- 敏感字段标记

可以存到：
- MySQL
- Elasticsearch
- 向量库
- YAML/JSON 配置中心

### B. 检索模块
输入用户问题，召回：

- 相关表
- 相关字段
- 相关指标
- 相关示例 SQL

技术可以用：

- BM25 关键词召回
- 向量召回
- 混合召回
- rerank 重排

### C. NL2DSL 模块
先把自然语言变成 DSL，而不是直接 SQL。

例如：

```json
{
  "query_type": "aggregation",
  "metric": "销售额",
  "group_by": ["产品"],
  "filters": [
    {"field": "区域", "op": "=", "value": "华南"},
    {"field": "时间", "op": "between", "value": ["2025-01-01", "2025-03-31"]}
  ],
  "sort": [{"field": "销售额", "order": "desc"}],
  "limit": 5
}
```

### D. DSL2SQL 模块
程序化转换，不完全依赖模型。

优点：
- 可控
- 可校验
- 易 debug
- 好维护

### E. 校验与修复模块
- SQL Parser 校验
- 库表字段 existence 校验
- 执行 explain 校验
- 错误重试修复

### F. 结果解释模块
除了给 SQL，还给用户解释：

- 识别到的指标是什么
- 过滤条件是什么
- 使用了哪些表
- 为什么这样映射

这样用户更信任，也方便纠错。

---

## 5. 推荐的提示词思路

你给模型的 prompt 不应该只说：

> 帮我把自然语言转成 SQL

而应当像这样约束：

```text
你是一个企业数据分析 SQL 生成助手。

要求：
1. 只能使用提供的表、字段、指标定义
2. 优先复用标准指标，不要自行创造口径
3. 如果用户词语有歧义，先输出歧义项
4. 时间表达式要转成标准日期范围
5. 输出 JSON，不要直接输出 SQL

输入：
- 用户问题
- 可用表结构
- 字段注释
- 指标定义
- 示例映射

输出格式：
{
  "intent": "",
  "tables": [],
  "metrics": [],
  "dimensions": [],
  "filters": [],
  "sort": [],
  "limit": null,
  "ambiguities": []
}
```

然后第二步再把 JSON 转 SQL。

---

## 6. 技术选型建议

如果你是 Java / Spring Boot 体系，可以这样搭：

### 后端
- Spring Boot：统一 API / 路由 / 权限 / 审计
- Python 服务：LLM 推理 / rerank / embedding
- Redis：缓存 schema 和映射结果
- MySQL / PostgreSQL：存元数据和指标字典
- Elasticsearch：关键词召回
- Milvus / pgvector：向量召回

### 解析与生成
- LLM：做语义理解、歧义识别、DSL生成、错误修复
- sqlglot / Calcite：做 SQL 解析和校验
- Jinja2 / 程序模板：DSL 渲染 SQL

### 数据治理
- dbt 或自定义语义层
- 数据血缘与指标口径平台

---

## 7. 一个最小可用版本怎么做

如果你先做 MVP，可以按这个顺序：

### 第一步
先只支持一个业务域，比如“销售分析”。

### 第二步
整理 3 份核心资产：
- 表结构说明
- 指标字典
- 20~50 条高质量问句-SQL 样本

### 第三步
流程先做成：

> 用户问题 -> 检索相关 schema -> LLM 生成 DSL -> 程序渲染 SQL -> SQL 校验 -> 返回结果

### 第四步
上线后收集：
- 用户原问题
- 生成 SQL
- 执行是否成功
- 用户是否修正过
- 哪类字段最易映射错

再持续迭代词典和示例。

---

## 8. 最容易失败的点

你提前避开这几个坑：

### 坑1：把全库 schema 全喂给模型
会导致：
- 上下文太大
- 误选表字段
- 准确率下降

### 坑2：没有统一指标口径
“销售额”“GMV”“订单金额”混在一起，模型肯定乱

### 坑3：直接生成 SQL，不做中间结构
出了错很难定位是理解错、映射错还是拼接错

### 坑4：没有结果校验
模型生成看起来像对，其实业务上是错的

### 坑5：缺少中文业务别名体系
企业里最常错的不是 SQL 语法，而是**业务词到字段的映射**

---

## 9. 最终建议

如果你的目标是“精准映射”，最佳实践就是：

**规则抽取 + 语义字典 + Schema/RAG召回 + LLM生成DSL + 程序化SQL渲染 + SQL校验修复**

一句话概括：

**不要做“自由生成 SQL”，要做“受约束的语义映射系统”。**

---

## 后续可以继续扩展的内容

1. Spring Boot + Python 的 NL2SQL 架构图
2. 一套可直接用的 Prompt 模板
3. 一个 DSL 设计样例
4. 一个销售域的完整 Demo（自然语言 -> DSL -> SQL）

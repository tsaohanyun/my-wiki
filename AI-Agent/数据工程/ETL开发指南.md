---
title: ETL开发指南
aliases:
  - ETL Development Guide
  - 数据抽取转换加载
  - ETL管道开发
tags:
  - data-engineering
  - etl
  - airflow
  - dbt
  - data-pipeline
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: internal
difficulty: intermediate
project: AI-Agent
---

# ETL开发指南

> 本指南涵盖 ETL（Extract-Transform-Load）开发的核心概念、工具选型、最佳实践及代码示例，重点关注 **Apache Airflow** 编排与 **dbt** 转换。

---

## 目录

- [1. ETL 概述](#1-etl-概述)
- [2. 数据抽取](#2-数据抽取extract)
- [3. 数据转换](#3-数据转换transform)
- [4. 数据加载](#4-数据加载load)
- [5. Apache Airflow 编排](#5-apache-airflow-编排)
- [6. dbt 转换层](#6-dbt-转换层)
- [7. 最佳实践](#7-最佳实践)
- [8. 相关页面](#8-相关页面)

---

## 1. ETL 概述

ETL 是数据工程的核心流程，将数据从源系统抽取出来，经过清洗和转换，最终加载到目标存储（数据仓库 / 数据湖）。

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Source   │ ──▶ │ Transform │ ──▶ │  Target   │
│ (Extract) │     │           │     │  (Load)   │
└──────────┘     └──────────┘     └──────────┘
   MySQL            Python/dbt        Snowflake
   API              Spark             BigQuery
   CSV/S3           SQL               Redshift
```

### ELT vs ETL

| 特性       | ETL                          | ELT                          |
| ---------- | ---------------------------- | ---------------------------- |
| 转换位置   | 独立引擎（Spark / Python）    | 目标数据库内（SQL）          |
| 适用场景   | 复杂转换、隐私脱敏            | 大规模数据、云数据仓库       |
| 代表工具   | Informatica, DataStage        | dbt, Snowflake, BigQuery     |

---

## 2. 数据抽取（Extract）

### 2.1 从数据库抽取（CDC 增量抽取）

```python
import pymysql
from datetime import datetime, timedelta

def extract_incremental(table_name: str, last_sync_time: str, batch_size: int = 5000):
    """基于更新时间戳的增量抽取"""
    connection = pymysql.connect(
        host="source-db.internal",
        user="etl_user",
        password="***",
        database="production",
        cursorclass=pymysql.cursors.SSCursor  # 流式游标，避免内存溢出
    )

    query = f"""
        SELECT id, user_id, event_type, payload, updated_at
        FROM {table_name}
        WHERE updated_at > %s
        ORDER BY updated_at
        LIMIT %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (last_sync_time, batch_size))
        columns = [desc[0] for desc in cursor.description]
        for row in cursor:
            yield dict(zip(columns, row))

    connection.close()
```

### 2.2 从 REST API 抽取

```python
import requests
import pandas as pd
from typing import Iterator

def extract_api_data(
    endpoint: str,
    params: dict,
    auth_token: str,
    page_size: int = 100
) -> Iterator[pd.DataFrame]:
    """分页抽取 API 数据"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    offset = 0

    while True:
        params.update({"offset": offset, "limit": page_size})
        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        records = data.get("results", [])

        if not records:
            break

        yield pd.DataFrame(records)
        offset += page_size

        if len(records) < page_size:
            break
```

---

## 3. 数据转换（Transform）

### 3.1 Python Pandas 转换

```python
import pandas as pd
import numpy as np

def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """订单数据清洗与转换"""
    # 去重
    df = df.drop_duplicates(subset=["order_id"])

    # 类型转换
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # 空值处理
    df["amount"] = df["amount"].fillna(0)
    df["customer_name"] = df["customer_name"].fillna("Unknown")

    # 派生字段
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["amount_bucket"] = pd.cut(
        df["amount"],
        bins=[0, 100, 1000, 10000, np.inf],
        labels=["micro", "small", "medium", "large"]
    )

    # 数据脱敏
    df["customer_email"] = df["customer_email"].apply(
        lambda x: x.split("@")[0][:2] + "***@" + x.split("@")[1] if pd.notna(x) else x
    )

    return df
```

### 3.2 PySpark 大规模转换

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType

spark = SparkSession.builder \
    .appName("etl_transform") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

def transform_with_spark(input_path: str, output_path: str):
    df = spark.read.parquet(input_path)

    result = (
        df
        .dropDuplicates(["order_id"])
        .withColumn("order_date", F.to_date("order_date"))
        .withColumn("amount", F.col("amount").cast(DecimalType(18, 2)))
        .fillna({"amount": 0, "customer_name": "Unknown"})
        .withColumn("order_month", F.date_format("order_date", "yyyy-MM"))
        .withColumn(
            "amount_bucket",
            F.when(F.col("amount") <= 100, "micro")
             .when(F.col("amount") <= 1000, "small")
             .when(F.col("amount") <= 10000, "medium")
             .otherwise("large")
        )
    )

    # 分区写入
    result.write \
        .partitionBy("order_month") \
        .mode("overwrite") \
        .parquet(output_path)

    spark.stop()
```

---

## 4. 数据加载（Load）

### 4.1 批量加载到数据仓库

```python
from snowflake.connector import connect
import pandas as pd
from io import StringIO

def load_to_snowflake(df: pd.DataFrame, table_name: str, sf_config: dict):
    """通过 COPY FROM STAGE 高效加载"""
    conn = connect(**sf_config)
    cursor = conn.cursor()

    # 1. 写入 CSV 到内部 stage
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False, header=False)
    csv_buffer.seek(0)

    cursor.execute(f"PUT file://stage_temp @{table_name}_stage OVERWRITE = TRUE")
    # 或使用 Python Connector 的 write_pandas
    from snowflake.connector.pandas_tools import write_pandas
    write_pandas(conn, df, f"{table_name.upper()}")

    cursor.close()
    conn.close()
```

### 4.2 使用 COPY INTO 加载

```sql
-- Snowflake COPY INTO 加载
COPY INTO raw.orders
FROM @s3_stage/orders/
FILE_FORMAT = (TYPE = PARQUET)
PATTERN = '.*orders.*\\.parquet'
ON_ERROR = 'CONTINUE';
```

---

## 5. Apache Airflow 编排

### 5.1 DAG 定义

```python
# dags/etl_orders_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.sql import SQLCheckOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime, timedelta
import pendulum

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
}

with DAG(
    dag_id="etl_orders_pipeline",
    default_args=default_args,
    description="每日订单 ETL 管道",
    schedule_interval="0 2 * * *",           # 每天凌晨 2 点
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Shanghai"),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "orders", "daily"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_orders",
        python_callable=extract_incremental,
        op_kwargs={
            "table_name": "orders",
            "last_sync_time": "{{ ds }}",   # Airflow 宏：逻辑日期
        },
    )

    transform_task = PythonOperator(
        task_id="transform_orders",
        python_callable=transform_orders,
    )

    load_task = SnowflakeOperator(
        task_id="load_to_warehouse",
        sql="""
            COPY INTO raw.orders
            FROM @stage/orders_transformed/
            FILE_FORMAT = (TYPE = PARQUET)
        """,
        snowflake_conn_id="snowflake_default",
    )

    dbt_run = BashOperator(
        task_id="dbt_run_models",
        bash_command="cd /opt/dbt && dbt run --select staging+ --target prod",
    )

    dbt_test = BashOperator(
        task_id="dbt_test_models",
        bash_command="cd /opt/dbt && dbt test --select staging+ --target prod",
    )

    data_quality_check = SQLCheckOperator(
        task_id="quality_check_row_count",
        sql="SELECT COUNT(*) FROM analytics.fct_orders WHERE order_date = '{{ ds }}'",
        snowflake_conn_id="snowflake_default",
    )

    # 依赖关系
    extract_task >> transform_task >> load_task >> dbt_run >> dbt_test >> data_quality_check
```

### 5.2 Airflow 最佳实践

```python
# 使用 TaskFlow API（推荐）
from airflow.decorators import task, dag

@dag(schedule_interval="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def etl_orders_pipeline_v2():

    @task
    def extract(**context):
        ds = context["ds"]
        # 抽取逻辑
        return {"data_path": f"/tmp/orders_{ds}.parquet"}

    @task
    def transform(extract_result):
        # 转换逻辑
        return {"data_path": extract_result["data_path"].replace("orders", "orders_t")}

    @task
    def load(transform_result):
        # 加载逻辑
        print(f"Loaded from {transform_result['data_path']}")

    load(transform(extract()))

etl_orders_pipeline_v2()
```

---

## 6. dbt 转换层

### 6.1 项目结构

```
dbt_project/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/           # 原始层：1:1 映射源表
│   │   ├── _staging.yml
│   │   └── stg_orders.sql
│   ├── intermediate/      # 中间层：清洗、标准化
│   │   └── int_orders_enriched.sql
│   └── marts/             # 业务层：维度模型
│       ├── core/
│       │   ├── _core.yml
│       │   ├── fct_orders.sql
│       │   └── dim_customers.sql
│       └── finance/
│           └── fct_revenue.sql
├── macros/
│   └── cents_to_dollars.sql
├── tests/
│   └── assert_positive_amount.sql
└── snapshots/
    └── snap_customers.sql
```

### 6.2 Staging 模型

```sql
-- models/staging/stg_orders.sql
{{ config(
    materialized = 'view',
    tags = ['staging']
) }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),

renamed AS (
    SELECT
        -- 主键
        order_id                    AS order_id,

        -- 外键
        customer_id                 AS customer_id,

        -- 时间字段
        CAST(order_date AS DATE)    AS order_date,
        CAST(created_at AS TIMESTAMP) AS created_at,

        -- 度量
        CAST(amount AS NUMBER(18,2)) AS order_amount,
        CAST(quantity AS INTEGER)    AS quantity,

        -- 标准化
        TRIM(LOWER(status))         AS order_status

    FROM source
)

SELECT * FROM renamed
```

### 6.3 Mart 层事实表

```sql
-- models/marts/core/fct_orders.sql
{{ config(
    materialized = 'incremental',
    unique_key = 'order_id',
    incremental_strategy = 'merge',
    on_schema_change = 'sync_all_columns',
    cluster_by = ['order_date'],
    tags = ['marts', 'core']
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

final AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.customer_tier,
        o.order_date,
        o.order_amount,
        o.quantity,
        o.order_amount / NULLIF(o.quantity, 0) AS unit_price,
        o.order_status
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    {% if is_incremental() %}
    WHERE o.order_date >= (SELECT COALESCE(MAX(order_date), '1900-01-01') FROM {{ this }})
    {% endif %}
)

SELECT * FROM final
```

### 6.4 dbt 测试

```yaml
# models/marts/core/_core.yml
version: 2

models:
  - name: fct_orders
    description: "订单事实表"
    columns:
      - name: order_id
        description: "订单唯一标识"
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: order_amount
        tests:
          - not_null
          - assert_positive_amount:
              expression: ">= 0"
    tests:
      - dbt_utils.expression_is_true:
          expression: "order_amount >= 0"
```

### 6.5 自定义宏

```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name, precision=2) %}
    ROUND({{ column_name }} / 100.0, {{ precision }})
{% endmacro %}

-- 使用示例
-- SELECT {{ cents_to_dollars('revenue_cents') }} AS revenue_usd
```

### 6.6 Snapshots（缓慢变化维度）

```sql
-- snapshots/snap_customers.sql
{% snapshot snap_customers %}
{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

SELECT customer_id, customer_name, customer_tier, updated_at
FROM {{ source('raw', 'customers') }}

{% endsnapshot %}
```

---

## 7. 最佳实践

### 7.1 幂等性设计

> **核心原则**：管道可以安全地重复执行，每次产生相同结果。

```python
# 使用 MERGE 而非 INSERT，保证幂等
MERGE INTO warehouse.orders AS target
USING staging.orders AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET
    target.amount = source.amount,
    target.updated_at = source.updated_at
WHEN NOT MATCHED THEN INSERT (order_id, amount, updated_at)
    VALUES (source.order_id, source.amount, source.updated_at);
```

### 7.2 分层架构

| 层级          | 职责                           | 物化方式   |
| ------------- | ------------------------------ | ---------- |
| **Raw**       | 原始落地，不修改               | 外部表     |
| **Staging**   | 类型标准化、重命名             | View       |
| **Intermediate** | 业务逻辑计算               | 临时表     |
| **Mart**      | 面向业务的维度模型             | Table/增量 |

### 7.3 监控与告警

```python
# 使用 Airflow Callback
def alert_on_failure(context):
    """发送失败告警到 Slack"""
    task_instance = context["task_instance"]
    message = f"""
    :rotating_light: *ETL 管道失败*
    DAG: {task_instance.dag_id}
    Task: {task_instance.task_id}
    Execution Date: {context['ds']}
    Log URL: {task_instance.log_url}
    """
    send_slack_notification(message)

default_args = {
    "on_failure_callback": alert_on_failure,
}
```

### 7.4 其他关键实践

- ✅ **增量加载**优先于全量加载
- ✅ 所有外部数据进入 **Raw 层**再处理
- ✅ 使用 **数据契约（Data Contract）** 定义 schema
- ✅ 合理设置 **重试策略**（指数退避）
- ✅ 敏感数据在 **Staging 层脱敏**
- ✅ 代码纳入 **版本控制（Git）**
- ✅ CI/CD 流水线中执行 `dbt parse` 和 `dbt test`

---

## 8. 相关页面

- [[数据管道设计]] - 批处理与流处理架构
- [[数据质量监控]] - Great Expectations / Soda 集成
- [[数据仓库建模]] - 维度建模与事实表设计
- [[元数据治理]] - 数据血缘与目录管理

---

*最后更新：2026-06-28*

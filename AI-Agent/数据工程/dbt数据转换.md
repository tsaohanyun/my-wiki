---
title: dbt数据转换
aliases:
  - dbt
  - data build tool
  - dbt核心包
  - 数据转换工具dbt
tags:
  - 数据工程
  - dbt
  - 数据转换
  - ELT
  - 数据建模
type: 技术文档
status: 完成
created: 2026-06-28
updated: 2026-06-28
source: 官方文档 + 实践总结
difficulty: 中级
project: AI-Agent
---

# dbt数据转换

> dbt（data build tool）是一个基于 SQL 的数据转换工具，实现了 ELT 模式中的 Transform 层。它让分析师能够用软件工程的方法管理数据转换逻辑——版本控制、测试、文档化、复用。

## 目录

- [[#核心概念]]
- [[#项目结构]]
- [[#模型]]
- [[#测试]]
- [[#文档]]
- [[#宏]]
- [[#种子文件]]
- [[#CI/CD集成]]
- [[#最佳实践]]
- [[#相关页面]]

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **Model** | 一个 SQL 文件，编译后生成数据仓库中的视图/表 |
| **Source** | 外部数据源表（如数据库中的原始表） |
| **Seed** | CSV 文件，可加载到数据仓库中作为参考表 |
| **Macro** | Jinja 宏，可复用的 SQL 片段 |
| **Test** | 数据质量断言（如非空、唯一、引用完整性） |
| **Snapshot** | 增量捕获源表数据变化（SCD Type 2） |
| **Materialization** | 模型物化方式（view / table / incremental / ephemeral） |

### ELT vs ETL

```
ETL（Extract-Transform-Load）:
  数据源 → Transform（外部引擎）→ Load → 仓库
  工具：Informatica, DataStage, Spark

ELT（Extract-Load-Transform）:
  数据源 → Load → 仓库 → Transform（仓库内SQL）
  工具：dbt, Fivetran, Snowflake, BigQuery

dbt 只负责 ELT 中的 Transform 层
```

---

## 项目结构

```
my_dbt_project/
├── dbt_project.yml          ← 项目配置文件
├── profiles.yml             ← 数据库连接配置（通常在 ~/.dbt/ 下）
├── packages.yml             ← dbt 包依赖
├── .gitignore
├── README.md
├── models/
│   ├── staging/             ← Staging 层（1:1 映射源表，轻度清洗）
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   └── schema.yml       ← Staging 模型的测试和文档
│   ├── intermediate/        ← 中间层（可选）
│   │   └── int_orders_enriched.sql
│   ├── marts/               ← Mart 层（面向业务的主题模型）
│   │   ├── core/
│   │   │   ├── dim_customers.sql
│   │   │   ├── fct_orders.sql
│   │   │   └── schema.yml
│   │   └── finance/
│   │       └── fct_revenue.sql
│   └── sources.yml          ← 源表定义
├── macros/
│   ├── finance_macros.sql
│   └── date_macros.sql
├── seeds/
│   ├── country_codes.csv
│   └── exchange_rates.csv
├── snapshots/
│   └── snap_customers.sql
├── tests/
│   ├── assert_order_amount_positive.sql
│   └── assert_customer_email_format.sql
├── analyses/                ← 独立分析查询（不物化）
│   └── monthly_revenue_trend.sql
└── docs/
    └── glossary.md
```

### dbt_project.yml

```yaml
# dbt_project.yml - 项目配置
name: 'my_analytics'
version: '1.0.0'
config-version: 2

profile: 'default'  # 对应 profiles.yml 中的 profile 名称

# 模型路径配置
model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
analysis-paths: ["analyses"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"      # 编译输出目录
clean-targets:
  - "target"
  - "dbt_packages"

# 全局模型配置
models:
  my_analytics:
    +persist_docs:
      relation: true
      columns: true
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +schema: marts
      core:
        +tags: ["core", "daily"]
      finance:
        +tags: ["finance"]
        +materialized: incremental
        +incremental_strategy: merge
        +unique_key: "id"

# 全局 Seed 配置
seeds:
  my_analytics:
    +schema: reference_data
    +column_types:
      country_code: varchar(2)
      exchange_rate: float

# 全局 Snapshot 配置
snapshots:
  +target_schema: snapshots
  +invalidate_hard_deletes: true

# 变量定义
vars:
  start_date: '2024-01-01'
  default_currency: 'USD'
  tax_rate: 0.08
```

### profiles.yml

```yaml
# ~/.dbt/profiles.yml
default:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: ANALYTICS_DEV
      database: ANALYTICS_DEV
      warehouse: COMPUTE_WH
      schema: public
      threads: 8

    prod:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: ANALYTICS_PROD
      database: ANALYTICS_PROD
      warehouse: COMPUTE_WH
      schema: public
      threads: 16

    # BigQuery 配置
    bq:
      type: bigquery
      method: service-account
      keyfile: "/path/to/keyfile.json"
      project: my-project
      dataset: analytics
      threads: 8

    # PostgreSQL 配置
    pg:
      type: postgres
      host: "{{ env_var('PG_HOST') }}"
      user: "{{ env_var('PG_USER') }}"
      password: "{{ env_var('PG_PASSWORD') }}"
      port: 5432
      dbname: analytics
      schema: public
      threads: 4
```

---

## 模型

### 物化方式

```sql
-- ====== View（默认）======
-- 编译为 CREATE VIEW，不存储数据，每次查询时执行
{{ config(materialized='view') }}

SELECT * FROM {{ source('raw', 'orders') }}

-- ====== Table ======
-- 编译为 CREATE TABLE AS，存储物化结果
{{ config(materialized='table') }}

SELECT * FROM {{ ref('stg_orders') }}

-- ====== Incremental（增量）======
-- 首次运行创建全量表，后续只追加新数据
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',  -- merge / append / delete+insert
    on_schema_change='sync_all_columns'
) }}

WITH orders AS (
    SELECT * FROM {{ source('raw', 'orders') }}
    {% if is_incremental() %}
    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
    {% endif %}
)
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount,
    status
FROM orders

-- ====== Ephemeral ======
-- 编译为 CTE 嵌入到引用模型中，不创建实际对象
{{ config(materialized='ephemeral') }}

SELECT * FROM {{ ref('stg_orders') }}
WHERE status IS NOT NULL
```

### Staging 层模型

```sql
-- models/staging/stg_orders.sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('raw_app', 'orders') }}
),

renamed AS (
    SELECT
        order_id::bigint           AS order_id,
        customer_id::bigint        AS customer_id,
        UPPER(order_status)        AS status,
        CAST(created_at AS TIMESTAMP) AS created_at,
        CAST(updated_at AS TIMESTAMP) AS updated_at,
        ROUND(total_amount::numeric, 2) AS total_amount,
        currency_code::varchar(3)  AS currency,
        _loaded_at                 AS dbt_loaded_at
    FROM source
    WHERE order_id IS NOT NULL
      AND created_at IS NOT NULL
)

SELECT * FROM renamed
```

### Source 定义

```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: raw_app
    database: raw_db
    schema: app
    description: "应用程序原始数据源"
    loaded_at_field: _loaded_at
    freshness:
      warn_after: { count: 12, period: hour }
      error_after: { count: 24, period: hour }
    tables:
      - name: orders
        description: "订单原始表"
        columns:
          - name: order_id
            description: "订单唯一标识"
            tests:
              - unique
              - not_null
          - name: customer_id
            description: "客户ID"
            tests:
              - not_null
          - name: status
            description: "订单状态"
            tests:
              - accepted_values:
                  values: ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']

      - name: customers
        description: "客户原始表"
        columns:
          - name: customer_id
            tests: [unique, not_null]
          - name: email
            tests:
              - not_null
              - unique
```

### Mart 层模型

```sql
-- models/marts/core/dim_customers.sql
{{ config(
    materialized='table',
    tags=['core', 'daily']
) }}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customer_orders AS (
    SELECT
        customer_id,
        MIN(created_at) AS first_order_date,
        MAX(created_at) AS most_recent_order_date,
        COUNT(*) AS total_orders,
        SUM(total_amount) AS lifetime_value,
        AVG(total_amount) AS avg_order_value
    FROM orders
    WHERE status != 'CANCELLED'
    GROUP BY 1
),

final AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.email,
        c.phone,
        c.city,
        c.country,
        c.signup_date,
        COALESCE(co.first_order_date, NULL) AS first_order_date,
        COALESCE(co.most_recent_order_date, NULL) AS most_recent_order_date,
        COALESCE(co.total_orders, 0) AS total_orders,
        COALESCE(co.lifetime_value, 0) AS lifetime_value,
        COALESCE(co.avg_order_value, 0) AS avg_order_value,
        CASE
            WHEN co.total_orders IS NULL THEN 'NEW'
            WHEN co.most_recent_order_date < DATEADD('day', -90, CURRENT_DATE) THEN 'CHURNED'
            ELSE 'ACTIVE'
        END AS customer_segment,
        CURRENT_TIMESTAMP AS dbt_updated_at
    FROM customers c
    LEFT JOIN customer_orders co ON c.customer_id = co.customer_id
)

SELECT * FROM final
```

```sql
-- models/marts/core/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    tags=['core', 'daily']
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
),

exchange_rates AS (
    SELECT * FROM {{ ref('seed_exchange_rates') }}
    WHERE currency = 'USD'
),

final AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.country AS customer_country,
        o.created_at AS order_date,
        o.status,
        o.total_amount AS original_amount,
        o.currency,
        ROUND(
            o.total_amount * COALESCE(
                CASE o.currency
                    WHEN 'USD' THEN 1.0
                    WHEN 'EUR' THEN 1.08
                    WHEN 'GBP' THEN 1.27
                    WHEN 'JPY' THEN 0.0067
                    ELSE 1.0
                END, 1.0
            ), 2
        ) AS usd_amount,
        CASE
            WHEN o.total_amount > 1000 THEN 'HIGH'
            WHEN o.total_amount > 100 THEN 'MEDIUM'
            ELSE 'LOW'
        END AS order_tier
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
)

SELECT * FROM final
```

---

## 测试

### 通用测试（Generic Tests）

```yaml
# models/marts/core/schema.yml
version: 2

models:
  - name: dim_customers
    description: "客户维度表"
    columns:
      - name: customer_id
        description: "客户唯一标识"
        tests:
          - unique
          - not_null

      - name: email
        tests:
          - unique
          - not_null
          # 正则表达式测试（需 dbt-utils 包）
          - dbt_utils.expression_is_true:
              expression: "REGEXP_LIKE(email, '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$')"

      - name: customer_segment
        tests:
          - accepted_values:
              values: ['NEW', 'ACTIVE', 'CHURNED']

      - name: lifetime_value
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000

  - name: fct_orders
    description: "订单事实表"
    columns:
      - name: order_id
        tests: [unique, not_null]

      - name: customer_id
        tests:
          - not_null
          # 引用完整性测试
          - relationships:
              to: ref('dim_customers')
              field: customer_id

      - name: usd_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0

    # 表级测试
    tests:
      - dbt_utils.expression_is_true:
          expression: "usd_amount >= 0"

      # 自定义唯一性组合测试
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - order_id
            - customer_id
```

### 自定义测试（Singular Tests）

```sql
-- tests/assert_order_amount_positive.sql
-- 文件名即测试名，查询结果应为0行

SELECT
    order_id,
    total_amount
FROM {{ ref('fct_orders') }}
WHERE total_amount < 0
```

```sql
-- tests/assert_no_orphan_orders.sql
-- 确保没有孤立订单（无对应客户）

SELECT
    o.order_id,
    o.customer_id
FROM {{ ref('fct_orders') }} o
LEFT JOIN {{ ref('dim_customers') }} c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
```

```sql
-- tests/assert_fresh_data.sql
-- 确保数据新鲜度

SELECT *
FROM {{ ref('fct_orders') }}
WHERE order_date < DATEADD('day', -2, CURRENT_DATE())
  AND status = 'PENDING'
```

### 运行测试

```bash
# 运行所有测试
dbt test

# 运行特定模型的测试
dbt test --select dim_customers

# 运行特定测试类型
dbt test --select test_type:singular
dbt test --select test_type:generic

# 运行时选择标签
dbt test --select tag:core

# 测试特定列
dbt test --select dim_customers.customer_id
```

---

## 文档

### schema.yml 文档

```yaml
version: 2

models:
  - name: fct_orders
    description: |
      订单事实表，包含所有订单的交易记录。
      每天通过增量策略更新。

      业务定义：
      - order_tier: HIGH (>1000), MEDIUM (100-1000), LOW (<100)
      - usd_amount: 统一折算为美元的金额

    meta:
      owner: "@data_team"
      slack_channel: "#data-alerts"
      refresh_frequency: "daily"
      sla: "06:00 UTC"

    columns:
      - name: order_id
        description: "{{ doc('order_id_definition') }}"

      - name: usd_amount
        description: "订单金额（折算为美元）"
        meta:
          metrics:
            total_revenue: "SUM(usd_amount)"
            avg_order_value: "AVG(usd_amount)"

      - name: order_tier
        description: |
          订单金额分层：
          - HIGH: > $1000
          - MEDIUM: $100 - $1000
          - LOW: < $100

    # 使用块级文档引用
    config:
      meta:
        mart_owner: "Sales Analytics"
```

### 文档块（Docs Block）

```markdown
<!-- docs/glossary.md -->

{% docs order_id_definition %}
订单唯一标识符。由系统在订单创建时自动生成。
格式：ORD-YYYYMMDD-XXXXXX（例如 ORD-20240601-000001）
{% enddocs %}

{% docs customer_lifetime_value %}
客户生命周期价值（LTV），计算为客户所有有效订单的总金额。
排除已取消的订单。
{% enddocs %}
```

### 生成和查看文档

```bash
# 生成文档
dbt docs generate

# 启动本地文档服务器
dbt docs serve --port 8080

# 访问 http://localhost:8080 查看
# 包含：
#   - DAG 依赖图（可视化）
#   - 模型/源表/列的文档
#   - 测试结果
#   - 血缘关系
```

---

## 宏

### 基础宏

```sql
-- macros/cents_to_dollars.sql
-- 金额转换宏
{% macro cents_to_dollars(column_name, currency_code='USD') %}

    CASE
        WHEN '{{ currency_code }}' = 'JPY' THEN ROUND({{ column_name }} * 0.0067, 2)
        WHEN '{{ currency_code }}' = 'EUR' THEN ROUND({{ column_name }} * 1.08, 2)
        ELSE ROUND({{ column_name }} / 100.0, 2)
    END

{% endmacro %}

-- 使用
-- SELECT {{ cents_to_dollars('amount', 'EUR') }} AS usd_amount
```

### 通用聚合宏

```sql
-- macros/aggregate_periods.sql
-- 按时间周期聚合的通用宏

{% macro aggregate_by_period(source_table, date_column, period='day', group_columns=[]) %}

    {%- set period_expr -%}
        {%- if period == 'hour' -%}
            DATE_TRUNC('hour', {{ date_column }})
        {%- elif period == 'day' -%}
            DATE_TRUNC('day', {{ date_column }})
        {%- elif period == 'week' -%}
            DATE_TRUNC('week', {{ date_column }})
        {%- elif period == 'month' -%}
            DATE_TRUNC('month', {{ date_column }})
        {%- elif period == 'quarter' -%}
            DATE_TRUNC('quarter', {{ date_column }})
        {%- elif period == 'year' -%}
            DATE_TRUNC('year', {{ date_column }})
        {%- endif -%}
    {%- endset -%}

    SELECT
        {{ period_expr }} AS period_start,
        {% for col in group_columns %}
            {{ col }},
        {% endfor %}
        COUNT(*) AS record_count,
        SUM(amount) AS total_amount,
        AVG(amount) AS avg_amount,
        MIN(amount) AS min_amount,
        MAX(amount) AS max_amount
    FROM {{ source_table }}
    GROUP BY {{ period_expr }}
    {% for col in group_columns %}
        , {{ col }}
    {% endfor %}

{% endmacro %}
```

### 增量过滤宏

```sql
-- macros/incremental_filter.sql
-- 标准化增量过滤条件

{% macro incremental_last_n_days(column_name, days=1) %}

    {% if is_incremental() %}
        {{ column_name }} > (
            SELECT COALESCE(
                MAX({{ column_name }}),
                DATEADD('day', -{{ days }}, CURRENT_DATE())
            )
            FROM {{ this }}
        )
    {% endif %}

{% endmacro %}

-- 使用
-- SELECT * FROM {{ source('raw', 'events') }}
-- WHERE {{ incremental_last_n_days('created_at', 7) }}
```

### 数据质量宏

```sql
-- macros/audit.sql
-- 数据审计宏

{% macro audit_row_count(model_name) %}

    SELECT
        '{{ model_name }}' AS model_name,
        '{{ run_started_at }}' AS run_time,
        COUNT(*) AS row_count
    FROM {{ ref(model_name) }}

{% endmacro %}

-- macros/generate_schema_name.sql
-- 自定义 Schema 命名规则
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ target.schema }}_{{ custom_schema_name | lower }}
    {%- endif -%}

{%- endmacro %}
```

---

## 种子文件

Seed 文件是将 CSV 加载到数据仓库的简便方式，适合小型参考数据。

```csv
<!-- seeds/country_codes.csv -->
country_code,country_name,region,continent
US,United States,North America,Americas
CN,China,East Asia,Asia
JP,Japan,East Asia,Asia
DE,Germany,Western Europe,Europe
GB,United Kingdom,Northern Europe,Europe
FR,France,Western Europe,Europe
```

```yaml
# schema.yml for seeds
version: 2

seeds:
  - name: country_codes
    description: "ISO 国家代码映射表"
    config:
      column_types:
        country_code: varchar(2)
        country_name: varchar(100)
        region: varchar(50)
        continent: varchar(20)
    columns:
      - name: country_code
        tests: [unique, not_null]

  - name: exchange_rates
    description: "货币汇率参考表"
    config:
      column_types:
        currency: varchar(3)
        rate_to_usd: float
        updated_date: date
```

```bash
# 加载种子文件
dbt seed

# 只加载特定种子
dbt seed --select country_codes

# 全量刷新（覆盖）
dbt seed --full-refresh
```

---

## CI/CD集成

### GitHub Actions

```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    paths:
      - 'models/**'
      - 'macros/**'
      - 'seeds/**'
      - 'tests/**'
      - 'dbt_project.yml'
  pull_request:
    branches: [main]

env:
  DBT_VERSION: "1.7"

jobs:
  # ====== PR 检查：编译和测试 ======
  dbt_ci:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dbt
        run: |
          pip install dbt-snowflake==${{ env.DBT_VERSION }}

      - name: Install dbt dependencies
        run: dbt deps

      - name: Check model changes
        id: changed
        uses: dorny/paths-filter@v3
        with:
          filters:
            models:
              - 'models/**/*.sql'

      - name: dbt compile
        run: dbt compile --target ci
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_CI_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_CI_PASSWORD }}

      - name: Run changed models
        if: steps.changed.outputs.models == 'true'
        run: |
          # 只构建 PR 中变更的模型及其下游
          CHANGED_MODELS=$(git diff --name-only origin/${{ github.base_ref }} HEAD -- 'models/**/*.sql' | sed 's|models/||;s|\.sql$||;s|/|.|g')
          echo "Changed models: $CHANGED_MODELS"
          dbt run --select state:modified+ --target ci --state ./target

      - name: Run tests
        run: dbt test --select state:modified+ --target ci --state ./target

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: dbt-target
          path: target/

  # ====== Main 分支：生产部署 ======
  dbt_deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: []
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dbt
        run: pip install dbt-snowflake==${{ env.DBT_VERSION }}

      - name: Install dependencies
        run: dbt deps

      - name: Seed reference data
        run: dbt seed --target prod

      - name: Run models
        run: dbt run --target prod

      - name: Run tests
        run: dbt test --target prod

      - name: Generate docs
        run: dbt docs generate --target prod

      - name: Deploy docs
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./target
          publish_branch: docs-pages

      - name: Notify Slack
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          slack-message: "dbt production deployment FAILED! 🚨"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Airflow 调度 dbt

```python
# airflow DAG: dbt_pipeline.py
from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="dbt_daily_run",
    schedule="0 3 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
) as dag:

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="cd /opt/dbt && dbt deps",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command="cd /opt/dbt && dbt seed --target prod",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/dbt && dbt run --target prod --select tag:daily",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/dbt && dbt test --target prod --select tag:daily",
    )

    dbt_docs = BashOperator(
        task_id="dbt_docs",
        bash_command="cd /opt/dbt && dbt docs generate --target prod",
    )

    dbt_deps >> dbt_seed >> dbt_run >> dbt_test >> dbt_docs
```

### 使用 dbt Cloud API

```python
# 使用 dbt Cloud API 触发任务
import requests
import time

DBT_CLOUD_API = "https://cloud.getdbt.com/api/v2"
ACCOUNT_ID = "12345"
PROJECT_ID = "67890"
ENVIRONMENT_ID = "11111"
API_TOKEN = "your_api_token"

headers = {"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json"}

# 触发 dbt Cloud 任务
def trigger_dbt_job():
    response = requests.post(
        f"{DBT_CLOUD_API}/accounts/{ACCOUNT_ID}/jobs/",
        json={
            "environment_id": ENVIRONMENT_ID,
            "execute_steps": ["dbt seed", "dbt run", "dbt test"],
            "cause": "Airflow triggered",
        },
        headers=headers,
    )
    run_id = response.json()["data"]["id"]
    return run_id

# 轮询任务状态
def wait_for_completion(run_id, timeout=3600):
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(
            f"{DBT_CLOUD_API}/accounts/{ACCOUNT_ID}/runs/{run_id}/",
            headers=headers,
        )
        status = response.json()["data"]["status"]
        # 10 = Success, 20 = Error, 30 = Cancelled
        if status in [10, 20, 30]:
            return status == 10
        time.sleep(30)
    raise TimeoutError("dbt Cloud job timed out")
```

---

## 最佳实践

### 模型设计

1. **分层设计**: `Staging → Intermediate → Marts`
2. **Staging 模型只做轻转换**: 重命名、类型转换、去重
3. **业务逻辑集中在 Mart 层**: 聚合、Join、计算指标
4. **使用 `ref()` 而非硬编码表名**: dbt 自动解析依赖关系
5. **幂等模型**: 重跑产生相同结果

### 命名规范

| 层级 | 前缀 | 示例 |
|------|------|------|
| Staging | `stg_` | `stg_customers` |
| Intermediate | `int_` | `int_orders_enriched` |
| Dimension | `dim_` | `dim_customers` |
| Fact | `fct_` | `fct_orders` |
| Bridge | `bridge_` | `bridge_customer_products` |
| Snapshot | `snap_` | `snap_customers` |
| Seed | 无前缀 | `country_codes` |

### ✅ 推荐做法

| 实践 | 说明 |
|------|------|
| **使用 dbt-utils 包** | 提供大量实用宏和测试 |
| **CI 中使用 `--select state:modified+`** | 只构建变更的模型 |
| **设置数据新鲜度检查** | `freshness` 配置自动告警 |
| **为所有列添加文档** | `dbt docs generate` 的价值 |
| **增量模型设置 `unique_key`** | 保证幂等性 |
| **使用 `on_schema_change`** | 源表 Schema 变化时自动处理 |
| **变量管理环境差异** | `{{ var('start_date') }}` |

### ❌ 避免的做法

1. **避免 Staging 层做 Join 或聚合**（放在中间层）
2. **避免增量模型依赖非增量模型**（可能导致数据不一致）
3. **避免在模型中使用 `SELECT *`**（显式列出列名）
4. **避免过深的模型依赖链**（>5层考虑重构）
5. **避免在 Mart 层使用 Ephemeral 物化**（性能差）

### 性能优化

```sql
-- 1. 使用增量策略
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='id',
    on_schema_change='append_new_columns'
) }}

-- 2. 使用分区和聚簇
{{ config(
    materialized='table',
    partition_by={'field': 'order_date', 'data_type': 'date'},
    cluster_by=['customer_id', 'product_id']
) }}

-- 3. 避免在 WHERE 中使用函数（阻止索引）
-- ❌ WHERE YEAR(order_date) = 2024
-- ✅ WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'

-- 4. 使用 CTE 组织复杂查询（dbt 原生支持）
WITH a AS (...),
     b AS (...),
     final AS (...)
SELECT * FROM final
```

---

## 常用命令速查

```bash
# 基础操作
dbt run                                    # 运行所有模型
dbt run --select my_model                  # 运行指定模型
dbt run --select my_model+                 # 运行模型及其下游
dbt run --select +my_model                 # 运行模型及其上游
dbt run --select tag:daily                 # 运行指定标签
dbt run --select state:modified+           # 运行变更的模型（需 --state）
dbt run --full-refresh                     # 全量刷新增量模型

# 测试
dbt test                                   # 运行所有测试
dbt test --select my_model                 # 测试指定模型
dbt test --select test_type:singular       # 只运行单文件测试

# 种子和快照
dbt seed                                   # 加载种子文件
dbt snapshot                               # 运行快照

# 文档
dbt docs generate                          # 生成文档
dbt docs serve                             # 启动文档服务器

# 编译和调试
dbt compile                                # 编译但不运行
dbt parse                                  # 解析但不编译
dbt run --debug                            # 调试模式

# 依赖
dbt deps                                   # 安装包依赖
dbt clean                                  # 清理 target 目录

# 状态比较
dbt run --select state:modified+ --state ./prev_target
```

---

## 相关页面

- [[Airflow工作流编排]] - dbt 任务的编排与调度
- [[数据湖架构]] - dbt 与数据湖表格式的集成
- [[Spark大数据处理]] - 大规模数据转换的替代方案
- [[Flink流处理引擎]] - 实时数据转换对比

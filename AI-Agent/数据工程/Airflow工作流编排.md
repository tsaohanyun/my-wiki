---
title: Airflow工作流编排
aliases:
  - Airflow
  - Apache Airflow
  - 工作流编排
  - DAG编排
tags:
  - 数据工程
  - 工作流
  - Airflow
  - 调度
  - ETL
type: 技术文档
status: 完成
created: 2026-06-28
updated: 2026-06-28
source: 官方文档 + 实践总结
difficulty: 中级
project: AI-Agent
---

# Airflow工作流编排

> Apache Airflow 是一个开源的工作流编排平台，通过 DAG（有向无环图）来定义、调度和监控数据管道。由 Airbnb 开发，现为 Apache 顶级项目。

## 目录

- [[#核心概念]]
- [[#DAG编写]]
- [[#Operator]]
- [[#Sensor]]
- [[#XCom]]
- [[#Schedule]]
- [[#最佳实践]]
- [[#相关页面]]

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **DAG** | Directed Acyclic Graph，有向无环图，定义任务依赖关系 |
| **Task** | DAG 中的一个节点，一个具体操作 |
| **Operator** | Task 的模板，定义操作类型（如 BashOperator、PythonOperator） |
| **Task Instance** | Task 的一次具体运行 |
| **DAG Run** | DAG 的一次完整执行 |
| **Scheduler** | 调度器，负责触发 DAG Run |
| **Executor** | 执行器，决定 Task 在哪里运行（Local/Celery/K8s） |

### 架构概览

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Scheduler   │───▶│   Executor    │───▶│   Task Worker    │
│  (调度器)    │    │  (执行器)     │    │   (任务执行)      │
└─────────────┘    └──────────────┘    └─────────────────┘
       │                                          │
       ▼                                          ▼
┌─────────────┐                        ┌─────────────────┐
│  Metadata    │◀──────────────────────│   Result Store   │
│  Database    │     (状态/日志回写)    │   (结果存储)      │
└─────────────┘                        └─────────────────┘
       │
       ▼
┌─────────────┐
│   Web UI     │
│  (可视化界面) │
└─────────────┘
```

---

## DAG编写

### 基本结构

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

# 默认参数
default_args = {
    "owner": "data_team",
    "depends_on_past": False,
    "email": ["data-alerts@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=2),
}

# 创建 DAG
with DAG(
    dag_id="data_pipeline_etl",
    default_args=default_args,
    description="每日 ETL 数据管道",
    schedule_interval="0 2 * * *",  # 每天凌晨2点
    start_date=datetime(2024, 1, 1),
    catchup=False,  # 不补跑历史
    max_active_runs=1,  # 最大并发运行数
    max_active_tasks=4,  # 最大并发任务数
    tags=["etl", "production"],
    doc_md="""
    ## ETL 数据管道
    此 DAG 负责：
    1. 从数据源抽取数据
    2. 清洗转换
    3. 加载到数据仓库
    """,
) as dag:

    # 定义任务
    extract = BashOperator(
        task_id="extract_data",
        bash_command="""
            echo "Extracting data from source..."
            python /opt/airflow/scripts/extract.py --date {{ ds }}
        """,
    )

    def transform_data(**context):
        import pandas as pd
        execution_date = context["ds"]
        # 读取抽取的数据
        df = pd.read_parquet(f"/tmp/raw_data_{execution_date}.parquet")
        # 清洗和转换
        df = df.dropna()
        df["processed_date"] = execution_date
        # 保存
        df.to_parquet(f"/tmp/transformed_{execution_date}.parquet")
        return f"/tmp/transformed_{execution_date}.parquet"

    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    load = BashOperator(
        task_id="load_to_warehouse",
        bash_command="""
            echo "Loading data to data warehouse..."
            python /opt/airflow/scripts/load.py --date {{ ds }} --file {{ ti.xcom_pull(task_ids='transform_data') }}
        """,
    )

    # 设置依赖关系
    extract >> transform >> load
```

### Task Group（任务分组）

```python
with DAG(
    dag_id="complex_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    with TaskGroup(group_id="staging_layer") as staging:
        extract_users = BashOperator(task_id="extract_users", bash_command="echo 'users'")
        extract_orders = BashOperator(task_id="extract_orders", bash_command="echo 'orders'")
        extract_products = BashOperator(task_id="extract_products", bash_command="echo 'products'")

    with TaskGroup(group_id="transform_layer") as transform:
        clean_users = PythonOperator(task_id="clean_users", python_callable=lambda: print("clean"))
        clean_orders = PythonOperator(task_id="clean_orders", python_callable=lambda: print("clean"))
        enrich_orders = PythonOperator(
            task_id="enrich_orders",
            python_callable=lambda: print("enrich"),
        )

    with TaskGroup(group_id="load_layer") as load:
        load_dw = BashOperator(task_id="load_data_warehouse", bash_command="echo 'dw'")
        load_mart = BashOperator(task_id="load_data_mart", bash_command="echo 'mart'")

    # 组间依赖
    staging >> transform >> load
```

### 动态 DAG（基于配置生成）

```python
import yaml
from pathlib import Path

def load_pipeline_configs():
    config_path = Path("/opt/airflow/configs/pipelines.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

configs = load_pipeline_configs()

for config in configs["pipelines"]:
    dag_id = f"pipeline_{config['name']}"

    with DAG(
        dag_id=dag_id,
        schedule_interval=config.get("schedule", "@daily"),
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=config.get("tags", []),
    ) as dag:

        tasks = []
        for step in config["steps"]:
            task = PythonOperator(
                task_id=step["task_id"],
                python_callable=globals()[step["function"]],
                op_kwargs=step.get("params", {}),
            )
            tasks.append(task)

        # 线性依赖
        for i in range(len(tasks) - 1):
            tasks[i] >> tasks[i + 1]

    # 将 DAG 注册到全局命名空间
    globals()[dag_id] = dag
```

### 条件分支

```python
from airflow.operators.python import BranchPythonOperator

def check_data_quality(**context):
    ds = context["ds"]
    # 模拟数据质量检查
    quality_score = 0.95  # 实际从检查结果获取
    if quality_score > 0.9:
        return "proceed_to_load"
    else:
        return "send_alert"

check_quality = BranchPythonOperator(
    task_id="check_data_quality",
    python_callable=check_data_quality,
)

proceed = PythonOperator(task_id="proceed_to_load", python_callable=lambda: print("Loading..."))
alert = PythonOperator(task_id="send_alert", python_callable=lambda: print("Alerting!"))

check_quality >> [proceed, alert]
```

---

## Operator

### 常用 Operator

```python
# ====== BashOperator ======
from airflow.operators.bash import BashOperator

run_script = BashOperator(
    task_id="run_spark_job",
    bash_command="""
        cd /opt/jobs
        spark-submit \
            --master yarn \
            --deploy-mode cluster \
            --num-executors 10 \
            --executor-memory 4g \
            etl_job.py --date {{ ds }}
    """,
    env={"SPARK_HOME": "/opt/spark"},
)

# ====== PythonOperator ======
from airflow.operators.python import PythonOperator

def process_data(execution_date, **context):
    import pandas as pd
    # 业务逻辑
    result = {"date": execution_date, "rows": 10000}
    context["ti"].xcom_push(key="result", value=result)
    return result

task = PythonOperator(
    task_id="process_data",
    python_callable=process_data,
    op_kwargs={"execution_date": "{{ ds }}"},
    op_args=[],  # 位置参数
    provide_context=True,
)

# ====== SparkSubmitOperator ======
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

spark_job = SparkSubmitOperator(
    task_id="spark_etl",
    application="/opt/jobs/etl_job.py",
    conn_id="spark_default",
    conf={
        "spark.executor.memory": "4g",
        "spark.executor.cores": "2",
        "spark.dynamicAllocation.enabled": "true",
    },
    total_executor_memory="40g",
    application_args=["--date", "{{ ds }}"],
)

# ====== DockerOperator ======
from airflow.providers.docker.operators.docker import DockerOperator

docker_task = DockerOperator(
    task_id="run_ml_inference",
    image="my-registry/ml-inference:latest",
    command="--input /data/input --output /data/output",
    volumes=["/shared/data:/data"],
    docker_url="unix://var/run/docker.sock",
    network_mode="bridge",
    auto_remove=True,
)

# ====== KubernetesPodOperator ======
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

k8s_task = KubernetesPodOperator(
    task_id="k8s_data_job",
    namespace="airflow-jobs",
    image="my-registry/data-job:latest",
    cmds=["python"],
    arguments=["-m", "jobs.etl", "--date", "{{ ds }}"],
    resources={
        "request_memory": "2Gi",
        "request_cpu": "1",
        "limit_memory": "4Gi",
        "limit_cpu": "2",
    },
    config_file="/opt/airflow/kube_config.yaml",
    get_logs=True,
)

# ====== GenericTransfer（数据库迁移）======
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

sql_task = SQLExecuteQueryOperator(
    task_id="run_sql",
    conn_id="warehouse_postgres",
    sql="""
        INSERT INTO dws.daily_summary (dt, total_sales, total_orders)
        SELECT
            '{{ ds }}' as dt,
            SUM(amount) as total_sales,
            COUNT(*) as total_orders
        FROM ods.orders
        WHERE DATE(order_time) = '{{ ds }}'
        ON CONFLICT (dt) DO UPDATE SET
            total_sales = EXCLUDED.total_sales,
            total_orders = EXCLUDED.total_orders;
    """,
)
```

---

## Sensor

Sensor 用于等待某个条件满足后才继续执行。

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.python import PythonSensor
from airflow.sensors.sql import SqlSensor
from airflow.sensors.date_time import DateTimeSensor
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime

# ====== FileSensor: 等待文件出现 ======
wait_for_file = FileSensor(
    task_id="wait_for_data_file",
    filepath="/data/incoming/daily_{{ ds }}.csv",
    fs_conn_id="fs_default",
    poke_interval=60,      # 每隔60秒检查一次
    timeout=3600,          # 超时时间1小时
    mode="poke",           # poke(阻塞) 或 reschedule(释放Worker)
)

# ====== PythonSensor: 自定义条件 ======
def check_api_ready(**context):
    import requests
    response = requests.get("http://api:8080/health")
    return response.status_code == 200

wait_for_api = PythonSensor(
    task_id="wait_for_api",
    python_callable=check_api_ready,
    poke_interval=30,
    timeout=600,
    mode="reschedule",  # 推荐：不占用 Worker slot
)

# ====== SqlSensor: 等待 SQL 查询返回结果 ======
wait_for_data = SqlSensor(
    task_id="wait_for_load_complete",
    conn_id="warehouse_postgres",
    sql="""
        SELECT COUNT(*) > 0
        FROM ods.orders
        WHERE DATE(created_at) = '{{ ds }}'
    """,
    success=lambda x: x > 0,
    poke_interval=120,
    mode="reschedule",
)

# ====== ExternalTaskSensor: 等待外部 DAG 完成 ======
wait_for_upstream = ExternalTaskSensor(
    task_id="wait_for_upstream_dag",
    external_dag_id="ingestion_pipeline",
    external_task_id="final_load",  # None 则等待整个 DAG
    check_existence=True,
    poke_interval=60,
    timeout=7200,
    mode="reschedule",
    execution_delta=timedelta(hours=1),  # 上游 DAG 执行时间偏移
    # 或者使用 execution_date_fn 更灵活
    execution_date_fn=lambda exec_date: exec_date - timedelta(hours=1),
)

# ====== DateTimeSensor: 等待指定时间 ======
wait_until = DateTimeSensor(
    task_id="wait_until_target_time",
    target_time="{{ dag_run.logical_date | ts }} + 30 minutes",
    mode="reschedule",
)
```

### Sensor 模式选择

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `poke` | 阻塞 Worker slot，持续检查 | 间隔很短（<60s） |
| `reschedule` | 每次检查后释放 Worker slot | 间隔较长（推荐） |

---

## XCom

XCom（Cross-Communication）用于 Task 之间传递小量数据。

```python
from airflow.operators.python import PythonOperator

# ====== 推送数据 ======
def extract_data(**context):
    data = {"total_records": 50000, "file_path": "/data/extracted.csv"}
    # 方式1：通过 context 推送
    context["ti"].xcom_push(key="extract_result", value=data)

    # 方式2：直接返回值（自动存储为 key="return_value"）
    return data

# ====== 拉取数据 ======
def transform_data(**context):
    ti = context["ti"]

    # 方式1：显式拉取
    data = ti.xcom_pull(task_ids="extract_data", key="extract_result")

    # 方式2：拉取返回值
    data = ti.xcom_pull(task_ids="extract_data", key="return_value")

    print(f"Received: {data}")
    return {"transformed": True}

# ====== 拉取多个 Task 的数据 ======
def aggregate_results(**context):
    ti = context["ti"]

    # 拉取多个 task 的数据
    results = ti.xcom_pull(
        task_ids=["task1", "task2", "task3"],
        key="return_value",
    )
    # results 是一个列表

    # 拉取同一 DAG 的上一个运行结果
    prev_result = ti.xcom_pull(
        task_ids="transform_data",
        key="return_value",
        dag_id=context["dag"].dag_id,
        run_id=context["prev_ds"],  # 上一个运行日期
    )

# ====== 使用 Jinja 模板拉取 ======
load_task = BashOperator(
    task_id="load_task",
    bash_command="""
        FILE_PATH={{ ti.xcom_pull(task_ids='extract_data', key='extract_result')['file_path'] }}
        echo "Loading from: $FILE_PATH"
        python load.py --file $FILE_PATH
    """,
)

# ====== TaskFlow API（简化版 XCom）======
from airflow.decorators import task, dag

@dag(start_date=datetime(2024, 1, 1), schedule="@daily", catchup=False)
def taskflow_pipeline():

    @task
    def extract():
        return {"data": [1, 2, 3, 4, 5], "source": "api"}

    @task
    def transform(data):
        return [x * 2 for x in data["data"]]

    @task
    def load(transformed_data):
        print(f"Loaded: {transformed_data}")

    # 自动处理 XCom 传递
    raw_data = extract()
    processed = transform(raw_data)
    load(processed)

taskflow_pipeline()
```

> **⚠️ 注意**: XCom 不适合传递大数据。默认存储在 Metadata DB 中，序列化方式有 JSON 和 Pickle。大数据请使用外部存储（S3、HDFS、数据库），XCom 只传路径或引用。

### 自定义 XCom 后端

```python
# custom_xcom_backend.py
from airflow.models.xcom import BaseXCom
import json

class S3XComBackend(BaseXCom):
    """将大 XCom 数据存储到 S3"""
    @staticmethod
    def serialize_value(value):
        if isinstance(value, (dict, list)) and len(json.dumps(value)) > 10000:
            # 大数据存到 S3，XCom 中只存引用
            key = upload_to_s3(value)
            return BaseXCom.serialize_value({"__xcom_s3_key__": key})
        return BaseXCom.serialize_value(value)

# airflow.cfg 配置：
# [core]
# xcom_backend = custom_xcom_backend.S3XComBackend
```

---

## Schedule

### 调度表达式

```python
# ====== Cron 预设 ======
dag1 = DAG(dag_id="d1", schedule_interval="@once")       # 仅执行一次
dag2 = DAG(dag_id="d2", schedule_interval="@hourly")      # 每小时
dag3 = DAG(dag_id="d3", schedule_interval="@daily")       # 每天 00:00
dag4 = DAG(dag_id="d4", schedule_interval="@weekly")      # 每周一 00:00
dag5 = DAG(dag_id="d5", schedule_interval="@monthly")     # 每月1日 00:00
dag6 = DAG(dag_id="d6", schedule_interval="@yearly")      # 每年1月1日 00:00

# ====== Cron 表达式（分 时 日 月 周）======
dag7 = DAG(dag_id="d7", schedule_interval="0 2 * * *")           # 每天凌晨2点
dag8 = DAG(dag_id="d8", schedule_interval="*/15 * * * *")        # 每15分钟
dag9 = DAG(dag_id="d9", schedule_interval="0 9-17 * * 1-5")      # 工作日9-17点整点
dag10 = DAG(dag_id="d10", schedule_interval="0 0 1 */3 *")       # 每季度第一天
dag11 = DAG(dag_id="d11", schedule_interval="0 0 * * 6,0")       # 每周六日午夜

# ====== Timetable（Airflow 2.2+，更灵活的调度）======
from airflow.timetables.interval import CronDataIntervalTimetable

dag12 = DAG(
    dag_id="d12",
    timetable=CronDataIntervalTimetable(
        cron="0 2 * * *",
        timezone="Asia/Shanghai",
    ),
)

# ====== 数据驱动调度（Dataset，Airflow 2.4+）======
from airflow.datasets import Dataset

warehouse_data = Dataset("s3://warehouse/daily_data")

# 生产者 DAG：更新数据集
producer_dag = DAG(
    dag_id="producer",
    schedule="@daily",
    catchup=False,
    start_date=datetime(2024, 1, 1),
)

with producer_dag:
    produce = BashOperator(
        task_id="produce_data",
        bash_command="echo 'producing data'",
        outlets=[warehouse_data],  # 声明输出数据集
    )

# 消费者 DAG：数据集更新后触发
consumer_dag = DAG(
    dag_id="consumer",
    schedule=[warehouse_data],  # 数据集更新时触发
    catchup=False,
    start_date=datetime(2024, 1, 1),
)

with consumer_dag:
    consume = BashOperator(
        task_id="consume_data",
        bash_command="echo 'consuming data'",
    )
```

### 执行时间概念

```python
"""
Airflow 调度时间概念（最易混淆部分）:

logical_date / execution_date:
  - DAG 的调度时间，不是实际运行时间
  - schedule_interval="@daily", start_date=2024-01-01
  - 第一个 DAG Run 的 logical_date = 2024-01-01 00:00:00
  - 但实际运行时间 = 2024-01-02 00:00:00 (下一个 interval 结束时)

  时间轴：
  |--- 2024-01-01 (data_interval_start) ---|--- 2024-01-02 (data_interval_end / 实际运行) ---|
        logical_date = 2024-01-01
        {{ ds }} = "2024-01-01"
        {{ ds }} 代表要处理的数据日期

模板变量：
  {{ ds }}           -> "2024-01-01"  (YYYY-MM-DD)
  {{ ts }}           -> "2024-01-01T00:00:00+00:00"
  {{ data_interval_start }} -> Pendulum datetime
  {{ data_interval_end }}   -> Pendulum datetime
  {{ prev_ds }}      -> 上一个运行日期
  {{ next_ds }}      -> 下一个运行日期
  {{ run_id }}       -> DAG Run 的唯一 ID
  {{ dag_run.conf }} -> 手动触发时传入的参数
"""
```

---

## 最佳实践

### DAG 设计原则

1. **原子性**: 每个 Task 应该是可独立重试的
2. **幂等性**: 重跑同一 Task 产生相同结果
3. **快速失败**: Task 执行时间不宜过长（>1小时考虑拆分）
4. **单一职责**: 一个 DAG 聚焦一个数据管道

### 代码示例：完整生产级 DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import logging

def failure_callback(context):
    """任务失败时的回调"""
    task_instance = context["task_instance"]
    logging.error(f"Task {task_instance.task_id} failed!")
    # 发送告警到 Slack/PagerDuty
    # send_alert(task_instance, context["exception"])

def success_callback(context):
    """任务成功时的回调"""
    logging.info(f"Task completed successfully!")

default_args = {
    "owner": "data_platform",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=60),
    "on_failure_callback": failure_callback,
    "on_success_callback": success_callback,
    "email_on_failure": True,
    "email": ["data-platform-alerts@company.com"],
}

with DAG(
    dag_id="production_data_pipeline",
    default_args=default_args,
    description="Production-grade data pipeline with full monitoring",
    schedule="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=8,
    tags=["production", "etl", "v2"],
    doc_md=__doc__,
    params={
        "environment": "production",
        "alert_enabled": True,
    },
) as dag:

    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    # 等待上游 DAG
    wait_upstream = ExternalTaskSensor(
        task_id="wait_for_ingestion",
        external_dag_id="data_ingestion",
        external_task_id=None,
        check_existence=True,
        mode="reschedule",
        timeout=7200,
        poke_interval=300,
    )

    with TaskGroup("extract") as extract_group:
        extract_users = PythonOperator(
            task_id="extract_users",
            python_callable=lambda: print("Extracting users"),
        )
        extract_orders = PythonOperator(
            task_id="extract_orders",
            python_callable=lambda: print("Extracting orders"),
        )

    with TaskGroup("transform") as transform_group:
        clean_data = PythonOperator(
            task_id="clean_data",
            python_callable=lambda: print("Cleaning"),
        )
        validate = PythonOperator(
            task_id="validate_quality",
            python_callable=lambda: print("Validating"),
        )

    with TaskGroup("load") as load_group:
        load_dwh = PythonOperator(
            task_id="load_dwh",
            python_callable=lambda: print("Loading to DWH"),
        )
        update_metadata = PythonOperator(
            task_id="update_metadata",
            python_callable=lambda: print("Updating metadata"),
        )

    # 依赖关系
    start >> wait_upstream >> extract_group >> transform_group >> load_group >> end
```

### ✅ 推荐做法

| 实践 | 说明 |
|------|------|
| **使用 `.airflowignore`** | 排除不需要解析的文件，加快 Scheduler 扫描 |
| **版本控制 DAG 代码** | Git 管理 DAG 定义，CI/CD 部署 |
| **设置合理的 `catchup`** | 多数场景设为 `False`，避免历史补跑雪崩 |
| **使用 Connection/Variable** | 敏感信息存储在 Airflow 元数据库，不要硬编码 |
| **Task 幂等** | 重跑安全，使用 `UPSERT` 而非 `INSERT` |
| **监控 SLA** | 设置 `sla` 参数，超时告警 |
| **使用 `reschedule` 模式** | Sensor 默认改用 `reschedule`，节省资源 |
| **清理 XCom** | 定期清理，避免 Metadata DB 膨胀 |

### ❌ 避免的做法

1. **避免在顶层执行重操作**（如数据库连接、API 调用）
2. **避免动态依赖 `datetime.now()`**（使用 `logical_date`）
3. **避免 Task 间传递大数据**（XCom 传引用不传数据）
4. **避免一个 DAG 超过 1000 个 Task**（拆分或用 TaskGroup）
5. **避免在 DAG 文件中使用 `time.sleep()`**（用 Sensor 替代）

### Airflow 配置要点

```ini
# airflow.cfg 关键配置

[core]
# Executor 类型：Sequential(测试) / Local / Celery / Kubernetes
executor = CeleryExecutor

# 并发控制
parallelism = 32              # 全局最大并发 Task 数
dag_concurrency = 16          # 每个 DAG 的最大并发 Task 数

[scheduler]
# DAG 文件解析间隔（秒）
dag_dir_list_interval = 300
# 每个 DAG 解析间隔（秒）
min_file_process_interval = 30
# 子进程解析 DAG 超时
parsing_timeout = 120

[celery]
worker_concurrency = 16       # 每个 Worker 并发 Task 数
broker_url = redis://redis:6379/0
result_backend = db+postgresql://airflow:pass@db/airflow

[scheduler]
# DAG 调度循环
scheduler_heartbeat_sec = 5
```

---

## 相关页面

- [[Spark大数据处理]] - Spark 任务通过 Airflow 调度
- [[Flink流处理引擎]] - Flink Job 提交与管理
- [[数据湖架构]] - 数据湖 ETL 管道编排
- [[dbt数据转换]] - dbt 模型通过 Airflow 调度

---
title: MLOps实践指南
aliases:
  - MLOps
  - 机器学习运维
  - 模型生命周期管理
tags:
  - AI
  - MLOps
  - 模型管理
  - DevOps
  - 实验跟踪
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: 实践总结
difficulty: advanced
project: AI-Agent
---

# MLOps实践指南

> MLOps（Machine Learning Operations）是将DevOps理念扩展到机器学习生命周期管理的一套方法论与工具链，目标是实现模型的**可重复、可追踪、可自动化**的从训练到部署的全流程管理。

## 1 核心理念

MLOps的核心在于将**数据-模型-部署**三者纳入统一的版本化与自动化管线：

```
数据版本管理 → 实验跟踪 → 模型注册 → CI/CD部署 → 在线监控 → 数据回流
```

| 阶段 | 核心工具 | 关键产出 |
|------|---------|---------|
| 数据管理 | DVC, LakeFS, Feast | 版本化数据集 |
| 实验跟踪 | MLflow, W&B, Comet | 超参数/指标记录 |
| 模型注册 | MLflow Model Registry | 版本化模型工件 |
| 部署服务 | TorchServe, Triton, KServe | 在线推理端点 |
| 监控运维 | Evidently, Grafana, Prometheus | 数据漂移检测 |

## 2 模型生命周期管理

### 2.1 生命周期阶段

```
需求定义 → 数据准备 → 特征工程 → 模型训练 → 验证评估 → 模型注册 → 灰度发布 → 生产部署 → 监控告警 → 迭代/下线
```

### 2.2 MLOps成熟度模型（Google分级）

| 级别 | 特征 | 自动化程度 |
|------|------|-----------|
| Level 0 | 手动流程，无CI/CD | 极低 |
| Level 1 | ML流水线自动化，实验可追踪 | 中 |
| Level 2 | CI/CD流水线全自动化，多环境管理 | 高 |

## 3 实验跟踪（Experiment Tracking）

### 3.1 MLflow Tracking 基础

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

# 设置实验名称（不存在则自动创建）
mlflow.set_experiment("iris-classification")

# 开启自动日志
mlflow.sklearn.autolog()

with mlflow.start_run(run_name="rf_baseline") as run:
    # 加载数据
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 手动记录超参数（autolog也会记录，这里展示手动方式）
    params = {
        "n_estimators": 100,
        "max_depth": 5,
        "random_state": 42,
    }
    mlflow.log_params(params)

    # 训练模型
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # 评估并记录指标
    y_pred = model.predict(X_test)
    mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
    mlflow.log_metric("f1_macro", f1_score(y_test, y_pred, average="macro"))

    # 记录模型
    mlflow.sklearn.log_model(model, "model")

    # 记录数据集信息作为tag
    mlflow.set_tag("dataset", "iris")
    mlflow.set_tag("framework", "sklearn")

    print(f"Run ID: {run.info.run_id}")
    print(f"Artifact URI: {run.info.artifact_uri}")
```

### 3.2 MLflow 高级用法：嵌套运行与参数搜索

```python
import mlflow
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import load_breast_cancer

X, y = load_breast_cancer(return_X_y=True)

mlflow.set_experiment("gbm-hyperparameter-search")

# 父运行
with mlflow.start_run(run_name="grid_search_parent") as parent_run:
    param_grid = {
        "n_estimators": [50, 100, 200],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.01, 0.1, 0.2],
    }

    gbm = GradientBoostingClassifier(random_state=42)
    grid = GridSearchCV(gbm, param_grid, cv=5, scoring="f1", n_jobs=-1)
    grid.fit(X, y)

    # 记录最佳结果
    mlflow.log_params(grid.best_params_)
    mlflow.log_metric("best_f1", grid.best_score_)

    # 为每个候选参数组合创建嵌套子运行
    results = grid.cv_results_
    for i in range(len(results["params"])):
        with mlflow.start_run(run_name=f"trial_{i}", nested=True):
            mlflow.log_params(results["params"][i])
            mlflow.log_metric("mean_f1", results["mean_test_score"][i])
            mlflow.log_metric("std_f1", results["std_test_score"][i])

    print(f"Best params: {grid.best_params_}")
    print(f"Best F1: {grid.best_score_:.4f}")
```

### 3.3 Weights & Biases (W&B) 实验跟踪

```python
import wandb
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# 初始化W&B
wandb.init(
    project="cifar10-cnn",
    config={
        "epochs": 20,
        "batch_size": 128,
        "learning_rate": 0.001,
        "architecture": "ResNet18",
        "dataset": "CIFAR-10",
    },
)

config = wandb.config

# 训练循环
for epoch in range(config.epochs):
    model.train()
    total_loss = 0
    correct = 0

    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        pred = output.argmax(dim=1)
        correct += pred.eq(target).sum().item()

    # 每个epoch记录指标
    wandb.log({
        "epoch": epoch,
        "train_loss": total_loss / len(train_loader),
        "train_acc": correct / len(train_loader.dataset),
        "learning_rate": optimizer.param_groups[0]["lr"],
    })

    # 记录模型梯度直方图
    for name, param in model.named_parameters():
        if param.grad is not None:
            wandb.histogram(name, param.grad.cpu().numpy())

# 保存模型工件
wandb.save("model.pth")
artifact = wandb.Artifact("cifar10-model", type="model")
artifact.add_file("model.pth")
wandb.log_artifact(artifact)

wandb.finish()
```

## 4 模型注册（Model Registry）

### 4.1 MLflow Model Registry 工作流

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# --- 注册模型 ---
result = mlflow.register_model(
    model_uri="runs:/<RUN_ID>/model",
    name="iris-classifier",
)

# --- 模型版本管理 ---
# 将模型阶段从 None → Staging → Production
client.transition_model_version_stage(
    name="iris-classifier",
    version=result.version,
    stage="Staging",
)

# 添加版本描述
client.update_model_version(
    name="iris-classifier",
    version=result.version,
    description="RF baseline, accuracy=0.95, F1=0.94",
)

# --- 查询生产环境模型 ---
production_versions = client.get_latest_versions(
    name="iris-classifier",
    stages=["Production"],
)

for mv in production_versions:
    print(f"Version: {mv.version}, Stage: {mv.current_stage}")
```

### 4.2 模型注册表最佳实践

```python
# 使用Tag进行细粒度版本管理（替代已废弃的Stage概念）
client.set_registered_model_tag(
    name="iris-classifier",
    key="domain",
    value="classification",
)

client.set_model_version_tag(
    name="iris-classifier",
    version=3,
    key="deployment_status",
    value="canary",
)

# 获取所有带有特定tag的模型版本
all_versions = client.search_model_versions("name='iris-classifier'")
canary_versions = [
    mv for mv in all_versions
    if mv.tags.get("deployment_status") == "canary"
]
```

## 5 在线推理服务

### 5.1 使用 MLflow pyfunc Server

```bash
# 启动MLflow模型服务
mlflow models serve \
  -m "models:/iris-classifier/Production" \
  -p 5001 \
  --host 0.0.0.0
```

```python
import requests
import json

# 调用推理端点
data = {
    "dataframe_split": {
        "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
        "data": [[5.1, 3.5, 1.4, 0.2]],
    }
}

response = requests.post(
    "http://localhost:5001/invocations",
    headers={"Content-Type": "application/json"},
    data=json.dumps(data),
)

print(f"Prediction: {response.json()}")
```

### 5.2 KServe 推理服务（Kubernetes原生）

```yaml
# kserve-inference.yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: iris-classifier
  namespace: ml-workspace
spec:
  predictor:
    minReplicas: 1
    maxReplicas: 5
    scaleTarget: 10
    scaleMetric: concurrency
    sklearn:
      storageUri: "s3://mlflow-models/iris-classifier/v3"
      resources:
        requests:
          cpu: "100m"
          memory: "256Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
```

```bash
# 部署推理服务
kubectl apply -f kserve-inference.yaml

# 调用推理
curl -v http://iris-classifier.ml-workspace.example.com/v1/models/iris-classifier:predict \
  -d '{"instances": [[5.1, 3.5, 1.4, 0.2]]}'
```

### 5.3 批量推理Pipeline

```python
import mlflow
import pandas as pd
from pathlib import Path

# 加载生产模型
model = mlflow.pyfunc.load_model("models:/iris-classifier/Production")

# 批量推理
def batch_predict(input_path: str, output_path: str, batch_size: int = 10000):
    """分批进行大规模推理"""
    chunks = pd.read_csv(input_path, chunksize=batch_size)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    all_preds = []
    for i, chunk in enumerate(chunks):
        preds = model.predict(chunk)
        all_preds.append(pd.DataFrame({"prediction": preds}))
        print(f"Batch {i}: {len(chunk)} rows processed")

    result = pd.concat(all_preds, ignore_index=True)
    result.to_csv(output_path, index=False)
    print(f"Total predictions: {len(result)}")

batch_predict("data/batch_input.csv", "data/batch_output.csv")
```

## 6 CI/CD流水线

### 6.1 GitHub Actions MLOps流水线

```yaml
# .github/workflows/mlops-pipeline.yml
name: MLOps Pipeline

on:
  push:
    branches: [main]
    paths:
      - "src/training/**"
      - "data/**"
  workflow_dispatch:

jobs:
  train-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install mlflow scikit-learn pandas

      - name: Run training pipeline
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: python src/training/train.py

      - name: Run model validation
        run: python src/validation/validate.py --threshold 0.90

      - name: Promote model to production
        if: success()
        run: python src/deployment/promote.py --model-name iris-classifier

      - name: Trigger deployment
        if: success()
        run: |
          curl -X POST \
            "${{ secrets.DEPLOY_WEBHOOK }}" \
            -H "Content-Type: application/json" \
            -d '{"model": "iris-classifier", "action": "deploy"}'
```

## 7 模型监控与漂移检测

### 7.1 Evidently 数据漂移检测

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
import pandas as pd

# 加载参考数据和生产数据
reference_data = pd.read_csv("data/reference.csv")
production_data = pd.read_csv("data/production.csv")

# 生成漂移报告
data_drift_report = Report(metrics=[DataDriftPreset()])
data_drift_report.run(
    reference_data=reference_data,
    current_data=production_data,
)
data_drift_report.save_html("reports/data_drift.html")

# 目标漂移检测
target_drift_report = Report(metrics=[TargetDriftPreset()])
target_drift_report.run(
    reference_data=reference_data,
    current_data=production_data,
    column_mapping=target_mapping,
)
target_drift_report.save_html("reports/target_drift.html")
```

### 7.2 Prometheus + Grafana 监控推理延迟

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# 定义监控指标
PREDICTION_COUNT = Counter(
    "model_predictions_total",
    "Total number of predictions",
    ["model_name", "model_version"],
)

PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds",
    "Time spent processing prediction",
    ["model_name"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

PREDICTION_ERROR = Counter(
    "model_prediction_errors_total",
    "Total prediction errors",
    ["error_type"],
)

# 在推理函数中埋点
def predict(input_data):
    try:
        start = time.time()
        result = model.predict(input_data)
        PREDICTION_LATENCY.labels(model_name="iris-classifier").observe(time.time() - start)
        PREDICTION_COUNT.labels(
            model_name="iris-classifier",
            model_version="v3",
        ).inc()
        return result
    except Exception as e:
        PREDICTION_ERROR.labels(error_type=type(e).__name__).inc()
        raise

start_http_server(8000)
```

## 8 最佳实践

### 8.1 工程规范

| 领域 | 最佳实践 |
|------|---------|
| 数据版本化 | 使用DVC管理数据集版本，与代码版本绑定 |
| 实验可复现 | 固定随机种子、记录完整环境依赖（`requirements.txt`/`conda.yaml`） |
| 模型评估 | 使用交叉验证、记录多维度指标（不仅accuracy） |
| 模型注册 | 语义化版本号 + 变更日志（changelog） |
| 部署策略 | Canary发布 → 金丝雀验证 → 全量发布 |
| 监控 | 同时监控**输入数据漂移**和**预测质量** |
| 安全 | 敏感凭证（API Key等）使用Secret Manager管理 |

### 8.2 实验跟踪规范

```python
# 规范的实验命名与Tag
mlflow.set_tags({
    "team": "nlp",
    "author": "zhang_san",
    "experiment_type": "finetune",
    "base_model": "bert-base-chinese",
    "task": "text_classification",
    "data_version": "v2.3",
})
```

### 8.3 团队协作流程

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ 数据工程师 │────→│ ML研究员  │────→│ ML工程师  │────→│ DevOps   │
│ 数据ETL   │     │ 模型实验   │     │ 工程化    │     │ 部署运维  │
│ 特征工程   │     │ 超参搜索   │     │ 流水线    │     │ 监控告警  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      ↕                ↕                ↕                ↕
  ┌──────────────────────────────────────────────────────────┐
  │              共享：MLflow / W&B / Git / Model Registry    │
  └──────────────────────────────────────────────────────────┘
```

## 9 工具选型对比

### 9.1 实验跟踪工具对比

| 特性 | MLflow | W&B | Comet | Neptune |
|------|--------|-----|-------|---------|
| 开源 | ✅ | 部分开源 | ❌ | 部分开源 |
| 自部署 | ✅ | ❌ | ❌ | ❌ |
| UI美观度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 模型注册 | ✅ 内置 | ✅ 内置 | ✅ | ✅ |
| 价格 | 免费(自部署) | $$ | $$ | $$$ |
| 大规模团队 | ✅ | ✅ | ✅ | ✅ |

### 9.2 模型服务框架对比

| 框架 | 适用场景 | 语言支持 | 动态批处理 | 优点 |
|------|---------|---------|-----------|------|
| TorchServe | PyTorch模型 | Python | ✅ | 官方支持，易于使用 |
| Triton Inference Server | 多框架 | C++/Python | ✅ | 高性能，多框架 |
| BentoML | 通用 | Python | ✅ | 易打包，易部署 |
| KServe | K8s原生 | 多语言 | ✅ | 云原生，自动伸缩 |
| Seldon Core | K8s原生 | 多语言 | ✅ | 企业级，解释性 |

## 相关页面

- [[模型部署指南]] - TorchServe、Triton、vLLM部署详解
- [[向量数据库实战]] - 向量检索与嵌入存储
- [[LangChain开发指南]] - LLM应用开发框架
- [[AI安全与对齐]] - 模型安全与对齐技术

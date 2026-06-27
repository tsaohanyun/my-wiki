---
title: Python机器学习实战
aliases: [ML实战, sklearn实战, 机器学习Python, MLOps]
tags: [python, machine-learning, sklearn, mlops]
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: 实践经验
difficulty: intermediate
project: 数据科学
---
# Python 机器学习实战

## 概述

本指南涵盖使用Python进行机器学习的完整流程，从数据准备到模型部署。

## 1. sklearn核心流程

### 分类模型

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# 加载数据
data = load_iris()
X, y = data.data, data.target

# 划分训练测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 使用Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# 训练
pipeline.fit(X_train, y_train)

# 预测
y_pred = pipeline.predict(X_test)

# 评估
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

# 交叉验证
scores = cross_val_score(pipeline, X, y, cv=5)
print(f"CV Score: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### 回归模型

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"MSE: {mse:.4f}, R2: {r2:.4f}")
```

## 2. 特征工程

### 特征预处理

```python
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    LabelEncoder, OneHotEncoder, OrdinalEncoder
)
from sklearn.impute import SimpleImputer, KNNImputer
import numpy as np
import pandas as pd

# 缺失值处理
imputer = KNNImputer(n_neighbors=5)
X_imputed = imputer.fit_transform(X)

# 数值特征缩放
scaler = RobustScaler()  # 对异常值鲁棒
X_scaled = scaler.fit_transform(X_imputed)

# 类别特征编码
# One-Hot编码（无序类别）
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_cat = ohe.fit_transform(categorical_features)

# 序数编码（有序类别）
oe = OrdinalEncoder(categories=[['low', 'medium', 'high']])
X_ord = oe.fit_transform(ordinal_features)
```

### 特征选择

```python
from sklearn.feature_selection import (
    SelectKBest, f_classif, RFE, RFECV,
    mutual_info_classif
)
from sklearn.linear_model import LassoCV

# 方差过滤
from sklearn.feature_selection import VarianceThreshold
selector = VarianceThreshold(threshold=0.01)
X_high_var = selector.fit_transform(X)

# 单变量统计检验
selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X, y)

# 递归特征消除
rfe = RFECV(estimator=RandomForestClassifier(), cv=5, scoring='f1')
X_rfe = rfe.fit_transform(X, y)
print(f"最优特征数: {rfe.n_features_}")

# L1正则化选择
lasso = LassoCV(cv=5)
lasso.fit(X, y)
selected = np.where(lasso.coef_ != 0)[0]
```

### 特征构造

```python
# 多项式特征
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_poly = poly.fit_transform(X)

# 自定义特征
df['feature_ratio'] = df['feature_a'] / (df['feature_b'] + 1e-8)
df['feature_diff'] = df['feature_a'] - df['feature_b']
df['feature_log'] = np.log1p(df['feature_c'])
```

## 3. 模型调优

### 网格搜索

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from scipy.stats import randint, uniform

param_grid = {
    'n_estimators': [100, 200, 500],
    'max_depth': [3, 5, 7, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='f1_weighted',
    n_jobs=-1,
    verbose=1
)
grid_search.fit(X_train, y_train)
print(f"最佳参数: {grid_search.best_params_}")
print(f"最佳分数: {grid_search.best_score_:.4f}")
```

### 随机搜索

```python
param_dist = {
    'n_estimators': randint(50, 500),
    'max_depth': [3, 5, 7, 10, None],
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': uniform(0.5, 0.5)
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_dist,
    n_iter=100,
    cv=5,
    scoring='f1_weighted',
    n_jobs=-1,
    random_state=42
)
random_search.fit(X_train, y_train)
```

### Optuna贝叶斯优化

```python
import optuna

def objective(trial):
    n_estimators = trial.suggest_int('n_estimators', 50, 500)
    max_depth = trial.suggest_int('max_depth', 3, 20)
    min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
    
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=42
    )
    
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1_weighted')
    return scores.mean()

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)
print(f"最佳参数: {study.best_params}")
print(f"最佳分数: {study.best_value:.4f}")
```

## 4. 模型评估

### 分类评估

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    classification_report, confusion_matrix
)
import matplotlib.pyplot as plt

# 综合报告
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))

# ROC曲线
fpr, tpr, _ = roc_curve(y_test, y_proba)
auc = roc_auc_score(y_test, y_proba)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'ROC (AUC = {auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()
```

### 回归评估

```python
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    mean_absolute_percentage_error
)

metrics = {
    'MAE': mean_absolute_error(y_test, y_pred),
    'MSE': mean_squared_error(y_test, y_pred),
    'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
    'R2': r2_score(y_test, y_pred),
    'MAPE': mean_absolute_percentage_error(y_test, y_pred)
}

for name, value in metrics.items():
    print(f"{name}: {value:.4f}")
```

### 交叉验证策略

```python
from sklearn.model_selection import (
    StratifiedKFold, TimeSeriesSplit, GroupKFold, RepeatedStratifiedKFold
)

# 分层K折（分类问题）
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 时间序列交叉验证
cv = TimeSeriesSplit(n_splits=5)

# 分组交叉验证
cv = GroupKFold(n_splits=5)

# 重复分层K折
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
```

## 5. 集成学习

### 投票分类器

```python
from sklearn.ensemble import (
    VotingClassifier, BaggingClassifier,
    StackingClassifier, AdaBoostClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

# 软投票
voting_clf = VotingClassifier(
    estimators=[
        ('lr', LogisticRegression()),
        ('rf', RandomForestClassifier(n_estimators=100)),
        ('svc', SVC(probability=True))
    ],
    voting='soft'
)
voting_clf.fit(X_train, y_train)
```

### 堆叠集成

```python
stacking_clf = StackingClassifier(
    estimators=[
        ('lr', LogisticRegression()),
        ('rf', RandomForestClassifier(n_estimators=100)),
        ('svc', SVC(probability=True))
    ],
    final_estimator=GradientBoostingRegressor(),
    cv=5
)
stacking_clf.fit(X_train, y_train)
```

## 6. 模型持久化

### 保存和加载

```python
import joblib

# 保存模型
joblib.dump(pipeline, 'model_pipeline.pkl')

# 加载模型
loaded_model = joblib.load('model_pipeline.pkl')
predictions = loaded_model.predict(X_new)
```

### 模型版本管理

```python
import mlflow

# 记录实验
mlflow.set_experiment("iris_classification")

with mlflow.start_run():
    # 记录参数
    mlflow.log_params(grid_search.best_params_)
    
    # 记录指标
    mlflow.log_metric('accuracy', accuracy_score(y_test, y_pred))
    mlflow.log_metric('f1_score', f1_score(y_test, y_pred, average='weighted'))
    
    # 记录模型
    mlflow.sklearn.log_model(grid_search.best_estimator_, 'model')
    
    # 记录特征重要性
    importances = grid_search.best_estimator_.feature_importances_
    for name, imp in zip(feature_names, importances):
        mlflow.log_metric(f'feature_{name}', imp)
```

## 7. 模型部署

### FastAPI部署

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="ML Model API")
model = joblib.load('model_pipeline.pkl')

class InputData(BaseModel):
    features: list[float]

class OutputData(BaseModel):
    prediction: int
    probability: float

@app.post("/predict", response_model=OutputData)
def predict(data: InputData):
    X = np.array(data.features).reshape(1, -1)
    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0].max()
    return OutputData(prediction=int(prediction), probability=float(probability))

@app.get("/health")
def health():
    return {"status": "healthy"}
```

### Docker部署

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 8. MLOps实践

### 数据版本管理

```python
import dvc

# DVC数据版本管理
# dvc init
# dvc add data/raw_data.csv
# dvc remote add -d storage s3://my-bucket/dvc
# dvc push
```

### 模型监控

```python
import evidently
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# 数据漂移检测
data_drift_report = Report(metrics=[DataDriftPreset()])
data_drift_report.calculate(
    reference_data=reference_df,
    current_data=current_df
)
data_drift_report.save('drift_report.html')
```

### CI/CD流水线

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    paths:
      - 'models/**'
      - 'data/**'

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Train model
        run: |
          pip install -r requirements.txt
          python train.py
      - name: Evaluate model
        run: python evaluate.py
      - name: Deploy model
        if: success()
        run: python deploy.py
```

## 最佳实践

1. **数据泄漏防护**：永远先split再preprocess，使用Pipeline
2. **分层采样**：分类问题使用StratifiedKFold
3. **特征重要性**：定期检查特征重要性变化
4. **模型监控**：部署后持续监控数据漂移
5. **版本管理**：使用MLflow/DVC管理模型和数据版本

## 相关页面

- [[Python数据分析工具箱]]
- [[机器学习入门]]
- [[深度学习基础]]
- [[数据质量工具箱]]

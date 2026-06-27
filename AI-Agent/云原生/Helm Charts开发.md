---
title: Helm Charts开发
aliases:
  - Helm开发
  - Helm Chart
  - Chart开发
tags:
  - 云原生
  - Helm
  - Kubernetes
  - 包管理
type: 文档
status: 已完成
created: 2024-01-15
updated: 2024-03-20
source: 内部实践
difficulty: 中级
project: AI-Agent
---

# Helm Charts开发

## 概述

Helm 是 Kubernetes 的包管理器，Charts 是 Helm 的打包格式。一个 Chart 是描述一组相关 Kubernetes 资源的文件集合。

## Chart 结构

```
mychart/
├── Chart.yaml          # Chart 元数据
├── Chart.lock          # 依赖锁定文件
├── values.yaml         # 默认配置值
├── values.schema.json  # Values JSON Schema（可选）
├── templates/          # 模板目录
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── serviceaccount.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── _helpers.tpl    # 模板辅助函数
│   ├── NOTES.txt       # 安装后提示信息
│   └── tests/
│       └── test-connection.yaml
├── charts/             # 子 Chart 依赖
├── crds/               # CRD 定义
└── README.md
```

## Chart.yaml 配置

```yaml
apiVersion: v2
name: myapp
description: A Helm chart for deploying MyApplication
type: application
version: 1.2.0
appVersion: "2.0.0"

maintainers:
  - name: devops-team
    email: devops@example.com

keywords:
  - web
  - api
  - microservice

home: https://github.com/example/myapp
sources:
  - https://github.com/example/myapp

dependencies:
  - name: redis
    version: "17.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
  - name: postgresql
    version: "12.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

## 模板语法

### 基础语法

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          env:
            {{- toYaml .Values.env | nindent 12 }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

### _helpers.tpl 辅助函数

```yaml
{{/*
生成应用全名
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
通用标签
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
选择器标签
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### 条件与循环

```yaml
# 条件渲染
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "myapp.fullname" . }}
{{- end }}

# 循环遍历
{{- range .Values.ingress.hosts }}
  - host: {{ .host | quote }}
    http:
      paths:
        {{- range .paths }}
        - path: {{ .path }}
          pathType: {{ .pathType }}
        {{- end }}
{{- end }}

# With 块
{{- with .Values.nodeSelector }}
nodeSelector:
  {{- toYaml . | nindent 8 }}
{{- end }}
```

## Values 配置

```yaml
# values.yaml
replicaCount: 3

image:
  repository: registry.example.com/myapp
  pullPolicy: IfNotPresent
  tag: ""

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

env:
  - name: LOG_LEVEL
    value: info
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: host

livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /readyz
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5

# 子 Chart 配置
redis:
  enabled: true
  architecture: standalone
  auth:
    enabled: true

postgresql:
  enabled: true
  auth:
    database: myapp
    username: myapp
```

## 环境差异化配置

```yaml
# values-staging.yaml
replicaCount: 1

image:
  tag: staging

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false

ingress:
  hosts:
    - host: staging.myapp.example.com
      paths:
        - path: /
          pathType: Prefix
```

```yaml
# values-production.yaml
replicaCount: 3

image:
  tag: latest

resources:
  limits:
    cpu: "1"
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
```

## Hook 使用

```yaml
# templates/job-db-migrate.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" . }}-db-migrate
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      containers:
        - name: db-migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["./migrate", "up"]
      restartPolicy: Never
  backoffLimit: 1
```

## 发布流程

### Chart 打包与发布

```bash
# 本地验证
helm lint ./mychart
helm template myrelease ./mychart -f values-production.yaml

# 打包
helm package ./mychart

# 推送到 OCI Registry
helm registry login registry.example.com -u admin
helm push mychart-1.2.0.tgz oci://registry.example.com/charts

# 推送到 ChartMuseum
curl --data-binary "@mychart-1.2.0.tgz" https://chartmuseum.example.com/api/charts

# 添加仓库
helm repo add myrepo https://chartmuseum.example.com
helm repo update
```

### CI/CD 集成

```yaml
# .github/workflows/helm-release.yml
name: Helm Chart Release
on:
  push:
    paths:
      - 'charts/**'
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install Helm
        uses: azure/setup-helm@v3

      - name: Lint Chart
        run: helm lint ./charts/myapp

      - name: Run chart-testing
        uses: helm/chart-testing-action@v2
        with:
          command: lint-and-install
          config: ct.yaml

      - name: Package & Push
        run: |
          helm package ./charts/myapp
          helm push myapp-*.tgz oci://ghcr.io/example/charts
```

## 最佳实践

1. **版本管理**：严格遵循语义化版本，Chart version 与 appVersion 分开管理
2. **默认安全**：values.yaml 中设置合理的安全默认值（如 `readOnlyRootFilesystem: true`）
3. **资源限制**：始终设置 resources requests 和 limits
4. **模板复用**：善用 `_helpers.tpl` 避免重复
5. **Schema 验证**：使用 `values.schema.json` 约束输入
6. **Chart 测试**：编写 `templates/tests/` 下的测试用例
7. **NOTES.txt**：提供清晰的安装后使用指引
8. **Chart.lock**：提交依赖锁定文件确保可重复构建
9. **安全扫描**：集成 trivy 或 checkov 进行 Chart 安全扫描
10. **文档化**：README.md 中说明所有可配置参数

## 相关页面

- [[Operator开发指南]] - 当 Helm 不足以管理复杂应用时
- [[服务网格实践]] - Helm 安装和配置服务网格
- [[云原生存储]] - Chart 中配置持久化存储
- [[云原生网络]] - Chart 中配置网络策略

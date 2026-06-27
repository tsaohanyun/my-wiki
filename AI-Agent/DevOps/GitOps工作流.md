---
title: GitOps工作流
aliases:
  - GitOps Workflow
  - GitOps实践
tags:
  - devops
  - gitops
  - argocd
  - fluxcd
  - kubernetes
  - configuration-management
type: reference
status: active
created: 2025-01-15
updated: 2025-01-15
source: internal
difficulty: intermediate
project: AI-Agent
---

# GitOps工作流

## 概述

GitOps是一种以Git仓库作为单一事实来源的运维模式，通过声明式配置和自动化工具来管理基础设施和应用部署。GitOps的核心原则是：

1. **声明式**: 所有系统状态都以声明式方式描述
2. **版本化和不可变**: 所有配置存储在Git中，可追溯
3. **自动拉取**: 自动从Git拉取并应用配置
4. **持续调和**: 自动检测并修复与期望状态的偏差

## GitOps架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                          GitOps工作流                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐            │
│  │   开发者    │────→│  Git仓库    │────→│  CI/CD     │            │
│  │  (代码变更) │     │ (配置仓库) │     │  流水线    │            │
│  └─────────────┘     └─────────────┘     └─────────────┘            │
│                              │                   │                    │
│                              │                   ▼                    │
│                              │           ┌─────────────┐             │
│                              │           │  镜像仓库   │             │
│                              │           └─────────────┘             │
│                              ▼                                       │
│                       ┌─────────────┐                                │
│                       │  GitOps     │                                │
│                       │  控制器     │                                │
│                       └─────────────┘                                │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Kubernetes集群                               │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │  │
│  │  │ 命名空间 │  │   Pod   │  │ Service │  │ Ingress │         │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## GitOps原则详解

### 1. 声明式配置

所有系统配置都使用声明式方式描述，而不是命令式脚本。

```yaml
# 声明式方式 - 描述期望状态
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:v1.2.3
        ports:
        - containerPort: 8080
```

### 2. 版本化和不可变

所有配置都存储在Git中，提供完整的变更历史。

```bash
# 配置仓库结构
config-repo/
├── README.md
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── overlays/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   └── production/
│       ├── kustomization.yaml
│       └── patches/
└── apps/
    ├── app-a/
    │   ├── base/
    │   └── overlays/
    └── app-b/
        ├── base/
        └── overlays/
```

### 3. 自动拉取

GitOps控制器自动从Git拉取配置变更。

```yaml
# ArgoCD自动同步配置
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  syncPolicy:
    automated:
      prune: true      # 删除Git中不存在的资源
      selfHeal: true   # 自动修复手动更改
    syncOptions:
      - CreateNamespace=true
```

### 4. 持续调和

控制器持续监控集群状态，自动修复与期望状态的偏差。

```yaml
# 调和循环示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  annotations:
    # 每30秒检查一次
    argocd.argoproj.io/sync-options: "RespectIgnoreDifferences=true"
spec:
  # 期望状态
  replicas: 3
  # 控制器会持续确保实际状态匹配
```

## ArgoCD

### 安装和配置

```yaml
# argocd-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: argocd
  labels:
    app.kubernetes.io/part-of: argocd

---
# argocd-install.yaml (Helm Values)
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cmd-params-cm
  namespace: argocd
data:
  # 启用HA模式
  server.enable.gzip: "true"
  server.insecure: "false"
  
---
# argocd-server-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  ingressClassName: nginx
  rules:
  - host: argocd.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              name: https
  tls:
  - hosts:
    - argocd.example.com
    secretName: argocd-secret
```

### Application配置

```yaml
# 单应用配置
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-application
  namespace: argocd
  annotations:
    argocd.argoproj.io/manifest-generate-paths: "/apps/my-app"
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  
  source:
    repoURL: https://github.com/org/k8s-configs.git
    targetRevision: main
    path: apps/my-app/overlays/production
    
    # 使用Kustomize
    kustomize:
      images:
        - my-app=registry.example.com/my-app:v1.2.3
    
    # 或使用Helm
    # helm:
    #   releaseName: my-app
    #   valueFiles:
    #     - values-production.yaml
    #   values: |
    #     replicaCount: 3
    #     image:
    #       tag: v1.2.3
  
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  
  # 忽略差异
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
    - group: ""
      kind: Service
      jqPathExpressions:
        - .spec.clusterIP
```

### AppProject配置

```yaml
# 多团队项目配置
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: backend-team
  namespace: argocd
spec:
  description: "Backend Team Project"
  
  # 允许的源仓库
  sourceRepos:
    - 'https://github.com/org/backend-configs.git'
    - 'https://github.com/org/shared-configs.git'
    - 'https://charts.example.com/*'
  
  # 允许的目标集群和命名空间
  destinations:
    - namespace: 'backend-*'
      server: https://kubernetes.default.svc
    - namespace: 'staging'
      server: https://staging-cluster.example.com
  
  # 允许的集群资源
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
    - group: 'rbac.authorization.k8s.io'
      kind: ClusterRole
  
  # 禁止的命名空间资源
  namespaceResourceBlacklist:
    - group: ''
      kind: ResourceQuota
    - group: ''
      kind: LimitRange
  
  # 角色定义
  roles:
    - name: developer
      description: "Developer access"
      policies:
        - p, proj:backend-team:developer, applications, get, backend-team/*, allow
        - p, proj:backend-team:developer, applications, sync, backend-team/*, allow
        - p, proj:backend-team:developer, applications, action/*, backend-team/*, allow
      groups:
        - backend-developers
    
    - name: admin
      description: "Admin access"
      policies:
        - p, proj:backend-team:admin, applications, *, backend-team/*, allow
        - p, proj:backend-team:admin, repositories, *, backend-team/*, allow
      groups:
        - backend-leads
  
  # 同步窗口
  syncWindows:
    # 工作时间允许同步
    - kind: allow
      schedule: '0 8-18 * * 1-5'
      duration: 10h
      applications:
        - '*'
      namespaces:
        - 'production'
    
    # 周末禁止同步
    - kind: deny
      schedule: '0 0 * * 0,6'
      duration: 48h
      applications:
        - '*'
      namespaces:
        - 'production'
```

### ApplicationSet配置

```yaml
# 多环境ApplicationSet
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-app-multi-env
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - env: dev
            cluster: https://dev-cluster.example.com
            revision: develop
          - env: staging
            cluster: https://staging-cluster.example.com
            revision: main
          - env: production
            cluster: https://prod-cluster.example.com
            revision: main
  
  template:
    metadata:
      name: 'my-app-{{env}}'
      labels:
        app: my-app
        env: '{{env}}'
    spec:
      project: backend-team
      
      source:
        repoURL: https://github.com/org/k8s-configs.git
        targetRevision: '{{revision}}'
        path: apps/my-app/overlays/{{env}}
      
      destination:
        server: '{{cluster}}'
        namespace: my-app
      
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
  
  # 同步策略
  strategy:
    type: RollingSync
    rollingSync:
      steps:
        - matchExpressions:
            - key: env
              operator: In
              values:
                - dev
        - matchExpressions:
            - key: env
              operator: In
              values:
                - staging
        - matchExpressions:
            - key: env
              operator: In
              values:
                - production
```

## FluxCD

### 安装配置

```yaml
# flux-system/gotk-components.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: flux-system
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/gitops-configs.git
  ref:
    branch: main
  secretRef:
    name: flux-system

---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: flux-system
  namespace: flux-system
spec:
  interval: 10m
  path: ./clusters/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  validation: client
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: source-controller
      namespace: flux-system
```

### 应用配置

```yaml
# apps/base/my-app/source.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/my-app-configs.git
  ref:
    branch: main
  secretRef:
    name: git-credentials

---
# apps/base/my-app/kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 10m
  path: ./overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
  validation: client
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: my-app
      namespace: production
  timeout: 3m
  
  # 依赖其他Kustomization
  dependsOn:
    - name: infrastructure
  
  # 解密配置
  decryption:
    provider: sops
    secretRef:
      name: sops-age
```

### 多环境配置

```yaml
# clusters/production/infrastructure.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 1h
  path: ./infrastructure/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  validation: client

---
# clusters/production/apps.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  path: ./apps/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  validation: client
  dependsOn:
    - name: infrastructure
```

### Helm Release配置

```yaml
# apps/base/my-app/helm-release.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 1h
  url: https://charts.bitnami.com/bitnami

---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: nginx
  namespace: production
spec:
  interval: 1h
  chart:
    spec:
      chart: nginx
      version: '15.x'
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
      interval: 1h
  
  values:
    replicaCount: 3
    image:
      registry: docker.io
      repository: bitnami/nginx
      tag: 1.25
    service:
      type: ClusterIP
      ports:
        http: 80
    ingress:
      enabled: true
      hostname: nginx.example.com
  
  # 值覆盖（环境特定）
  valuesFrom:
    - kind: ConfigMap
      name: nginx-values
      optional: true
  
  upgrade:
    remediation:
      retries: 3
      remediateLastFailure: true
  
  test:
    enable: true
  
  rollback:
    cleanupOnFail: true
```

## 配置管理

### Kustomize配置

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

metadata:
  name: my-app

resources:
  - deployment.yaml
  - service.yaml
  - ingress.yaml
  - configmap.yaml
  - hpa.yaml

commonLabels:
  app: my-app
  managed-by: kustomize

# 通用注解
commonAnnotations:
  team: backend
  cost-center: engineering

# 命名空间
namespace: production

# 镜像覆盖
images:
  - name: my-app
    newName: registry.example.com/my-app
    newTag: v1.2.3

# ConfigMap生成器
configMapGenerator:
  - name: app-config
    literals:
      - LOG_LEVEL=info
      - DATABASE_HOST=db.example.com
    files:
      - config.yaml

# Secret生成器
secretGenerator:
  - name: app-secrets
    literals:
      - API_KEY=encrypted-api-key
    type: Opaque

# 补丁
patches:
  - target:
      kind: Deployment
      name: my-app
    patch: |
      - op: replace
        path: /spec/replicas
        value: 3

# 变量替换
vars:
  - name: SERVICE_NAME
    objref:
      kind: Service
      name: my-app
      apiVersion: v1
    fieldref:
      fieldpath: metadata.name
```

### 环境覆盖

```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

metadata:
  name: my-app-production

resources:
  - ../../base

namespace: production

# 生产环境补丁
patches:
  - target:
      kind: Deployment
      name: my-app
    patch: |
      - op: replace
        path: /spec/replicas
        value: 5
      - op: replace
        path: /spec/template/spec/containers/0/resources/requests/memory
        value: "512Mi"
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/memory
        value: "1Gi"
      - op: replace
        path: /spec/template/spec/containers/0/resources/requests/cpu
        value: "250m"
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/cpu
        value: "1000m"
  
  - target:
      kind: HorizontalPodAutoscaler
      name: my-app
    patch: |
      - op: replace
        path: /spec/minReplicas
        value: 5
      - op: replace
        path: /spec/maxReplicas
        value: 20

# 生产环境镜像
images:
  - name: my-app
    newName: registry.example.com/my-app
    newTag: v1.2.3

# 生产环境ConfigMap
configMapGenerator:
  - name: app-config
    behavior: merge
    literals:
      - LOG_LEVEL=warn
      - DATABASE_HOST=prod-db.example.com
      - CACHE_TTL=3600

# 生产环境额外资源
resources:
  - pdb.yaml
  - network-policy.yaml
```

### SOPS密钥管理

```yaml
# .sops.yaml
creation_rules:
  - path_regex: \.yaml$
    encrypted_regex: ^(data|stringData)$
    age: >-
      age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

```bash
# 加密Secret
sops --encrypt --in-place secret.yaml

# 解密查看
sops --decrypt secret.yaml

# 编辑加密文件
sops secret.yaml
```

```yaml
# secret.yaml (加密后)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  DB_PASSWORD: ENC[AES256_GCM,data:xxxxx,iv:xxxxx,tag:xxxxx,type:str]
  API_KEY: ENC[AES256_GCM,data:xxxxx,iv:xxxxx,tag:xxxxx,type:str]
sops:
  age:
    - recipient: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      enc: |
        -----BEGIN AGE ENCRYPTED FILE-----
        xxxxx
        -----END AGE ENCRYPTED FILE-----
  lastmodified: "2025-01-15T00:00:00Z"
  version: 3.8.1
```

## GitOps最佳实践

### 1. 仓库结构

```
gitops-configs/
├── README.md
├── .sops.yaml
├── infrastructure/
│   ├── base/
│   │   ├── cert-manager/
│   │   ├── ingress-nginx/
│   │   └── monitoring/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
├── apps/
│   ├── base/
│   │   ├── frontend/
│   │   ├── backend/
│   │   └── database/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
└── clusters/
    ├── dev/
    │   ├── flux-system/
    │   └── apps.yaml
    ├── staging/
    │   ├── flux-system/
    │   └── apps.yaml
    └── production/
        ├── flux-system/
        └── apps.yaml
```

### 2. 分支策略

```
main (生产环境配置)
  ├── develop (开发环境配置)
  │   ├── feature/* (功能分支)
  │   └── bugfix/* (修复分支)
  └── release/* (发布分支)
```

### 3. 变更流程

```yaml
# 变更流程配置
change_process:
  steps:
    - name: "创建分支"
      description: "从main分支创建feature分支"
      tool: "git"
    
    - name: "修改配置"
      description: "修改Kubernetes配置文件"
      tool: "编辑器"
    
    - name: "本地验证"
      description: "使用kustomize build验证"
      command: "kustomize build overlays/dev | kubectl apply --dry-run=client -f -"
    
    - name: "提交PR"
      description: "提交Pull Request到main分支"
      tool: "GitHub/GitLab"
    
    - name: "自动化检查"
      description: "运行CI检查"
      checks:
        - lint
        - validate
        - security-scan
    
    - name: "代码审查"
      description: "团队成员审查代码"
      required_approvals: 2
    
    - name: "合并"
      description: "合并到main分支"
      auto_merge: true
    
    - name: "自动部署"
      description: "GitOps控制器自动部署"
      tool: "ArgoCD/FluxCD"
```

### 4. 安全实践

```yaml
# RBAC配置
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: argocd-app-viewer
  namespace: argocd
rules:
  - apiGroups: ["argoproj.io"]
    resources: ["applications"]
    verbs: ["get", "list", "watch"]

---
# 审计日志
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
    resources:
      - group: "argoproj.io"
        resources: ["applications"]
  
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["secrets"]
```

### 5. 监控和告警

```yaml
# ArgoCD监控配置
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: argocd-metrics
  namespace: argocd
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: argocd-server
  endpoints:
  - port: metrics
    interval: 30s

---
# 告警规则
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: argocd-alerts
  namespace: argocd
spec:
  groups:
  - name: argocd
    rules:
    - alert: ArgoCDAppNotSynced
      expr: |
        argocd_app_info{sync_status!="Synced"} == 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "ArgoCD应用未同步"
        description: "应用 {{ $labels.name }} 已超过5分钟未同步"
    
    - alert: ArgoCDAppDegraded
      expr: |
        argocd_app_info{health_status="Degraded"} == 1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "ArgoCD应用健康状态降级"
        description: "应用 {{ $labels.name }} 健康状态为Degraded"
```

## GitOps工作流示例

### 完整部署流程

```yaml
# .github/workflows/gitops-deploy.yml
name: GitOps Deploy

on:
  push:
    branches: [main]
    paths:
      - 'apps/**'
      - 'infrastructure/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Kustomize
        uses: imranismail/setup-kustomize@v2
      
      - name: Validate configurations
        run: |
          kustomize build apps/overlays/dev | kubectl apply --dry-run=client -f -
          kustomize build apps/overlays/staging | kubectl apply --dry-run=client -f -
          kustomize build apps/overlays/production | kubectl apply --dry-run=client -f -
      
      - name: Run kubeval
        uses: instrumenta/kubeval-action@master
        with:
          files: apps/overlays/production
      
      - name: Run kubesec
        uses: controlplaneio/kubesec-action@master
        with:
          input: apps/overlays/production/deployment.yaml

  deploy-dev:
    needs: validate
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4
      
      - name: Update image tag
        run: |
          cd apps/overlays/dev
          kustomize edit set image my-app=registry.example.com/my-app:${{ github.sha }}
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Update dev image to ${{ github.sha }}"
          git push

  deploy-staging:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      
      - name: Update image tag
        run: |
          cd apps/overlays/staging
          kustomize edit set image my-app=registry.example.com/my-app:${{ github.sha }}
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Update staging image to ${{ github.sha }}"
          git push

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - uses: actions/checkout@v4
      
      - name: Update image tag
        run: |
          cd apps/overlays/production
          kustomize edit set image my-app=registry.example.com/my-app:${{ github.sha }}
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Update production image to ${{ github.sha }}"
          git push
```

## 常见问题解决

### 1. 同步冲突

```yaml
# 解决同步冲突
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  annotations:
    # 忽略特定资源的差异
    argocd.argoproj.io/manifest-generate-paths: |
      - /apps/my-app
    # 强制同步
    argocd.argoproj.io/sync-options: Force=true
```

### 2. 性能优化

```yaml
# 优化大型仓库
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  source:
    # 使用目录而不是整个仓库
    path: apps/my-app
    # 限制同步范围
    directory:
      recurse: false
      jsonnet: {}
      exclude: '.*'
```

### 3. 灾难恢复

```bash
# 备份ArgoCD应用
argocd app list -o yaml > apps-backup.yaml

# 恢复ArgoCD应用
kubectl apply -f apps-backup.yaml

# 重新同步所有应用
argocd app sync --all
```

## 相关页面

- [[CI-CD流水线设计]] - CI/CD集成
- [[基础设施即代码]] - 基础设施管理
- [[容器安全最佳实践]] - 安全实践
- [[SRE实践指南]] - 可靠性工程

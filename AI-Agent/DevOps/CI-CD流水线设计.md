---
title: CI/CD流水线设计
aliases:
  - CI/CD Pipeline Design
  - 持续集成持续部署
tags:
  - devops
  - ci-cd
  - jenkins
  - gitlab-ci
  - github-actions
  - argocd
  - automation
type: reference
status: active
created: 2025-01-15
updated: 2025-01-15
source: internal
difficulty: intermediate
project: AI-Agent
---

# CI/CD流水线设计

## 概述

CI/CD（持续集成/持续部署）是现代软件开发的核心实践，通过自动化构建、测试和部署流程，提高软件交付速度和质量。

## 主流CI/CD工具对比

| 特性 | Jenkins | GitLab CI | GitHub Actions | ArgoCD |
|------|---------|-----------|----------------|--------|
| 部署方式 | 自托管 | SaaS/自托管 | SaaS | 自托管 |
| 配置语言 | Groovy | YAML | YAML | YAML/CRD |
| 学习曲线 | 中等 | 低 | 低 | 中等 |
| 生态系统 | 丰富 | 集成 | Marketplace | K8s原生 |
| 适用场景 | 企业级 | 全流程 | 开源项目 | K8s部署 |

## Jenkins

### 基础Pipeline配置

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.example.com'
        APP_NAME = 'my-application'
        VERSION = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh '''
                    echo "Building application..."
                    mvn clean package -DskipTests
                '''
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'mvn test'
                    }
                    post {
                        always {
                            junit 'target/surefire-reports/*.xml'
                        }
                    }
                }
                
                stage('Integration Tests') {
                    steps {
                        sh 'mvn verify -P integration-tests'
                    }
                }
                
                stage('Code Analysis') {
                    steps {
                        withSonarQubeEnv('sonarqube') {
                            sh 'mvn sonar:sonar'
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_REGISTRY}/${APP_NAME}:${VERSION}")
                }
            }
        }
        
        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'registry-credentials') {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                sh """
                    kubectl set image deployment/${APP_NAME} \
                        ${APP_NAME}=${DOCKER_REGISTRY}/${APP_NAME}:${VERSION} \
                        --namespace=staging
                """
            }
        }
        
        stage('Deploy to Production') {
            input {
                message "Deploy to production?"
                ok "Yes, deploy it"
            }
            steps {
                sh """
                    kubectl set image deployment/${APP_NAME} \
                        ${APP_NAME}=${DOCKER_REGISTRY}/${APP_NAME}:${VERSION} \
                        --namespace=production
                """
            }
        }
    }
    
    post {
        success {
            slackSend(
                color: 'good',
                message: "Build ${env.BUILD_NUMBER} succeeded for ${APP_NAME}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Build ${env.BUILD_NUMBER} failed for ${APP_NAME}"
            )
        }
    }
}
```

### 多分支Pipeline

```groovy
// Jenkinsfile - 多分支策略
pipeline {
    agent any
    
    triggers {
        pollSCM('H/5 * * * *')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        stage('Determine Branch') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        env.DEPLOY_ENV = 'production'
                        env.APPROVAL_REQUIRED = true
                    } else if (env.BRANCH_NAME == 'develop') {
                        env.DEPLOY_ENV = 'staging'
                        env.APPROVAL_REQUIRED = false
                    } else {
                        env.DEPLOY_ENV = 'dev'
                        env.APPROVAL_REQUIRED = false
                    }
                }
            }
        }
        
        // ... 其他阶段
    }
}
```

## GitLab CI

### 完整配置示例

```yaml
# .gitlab-ci.yml
variables:
  DOCKER_REGISTRY: registry.gitlab.com
  DOCKER_IMAGE: $DOCKER_REGISTRY/$CI_PROJECT_PATH
  KUBE_NAMESPACE: default

stages:
  - build
  - test
  - security
  - package
  - deploy

# 全局缓存配置
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .npm/

# 构建阶段
build:
  stage: build
  image: node:18-alpine
  script:
    - npm ci --cache .npm
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour

# 单元测试
unit-test:
  stage: test
  image: node:18-alpine
  script:
    - npm ci
    - npm run test:unit -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

# 集成测试
integration-test:
  stage: test
  image: node:18-alpine
  services:
    - postgres:14
    - redis:7
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: testuser
    POSTGRES_PASSWORD: testpass
    DATABASE_URL: postgres://testuser:testpass@postgres:5432/testdb
    REDIS_URL: redis://redis:6379
  script:
    - npm ci
    - npm run test:integration

# 安全扫描
sast:
  stage: security
  include:
    - template: Security/SAST.gitlab-ci.yml

dependency-scanning:
  stage: security
  include:
    - template: Security/Dependency-Scanning.gitlab-ci.yml

container-scanning:
  stage: security
  include:
    - template: Security/Container-Scanning.gitlab-ci.yml

# Docker构建
build-image:
  stage: package
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHA .
    - docker tag $DOCKER_IMAGE:$CI_COMMIT_SHA $DOCKER_IMAGE:latest
    - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA
    - docker push $DOCKER_IMAGE:latest
  only:
    - main
    - tags

# 部署到Staging
deploy-staging:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - kubectl config use-context staging
    - |
      kubectl set image deployment/myapp \
        myapp=$DOCKER_IMAGE:$CI_COMMIT_SHA \
        -n $KUBE_NAMESPACE
    - kubectl rollout status deployment/myapp -n $KUBE_NAMESPACE --timeout=300s
  only:
    - develop

# 部署到Production
deploy-production:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://example.com
  script:
    - kubectl config use-context production
    - |
      kubectl set image deployment/myapp \
        myapp=$DOCKER_IMAGE:$CI_COMMIT_SHA \
        -n $KUBE_NAMESPACE
    - kubectl rollout status deployment/myapp -n $KUBE_NAMESPACE --timeout=300s
  only:
    - main
  when: manual
```

## GitHub Actions

### 完整工作流配置

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 代码质量检查
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run ESLint
        run: npm run lint
      
      - name: Run Prettier
        run: npm run format:check

  # 单元测试
  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        node-version: [16, 18, 20]
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm run test:coverage
        env:
          DATABASE_URL: postgres://testuser:testpass@localhost:5432/testdb
      
      - name: Upload coverage
        if: matrix.node-version == 18
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  # 安全扫描
  security:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # 构建和推送Docker镜像
  build-and-push:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.event_name == 'push'
    permissions:
      contents: read
      packages: write
    
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      version: ${{ steps.version.outputs.version }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate version
        id: version
        run: echo "version=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # 部署到Staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.example.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy to staging
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ needs.build-and-push.outputs.image-tag }} \
            -n staging
          kubectl rollout status deployment/myapp -n staging --timeout=300s

  # 部署到Production
  deploy-production:
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://example.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
      
      - name: Deploy to production
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ needs.build-and-push.outputs.image-tag }} \
            -n production
          kubectl rollout status deployment/myapp -n production --timeout=300s
```

## ArgoCD

### Application配置

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-application
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  
  source:
    repoURL: https://github.com/org/k8s-manifests.git
    targetRevision: HEAD
    path: apps/my-application/overlays/production
    
    # 使用Kustomize
    kustomize:
      images:
        - myapp=registry.example.com/myapp:v1.2.3
  
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
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  
  # 健康检查配置
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
```

### AppProject配置

```yaml
# argocd-project.yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: my-project
  namespace: argocd
spec:
  description: "My Project Applications"
  
  sourceRepos:
    - 'https://github.com/org/k8s-manifests.git'
    - 'https://charts.example.com/*'
  
  destinations:
    - namespace: 'staging'
      server: https://kubernetes.default.svc
    - namespace: 'production'
      server: https://kubernetes.default.svc
  
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
  
  namespaceResourceBlacklist:
    - group: ''
      kind: ResourceQuota
    - group: ''
      kind: LimitRange
  
  roles:
    - name: developer
      description: "Developer access"
      policies:
        - p, proj:my-project:developer, applications, get, my-project/*, allow
        - p, proj:my-project:developer, applications, sync, my-project/*, allow
      groups:
        - dev-team
  
  syncWindows:
    - kind: allow
      schedule: '0 8-18 * * 1-5'
      duration: 10h
      applications:
        - '*'
      namespaces:
        - production
    - kind: deny
      schedule: '0 0 * * 0,6'
      duration: 48h
      applications:
        - '*'
      namespaces:
        - production
```

## 最佳实践

### 1. 流水线设计原则

- **快速反馈**: 将快速检查（lint、单元测试）放在前面
- **并行执行**: 独立任务并行运行以缩短总时间
- **缓存利用**: 合理使用缓存减少重复构建
- **失败快速**: 设置超时和失败阈值

### 2. 分支策略

```
main (production)
  ↑
develop (staging)
  ↑
feature/* (dev)
```

### 3. 环境管理

- 使用独立的配置文件管理不同环境
- 敏感信息使用Secret管理
- 环境变量分离配置

### 4. 安全实践

- 扫描依赖漏洞
- 镜像安全扫描
- Secret不硬编码
- 最小权限原则

### 5. 监控与告警

- 构建时间监控
- 失败率告警
- 部署频率统计
- 变更前置时间

## 相关页面

- [[基础设施即代码]] - 基础设施自动化管理
- [[容器安全最佳实践]] - 容器安全相关实践
- [[GitOps工作流]] - GitOps部署模式
- [[SRE实践指南]] - 可靠性工程实践

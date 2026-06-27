---
title: Kubernetes容器编排指南
aliases: [K8s教程, 容器编排, Kubernetes命令]
tags: [kubernetes, 容器编排, 运维]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: advanced
project: 运维
---
# Kubernetes 容器编排指南

## 概述

本指南提供Kubernetes容器编排的配置方法和最佳实践。

## 1. 基础概念

### 核心组件

- **Master节点**：API Server、Scheduler、Controller Manager、etcd
- **Node节点**：kubelet、kube-proxy、Container Runtime
- **Pod**：最小部署单元，包含一个或多个容器
- **Service**：服务发现和负载均衡
- **Deployment**：无状态应用部署
- **StatefulSet**：有状态应用部署
- **DaemonSet**：每节点运行一个Pod
- **Job/CronJob**：批处理任务

### 常用资源

```yaml
# Pod
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx:latest

# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
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
      - name: my-container
        image: nginx:latest

# Service
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

## 2. 常用命令

### 集群管理

```bash
# 查看集群信息
kubectl cluster-info

# 查看节点
kubectl get nodes

# 查看节点详情
kubectl describe node node-name

# 查看组件状态
kubectl get componentstatuses
```

### 资源管理

```bash
# 创建资源
kubectl apply -f resource.yaml

# 查看资源
kubectl get pods
kubectl get services
kubectl get deployments

# 查看资源详情
kubectl describe pod pod-name

# 删除资源
kubectl delete pod pod-name
kubectl delete -f resource.yaml
```

### 日志调试

```bash
# 查看Pod日志
kubectl logs pod-name

# 实时查看日志
kubectl logs -f pod-name

# 查看容器日志
kubectl logs pod-name -c container-name

# 进入容器
kubectl exec -it pod-name -- /bin/bash

# 查看Pod事件
kubectl get events --field-selector involvedObject.name=pod-name
```

## 3. Pod配置

### 资源限制

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx:latest
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### 环境变量

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx:latest
    env:
    - name: MY_VAR
      value: "my-value"
    - name: SECRET_VAR
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: password
```

### 卷挂载

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx:latest
    volumeMounts:
    - name: my-volume
      mountPath: /data
  volumes:
  - name: my-volume
    persistentVolumeClaim:
      claimName: my-pvc
```

## 4. Deployment配置

### 滚动更新

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:1.19
```

### 回滚操作

```bash
# 查看更新历史
kubectl rollout history deployment/my-deployment

# 回滚到上一版本
kubectl rollout undo deployment/my-deployment

# 回滚到指定版本
kubectl rollout undo deployment/my-deployment --to-revision=2
```

## 5. Service配置

### 服务类型

```yaml
# ClusterIP（默认）
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80

# NodePort
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080

# LoadBalancer
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80
```

## 6. 配置管理

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  config.yaml: |
    database:
      host: localhost
      port: 5432
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=  # base64编码
  password: cGFzc3dvcmQ=  # base64编码
```

## 7. 存储配置

### PersistentVolume

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data
```

### PersistentVolumeClaim

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

## 8. 网络配置

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```

## 9. 监控诊断

### 资源监控

```bash
# 查看资源使用
kubectl top pods
kubectl top nodes

# 查看Pod状态
kubectl get pods -o wide

# 查看Pod详情
kubectl describe pod pod-name
```

### 故障排查

```bash
# 查看Pod日志
kubectl logs pod-name

# 查看前一个容器日志
kubectl logs pod-name --previous

# 进入容器调试
kubectl exec -it pod-name -- /bin/bash

# 查看事件
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 相关页面

- [[Docker容器化指南]]
- [[Linux运维常用命令]]
- [[Nginx配置指南]]

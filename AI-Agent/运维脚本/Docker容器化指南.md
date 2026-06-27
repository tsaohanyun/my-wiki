---
title: Docker容器化指南
aliases: [Docker教程, 容器化, Docker命令]
tags: [docker, 容器化, 部署]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# Docker 容器化指南

## 概述

本指南提供Docker容器化的常用命令和最佳实践。

## 1. 基础命令

### 镜像操作

```bash
# 拉取镜像
docker pull nginx:latest

# 查看本地镜像
docker images

# 删除镜像
docker rmi nginx:latest

# 构建镜像
docker build -t my-app:v1.0 .
```

### 容器操作

```bash
# 运行容器
docker run -d -p 80:80 --name my-nginx nginx

# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 停止容器
docker stop my-nginx

# 启动容器
docker start my-nginx

# 删除容器
docker rm my-nginx
```

## 2. Dockerfile编写

### 基础模板

```dockerfile
# 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app.py"]
```

### 多阶段构建

```dockerfile
# 构建阶段
FROM python:3.9 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .
CMD ["python", "app.py"]
```

## 3. Docker Compose

### 基础模板

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重建服务
docker-compose up -d --build
```

## 4. 数据管理

### 数据卷

```bash
# 创建数据卷
docker volume create my-volume

# 查看数据卷
docker volume ls

# 使用数据卷
docker run -v my-volume:/app/data nginx
```

### 绑定挂载

```bash
# 绑定挂载
docker run -v /host/path:/container/path nginx

# 只读挂载
docker run -v /host/path:/container/path:ro nginx
```

## 5. 网络管理

### 网络操作

```bash
# 创建网络
docker network create my-network

# 查看网络
docker network ls

# 连接容器到网络
docker network connect my-network my-container

# 断开网络
docker network disconnect my-network my-container
```

### 网络模式

```bash
# 桥接模式（默认）
docker run --network bridge nginx

# 主机模式
docker run --network host nginx

# 无网络
docker run --network none nginx
```

## 6. 日志管理

### 日志查看

```bash
# 查看容器日志
docker logs my-container

# 实时查看日志
docker logs -f my-container

# 查看最后100行
docker logs --tail 100 my-container
```

### 日志驱动

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

## 7. 资源限制

### CPU限制

```bash
# 限制CPU使用
docker run --cpus="1.5" nginx

# CPU份额
docker run --cpu-shares=512 nginx
```

### 内存限制

```bash
# 限制内存
docker run --memory="512m" nginx

# 内存+Swap
docker run --memory="512m" --memory-swap="1g" nginx
```

## 8. 安全实践

### 镜像安全

```bash
# 使用官方镜像
docker pull nginx:latest

# 扫描镜像漏洞
docker scan nginx:latest

# 使用最小基础镜像
FROM alpine:3.14
```

### 容器安全

```bash
# 以非root用户运行
RUN adduser -D myuser
USER myuser

# 只读文件系统
docker run --read-only nginx

# 限制capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx
```

## 9. 常用镜像

### 开发环境

```bash
# Python
docker pull python:3.9-slim

# Node.js
docker pull node:16-alpine

# Java
docker pull openjdk:11-jre-slim
```

### 数据库

```bash
# MySQL
docker pull mysql:8.0

# PostgreSQL
docker pull postgres:13

# MongoDB
docker pull mongo:5.0

# Redis
docker pull redis:6-alpine
```

### Web服务器

```bash
# Nginx
docker pull nginx:latest

# Apache
docker pull httpd:2.4
```

## 相关页面

- [[Python运维脚本库]]
- [[SSH隧道与远程管理]]
- [[Hermes-Agent架构总览]]

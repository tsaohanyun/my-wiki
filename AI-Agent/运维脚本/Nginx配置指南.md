---
title: Nginx配置指南
aliases: [Nginx教程, Web服务器, 反向代理]
tags: [nginx, web服务器, 运维]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# Nginx 配置指南

## 概述

本指南提供Nginx Web服务器的配置方法和最佳实践。

## 1. 基础配置

### 配置文件结构

```nginx
# 主配置文件
/etc/nginx/nginx.conf

# 站点配置
/etc/nginx/conf.d/*.conf
/etc/nginx/sites-enabled/*
```

### 基础配置示例

```nginx
# 全局配置
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

# 事件配置
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

# HTTP配置
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
```

## 2. 虚拟主机

### 静态网站

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### PHP网站

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.php index.html;
    
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

## 3. 反向代理

### 基础反向代理

```nginx
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 负载均衡

```nginx
upstream backend {
    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com;
}

server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### WebSocket代理

```nginx
server {
    listen 80;
    server_name example.com;
    
    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 4. SSL配置

### HTTPS配置

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    
    ssl_certificate /etc/nginx/ssl/example.com.crt;
    ssl_certificate_key /etc/nginx/ssl/example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## 5. 缓存配置

### 静态文件缓存

```nginx
server {
    listen 80;
    server_name example.com;
    
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

### 代理缓存

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m use_temp_path=off;

server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_cache my_cache;
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
        proxy_pass http://localhost:8080;
    }
}
```

## 6. 安全配置

### 限制访问

```nginx
server {
    listen 80;
    server_name example.com;
    
    # 限制IP访问
    allow 192.168.1.0/24;
    deny all;
    
    # 限制请求方法
    if ($request_method !~ ^(GET|HEAD|POST)$) {
        return 405;
    }
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### 防盗链

```nginx
server {
    listen 80;
    server_name example.com;
    
    location ~* \.(jpg|jpeg|png|gif)$ {
        valid_referers none blocked server_names *.example.com;
        if ($invalid_referer) {
            return 403;
        }
    }
}
```

## 7. 性能优化

### 连接优化

```nginx
http {
    # 连接超时
    keepalive_timeout 65;
    client_body_timeout 10;
    client_header_timeout 10;
    send_timeout 10;
    
    # 缓冲区
    client_body_buffer_size 10K;
    client_header_buffer_size 1k;
    client_max_body_size 8m;
    large_client_header_buffers 4 4k;
}
```

### 工作进程优化

```nginx
# 根据CPU核心数设置
worker_processes auto;

# 每个进程的最大连接数
events {
    worker_connections 1024;
}
```

## 8. 日志管理

### 日志配置

```nginx
# 访问日志
access_log /var/log/nginx/access.log;

# 错误日志
error_log /var/log/nginx/error.log warn;

# 自定义日志格式
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                '$status $body_bytes_sent "$http_referer" '
                '"$http_user_agent" "$http_x_forwarded_for"';
```

### 日志轮转

```bash
# /etc/logrotate.d/nginx
/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 nginx adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

## 9. 常用命令

```bash
# 启动Nginx
sudo systemctl start nginx

# 停止Nginx
sudo systemctl stop nginx

# 重启Nginx
sudo systemctl restart nginx

# 重新加载配置
sudo nginx -s reload

# 测试配置
sudo nginx -t

# 查看版本
nginx -v
```

## 相关页面

- [[Docker容器化指南]]
- [[Linux运维常用命令]]
- [[SSH隧道与远程管理]]

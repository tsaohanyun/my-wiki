---
title: API设计指南
aliases: [API设计, RESTful API, 接口设计]
tags: [api, rest, 设计]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 开发
---
# API 设计指南

## 概述

本指南提供RESTful API设计的最佳实践。

## 1. URL设计

### 命名规范

```bash
# 使用名词复数
GET /api/users          # 获取用户列表
GET /api/users/123      # 获取单个用户
POST /api/users         # 创建用户
PUT /api/users/123      # 更新用户
DELETE /api/users/123   # 删除用户

# 使用小写字母和连字符
GET /api/user-profiles  # ✅ 正确
GET /api/userProfiles   # ❌ 错误（驼峰）
GET /api/user_profiles  # ❌ 错误（下划线）

# 层级关系
GET /api/users/123/orders           # 用户的订单
GET /api/users/123/orders/456       # 用户的特定订单
```

### 查询参数

```bash
# 过滤
GET /api/users?status=active
GET /api/users?role=admin&status=active

# 排序
GET /api/users?sort=name
GET /api/users?sort=-created_at    # 降序
GET /api/users?sort=name,-created_at

# 分页
GET /api/users?page=1&per_page=20
GET /api/users?offset=0&limit=20

# 搜索
GET /api/users?q=john
GET /api/users?search=john&fields=name,email
```

## 2. HTTP方法

### 方法语义

```bash
# GET - 获取资源
GET /api/users           # 获取列表
GET /api/users/123       # 获取单个

# POST - 创建资源
POST /api/users          # 创建用户

# PUT - 全量更新
PUT /api/users/123       # 更新用户（全量）

# PATCH - 部分更新
PATCH /api/users/123     # 更新用户（部分）

# DELETE - 删除资源
DELETE /api/users/123    # 删除用户
```

### 幂等性

```bash
# 幂等（多次调用结果相同）
GET /api/users/123       # 幂等
PUT /api/users/123       # 幂等
DELETE /api/users/123    # 幂等

# 非幂等（多次调用结果不同）
POST /api/users          # 非幂等
```

## 3. 请求/响应格式

### 请求格式

```json
// POST /api/users
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword",
    "role": "user"
}

// PATCH /api/users/123
{
    "name": "John Smith"
}
```

### 响应格式

```json
// 成功响应
{
    "code": 200,
    "message": "Success",
    "data": {
        "id": 123,
        "name": "John Doe",
        "email": "john@example.com"
    }
}

// 列表响应
{
    "code": 200,
    "message": "Success",
    "data": {
        "items": [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ],
        "total": 100,
        "page": 1,
        "per_page": 20
    }
}

// 错误响应
{
    "code": 400,
    "message": "Validation Error",
    "errors": [
        {
            "field": "email",
            "message": "Invalid email format"
        }
    ]
}
```

## 4. 状态码

### 常用状态码

```bash
# 成功
200 OK                    # GET/PUT/PATCH成功
201 Created               # POST成功
204 No Content            # DELETE成功

# 客户端错误
400 Bad Request           # 请求参数错误
401 Unauthorized          # 未认证
403 Forbidden             # 无权限
404 Not Found             # 资源不存在
409 Conflict              # 资源冲突
422 Unprocessable Entity  # 数据验证失败
429 Too Many Requests     # 请求过于频繁

# 服务端错误
500 Internal Server Error # 服务器内部错误
502 Bad Gateway           # 网关错误
503 Service Unavailable   # 服务不可用
```

## 5. 认证授权

### JWT认证

```bash
# 登录
POST /api/auth/login
{
    "email": "john@example.com",
    "password": "securepassword"
}

# 响应
{
    "code": 200,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600
    }
}

# 使用Token
GET /api/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key认证

```bash
# 请求头
GET /api/users
X-API-Key: your-api-key

# 查询参数
GET /api/users?api_key=your-api-key
```

## 6. 版本控制

### URL版本

```bash
GET /api/v1/users
GET /api/v2/users
```

### 请求头版本

```bash
GET /api/users
Accept: application/vnd.myapp.v1+json
```

## 7. 限流

### 响应头

```bash
# 限流信息
X-RateLimit-Limit: 1000        # 总配额
X-RateLimit-Remaining: 999     # 剩余配额
X-RateLimit-Reset: 1625097600  # 重置时间

# 超限响应
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

## 8. 错误处理

### 错误响应格式

```json
{
    "code": 400,
    "message": "Validation Error",
    "errors": [
        {
            "field": "email",
            "code": "invalid_format",
            "message": "Invalid email format"
        },
        {
            "field": "password",
            "code": "too_short",
            "message": "Password must be at least 8 characters"
        }
    ],
    "request_id": "req_123456"
}
```

### 常见错误码

```json
{
    "VALIDATION_ERROR": "数据验证失败",
    "AUTHENTICATION_ERROR": "认证失败",
    "AUTHORIZATION_ERROR": "授权失败",
    "NOT_FOUND": "资源不存在",
    "CONFLICT": "资源冲突",
    "RATE_LIMIT_EXCEEDED": "请求过于频繁",
    "INTERNAL_ERROR": "服务器内部错误"
}
```

## 9. 文档规范

### OpenAPI/Swagger

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /api/users:
    get:
      summary: Get user list
      parameters:
        - name: page
          in: query
          schema:
            type: integer
        - name: per_page
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
```

## 10. 安全实践

### 输入验证

```python
# 验证规则
{
    "name": {
        "type": "string",
        "min_length": 1,
        "max_length": 100
    },
    "email": {
        "type": "string",
        "format": "email"
    },
    "age": {
        "type": "integer",
        "minimum": 0,
        "maximum": 150
    }
}
```

### SQL注入防护

```python
# ❌ 错误（字符串拼接）
query = f"SELECT * FROM users WHERE name = '{name}'"

# ✅ 正确（参数化查询）
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (name,))
```

### CORS配置

```python
# 允许的源
Access-Control-Allow-Origin: https://example.com

# 允许的方法
Access-Control-Allow-Methods: GET, POST, PUT, DELETE

# 允许的头
Access-Control-Allow-Headers: Content-Type, Authorization
```

## 相关页面

- [[Python脚本编程指南]]
- [[JavaScript前端开发指南]]
- [[设计模式指南]]

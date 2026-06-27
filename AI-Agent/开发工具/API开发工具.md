---
title: API开发工具
aliases:
  - API工具
  - HTTP工具
  - REST API
tags:
  - 开发工具
  - API
  - HTTP
  - Postman
  - Swagger
type: wiki
status: active
created: 2026-06-27
updated: 2026-06-27
source: 内部整理
difficulty: intermediate
project: AI-Agent
---

# API开发工具

## 1. Postman

### 核心功能
- **Collections** — API请求集合，支持文件夹组织
- **Environment** — 多环境变量（dev/staging/prod）
- **Pre/Post Scripts** — 请求前后执行JavaScript
- **Tests** — 自动化API测试
- **Mock Server** — 模拟API响应
- **Monitors** — 定时监控API健康

### 环境变量配置
```json
// Environment: Development
{
  "base_url": "http://localhost:3000",
  "api_key": "dev-abc123",
  "user_id": "test-user-001"
}

// Environment: Production
{
  "base_url": "https://api.example.com",
  "api_key": "prod-xyz789",
  "user_id": "admin-001"
}
```

### Pre-request Script 示例
```javascript
// 自动生成签名
const timestamp = Date.now();
const secret = pm.environment.get("api_secret");
const signature = CryptoJS.HmacSHA256(timestamp.toString(), secret).toString();

pm.environment.set("timestamp", timestamp);
pm.environment.set("signature", signature);

// 从登录接口获取token
pm.sendRequest({
  url: pm.environment.get("base_url") + "/auth/login",
  method: "POST",
  header: { "Content-Type": "application/json" },
  body: {
    mode: "raw",
    raw: JSON.stringify({ username: "admin", password: "secret" })
  }
}, (err, res) => {
  pm.environment.set("token", res.json().token);
});
```

### Test Script 示例
```javascript
// 状态码检查
pm.test("Status code is 200", () => {
  pm.response.to.have.status(200);
});

// 响应时间检查
pm.test("Response time < 500ms", () => {
  pm.expect(pm.response.responseTime).to.be.below(500);
});

// JSON Schema验证
pm.test("Valid response schema", () => {
  const schema = {
    type: "object",
    required: ["id", "name", "email"],
    properties: {
      id: { type: "number" },
      name: { type: "string" },
      email: { type: "string", format: "email" }
    }
  };
  pm.response.to.have.jsonSchema(schema);
});

// 提取数据到变量
pm.test("Extract token", () => {
  const json = pm.response.json();
  pm.environment.set("auth_token", json.token);
});
```

### Collection Runner
```bash
# CLI运行（Newman）
npm install -g newman

# 运行collection
newman run collection.json -e environment.json

# 生成HTML报告
newman run collection.json -r html

# 持续集成
newman run collection.json \
  --reporters cli,junit \
  --reporter-junit-export results.xml
```

---

## 2. Insomnia

### 特点
- 轻量级，启动快
- 原生GraphQL支持
- 模板标签（动态变量）
- 设计模式（API规范编辑）
- 插件系统

### 环境配置
```yaml
# Base Environment
base_url: http://localhost:8080
timeout: 30s

# Sub Environment: Development
base_url: http://localhost:3000
api_token: dev-token-123

# Sub Environment: Production
base_url: https://api.prod.com
api_token: ${PROD_TOKEN}  # 从系统环境变量读取
```

### 模板标签
```
# 动态时间戳
{% now 'iso-8601', '' %}

# 随机UUID
{% uuid 'v4' }

# 随机数
{% randomInt 1, 100 %}

# 从响应中提取
{% response 'body', 'req_123', 'b64::data.token::b64', 'never' %}
```

### GraphQL 支持
```graphql
# 查询
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    posts {
      title
      createdAt
    }
  }
}

# 变量
{
  "id": "123"
}
```

---

## 3. curl

### 基础用法
```bash
# GET请求
curl https://api.example.com/users

# 带Header
curl -H "Authorization: Bearer token123" \
     -H "Content-Type: application/json" \
     https://api.example.com/users

# POST JSON
curl -X POST https://api.example.com/users \
     -H "Content-Type: application/json" \
     -d '{"name": "John", "email": "john@example.com"}'

# POST 表单
curl -X POST https://api.example.com/upload \
     -F "file=@./photo.jpg" \
     -F "name=test"

# PUT更新
curl -X PUT https://api.example.com/users/1 \
     -H "Content-Type: application/json" \
     -d '{"name": "Jane"}'

# DELETE
curl -X DELETE https://api.example.com/users/1
```

### 高级选项
```bash
# 详细输出（调试）
curl -v https://api.example.com/users

# 只看HTTP头
curl -I https://api.example.com/users

# 保存响应到文件
curl -o response.json https://api.example.com/data

# 跟随重定向
curl -L https://api.example.com/redirect

# 设置超时
curl --connect-timeout 5 --max-time 30 https://api.example.com

# 忽略SSL验证（开发环境）
curl -k https://localhost:8443/api

# 使用代理
curl -x http://proxy:8080 https://api.example.com

# 限速
curl --limit-rate 100K https://api.example.com/large-file

# 并发请求（curl 7.66+）
curl --parallel --parallel-max 5 \
  https://api.example.com/1 \
  https://api.example.com/2 \
  https://api.example.com/3
```

### 认证方式
```bash
# Basic Auth
curl -u username:password https://api.example.com

# Bearer Token
curl -H "Authorization: Bearer eyJhbGc..." https://api.example.com

# API Key Header
curl -H "X-API-Key: my-api-key" https://api.example.com

# Client Certificate
curl --cert client.pem --key key.pem https://api.example.com
```

---

## 4. HTTPie

### 安装
```bash
pip install httpie
# 或
brew install httpie
```

### 核心用法（比curl更友好）
```bash
# GET（默认）
http GET https://api.example.com/users

# POST JSON（自动设置Content-Type）
http POST https://api.example.com/users \
  name=John \
  email=john@example.com \
  age:=25  # := 表示非字符串类型

# 带Header
http GET https://api.example.com/users \
  Authorization:"Bearer token123"

# 表单提交
http --form POST https://api.example.com/upload \
  file@./photo.jpg

# 文件上传
http --form POST https://api.example.com/upload \
  file@data.json

# 下载文件
http --download https://api.example.com/file.pdf

# 输出选项
http --print=HhBb GET https://api.example.com/users
# H=请求头 h=响应头 B=请求体 b=响应体

# 会话管理（自动保存cookie）
http --session=login POST https://api.example.com/auth \
  username=admin password=secret

http --session=login GET https://api.example.com/dashboard
```

### 与curl对比
```bash
# curl
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "age": 25}'

# httpie（等价）
http POST https://api.example.com/users name=John age:=25
```

---

## 5. Swagger / OpenAPI

### OpenAPI规范示例
```yaml
openapi: 3.0.3
info:
  title: 用户管理API
  version: 1.0.0
  description: 用户CRUD操作API

servers:
  - url: http://localhost:3000/api/v1
    description: 开发环境
  - url: https://api.example.com/v1
    description: 生产环境

paths:
  /users:
    get:
      summary: 获取用户列表
      tags: [Users]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  total:
                    type: integer

    post:
      summary: 创建用户
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        '201':
          description: 创建成功

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
          format: email
        createdAt:
          type: string
          format: date-time

    CreateUser:
      type: object
      required: [name, email]
      properties:
        name:
          type: string
          minLength: 2
          maxLength: 50
        email:
          type: string
          format: email
```

### Swagger UI 配置（Express）
```javascript
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'My API',
      version: '1.0.0',
    },
  },
  apis: ['./routes/*.js'], // 注释生成文档
};

const specs = swaggerJsdoc(options);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));
```

### 代码注释生成文档
```javascript
/**
 * @swagger
 * /users/{id}:
 *   get:
 *     summary: 根据ID获取用户
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: 成功
 *       404:
 *         description: 用户不存在
 */
router.get('/users/:id', async (req, res) => {
  // ...
});
```

---

## 最佳实践

1. **统一规范** — 团队使用统一的API设计规范（RESTful/GraphQL）
2. **环境分离** — 严格区分dev/staging/prod环境配置
3. **自动化测试** — 用Newman或httpie脚本在CI中跑API测试
4. **文档先行** — 先写OpenAPI规范，再实现接口
5. **版本控制** — URL路径 `/v1/` 或 Header 版本管理
6. **错误格式统一** — `{ "error": { "code": "xxx", "message": "xxx" } }`
7. **限流和重试** — 客户端实现指数退避重试策略

---

## 相关页面

- [[VSCode高效使用指南]]
- [[Git高级技巧]]
- [[命令行效率工具]]
- [[数据库客户端工具]]

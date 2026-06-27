---
title: Web应用安全
aliases:
  - Web Security
  - Web App Security
  - Web应用防护
tags:
  - security
  - web
  - owasp
  - xss
  - csrf
  - sql-injection
type: reference
status: active
created: 2026-06-27
updated: 2026-06-27
source: OWASP Foundation
difficulty: intermediate
project: AI-Agent
---

# Web应用安全

## 概述

Web应用安全是保护Web应用程序免受各种网络攻击的实践。本文档涵盖OWASP Top 10、常见攻击类型及防御策略。

---

## OWASP Top 10 (2021)

| 排名 | 风险类别 | 描述 |
|------|----------|------|
| A01 | Broken Access Control | 访问控制失效，用户越权操作 |
| A02 | Cryptographic Failures | 加密机制失效，敏感数据泄露 |
| A03 | Injection | 注入攻击（SQL、NoSQL、OS、LDAP） |
| A04 | Insecure Design | 不安全的设计模式 |
| A05 | Security Misconfiguration | 安全配置错误 |
| A06 | Vulnerable Components | 使用含漏洞的组件 |
| A07 | Identity & Auth Failures | 身份认证和认证失败 |
| A08 | Software & Data Integrity | 软件和数据完整性失效 |
| A09 | Security Logging Failures | 安全日志和监控不足 |
| A10 | SSRF | 服务端请求伪造 |

---

## XSS（跨站脚本攻击）

### 攻击类型

| 类型 | 说明 | 持久性 |
|------|------|--------|
| **反射型 XSS** | 恶意脚本通过URL参数注入 | 非持久 |
| **存储型 XSS** | 恶意脚本存储在服务器端 | 持久 |
| **DOM型 XSS** | 通过DOM操作在客户端执行 | 非持久 |

### 防御措施

```javascript
// 1. 输出编码（HTML上下文）
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// 2. 使用textContent代替innerHTML
element.textContent = userInput;  // 安全
// element.innerHTML = userInput;  // 危险！

// 3. CSP头配置
// Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'
```

```python
# Python - 使用Jinja2自动转义
from markupsafe import escape
safe_output = escape(user_input)

# Django模板自动转义
# {{ user_input }}  <!-- 自动转义 -->
# {{ user_input|safe }}  <!-- 标记为安全，谨慎使用 -->
```

---

## CSRF（跨站请求伪造）

### 攻击原理

```
用户登录 bank.com → 获取Cookie
         ↓
访问恶意站点 → 自动发起请求到 bank.com/transfer
         ↓
浏览器携带Cookie → 服务器认为是合法请求
```

### 防御实现

```python
# Django CSRF保护
from django.middleware.csrf import CsrfViewMiddleware

# 模板中使用
# <form method="post">
#   {% csrf_token %}
#   ...
# </form>

# Flask CSRF保护
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

```javascript
// 前端 - 设置自定义请求头
fetch('/api/transfer', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': getCsrfToken()  // 自定义头触发CORS预检
  },
  body: JSON.stringify(data)
});

// SameSite Cookie属性
document.cookie = 'session=abc; SameSite=Strict; Secure; HttpOnly';
```

---

## SQL注入

### 攻击示例

```sql
-- 原始查询
SELECT * FROM users WHERE id = '1';

-- 注入攻击
SELECT * FROM users WHERE id = '1' OR '1'='1';
SELECT * FROM users WHERE id = '1'; DROP TABLE users;--';
```

### 防御措施

```python
# ✅ 参数化查询（防止SQL注入）
import sqlite3
conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

# 安全 - 参数化查询
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# 危险 - 字符串拼接
# cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# ✅ 使用ORM（SQLAlchemy）
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:///db.sqlite')

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM users WHERE id = :id"),
        {"id": user_id}
    )
```

```javascript
// Node.js - 使用参数化查询
const mysql = require('mysql2/promise');
const connection = await mysql.createConnection(config);

// 安全 - 参数化
const [rows] = await connection.execute(
  'SELECT * FROM users WHERE id = ?',
  [userId]
);

// 使用ORM（Prisma）
const user = await prisma.user.findUnique({
  where: { id: parseInt(userId) }
});
```

---

## 安全响应头

### Nginx配置

```nginx
server {
    # XSS防护
    add_header X-XSS-Protection "1; mode=block" always;

    # 内容类型嗅探防护
    add_header X-Content-Type-Options "nosniff" always;

    # 点击劫持防护
    add_header X-Frame-Options "SAMEORIGIN" always;

    # HSTS - 强制HTTPS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # 内容安全策略
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;" always;

    # 引用策略
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 权限策略
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
}
```

### Express.js中间件

```javascript
const helmet = require('helmet');
const express = require('express');
const app = express();

app.use(helmet());

// 自定义CSP
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'nonce-{random}'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'", "https://api.example.com"],
    frameAncestors: ["'none'"],
    baseUri: ["'self'"],
    formAction: ["'self'"]
  }
}));
```

---

## 最佳实践

### 输入验证

```python
# 使用Pydantic进行输入验证
from pydantic import BaseModel, constr, validator

class UserInput(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    age: int = Field(ge=0, le=150)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v
```

### 认证安全

```python
# 密码哈希（bcrypt）
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### 会话管理

```javascript
// 安全的Cookie配置
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    secure: true,          // 仅HTTPS
    httpOnly: true,        // 禁止JS访问
    sameSite: 'strict',    // CSRF防护
    maxAge: 3600000        // 1小时过期
  },
  resave: false,
  saveUninitialized: false
}));
```

---

## 安全检查清单

| 检查项 | 说明 | 优先级 |
|--------|------|--------|
| 输入验证 | 所有用户输入必须验证和清理 | 🔴 高 |
| 输出编码 | 根据上下文（HTML/JS/URL）正确编码 | 🔴 高 |
| 参数化查询 | 禁止字符串拼接SQL | 🔴 高 |
| CSRF Token | 所有状态变更请求需验证Token | 🔴 高 |
| 安全头 | 配置所有推荐的安全响应头 | 🟡 中 |
| HTTPS | 全站启用HTTPS + HSTS | 🔴 高 |
| 依赖更新 | 定期更新依赖，修复已知漏洞 | 🟡 中 |
| 错误处理 | 不泄露敏感的错误信息 | 🟡 中 |

---

## 相关页面

- [[API安全设计]] - API层面的安全防护
- [[安全开发生命周期]] - SDL流程集成安全实践
- [[零信任架构]] - 零信任安全模型
- [[云安全最佳实践]] - 云端部署安全配置

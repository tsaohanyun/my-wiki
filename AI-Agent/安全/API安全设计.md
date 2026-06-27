---
title: API安全设计
aliases:
  - API Security
  - API认证授权
  - API防护
tags:
  - security
  - api
  - oauth2
  - jwt
  - authentication
  - authorization
type: reference
status: active
created: 2026-06-27
updated: 2026-06-27
source: OWASP API Security Top 10
difficulty: intermediate
project: AI-Agent
---

# API安全设计

## 概述

API安全设计涵盖认证授权、令牌管理、网关防护和流量控制等关键领域，保护API免受未授权访问和滥用。

---

## 认证与授权

### 认证方式对比

| 方式 | 适用场景 | 安全性 | 复杂度 |
|------|----------|--------|--------|
| API Key | 服务间调用、简单集成 | 中 | 低 |
| OAuth 2.0 | 第三方授权、用户委托 | 高 | 高 |
| JWT | 无状态认证、微服务 | 高 | 中 |
| mTLS | 服务间双向认证 | 很高 | 高 |
| OpenID Connect | 身份联合、SSO | 高 | 中 |

---

## OAuth 2.0

### 授权码流程（推荐）

```
┌──────────┐                              ┌──────────────┐
│  Client   │──1.授权请求──→              │Authorization │
│  (App)    │                              │   Server     │
│           │←─2.授权码────────────────────│              │
│           │                              └──────────────┘
│           │──3.授权码+客户端凭证──→      ┌──────────────┐
│           │                              │ Token        │
│           │←─4.Access Token+Refresh──────│ Endpoint     │
└──────────┘                              └──────────────┘
```

### OAuth 2.0 服务器实现

```python
# FastAPI + Authlib 实现OAuth2授权服务器
from authlib.integrations.starlette_oauth import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from starlette.applications import Starlette

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post']

    def generate_authorization_code(self, client, grant_user, request):
        import secrets
        return secrets.token_urlsafe(32)

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)

# 注册授权类型
server = AuthorizationServer(app)
server.register_grant(AuthorizationCodeGrant, [CodeChallenge(required=True)])

# 授权端点
@app.route('/oauth/authorize', methods=['GET', 'POST'])
async def authorize(request):
    if request.method == 'GET':
        # 显示授权确认页面
        grant = server.get_authorization_grant(request)
        return templates.TemplateResponse('authorize.html', {
            'grant': grant,
            'user': current_user
        })
    # 用户确认授权
    return server.create_authorization_response(request)
```

### PKCE增强安全

```javascript
// 前端PKCE实现
async function generatePKCE() {
  const verifier = generateRandomString(128);
  const challenge = await sha256(verifier);
  return {
    code_verifier: verifier,
    code_challenge: base64urlencode(challenge)
  };
}

// 授权请求
const pkce = await generatePKCE();
const authUrl = new URL('https://auth.example.com/authorize');
authUrl.searchParams.set('response_type', 'code');
authUrl.searchParams.set('client_id', CLIENT_ID);
authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
authUrl.searchParams.set('code_challenge', pkce.code_challenge);
authUrl.searchParams.set('code_challenge_method', 'S256');
authUrl.searchParams.set('scope', 'openid profile email');
authUrl.searchParams.set('state', generateRandomString(32));

// 令牌交换时验证
const tokenResponse = await fetch('https://auth.example.com/token', {
  method: 'POST',
  body: JSON.stringify({
    grant_type: 'authorization_code',
    code: authorizationCode,
    redirect_uri: REDIRECT_URI,
    code_verifier: pkce.code_verifier
  })
});
```

---

## JWT（JSON Web Token）

### JWT结构

```
Header.Payload.Signature

Header:  {"alg": "RS256", "typ": "JWT", "kid": "key-id-1"}
Payload: {"sub": "user123", "iss": "auth.example.com", "exp": 1700000000, "scope": "read write"}
Signature: RS256(header + "." + payload, privateKey)
```

### JWT生成与验证

```python
# Python - PyJWT
import jwt
from datetime import datetime, timedelta

# 生成JWT（使用RS256非对称加密）
def create_access_token(user_id: str, scopes: list[str]) -> str:
    private_key = open('private_key.pem').read()
    payload = {
        'sub': user_id,
        'iss': 'https://auth.example.com',
        'aud': 'https://api.example.com',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'scope': ' '.join(scopes),
        'jti': str(uuid.uuid4())  # 唯一标识，用于令牌撤销
    }
    return jwt.encode(payload, private_key, algorithm='RS256',
                      headers={'kid': 'current-key-id'})

# 验证JWT
def verify_token(token: str) -> dict:
    public_key = open('public_key.pem').read()
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            issuer='https://auth.example.com',
            audience='https://api.example.com',
            options={'require': ['exp', 'iss', 'aud', 'sub']}
        )
        # 检查令牌是否被撤销
        if is_token_revoked(payload['jti']):
            raise jwt.InvalidTokenError('Token has been revoked')
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, 'Token expired')
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, f'Invalid token: {e}')
```

```javascript
// Node.js - jose库
import { SignJWT, jwtVerify, importPKCS8, importSPKI } from 'jose';

// 生成JWT
async function createToken(userId, scopes) {
  const privateKey = await importPKCS8(PRIVATE_KEY, 'RS256');
  return new SignJWT({ sub: userId, scope: scopes.join(' ') })
    .setProtectedHeader({ alg: 'RS256', kid: 'key-1' })
    .setIssuedAt()
    .setIssuer('https://auth.example.com')
    .setAudience('https://api.example.com')
    .setExpirationTime('15m')
    .setJti(crypto.randomUUID())
    .sign(privateKey);
}

// 验证JWT
async function verifyToken(token) {
  const publicKey = await importSPKI(PUBLIC_KEY, 'RS256');
  const { payload } = await jwtVerify(token, publicKey, {
    issuer: 'https://auth.example.com',
    audience: 'https://api.example.com',
    requiredClaims: ['exp', 'iss', 'aud', 'sub']
  });
  return payload;
}
```

### JWT安全最佳实践

| 实践 | 说明 |
|------|------|
| 使用RS256/ES256 | 非对称算法，便于密钥轮换 |
| 设置短过期时间 | Access Token 15分钟以内 |
| 包含jti声明 | 支持令牌撤销 |
| 验证iss/aud | 防止令牌被其他服务误用 |
| 不存储敏感信息 | JWT payload可被解码 |
| 使用HTTPS传输 | 防止令牌被截获 |

---

## API网关安全

### Kong网关配置

```yaml
# Kong声明式配置 (kong.yml)
_format_version: "3.0"

services:
  - name: user-api
    url: http://user-service:8080
    routes:
      - name: user-routes
        paths: ["/api/v1/users"]
        strip_path: true
    plugins:
      # JWT认证
      - name: jwt
        config:
          key_claim_name: kid
          claims_to_verify: [exp, iss]
          run_on_preflight: false

      # 限流
      - name: rate-limiting
        config:
          minute: 100
          hour: 5000
          policy: redis
          redis:
            host: redis
            port: 6379

      # IP限制
      - name: ip-restriction
        config:
          allow: ["10.0.0.0/8", "172.16.0.0/12"]
          status: 403

      # CORS
      - name: cors
        config:
          origins: ["https://app.example.com"]
          methods: ["GET", "POST", "PUT", "DELETE"]
          headers: ["Authorization", "Content-Type"]
          max_age: 3600

      # 请求大小限制
      - name: request-size-limiting
        config:
          allowed_payload_size: 10  # MB
```

### APISIX网关配置

```yaml
# APISIX路由配置
routes:
  - uri: /api/v1/*
    plugins:
      jwt-auth:
        key: user-key
        secret: my-secret-key
        algorithm: RS256

      limit-count:
        count: 100
        time_window: 60
        rejected_code: 429
        key: consumer_name

      response-rewrite:
        headers:
          X-Request-ID: $request_id
          X-RateLimit-Limit: 100
```

---

## 限流策略

### 令牌桶算法实现

```python
import time
import threading

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # 令牌生成速率（个/秒）
        self.capacity = capacity  # 桶容量
        self.tokens = capacity
        self.last_time = time.monotonic()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.monotonic()
            # 补充令牌
            elapsed = now - self.last_time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_time = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

# Redis分布式限流
import redis

class RedisRateLimiter:
    def __init__(self, redis_client: redis.Redis, key: str, limit: int, window: int):
        self.redis = redis_client
        self.key = key
        self.limit = limit
        self.window = window

    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        key = f"rate:{self.key}:{identifier}"
        now = time.time()
        pipe = self.redis.pipeline()

        # 滑动窗口
        pipe.zremrangebyscore(key, 0, now - self.window)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, self.window)
        results = pipe.execute()

        count = results[2]
        remaining = max(0, self.limit - count)
        allowed = count <= self.limit

        return allowed, {
            'X-RateLimit-Limit': self.limit,
            'X-RateLimit-Remaining': remaining,
            'X-RateLimit-Reset': int(now + self.window)
        }
```

```javascript
// Express中间件限流
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');

// 基于IP的限流
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15分钟
  max: 100,                    // 每窗口100次请求
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later' },
  keyGenerator: (req) => req.ip || req.headers['x-forwarded-for']
});

// 基于用户的限流
const userLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 60,
  keyGenerator: (req) => req.user?.id || req.ip
});

app.use('/api/', apiLimiter);
app.use('/api/sensitive/', userLimiter);
```

---

## API安全检查清单

| 类别 | 检查项 | 优先级 |
|------|--------|--------|
| 认证 | 使用标准认证协议（OAuth2/OIDC） | 🔴 高 |
| 认证 | Access Token短期有效（≤15min） | 🔴 高 |
| 认证 | 实现令牌撤销机制 | 🟡 中 |
| 授权 | 实施最小权限原则 | 🔴 高 |
| 授权 | 验证每个请求的权限 | 🔴 高 |
| 传输 | 全面使用HTTPS/TLS 1.3 | 🔴 高 |
| 输入 | 验证所有请求参数 | 🔴 高 |
| 输入 | 限制请求体大小 | 🟡 中 |
| 限流 | 实施速率限制 | 🔴 高 |
| 限流 | 使用滑动窗口算法 | 🟡 中 |
| 日志 | 记录所有认证事件 | 🟡 中 |
| 版本 | 使用API版本控制 | 🟢 低 |

---

## 相关页面

- [[Web应用安全]] - Web层面的安全防护
- [[安全开发生命周期]] - SDL中的API安全实践
- [[零信任架构]] - API零信任访问控制
- [[云安全最佳实践]] - 云端API安全配置

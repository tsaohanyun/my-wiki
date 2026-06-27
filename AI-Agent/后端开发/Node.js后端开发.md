---
title: Node.js 后端开发
aliases:
  - NodeJS后端
  - Express开发
  - NestJS开发
tags:
  - nodejs
  - express
  - koa
  - nestjs
  - backend
  - javascript
  - typescript
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: AI-Agent Wiki
difficulty: intermediate
project: AI-Agent
---

# Node.js 后端开发

## 概述

Node.js 基于 V8 引擎的非阻塞 I/O 模型，非常适合构建高并发的网络服务。主流框架包括 **Express**（轻量灵活）、**Koa**（现代化中间件）、**NestJS**（企业级 TypeScript 框架）。本页涵盖三大框架的核心用法、中间件机制和 ORM 选型。

---

## 1. Express 框架

Express 是 Node.js 最流行的 Web 框架，以简单灵活著称。

### 1.1 基础应用

```javascript
const express = require('express');
const app = express();

// 解析 JSON 请求体
app.use(express.json());
// 解析 URL-encoded 请求体
app.use(express.urlencoded({ extended: true }));

// 路由
app.get('/', (req, res) => {
    res.json({ message: 'Hello, Express!' });
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

### 1.2 路由组织

```javascript
const { Router } = require('express');
const router = Router();

// 用户资源路由
router.get('/users', getAllUsers);
router.get('/users/:id', getUserById);
router.post('/users', createUser);
router.put('/users/:id', updateUser);
router.delete('/users/:id', deleteUser);

app.use('/api/v1', router);
```

### 1.3 中间件

```javascript
// 日志中间件
const logger = (req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.url} ${res.statusCode} ${duration}ms`);
    });
    next();
};

// 认证中间件
const auth = (req, res, next) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) {
        return res.status(401).json({ error: '未授权：缺少 Token' });
    }
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        return res.status(403).json({ error: 'Token 无效' });
    }
};

// 错误处理中间件（必须放在所有路由之后）
const errorHandler = (err, req, res, next) => {
    console.error(err.stack);
    const status = err.status || 500;
    res.status(status).json({
        error: err.name || 'InternalServerError',
        message: err.message || '服务器内部错误'
    });
};

app.use(logger);
app.use('/api/v1/users', auth, userRouter);
app.use(errorHandler);
```

### 1.4 异步路由包装

```javascript
// 包装异步控制器，自动捕获 Promise rejection
const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
};

// 使用方式
router.post('/users', asyncHandler(async (req, res) => {
    const user = await UserService.create(req.body);
    res.status(201).json(user);
}));
```

---

## 2. Koa 框架

Koa 由 Express 原班团队打造，基于 `async/await` 中间件的"洋葱模型"。

### 2.1 基础应用

```javascript
const Koa = require('koa');
const bodyParser = require('koa-bodyparser');
const logger = require('koa-logger');
const cors = require('@koa/cors');

const app = new Koa();

app.use(logger());
app.use(cors());
app.use(bodyParser());

app.use(async (ctx) => {
    ctx.body = { message: 'Hello, Koa!' };
});

app.listen(3000);
```

### 2.2 洋葱模型中间件

```javascript
// 执行顺序：A -> B -> C -> B' -> A'
app.use(async (ctx, next) => {
    console.log('Middleware A - Before');
    const start = Date.now();
    await next(); // 进入下一层中间件
    const duration = Date.now() - start;
    console.log(`Middleware A - After (${duration}ms)`);
    ctx.set('X-Response-Time', `${duration}ms`);
});

app.use(async (ctx, next) => {
    console.log('Middleware B - Before');
    await next();
    console.log('Middleware B - After');
});

app.use(async (ctx) => {
    console.log('Middleware C - Handler');
    ctx.body = { data: 'response' };
});
```

### 2.3 Koa 路由与控制器

```javascript
const Router = require('@koa/router');
const router = new Router({ prefix: '/api/v1' });

router.get('/users', async (ctx) => {
    const users = await UserModel.find().limit(20);
    ctx.body = { data: users };
});

router.get('/users/:id', async (ctx) => {
    const user = await UserModel.findById(ctx.params.id);
    if (!user) {
        ctx.throw(404, '用户不存在');
    }
    ctx.body = { data: user };
});

router.post('/users', async (ctx) => {
    const { username, email } = ctx.request.body;
    if (!username || !email) {
        ctx.throw(400, '用户名和邮箱为必填项');
    }
    const exists = await UserModel.findOne({ email });
    if (exists) {
        ctx.throw(409, '邮箱已被注册');
    }
    const user = await UserModel.create({ username, email });
    ctx.status = 201;
    ctx.body = { data: user };
});

app.use(router.routes()).use(router.allowedMethods());
```

---

## 3. NestJS 框架

NestJS 是一个渐进式 Node.js 框架，深度集成 TypeScript，灵感来自 Angular，支持依赖注入、模块化架构。

### 3.1 项目结构

```
src/
├── main.ts              # 入口文件
├── app.module.ts        # 根模块
├── common/              # 公共模块
│   ├── decorators/
│   ├── filters/
│   ├── guards/
│   ├── interceptors/
│   └── pipes/
├── modules/
│   ├── auth/
│   │   ├── auth.module.ts
│   │   ├── auth.controller.ts
│   │   ├── auth.service.ts
│   │   ├── strategies/
│   │   └── dto/
│   └── users/
│       ├── users.module.ts
│       ├── users.controller.ts
│       ├── users.service.ts
│       ├── users.repository.ts
│       └── dto/
└── config/
```

### 3.2 控制器与服务

```typescript
// users.controller.ts
@Controller('users')
@ApiTags('用户管理')
export class UsersController {

    constructor(private readonly usersService: UsersService) {}

    @Post()
    @HttpCode(HttpStatus.CREATED)
    @UsePipes(new ValidationPipe({ transform: true }))
    async create(@Body() createUserDto: CreateUserDto): Promise<UserResponseDto> {
        return this.usersService.create(createUserDto);
    }

    @Get()
    @UseGuards(JwtAuthGuard)
    async findAll(
        @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
        @Query('limit', new DefaultValuePipe(10), ParseIntPipe) limit: number
    ): Promise<PaginatedResult<UserResponseDto>> {
        return this.usersService.findAll({ page, limit });
    }

    @Get(':id')
    @UseGuards(JwtAuthGuard)
    async findOne(@Param('id', ParseIntPipe) id: number): Promise<UserResponseDto> {
        return this.usersService.findOne(id);
    }

    @Patch(':id')
    @UseGuards(JwtAuthGuard)
    async update(
        @Param('id', ParseIntPipe) id: number,
        @Body() updateUserDto: UpdateUserDto
    ): Promise<UserResponseDto> {
        return this.usersService.update(id, updateUserDto);
    }

    @Delete(':id')
    @HttpCode(HttpStatus.NO_CONTENT)
    @UseGuards(JwtAuthGuard, AdminGuard)
    async remove(@Param('id', ParseIntPipe) id: number): Promise<void> {
        await this.usersService.remove(id);
    }
}
```

```typescript
// users.service.ts
@Injectable()
export class UsersService {

    constructor(
        @InjectRepository(UserRepository)
        private readonly userRepository: UserRepository,
        private readonly eventBus: EventBus,
    ) {}

    async create(dto: CreateUserDto): Promise<UserResponseDto> {
        const exists = await this.userRepository.existsByEmail(dto.email);
        if (exists) {
            throw new ConflictException('邮箱已被注册');
        }
        const hashedPassword = await bcrypt.hash(dto.password, 10);
        const user = await this.userRepository.save({
            ...dto,
            password: hashedPassword,
        });
        await this.eventBus.publish(new UserCreatedEvent(user.id));
        return toResponseDto(user);
    }

    async findOne(id: number): Promise<UserResponseDto> {
        const user = await this.userRepository.findById(id);
        if (!user) {
            throw new NotFoundException(`用户 #${id} 不存在`);
        }
        return toResponseDto(user);
    }
}
```

### 3.3 DTO 与验证

```typescript
// dto/create-user.dto.ts
import { IsEmail, IsString, MinLength, MaxLength, Matches } from 'class-validator';

export class CreateUserDto {
    @IsString()
    @MinLength(3, { message: '用户名至少 3 个字符' })
    @MaxLength(50, { message: '用户名最多 50 个字符' })
    readonly username: string;

    @IsEmail({}, { message: '邮箱格式不正确' })
    readonly email: string;

    @IsString()
    @MinLength(8, { message: '密码至少 8 个字符' })
    @Matches(/^(?=.*[A-Z])(?=.*\d).+$/, { message: '密码须包含大写字母和数字' })
    readonly password: string;
}
```

### 3.4 全局异常过滤器

```typescript
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
    private readonly logger = new Logger(AllExceptionsFilter.name);

    catch(exception: unknown, host: ArgumentsHost): void {
        const ctx = host.switchToHttp();
        const response = ctx.getResponse<Response>();
        const request = ctx.getRequest<Request>();

        let status = HttpStatus.INTERNAL_SERVER_ERROR;
        let message = '服务器内部错误';

        if (exception instanceof HttpException) {
            status = exception.getStatus();
            const res = exception.getResponse();
            message = typeof res === 'string' ? res : (res as any).message;
        } else if (exception instanceof Error) {
            this.logger.error(exception.stack);
        }

        response.status(status).json({
            code: status,
            message,
            timestamp: new Date().toISOString(),
            path: request.url,
        });
    }
}
```

### 3.5 模块定义

```typescript
@Module({
    imports: [
        TypeOrmModule.forFeature([UserEntity]),
        PassportModule.register({ defaultStrategy: 'jwt' }),
        JwtModule.register({
            secret: process.env.JWT_SECRET,
            signOptions: { expiresIn: '24h' },
        }),
    ],
    controllers: [UsersController, AuthController],
    providers: [UsersService, AuthService, JwtStrategy],
    exports: [UsersService],
})
export class UsersModule {}
```

---

## 4. ORM 选型

### 4.1 Prisma（推荐）

```prisma
// schema.prisma
generator client {
    provider = "prisma-client-js"
}

datasource db {
    provider = "postgresql"
    url      = env("DATABASE_URL")
}

model User {
    id        Int      @id @default(autoincrement())
    email     String   @unique
    username  String   @unique
    posts     Post[]
    createdAt DateTime @default(now())
    updatedAt DateTime @updatedAt
}

model Post {
    id       Int    @id @default(autoincrement())
    title    String
    content  String?
    authorId Int
    author   User   @relation(fields: [authorId], references: [id])
}
```

```typescript
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

// 查询（含关联）
const users = await prisma.user.findMany({
    include: { posts: true },
    where: { email: { contains: '@example.com' } },
    orderBy: { createdAt: 'desc' },
    take: 20,
});

// 事务
await prisma.$transaction(async (tx) => {
    const user = await tx.user.create({ data: { email, username } });
    await tx.post.create({ data: { title: 'Hello', authorId: user.id } });
});
```

### 4.2 TypeORM

```typescript
@Entity('users')
export class User {
    @PrimaryGeneratedColumn()
    id: number;

    @Column({ unique: true })
    email: string;

    @Column()
    username: string;

    @CreateDateColumn()
    createdAt: Date;

    @UpdateDateColumn()
    updatedAt: Date;

    @OneToMany(() => Post, (post) => post.author)
    posts: Post[];
}

// 自定义 Repository
@EntityRepository(User)
export class UserRepository extends Repository<User> {
    async findActiveUsers(): Promise<User[]> {
        return this.createQueryBuilder('user')
            .leftJoinAndSelect('user.posts', 'post')
            .where('user.deletedAt IS NULL')
            .orderBy('user.createdAt', 'DESC')
            .getMany();
    }
}
```

### 4.3 对比

| 特性 | Prisma | TypeORM | Sequelize |
|------|--------|---------|-----------|
| 类型安全 | ✅ 原生 TypeScript | ✅ 支持 | ⚠️ 弱 |
| 模式定义 | Declarative Schema | 装饰器/JSON | JSON Model |
| 迁移工具 | 内置 | 内置 | 第三方 |
| 学习曲线 | 低 | 中 | 中 |
| 查询体验 | DSL（非常直观） | QueryBuilder | 操作符风格 |
| 性能 | 好 | 好 | 一般 |

---

## 5. 中间件模式深入

### 5.1 Express/Koa 中间件职责分离

```javascript
// === 请求限流中间件 ===
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,  // 15 分钟窗口
    max: 100,                   // 每个 IP 最多 100 次请求
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: '请求过于频繁，请稍后重试' },
});

app.use('/api/', limiter);

// === CORS 中间件 ===
const cors = require('cors');
app.use(cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
}));

// === Helmet 安全头 ===
const helmet = require('helmet');
app.use(helmet());

// === 请求 ID 追踪 ===
const { v4: uuidv4 } = require('uuid');
app.use((req, res, next) => {
    req.id = req.headers['x-request-id'] || uuidv4();
    res.setHeader('X-Request-Id', req.id);
    next();
});
```

### 5.2 NestJS 中间件 / 守卫 / 拦截器 / 管道

```typescript
// --- Guard（认证授权） ---
@Injectable()
export class RolesGuard implements CanActivate {
    constructor(private reflector: Reflector) {}

    canActivate(context: ExecutionContext): boolean {
        const requiredRoles = this.reflector.get<string[]>(
            ROLES_KEY,
            context.getHandler()
        );
        if (!requiredRoles) return true;

        const { user } = context.switchToHttp().getRequest();
        return requiredRoles.some((role) => user.roles?.includes(role));
    }
}

// --- Interceptor（日志 / 缓存 / 响应转换） ---
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
    private logger = new Logger(LoggingInterceptor.name);

    intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
        const req = context.switchToHttp().getRequest();
        const now = Date.now();

        return next.handle().pipe(
            tap(() => {
                this.logger.log(`${req.method} ${req.url} - ${Date.now() - now}ms`);
            }),
            catchError((err) => {
                this.logger.error(`${req.method} ${req.url} - ${err.message}`);
                return throwError(() => err);
            })
        );
    }
}

// --- Pipe（参数验证与转换） ---
@Injectable()
export class ParseIntOrNullPipe implements PipeTransform {
    transform(value: string): number | null {
        if (value === undefined || value === null) return null;
        const val = parseInt(value, 10);
        if (isNaN(val)) {
            throw new BadRequestException('参数必须是整数');
        }
        return val;
    }
}
```

---

## 6. 最佳实践

### 6.1 安全建议

- ✅ **始终使用 Helmet** 设置安全 HTTP 头
- ✅ **使用 `express-rate-limit`** 防止暴力破解
- ✅ **密码使用 `bcrypt` 或 `argon2` 哈希**，绝不存明文
- ✅ **使用环境变量管理密钥**，使用 `dotenv` 或 Vault
- ✅ **输入校验**：`class-validator`（NestJS）/ `joi`（Express）
- ✅ **SQL 注入防护**：使用参数化查询（Prisma/TypeORM 默认安全）
- ❌ 不要在客户端存储 JWT 于 `localStorage`，使用 `HttpOnly Cookie`
- ❌ 不要信任任何客户端输入

### 6.2 性能建议

- ✅ **使用集群模式**：`cluster` 模块或 PM2 充分利用多核
- ✅ **数据库连接池**：合理设置 `poolSize`
- ✅ **缓存**：Redis 缓存热点数据，减少数据库压力
- ✅ **流式响应**：大文件使用 `stream` 而非一次性 `Buffer`
- ✅ **合理使用 `async/await`**，避免阻塞事件循环
- ✅ **压缩响应**：`compression` 中间件

### 6.3 项目工程化

```json
// package.json 脚本
{
  "scripts": {
    "start:dev": "nest start --watch",
    "start:prod": "NODE_ENV=production node dist/main.js",
    "build": "nest build",
    "lint": "eslint \"{src,apps,libs,test}/**/*.ts\" --fix",
    "test": "jest",
    "test:e2e": "jest --config ./test/jest-e2e.json",
    "docker:build": "docker build -t app-backend .",
    "docker:run": "docker run -p 3000:3000 app-backend"
  }
}
```

---

## 7. 相关页面

- [[Java Spring Boot 开发]]
- [[Python 异步编程]]
- [[gRPC 服务开发]]
- [[Rust 系统编程]]
- [[TypeScript 类型体操]]
- [[微服务架构]]
- [[Docker 与容器化部署]]

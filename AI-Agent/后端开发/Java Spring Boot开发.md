---
title: Java Spring Boot 开发
aliases:
  - SpringBoot
  - Spring Boot
  - Java后端框架
tags:
  - java
  - spring-boot
  - backend
  - framework
  - auto-configuration
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: AI-Agent Wiki
difficulty: intermediate
project: AI-Agent
---

# Java Spring Boot 开发

## 概述

Spring Boot 是基于 Spring 框架的快速开发脚手架，通过**自动配置**、**起步依赖（Starter）**和**内嵌服务器**大幅简化了 Spring 应用的创建与部署。它遵循"约定优于配置"的理念，让开发者专注于业务逻辑。

---

## 1. 核心特性

### 1.1 自动配置（Auto-Configuration）

Spring Boot 根据类路径中的依赖、已定义的 Bean 等条件，自动装配所需的配置。

```java
// 通过 @SpringBootApplication 开启自动配置
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

`@SpringBootApplication` 等价于：

```java
@SpringBootConfiguration   // 标记配置类
@EnableAutoConfiguration   // 开启自动配置
@ComponentScan             // 组件扫描
```

**自定义排除自动配置：**

```java
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### 1.2 条件装配注解

| 注解 | 说明 |
|------|------|
| `@ConditionalOnClass` | 类路径存在指定类时生效 |
| `@ConditionalOnMissingBean` | 容器中不存在指定 Bean 时生效 |
| `@ConditionalOnProperty` | 配置属性满足条件时生效 |
| `@ConditionalOnBean` | 容器中存在指定 Bean 时生效 |
| `@ConditionalOnWebApplication` | 是 Web 应用时生效 |

```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(prefix = "app.datasource", name = "enabled", havingValue = "true")
public class DataSourceConfig {

    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource() {
        return DataSourceBuilder.create()
                .url("jdbc:mysql://localhost:3306/mydb")
                .username("root")
                .password("secret")
                .build();
    }
}
```

---

## 2. 起步依赖（Starter）

Spring Boot Starter 是一组预打包的依赖集合，引入一个 Starter 即可获得该功能领域所有必要的库。

| Starter | 说明 |
|---------|------|
| `spring-boot-starter-web` | Web 开发（Spring MVC + Tomcat） |
| `spring-boot-starter-data-jpa` | 数据持久化（JPA + Hibernate） |
| `spring-boot-starter-security` | 安全认证与授权 |
| `spring-boot-starter-data-redis` | Redis 缓存与消息 |
| `spring-boot-starter-actuator` | 生产级监控端点 |
| `spring-boot-starter-test` | 测试支持 |
| `spring-boot-starter-validation` | 参数校验 |

**Maven 依赖示例：**

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
</dependencies>
```

---

## 3. RESTful API 开发

### 3.1 控制器

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping
    public ResponseEntity<UserDTO> createUser(@Valid @RequestBody CreateUserRequest request) {
        UserDTO created = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.getUserById(id));
    }

    @GetMapping
    public ResponseEntity<Page<UserDTO>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "id") String sort
    ) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
        return ResponseEntity.ok(userService.getUsers(pageable));
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserDTO> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request
    ) {
        return ResponseEntity.ok(userService.updateUser(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}
```

### 3.2 参数校验

```java
@Data
public class CreateUserRequest {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 50, message = "用户名长度须在 3~50 之间")
    private String username;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄不能小于 18")
    @Max(value = 120, message = "年龄不能大于 120")
    private Integer age;
}
```

**全局异常处理：**

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidationException(
            MethodArgumentNotValidException ex
    ) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
                errors.put(error.getField(), error.getDefaultMessage())
        );
        return ResponseEntity.badRequest().body(errors);
    }

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, String>> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("message", ex.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> handleGeneric(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Internal Server Error", "message", ex.getMessage()));
    }
}
```

---

## 4. 数据持久层

### 4.1 JPA 实体与 Repository

```java
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
```

```java
public interface UserRepository extends JpaRepository<User, Long>,
        JpaSpecificationExecutor<User> {

    Optional<User> findByEmail(String email);

    boolean existsByEmail(String email);

    @Query("SELECT u FROM User u WHERE u.username LIKE %:keyword%")
    Page<User> searchByUsername(@Param("keyword") String keyword, Pageable pageable);
}
```

### 4.2 事务管理

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    @Transactional
    public UserDTO createUser(CreateUserRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("邮箱已被注册");
        }
        User user = User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .build();
        return toDTO(userRepository.save(user));
    }

    @Transactional(readOnly = true)
    public UserDTO getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("用户不存在: " + id));
        return toDTO(user);
    }
}
```

---

## 5. 配置管理

### 5.1 application.yml

```yaml
server:
  port: 8080
  servlet:
    context-path: /api

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC
    username: ${DB_USERNAME:root}
    password: ${DB_PASSWORD:secret}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        format_sql: true
        dialect: org.hibernate.dialect.MySQL8Dialect

  redis:
    host: ${REDIS_HOST:localhost}
    port: ${REDIS_PORT:6379}

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when_authorized

logging:
  level:
    com.example: DEBUG
    org.hibernate.SQL: DEBUG
```

### 5.2 类型安全配置

```java
@ConfigurationProperties(prefix = "app.jwt")
@Data
public class JwtProperties {
    private String secret;
    private long expiration = 86400000;
    private String header = "Authorization";
}
```

```java
@Configuration
@EnableConfigurationProperties(JwtProperties.class)
public class JwtConfig {

    @Bean
    public JwtUtil jwtUtil(JwtProperties properties) {
        return new JwtUtil(properties.getSecret(), properties.getExpiration());
    }
}
```

---

## 6. Actuator 监控

Actuator 提供生产级的监控和管理端点。

### 6.1 常用端点

| 端点 | 说明 |
|------|------|
| `/actuator/health` | 应用健康状态 |
| `/actuator/info` | 应用信息 |
| `/actuator/metrics` | 度量指标 |
| `/actuator/prometheus` | Prometheus 格式指标 |
| `/actuator/loggers` | 动态日志级别 |
| `/actuator/env` | 环境属性 |
| `/actuator/beans` | 所有 Bean 列表 |
| `/actuator/threaddump` | 线程转储 |

### 6.2 自定义健康指标

```java
@Component
public class CustomHealthIndicator implements HealthIndicator {

    private final ExternalServiceClient externalServiceClient;

    public CustomHealthIndicator(ExternalServiceClient externalServiceClient) {
        this.externalServiceClient = externalServiceClient;
    }

    @Override
    public Health health() {
        try {
            if (externalServiceClient.isAvailable()) {
                return Health.up()
                        .withDetail("externalService", "可达")
                        .withDetail("latency", externalServiceClient.getLatency() + "ms")
                        .build();
            }
            return Health.down().withDetail("externalService", "不可达").build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

### 6.3 自定义度量指标

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final MeterRegistry meterRegistry;
    private final Counter orderCreatedCounter;
    private final Timer orderProcessTimer;

    public OrderService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.orderCreatedCounter = Counter.builder("app.orders.created")
                .description("创建的订单总数")
                .tag("type", "standard")
                .register(meterRegistry);
        this.orderProcessTimer = Timer.builder("app.orders.process.duration")
                .description("订单处理耗时")
                .register(meterRegistry);
    }

    public void createOrder(OrderRequest request) {
        orderProcessTimer.record(() -> {
            // 订单处理逻辑
            orderCreatedCounter.increment();
        });
    }
}
```

---

## 7. 最佳实践

### 7.1 项目分层

```
src/main/java/com/example/
├── config/          # 配置类
├── controller/      # 控制器层
├── service/         # 业务逻辑层
│   ├── impl/
├── repository/      # 数据访问层
├── model/
│   ├── entity/      # 实体类
│   ├── dto/         # 数据传输对象
│   ├── request/     # 请求对象
│   └── response/    # 响应对象
├── exception/       # 异常处理
├── security/        # 安全配置
└── util/            # 工具类
```

### 7.2 关键建议

- ✅ **使用构造器注入**而非字段注入（`@RequiredArgsConstructor`）
- ✅ **统一异常处理**，不要在控制器中写 try-catch
- ✅ **DTO 隔离**，不要将实体直接返回给客户端
- ✅ **生产环境关闭 `ddl-auto: create`**，使用 Flyway/Liquibase 管理数据库迁移
- ✅ **使用 `@Transactional(readOnly = true)`** 标注只读查询方法
- ✅ **敏感配置使用环境变量**，不要硬编码
- ✅ **开启 Actuator 并集成 Prometheus + Grafana**
- ✅ **统一 API 版本管理**（URL 路径或 Header）
- ❌ 不要在 `@Service` 中直接操作 `HttpServletRequest`
- ❌ 不要滥用 `@Autowired` 字段注入

### 7.3 Docker 部署

```dockerfile
# 多阶段构建
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre-alpine
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "-XX:+UseG1GC", "-Xmx512m", "/app.jar"]
```

---

## 8. 相关页面

- [[Node.js 后端开发]]
- [[Python 异步编程]]
- [[gRPC 服务开发]]
- [[Rust 系统编程]]
- [[数据库设计与优化]]
- [[微服务架构]]
- [[Docker 与容器化部署]]

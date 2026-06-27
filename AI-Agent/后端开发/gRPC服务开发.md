---
title: gRPC 服务开发
aliases:
  - gRPC
  - gRPC开发
  - Protobuf
  - Protocol Buffers
tags:
  - grpc
  - protobuf
  - rpc
  - microservices
  - streaming
  - interceptor
  - grpc-gateway
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: AI-Agent Wiki
difficulty: intermediate
project: AI-Agent
---

# gRPC 服务开发

## 概述

gRPC 是 Google 开源的高性能 RPC 框架，基于 **HTTP/2** 传输、**Protocol Buffers** 序列化。相比 REST + JSON，gRPC 提供：

- **更快的序列化**：Protobuf 二进制格式比 JSON 更紧凑高效
- **强类型契约**：`.proto` 文件定义接口，多语言自动生成客户端/服务端代码
- **双向流式通信**：支持 Unary、Server Streaming、Client Streaming、Bidirectional Streaming
- **内置拦截器**：统一的认证、日志、链路追踪
- **健康检查与服务发现**：原生支持

---

## 1. Protobuf 基础

### 1.1 消息定义

```protobuf
syntax = "proto3";

package com.example.users;
option go_package = "github.com/example/proto/users";
option java_package = "com.example.proto.users";
option java_multiple_files = true;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// 用户消息
message User {
    int64 id = 1;
    string username = 2;
    string email = 3;
    UserStatus status = 4;
    google.protobuf.Timestamp created_at = 5;
    google.protobuf.Timestamp updated_at = 6;
    repeated string roles = 7;      // 数组字段
    map<string, string> metadata = 8; // Map 字段
    optional string nickname = 9;   // 可选字段（proto3 显式 optional）
}

// 枚举
enum UserStatus {
    USER_STATUS_UNSPECIFIED = 0;  // proto3 枚举必须以 0 值开头
    USER_STATUS_ACTIVE = 1;
    USER_STATUS_INACTIVE = 2;
    USER_STATUS_BANNED = 3;
}

// 请求/响应消息
message CreateUserRequest {
    string username = 1 [(validate.rules).string.min_len = 3];
    string email = 2;
    string password = 3;
}

message GetUserRequest {
    int64 id = 1;
}

message ListUsersRequest {
    int32 page = 1;
    int32 page_size = 2;
    string sort_by = 3;
    string order = 4;  // asc / desc
}

message ListUsersResponse {
    repeated User users = 1;
    int32 total = 2;
    int32 page = 3;
    int32 page_size = 4;
}

message UpdateUserRequest {
    int64 id = 1;
    optional string username = 2;
    optional string email = 3;
    optional UserStatus status = 4;
}

message DeleteUserRequest {
    int64 id = 1;
}
```

### 1.2 嵌套消息与 Oneof

```protobuf
message SearchResult {
    string query = 1;
    oneof result_type {
        User user = 2;          // 三选一
        Product product = 3;
        Article article = 4;
    }
}

message Product {
    int64 id = 1;
    string name = 2;
    double price = 3;

    message InventoryInfo {      // 嵌套消息
        int32 stock = 1;
        string warehouse = 2;
    }
    InventoryInfo inventory = 4;
}

message Article {
    int64 id = 1;
    string title = 2;
    string content = 3;
}
```

### 1.3 服务定义

```protobuf
// 同步请求-响应（Unary RPC）
service UserService {
    rpc CreateUser(CreateUserRequest) returns (User);
    rpc GetUser(GetUserRequest) returns (User);
    rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
    rpc UpdateUser(UpdateUserRequest) returns (User);
    rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);

    // 服务端流式：客户端发一个请求，服务端返回多条数据流
    rpc StreamUsers(StreamUsersRequest) returns (stream User);

    // 客户端流式：客户端连续发送多条，服务端返回一个汇总
    rpc BatchCreateUsers(stream CreateUserRequest) returns (BatchCreateResponse);

    // 双向流式：双方持续收发
    rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message StreamUsersRequest {
    string filter = 1;
}

message BatchCreateResponse {
    int32 success_count = 1;
    int32 failure_count = 2;
    repeated string errors = 3;
}

message ChatMessage {
    int64 user_id = 1;
    string content = 2;
    google.protobuf.Timestamp sent_at = 3;
}
```

---

## 2. Go gRPC 实现

### 2.1 代码生成

```bash
# 安装工具链
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# 生成 Go 代码
protoc \
    --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    proto/users.proto
```

### 2.2 服务端实现

```go
package main

import (
    "context"
    "fmt"
    "log"
    "net"
    "sync"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    "google.golang.org/protobuf/types/known/timestamppb"
    pb "github.com/example/proto/users"
)

// --- 服务实现 ---

type userServer struct {
    pb.UnimplementedUserServiceServer
    mu    sync.RWMutex
    users map[int64]*pb.User
    nextID int64
}

func NewUserServer() *userServer {
    return &userServer{
        users:  make(map[int64]*pb.User),
        nextID: 1,
    }
}

// Unary RPC
func (s *userServer) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.User, error) {
    // 校验
    if req.GetUsername() == "" {
        return nil, status.Error(codes.InvalidArgument, "用户名不能为空")
    }

    s.mu.Lock()
    defer s.mu.Unlock()

    // 检查唯一性
    for _, u := range s.users {
        if u.GetEmail() == req.GetEmail() {
            return nil, status.Error(codes.AlreadyExists, "邮箱已存在")
        }
    }

    now := timestamppb.Now()
    user := &pb.User{
        Id:        s.nextID,
        Username:  req.GetUsername(),
        Email:     req.GetEmail(),
        Status:    pb.UserStatus_USER_STATUS_ACTIVE,
        CreatedAt: now,
        UpdatedAt: now,
    }
    s.users[user.Id] = user
    s.nextID++

    log.Printf("创建用户: id=%d, username=%s", user.Id, user.Username)
    return user, nil
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    user, ok := s.users[req.GetId()]
    if !ok {
        return nil, status.Errorf(codes.NotFound, "用户 #%d 不存在", req.GetId())
    }
    return user, nil
}

// 服务端流式
func (s *userServer) StreamUsers(req *pb.StreamUsersRequest, stream pb.UserService_StreamUsersServer) error {
    s.mu.RLock()
    defer s.mu.RUnlock()

    for _, user := range s.users {
        // 发送前检查 context 是否已取消
        if err := stream.Context().Err(); err != nil {
            return err // 客户端断开或超时
        }

        if err := stream.Send(user); err != nil {
            return status.Errorf(codes.Internal, "发送数据失败: %v", err)
        }
        time.Sleep(100 * time.Millisecond) // 模拟处理延迟
    }
    return nil
}

// 客户端流式
func (s *userServer) BatchCreateUsers(stream pb.UserService_BatchCreateUsersServer) error {
    var successCount, failureCount int32
    var errors []string

    for {
        req, err := stream.Recv()
        if err != nil { // io.EOF 表示客户端发送完毕
            break
        }

        // 处理每条请求
        _, createErr := s.CreateUser(stream.Context(), req)
        if createErr != nil {
            failureCount++
            errors = append(errors, fmt.Sprintf("用户 %s: %v", req.GetUsername(), createErr))
        } else {
            successCount++
        }
    }

    return stream.SendAndClose(&pb.BatchCreateResponse{
        SuccessCount: successCount,
        FailureCount: failureCount,
        Errors:       errors,
    })
}

// 双向流式
func (s *userServer) Chat(stream pb.UserService_ChatServer) error {
    // 为每个客户端启动一个 goroutine 接收，另一个发送
    // 简化示例：echo 模式
    for {
        msg, err := stream.Recv()
        if err != nil {
            return err
        }

        // 处理消息
        reply := &pb.ChatMessage{
            UserId:  msg.GetUserId(),
            Content: fmt.Sprintf("Echo: %s", msg.GetContent()),
            SentAt:  timestamppb.Now(),
        }

        if err := stream.Send(reply); err != nil {
            return err
        }
    }
}

// --- 启动服务器 ---

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("监听失败: %v", err)
    }

    // 创建 gRPC 服务器（注册拦截器）
    s := grpc.NewServer(
        grpc.UnaryInterceptor(UnaryLoggingInterceptor),
        grpc.StreamInterceptor(StreamLoggingInterceptor),
    )

    // 注册服务
    pb.RegisterUserServiceServer(s, NewUserServer())

    // 注册健康检查
    healthpb.RegisterHealthServer(s, health.NewServer())

    log.Println("gRPC 服务器启动: :50051")
    if err := s.Serve(lis); err != nil {
        log.Fatalf("启动失败: %v", err)
    }
}
```

### 2.3 客户端实现

```go
package main

import (
    "context"
    "io"
    "log"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    pb "github.com/example/proto/users"
)

func main() {
    // 建立连接（带超时和重试）
    conn, err := grpc.Dial(
        "localhost:50051",
        grpc.WithTransportCredentials(insecure.NewCredentials()),
        grpc.WithDefaultCallOptions(grpc.MaxCallRecvMsgSize(10*1024*1024)),
    )
    if err != nil {
        log.Fatalf("连接失败: %v", err)
    }
    defer conn.Close()

    client := pb.NewUserServiceClient(conn)

    // --- Unary 调用 ---
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    user, err := client.CreateUser(ctx, &pb.CreateUserRequest{
        Username: "alice",
        Email:    "alice@example.com",
        Password: "secure123",
    })
    if err != nil {
        log.Fatalf("创建用户失败: %v", err)
    }
    log.Printf("创建成功: %+v", user)

    // --- 服务端流式 ---
    log.Println("=== 服务端流式 ===")
    stream, err := client.StreamUsers(ctx, &pb.StreamUsersRequest{Filter: ""})
    if err != nil {
        log.Fatalf("打开流失败: %v", err)
    }
    for {
        u, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            log.Fatalf("接收失败: %v", err)
        }
        log.Printf("收到用户: %s", u.GetUsername())
    }

    // --- 客户端流式 ---
    log.Println("=== 客户端流式 ===")
    batchStream, err := client.BatchCreateUsers(ctx)
    if err != nil {
        log.Fatalf("打开流失败: %v", err)
    }
    for i := 0; i < 5; i++ {
        if err := batchStream.Send(&pb.CreateUserRequest{
            Username: "batch_user",
            Email:    "batch@example.com",
        }); err != nil {
            log.Fatalf("发送失败: %v", err)
        }
    }
    resp, err := batchStream.CloseAndRecv()
    if err != nil {
        log.Fatalf("关闭流失败: %v", err)
    }
    log.Printf("批量创建结果: 成功=%d, 失败=%d", resp.GetSuccessCount(), resp.GetFailureCount())
}
```

---

## 3. Python gRPC 实现

### 3.1 代码生成

```bash
pip install grpcio grpcio-tools

python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=./gen \
    --grpc_python_out=./gen \
    proto/users.proto
```

### 3.2 服务端

```python
import grpc
from concurrent import futures
import time
from google.protobuf import timestamp_pb2

import users_pb2 as pb
import users_pb2_grpc as pb_grpc


class UserServiceServicer(pb_grpc.UserServiceServicer):

    def __init__(self):
        self.users = {}
        self.next_id = 1

    def CreateUser(self, request, context):
        # 输入校验
        if not request.username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "用户名不能为空")

        # 检查邮箱唯一性
        for u in self.users.values():
            if u.email == request.email:
                context.abort(grpc.StatusCode.ALREADY_EXISTS, "邮箱已存在")

        now = timestamp_pb2.Timestamp()
        now.GetCurrentTime()

        user = pb.User(
            id=self.next_id,
            username=request.username,
            email=request.email,
            status=pb.USER_STATUS_ACTIVE,
            created_at=now,
            updated_at=now,
        )
        self.users[user.id] = user
        self.next_id += 1
        return user

    def GetUser(self, request, context):
        user = self.users.get(request.id)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, f"用户 #{request.id} 不存在")
        return user

    def StreamUsers(self, request, context):
        """服务端流式"""
        for user in self.users.values():
            if context.is_active() is False:
                break
            yield user
            time.sleep(0.1)

    def BatchCreateUsers(self, request_iterator, context):
        """客户端流式"""
        success = 0
        failure = 0
        errors = []

        for req in request_iterator:
            try:
                self.CreateUser(req, context)
                success += 1
            except Exception as e:
                failure += 1
                errors.append(f"{req.username}: {str(e)}")

        return pb.BatchCreateResponse(
            success_count=success,
            failure_count=failure,
            errors=errors,
        )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[LoggingInterceptor()],
    )
    pb_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC 服务器启动: :50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
```

### 3.3 客户端

```python
import grpc
import users_pb2 as pb
import users_pb2_grpc as pb_grpc


def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        client = pb_grpc.UserServiceStub(channel)

        # Unary 调用
        user = client.CreateUser(pb.CreateUserRequest(
            username="alice",
            email="alice@example.com",
            password="secure123",
        ))
        print(f"创建用户: {user.username} (ID: {user.id})")

        # 服务端流式
        print("=== 服务端流式 ===")
        for user in client.StreamUsers(pb.StreamUsersRequest(filter="")):
            print(f"  用户: {user.username}")

        # 客户端流式
        print("=== 客户端流式 ===")
        def request_generator():
            for i in range(5):
                yield pb.CreateUserRequest(
                    username=f"batch_user_{i}",
                    email=f"batch{i}@example.com",
                )

        response = client.BatchCreateUsers(request_generator())
        print(f"成功: {response.success_count}, 失败: {response.failure_count}")


if __name__ == "__main__":
    main()
```

---

## 4. 拦截器

### 4.1 服务端拦截器

**Go 实现：**

```go
// Unary 拦截器：日志 + 链路追踪
func UnaryLoggingInterceptor(
    ctx context.Context,
    req interface{},
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (resp interface{}, err error) {
    start := time.Now()

    // 前置处理
    requestID := uuid.New().String()
    ctx = context.WithValue(ctx, "request_id", requestID)
    log.Printf("[gRPC] ➜ %s | request_id=%s", info.FullMethod, requestID)

    // 调用实际处理器
    resp, err = handler(ctx, req)

    // 后置处理
    duration := time.Since(start)
    status := "OK"
    code := codes.OK
    if err != nil {
        if s, ok := status.FromError(err); ok {
            code = s.Code()
            status = s.Message()
        }
    }
    log.Printf("[gRPC] ➜ %s | code=%s | duration=%v | request_id=%s",
        info.FullMethod, code, duration, requestID)

    return resp, err
}

// Stream 拦截器
func StreamLoggingInterceptor(
    srv interface{},
    ss grpc.ServerStream,
    info *grpc.StreamServerInfo,
    handler grpc.StreamHandler,
) error {
    start := time.Now()
    log.Printf("[gRPC-Stream] ➜ %s (client_stream=%v, server_stream=%v)",
        info.FullMethod, info.IsClientStream, info.IsServerStream)

    err := handler(srv, ss)

    log.Printf("[gRPC-Stream] ➜ %s | duration=%v | err=%v",
        info.FullMethod, time.Since(start), err)
    return err
}

// 认证拦截器
func AuthInterceptor(tokenValidator func(string) bool) grpc.UnaryServerInterceptor {
    return func(
        ctx context.Context,
        req interface{},
        info *grpc.UnaryServerInfo,
        handler grpc.UnaryHandler,
    ) (interface{}, error) {
        // 跳过不需要认证的方法
        if info.FullMethod == "/grpc.health.v1.Health/Check" {
            return handler(ctx, req)
        }

        md, ok := metadata.FromIncomingContext(ctx)
        if !ok {
            return nil, status.Error(codes.Unauthenticated, "缺少元数据")
        }

        tokens := md.Get("authorization")
        if len(tokens) == 0 {
            return nil, status.Error(codes.Unauthenticated, "缺少认证 Token")
        }

        if !tokenValidator(strings.TrimPrefix(tokens[0], "Bearer ")) {
            return nil, status.Error(codes.Unauthenticated, "Token 无效")
        }

        return handler(ctx, req)
    }
}

// 拦截器链
func ChainUnaryInterceptors(interceptors ...grpc.UnaryServerInterceptor) grpc.UnaryServerInterceptor {
    return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
        // 从后往前构建调用链
        chain := handler
        for i := len(interceptors) - 1; i >= 0; i-- {
            interceptor := interceptors[i]
            currentHandler := chain
            chain = func(ctx context.Context, req interface{}) (interface{}, error) {
                return interceptor(ctx, req, info, func(ctx context.Context, req interface{}) (interface{}, error) {
                    return currentHandler(ctx, req)
                })
            }
        }
        return chain(ctx, req)
    }
}
```

**Python 实现：**

```python
import grpc
import time
import logging

logger = logging.getLogger(__name__)


class LoggingInterceptor(grpc.ServerInterceptor):

    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        start = time.perf_counter()

        # 前置日志
        logger.info(f"[gRPC] ➜ {method}")

        # 调用下一个处理器
        handler = continuation(handler_call_details)

        def wrapper(behavior):
            def new_behavior(request_or_iterator, context):
                try:
                    result = behavior(request_or_iterator, context)
                    duration = (time.perf_counter() - start) * 1000
                    logger.info(f"[gRPC] ✅ {method} | {duration:.1f}ms")
                    return result
                except Exception as e:
                    duration = (time.perf_counter() - start) * 1000
                    logger.error(f"[gRPC] ❌ {method} | {duration:.1f}ms | {e}")
                    raise
            return new_behavior

        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                wrapper(handler.unary_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler
```

### 4.2 客户端拦截器

```go
// 客户端拦截器：自动添加认证 Token
func AuthClientInterceptor(token string) grpc.UnaryClientInterceptor {
    return func(
        ctx context.Context,
        method string,
        req, reply interface{},
        cc *grpc.ClientConn,
        invoker grpc.UnaryInvoker,
        opts ...grpc.CallOption,
    ) error {
        // 注入 Token 到元数据
        ctx = metadata.AppendToOutgoingContext(ctx, "authorization", "Bearer "+token)
        ctx = metadata.AppendToOutgoingContext(ctx, "x-request-id", uuid.New().String())
        return invoker(ctx, method, req, reply, cc, opts...)
    }
}

// 使用
conn, _ := grpc.Dial(
    "localhost:50051",
    grpc.WithUnaryInterceptor(AuthClientInterceptor("my-jwt-token")),
)
```

---

## 5. gRPC-Gateway

gRPC-Gateway 将 gRPC 服务自动暴露为 RESTful API，让不支持 gRPC 的客户端也能访问。

### 5.1 Protobuf 注解

```protobuf
import "google/api/annotations.proto";

service UserService {
    rpc CreateUser(CreateUserRequest) returns (User) {
        option (google.api.http) = {
            post: "/v1/users"
            body: "*"
        };
    }

    rpc GetUser(GetUserRequest) returns (User) {
        option (google.api.http) = {
            get: "/v1/users/{id}"
        };
    }

    rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {
        option (google.api.http) = {
            get: "/v1/users"
        };
    }

    rpc UpdateUser(UpdateUserRequest) returns (User) {
        option (google.api.http) = {
            patch: "/v1/users/{id}"
            body: "*"
        };
    }

    rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty) {
        option (google.api.http) = {
            delete: "/v1/users/{id}"
        };
    }
}
```

### 5.2 生成网关代码并运行

```bash
# 安装 protoc-gen-grpc-gateway
go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-grpc-gateway@latest

# 生成网关 reverse-proxy 代码
protoc \
    --proto_path=proto \
    --proto_path=$(go env GOPATH)/pkg/mod/github.com/grpc-ecosystem/grpc-gateway/v2*/third_party/googleapis \
    --grpc-gateway_out=. \
    --grpc-gateway_opt=paths=source_relative \
    proto/users.proto
```

```go
// gateway main.go
package main

import (
    "context"
    "log"
    "net/http"

    "github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
    pb "github.com/example/proto/users"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
)

func main() {
    ctx := context.Background()
    ctx, cancel := context.WithCancel(ctx)
    defer cancel()

    mux := runtime.NewServeMux(
        runtime.WithMarshalerOption(runtime.MIMEWildcard, &runtime.JSONPb{
            MarshalOptions: protojson.MarshalOptions{
                UseProtoNames: true,  // snake_case JSON 字段名
            },
        }),
    )

    // 连接 gRPC 服务
    opts := []grpc.DialOption{grpc.WithTransportCredentials(insecure.NewCredentials())}
    err := pb.RegisterUserServiceHandlerFromEndpoint(ctx, mux, "localhost:50051", opts)
    if err != nil {
        log.Fatalf("注册网关失败: %v", err)
    }

    // CORS 中间件
    handler := corsMiddleware(mux)

    log.Println("REST 网关启动: :8080")
    log.Println("  GET    /v1/users")
    log.Println("  POST   /v1/users")
    log.Println("  GET    /v1/users/{id}")
    log.Println("  PATCH  /v1/users/{id}")
    log.Println("  DELETE /v1/users/{id}")

    if err := http.ListenAndServe(":8080", handler); err != nil {
        log.Fatalf("网关启动失败: %v", err)
    }
}

func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

---

## 6. 错误处理与状态码

### 6.1 标准 gRPC 状态码

| 状态码 | 值 | 说明 |
|--------|-----|------|
| `OK` | 0 | 成功 |
| `CANCELLED` | 1 | 调用被取消 |
| `UNKNOWN` | 2 | 未知错误 |
| `INVALID_ARGUMENT` | 3 | 参数无效 |
| `DEADLINE_EXCEEDED` | 4 | 超时 |
| `NOT_FOUND` | 5 | 资源未找到 |
| `ALREADY_EXISTS` | 6 | 资源已存在 |
| `PERMISSION_DENIED` | 7 | 权限不足 |
| `RESOURCE_EXHAUSTED` | 8 | 资源耗尽（限流） |
| `FAILED_PRECONDITION` | 9 | 前置条件不满足 |
| `ABORTED` | 10 | 操作中止 |
| `OUT_OF_RANGE` | 11 | 超出范围 |
| `UNIMPLEMENTED` | 12 | 未实现 |
| `INTERNAL` | 13 | 内部错误 |
| `UNAVAILABLE` | 14 | 服务不可用 |
| `UNAUTHENTICATED` | 16 | 未认证 |

### 6.2 富错误信息（Rich Error Model）

```protobuf
import "google/rpc/error_details.proto";

// 错误详情消息
message FieldViolation {
    string field = 1;
    string description = 2;
}
```

```go
import (
    "google.golang.org/grpc/status"
    "google.golang.org/genproto/googleapis/rpc/errdetails"
)

func (s *userServer) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.User, error) {
    var violations []*errdetails.BadRequest_FieldViolation
    if req.GetUsername() == "" {
        violations = append(violations, &errdetails.BadRequest_FieldViolation{
            Field:       "username",
            Description: "用户名不能为空",
        })
    }
    if req.GetEmail() == "" {
        violations = append(violations, &errdetails.BadRequest_FieldViolation{
            Field:       "email",
            Description: "邮箱不能为空",
        })
    }

    if len(violations) > 0 {
        st, _ := status.New(codes.InvalidArgument, "请求参数校验失败").
            WithDetails(&errdetails.BadRequest{
                FieldViolations: violations,
            }).WithDetails(&errdetails.ErrorInfo{
                Reason:   "VALIDATION_ERROR",
                Domain:   "example.com",
                Metadata: map[string]string{"code": "400"},
            }).ToProto()
        return nil, st.Err()
    }

    // 正常逻辑...
}
```

---

## 7. 最佳实践

### 7.1 设计原则

- ✅ **Protobuf 版本管理**：使用 `package` 加版本号（如 `users.v1`），新版本用新包名
- ✅ **字段编号永不复用**：废弃字段保留编号，防止兼容性问题
- ✅ **使用 `optional`** 标注真正可选的字段（proto3 默认值无法区分"未设置"和"零值"）
- ✅ **请求/响应使用独立消息**，不要复用
- ✅ **合理设置 Deadline**：客户端必须设置超时，服务端检查 context
- ✅ **拦截器处理横切关注点**：认证、日志、链路追踪、限流
- ✅ **健康检查**：实现 `grpc.health.v1.Health` 服务
- ✅ **合理使用流式**：大数据量传输、实时推送、聊天场景使用流式
- ✅ **连接池复用**：客户端 `grpc.Dial` 后保持连接复用
- ❌ 不要在 `.proto` 中定义业务逻辑
- ❌ 不要发送过大的消息（建议单消息 < 1MB，大文件用流式或对象存储）
- ❌ 不要忽略 context 取消信号

### 7.2 性能优化

```go
// 服务端优化配置
s := grpc.NewServer(
    grpc.MaxRecvMsgSize(10*1024*1024),   // 10MB
    grpc.MaxSendMsgSize(10*1024*1024),
    grpc.MaxConcurrentStreams(100),
    grpc.KeepaliveParams(keepalive.ServerParameters{
        MaxConnectionIdle:     5 * time.Minute,
        MaxConnectionAge:      30 * time.Minute,
        MaxConnectionAgeGrace: 5 * time.Second,
        Time:                  30 * time.Second,
        Timeout:               10 * time.Second,
    }),
)

// 客户端优化配置
conn, _ := grpc.Dial(
    target,
    grpc.WithTransportCredentials(insecure.NewCredentials()),
    grpc.WithDefaultCallOptions(
        grpc.MaxCallRecvMsgSize(10*1024*1024),
    ),
    grpc.WithKeepaliveParams(keepalive.ClientParameters{
        Time:                30 * time.Second,
        Timeout:             10 * time.Second,
        PermitWithoutStream: true,
    }),
    grpc.WithDefaultServiceConfig(`{
        "loadBalancingPolicy": "round_robin",
        "methodConfig": [{
            "name": [{"service": "com.example.users.UserService"}],
            "retryPolicy": {
                "maxAttempts": 3,
                "initialBackoff": "0.1s",
                "maxBackoff": "1s",
                "backoffMultiplier": 2,
                "retryableStatusCodes": ["UNAVAILABLE", "DEADLINE_EXCEEDED"]
            }
        }]
    }`),
)
```

### 7.3 Docker 部署

```dockerfile
# 多阶段构建：Go gRPC 服务
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server

FROM alpine:3.19
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/server /app/server
EXPOSE 50051
HEALTHCHECK --interval=30s --timeout=5s \
    CMD grpc_health_probe -addr=localhost:50051 || exit 1
ENTRYPOINT ["/app/server"]
```

---

## 8. 相关页面

- [[Java Spring Boot 开发]]
- [[Node.js 后端开发]]
- [[Python 异步编程]]
- [[Rust 系统编程]]
- [[Protobuf 最佳实践]]
- [[微服务架构]]
- [[服务网格与 Istio]]
- [[gRPC-Gateway 集成]]

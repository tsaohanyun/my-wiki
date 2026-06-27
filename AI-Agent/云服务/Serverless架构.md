---
title: Serverless架构
aliases:
  - 无服务器架构
  - FaaS Architecture
  - Serverless Computing
tags:
  - cloud
  - serverless
  - faas
  - architecture
  - microservices
type: guide
status: active
created: 2025-01-27
updated: 2025-01-27
source: internal
difficulty: advanced
project: cloud-services
---

# Serverless架构

## 什么是Serverless

Serverless（无服务器）是一种云原生开发模型，开发者无需管理服务器基础设施，只需专注于编写业务逻辑。云提供商负责基础设施的供应、扩展和维护。

## Serverless vs 传统架构

| 特性 | 传统架构 | Serverless |
|------|----------|------------|
| 服务器管理 | 需要 | 不需要 |
| 扩展方式 | 手动/自动伸缩 | 自动扩展 |
| 计费模式 | 按资源预留 | 按实际使用 |
| 冷启动 | 无 | 可能有 |
| 运行时长限制 | 无 | 通常15分钟 |
| 适用场景 | 长期运行服务 | 事件驱动任务 |

---

## 函数计算

### AWS Lambda vs 阿里云函数计算

| 特性 | AWS Lambda | 阿里云函数计算 |
|------|------------|---------------|
| 最大内存 | 10GB | 32GB |
| 最大超时 | 15分钟 | 10分钟（HTTP）/ 10分钟（事件） |
| 支持运行时 | Node.js, Python, Java, Go, .NET, Ruby, Rust | Node.js, Python, Java, Go, PHP, .NET |
| 容器镜像支持 | 是 | 是 |
| GPU支持 | 否 | 是 |
| 价格 | $0.0000166667/GB-s | ¥0.00011108/GB-s |

### 函数计算架构示例

```python
# AWS Lambda函数示例
import json
import boto3
from datetime import datetime

# 初始化客户端（在函数外部，复用连接）
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
table = dynamodb.Table('orders')

def lambda_handler(event, context):
    """
    处理订单消息
    """
    for record in event['Records']:
        try:
            # 解析SQS消息
            message = json.loads(record['body'])
            order_id = message['order_id']
            customer_id = message['customer_id']
            items = message['items']

            # 计算订单总价
            total = sum(item['price'] * item['quantity'] for item in items)

            # 保存到DynamoDB
            table.put_item(Item={
                'order_id': order_id,
                'customer_id': customer_id,
                'items': items,
                'total': total,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            })

            # 发送到下一个处理队列
            sqs.send_message(
                QueueUrl='https://sqs.amazonaws.com/123456789/payment-queue',
                MessageBody=json.dumps({
                    'order_id': order_id,
                    'total': total
                })
            )

            print(f"Order {order_id} processed successfully")

        except Exception as e:
            print(f"Error processing order: {e}")
            # 发送到死信队列
            raise

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Orders processed'})
    }
```

### 阿里云函数计算示例

```python
# 阿里云函数计算示例
import json
from alibabacloud_fc20230330.client import Client
from alibabacloud_fc20230330 import models as fc_models

def handler(event, context):
    """
    HTTP触发器处理函数
    """
    # 获取请求信息
    request = json.loads(event)
    method = request.get('httpMethod', 'GET')
    path = request.get('path', '/')

    # 路由处理
    if method == 'GET' and path == '/api/orders':
        return get_orders(request)
    elif method == 'POST' and path == '/api/orders':
        return create_order(request)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }

def get_orders(request):
    """获取订单列表"""
    # 使用表格存储（TableStore）替代DynamoDB
    from tablestore import OTSClient

    client = OTSClient(
        endpoint='https://instance.cn-hangzhou.ots.aliyuncs.com',
        access_key_id=context.credentials.access_key_id,
        access_key_secret=context.credentials.access_key_secret,
        instance_name='my-instance'
    )

    # 查询订单
    _, _, rows, _ = client.get_range(
        table_name='orders',
        direction='FORWARD',
        inclusive_start_primary_key=[('order_id', 'INF_MIN')],
        exclusive_end_primary_key=[('order_id', 'INF_MAX')],
        limit=100
    )

    orders = [
        dict(zip(['order_id', 'customer_id', 'total', 'status'],
                 [col.value for col in row]))
        for row in rows
    ]

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(orders)
    }

def create_order(request):
    """创建新订单"""
    body = json.loads(request.get('body', '{}'))

    # 验证请求
    if 'customer_id' not in body or 'items' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request'})
        }

    # 生成订单ID
    import uuid
    order_id = str(uuid.uuid4())

    # 保存订单
    # ... 业务逻辑 ...

    return {
        'statusCode': 201,
        'body': json.dumps({'order_id': order_id})
    }
```

---

## 事件驱动架构

### 1. 事件驱动模式

```
┌─────────────────────────────────────────────────────────────────┐
│                     事件驱动架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │  API     │───▶│  Event  │───▶│  Event  │───▶│  Action │     │
│  │ Gateway  │    │ Source  │    │  Bus    │    │ Handler │     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│                       │              │              │            │
│                       ▼              ▼              ▼            │
│                  ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│                  │  S3 /   │    │  SQS /  │    │ Lambda  │     │
│                  │  OSS    │    │  EventBridge │ │ / FC    │     │
│                  └─────────┘    └─────────┘    └─────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. AWS EventBridge配置

```hcl
# EventBridge规则
resource "aws_cloudwatch_event_rule" "order_created" {
  name        = "order-created"
  description = "Capture order created events"

  event_pattern = jsonencode({
    source      = ["custom.orders"]
    detail-type = ["OrderCreated"]
    detail = {
      status = ["pending"]
    }
  })
}

# EventBridge目标
resource "aws_cloudwatch_event_target" "process_order" {
  rule      = aws_cloudwatch_event_rule.order_created.name
  target_id = "ProcessOrder"
  arn       = aws_lambda_function.order_processor.arn
}

resource "aws_cloudwatch_event_target" "send_notification" {
  rule      = aws_cloudwatch_event_rule.order_created.name
  target_id = "SendNotification"
  arn       = aws_sns_topic.order_notifications.arn
}

# Lambda权限
resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_processor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.order_created.arn
}
```

### 3. 事件发布示例

```python
import boto3
import json
from datetime import datetime

eventbridge = boto3.client('events')

def publish_order_event(order_id, customer_id, items, total):
    """发布订单创建事件"""
    event = {
        'Source': 'custom.orders',
        'DetailType': 'OrderCreated',
        'Detail': json.dumps({
            'order_id': order_id,
            'customer_id': customer_id,
            'items': items,
            'total': total,
            'status': 'pending',
            'timestamp': datetime.utcnow().isoformat()
        }),
        'EventBusName': 'default'
    }

    response = eventbridge.put_events(Entries=[event])
    return response
```

---

## 冷启动优化

### 1. 什么是冷启动

冷启动是指Serverless函数首次调用或长时间未调用后的初始化过程。包括：
- 下载代码
- 初始化运行时
- 执行初始化代码
- 运行函数

### 2. 冷启动影响因素

| 因素 | 影响程度 | 优化建议 |
|------|----------|----------|
| 代码包大小 | 高 | 压缩代码、移除不必要依赖 |
| 运行时选择 | 中 | 选择轻量级运行时 |
| VPC配置 | 高 | 使用VPC连接器 |
| 初始化逻辑 | 中 | 延迟加载、复用连接 |
| 内存配置 | 中 | 合理配置内存 |

### 3. 冷启动优化策略

```python
# ❌ 不好的做法：每次调用都初始化
def bad_handler(event, context):
    import boto3
    import pymysql

    # 每次调用都创建新连接
    s3 = boto3.client('s3')
    conn = pymysql.connect(host='...', user='...', password='...')

    result = conn.execute('SELECT * FROM users')
    return result


# ✅ 好的做法：复用连接
import boto3
import pymysql

# 在函数外部初始化，利用容器复用
s3 = boto3.client('s3')

# 连接池
_db_connection = None

def get_db_connection():
    global _db_connection
    if _db_connection is None or not _db_connection.open:
        _db_connection = pymysql.connect(
            host='...',
            user='...',
            password='...',
            cursorclass=pymysql.cursors.DictCursor
        )
    return _db_connection

def good_handler(event, context):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM users')
        result = cursor.fetchall()
    return result
```

```python
# 延迟加载示例
import importlib

_heavy_module = None

def get_heavy_module():
    global _heavy_module
    if _heavy_module is None:
        _heavy_module = importlib.import_module('heavy_module')
    return _heavy_module

def handler(event, context):
    # 只在需要时加载
    if event.get('need_heavy_processing'):
        heavy = get_heavy_module()
        return heavy.process(event['data'])
    return {'status': 'processed'}
```

### 4. Provisioned Concurrency（预配置并发）

```hcl
# AWS Lambda预配置并发
resource "aws_lambda_provisioned_concurrency_config" "api" {
  function_name                  = aws_lambda_function.api.function_name
  provisioned_concurrent_executions = 10
  qualifier                     = aws_lambda_function.api.version
}

# 阿里云函数计算预留实例
resource "alicloud_fc_function_async_invoke_config" "api" {
  service_name  = alicloud_fc_service.api.name
  function_name = alicloud_fc_function.api.name

  async_invoker_config {
    max_async_retry_attempts = 2
    max_async_event_age_in_seconds = 3600

    destination_config {
      on_failure {
        destination = alicloud_mns_queue.dead_letter.name
      }
    }
  }
}
```

---

## 成本模型

### 1. 成本计算公式

```
函数成本 = 请求数 × (内存GB × 执行时间秒) × 单价
```

### 2. 成本对比分析

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ServerlessCostEstimate:
    """Serverless成本估算器"""

    # 请求参数
    monthly_requests: int
    avg_duration_ms: int
    memory_mb: int

    # AWS Lambda定价
    AWS_REQUEST_PRICE = 0.0000002  # $0.20 per 1M requests
    AWS_GB_SECOND_PRICE = 0.0000166667  # $0.0000166667 per GB-second

    # 阿里云函数计算定价
    ALI_REQUEST_PRICE = 0.00000012  # ¥0.12 per 1M requests
    ALI_GB_SECOND_PRICE = 0.00011108  # ¥0.00011108 per GB-second

    def calculate_aws_cost(self) -> float:
        """计算AWS Lambda成本"""
        request_cost = self.monthly_requests * self.AWS_REQUEST_PRICE
        compute_cost = (
            self.monthly_requests
            * (self.memory_mb / 1024)
            * (self.avg_duration_ms / 1000)
            * self.AWS_GB_SECOND_PRICE
        )
        return request_cost + compute_cost

    def calculate_ali_cost(self) -> float:
        """计算阿里云函数计算成本"""
        request_cost = self.monthly_requests * self.ALI_REQUEST_PRICE
        compute_cost = (
            self.monthly_requests
            * (self.memory_mb / 1024)
            * (self.avg_duration_ms / 1000)
            * self.ALI_GB_SECOND_PRICE
        )
        return request_cost + compute_cost

    def compare_with_server(self, server_monthly_cost: float) -> dict:
        """与传统服务器成本对比"""
        aws_cost = self.calculate_aws_cost()
        ali_cost = self.calculate_ali_cost()

        return {
            'serverless': {
                'AWS Lambda': f"${aws_cost:.2f}",
                '阿里云函数计算': f"¥{ali_cost:.2f}"
            },
            'server': f"${server_monthly_cost:.2f}",
            'recommendation': 'Serverless' if min(aws_cost, ali_cost) < server_monthly_cost else 'Server'
        }

# 示例：估算API Gateway + Lambda成本
estimator = ServerlessCostEstimate(
    monthly_requests=10_000_000,  # 1000万次请求
    avg_duration_ms=200,          # 平均200ms
    memory_mb=256                 # 256MB内存
)

print(f"AWS Lambda月成本: ${estimator.calculate_aws_cost():.2f}")
print(f"阿里云函数计算月成本: ¥{estimator.calculate_ali_cost():.2f}")
```

### 3. 成本优化建议

| 优化策略 | 效果 | 实施难度 |
|----------|------|----------|
| 合理配置内存 | 降低20-40% | 低 |
| 减少执行时间 | 降低30-50% | 中 |
| 使用Provisioned Concurrency | 降低冷启动成本 | 中 |
| 批量处理请求 | 降低请求数量 | 中 |
| 使用ARM架构 | 降低20%计算成本 | 低 |

---

## Serverless框架

### 1. 使用Serverless Framework部署

```yaml
# serverless.yml
service: my-api

provider:
  name: aws
  runtime: python3.12
  stage: ${opt:stage, 'dev'}
  region: ap-northeast-1
  memorySize: 256
  timeout: 30

  environment:
    TABLE_NAME: ${self:service}-${self:provider.stage}
    STAGE: ${self:provider.stage}

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:PutItem
            - dynamodb:GetItem
            - dynamodb:Scan
            - dynamodb:Query
          Resource: !GetAtt OrdersTable.Arn

functions:
  api:
    handler: src/handler.api
    events:
      - httpApi:
          path: /orders
          method: GET
      - httpApi:
          path: /orders
          method: POST
      - httpApi:
          path: /orders/{id}
          method: GET

  orderProcessor:
    handler: src/processor.handler
    memorySize: 512
    timeout: 60
    events:
      - sqs:
          arn: !GetAtt OrderQueue.Arn
          batchSize: 10

resources:
  Resources:
    OrdersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-${self:provider.stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: order_id
            AttributeType: S
        KeySchema:
          - AttributeName: order_id
            KeyType: HASH

    OrderQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-${self:provider.stage}-orders
        VisibilityTimeout: 120
        RedrivePolicy:
          deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
          maxReceiveCount: 3

    DeadLetterQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-${self:provider.stage}-orders-dlq
```

### 2. 部署命令

```bash
# 安装Serverless Framework
npm install -g serverless

# 部署到开发环境
serverless deploy --stage dev

# 部署到生产环境
serverless deploy --stage prod

# 查看部署信息
serverless info --stage prod

# 查看日志
serverless logs -f api --stage prod

# 本地调试
serverless offline
```

---

## 最佳实践

### 1. 函数设计原则

- ✅ **单一职责**：每个函数只做一件事
- ✅ **无状态设计**：不在函数内存储状态
- ✅ **幂等性**：函数可以安全地重复执行
- ✅ **快速失败**：尽早验证输入，快速返回错误
- ✅ **超时处理**：设置合理的超时时间

### 2. 错误处理

```python
import json
import logging
from functools import wraps

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def error_handler(func):
    """统一错误处理装饰器"""
    @wraps(func)
    def wrapper(event, context):
        try:
            return func(event, context)
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }
        except Exception as e:
            logger.error(f"Internal error: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal server error'})
            }
    return wrapper

@error_handler
def handler(event, context):
    # 业务逻辑
    body = json.loads(event.get('body', '{}'))

    if 'name' not in body:
        raise ValueError("Name is required")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': f"Hello {body['name']}"})
    }
```

### 3. 监控和追踪

```python
import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# 自动为所有AWS SDK调用添加X-Ray追踪
patch_all()

@xray_recorder.capture('process_order')
def process_order(order_data):
    """处理订单并记录追踪信息"""
    # 添加自定义注解
    xray_recorder.current_subsegment().put_annotation('order_id', order_data['order_id'])
    xray_recorder.current_subsegment().put_metadata('order_data', order_data)

    # 业务逻辑
    # ...

    return result
```

---

## 相关页面

- [[AWS核心服务指南]] - Lambda服务详解
- [[阿里云服务指南]] - 函数计算详解
- [[云成本优化]] - Serverless成本优化
- [[多云架构设计]] - 跨云Serverless部署

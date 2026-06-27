---
title: AWS核心服务指南
aliases:
  - AWS Services Guide
  - AWS核心服务
  - AWS Core Services
tags:
  - cloud
  - aws
  - infrastructure
  - devops
type: guide
status: active
created: 2025-01-27
updated: 2025-01-27
source: internal
difficulty: intermediate
project: cloud-services
---

# AWS核心服务指南

## 服务概览

AWS（Amazon Web Services）是全球领先的云服务提供商，提供200+全功能服务。本文档介绍最常用的核心服务。

## 1. EC2（Elastic Compute Cloud）

### 实例类型选择

| 系列 | 用途 | 示例实例 |
|------|------|----------|
| T系列 | 通用突发型 | t3.micro, t3.medium |
| M系列 | 通用平衡型 | m5.large, m6i.xlarge |
| C系列 | 计算优化型 | c5.2xlarge, c6i.large |
| R系列 | 内存优化型 | r5.xlarge, r6i.2xlarge |
| G系列 | GPU实例 | g4dn.xlarge, p3.2xlarge |

### 启动EC2实例（Terraform）

```hcl
provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_instance" "web_server" {
  ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2
  instance_type = "t3.medium"
  key_name      = "my-key-pair"

  vpc_security_group_ids = [aws_security_group.web_sg.id]
  subnet_id              = aws_subnet.public.id

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name        = "web-server"
    Environment = "production"
    Team        = "platform"
  }
}

resource "aws_security_group" "web_sg" {
  name        = "web-server-sg"
  description = "Security group for web server"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### EC2最佳实践

- ✅ 使用Spot实例降低70%成本（适用于无状态工作负载）
- ✅ 启用详细监控（CloudWatch 1分钟粒度）
- ✅ 使用启动模板（Launch Template）标准化实例配置
- ✅ 定期轮换AMI，保持系统补丁更新
- ✅ 使用IAM角色而非硬编码凭证
- ❌ 避免使用根账户操作EC2
- ❌ 避免在公网暴露SSH端口

---

## 2. S3（Simple Storage Service）

### 存储类别

| 存储类别 | 持久性 | 可用性 | 检索费用 | 适用场景 |
|----------|--------|--------|----------|----------|
| S3 Standard | 99.999999999% | 99.99% | 无 | 频繁访问 |
| S3 IA | 99.999999999% | 99.9% | 按GB计费 | 低频访问 |
| S3 Glacier | 99.999999999% | 99.99% | 分钟~小时 | 归档存储 |
| S3 Glacier Deep Archive | 99.999999999% | 99.99% | 12~48小时 | 深度归档 |

### S3配置示例

```hcl
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data-bucket"

  tags = {
    Name        = "Data Bucket"
    Environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "data_bucket" {
  bucket = aws_s3_bucket.data_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_bucket" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data_bucket" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_bucket" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### S3最佳实践

- ✅ 启用版本控制防止误删除
- ✅ 使用生命周期策略自动降级存储类别
- ✅ 启用服务端加密（SSE-S3或SSE-KMS）
- ✅ 阻止公共访问（除非必要）
- ✅ 使用预签名URL临时共享文件
- ✅ 启用访问日志审计

---

## 3. RDS（Relational Database Service）

### 支持的数据库引擎

- MySQL / MariaDB
- PostgreSQL
- Oracle
- SQL Server
- Amazon Aurora（MySQL/PostgreSQL兼容）

### RDS配置示例

```hcl
resource "aws_db_subnet_group" "main" {
  name       = "main-db-subnet"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "Main DB subnet group"
  }
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier     = "my-aurora-cluster"
  engine                 = "aurora-postgresql"
  engine_version         = "15.4"
  database_name          = "mydb"
  master_username        = "admin"
  master_password        = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"

  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  deletion_protection = true
  skip_final_snapshot = false

  tags = {
    Name        = "aurora-cluster"
    Environment = "production"
  }
}

resource "aws_rds_cluster_instance" "aurora_instances" {
  count              = 2
  identifier         = "my-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.r6g.large"
  engine             = aws_rds_cluster.aurora.engine

  performance_insights_enabled = true
}
```

### RDS最佳实践

- ✅ 使用Multi-AZ部署实现高可用
- ✅ 启用自动备份（保留期7天+）
- ✅ 启用存储加密
- ✅ 使用Parameter Group优化数据库参数
- ✅ 定期创建手动快照
- ✅ 启用Performance Insights监控慢查询

---

## 4. Lambda

### Lambda函数示例

```python
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

def lambda_handler(event, context):
    """
    处理API Gateway请求
    """
    try:
        logger.info(f"Event: {json.dumps(event)}")

        http_method = event['httpMethod']
        path = event['path']

        if http_method == 'GET' and path == '/items':
            response = table.scan()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response['Items'])
            }

        elif http_method == 'POST' and path == '/items':
            body = json.loads(event['body'])
            table.put_item(Item=body)
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Item created'})
            }

        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
```

### Lambda Terraform配置

```hcl
resource "aws_lambda_function" "api_handler" {
  filename         = "lambda.zip"
  function_name    = "api-handler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.lambda_handler"
  runtime         = "python3.12"
  timeout         = 30
  memory_size     = 256

  vpc_config {
    subnet_ids         = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  environment {
    variables = {
      TABLE_NAME = "my-table"
      REGION     = "ap-northeast-1"
    }
  }

  tracing_config {
    mode = "Active"  # X-Ray tracing
  }
}
```

### Lambda最佳实践

- ✅ 保持函数小巧，单一职责
- ✅ 使用环境变量存储配置
- ✅ 复用连接（数据库、SDK客户端）利用容器复用
- ✅ 设置合理的超时时间和内存
- ✅ 使用Lambda Layers共享公共依赖
- ✅ 启用X-Ray进行分布式追踪

---

## 5. VPC（Virtual Private Cloud）

### VPC架构示例

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "production-vpc"
  }
}

# 公有子网
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-northeast-1a"
  map_public_ip_on_launch = true

  tags = { Name = "public-a" }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "ap-northeast-1c"
  map_public_ip_on_launch = true

  tags = { Name = "public-b" }
}

# 私有子网
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "ap-northeast-1a"

  tags = { Name = "private-a" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "ap-northeast-1c"

  tags = { Name = "private-b" }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "main-igw" }
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id
  tags          = { Name = "main-nat" }
}

# 路由表
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
}
```

---

## 6. IAM（Identity and Access Management）

### IAM策略示例

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ReadOnlyAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### IAM Terraform配置

```hcl
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
```

### IAM最佳实践

- ✅ 启用MFA（多因素认证）
- ✅ 遵循最小权限原则
- ✅ 使用IAM角色而非长期凭证
- ✅ 定期轮换访问密钥
- ✅ 使用AWS Organizations管理多账户
- ✅ 启用CloudTrail审计IAM操作

---

## 相关页面

- [[阿里云服务指南]] - 阿里云对应服务对比
- [[多云架构设计]] - 多云环境下的架构设计
- [[云成本优化]] - AWS成本优化策略
- [[Serverless架构]] - Lambda深度实践

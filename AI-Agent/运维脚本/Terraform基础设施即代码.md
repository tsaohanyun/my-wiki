---
title: "Terraform基础设施即代码"
aliases:
  - Terraform IaC
  - Terraform指南
  - 基础设施即代码
tags:
  - terraform
  - iac
  - 云原生
  - 基础设施
  - 运维
type: reference
status: active
created: 2025-01-01
updated: 2025-06-27
source: internal
difficulty: intermediate
project: AI-Agent
---

# Terraform基础设施即代码

## 概述

Terraform是HashiCorp开发的基础设施即代码（IaC）工具，通过声明式配置文件管理云基础设施的生命周期。

---

## 1. 基础配置

### 1.1 Provider配置

```hcl
# main.tf
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.200"
    }
  }
}

# AWS Provider
provider "aws" {
  region = "us-west-2"

  default_tags {
    tags = {
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}
```

### 1.2 后端存储

```hcl
# 使用S3存储状态
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/network/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# 使用阿里云OSS
terraform {
  backend "oss" {
    bucket   = "terraform-state-bucket"
    prefix   = "prod"
    region   = "cn-hangzhou"
    encrypt  = true
  }
}
```

### 1.3 变量与输出

```hcl
# variables.tf
variable "environment" {
  description = "部署环境"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment 必须是 dev, staging, 或 prod"
  }
}

variable "instance_config" {
  description = "实例配置"
  type = object({
    instance_type = string
    disk_size     = number
    disk_type     = optional(string, "gp3")
  })
}

variable "tags" {
  description = "资源标签"
  type        = map(string)
  default     = {}
}

# outputs.tf
output "instance_ip" {
  description = "实例公网IP"
  value       = aws_instance.web.public_ip
}

output "db_endpoint" {
  description = "数据库连接端点"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}
```

---

## 2. 资源定义

### 2.1 计算资源

```hcl
# EC2实例
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_config.instance_type
  subnet_id     = aws_subnet.public.id

  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.deployer.key_name

  root_block_device {
    volume_size = var.instance_config.disk_size
    volume_type = var.instance_config.disk_type
    encrypted   = true
  }

  user_data = templatefile("${path.module}/templates/init.sh", {
    hostname = "web-${var.environment}"
  })

  tags = merge(var.tags, {
    Name = "web-${var.environment}"
  })
}

# Auto Scaling Group
resource "aws_autoscaling_group" "web" {
  name                = "web-asg-${var.environment}"
  desired_capacity    = 2
  max_size            = 10
  min_size            = 2
  target_group_arns   = [aws_lb_target_group.main.arn]
  vpc_zone_identifier = aws_subnet.private[*].id

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
  }
}
```

### 2.2 网络资源

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "vpc-${var.environment}" }
}

# 子网
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "public-${count.index}" }
}

# 安全组
resource "aws_security_group" "web" {
  name_prefix = "web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
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

  lifecycle {
    create_before_destroy = true
  }
}
```

### 2.3 数据库资源

```hcl
resource "aws_db_instance" "main" {
  identifier     = "db-${var.environment}"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 500
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "appdb"
  username = "admin"
  password = var.db_password  # 从外部注入

  multi_az               = var.environment == "prod"
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = 7
  skip_final_snapshot     = var.environment != "prod"

  tags = { Name = "db-${var.environment}" }
}
```

---

## 3. 模块化

### 3.1 模块结构

```
modules/
├── vpc/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ecs-service/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── rds/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

### 3.2 模块定义

```hcl
# modules/vpc/main.tf
variable "cidr_block" {
  type = string
}

variable "environment" {
  type = string
}

variable "azs" {
  type    = list(string)
  default = ["cn-hangzhou-a", "cn-hangzhou-b"]
}

resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  tags = { Name = "vpc-${var.environment}" }
}

resource "aws_subnet" "private" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.cidr_block, 8, count.index + 10)
  availability_zone = var.azs[count.index]
}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}
```

### 3.3 模块调用

```hcl
# 调用本地模块
module "vpc" {
  source = "./modules/vpc"

  cidr_block  = "10.0.0.0/16"
  environment = var.environment
  azs         = ["cn-hangzhou-a", "cn-hangzhou-b"]
}

# 调用远程模块
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "eks-${var.environment}"
  cluster_version = "1.28"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
}

# 使用模块输出
resource "aws_security_group" "app" {
  vpc_id = module.vpc.vpc_id
}
```

---

## 4. 状态管理

### 4.1 状态操作命令

```bash
# 初始化
terraform init
terraform init -upgrade          # 升级provider
terraform init -migrate-state    # 迁移后端

# 计划与应用
terraform plan -out=tfplan
terraform apply tfplan
terraform apply -auto-approve

# 查看状态
terraform state list
terraform state show aws_instance.web

# 移动/重命名资源
terraform state mv aws_instance.old aws_instance.new

# 从状态中移除（不删除资源）
terraform state rm aws_instance.orphan

# 导入已有资源
terraform import aws_instance.web i-1234567890abcdef0
```

### 4.2 工作空间

```bash
# 创建工作空间
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# 切换工作空间
terraform workspace select prod

# 在配置中使用
locals {
  env_config = {
    dev     = { instance_type = "t3.micro",  count = 1 }
    staging = { instance_type = "t3.small",  count = 2 }
    prod    = { instance_type = "t3.large",  count = 4 }
  }
  config = local.env_config[terraform.workspace]
}
```

### 4.3 状态锁

```hcl
# DynamoDB表用于状态锁
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

---

## 5. 高级特性

### 5.1 for_each与dynamic

```hcl
# for_each遍历
resource "aws_iam_user" "users" {
  for_each = toset(["alice", "bob", "charlie"])
  name     = each.value
}

# dynamic块
resource "aws_security_group" "main" {
  name = "dynamic-sg"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

### 5.2 数据源

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-*"]
  }
}

data "aws_caller_identity" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
```

### 5.3 provisioner（不推荐但了解）

```hcl
resource "aws_instance" "web" {
  # ... 配置

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx",
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }

  # 最好使用 user_data 或 Ansible 替代 provisioner
}
```

---

## 6. CI/CD集成

### 6.1 GitHub Actions

```yaml
# .github/workflows/terraform.yml
name: Terraform
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color
        continue-on-error: true

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve
```

---

## 最佳实践

| 编号 | 实践 | 说明 |
|------|------|------|
| 1 | 远程状态存储 | 使用S3/OSS+DynamoDB锁 |
| 2 | 模块化 | 可复用模块减少重复代码 |
| 3 | 变量验证 | 使用 `validation` 块检查输入 |
| 4 | 版本锁定 | provider和模块都锁定版本 |
| 5 | 分环境部署 | 使用workspace或目录隔离 |
| 6 | Plan先审后Apply | CI中plan作为检查点 |
| 7 | 敏感数据管理 | 密码等用外部注入，不写入配置 |
| 8 | 标签规范 | 统一标签便于成本管理 |

---

## 相关页面

- [[Shell脚本编程指南]] - Shell脚本基础知识
- [[Grafana可视化指南]] - 基础设施监控可视化
- [[监控告警体系设计]] - 云资源监控告警
- [[ELK进阶配置]] - 日志收集与分析

project: hermes
---
title: XXL JOB定时任务管理
aliases: [XXL-JOB, 定时任务, 任务调度]
tags: [xxl-job, 定时任务, 运维]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: devops/xxl-job-admin
difficulty: advanced
---
# XXL-JOB 定时任务管理

## 概述

XXL-JOB 是分布式任务调度平台，通过REST API管理定时任务。

## 环境配置

| 环境 | 端口 | 访问地址 |
|------|------|----------|
| UAT | 18081 | 通过跳板机2223端口 |
| PROD | 18082 | 通过跳板机2223端口 |

**认证**：admin / 123456

## 常用API

### 1. 触发任务

```bash
curl -X POST "http://localhost:18081/api/jobinfo/trigger" \
  -H "Content-Type: application/json" \
  -H "XXL-JOB-ACCESS-TOKEN: default" \
  -d '{
    "jobId": 479,
    "executorParam": "{\"code\":\"lm_st_balances\",\"t\":{\"createDate\":\"2026-06-01\",\"endDate\":\"2026-06-30\"}}"
  }'
```

### 2. 查询任务状态

```bash
curl "http://localhost:18081/api/jobinfo/list" \
  -H "XXL-JOB-ACCESS-TOKEN: default"
```

## 重要陷阱

### 1. trigger API不用默认参数

**错误**：只传jobId，不传executorParam

**正确**：必须显式传executorParam，否则任务会用空参数执行

### 2. Token过长导致bash引号问题

**问题**：token超过400字符时，bash嵌套引号极易出错

**解决方案**：
1. 用Python生成含完整token的.bat文件
2. .bat文件必须CRLF换行 + chcp 65001开头
3. SCP上传到跳板机后执行

### 3. 隧道需手动建立

```bash
# 通过跳板机建立隧道
sshpass -p 'Tunnel@2026!' ssh -L 18081:localhost:18081 -N tunnel@162.14.73.9 -p 2223
```

## 相关页面

- [[IIDP绩效指标计算]]
- [[SSH隧道与远程管理]]
project: hermes
---
title: IIDP绩效指标计算
aliases: [IIDP, 绩效指标, LmIndicator]
tags: [iidp, 绩效, api]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: data-science/lm-indicator-calc
difficulty: advanced
---
# IIDP 绩效指标计算

## 概述

IIDP平台提供JSON-RPC API用于绩效指标计算。

## API配置

- **端点**：`http://172.20.193.21:32679/api/root/rpc/login`
- **模型**：LmIndicatorOperations
- **认证**：密码需base64编码

## 计算流程

### 1. 获取Token

```bash
# 通过跳板机执行PowerShell获取token
ssh -p 2223 -i hermesdashborad.pem ThinkPad@localhost "powershell -Command "$response = Invoke-RestMethod -Uri 'http://172.20.193.21:32679/api/root/rpc/login' -Method Post -Body @{username='admin'; password='base64encoded'} -ContentType 'application/json'; $response.result.data.token""
```

### 2. 调用计算接口

```json
{
  "jsonrpc": "2.0",
  "method": "calculate",
  "params": {
    "model": "LmIndicatorOperations",
    "startDate": "2026-06-01",
    "endDate": "2026-06-30"
  },
  "id": 1
}
```

## 并行策略

**问题**：单批指标过多(>20)会超时

**解决方案**：
1. 拆成每批7~9个指标的独立PS1脚本
2. SCP上传跳板机后并行发射多个SSH进程
3. 跳板机PowerShell 5.1不支持`-AsJob`参数

## 数据验证

结果以`lm_st_summary_table(validflag=1)`为准。

## 相关页面

- [[XXL-JOB定时任务管理]]
- [[SSH隧道与远程管理]]
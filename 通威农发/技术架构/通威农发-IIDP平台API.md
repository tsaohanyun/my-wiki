---
author: Hermes Wiki Agent
created: '2026-06-24'
description: 项目：**通威农发** > 本页面记录通过抓包/逆向分析发现的IIDP平台REST/JSON-RPC接口，包括认证方式、通用调用格式和已验证的具体业务接口。
  IIDP平台（地址 `http://172.20.193.21:32679`）使用 JSON-RPC 2.0 协议作为核心通信机制，所有业务操作通过统一的 `/api/root/rpc/service`
  端点完成。 **请求体：** ```j...
project: 通威农发
status: published
tags:
- user
- workflow
- template
- tw-nongfa
- database
title: IIDP平台API接口文档
type: architecture
updated: '2026-06-24'
version: 1.0.20260626
aliases:
  - "IIDP"
  - "IIDP API"
  - "JSON-RPC"
---


项目：**通威农发**

# IIDP平台API接口文档

> 本页面记录通过抓包/逆向分析发现的IIDP平台REST/JSON-RPC接口，包括认证方式、通用调用格式和已验证的具体业务接口。

## 概述

IIDP平台（地址 `http://172.20.193.21:32679`）使用 JSON-RPC 2.0 协议作为核心通信机制，所有业务操作通过统一的 `/api/root/rpc/service` 端点完成。

### 关键信息

| 项目 | 值 |
|------|-----|
| 平台地址 | `http://172.20.193.21:32679` |
| 认证方式 | JSON-RPC登录获取token（Bearer + Cookie双通道） |
| 登录接口 | `POST /api/root/rpc/login` |
| 业务接口 | `POST /api/root/rpc/service` |
| 协议 | JSON-RPC 2.0 |

---

## 认证接口

### 登录获取Token

| 项目 | 值 |
|------|-----|
| **端点** | `POST /api/root/rpc/login` |
| **Content-Type** | `application/json` |
| **密码编码** | Base64（UTF-8） |

**请求体：**

```json
{
    "id": "login",
    "jsonrpc": "2.0",
    "method": "login",
    "params": {
        "login": "caohanyun",
        "password": "UXdlciEyMzQ="
    }
}
```

> ⚠️ `password` 字段必须先对明文密码做 Base64 编码。例如 `Qwer!234` → `UXdlciEyMzQ=`

**响应体（关键字段）：**

```json
{
    "result": {
        "data": {
            "login": "caohanyun",
            "name": "曹瀚云",
            "id": "044js2hehjjp7",
            "token": "cae26ebfc0a54a39...",
            "roles": [...],
            "pwd_expire_day": 90
        }
    },
    "id": "login",
    "jsonrpc": "2.0",
    "error": null
}
```

### Token使用方式

后续调用业务接口时，需**同时**携带以下两种认证：

| 位置 | 字段 | 值 |
|------|------|-----|
| HTTP Header | `Authorization` | `Bearer {token}` |
| HTTP Cookie | `sieIiotToken` | `{token}` |

> 两者缺一不可。仅传 Authorization 会返回 `{"error":{"code":7100,"message":"token不能为空"}}`。

### 自动获取Token

已在跳板机上部署 `C:\temp\get_iidp_token.ps1`，从服务器调用：

```bash
# 从服务器通过跳板机获取
TOKEN=$(/home/agentuser/get_iidp_token.sh)
```

---

## 通用业务接口

### 调用格式

| 项目 | 值 |
|------|-----|
| **端点** | `POST /api/root/rpc/service` |
| **Content-Type** | `application/json` |
| **URL参数** | `?model={ModelName}&service={app}.{ModelName}.{form}.{formType}:{tag}` |

**请求体模板：**

```json
{
    "id": "auto-generated-guid",
    "jsonrpc": "2.0",
    "method": "service",
    "params": {
        "args": {
            "valuesList": [
                {
                    "字段1": "值1",
                    "字段2": "值2"
                }
            ],
            "useDisplayForModel": true
        },
        "context": {
            "uid": "",
            "timeZone": "UTC+8",
            "lang": "zh-CN"
        },
        "model": "ModelName",
        "tag": "master",
        "service": "app.ModelName.form_name.form_type:master#action",
        "app": "dim-ind"
    }
}
```

### service字段命名规则

IIDP存在**两种调用模式**：

#### 模式A：长格式（表单操作）

```
service = {app}.{ModelName}.{page_name}.{component_type}:{tag}#{action}
```

- `#create` = 新增记录
- `#update` = 修改记录
- `#delete` = 删除记录
- 无后缀 = 查询/加载

args中使用 `valuesList: [{}]` 传入数据，适用于**新增/批量操作**。

#### 模式B：短格式（直接CRUD）

```
URL参数: ?model={ModelName}&service={action}
请求体: args.ids + args.values
```

- `service=update` = 按主键更新
- `service=create` = 新增
- `service=delete` = 删除

args中使用 `ids: ["记录ID"]` + `values: {字段: 值}` 传入数据，适用于**按主键精确操作单条记录**。

> ⚠️ 两种模式不可混用。模式A的service在URL中，模式B的service可在URL参数或请求体中。

### 其他必要Header

| Header | 值 |
|--------|-----|
| `Accept` | `application/json, text/plain, */*` |
| `Origin` | `http://172.20.193.21:32679` |
| `Referer` | `http://172.20.193.21:32679/iidp/dim-ind/dim_lm_ind_menu/lm_indicator_report_vo_menu?loginType=ignoreCas` |

---

## 已验证的业务接口

### 1. 绩效指标报表配置（lm_indicator_report）

| 项目 | 值 |
|------|-----|
| **Model** | `LmIndicatorReportVo` |
| **App** | `dim-ind` |
| **功能** | 绩效指标与报表的关联关系维护 |
| **对应数据库表** | `lm_indicator_report` |

#### 新增记录（#create）

**URL参数：**
```
?model=LmIndicatorReportVo&service=dim-ind.LmIndicatorReportVo.lm_indicator_report_vo_form.form:master
```

**valuesList字段：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `indicatorCode` | string | 指标代码 | `"FGLBL"` |
| `indicatorName` | string | 指标名称 | `"返工料比例"` |
| `alarmReport` | string | 报表类型（1=经营管理分析表, 2=生产体检表） | `"1"` |
| `reportCode` | string | 报表代码（来自lm_report_config.report_code） | `"index_report_rework_material_ratio_manage_checkup"` |
| `reportName` | string | 报表名称 | `"2.9返工料比例"` |
| `indicatorPath` | string | IIDP菜单路径 | `/dim-ind/dim_lm_ind_manage_checkup_menu/{report_code}_menu` |
| `lmIndicatorRecord` | string | 指标记录ID（lm_indicator_record.id） | `"05l3nhk0jd8sx"` |
| `lmReportConfig` | string | 报表配置ID（lm_report_config.id） | `"05cw0e6guujcf"` |

**indicatorPath拼接规则：**

```
/dim-ind/dim_lm_ind_manage_checkup_menu/{report_code}_menu
```

> 例：report_code = `index_report_product_total_manage_checkup`
> → indicatorPath = `/dim-ind/dim_lm_ind_manage_checkup_menu/index_report_product_total_manage_checkup_menu`

**service字段（创建）：**
```
dim-ind.LmIndicatorReportVo.lm_indicator_report_vo_form.form:master#create
```

#### 相关数据字典

| alarm_report值 | 含义 | 备注 |
|----------------|------|------|
| 1 | 经营管理分析表 | report_name以"2"开头的lm_report_config |
| 2 | 生产体检表 | report_name以"1"开头的lm_report_config |
| 3 | 报表3 | — |
| 4-5 | 仓储班长/仓储员 | — |
| 10-17 | 各生产岗位角色 | — |

> 字典来源：`SELECT * FROM base_dict_value WHERE dict_type = 'lm_ind_alarm_report'`

#### 关键数据表关系

```
lm_indicator_report (报表关联表)
  ├── indicator_record_id → lm_indicator_record.id (指标记录)
  ├── report_config_id    → lm_report_config.id (报表配置)
  └── alarm_report        → base_dict_value.dict_value (报表类型)
```

---

### 2. 绩效指标计算（LmIndicatorOperations）

| 项目 | 值 |
|------|-----|
| **Model** | `LmIndicatorOperations` |
| **App** | `dim-ind` |
| **功能** | 触发绩效指标计算，结果写入lm_st_summary_table等表 |

> 详见 [[项目知识备忘]] 中"IIDP绩效指标计算"章节和 `data-science/lm-indicator-calc` 技能。

#### 触发计算

**URL参数：**
```
?model=LmIndicatorOperations&service=dim-ind.LmIndicatorOperations.{method}
```

**请求体（valuesList）：**

```json
{
    "code": "lm_st_balances",
    "t": {
        "createDate": "2026-01-01",
        "endDate": "2026-06-30"
    }
}
```

**已知的code值：**

| code | 说明 | XXL-Job Task ID |
|------|------|-----------------|
| `lm_st_balances` | 科目余额表转换 | 479 |
| `lm_st_summary_table` | 绩效汇总表 | — |

> `createDate`/`endDate` 为日粒度，但结果表中的 `date` 字段为月粒度（`YYYY-MM-01`）。
> 已知bug：海外 `account_desc` 超过64字符会导致IIDP VARCHAR(64)报错，需SUBSTRING截断。

---

### 3. 接口请求参数配置（InterfaceEbsReqParamVO）

| 项目 | 值 |
|------|-----|
| **Model** | `InterfaceEbsReqParamVO` |
| **App** | `dim-common-interface` |
| **调用模式** | 模式B（短格式：`service=update`） |
| **功能** | 维护EBS接口的请求参数配置（如期间、组织代码、业务实体等） |
| **对应数据库表** | `interface_ebs_req_param` |

#### 更新记录

**URL参数：**
```
?model=InterfaceEbsReqParamVO&service=update
```

**请求体（按主键更新）：**

```json
{
    "id": "guid",
    "jsonrpc": "2.0",
    "method": "service",
    "params": {
        "args": {
            "ids": ["04ol9d15eyhg2"],
            "values": {
                "keyDesc": "期间",
                "keyName": "PERIOD_NAME",
                "keyValue": "202501",
                "operation": "EQ",
                "operationType": "C",
                "validflag": "1",
                "code": "DIM_BALANCES_GET",
                "id": "04ol9d15eyhg2"
            },
            "useDisplayForModel": true
        },
        "context": {
            "uid": "",
            "timeZone": "UTC+8",
            "lang": "zh-CN"
        },
        "model": "InterfaceEbsReqParamVO",
        "tag": "master",
        "service": "update",
        "app": "dim-common-interface"
    }
}
```

#### 参数字段映射（curl values → 数据库列）

| curl values（驼峰） | 表列名（下划线） | 类型 | 说明 | 示例 |
|---------------------|------------------|------|------|------|
| `id` | `id` | VARCHAR(64) | 主键（冗余传入） | `04ol9d15eyhg2` |
| `code` | `code` | VARCHAR(64) | 接口编码 | `DIM_BALANCES_GET` |
| `keyDesc` | `key_desc` | VARCHAR(64) | 参数中文描述 | `期间` |
| `keyName` | `key_name` | VARCHAR(64) | Oracle EBS字段名 | `PERIOD_NAME` |
| `keyValue` | `key_value` | VARCHAR(2000) | 参数值 | `202501` |
| `operation` | `operation` | VARCHAR(64) | 操作符（EQ/IN） | `EQ` |
| `operationType` | `operation_type` | VARCHAR(64) | 值类型（C=常量） | `C` |
| `validflag` | `validflag` | VARCHAR(16) | 有效标志（1有效/0删除） | `1` |

> ⚠️ `tenant_id`、`create_user`、`create_date`、`update_user`、`update_date` 不在values中传入，后端自动处理。

#### interface_ebs_req_param 表结构

| 列名 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(64) | 主键 |
| `code` | VARCHAR(64) | 接口编码（如DIM_BALANCES_GET） |
| `key_desc` | VARCHAR(64) | 参数描述（中文） |
| `key_name` | VARCHAR(64) | 参数键名（Oracle EBS字段名） |
| `key_value` | VARCHAR(2000) | 参数值（IN操作时多个值逗号分隔） |
| `operation` | VARCHAR(64) | 操作符：EQ=等于，IN=包含 |
| `operation_type` | VARCHAR(64) | 值类型：C=常量 |
| `validflag` | VARCHAR(16) | 逻辑删除（1有效/0删除） |
| `tenant_id` | VARCHAR(64) | 租户ID |
| `create_user` | VARCHAR(64) | 创建人 |
| `create_date` | TIMESTAMP | 创建时间 |
| `update_user` | VARCHAR(64) | 修改人 |
| `update_date` | TIMESTAMP | 修改时间 |

#### 当前有效配置一览（2026-06-24）

| 接口编码 (code) | 参数 (key_name) | 当前值 | 操作符 | 用途 |
|----------------|-----------------|--------|--------|------|
| `DIM_BALANCES_GET` | `PERIOD_NAME` | 202501 | EQ | 科目余额取数期间 |
| `DIM_BALANCE_GET_SPECIAL` | `PERIOD_CODE` | 202603 | EQ | 特殊余额取数期间 |
| `DIM_COST_GET` | `ORGANIZATION_CODE` | 1 | IN | 成本取数-库存组织 |
| `DIM_COST_GET_CDSW` | `ORGANIZATION_CODE` | 1 | IN | 成本取数(CDSW)-库存组织 |
| `DIM_CUSTOMER_GET_INCREMENT` | `OPERATING_UNIT` | *(57个OU)* | IN | 增量客户同步-业务实体 |
| `DIM_CUSTOMER_GET_INITIAL` | `OPERATING_UNIT` | 2041_OU_广东预混厂 | IN | 初始客户同步-业务实体 |
| `DIM_ITEM_GET_INCREMENT` | `ORGANIZATION_CODE` | *(75个组织)* | IN | 增量物料同步-库存组织 |
| `DIM_ITEM_GET_INCREMENT_NO` | `ORGANIZATION_CODE` | *(66个组织)* | IN | 增量物料同步(否)-库存组织 |

> IN操作符的`key_value`为逗号分隔的多值列表，存放在VARCHAR(2000)中。

---

## 调用工具与脚本

### 跳板机执行路径

所有IIDP API调用必须通过跳板机（`172.20.193.21`内网）执行，因为：
1. IIDP平台仅在内网可访问
2. 服务器通过反向SSH隧道连接跳板机（端口2223）

| 脚本 | 位置 | 用途 |
|------|------|------|
| `get_iidp_token.ps1` | 跳板机 `C:\temp\` | 获取IIDP Token |
| `iidp_api.ps1` | 跳板机 `C:\temp\` | 完整API工具（登录+调用封装） |
| `get_iidp_token.sh` | 服务器 `~/` | 从服务器通过跳板机获取Token |

### 调用流程

```
服务器 → sshpass → 跳板机(2223) → PowerShell → IIDP API(32679)
```

1. 服务器通过 `sshpass -p 'Y*7@jB3#8&' ssh -p 2223 win10@localhost` 连接跳板机
2. 在跳板机上执行PowerShell脚本调用IIDP API
3. PowerShell脚本需要UTF-8 BOM头（Windows PowerShell 5.1默认GBK编码）
4. 返回结果通过SSH stdout回传服务器

### Windows跳板机注意事项

- PowerShell脚本必须保存为 **UTF-8 with BOM** 编码，否则中文内容会乱码
- 跳板机SSH用户：`win10`，密码：`Y*7@jB3#8&`
- 跳板机主机名：`DESKTOP-S4SIDN6`

---

## 相关页面

- [[项目知识备忘]] — SSH隧道端口映射、DB连接信息、XXL-Job等
- [[通威农发-数据库总览]] — 数据库表结构总览
- [[CPT报表分析]] — 帆软CPT报表模板分析
- [[指标与报表结构]] — 绩效指标与报表的业务关系

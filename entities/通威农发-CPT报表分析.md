---
title: 通威农发CPT报表分析
created: 2026-05-14
updated: 2026-05-14
type: entity
tags: [通威农发, CPT, FineReport, 报表, 指标编码, 数据分析]
confidence: high
related: [[fine-report-cpt]], [[通威农发-数据库总览]], [[通威农发-报表预处理中间表]]
---

# 通威农发CPT报表分析

> 通威农发项目共30张FineReport CPT绩效报表的分析经验汇总。
> 报表路径：`/home/agentuser/finereport-files/通威农发/`

## 报表概况

通威农发绩效报表共 **30张CPT文件**（含3张绩效功能表），分4组管理：

| 组别 | 报表范围 | 主题 |
|------|----------|------|
| 组1 | 1.1总产销量、1.2产能利用率、1.16投入产出比、2.1产品大类、2.2产能利用率、2.8投入产出比、1.7十项核心原料损耗、2.6厂内大损耗 | 产量与产能 |
| 组2 | 1.3吨燃动费、1.3.1吨电耗吨汽耗、1.4吨非折旧费用、1.5吨人工费、1.6变动生产费用节约额、1.13单班产量达成率 | 费用与效率 |
| 组3 | 1.8质量投诉处理率、1.8.1质量投诉数量、1.9外观竞胜平、1.10返工料比例、1.10.1质量故障料总量、1.11合格率、2.7月度客诉、2.9返工料比例、2.9.1质量故障料总量、2.10外观竞胜平、2.11产品合格率 | 质量指标 |
| 组4 | 1.12安全事故、1.14关键岗位配置完成率、1.15总人均产量、2.11人均产量、2.11.1生产人数、2.12安全事故、2.13关键岗位配置完成率 | 安全与人力 |

## 核心数据源

所有绩效报表CPT的数据管道：

```
wms_ext_ng_stock_order (NG不合格品库存)
  → view_wms_ext_ng_stock_order (视图，⚠️有已知BUG)
    → CPT报表SQL

lm_st_summary_table (汇总表，target_code区分指标)
  → lm_indicator_standard_detail (指标标准定义)
    → lm_indicator_standard_detail_value (标准值数值)
```

## 指标编码体系 (target_code)

通过 `grep -roh` 从全部30张CPT提取的完整编码清单：

### 按前缀分类

| 前缀 | 指标域 | 编码数量 | 关键编码 |
|------|--------|----------|----------|
| `FGLBL_` | 返工料比例 | 15 | FGLBL_HGL, FGLBL_SL, FGLBL_ZCL, FGLBL_SCBHG, FGLBL_CPJYBHG, FGLBL_GCBHG, FGLBL_HJLSL, FGLBL_ZLGZL, FGLBL_THLBHG, FGLBL_GSYY, FGLBL_KHYY, FGLBL_KCBHG, FGLBL_KCJY, FGLBL_KNWF, FGLBL_KCCQ |
| `KS_` | 客诉质量 | 13 | KS_KHTSZL, KS_DHTSCLSL, KS_JGZLCLSL, KS_YZXGCLSL, KS_BZQBZCLSL, KS_BZZLCLSL, KS_DHTSSL, KS_JGZLSL, KS_YZXGSL, KS_BZQBZSL, KS_BZZLSL, KS_ZLTS, KS_TOTALCLV |
| `CNLYL_` | 产能利用率 | 2 | CNLYL_CN, CNLYL_NLJ |
| `DFZJFY_` | 吨非折旧费用 | 6 | DFZJFY_DCJSBHY_Y, DFZJFY_DCJSBHY_ND, DFZJFY_DCQDTX_Y, DFZJFY_DCQDTX_N, DFZJFY_DHJBHF_Y, DFZJFY_DHJBHF_N |
| `DDFZJFY_` | 当期非折旧费用 | 2 | DDFZJFY_N_YS, DDFZJFY_Y_YS |
| `DRGFY` | 吨人工费 | 1 | DRGFY-ZCL |
| `DBCL_` | 单班产量 | 2 | DBCL_DCL_Y, DBCL_DCL_N |
| `GJGW_` | 关键岗位 | 1 | GJGW_PBL |
| `BZSCXL_` | 标准生产效率 | 2 | BZSCXL_Y, BZSCXL_N |
| `CWZBKM` | 财务指标科目 | 3 | CWZBKM15, CWZBKM16, CWZBKM17 |
| `HXWLSHL` | 核心物料损耗 | 2 | HXWLSHL12, HXWLSHLN0011 |
| `DHSL/DHXSCL` | 单耗/吨消耗产量 | 9 | DHSL01-05, DHXSCL01-04 |

### FGLBL_ 返工料比例指标详解（5月14日提取）

从 `1返工料比例.cpt` 中提取的14个编码，覆盖三大维度：

**生产缺陷维度**：
- `FGLBL_SCBHG` — 生产不合格总量
- `FGLBL_CPJYBHG` — 成品检验不合格总量
- `FGLBL_GCBHG` — 过程不合格总量
- `FGLBL_HJLSL` — 回机料总量
- `FGLBL_ZLGZL` — 质量故障料总量

**客户退货维度**：
- `FGLBL_THLBHG` — 客户退货料不合格量
- `FGLBL_GSYY` — 公司原因退货总量
- `FGLBL_KHYY` — 客户原因退货总量

**库存问题维度**：
- `FGLBL_KCBHG` — 库存检验不合格总量
- `FGLBL_KCJY` — 库存检验不合格
- `FGLBL_KNWF` — 库房五防异常总量
- `FGLBL_KCCQ` — 库存超期总量

**核心计算**：
- `FGLBL_SL` = 返工料比例（最终指标）
- `FGLBL_ZCL` = 主产量（分母）

## 已知视图BUG

### view_wms_ext_ng_stock_order 企业关联错误

**问题**：视图用 `re.id = n.warehouse_id` 关联企业表，但 `warehouse_id` 是仓库ID，不是企业ID。

**正确路径**：`cargo_owner_code → res_inv_org.inv_org_code → res_inv_org.company_id → res_enterprise.id`

**修正SQL**：
```sql
LEFT JOIN res_inv_org    rio ON rio.inv_org_code = n.cargo_owner_code
LEFT JOIN res_enterprise re  ON re.id            = rio.company_id
```

详见 [[通威农发-数据库总览]] 中的视图BUG章节。

## CPT修改经验

### 常见修改模式

1. **数据源切换**：修改 `O/Attributes dsName` + `columnName`，注意检查 `<Result>` 公式兼容性
2. **SQL改写**：编辑 `<Query>` CDATA，注意保留 `${paramName}` 参数引用
3. **新增指标**：在 `lm_indicator_standard_detail` 添加 target_code，在CPT的SQL中引用

### 已踩坑点

- **Result公式与数据源格式不匹配**：切换dsName时，新数据源的列格式可能与旧的不同（如数字"5"vs字符串"5月"），需要重置Result公式为 `$$$`
- **LEFT JOIN退化为INNER JOIN**：右表条件放在WHERE而非ON中会丢失不匹配行
- **decimal精度丢失**：`CAST(... AS decimal(12,3))` 会截断小于0.0005的值
- **MySQL列名大小写不敏感**：多表JOIN时同名列冲突需用别名区分

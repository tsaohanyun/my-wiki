---
title: FineReport CPT 模板文件
created: 2026-04-30
updated: 2026-04-30
type: entity
tags: [framework, api, tool]
sources: [raw/articles/skill-fine-report-cpt.md]
---

# FineReport (帆软报表) CPT 模板文件

## 概述
CPT 是帆软 FineReport 的报表模板格式，本质是标准 XML 文件（UTF-8），定义数据源、参数、单元格布局、图表、样式和页面设置。

## XML 结构层级

```
WorkBook (root)
├── TableDataMap          — 数据源定义
│   └── TableData[]       — 单个数据集
├── ElementCaseMobileAttr — 移动端渲染设置
├── Report                — 主报表
│   ├── ReportPageAttr    — 页面/重复设置
│   ├── RowHeight         — 默认行高
│   ├── ColumnWidth       — 默认列宽
│   ├── FloatElementList  — 浮动元素（图表）
│   ├── CellElementList   — 单元格网格（C 元素）
│   └── ReportAttrSet     — 页眉页脚
├── ReportParameterAttr   — 参数面板配置
│   └── ParameterUI       — 参数表单控件
├── StyleList             — 命名样式定义
├── DesensitizationList   — 数据脱敏规则
├── DesignerVersion       — 设计器版本
├── PreviewType           — 预览模式
├── TemplateThemeAttrMark — 主题（如"经典浅灰"）
├── StrategyConfigsAttr   — 数据集缓存策略
├── ForkIdAttrMark        — 分支ID
├── TemplateCloudInfoAttrMark — 云元数据
└── TemplateIdAttMark     — 模板UUID
```

## 关键属性

### 数据集 TableData
| 属性 | 含义 |
|------|------|
| `name` | 数据集名称，单元格通过 `dsName` 引用 |
| `class` | `DBTableData`=SQL查询, `EmbeddedTableData`=内嵌数据, `NameTableData`=服务器数据集引用 |
| `maxMemRowCount` | 内存最大缓存行数，-1=无限 |
| `desensitizeOpen` | 启用数据脱敏 |

### 单元格元素 `<C>`
| 属性 | 含义 |
|------|------|
| `c` | 列索引（0起始） |
| `r` | 行索引（0起始） |
| `cs` | 列合并数 |
| `rs` | 行合并数 |
| `s` | 样式索引（指向 StyleList） |

### 单元格值类型 `<O>`
| 属性 | 含义 |
|------|------|
| 无 `t` 属性 | 纯文本/静态值 |
| `t=DSColumn` | 数据列绑定 |
| `t=CC` | 图表组件 |
| `t=XMLable` | 可序列化对象 |
| `class=com.fr.base.Formula` | 公式表达式 |

### 扩展方向
| 属性 | 含义 |
|------|------|
| `dir=0` | 纵向扩展（向下） |
| `dir=1` | 横向扩展（向右） |
| `left` | 左父格引用（如 "B10"） |
| `leftParentDefault=false` | 自定义左父格覆盖 |

## 单位系统
- **位置/尺寸**（Location, RowHeight, ColumnWidth）：EMU 单位。1英寸=914400 EMU，1cm=360000 EMU
- **字号**：1/4磅单位。值÷4=实际pt（72 → 18pt）
- **颜色**：有符号32位整数表示RGB。转换：`value & 0xFFFFFF`

## SQL 参数语法
- `${paramName}` — 直接参数替换
- `${IF(LEN(param)==0, "", "and col='" + param + "'")}` — 条件SQL片段

## 常见修改模式
- **改SQL查询**：编辑 TableData 中 `<Query>` CDATA 内容
- **加参数**：在 TableData/Parameters 下添加 `<Parameter>`，SQL 中用 `${newParam}`
- **改单元格绑定**：修改 `O/Attributes` 的 `dsName` 和 `columnName`
- **改样式**：更新 `C.s` 索引或修改 StyleList 条目
- **改图表**：修改 FloatElement → Chart 子树
- **加单元格**：添加 `<C>` 元素，含 c, r, s 属性和子元素

## 样式系统
| 属性 | 含义 |
|------|------|
| `FRFont.name` | 字体族（simhei=黑体, SimSun=宋体） |
| `FRFont.size` | 字号（1/4磅单位） |
| `FRFont.style` | 0=常规, 1=粗体 |
| `Background.name` | `NullBackground`=无, `ColorBackground`=纯色 |
| `Format.roundingMode=6` | 大概率 HALF_EVEN（银行家舍入） |

## 缓存策略 StrategyConfig
| 属性 | 含义 |
|------|------|
| `dsName` | 适用数据集 |
| `enabled` | 启用缓存 |
| `timeToLive` | 缓存TTL（毫秒，1500000=25分钟） |
| `timeToIdle` | 空闲超时（毫秒，86400000=24小时） |
| `updateInterval` | 刷新间隔（毫秒） |
| `updateSchema` | 定时刷新Cron表达式 |

## 注意事项
- CPT 文件可能很大（20K+行），读取时用 offset/limit
- `ColumnNames` 使用 `,,` 作为分隔符
- 单元格仅存储非空单元格，空单元格由网格隐含
- 字号单位不是磅，必须除以4
- 位置/尺寸值是 EMU，不是像素或厘米
- 部分属性含义为推断，关键编辑前需验证

## 相关链接
- [[html-prototype-generation]] — 原型生成可与报表系统配合
- [[frontend-design-system]] — 前端设计系统概述

---
author: Hermes Wiki Agent
created: '2026-06-26'
description: Wiki frontmatter标准规范，参考Azure DevOps YAML schema最佳实践，支持参数化、模板化、类型约束等高级特性
project: 通用
status: published
tags:
- frontmatter
- yaml
- standard
- azure-devops
title: Wiki Frontmatter 标准规范 (v2)
type: reference
updated: '2026-06-26'
version: 1.0.20260626
---


# Wiki Frontmatter 标准规范 (v2)

> 参考 Azure DevOps YAML Schema 最佳实践，支持参数化、模板化、类型约束等高级特性

## 一、设计原则

### 1.1 分层结构
```
frontmatter
├── 基础字段 (必填)
│   ├── title
│   ├── project
│   ├── created
│   ├── updated
│   └── type
├── 扩展字段 (推荐)
│   ├── description
│   ├── tags
│   ├── status
│   └── author
├── 关联字段 (可选)
│   ├── sources
│   ├── related
│   └── dependencies
└── 自定义字段 (扩展)
    └── x_*
```

### 1.2 类型系统
参考Azure DevOps的类型定义：

| 类型 | 说明 | 示例 |
|------|------|------|
| `string` | 字符串 | `'hello world'` |
| `number` | 数字 | `42`, `3.14` |
| `boolean` | 布尔值 | `true`, `false` |
| `array` | 数组 | `[1, 2, 3]` |
| `object` | 对象 | `{key: value}` |
| `enum` | 枚举 | `'concept'`, `'blueprint'` |

## 二、字段定义规范

### 2.1 基础字段 (必填)

```yaml
# 文档标题
# 类型: string
# 约束: 必填，不超过100字符
# 提取规则: 从第一个 # 标题提取
title: string

# 项目归属
# 类型: enum
# 可选值: '通威农发' | '通用' | '欧软' | string
# 提取规则: 根据路径自动提取
project: enum | string

# 创建日期
# 类型: string (ISO 8601格式)
# 约束: 必填，格式 YYYY-MM-DD
created: string

# 更新日期  
# 类型: string (ISO 8601格式)
# 约束: 必填，格式 YYYY-MM-DD
updated: string

# 文档类型
# 类型: enum
# 可选值: 见下方 type 枚举定义
type: enum
```

### 2.2 type 枚举定义

```yaml
# 概念文档 - 解释概念、原理、方法论
concept: 
  description: '概念性文档，解释理论和方法'
  examples: ['智能制造', '数字化转型']

# 蓝图方案 - 业务流程设计
blueprint:
  description: '业务蓝图，包含流程设计和规范'
  examples: ['计划生产配方', '质量管理']

# 架构文档 - 技术架构设计
architecture:
  description: '技术架构，包含系统设计和接口'
  examples: ['数据库设计', 'API文档']

# 设计文档 - 详细设计说明
design:
  description: '详细设计，包含功能规格和实现'
  examples: ['功能设计', '接口设计']

# 参考文档 - 参考资料和手册
reference:
  description: '参考资料，包含手册和指南'
  examples: ['操作手册', 'API参考']

# 实体文档 - 具体实体描述
entity:
  description: '实体文档，描述具体业务对象'
  examples: ['数据字典', '业务术语']

# 培训文档 - 培训材料
training:
  description: '培训材料，包含教程和课程'
  examples: ['培训课件', '操作指南']

# 术语表 - 术语和定义
glossary:
  description: '术语表，包含术语定义和解释'
  examples: ['制造业术语', '业务术语']

# 案例文档 - 实际案例和经验
case:
  description: '案例文档，包含实际案例和经验'
  examples: ['踩坑经验', '最佳实践']
```

### 2.3 扩展字段 (推荐)

```yaml
# 文档描述
# 类型: string
# 约束: 推荐，不超过200字符
# 提取规则: 从内容中自动提取摘要
description: string

# 标签列表
# 类型: array[string]
# 约束: 推荐，最多5个标签
# 提取规则: 从内容和路径中自动提取
tags: array[string]

# 文档状态
# 类型: enum
# 可选值: 'draft' | 'review' | 'published' | 'archived'
# 默认值: 'published'
status: enum

# 文档作者
# 类型: string
# 默认值: 'Hermes Wiki Agent'
author: string

# 版本号
# 类型: string (语义化版本)
# 示例: '1.0.0', '2.1.3'
version: string
```

### 2.4 关联字段 (可选)

```yaml
# 来源文件
# 类型: array[string]
# 说明: 文档内容的来源文件路径
sources: array[string]

# 相关文档
# 类型: array[string]
# 说明: 相关的wiki页面链接
related: array[string]

# 依赖文档
# 类型: array[string]
# 说明: 依赖的其他文档
dependencies: array[string]

# 前置文档
# 类型: array[string]
# 说明: 阅读本文档前建议先阅读的文档
prerequisites: array[string]
```

### 2.5 自定义字段 (扩展)

```yaml
# 自定义字段必须以 x_ 前缀开头
# 类型: any
# 说明: 用于扩展自定义元数据
x_custom_field: any

# 示例
x_business_domain: '生产管理'
x_data_source: 'IIDP平台'
x_api_version: 'v2'
```

## 三、参数化模板

### 3.1 模板定义

参考Azure DevOps的`parameters`，支持frontmatter模板：

```yaml
# 模板引用
# 类型: string
# 说明: 引用预定义的frontmatter模板
template: string

# 模板参数
# 类型: object
# 说明: 传递给模板的参数
parameters: object
```

### 3.2 预定义模板

```yaml
# 概念文档模板
templates:
  concept:
    type: concept
    status: published
    tags: [concept]
    
  # 蓝图文档模板
  blueprint:
    type: blueprint
    status: published
    tags: [blueprint, workflow]
    
  # 架构文档模板
  architecture:
    type: architecture
    status: published
    tags: [architecture, technical]
    
  # 培训文档模板
  training:
    type: training
    status: published
    tags: [training, education]
```

### 3.3 模板使用示例

```yaml
# 使用概念文档模板
template: concept
parameters:
  domain: '制造业'
  level: '高级'
  
# 渲染结果
title: [从内容提取]
project: [自动提取]
type: concept
status: published
tags: [concept, 制造业]
x_domain: 制造业
x_level: 高级
```

## 四、验证规则

### 4.1 必填字段验证

```yaml
validation:
  required:
    - title
    - project
    - created
    - updated
    - type
```

### 4.2 类型验证

```yaml
validation:
  types:
    title: string
    project: string
    created: string  # ISO 8601格式
    updated: string  # ISO 8601格式
    type: string     # 枚举值
    description: string
    tags: array
    status: string   # 枚举值
    author: string
    version: string  # 语义化版本
```

### 4.3 格式验证

```yaml
validation:
  formats:
    created: '^\d{4}-\d{2}-\d{2}$'
    updated: '^\d{4}-\d{2}-\d{2}$'
    version: '^\d+\.\d+\.\d+$'
```

### 4.4 约束验证

```yaml
validation:
  constraints:
    title:
      maxLength: 100
    description:
      maxLength: 200
    tags:
      maxItems: 5
      uniqueItems: true
```

## 五、自动提取规则

### 5.1 字段提取优先级

```yaml
extraction:
  title:
    priority:
      - '从第一个 # 标题提取'
      - '从 ## 标题提取'
      - '使用文件名'
      
  project:
    rules:
      - path: '*/通威农发/*'
        value: '通威农发'
      - path: '*/欧软/*'
        value: '欧软'
      - default: '通用'
      
  type:
    rules:
      - path: '*/concepts/*'
        value: 'concept'
      - path: '*/业务蓝图/*'
        value: 'blueprint'
      - path: '*/技术架构/*'
        value: 'architecture'
      - path: '*/详细设计/*'
        value: 'design'
      - path: '*/培训/*'
        value: 'training'
      - default: 'reference'
```

### 5.2 标签提取规则

```yaml
extraction:
  tags:
    # 内容关键词提取
    keywords:
      - pattern: 'MES|WMS|APS|ERP'
        tag: 'enterprise-system'
      - pattern: 'SQL|数据库|查询'
        tag: 'database'
      - pattern: '接口|API|集成'
        tag: 'integration'
      - pattern: '流程|工作流|审批'
        tag: 'workflow'
      - pattern: '设备|机械|产线'
        tag: 'equipment'
      - pattern: '质量|检验|标准'
        tag: 'quality'
      - pattern: '仓储|库存|物流'
        tag: 'warehouse'
    
    # 路径标签提取
    path_tags:
      - path: '*/concepts/*'
        tag: 'concept'
      - path: '*/通威农发/*'
        tag: 'tw-nongfa'
      - path: '*/欧软/*'
        tag: 'ouft'
    
    # 限制
    constraints:
      maxTags: 5
      unique: true
```

## 六、样例文档

### 6.1 概念文档样例

```yaml
---
title: 智能制造
project: 通用
created: '2026-04-30'
updated: '2026-06-26'
type: concept
status: published
description: '智能制造是以数据、算力、算法三大要素驱动的制造业范式变革'
tags:
- smart-manufacturing
- digital-transformation
- industry-4
author: Hermes Wiki Agent
version: '1.0.0'
sources:
- raw/articles/smart-manufacturing-overview.md
related:
- '[[数字化转型]]'
- '[[concepts/smart-manufacturing|工业4.0]]'
x_domain: 制造业
x_level: 高级
---
```

### 6.2 蓝图文档样例

```yaml
---
title: 蓝图方案：计划生产配方
project: 通威农发
created: '2026-06-17'
updated: '2026-06-26'
type: blueprint
status: published
description: '计划管理+生产管理+配方管理+施耐德工厂MES蓝图'
tags:
- blueprint
- workflow
- tw-nongfa
- production
- formula
author: Hermes Wiki Agent
version: '2.1.0'
sources:
- '通威农发/业务调研/计划生产配方调研.md'
related:
- '[[通威农发/业务蓝图/蓝图方案-质量管理]]'
- '[[通威农发/业务蓝图/蓝图方案-设备管理]]'
dependencies:
- '[[通威农发/项目知识备忘]]'
x_flow_numbers: 'PL001-PL006, PD001-PD009'
x_business_domain: '计划生产'
---
```

### 6.3 架构文档样例

```yaml
---
title: IIDP平台API接口文档
project: 通威农发
created: '2026-06-24'
updated: '2026-06-26'
type: architecture
status: published
description: 'IIDP平台REST/JSON-RPC接口文档，包含认证方式和业务接口'
tags:
- architecture
- api
- tw-nongfa
- integration
- iidp
author: Hermes Wiki Agent
version: '1.2.0'
sources:
- '通威农发/技术架构/IIDP平台分析.md'
related:
- '[[通威农发/技术架构/通威农发-数据库总览]]'
x_api_version: 'v2'
x_protocol: 'JSON-RPC 2.0'
x_base_url: 'http://172.20.193.21:32679'
---
```

### 6.4 培训文档样例

```yaml
---
title: 功能设计快速上手培训
project: 通威农发
created: '2026-06-10'
updated: '2026-06-26'
type: training
status: published
description: '功能设计快速上手方法论，从业务需求到数据表+页面布局的5步流程'
tags:
- training
- methodology
- tw-nongfa
- functional-design
author: Hermes Wiki Agent
version: '1.0.0'
related:
- '[[通威农发/详细设计/详细设计-功能设计]]'
x_duration: '2小时'
x_level: '初级'
x_audience: '产品经理、实施顾问'
---
```

### 6.5 术语表样例

```yaml
---
title: 制造业术语库
project: 通用
created: '2026-06-26'
updated: '2026-06-26'
type: glossary
status: published
description: '制造业领域60+术语定义，包含MES/ERP/WMS/APS等系统术语'
tags:
- glossary
- terminology
- manufacturing
- mes
- erp
author: Hermes Wiki Agent
version: '1.0.0'
sources:
- '通威农发/项目知识备忘.md'
- '通威农发/行业知识/饲料行业知识.md'
x_term_count: 60
x_domains: '生产管理、质量管理、设备管理、仓储管理'
---
```

## 七、迁移指南

### 7.1 从v1迁移到v2

```yaml
# v1 格式
---
title: 文档标题
project: 通威农发
created: '2026-06-26'
updated: '2026-06-26'
type: blueprint
description: '文档描述'
tags:
- tag1
- tag2
---

# v2 格式 (向后兼容，新增字段)
---
title: 文档标题
project: 通威农发
created: '2026-06-26'
updated: '2026-06-26'
type: blueprint
status: published  # 新增
description: '文档描述'
tags:
- tag1
- tag2
author: Hermes Wiki Agent  # 新增
version: '1.0.0'  # 新增
x_custom: value  # 新增自定义字段
---
```

### 7.2 兼容性说明

- ✅ **向后兼容**: v1格式仍然有效
- ✅ **渐进式迁移**: 可以逐步添加新字段
- ✅ **自动补全**: 缺少的字段使用默认值
- ✅ **类型检查**: 严格的类型验证

## 八、最佳实践

### 8.1 字段命名规范

```yaml
# 使用小写字母和下划线
good_field_name: value

# 避免大写字母和连字符
BadFieldName: value  # 不推荐
bad-field-name: value  # 不推荐
```

### 8.2 数组格式

```yaml
# 推荐格式
tags:
- tag1
- tag2
- tag3

# 也支持内联格式
tags: [tag1, tag2, tag3]
```

### 8.3 字符串引用

```yaml
# 包含特殊字符时必须引用
description: '包含: 冒号的描述'
title: "包含'单引号'的标题"

# 简单字符串可以不引用
project: 通用
type: concept
```

### 8.4 日期格式

```yaml
# ISO 8601 格式
created: '2026-06-26'
updated: '2026-06-26T10:30:00'

# 支持时间戳
created: 2026-06-26
```

## 九、工具支持

### 9.1 验证脚本

```bash
# 验证单个文件
python3 scripts/validate_frontmatter.py --file wiki/page.md

# 验证所有文件
python3 scripts/validate_frontmatter.py

# 验证并自动修复
python3 scripts/scan_frontmatter.py --fix
```

### 9.2 模板生成

```bash
# 生成概念文档模板
python3 scripts/generate_frontmatter.py --template concept

# 生成蓝图文档模板
python3 scripts/generate_frontmatter.py --template blueprint

# 生成自定义模板
python3 scripts/generate_frontmatter.py --template custom --params '{"domain": "制造业"}'
```

### 9.3 IDE支持

- **VS Code**: 安装YAML扩展，支持frontmatter语法高亮
- **IntelliJ**: 内置YAML支持，自动补全和验证
- **Vim**: 使用vim-yaml插件

## 十、版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v2.0 | 2026-06-26 | 参考Azure DevOps YAML schema，增加参数化、模板化、类型约束 |
| v1.0 | 2026-06-26 | 初始版本，定义基础字段和验证规则 |

---

**参考文档**:
- [Azure DevOps YAML Schema Reference](https://learn.microsoft.com/zh-cn/azure/devops/pipelines/yaml-schema/)
- [YAML Specification](https://yaml.org/spec/)
- [Obsidian Frontmatter](https://help.obsidian.md/Advanced+topics/YAML+front+matter)

---
title: Wiki Frontmatter 标准模板
project: 通用
created: '2026-06-26'
updated: '2026-06-26'
type: reference
description: 'Wiki frontmatter标准模板，定义必填字段、可选字段、自动提取规则和验证规则'
tags:
- warehouse
- wms
- aps
- template
- equipment
---

# Wiki Frontmatter 标准模板
# 所有wiki页面必须包含以下frontmatter字段
# 生成器必须在创建文件时自动填充这些字段

# 必填字段
required_fields:
  - title: "文档标题（从内容中提取或手动指定）"
  - "project: '通威农发' | '通用' | '欧软' | 其他项目名"
  - "created: 'YYYY-MM-DD'（文件创建日期）"
  - "updated: 'YYYY-MM-DD'（最后修改日期）"
  - "type: 'concept' | 'blueprint' | 'architecture' | 'design' | 'reference' | 'entity' | 'training'"

# 可选但推荐字段
optional_fields:
  - description: "简短描述（100-200字），从内容中自动提取"
  - tags: "标签列表，最多5个，从内容中自动提取"
  - sources: "来源文件列表（如果从其他文档提取）"
  - status: "'draft' | 'review' | 'published'（默认published）"
  - author: "作者（默认Hermes Wiki Agent）"

# 自动提取规则
auto_extraction:
  title:
    - "从第一个 # 标题提取"
    - "如果没有，从 ## 标题提取"
    - "最后才使用文件名"
  
  project:
    - "路径包含'通威农发' → '通威农发'"
    - "路径包含'欧软' → '欧软'"
    - "其他 → '通用'"
  
  type:
    - "路径包含'concepts/' → 'concept'"
    - "路径包含'业务蓝图' → 'blueprint'"
    - "路径包含'技术架构' → 'architecture'"
    - "路径包含'详细设计' → 'design'"
    - "路径包含'培训' → 'training'"
    - "其他 → 'reference'"
  
  tags:
    - "从内容中提取关键词（MES/WMS/APS/SQL/设备/质量/仓储等）"
    - "从路径中提取（concepts/ → concept, 通威农发 → tw-nongfa）"
    - "最多5个标签，去重"

# 模板示例
template: |
  ---
  title: [自动提取或手动指定]
  project: [自动提取]
  created: '[YYYY-MM-DD]'
  updated: '[YYYY-MM-DD]'
  type: [自动提取]
  description: '[自动提取摘要]'
  tags:
  - [自动提取标签1]
  - [自动提取标签2]
  - [自动提取标签3]
  ---

# 验证规则
validation:
  required: "title, project, created, updated, type 必须存在"
  date_format: "created和updated必须是YYYY-MM-DD格式"
  type_values: "type必须是预定义值之一"
  tag_limit: "tags最多5个"
  description_length: "description不超过200字符"

project: hermes
---
title: Wiki管理最佳实践
aliases: [Wiki维护, Obsidian管理, 知识库管理]
tags: [wiki, obsidian, 知识管理]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: session-history
difficulty: intermediate
---
# Wiki 管理最佳实践

## YAML Frontmatter 规范

### 必需字段

```yaml
---
title: Wiki管理最佳实践
aliases: [别名1, 别名2]
tags: [标签1, 标签2]
type: concept|guide|reference|blueprint
status: published|draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: 来源
difficulty: beginner|intermediate|advanced
---
```

### aliases 批量添加

使用Python脚本批量添加aliases：

```python
import os
import yaml
import re

# 定义别名映射
ALIAS_MAP = {
    "页面名称": ["别名1", "别名2", "English Alias"],
}

def inject_aliases(fpath, aliases):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'title: Wiki管理最佳实践
aliases:' in content:
        return False  # 已有aliases
    
    # 在frontmatter末尾插入
    alias_block = "title: Wiki管理最佳实践
aliases:
" + "
".join(f'  - "{a}"' for a in aliases)
    new_content = content.replace('---
', f'{alias_block}
---
', 1)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True
```

## 标签一致性

### 标签层级规范

- L1：核心标签（如`data-governance`）
- L2：模块标签（如`metadata`）
- L3：功能标签（如`data-catalog`）
- L4：概念标签（如`data-lineage`）

### 检查脚本

```python
from collections import Counter

# 统计标签使用频率
all_tags = Counter()
for f in wiki_dir.rglob("*.md"):
    # 提取tags字段
    ...
    
# 检查相似标签
for tag1, tag2 in similar_tags:
    print(f"'{tag1}' vs '{tag2}'")
```

## 大文件拆分

当文件超过100KB时，应拆分为子文件：

1. 创建子目录
2. 按章节拆分
3. 创建索引文件
4. 更新相关链接

## 相关页面

- [[Hermes-Agent架构总览]]
- [[Wiki验证脚本]]
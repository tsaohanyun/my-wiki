project: hermes
---
title: Hermes Skills开发指南
aliases: [Skill开发, 技能创建, SKILL.md]
tags: [skills, 开发, 扩展]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: hermes-agent-skill-authoring
difficulty: advanced
---
# Hermes Skills 开发指南

## Skill 结构

```
~/.hermes/skills/
├── category/
│   └── skill-name/
│       ├── SKILL.md          # 主文件（必需）
│       ├── references/       # 参考文档
│       ├── templates/        # 模板文件
│       └── scripts/          # 脚本文件
```

## SKILL.md 格式

```yaml
---
name: skill-name
description: 技能描述
category: category-name
triggers:
  - 触发条件1
  - 触发条件2
---

# 技能标题

## 使用场景
...

## 执行步骤
1. 步骤1
2. 步骤2

## 注意事项
...
```

## 创建Skill

```bash
# 使用skill-creator技能
hermes skill create --name my-skill --category my-category

# 或手动创建
mkdir -p ~/.hermes/skills/my-category/my-skill
cat > ~/.hermes/skills/my-category/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: 我的自定义技能
---
# My Skill
...
EOF
```

## 最佳实践

1. **触发条件明确**：定义清晰的触发场景
2. **步骤详细**：包含具体命令和示例
3. **陷阱记录**：记录常见错误和解决方法
4. **验证步骤**：包含验证成功的方法

## 相关页面

- [[Hermes-Agent架构总览]]
- [[Hermes-常见问题排查]]
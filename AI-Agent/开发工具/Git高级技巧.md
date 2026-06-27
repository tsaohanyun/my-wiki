---
title: Git高级技巧
aliases:
  - git
  - Git技巧
  - Git Tips
tags:
  - 开发工具
  - Git
  - 版本控制
  - 效率
type: wiki
status: active
created: 2026-06-27
updated: 2026-06-27
source: 内部整理
difficulty: advanced
project: AI-Agent
---

# Git高级技巧

## 1. 分支策略

### Git Flow
```
main ─────────────────────────────  (生产)
  │
  ├── develop ────────────────────  (开发主线)
  │     ├── feature/login ───────  (功能分支)
  │     ├── feature/dashboard ───
  │     └── release/v1.2 ────────  (发布分支)
  │           └── hotfix/crash ──  (热修复)
  └──
```

```bash
# 开始新功能
git checkout develop
git checkout -b feature/login

# 完成功能
git checkout develop
git merge --no-ff feature/login
git branch -d feature/login

# 发布
git checkout -b release/v1.2 develop
# 测试通过后合并
git checkout main
git merge --no-ff release/v1.2
git tag -a v1.2 -m "Release v1.2"
```

### Trunk-Based Development（推荐）
```bash
# 短生命周期分支，频繁合并到main
git checkout -b feat/short-lived
# 小步提交，当天合并
git push origin feat/short-lived
# PR → Code Review → Squash Merge → main
```

### 分支命名规范
```
feat/add-login          # 新功能
fix/memory-leak         # Bug修复
hotfix/crash-on-start   # 紧急修复
refactor/api-layer      # 重构
docs/readme-update      # 文档
chore/ci-update         # 工程化
```

---

## 2. Rebase 详解

### 交互式 Rebase
```bash
# 修改最近5个提交
git rebase -i HEAD~5

# 编辑器中的操作：
pick abc1234 第一次提交
squash def5678 第二次提交    # 合并到上一个
reword ghi9012 第三次提交   # 修改提交信息
drop jkl3456 无用提交       # 删除
edit mno7890 需要修改的提交  # 暂停以修改
fixup pqr1234 丢弃消息合并   # 合并但丢弃消息
```

### Rebase vs Merge
```bash
# merge: 保留分支历史，创建合并提交
git merge feature/login

# rebase: 线性历史，更干净
git rebase main
git checkout main
git merge feature/login  # fast-forward
```

### 黄金规则
> **永远不要 rebase 已经推送到远程的公共分支**

### 自动 Stash Rebase
```bash
git pull --rebase origin main
# 等价于
git fetch origin
git rebase origin/main
```

---

## 3. Cherry-Pick

### 基本用法
```bash
# 将特定提交应用到当前分支
git cherry-pick abc1234

# cherry-pick多个提交
git cherry-pick abc1234 def5678

# cherry-pick一个范围
git cherry-pick abc1234..ghi9012

# 只应用变更，不自动提交
git cherry-pick --no-commit abc1234
```

### 冲突处理
```bash
git cherry-pick abc1234
# 如果有冲突：
# 1. 解决冲突
git add .
git cherry-pick --continue

# 或者放弃
git cherry-pick --abort
```

### 实际场景
```bash
# 从develop分支挑选热修复到main
git checkout main
git cherry-pick <hotfix-commit>

# 从feature分支挑选部分功能到release
git checkout release/v1.2
git cherry-pick abc1234 def5678
```

---

## 4. Git Bisect（二分查找Bug）

### 基本流程
```bash
# 开始二分查找
git bisect start

# 标记当前版本有问题
git bisect bad

# 标记已知正常的版本
git bisect good v1.0

# Git自动checkout中间版本，测试后标记
git bisect good   # 或 git bisect bad

# 找到引入bug的提交后
git bisect reset
```

### 自动化 Bisect
```bash
# 用脚本自动测试（0=good, 非0=bad）
git bisect start v2.0 v1.0
git bisect run npm test

# 或用自定义脚本
git bisect run ./test-script.sh
```

### 实用技巧
```bash
# 跳过无法测试的版本
git bisect skip

# 查看当前bisect状态
git bisect log

# 重放之前的bisect日志
git bisect replay bisect.log
```

---

## 5. Git Worktree（多工作目录）

### 使用场景
- 同时在多个分支上工作
- 修复hotfix时不想中断当前开发
- 对比不同分支的代码

### 基本操作
```bash
# 创建新的工作树
git worktree add ../hotfix-branch hotfix/crash
git worktree add ../feature-v2 feature/v2

# 列出所有工作树
git worktree list

# 输出：
# /home/user/project              abc1234 [main]
# /home/user/hotfix-branch        def5678 [hotfix/crash]
# /home/user/feature-v2           ghi9012 [feature/v2]

# 删除工作树
git worktree remove ../hotfix-branch

# 清理无效的工作树引用
git worktree prune
```

### 最佳实践
```bash
# 将worktree放在项目同级目录
cd ~/projects/myapp
git worktree add ../myapp-hotfix hotfix/urgent-fix

# 在worktree中独立工作
cd ../myapp-hotfix
# 修复、测试、提交
git commit -am "fix: urgent crash"
git push

# 回到主目录
cd ../myapp
git worktree remove ../myapp-hotfix
```

---

## 6. 其他高级技巧

### Stash 管理
```bash
git stash push -m "WIP: login feature"
git stash list
git stash show -p stash@{0}  # 查看diff
git stash pop stash@{0}
git stash branch new-branch stash@{0}  # 从stash创建分支
```

### Reflog（后悔药）
```bash
# 查看所有HEAD移动记录
git reflog

# 恢复误删的分支
git checkout -b recovered-branch HEAD@{3}

# 恢复误reset的提交
git reset --hard HEAD@{5}
```

### 配置优化
```bash
# .gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    lg = log --oneline --graph --decorate --all
    undo = reset --soft HEAD~1
    amend = commit --amend --no-edit
    wip = stash push -m "WIP"

[core]
    autocrlf = input
    pager = delta

[merge]
    conflictstyle = diff3

[diff]
    algorithm = histogram
```

---

## 最佳实践

1. **小步提交** — 每个提交完成一个逻辑变更
2. **写好提交信息** — 遵循 Conventional Commits 规范
3. **善用 `git add -p`** — 暂存模式，精确选择要提交的代码块
4. **定期清理** — 删除已合并的远程分支 `git branch -d`
5. **用 `.gitignore`** — 避免提交构建产物和敏感信息
6. **保护主分支** — 使用 branch protection rules + PR review

---

## 相关页面

- [[VSCode高效使用指南]]
- [[命令行效率工具]]
- [[API开发工具]]

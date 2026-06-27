---
title: Git版本控制指南
aliases: [Git教程, 版本控制, Git命令]
tags: [git, 版本控制, 开发工具]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: beginner
project: 开发工具
---
# Git 版本控制指南

## 概述

本指南提供Git版本控制的常用命令和最佳实践。

## 1. 基础命令

### 仓库初始化

```bash
# 初始化本地仓库
git init

# 克隆远程仓库
git clone https://github.com/user/repo.git
```

### 文件操作

```bash
# 添加文件到暂存区
git add filename
git add .  # 添加所有文件

# 提交文件
git commit -m "提交信息"

# 查看状态
git status

# 查看差异
git diff
git diff --staged
```

### 分支操作

```bash
# 查看分支
git branch

# 创建分支
git branch feature-name

# 切换分支
git checkout feature-name

# 创建并切换分支
git checkout -b feature-name

# 删除分支
git branch -d feature-name
```

## 2. 远程操作

### 远程仓库

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 推送到远程
git push origin main

# 拉取远程更新
git pull origin main
```

### 分支推送

```bash
# 推送本地分支到远程
git push -u origin feature-name

# 删除远程分支
git push origin --delete feature-name
```

## 3. 高级操作

### 暂存操作

```bash
# 暂存当前修改
git stash

# 查看暂存列表
git stash list

# 恢复暂存
git stash pop

# 删除暂存
git stash drop
```

### 合并操作

```bash
# 合并分支
git checkout main
git merge feature-name

# 解决冲突后提交
git add .
git commit -m "解决冲突"
```

### 变基操作

```bash
# 变基到main分支
git checkout feature-name
git rebase main

# 解决冲突后继续变基
git add .
git rebase --continue
```

## 4. 版本回退

### 回退操作

```bash
# 回退到指定提交
git reset --hard commit-hash

# 回退到上一个版本
git reset --hard HEAD~1

# 回退但保留修改
git reset --soft HEAD~1
```

### 撤销操作

```bash
# 撤销工作区修改
git checkout -- filename

# 撤销暂存区修改
git reset HEAD filename
```

## 5. 标签管理

### 标签操作

```bash
# 查看标签
git tag

# 创建标签
git tag v1.0.0

# 创建带注释的标签
git tag -a v1.0.0 -m "版本1.0.0"

# 推送标签到远程
git push origin v1.0.0

# 删除标签
git tag -d v1.0.0
```

## 6. 日志查看

### 提交日志

```bash
# 查看提交日志
git log

# 简洁模式
git log --oneline

# 图形模式
git log --graph --oneline --all

# 查看指定文件的日志
git log filename
```

## 7. 配置设置

### 用户配置

```bash
# 设置用户名
git config --global user.name "Your Name"

# 设置邮箱
git config --global user.email "your@email.com"

# 查看配置
git config --list
```

### 别名设置

```bash
# 设置别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
```

## 8. 最佳实践

### 提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

### 分支策略

```
main        # 主分支，稳定版本
develop     # 开发分支
feature/*   # 功能分支
release/*   # 发布分支
hotfix/*    # 热修复分支
```

## 相关页面

- [[SSH隧道与远程管理]]
- [[Hermes-Skills开发指南]]
- [[Wiki管理最佳实践]]

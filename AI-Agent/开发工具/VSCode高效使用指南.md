---
title: VSCode高效使用指南
aliases:
  - vscode
  - VSCode指南
  - VS Code Tips
tags:
  - 开发工具
  - IDE
  - VSCode
  - 效率
type: wiki
status: active
created: 2026-06-27
updated: 2026-06-27
source: 内部整理
difficulty: intermediate
project: AI-Agent
---

# VSCode高效使用指南

## 1. 必知快捷键

### 通用操作
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+P` | 打开命令面板 |
| `Ctrl+P` | 快速打开文件 |
| `Ctrl+Shift+N` | 新窗口 |
| `Ctrl+,` | 打开设置 |
| `Ctrl+K Ctrl+S` | 自定义快捷键 |

### 编辑
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+D` | 选中下一个相同词 |
| `Alt+↑/↓` | 上/下移动行 |
| `Shift+Alt+↑/↓` | 上/下复制行 |
| `Ctrl+Shift+K` | 删除整行 |
| `Ctrl+/` | 切换行注释 |
| `Ctrl+Shift+/` | 切换块注释 |
| `Ctrl+Enter` | 在下方插入空行 |
| `Ctrl+L` | 选中当前行 |
| `Alt+Click` | 多光标 |

### 导航
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+G` | 跳转到行 |
| `Ctrl+Shift+O` | 跳转到符号 |
| `F12` | 转到定义 |
| `Shift+F12` | 查找引用 |
| `Ctrl+T` | 工作区符号搜索 |
| `Ctrl+Tab` | 切换编辑器 |

---

## 2. 必装插件推荐

### 通用
- **GitLens** — 行内显示git blame、文件历史
- **Error Lens** — 在行内显示错误/警告
- **Todo Tree** — 高亮TODO/FIXME注释
- **Bookmarks** — 代码书签标记
- **Project Manager** — 多项目快速切换

### 前端开发
- **ESLint** — 代码检查
- **Prettier** — 格式化
- **Auto Rename Tag** — HTML标签自动重命名
- **Tailwind CSS IntelliSense** — Tailwind类名提示
- **ES7+ Snippets** — React/Vue代码片段

### Python
- **Python (ms-python)** — 语言支持
- **Pylance** — 类型检查和智能提示
- **Jupyter** — Notebook支持

### 远程/容器
- **Remote - SSH** — SSH远程开发
- **Remote - Containers** — 容器内开发
- **Remote - WSL** — WSL开发

### 主题和外观
- **One Dark Pro** — 经典暗色主题
- **Material Icon Theme** — 文件图标
- **Bracket Pair Colorizer** — 括号配对着色（内置v1.67+）

---

## 3. 调试技巧

### launch.json 配置示例

**Node.js 调试：**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "调试当前文件",
      "program": "${file}",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "type": "node",
      "request": "attach",
      "name": "附加到进程",
      "port": 9229
    }
  ]
}
```

**Python 调试：**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: 当前文件",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

### 调试快捷键
| 快捷键 | 功能 |
|--------|------|
| `F5` | 开始/继续调试 |
| `F9` | 切换断点 |
| `F10` | 单步跳过 |
| `F11` | 单步进入 |
| `Shift+F11` | 单步跳出 |

### 条件断点
- 右键断点 → 编辑断点 → 输入表达式（如 `i === 50`）
- 日志断点：不暂停程序，只输出日志到调试控制台

---

## 4. 远程开发

### SSH远程开发
1. 安装 `Remote - SSH` 插件
2. `Ctrl+Shift+P` → `Remote-SSH: Connect to Host`
3. 输入 `user@host` 或在 `~/.ssh/config` 中配置：

```
Host dev-server
    HostName 192.168.1.100
    User developer
    IdentityFile ~/.ssh/id_rsa
```

### Docker容器开发
1. 安装 `Remote - Containers` 插件
2. 项目根目录创建 `.devcontainer/devcontainer.json`：

```json
{
  "name": "Node.js Dev",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:20",
  "extensions": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ],
  "forwardPorts": [3000],
  "postCreateCommand": "npm install"
}
```

### Codespace 云端开发
- 直接在GitHub仓库页面 → Code → Codespaces → Create
- VSCode自动连接到云端环境

---

## 5. settings.json 实用配置

```json
{
  "editor.formatOnSave": true,
  "editor.minimap.enabled": false,
  "editor.fontSize": 14,
  "editor.fontFamily": "JetBrains Mono, Fira Code, monospace",
  "editor.fontLigatures": true,
  "editor.tabSize": 2,
  "editor.wordWrap": "on",
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "terminal.integrated.fontSize": 13,
  "git.autofetch": true,
  "workbench.startupEditor": "none",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## 最佳实践

1. **善用命令面板** — 记不住快捷键就用 `Ctrl+Shift+P`
2. **配置多根工作区** — 关联项目用 `.code-workspace` 管理
3. **使用 Snippets** — 自定义代码片段减少重复输入
4. **打开 Vim 模式** — `vim` 插件大幅提升纯键盘效率
5. **利用 Tasks** — `tasks.json` 配置构建/测试/部署命令
6. **定期清理插件** — 禁用不常用插件提升启动速度

---

## 相关页面

- [[Git高级技巧]]
- [[命令行效率工具]]
- [[API开发工具]]
- [[数据库客户端工具]]

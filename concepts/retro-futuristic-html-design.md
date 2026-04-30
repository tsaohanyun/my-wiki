---
title: 复古未来风 HTML 设计系统
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [framework, design-principle, pattern]
sources: [raw/articles/skill-retro-futuristic-html.md]
---

# 复古未来风 HTML 设计系统

## 概述
CRT 终端美学 × 太空时代仪表盘的完整设计系统。三个视觉支柱：CRT终端、太空控制面板、霓虹黑色电影。

## 字体体系

| 角色 | 字体 | Google Fonts 参数 |
|------|------|-------------------|
| 标题 | Orbitron (700/900) | `family=Orbitron:wght@400;700;900` |
| 数据/等宽 | Share Tech Mono | `family=Share+Tech+Mono` |
| 正文 | Rajdhani (300-700) | `family=Rajdhani:wght@300;400;500;600;700` |

规则：
- Orbitron：letter-spacing 0.08-0.15em，标题始终大写
- Share Tech Mono：数据值 0.02-0.06em，标签 0.1em+
- Rajdhani：正文，CJK回退 PingFang SC / Microsoft YaHei

## 色彩体系

```css
:root {
  --amber: #ff9e1b;          /* 主强调 — 标题、边框、光晕 */
  --amber-dim: #b36e0f;      /* 暗淡琥珀 — 非激活边框（不可用于深色背景文字） */
  --amber-glow: #ffb84d;     /* 亮琥珀 — 高亮 */
  --cyan: #00e5ff;           /* 次强调 — 分类、链接 */
  --cyan-dim: #007a8a;       /* 暗淡青色 */
  --magenta: #ff2d95;        /* 第三色 — 少用，警告 */
  --green: #39ff14;          /* 状态：在线、活跃、成功 */
  --green-dim: #1a8a0a;
  --red: #ff3b3b;            /* 状态：离线、错误、空 */
  --bg-deep: #0a0a12;        /* 最深背景 */
  --bg-panel: rgba(12,14,28,0.92);
  --bg-card: rgba(18,22,42,0.88);
  --border-main: rgba(255,158,27,0.35);
  --border-accent: rgba(0,229,255,0.3);
  --text-main: #d4c8a8;      /* 主文字 — 暖色羊皮纸 */
  --text-dim: #7a7060;       /* 暗淡文字 */
  --text-bright: #ffe4b5;    /* 高亮文字 */
}
```

色彩使用规则：
- Amber：标题、卡片边框、主光晕、版本徽章
- Cyan：分类标题、端点URL、辅助数据
- Green：活跃工具、正值、在线状态
- Red：离线、空值、错误
- amber-dim 不用于深色背景上的文字

## 视觉效果

### CRT 扫描线覆盖
`body::after` — fixed, 全屏, pointer-events:none, z-index:9999
```css
background: repeating-linear-gradient(
  0deg, transparent, transparent 2px,
  rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px
);
```

### 移动扫描条
8秒循环的水平光带动画

### 背景网格
40px网格，amber色0.03透明度

### 标题闪烁
模拟CRT微妙闪烁，保持克制（仅2-3次opacity下降）

### 霓虹光晕（text-shadow）
- Amber：`0 0 10px rgba(255,158,27,0.6), 0 0 30px rgba(255,158,27,0.3), 0 0 60px rgba(255,158,27,0.15)`
- Cyan：`0 0 8px rgba(0,229,255,0.4)`
- Green：`0 0 6px rgba(57,255,20,0.3)`

### 脉冲状态菱形
绿光脉冲动画

### 角框装饰
四个L形角固定在视口边缘，40×40px，amber-dim，opacity 0.4

## 形状语言

### 卡片 Clip-Path（科幻斜角）
```css
clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
```
右上和左下角切14px

### 标签 Clip-Path（梯形）
```css
clip-path: polygon(5px 0, 100% 0, calc(100% - 5px) 100%, 0 100%);
```

### 状态指示器：菱形
```css
clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
```

## 标签约定
使用终端风格前缀标签：
- `> MODEL` 不用 "当前模型"
- `> PROVIDER` 不用 "服务提供商"
- `> UPTIME` 不用 "运行时间"

徽章文本：ACTIVE / OFFLINE / NULL / CLI（大写英文）

### 图标使用几何 Unicode 符号（不用 emoji）
- ◈ 主区块 | ◉ 系统状态 | ⧫ 工具 | ⬡ 内存/密钥 | ⬢ 技能矩阵

## 布局
- 容器 max-width: 1440px
- 网格：`repeat(auto-fit, minmax(420px, 1fr))`，gap 20px
- 全宽卡片：`grid-column: 1 / -1`
- 响应式断点：800px → 单列

## 注意事项
1. 扫描线 z-index 必须9999且 pointer-events:none，否则阻断点击
2. amber-dim (#b36e0f) 在深色背景上不可读，文字用全amber (#ff9e1b)
3. 闪烁动画保持微妙，过度闪烁致头痛
4. clip-path + overflow:hidden 有交互问题，box-shadow 慎用
5. Orbitron 字体较重，Google Fonts 默认 font-display:swap
6. 移动端可减小网格 minmax 到 320px

## 相关链接
- [[frontend-design-system]] — 前端设计方法论总览
- [[html-prototype-generation]] — Apple Design 原型生成（对比风格）
- [[popular-web-design-templates]] — 更多设计模板

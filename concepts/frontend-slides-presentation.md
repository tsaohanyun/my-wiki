---
title: HTML 演示文稿生成
created: 2026-04-30
updated: 2026-05-01
type: concept
tags: [framework, tool, best-practice]
sources: [raw/articles/skill-frontend-slides.md]
---

# HTML 演示文稿生成

## 概述
创建零依赖、动画丰富的 HTML 演示文稿，完全在浏览器中运行。支持从零创建、PPT转换和已有演示增强三种模式。

## 核心原则
1. **零依赖** — 单个 HTML 文件，内联 CSS/JS，无 npm/构建工具
2. **展示而非讲述** — 生成视觉预览而非抽象选择
3. **独特设计** — 拒绝泛用"AI slop"，每份演示都需定制感
4. **视口适配（不可妥协）** — 每张幻灯片必须精确适配 100vh，绝不滚动

## 视口适配规则
- 每个 `.slide` 必须 `height: 100vh; height: 100dvh; overflow: hidden;`
- 所有字号和间距使用 `clamp(min, preferred, max)`，绝不用固定 px/rem
- 内容容器需要 `max-height` 约束
- 图片：`max-height: min(50vh, 400px)`
- 需要高度断点：700px, 600px, 500px
- 包含 `prefers-reduced-motion` 支持

## 每张幻灯片内容密度上限

| 幻灯片类型 | 最大内容 |
|-----------|---------|
| 标题页 | 1标题 + 1副标题 + 可选标语 |
| 内容页 | 1标题 + 4-6要点 或 1标题 + 2段落 |
| 特性网格 | 1标题 + 最多6卡片 (2×3 或 3×2) |
| 代码页 | 1标题 + 8-10行代码 |
| 引言页 | 1引言(最多3行) + 署名 |
| 图片页 | 1标题 + 1图片 (最高60vh) |

超出限制？拆成多页。绝不塞入，绝不滚动。

## 工作流程

### 阶段 0：检测模式
- **模式A：新建演示** → 阶段 1
- **模式B：PPT转换** → 阶段 4
- **模式C：增强现有** → 遵循修改规则

### 阶段 1：内容发现
询问：用途（路演/教学/会议/内部）、长度（5-10/10-20/20+）、内容状态、是否需要浏览器内编辑

### 阶段 2：风格发现
"展示而非讲述"阶段：
- 选择心情：震撼/兴奋/平静/灵感
- 生成3个风格预览幻灯片

| 心情 | 推荐预设 |
|------|---------|
| 震撼 | Bold Signal, Electric Studio, Dark Botanical |
| 兴奋 | Creative Voltage, Neon Cyber, Split Pastel |
| 平静 | Notebook Tabs, Paper & Ink, Swiss Modern |
| 灵感 | Dark Botanical, Vintage Editorial, Pastel Geometry |

### 阶段 3：生成演示
关键要求：
- 单个自包含 HTML 文件
- 包含 viewport-base.css 全部内容
- 使用 Fontshare 或 Google Fonts 字体
- 详细注释每个区块
- `/* === SECTION NAME ===` 注释块

### 阶段 4：PPT转换
1. `python scripts/extract-pptx.py <input.pptx> <output_dir>` 提取内容
2. 确认提取结果
3. 阶段 2 风格选择
4. 生成 HTML

### 阶段 5：交付
- 文件位置、风格名、幻灯片数
- 导航方式：方向键/空格/滚动/点击导航点
- 自定义方式：`:root` CSS变量、字体链接、`.reveal` 类动画

### 阶段 6：分享与导出（可选）
- 部署到 URL（Vercel）：`bash scripts/deploy.sh <path>`
- 导出 PDF：`bash scripts/export-pdf.sh <path-to-html> [output.pdf]`（用 Playwright 截图1920×1080合成PDF，`--compact` 为1280×720）

## 修改规则（模式C）
1. 添加内容前：计算现有元素，检查密度限制
2. 添加图片：必须有 `max-height: min(50vh, 400px)`
3. 添加文字：每页最多4-6要点
4. 任何修改后验证：`.slide` 有 `overflow:hidden`，新元素用 `clamp()`
5. 主动重组：修改会导致溢出时自动拆分

## 相关链接
- [[frontend-design-system]] — 前端设计方法论
- [[popular-web-design-templates]] — 设计模板库
- [[retro-futuristic-html-design]] — 复古未来风（适合科技演示）

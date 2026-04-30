---
title: HTML 生成风格对比
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [comparison, framework, architecture]
sources: [raw/articles/skill-apple-prototype-html.md, raw/articles/skill-retro-futuristic-html.md, raw/articles/skill-popular-web-designs.md, raw/articles/skill-frontend-design.md, raw/articles/skill-frontend-slides.md]
---

# HTML 生成风格对比

## 对比维度

| 维度 | Apple Design 原型 | 复古未来风 | 通用前端设计 | 热门设计模板 | HTML 演示文稿 |
|------|------------------|-----------|-------------|-------------|-------------|
| **目标场景** | 产品原型/B端业务 | 科技/控制台/游戏 | 任意前端界面 | 任意前端界面 | 演讲/路演/教学 |
| **主题** | 浅色 | 深色 | 由场景决定 | 54种可选 | 由场景决定 |
| **主字体** | Inter | Orbitron + Share Tech Mono + Rajdhani | 创意选择 | 随模板 | 创意选择 |
| **动画** | 零动画 | CRT闪烁/扫描/脉冲 | 丰富动画 | 随模板 | 丰富动画 |
| **色彩体系** | 蓝/绿/橙/红功能色 | 琥珀/青/绿/红终端色 | CSS变量驱动 | 每套模板独立 | CSS变量驱动 |
| **圆角** | 16px/10px 大圆角 | clip-path 斜切角 | 由场景决定 | 随模板 | 由场景决定 |
| **阴影** | 极轻(0.04透明度) | 霓虹光晕(text-shadow) | 由场景决定 | 随模板 | 由场景决定 |
| **输出格式** | 多页HTML(每页一文件) | 单页/多页HTML | 单页/组件 | 单页/多页HTML | 单文件HTML |
| **功能说明面板** | 必须(浮动/抽屉) | 无 | 无 | 无 | 无 |
| **移动端支持** | 有(底部标签+抽屉) | 有(响应式) | 由场景决定 | 随模板 | 简化 |
| **依赖** | 仅Google Fonts | 仅Google Fonts | 仅Google Fonts | 仅Google Fonts | 零依赖 |

## 选型建议

### 你要做什么？

| 场景 | 推荐风格 | 理由 |
|------|---------|------|
| B端业务系统原型 | Apple Design | 功能面板+角色权限+双标准输入完美适配 |
| 开发者工具/控制台 | 复古未来风 | 终端美学+数据密集+等宽字体 |
| 营销Landing Page | 热门模板(Stripe/Framer/Apple) | 高级感+视觉冲击 |
| 数据仪表盘 | 热门模板(Linear/Sentry/Kraken) | 暗色+数据密集+精致 |
| 演讲/路演 | HTML 演示文稿 | 100vh适配+动画+零依赖 |
| 创意/艺术项目 | 通用前端设计 | 完全自由发挥 |
| 技术文档站 | 热门模板(Mintlify/Notion) | 阅读优化+内容优先 |

### 风格组合
- Apple 原型 + FineReport：业务系统原型展示 + 报表模板开发
- 复古未来风 + 演示文稿：科技感演讲
- 热门模板 + 通用设计：快速套用+定制化

## 相关链接
- [[html-prototype-generation]] — Apple Design 原型详解
- [[retro-futuristic-html-design]] — 复古未来风详解
- [[frontend-design-system]] — 通用设计方法论
- [[popular-web-design-templates]] — 54种模板目录
- [[frontend-slides-presentation]] — 演示文稿详解
- [[fine-report-cpt]] — FineReport 报表模板

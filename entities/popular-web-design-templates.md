---
title: 54种热门网页设计模板
created: 2026-04-30
updated: 2026-04-30
type: entity
tags: [framework, library, tool]
sources: [raw/articles/skill-popular-web-designs.md]
---

# 54种热门网页设计模板

## 概述
从真实网站提取的54套生产级设计系统。每套模板捕捉完整的视觉语言：色彩体系、字体层级、组件样式、间距系统、阴影、响应行为和可直接使用的CSS值。

## 使用方法
1. 从目录中选择设计
2. 加载模板：`skill_view(name="popular-web-designs", file_path="templates/<site>.md")`
3. 应用设计令牌和组件规格生成HTML
4. 可配合 `generative-widgets` 技能通过 cloudflared 隧道提供

每个模板含 Hermes 实现说明：
- CDN字体替代和 Google Fonts `<link>` 标签
- 主字体和等宽字体的 CSS font-family 堆栈
- write_file 创建 HTML + browser_vision 验证的提醒

## 字体替代参考

| 专有字体 | CDN 替代 | 特征 |
|---------|---------|------|
| Geist / Geist Sans | Geist (Google Fonts) | 几何、压缩字距 |
| sohne-var (Stripe) | Source Sans 3 | 轻量优雅 |
| Airbnb Cereal VF | DM Sans | 圆润友好几何 |
| Circular (Spotify) | DM Sans | 几何温暖 |
| UberMove | DM Sans | 粗壮紧凑 |
| Berkeley Mono | JetBrains Mono | 技术等宽 |
| waldenburgNormal (Sanity) | Space Grotesk | 几何微缩 |

## AI & 机器学习类

| 模板 | 风格 |
|------|------|
| `claude.md` | 温暖赤土色调，干净编辑布局 |
| `cohere.md` | 鲜艳渐变，数据密集仪表盘 |
| `elevenlabs.md` | 深色电影UI，音频波形美学 |
| `minimax.md` | 大胆暗色界面+霓虹点缀 |
| `mistral.ai.md` | 法式极简，紫色调 |
| `ollama.md` | 终端优先，单色简约 |
| `opencode.ai.md` | 开发者中心暗色主题，全等宽 |
| `replicate.md` | 纯白画布，代码优先 |
| `runwayml.md` | 电影暗色UI，媒体丰富 |
| `together.ai.md` | 技术蓝图风格 |
| `voltagent.md` | 纯黑画布，翡翠点缀，终端原生 |
| `x.ai.md` | 极简单色，未来极简，全等宽 |

## 开发工具 & 平台类

| 模板 | 风格 |
|------|------|
| `cursor.md` | 优雅暗色界面，渐变点缀 |
| `linear.app.md` | 超极简暗色模式，精确，紫色点缀 |
| `vercel.md` | 黑白精确，Geist 字体系统 |
| `supabase.md` | 深翡翠主题，代码优先 |
| `sentry.md` | 暗色仪表盘，数据密集，粉紫点缀 |
| `raycast.md` | 优雅暗色，活力渐变 |
| `warp.md` | 暗色IDE式界面 |

## 基础设施 & 云类

| 模板 | 风格 |
|------|------|
| `stripe.md` | 标志性紫色渐变，weight-300 优雅 |
| `hashicorp.md` | 企业干净，黑白 |
| `clickhouse.md` | 黄色点缀，技术文档风格 |
| `mongodb.md` | 绿叶品牌，开发者文档 |

## 设计 & 生产力类

| 模板 | 风格 |
|------|------|
| `notion.md` | 温暖极简，衬线标题，柔和表面 |
| `figma.md` | 鲜艳多彩，趣味专业 |
| `framer.md` | 大胆黑蓝，动效优先 |
| `apple.md` | 高级留白，SF Pro，电影级图像 |

## 金融科技 & 加密类

| 模板 | 风格 |
|------|------|
| `coinbase.md` | 干净蓝色，信任导向 |
| `kraken.md` | 紫色暗色UI，数据密集 |
| `revolut.md` | 优雅暗色，渐变卡片 |

## 企业 & 消费类

| 模板 | 风格 |
|------|------|
| `airbnb.md` | 温暖珊瑚，摄影驱动 |
| `spacex.md` | 极简黑白，全出血图像 |
| `spotify.md` | 暗底鲜绿，粗体字 |
| `uber.md` | 粗壮黑白，都市活力 |
| `nvidia.md` | 绿黑能量，技术力量美学 |
| `bmw.md` | 深色高级表面，精确工程美学 |

## 选择建议

| 场景 | 推荐模板 |
|------|---------|
| 开发者工具/仪表盘 | Linear, Vercel, Supabase, Sentry |
| 文档/内容站 | Mintlify, Notion, Sanity, MongoDB |
| 营销/Landing Page | Stripe, Framer, Apple, SpaceX |
| 暗色模式UI | Linear, Cursor, ElevenLabs, Warp |
| 数据密集仪表盘 | Sentry, Kraken, Cohere, ClickHouse |
| 等宽/终端美学 | Ollama, OpenCode, x.ai, VoltAgent |

## 相关链接
- [[frontend-design-system]] — 前端设计方法论
- [[html-prototype-generation]] — Apple Design 原型
- [[retro-futuristic-html-design]] — 复古未来风
- [[frontend-slides-presentation]] — 演示文稿生成

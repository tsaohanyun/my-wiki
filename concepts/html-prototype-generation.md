---
title: HTML 原型生成
created: 2026-04-30
updated: 2026-04-30
type: concept
tags: [framework, architecture, best-practice]
sources: [raw/articles/skill-apple-prototype-html.md, raw/articles/skill-product-prototype-html.md]
---

# HTML 原型生成

## 概述
使用 Apple Design Language 生成产品原型 HTML 页面。每个页面是自包含的 HTML+CSS+JS 文件，内嵌功能说明面板供利益相关者审阅。覆盖 Web 端和移动端两种布局模式。

## 设计系统：Apple Design Language

### CSS 变量
```css
:root {
  --bg: #F5F5F7; --card: #FFFFFF; --text-primary: #1D1D1F;
  --text-secondary: #86868B; --text-tertiary: #AEAEB2;
  --accent: #007AFF; --border: #E5E5EA;
  --success: #34C759; --warning: #FF9500; --danger: #FF3B30;
  --purple: #5856D6; --radius: 16px; --radius-sm: 10px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04);
}
```

### 核心原则
- 字体：Inter（Google Fonts CDN）
- 浅色主题、大圆角、极轻阴影
- 零动画（静态原型）
- 颜色体系：accent蓝、success绿、warning橙、danger红、purple辅助

## Web 布局模式
```
┌──────────────────────────────────────────────┐
│ Top Nav (logo + role + logout)               │
├──────┬───────────────────────────────────────┤
│ Side │ Content Area                          │
│ bar  │                                       │
│ nav  │  Cards / Tables / Forms              │
│      │                                       │
├──────┴───────────────────────────────────────┤
                                   [Func Panel] │ (fixed, top-right)
```
- 顶栏：sticky, `backdrop-filter:blur(20px)`, 高52px
- 侧栏：220px宽，导航项含激活状态
- 功能面板：fixed定位，320px宽，右上角

## 移动端布局模式
```
┌──────────────────────┐
│ Nav Bar (back+title)  │
├──────────────────────┤
│                      │
│ Content (cards,      │
│ forms, lists)        │
│                      │
├──────────────────────┤
│ Bottom Tab Bar       │
└──────────────────────┘
                  [i FAB] → triggers bottom drawer
```
- 视口：max-width 430px, `margin:0 auto`
- 底部标签栏：fixed, `backdrop-filter:blur(20px)`, `safe-area-inset-bottom`
- 功能FAB：fixed, 底部96px, 右侧16px
- 功能面板：底部抽屉式，`transform:translateY(100%)` 切换

## 功能说明面板
每个页面必须包含功能说明面板，内容涵盖：
1. 页面用途和入口条件
2. 关键交互行为
3. 角色权限可见性
4. 业务规则约束
5. 数据流（操作后发生什么）

- **Web**：浮动面板，右上角，320px宽，蓝色"功能说明"徽章
- **Mobile**：FAB触发底部抽屉，含手柄栏，半透明遮罩

## 常用组件

### 状态标签
```html
<span class="tag tag-pending">待检验</span>   <!-- 橙色 -->
<span class="tag tag-progress">检验中</span>  <!-- 蓝色 -->
<span class="tag tag-done">已完成</span>      <!-- 绿色 -->
<span class="tag tag-fail">不合格</span>       <!-- 红色 -->
```

### 信息卡片（键值对行）
```html
<div class="info-card">
  <div class="info-row">
    <span class="info-key">标签</span>
    <span class="info-val">值</span>
  </div>
</div>
```

### 定量输入（双标准）
显示国标和企业标准的上下限，输入自动判定：
```html
<div class="quant-std-row">
  <div class="std-chip"><label>国标下限</label><span>0.80</span></div>
  <div class="std-chip"><label>企业下限</label><span>0.70</span></div>
</div>
<input class="quant-input" placeholder="实测值">
<span class="quant-judge judge-pass">✓ 合格</span>
```

### 定性输入
双按钮切换：合格 / 不合格，激活时显示绿/红样式。

## 文件命名与结构
```
project-name/
  web/
    01-page.html
    02-page.html
  mobile/
    09-page.html    （编号从Web续接）
    10-page.html
```

## 工作流程
1. 明确业务需求（角色、实体、流程、规则）
2. 映射页面到 Web 和 Mobile 两端
3. 先生成 Web 页面（宽布局，侧栏导航）
4. 再生成 Mobile 页面（紧凑，标签栏，底部抽屉）
5. 每个页面自包含，可独立浏览
6. 不包含登录页面（认证属于范围外）

## 注意事项
- 不使用外部JS/CSS库，仅允许 Google Fonts CDN
- 移动端固定底部元素必须使用 safe-area-inset-bottom
- 定量输入需同时显示国标和企业标准
- 交互元素应有基本JS状态切换
- 每个HTML文件控制在20KB以内

## 相关链接
- [[frontend-design-system]] — 前端设计系统总览
- [[retro-futuristic-html-design]] — 另一种风格选择
- [[popular-web-design-templates]] — 54种设计模板
- [[fine-report-cpt]] — 报表模板系统

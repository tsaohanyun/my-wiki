---
ingested: 2026-04-30
sha256: 7f3b83dd96ee3d04
source_url: hermes-skill://product-prototype-html
title: Product Prototype HTML Generator
---
---
name: product-prototype-html
version: 1.0
description: Generate product prototype UI pages in HTML format with Apple Design style, covering both Web and Mobile terminals. Each page includes a built-in function description panel.
triggers:
  - product prototype
  - 产品原型
  - prototype HTML
  - UI prototype
  - 原型设计
---

# Product Prototype HTML Generator

## Overview
Generate complete product prototype as individual HTML files with Apple Design Language. Each page is self-contained (HTML+CSS+JS, no external dependencies except Google Fonts). Output both Web and Mobile versions.

## Design System: Apple Design Language

### CSS Variables
```css
:root {
  --bg: #F5F5F7; --card: #FFFFFF; --text-primary: #1D1D1F;
  --text-secondary: #86868B; --text-tertiary: #AEAEB2;
  --accent: #007AFF; --border: #E5E5EA;
  --success: #34C759; --warning: #FF9500; --danger: #FF3B30;
  --purple: #5856D6;
  --radius: 16px; --radius-sm: 10px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04);
}
```

### Key Principles
- Font: Inter (Google Fonts CDN)
- Light theme, large border-radius, ultra-light shadows
- Zero animations (static prototype)
- Color system: accent blue, success green, warning orange, danger red, purple for secondary
- Spacing: 16-20px for mobile, 24-32px for web

## Layout Templates

### Web Layout
- Top navigation bar: logo + role name + avatar (sticky, blur backdrop)
- Left sidebar: vertical nav links (width ~220px)
- Right content area: max-width 960px centered
- Function description panel: fixed top-right corner, 320px wide

### Mobile Layout
- Viewport: max-width 430px, margin 0 auto
- Top nav bar: back button + title + action
- Content: card-based layout, 20px horizontal padding
- Bottom tab bar: fixed, blur backdrop, safe-area-inset-bottom
- Function description: bottom sheet drawer (slide up), triggered by floating "i" FAB button
- Safe area: `env(safe-area-inset-bottom, 0px)` for bottom bars

## Page Types & Naming Convention

- Number files sequentially: `01-login.html`, `02-dashboard.html`, etc.
- Web and Mobile in separate directories
- **Do NOT include login page** — login/authentication is out of scope for prototypes

## Function Description Panel

Every page MUST include a function description panel explaining:
1. Page purpose and entry conditions
2. Key interaction behaviors
3. Role-based visibility/permissions
4. Business rules and constraints
5. Data flow (what happens after action)

### Web Implementation
Fixed-position panel in top-right corner with:
- Badge label "功能说明"
- Numbered list with icon circles

### Mobile Implementation
- Floating action button (FAB) at bottom-right, 44px circle with "i"
- Bottom sheet drawer sliding up from bottom
- Semi-transparent overlay behind
- Handle bar at top for drag-to-dismiss feel

## Common Components

### Status Badges
```html
<span class="tag tag-pending">待检验</span>   <!-- orange -->
<span class="tag tag-progress">检验中</span>   <!-- blue -->
<span class="tag tag-done">已完成</span>       <!-- green -->
<span class="tag tag-fail">不合格</span>        <!-- red -->
```

### Info Card
Display key-value pairs in a white card with rows separated by borders.

### Form Elements
- Inputs: var(--bg) background, 1px border, rounded corners
- Focus: accent border + 3px accent shadow ring
- Textareas: resize:none, min-height proportional
- Selects: native styled with consistent sizing

### Quantitative Input (for inspection systems)
Show dual standard limits (national + enterprise):
```html
<div class="quant-std-row">
  <div class="std-chip"><label>国标下限</label><span>24.0</span></div>
  <div class="std-chip"><label>企业下限</label><span>25.0</span></div>
</div>
<input class="quant-input" placeholder="实测值">
```
Auto-highlight: border turns green (pass) or red (fail) based on input vs limits.

### Qualitative Input
Two-button toggle: 合格 / 不合格, styled with green/red when active.

## File Structure
```
project-name/
  web/
    01-page.html
    02-page.html
    ...
  mobile/
    09-page.html    (continue numbering from web)
    10-page.html
    ...
```

## Workflow
1. Clarify business requirements (roles, entities, flows, rules)
2. Map pages to both Web and Mobile (typically same page count)
3. Generate Web pages first (wider layout, sidebar nav)
4. Generate Mobile pages (compact, tab bar, bottom sheets)
5. Each page must be self-contained and viewable standalone
6. Backup all files to /home/agentuser/worklog/file/

## Pitfalls
- Never use external JS/CSS libraries — only Google Fonts CDN is allowed
- Never include login page in future prototypes (authentication is out of scope)
- Mobile pages MUST use safe-area-inset-bottom for fixed bottom elements
- Quantitative inputs need both national and enterprise standards displayed
- All interactive elements (buttons, toggles, tabs) should have basic JS for state changes
- Keep each HTML file under 20KB for fast loading

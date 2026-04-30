---
source_url: hermes-skill://apple-prototype-html
ingested: 2026-04-30
sha256: 445f6d767fd5aa8e
---
---
name: apple-prototype-html
description: Generate product prototype HTML pages using Apple Design Language. Use when creating UI prototypes, wireframes-as-code, or business application mockups that need a polished Apple-style look. Outputs self-contained HTML+CSS+JS files, one per page, with embedded functional description panels.
tags: [prototype, apple-design, html, mobile, web]
---

Generate product prototype HTML pages using Apple Design Language for business applications. Each page is a self-contained HTML file with embedded CSS and JS. Pages include functional description panels for stakeholder review.

## Design System

### CSS Variables (define in every page)
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

### Typography & Style Rules
- Font: Inter via Google Fonts CDN
- Zero animations (prototype, not production)
- Light theme only, no dark mode
- Large border-radius (16px cards, 10px inputs)
- Ultra-light shadows only
- Restrained, elegant aesthetic

## Web Layout Pattern

Structure: Top nav bar + Left sidebar navigation + Right content area + Floating func panel

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

- Top nav: sticky, `backdrop-filter:blur(20px)`, height 52px
- Sidebar: 220px wide, nav items with active state
- Func panel: fixed position, 320px wide, right 20px, top 20px

## Mobile Layout Pattern

Structure: Nav bar + Scrollable content + Bottom tab bar + Drawer func panel (triggered by FAB)

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

- Viewport: max-width 430px, `margin:0 auto`
- Bottom tab: fixed, `backdrop-filter:blur(20px)`, `safe-area-inset-bottom` padding
- Func FAB: fixed, bottom 96px (or 80px if no tab bar), right 16px
- Func panel: bottom drawer with handle, `transform:translateY(100%)` toggle
- Overlay: full-screen semi-transparent backdrop for drawer

## Functional Description Panel

Every page MUST include a functional description panel explaining:
- What the page does
- Key interactions and behaviors
- Role-based access rules
- Business logic constraints

### Web: Floating Panel (right side)
- Fixed position, 320px wide, top-right
- Blue badge "功能说明" + page title
- Numbered list with `func-num` circle indicators

### Mobile: Bottom Drawer
- Triggered by floating action button (FAB) showing "i"
- Slides up from bottom with handle bar
- Same content format as web
- Semi-transparent overlay backdrop
- `safe-area-inset-bottom` padding at bottom

## Component Patterns

### Status Badges
```html
<span class="tag tag-pending">待检验</span>   <!-- orange bg -->
<span class="tag tag-progress">检验中</span>  <!-- blue bg -->
<span class="tag tag-done">已完成</span>      <!-- green bg -->
<span class="tag tag-fail">不合格</span>       <!-- red bg -->
```

### Info Card (key-value rows)
```html
<div class="info-card">
  <div class="info-row">
    <span class="info-key">标签</span>
    <span class="info-val">值</span>
  </div>
</div>
```

### Quantitative Input (dual standard)
Show both national (国标) and enterprise (企业) standard upper/lower limits. Auto-judge on input:
```html
<div class="quant-std-row">
  <div class="std-chip"><label>国标下限</label><span>0.80</span></div>
  <div class="std-chip"><label>企业下限</label><span>0.70</span></div>
</div>
<input class="quant-input" placeholder="实测值">
<span class="quant-judge judge-pass">✓ 合格</span>
```

### Progress Bar (multi-step workflow)
Show workflow stages with dots and connecting lines. States: done (green), active (blue), pending (gray).

## Page Naming Convention

- Web: `01-name.html`, `02-name.html`, ... (sequential)
- Mobile: continue numbering from web: `09-name.html`, `10-name.html`, ...
- Store in separate directories: `web/` and `mobile/`

## Workflow

1. Clarify business requirements (roles, entities, workflow, rules)
2. Map out page list for each platform
3. Build pages sequentially, establishing CSS variable system in first page
4. Copy CSS variables and shared patterns across pages
5. Each page is self-contained (no shared CSS file) for easy standalone review
6. Include realistic sample data — not lorem ipsum

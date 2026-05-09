---
ingested: 2026-04-30
sha256: f181dc1e99af263b
source_url: hermes-skill://retro-futuristic-html
title: Retro-Futuristic HTML Design System
---
---
name: retro-futuristic-html
description: >
  Design system for retro-futuristic (复古未来风) HTML pages. CRT terminal aesthetics,
  sci-fi dashboard panels, neon glow effects, scanline overlays, and space-age typography.
  Use when the user requests retro-futuristic, cyberpunk-terminal, sci-fi dashboard,
  or CRT-style HTML design. Also the user's stated preference for HTML styling.
version: 1.0.0
tags: [html, css, design, retro-futuristic, crt, sci-fi, terminal]
---

# Retro-Futuristic HTML Design System

A complete design system for creating retro-futuristic web pages — CRT terminal meets space-age dashboard.

## Core Aesthetic

Three visual pillars:
1. **CRT Terminal** — scanlines, phosphor glow, flicker, monospace data
2. **Space-Age Control Panel** — angled clip-paths, neon indicators, grid overlays
3. **Neon Noir** — deep dark backgrounds, amber/cyan glow, stark contrast

## Typography

| Role | Font | Google Fonts Link | Fallback |
|------|------|-------------------|----------|
| Title/Heading | Orbitron (weight 700/900) | `family=Orbitron:wght@400;700;900` | monospace |
| Data/Monospace | Share Tech Mono | `family=Share+Tech+Mono` | monospace |
| Body Text | Rajdhani (weight 300-700) | `family=Rajdhani:wght@300;400;500;600;700` | sans-serif |

Font loading:
```html
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

Key rules:
- Orbitron: letter-spacing 0.08-0.15em, always uppercase for headers
- Share Tech Mono: letter-spacing 0.02-0.06em for data values, 0.1em+ for labels
- Rajdhani: body text, works well with CJK fallbacks (PingFang SC, Microsoft YaHei)

## Color Palette

### Primary Colors (CSS Custom Properties)
```css
:root {
  --amber: #ff9e1b;          /* Primary accent — headers, borders, glow */
  --amber-dim: #b36e0f;      /* Muted amber — inactive borders */
  --amber-glow: #ffb84d;     /* Bright amber — highlights */
  --cyan: #00e5ff;           /* Secondary accent — categories, links */
  --cyan-dim: #007a8a;       /* Muted cyan */
  --magenta: #ff2d95;        /* Tertiary — rarely used, for alerts */
  --green: #39ff14;          /* Status: online, active, success */
  --green-dim: #1a8a0a;      /* Muted green */
  --red: #ff3b3b;            /* Status: offline, error, null */
  --bg-deep: #0a0a12;        /* Deepest background */
  --bg-panel: rgba(12,14,28,0.92);  /* Panel background */
  --bg-card: rgba(18,22,42,0.88);   /* Card background */
  --border-main: rgba(255,158,27,0.35);  /* Primary border */
  --border-accent: rgba(0,229,255,0.3);  /* Secondary border */
  --text-main: #d4c8a8;      /* Primary text — warm parchment */
  --text-dim: #7a7060;       /* Muted text */
  --text-bright: #ffe4b5;    /* Highlighted text */
}
```

### Color Usage Rules
- Amber: headers, card borders, primary glow, version badges
- Cyan: category headings, endpoint URLs, secondary data
- Green: active tools, positive values, online status
- Red: offline status, null values, error states
- Amber-dim: inactive borders, decorative elements (not for text on dark)

## Visual Effects

### 1. CRT Scanline Overlay
Apply to `body::after` — fixed, full-screen, pointer-events none, z-index 9999:
```css
body::after {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px
  );
  pointer-events: none;
  z-index: 9999;
}
```

### 2. Moving Scan Bar
A slow-moving horizontal light band:
```css
@keyframes scanline {
  0% { top: -5%; }
  100% { top: 105%; }
}
.scan-bar {
  position: fixed; left: 0; right: 0; height: 60px;
  background: linear-gradient(180deg, transparent, rgba(0,229,255,0.04),
    rgba(0,229,255,0.08), rgba(0,229,255,0.04), transparent);
  animation: scanline 8s linear infinite;
  pointer-events: none; z-index: 9998;
}
```

### 3. Background Grid
```css
body::before {
  content: '';
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background:
    linear-gradient(rgba(255,158,27,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,158,27,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none; z-index: 0;
}
```

### 4. Title Flicker
Subtle CRT-style flicker on main heading:
```css
@keyframes flicker {
  0%, 100% { opacity: 1; }
  92% { opacity: 1; } 93% { opacity: 0.8; } 94% { opacity: 1; }
  96% { opacity: 0.9; } 97% { opacity: 1; }
}
```

### 5. Neon Glow (text-shadow)
```css
/* Amber glow */
text-shadow: 0 0 10px rgba(255,158,27,0.6), 0 0 30px rgba(255,158,27,0.3),
  0 0 60px rgba(255,158,27,0.15);

/* Cyan glow */
text-shadow: 0 0 8px rgba(0,229,255,0.4);

/* Green glow */
text-shadow: 0 0 6px rgba(57,255,20,0.3);
```

### 6. Pulsing Status Diamond
```css
@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 4px var(--green); }
  50% { box-shadow: 0 0 12px var(--green), 0 0 24px rgba(57,255,20,0.3); }
}
```

### 7. Corner Frame Decorations
Four L-shaped corners fixed at viewport edges:
```css
.corner-tl { top: 12px; left: 12px; border-width: 2px 0 0 2px; }
.corner-tr { top: 12px; right: 12px; border-width: 2px 2px 0 0; }
/* etc. — 40x40px, border-color: var(--amber-dim), opacity: 0.4 */
```

## Shape Language

### Card Clip-Path (Sci-Fi Angled Corners)
```css
clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
```
Top-right and bottom-left corners are cut at 14px.

### Tag/Badge Clip-Path (Trapezoid)
```css
clip-path: polygon(5px 0, 100% 0, calc(100% - 5px) 100%, 0 100%);
```
Left edge leans right, right edge leans left.

### Status Indicator Shape
Diamond instead of circle:
```css
clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
```

### Progress Bar Clip-Path
Single-side angled:
```css
clip-path: polygon(0 0, 100% 0, calc(100% - 4px) 100%, 0 100%);
```

## Label Conventions

Use terminal-style prefix labels:
- `> MODEL` not "当前模型"
- `> PROVIDER` not "服务提供商"
- `> UPTIME` not "运行时间"
- `> CRON_JOBS` not "定时任务"

Uppercase English key + Chinese/English value. This reinforces the terminal aesthetic.

Badge text: `ACTIVE` / `OFFLINE` / `NULL` / `CLI` (uppercase, English)

## Card Structure

```html
<div class="card">
  <div class="card-header">
    <span class="icon">◈</span>   <!-- Unicode symbol, not emoji -->
    <h2>SECTION TITLE</h2>
  </div>
  <div class="card-body">
    <!-- stat-rows, tool-grids, skill-tags, etc. -->
  </div>
</div>
```

Header icons: Use geometric Unicode symbols instead of emoji:
- ◈ (diamond with dot) — primary sections
- ◉ (fisheye) — system status
- ⧫ (black lozenge) — tools
- ⬡ (hexagon) — memory/keys
- ⬢ (black hexagon) — skill matrix

## Layout

- Container max-width: 1440px
- Grid: `repeat(auto-fit, minmax(420px, 1fr))`, gap 20px
- Full-width cards: `grid-column: 1 / -1`
- Responsive breakpoint: 800px → single column

## Pitfalls

1. **Scanline z-index** — must be 9999 and pointer-events:none, or it blocks clicks
2. **Text contrast** — amber-dim (#b36e0f) is unreadable on dark backgrounds; use full amber (#ff9e1b) for text
3. **Flicker animation** — keep it subtle (only 2-3 opacity dips per cycle). Aggressive flicker causes headaches
4. **clip-path + overflow:hidden** — clip-path clips the visual but hover shadows may extend; use box-shadow sparingly
5. **Google Fonts loading** — Orbitron is heavy; include `font-display: swap` behavior (Google Fonts handles this by default)
6. **Mobile responsiveness** — clip-path cards still work at small sizes; reduce grid minmax to 320px if needed

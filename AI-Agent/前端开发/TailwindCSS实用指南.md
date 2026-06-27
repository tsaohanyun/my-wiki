---
title: "TailwindCSS实用指南"
aliases:
  - "TailwindCSS教程"
  - "Tailwind CSS"
  - "原子化CSS"
tags:
  - "前端"
  - "CSS"
  - "TailwindCSS"
  - "UI框架"
type: "技术指南"
status: "已完成"
created: "2026-06-27"
updated: "2026-06-27"
source: "Hermes Agent"
difficulty: "初级-中级"
project: "前端开发"
---

# TailwindCSS实用指南

## 目录

1. [基础工具类](#基础工具类)
2. [响应式设计](#响应式设计)
3. [组件模式](#组件模式)
4. [自定义配置](#自定义配置)

## 基础工具类

### 颜色与背景

```html
<!-- 文字颜色 -->
<p class="text-gray-900">深灰色文字</p>
<p class="text-blue-600">蓝色文字</p>
<p class="text-red-500">红色文字</p>

<!-- 背景颜色 -->
<div class="bg-white">白色背景</div>
<div class="bg-gray-100">浅灰色背景</div>
<div class="bg-gradient-to-r from-blue-500 to-purple-500">
  渐变背景
</div>

<!-- 不透明度 -->
<div class="bg-black/50">50%透明度背景</div>
<div class="text-white/75">75%透明度文字</div>
```

### 间距与布局

```html
<!-- 外边距 -->
<div class="m-4">四方向外边距16px</div>
<div class="mt-8">顶部外边距32px</div>
<div class="mx-auto">水平居中</div>

<!-- 内边距 -->
<div class="p-4">四方向内边距16px</div>
<div class="px-6 py-3">水平24px，垂直12px</div>

<!-- Flexbox布局 -->
<div class="flex items-center justify-between">
  <span>左侧</span>
  <span>右侧</span>
</div>

<!-- Grid布局 -->
<div class="grid grid-cols-3 gap-4">
  <div class="bg-white p-4 rounded">项目1</div>
  <div class="bg-white p-4 rounded">项目2</div>
  <div class="bg-white p-4 rounded">项目3</div>
</div>
```

### 排版

```html
<!-- 字体大小 -->
<h1 class="text-4xl font-bold">大标题</h1>
<h2 class="text-2xl font-semibold">副标题</h2>
<p class="text-base">正文内容</p>
<small class="text-sm text-gray-500">小字说明</small>

<!-- 行高 -->
<p class="leading-relaxed">宽松行高</p>
<p class="leading-tight">紧凑行高</p>

<!-- 文字对齐 -->
<p class="text-center">居中对齐</p>
<p class="text-right">右对齐</p>
```

### 边框与圆角

```html
<!-- 边框 -->
<div class="border">默认边框</div>
<div class="border-2 border-blue-500">蓝色粗边框</div>
<div class="border-t border-gray-200">只有顶部边框</div>

<!-- 圆角 -->
<div class="rounded">小圆角</div>
<div class="rounded-lg">大圆角</div>
<div class="rounded-full">完全圆形</div>

<!-- 阴影 -->
<div class="shadow">默认阴影</div>
<div class="shadow-lg">大阴影</div>
<div class="shadow-2xl">超大阴影</div>
```

### 颜色系统

```html
<!-- 自定义颜色 -->
<div class="bg-primary-500">主色调</div>
<div class="bg-secondary-500">次色调</div>
<div class="text-accent-500">强调色</div>
```

## 响应式设计

### 断点系统

```html
<!-- 移动端优先 -->
<div class="text-sm md:text-base lg:text-lg xl:text-xl">
  响应式文字大小
</div>

<!-- 响应式布局 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="bg-white p-4 rounded">项目1</div>
  <div class="bg-white p-4 rounded">项目2</div>
  <div class="bg-white p-4 rounded">项目3</div>
</div>

<!-- 响应式显示/隐藏 -->
<div class="hidden md:block">仅在中等屏幕以上显示</div>
<div class="block md:hidden">仅在小屏幕显示</div>
```

### 响应式导航栏

```html
<nav class="bg-white shadow">
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex justify-between h-16">
      <!-- Logo -->
      <div class="flex items-center">
        <span class="text-xl font-bold">Logo</span>
      </div>

      <!-- 桌面端菜单 -->
      <div class="hidden md:flex items-center space-x-8">
        <a href="#" class="text-gray-700 hover:text-blue-500">首页</a>
        <a href="#" class="text-gray-700 hover:text-blue-500">关于</a>
        <a href="#" class="text-gray-700 hover:text-blue-500">联系</a>
      </div>

      <!-- 移动端菜单按钮 -->
      <div class="md:hidden flex items-center">
        <button class="text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</nav>
```

### 响应式卡片布局

```html
<div class="container mx-auto px-4 py-8">
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    <!-- 卡片1 -->
    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      <img src="image1.jpg" alt="Card 1" class="w-full h-48 object-cover">
      <div class="p-4">
        <h3 class="text-lg font-semibold mb-2">卡片标题</h3>
        <p class="text-gray-600 text-sm">卡片描述内容...</p>
      </div>
    </div>
    <!-- 更多卡片... -->
  </div>
</div>
```

## 组件模式

### 按钮组件

```html
<!-- 基础按钮 -->
<button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
  主要按钮
</button>

<!-- 次要按钮 -->
<button class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors">
  次要按钮
</button>

<!-- 危险按钮 -->
<button class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors">
  危险按钮
</button>

<!-- 禁用按钮 -->
<button class="px-4 py-2 bg-gray-300 text-gray-500 rounded cursor-not-allowed" disabled>
  禁用按钮
</button>

<!-- 加载按钮 -->
<button class="px-4 py-2 bg-blue-500 text-white rounded opacity-75 cursor-wait">
  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
  加载中...
</button>
```

### 表单组件

```html
<div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
  <h2 class="text-2xl font-bold mb-6">登录</h2>
  <form>
    <!-- 邮箱输入 -->
    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
        邮箱
      </label>
      <input
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        id="email"
        type="email"
        placeholder="your@email.com"
      >
    </div>

    <!-- 密码输入 -->
    <div class="mb-6">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
        密码
      </label>
      <input
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        id="password"
        type="password"
        placeholder="••••••••"
      >
    </div>

    <!-- 提交按钮 -->
    <button
      class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline transition-colors"
      type="submit"
    >
      登录
    </button>
  </form>
</div>
```

### 卡片组件

```html
<div class="max-w-sm rounded overflow-hidden shadow-lg">
  <img class="w-full" src="card-image.jpg" alt="Card image">
  <div class="px-6 py-4">
    <div class="font-bold text-xl mb-2">卡片标题</div>
    <p class="text-gray-700 text-base">
      这是卡片的描述内容，可以包含多行文字。
    </p>
  </div>
  <div class="px-6 pt-4 pb-2">
    <span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2 mb-2">#标签1</span>
    <span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2 mb-2">#标签2</span>
    <span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2 mb-2">#标签3</span>
  </div>
</div>
```

### 模态框组件

```html
<!-- 触发按钮 -->
<button onclick="document.getElementById('modal').classList.remove('hidden')" 
        class="px-4 py-2 bg-blue-500 text-white rounded">
  打开模态框
</button>

<!-- 模态框 -->
<div id="modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
  <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
    <div class="mt-3 text-center">
      <h3 class="text-lg leading-6 font-medium text-gray-900">模态框标题</h3>
      <div class="mt-2 px-7 py-3">
        <p class="text-sm text-gray-500">
          这是模态框的内容。
        </p>
      </div>
      <div class="items-center px-4 py-3">
        <button onclick="document.getElementById('modal').classList.add('hidden')"
                class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300">
          确定
        </button>
      </div>
    </div>
  </div>
</div>
```

### 暗黑模式

```html
<!-- 配置 -->
<!-- tailwind.config.js -->
<!-- module.exports = { darkMode: 'class' } -->

<!-- 使用 -->
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-white">标题</h1>
  <p class="text-gray-600 dark:text-gray-300">正文内容</p>
</div>

<!-- 暗黑模式切换按钮 -->
<button onclick="document.documentElement.classList.toggle('dark')"
        class="p-2 bg-gray-200 dark:bg-gray-700 rounded">
  切换主题
</button>
```

## 自定义配置

### tailwind.config.js

```javascript
// tailwind.config.js
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
      fontFamily: {
        sans: ['Inter var', ...defaultTheme.fontFamily.sans],
        display: ['Lexend', ...defaultTheme.fontFamily.sans],
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### 自定义工具类

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-500 text-white rounded-lg 
           hover:bg-blue-600 focus:outline-none focus:ring-2 
           focus:ring-blue-500 focus:ring-offset-2 transition-colors;
  }

  .btn-secondary {
    @apply px-4 py-2 bg-gray-200 text-gray-700 rounded-lg 
           hover:bg-gray-300 focus:outline-none focus:ring-2 
           focus:ring-gray-500 focus:ring-offset-2 transition-colors;
  }

  .card {
    @apply bg-white rounded-lg shadow-md p-6 
           hover:shadow-lg transition-shadow;
  }

  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-blue-500 
           focus:border-transparent transition-all;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }

  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

### 使用自定义类

```html
<!-- 使用自定义组件类 -->
<button class="btn-primary">主要按钮</button>
<button class="btn-secondary">次要按钮</button>

<div class="card">
  <h3 class="text-lg font-semibold">卡片标题</h3>
  <p class="text-gray-600">卡片内容</p>
</div>

<input class="input-field" placeholder="输入内容...">
```

## 最佳实践

### 性能优化

1. **使用JIT模式** - TailwindCSS 3.x默认启用JIT，按需生成CSS
2. **内容扫描** - 确保`content`配置正确扫描所有文件
3. **避免`@apply`滥用** - 仅在真正需要复用时使用

### 代码组织

1. **组件提取** - 将重复的类组合提取为组件
2. **一致的命名** - 使用一致的类命名约定
3. **响应式优先** - 移动端优先设计

### 可维护性

1. **使用主题配置** - 通过`tailwind.config.js`自定义主题
2. **避免魔法数字** - 使用预定义的间距和大小
3. **文档化** - 为自定义类添加注释

### 常见模式

```html
<!-- 截断文本 -->
<p class="truncate">这是一段很长的文本...</p>

<!-- 多行截断 -->
<p class="line-clamp-3">这是一段很长的文本，将被截断为三行显示...</p>

<!-- 滚动容器 -->
<div class="overflow-auto max-h-96 scrollbar-hide">
  <!-- 内容 -->
</div>

<!-- 固定宽高比 -->
<div class="aspect-video">
  <!-- 16:9 -->
</div>
<div class="aspect-square">
  <!-- 1:1 -->
</div>
```

## 相关页面

- [[Next.js开发指南]]
- [[前端性能优化]]
- [[前端测试策略]]
- [[PWA开发指南]]

---

*最后更新于 2026-06-27*

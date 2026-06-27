---
title: "Next.js开发指南"
aliases:
  - "Next.js教程"
  - "Next.js App Router"
  - "React Server Components"
tags:
  - "前端"
  - "React"
  - "Next.js"
  - "SSR"
  - "SSG"
type: "技术指南"
status: "已完成"
created: "2026-06-27"
updated: "2026-06-27"
source: "Hermes Agent"
difficulty: "中级"
project: "前端开发"
---

# Next.js开发指南

## 目录

1. [App Router架构](#app-router架构)
2. [Server Components](#server-components)
3. [数据获取策略](#数据获取策略)
4. [部署与优化](#部署与优化)

## App Router架构

### 项目结构

```
my-app/
├── app/
│   ├── layout.tsx          # 根布局
│   ├── page.tsx            # 首页
│   ├── loading.tsx         # 加载状态
│   ├── error.tsx           # 错误处理
│   ├── not-found.tsx       # 404页面
│   ├── dashboard/
│   │   ├── layout.tsx      # 嵌套布局
│   │   ├── page.tsx        # 仪表盘页面
│   │   └── settings/
│   │       └── page.tsx    # 设置页面
│   └── api/
│       └── users/
│           └── route.ts    # API路由
└── public/
    └── images/
```

### 根布局示例

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'My Next.js App',
  description: 'A modern web application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

### 嵌套布局

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex">
      <aside className="w-64 bg-gray-100 p-4">
        <nav>
          <ul className="space-y-2">
            <li><a href="/dashboard">概览</a></li>
            <li><a href="/dashboard/settings">设置</a></li>
          </ul>
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  )
}
```

### Loading与Error处理

```tsx
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
      <div className="h-64 bg-gray-200 rounded"></div>
    </div>
  )
}

// app/dashboard/error.tsx
'use client'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="text-center p-8">
      <h2 className="text-2xl font-bold text-red-600 mb-4">
        出错了！
      </h2>
      <p className="mb-4">{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-blue-500 text-white rounded"
      >
        重试
      </button>
    </div>
  )
}
```

## Server Components

### 默认Server Components

```tsx
// app/page.tsx (默认是Server Component)
import { fetchUsers } from '@/lib/api'

export default async function HomePage() {
  // 可以直接使用async/await
  const users = await fetchUsers()

  return (
    <div>
      <h1>用户列表</h1>
      <ul>
        {users.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

### Client Components

```tsx
// components/Counter.tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div className="p-4 border rounded">
      <p className="text-2xl mb-2">计数: {count}</p>
      <div className="space-x-2">
        <button
          onClick={() => setCount(count - 1)}
          className="px-3 py-1 bg-red-500 text-white rounded"
        >
          减少
        </button>
        <button
          onClick={() => setCount(count + 1)}
          className="px-3 py-1 bg-green-500 text-white rounded"
        >
          增加
        </button>
      </div>
    </div>
  )
}
```

### 组件组合模式

```tsx
// app/page.tsx (Server Component)
import ClientCounter from '@/components/Counter'
import ServerData from '@/components/ServerData'

export default function Page() {
  return (
    <div>
      <ServerData />
      <ClientCounter />
    </div>
  )
}

// components/ServerData.tsx (Server Component)
export default async function ServerData() {
  const data = await fetch('https://api.example.com/data')
  const json = await data.json()

  return <div>服务器数据: {json.value}</div>
}
```

## 数据获取策略

### 服务器端数据获取

```tsx
// app/posts/page.tsx
interface Post {
  id: number
  title: string
  content: string
}

export default async function PostsPage() {
  // 在服务器端获取数据
  const res = await fetch('https://api.example.com/posts', {
    cache: 'no-store', // 或 'force-cache'
  })
  const posts: Post[] = await res.json()

  return (
    <div>
      <h1>文章列表</h1>
      {posts.map((post) => (
        <article key={post.id} className="mb-4 p-4 border rounded">
          <h2 className="text-xl font-bold">{post.title}</h2>
          <p className="mt-2">{post.content}</p>
        </article>
      ))}
    </div>
  )
}
```

### 缓存策略

```tsx
// 强制缓存（静态数据）
const res = await fetch('https://api.example.com/static-data', {
  cache: 'force-cache',
})

// 禁用缓存（动态数据）
const res = await fetch('https://api.example.com/real-time-data', {
  cache: 'no-store',
})

// 定时重新验证
const res = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 }, // 每小时重新验证
})
```

### Server Actions

```tsx
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  // 保存到数据库
  await db.posts.create({
    data: { title, content },
  })

  revalidatePath('/posts')
}

// app/posts/create/page.tsx
import { createPost } from '@/app/actions'

export default function CreatePostPage() {
  return (
    <form action={createPost}>
      <input
        name="title"
        placeholder="文章标题"
        className="border p-2 w-full mb-2"
      />
      <textarea
        name="content"
        placeholder="文章内容"
        className="border p-2 w-full mb-2 h-32"
      />
      <button
        type="submit"
        className="px-4 py-2 bg-blue-500 text-white rounded"
      >
        创建文章
      </button>
    </form>
  )
}
```

### API路由

```tsx
// app/api/users/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const users = await db.users.findMany()
  return NextResponse.json(users)
}

export async function POST(request: Request) {
  const body = await request.json()
  const user = await db.users.create({ data: body })
  return NextResponse.json(user, { status: 201 })
}

// app/api/users/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const user = await db.users.findUnique({
    where: { id: parseInt(params.id) },
  })

  if (!user) {
    return NextResponse.json(
      { error: '用户不存在' },
      { status: 404 }
    )
  }

  return NextResponse.json(user)
}
```

## 部署与优化

### 静态导出

```tsx
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // 启用静态导出
  images: {
    unoptimized: true, // 静态导出时需要
  },
}

module.exports = nextConfig
```

### 图片优化

```tsx
import Image from 'next/image'

export default function OptimizedImage() {
  return (
    <Image
      src="/images/hero.jpg"
      alt="Hero image"
      width={800}
      height={400}
      priority
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  )
}
```

### 字体优化

```tsx
import { Inter, Roboto } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const roboto = Roboto({
  weight: ['400', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto',
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${roboto.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

### 中间件

```tsx
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 检查认证
  const token = request.cookies.get('token')
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/dashboard')

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // 添加自定义头部
  const response = NextResponse.next()
  response.headers.set('x-custom-header', 'my-value')

  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
}
```

### 环境变量

```env
# .env.local
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
NEXT_PUBLIC_API_URL=https://api.example.com
```

```tsx
// 使用环境变量
const apiUrl = process.env.NEXT_PUBLIC_API_URL // 客户端可访问
const dbUrl = process.env.DATABASE_URL          // 仅服务器端
```

## 最佳实践

### 性能优化

1. **使用Server Components** - 默认使用Server Components，减少客户端JavaScript
2. **图片优化** - 使用`next/image`组件自动优化图片
3. **字体优化** - 使用`next/font`自动优化字体加载
4. **代码分割** - 使用`dynamic`导入实现懒加载

### 代码组织

1. **组件拆分** - Server Components与Client Components合理拆分
2. **目录结构** - 遵循App Router的目录结构约定
3. **类型安全** - 使用TypeScript确保类型安全

### 安全性

1. **环境变量** - 敏感信息使用`.env.local`，不暴露给客户端
2. **输入验证** - 使用Zod等库验证输入数据
3. **CSRF防护** - Server Actions自动提供CSRF防护

## 相关页面

- [[TailwindCSS实用指南]]
- [[前端性能优化]]
- [[前端测试策略]]
- [[PWA开发指南]]

---

*最后更新于 2026-06-27*

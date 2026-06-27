---
title: "PWA开发指南"
aliases:
  - "Progressive Web App"
  - "渐进式Web应用"
  - "PWA教程"
tags:
  - "前端"
  - "PWA"
  - "Service Worker"
  - "离线应用"
  - "推送通知"
type: "技术指南"
status: "已完成"
created: "2026-06-27"
updated: "2026-06-27"
source: "Hermes Agent"
difficulty: "中级"
project: "前端开发"
---

# PWA开发指南

## 目录

1. [Service Worker](#service-worker)
2. [离线缓存](#离线缓存)
3. [推送通知](#推送通知)
4. [安装体验](#安装体验)

## Service Worker

### 注册Service Worker

```javascript
// main.js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        console.log('SW registered:', registration.scope)
        
        // 检查更新
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          console.log('New SW installing...')
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'activated') {
              console.log('New SW activated')
              // 通知用户有新版本
              showUpdateNotification()
            }
          })
        })
      })
      .catch((error) => {
        console.log('SW registration failed:', error)
      })
  })
}
```

### Service Worker生命周期

```javascript
// sw.js
const CACHE_NAME = 'my-app-v1'

// 安装事件 - 预缓存资源
self.addEventListener('install', (event) => {
  console.log('SW installing...')
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Caching app shell')
      return cache.addAll([
        '/',
        '/index.html',
        '/styles.css',
        '/app.js',
        '/images/logo.png',
        '/offline.html',
      ])
    })
  )
  
  // 跳过等待，立即激活
  self.skipWaiting()
})

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
  console.log('SW activating...')
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('Deleting old cache:', name)
            return caches.delete(name)
          })
      )
    })
  )
  
  // 立即控制所有客户端
  self.clients.claim()
})

// 请求拦截
self.addEventListener('fetch', (event) => {
  // 跳过非GET请求
  if (event.request.method !== 'GET') return
  
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // 返回缓存或发起网络请求
      return cachedResponse || fetch(event.request)
    })
  )
})
```

### 更新Service Worker

```javascript
// 检查更新
function checkForUpdates() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.update()
    })
  }
}

// 监听更新
let newWorker = null
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (newWorker) {
      window.location.reload()
    }
  })
  
  navigator.serviceWorker.ready.then((registration) => {
    registration.addEventListener('updatefound', () => {
      newWorker = registration.installing
      
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed') {
          if (navigator.serviceWorker.controller) {
            // 有新版本可用
            showUpdateUI()
          }
        }
      })
    })
  })
}
```

## 离线缓存

### 缓存策略

```javascript
// sw.js - Cache First策略
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    return cachedResponse
  }
  
  try {
    const response = await fetch(request)
    const cache = await caches.open(CACHE_NAME)
    cache.put(request, response.clone())
    return response
  } catch (error) {
    // 返回离线页面
    return caches.match('/offline.html')
  }
}

// Network First策略
async function networkFirst(request) {
  try {
    const response = await fetch(request)
    const cache = await caches.open(CACHE_NAME)
    cache.put(request, response.clone())
    return response
  } catch (error) {
    const cachedResponse = await caches.match(request)
    return cachedResponse || caches.match('/offline.html')
  }
}

// Stale While Revalidate策略
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME)
  const cachedResponse = await cache.match(request)
  
  const fetchPromise = fetch(request).then((response) => {
    cache.put(request, response.clone())
    return response
  }).catch(() => {
    return caches.match('/offline.html')
  })
  
  return cachedResponse || fetchPromise
}
```

### 动态缓存

```javascript
// 根据请求类型选择策略
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // 静态资源 - Cache First
  if (url.pathname.match(/\.(js|css|png|jpg|svg|woff2)$/)) {
    event.respondWith(cacheFirst(request))
    return
  }
  
  // API请求 - Network First
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request))
    return
  }
  
  // 页面 - Stale While Revalidate
  event.respondWith(staleWhileRevalidate(request))
})
```

### IndexedDB离线存储

```javascript
// db.js
class OfflineDB {
  constructor() {
    this.dbName = 'OfflineDB'
    this.dbVersion = 1
    this.db = null
  }

  async open() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion)
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        
        if (!db.objectStoreNames.contains('pendingRequests')) {
          db.createObjectStore('pendingRequests', { keyPath: 'id', autoIncrement: true })
        }
        
        if (!db.objectStoreNames.contains('cachedData')) {
          db.createObjectStore('cachedData', { keyPath: 'url' })
        }
      }
      
      request.onsuccess = (event) => {
        this.db = event.target.result
        resolve(this.db)
      }
      
      request.onerror = (event) => {
        reject(event.target.error)
      }
    })
  }

  async savePendingRequest(request) {
    const db = await this.open()
    const transaction = db.transaction(['pendingRequests'], 'readwrite')
    const store = transaction.objectStore('pendingRequests')
    
    return store.add({
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers.entries()),
      body: await request.clone().text(),
      timestamp: Date.now(),
    })
  }

  async getPendingRequests() {
    const db = await this.open()
    const transaction = db.transaction(['pendingRequests'], 'readonly')
    const store = transaction.objectStore('pendingRequests')
    
    return new Promise((resolve, reject) => {
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async clearPendingRequests() {
    const db = await this.open()
    const transaction = db.transaction(['pendingRequests'], 'readwrite')
    const store = transaction.objectStore('pendingRequests')
    
    return store.clear()
  }

  async cacheData(url, data) {
    const db = await this.open()
    const transaction = db.transaction(['cachedData'], 'readwrite')
    const store = transaction.objectStore('cachedData')
    
    return store.put({
      url,
      data,
      timestamp: Date.now(),
    })
  }

  async getCachedData(url) {
    const db = await this.open()
    const transaction = db.transaction(['cachedData'], 'readonly')
    const store = transaction.objectStore('cachedData')
    
    return new Promise((resolve, reject) => {
      const request = store.get(url)
      request.onsuccess = () => resolve(request.result?.data)
      request.onerror = () => reject(request.error)
    })
  }
}

export const offlineDB = new OfflineDB()
```

### 同步离线数据

```javascript
// sw.js - Background Sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-pending-requests') {
    event.waitUntil(syncPendingRequests())
  }
})

async function syncPendingRequests() {
  const db = new OfflineDB()
  const pendingRequests = await db.getPendingRequests()
  
  for (const requestData of pendingRequests) {
    try {
      const response = await fetch(requestData.url, {
        method: requestData.method,
        headers: requestData.headers,
        body: requestData.body,
      })
      
      if (response.ok) {
        // 同步成功，删除待处理请求
        await db.clearPendingRequests()
        
        // 通知客户端同步完成
        self.clients.matchAll().then((clients) => {
          clients.forEach((client) => {
            client.postMessage({
              type: 'SYNC_COMPLETE',
              data: requestData,
            })
          })
        })
      }
    } catch (error) {
      console.error('Sync failed:', error)
    }
  }
}
```

## 推送通知

### 请求权限

```javascript
// notifications.js
async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.log('This browser does not support notifications')
    return false
  }
  
  if (Notification.permission === 'granted') {
    return true
  }
  
  if (Notification.permission === 'denied') {
    console.log('Notifications are denied')
    return false
  }
  
  const permission = await Notification.requestPermission()
  return permission === 'granted'
}

// 订阅推送
async function subscribeToPush() {
  const registration = await navigator.serviceWorker.ready
  
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
  })
  
  // 发送订阅到服务器
  await fetch('/api/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription),
  })
  
  return subscription
}

// VAPID密钥转换
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  
  return outputArray
}
```

### 处理推送消息

```javascript
// sw.js
self.addEventListener('push', (event) => {
  console.log('Push received:', event)
  
  let data = { title: '新消息', body: '您有一条新消息' }
  
  if (event.data) {
    data = event.data.json()
  }
  
  const options = {
    body: data.body,
    icon: '/images/icon-192x192.png',
    badge: '/images/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/',
    },
    actions: [
      {
        action: 'open',
        title: '查看',
      },
      {
        action: 'close',
        title: '关闭',
      },
    ],
  }
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  )
})

// 通知点击处理
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event)
  
  event.notification.close()
  
  if (event.action === 'open' || !event.action) {
    const url = event.notification.data.url
    
    event.waitUntil(
      self.clients.matchAll({ type: 'window' }).then((clients) => {
        // 如果已有窗口打开，聚焦到该窗口
        for (const client of clients) {
          if (client.url === url && 'focus' in client) {
            return client.focus()
          }
        }
        
        // 否则打开新窗口
        return self.clients.openWindow(url)
      })
    )
  }
})
```

### 服务器端推送

```javascript
// server/push.js
const webPush = require('web-push')

// 配置VAPID密钥
webPush.setVapidDetails(
  'mailto:your@email.com',
  process.env.VAPID_PUBLIC_KEY,
  process.env.VAPID_PRIVATE_KEY
)

// 存储订阅
const subscriptions = new Map()

// 订阅端点
app.post('/api/subscribe', (req, res) => {
  const subscription = req.body
  const userId = req.user.id
  
  subscriptions.set(userId, subscription)
  res.status(201).json({ message: 'Subscribed successfully' })
})

// 发送推送通知
async function sendPushNotification(userId, payload) {
  const subscription = subscriptions.get(userId)
  
  if (!subscription) {
    console.log('No subscription found for user:', userId)
    return
  }
  
  try {
    await webPush.sendNotification(subscription, JSON.stringify(payload))
    console.log('Push notification sent to user:', userId)
  } catch (error) {
    console.error('Failed to send push notification:', error)
    
    // 如果订阅失效，删除它
    if (error.statusCode === 410) {
      subscriptions.delete(userId)
    }
  }
}

// 使用示例
app.post('/api/send-notification', async (req, res) => {
  const { userId, title, body, url } = req.body
  
  await sendPushNotification(userId, {
    title,
    body,
    url,
  })
  
  res.json({ message: 'Notification sent' })
})
```

## 安装体验

### 检测安装状态

```javascript
// install.js
let deferredPrompt = null

// 监听beforeinstallprompt事件
window.addEventListener('beforeinstallprompt', (event) => {
  // 阻止默认提示
  event.preventDefault()
  
  // 保存事件以便稍后触发
  deferredPrompt = event
  
  // 显示自定义安装按钮
  showInstallButton()
})

// 监听appinstalled事件
window.addEventListener('appinstalled', (event) => {
  console.log('App installed successfully')
  deferredPrompt = null
  
  // 隐藏安装按钮
  hideInstallButton()
  
  // 发送分析事件
  sendAnalyticsEvent('app_installed')
})

// 检测是否已安装
function isAppInstalled() {
  return window.matchMedia('(display-mode: standalone)').matches ||
         window.navigator.standalone === true
}
```

### 自定义安装UI

```html
<!-- install-prompt.html -->
<div id="install-prompt" class="hidden fixed bottom-4 right-4 bg-white rounded-lg shadow-xl p-4 max-w-sm">
  <div class="flex items-start">
    <img src="/images/icon-192x192.png" alt="App icon" class="w-16 h-16 rounded-lg mr-4">
    <div class="flex-1">
      <h3 class="font-bold text-lg">安装应用</h3>
      <p class="text-gray-600 text-sm mt-1">
        将应用添加到主屏幕，获得更好的体验
      </p>
    </div>
    <button id="close-install-prompt" class="text-gray-400 hover:text-gray-600">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>
  </div>
  <div class="mt-4 flex justify-end space-x-2">
    <button id="install-later" class="px-4 py-2 text-gray-600 hover:text-gray-800">
      稍后
    </button>
    <button id="install-now" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
      安装
    </button>
  </div>
</div>

<script>
const installPrompt = document.getElementById('install-prompt')
const installButton = document.getElementById('install-now')
const closeButtons = document.querySelectorAll('#close-install-prompt, #install-later')

function showInstallButton() {
  installPrompt.classList.remove('hidden')
}

function hideInstallButton() {
  installPrompt.classList.add('hidden')
}

installButton.addEventListener('click', async () => {
  if (deferredPrompt) {
    // 显示安装提示
    deferredPrompt.prompt()
    
    // 等待用户响应
    const { outcome } = await deferredPrompt.userChoice
    console.log('User choice:', outcome)
    
    if (outcome === 'accepted') {
      console.log('User accepted the install prompt')
    }
    
    deferredPrompt = null
    hideInstallButton()
  }
})

closeButtons.forEach((button) => {
  button.addEventListener('click', () => {
    hideInstallButton()
  })
})
</script>
```

### Web App Manifest

```json
{
  "name": "My PWA App",
  "short_name": "MyApp",
  "description": "A Progressive Web App",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "orientation": "portrait",
  "scope": "/",
  "lang": "zh-CN",
  "categories": ["productivity", "utilities"],
  "screenshots": [
    {
      "src": "/screenshots/screenshot1.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    },
    {
      "src": "/screenshots/screenshot2.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ],
  "icons": [
    {
      "src": "/images/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "/images/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "/images/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "/images/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png"
    },
    {
      "src": "/images/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png"
    },
    {
      "src": "/images/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/images/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png"
    },
    {
      "src": "/images/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

### Next.js PWA配置

```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
})

module.exports = withPWA({
  // 其他Next.js配置
})

// public/manifest.json
{
  "name": "My Next.js PWA",
  "short_name": "NextPWA",
  "description": "A PWA built with Next.js",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}

// app/layout.tsx
export const metadata = {
  manifest: '/manifest.json',
  themeColor: '#3b82f6',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
}
```

## 最佳实践

### 性能优化

1. **预缓存关键资源** - 缓存App Shell和关键静态资源
2. **合理的缓存策略** - 根据资源类型选择合适的缓存策略
3. **增量缓存** - 按需缓存非关键资源

### 用户体验

1. **离线优先** - 优先考虑离线用户体验
2. **同步状态** - 同步在线和离线数据状态
3. **更新提示** - 及时通知用户应用更新

### 安全性

1. **HTTPS** - PWA必须运行在HTTPS环境下
2. **权限管理** - 合理请求推送通知权限
3. **数据加密** - 敏感数据加密存储

### 测试清单

```markdown
- [ ] Service Worker正确注册和激活
- [ ] 离线状态下可以访问App Shell
- [ ] 离线数据同步正常工作
- [ ] 推送通知正确发送和接收
- [ ] 安装提示正确显示
- [ ] 应用可以从主屏幕启动
- [ ] 主题色和图标正确显示
- [ ] 不同网络条件下的性能表现
```

## 相关页面

- [[Next.js开发指南]]
- [[TailwindCSS实用指南]]
- [[前端性能优化]]
- [[前端测试策略]]

---

*最后更新于 2026-06-27*

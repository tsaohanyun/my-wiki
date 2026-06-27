---
title: Vue开发指南
aliases:
  - Vue.js指南
  - Vue3开发
tags:
  - Vue
  - Vue3
  - 组合式API
  - 前端
  - 编程基础
type: wiki
status: published
created: 2025-01-01
updated: 2025-01-01
source: AI-Agent知识库
difficulty: intermediate
project: AI-Agent
---

# Vue开发指南

Vue 3 是一个渐进式 JavaScript 框架，组合式 API 提供了更灵活的代码组织方式。

## 1. 组合式 API (Composition API)

### setup 语法糖

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

// 响应式状态
const count = ref(0);
const message = ref("Hello Vue 3");

// 计算属性
const doubleCount = computed(() => count.value * 2);

// 方法
function increment() {
  count.value++;
}

// 生命周期
onMounted(() => {
  console.log("Component mounted");
});
</script>

<template>
  <div>
    <p>{{ message }}: {{ count }} x 2 = {{ doubleCount }}</p>
    <button @click="increment">+1</button>
  </div>
</template>
```

## 2. 响应式系统

### ref 与 reactive

```vue
<script setup lang="ts">
import { ref, reactive, toRefs, computed, watch, watchEffect } from "vue";

// ref - 适用于原始值
const name = ref("Alice");
const age = ref(30);

// reactive - 适用于对象
const state = reactive({
  items: [] as string[],
  loading: false,
  error: null as string | null,
});

// toRefs - 解构时保持响应性
const { items, loading } = toRefs(state);

// watch - 精确监听
watch(name, (newVal, oldVal) => {
  console.log(`Name changed: ${oldVal} -> ${newVal}`);
});

// watchEffect - 自动追踪依赖
watchEffect(() => {
  console.log(`Current name: ${name.value}, age: ${age.value}`);
});

// 深度监听
watch(
  () => state.items,
  (newItems) => {
    console.log("Items changed:", newItems);
  },
  { deep: true }
);
</script>
```

### 自定义组合式函数 (Composables)

```typescript
// composables/useFetch.ts
import { ref, watchEffect, type Ref } from "vue";

interface UseFetchReturn<T> {
  data: Ref<T | null>;
  error: Ref<string | null>;
  loading: Ref<boolean>;
  refetch: () => Promise<void>;
}

export function useFetch<T>(url: Ref<string> | string): UseFetchReturn<T> {
  const data = ref<T | null>(null) as Ref<T | null>;
  const error = ref<string | null>(null);
  const loading = ref(false);

  async function fetchData() {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(typeof url === "string" ? url : url.value);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data.value = await res.json();
    } catch (err) {
      error.value = (err as Error).message;
    } finally {
      loading.value = false;
    }
  }

  watchEffect(() => { fetchData(); });

  return { data, error, loading, refetch: fetchData };
}
```

```vue
<!-- 使用 composable -->
<script setup lang="ts">
import { ref } from "vue";
import { useFetch } from "./composables/useFetch";

interface User { id: number; name: string; }

const userId = ref(1);
const { data: user, loading, error } = useFetch<User>(
  computed(() => `https://api.example.com/users/${userId.value}`)
);
</script>
```

## 3. 组件

### Props 与 Emits

```vue
<script setup lang="ts">
// 子组件 TodoItem.vue
interface Todo {
  id: number;
  text: string;
  done: boolean;
}

const props = defineProps<{
  todo: Todo;
  index: number;
}>();

const emit = defineEmits<{
  toggle: [id: number];
  delete: [id: number];
}>();
</script>

<template>
  <li :class="{ done: todo.done }">
    <input type="checkbox" :checked="todo.done" @change="emit('toggle', todo.id)" />
    <span>{{ todo.text }}</span>
    <button @click="emit('delete', todo.id)">删除</button>
  </li>
</template>
```

### 插槽 (Slots)

```vue
<!-- Card.vue -->
<script setup lang="ts">
defineSlots<{
  header(props: {}): any;
  default(props: {}): any;
  footer(props: { count: number }): any;
}>();

defineProps<{ count: number }>();
</script>

<template>
  <div class="card">
    <div class="header"><slot name="header" /></div>
    <div class="body"><slot /></div>
    <div class="footer"><slot name="footer" :count="count" /></div>
  </div>
</template>
```

### provide / inject

```typescript
// 祖先组件
import { provide, ref } from "vue";

const theme = ref("dark");
provide("theme", theme);
provide("appName", "MyApp");

// 后代组件
import { inject } from "vue";

const theme = inject<Ref<string>>("theme", ref("light"));
const appName = inject<string>("appName", "Default");
```

## 4. 路由 (Vue Router)

```typescript
// router/index.ts
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("../views/Home.vue"),
    },
    {
      path: "/users/:id",
      name: "user",
      component: () => import("../views/User.vue"),
      props: true, // 将 params 作为 props 传递
    },
    {
      path: "/dashboard",
      component: () => import("../views/Dashboard.vue"),
      meta: { requiresAuth: true },
      children: [
        { path: "profile", component: () => import("../views/Profile.vue") },
        { path: "settings", component: () => import("../views/Settings.vue") },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});

// 路由守卫
router.beforeEach((to, from) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: "login" };
  }
});

export default router;
```

```vue
<!-- 使用路由 -->
<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const userId = route.params.id;
function goToUser(id: number) {
  router.push({ name: "user", params: { id } });
}
</script>

<template>
  <nav>
    <RouterLink to="/">首页</RouterLink>
    <RouterLink to="/dashboard">控制台</RouterLink>
  </nav>
  <RouterView />
</template>
```

## 5. 状态管理 (Pinia)

```typescript
// stores/counter.ts
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useCounterStore = defineStore("counter", () => {
  const count = ref(0);
  const doubleCount = computed(() => count.value * 2);

  function increment() { count.value++; }
  function decrement() { count.value--; }

  return { count, doubleCount, increment, decrement };
});
```

```vue
<script setup lang="ts">
import { useCounterStore } from "@/stores/counter";

const counter = useCounterStore();
</script>

<template>
  <div>
    <p>Count: {{ counter.count }}</p>
    <p>Double: {{ counter.doubleCount }}</p>
    <button @click="counter.increment()">+1</button>
  </div>
</template>
```

## 6. 最佳实践

| 实践 | 说明 |
|------|------|
| 使用 `<script setup>` | 更简洁的语法，更好的类型推断 |
| Composables 复用逻辑 | 提取可复用的状态逻辑到独立函数 |
| 使用 TypeScript | 完整的类型安全支持 |
| 异步组件 + 路由懒加载 | `defineAsyncComponent` 和动态 `import` |
| Props 校验 | 使用 TypeScript 接口定义 Props 类型 |
| 使用 Pinia | 官方推荐的状态管理方案 |

## 相关页面

- [[TypeScript开发指南]] - TypeScript 类型系统
- [[React开发指南]] - React 框架对比
- [[设计模式进阶]] - 前端常用设计模式

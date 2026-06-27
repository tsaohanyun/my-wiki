---
title: TypeScript开发指南
aliases:
  - TypeScript指南
  - TS开发指南
tags:
  - TypeScript
  - 类型系统
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

# TypeScript开发指南

TypeScript 是 JavaScript 的超集，添加了可选的静态类型和基于类的面向对象编程。

## 1. 基础语法

### 基本类型

```typescript
// 原始类型
let isDone: boolean = false;
let decimal: number = 6;
let color: string = "blue";
let list: number[] = [1, 2, 3];
let tuple: [string, number] = ["hello", 10];

// 枚举
enum Direction {
  Up = "UP",
  Down = "DOWN",
  Left = "LEFT",
  Right = "RIGHT",
}

// 特殊类型
let notSure: unknown = 4;
let anything: any = "could be anything";
let nothing: void = undefined;
let never: never; // 永远不会到达的类型
```

### 变量声明

```typescript
const API_URL = "https://api.example.com"; // 不可变
let currentUser: string = "admin";          // 可变

// 解构
const { name, age }: { name: string; age: number } = { name: "Alice", age: 30 };
const [first, ...rest]: number[] = [1, 2, 3, 4];
```

## 2. 类型系统

### 类型别名与联合类型

```typescript
type ID = string | number;
type Status = "active" | "inactive" | "pending";

interface User {
  id: ID;
  name: string;
  status: Status;
}

// 交叉类型
type Admin = User & { permissions: string[] };

// 条件类型
type IsString<T> = T extends string ? true : false;
```

### 类型守卫

```typescript
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function processValue(value: string | number) {
  if (isString(value)) {
    console.log(value.toUpperCase());
  } else {
    console.log(value.toFixed(2));
  }
}
```

## 3. 接口

```typescript
interface Animal {
  name: string;
  age: number;
  speak(): string;
}

interface Flyable {
  fly(): void;
}

// 继承
interface Bird extends Animal, Flyable {
  wingspan: number;
}

// 可选属性和只读属性
interface Config {
  readonly apiKey: string;
  timeout?: number;
  retries?: number;
}

// 索引签名
interface Dictionary<T> {
  [key: string]: T;
}

const colors: Dictionary<string> = {
  red: "#ff0000",
  green: "#00ff00",
};
```

## 4. 泛型

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg;
}

// 泛型接口
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<T>;
  delete(id: string): Promise<void>;
}

// 泛型约束
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// 泛型类
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }
}
```

## 5. 装饰器

```typescript
// 类装饰器
function Logger(prefix: string) {
  return function (constructor: Function) {
    console.log(`${prefix}: ${constructor.name} created`);
  };
}

// 方法装饰器
function Log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${key} with`, args);
    return original.apply(this, args);
  };
  return descriptor;
}

// 属性装饰器
function Validate(target: any, key: string) {
  let value = target[key];
  const getter = () => value;
  const setter = (newVal: any) => {
    if (!newVal) throw new Error(`${key} cannot be empty`);
    value = newVal;
  };
  Object.defineProperty(target, key, { get: getter, set: setter });
}

@Logger("Service")
class UserService {
  @Validate
  name: string = "";

  @Log
  getUser(id: string): string {
    return `User ${id}`;
  }
}
```

## 6. 最佳实践

| 实践 | 说明 |
|------|------|
| 启用 `strict` 模式 | `tsconfig.json` 中设置 `"strict": true` |
| 避免使用 `any` | 使用 `unknown` 替代，配合类型守卫 |
| 使用 `readonly` | 防止意外修改 |
| 善用类型推断 | 不必处处标注类型 |
| 使用 `satisfies` | TypeScript 4.9+，验证类型但保留推断 |

```json
// tsconfig.json 推荐配置
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

## 相关页面

- [[React开发指南]] - TypeScript + React 开发
- [[Vue开发指南]] - TypeScript + Vue 开发
- [[设计模式进阶]] - 设计模式的 TypeScript 实现

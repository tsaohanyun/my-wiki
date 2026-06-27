---
title: React开发指南
aliases:
  - React指南
  - React.js开发
tags:
  - React
  - Hooks
  - 前端
  - 状态管理
  - 编程基础
type: wiki
status: published
created: 2025-01-01
updated: 2025-01-01
source: AI-Agent知识库
difficulty: intermediate
project: AI-Agent
---

# React开发指南

React 是一个用于构建用户界面的 JavaScript 库，采用组件化和声明式编程范式。

## 1. 组件

### 函数组件

```tsx
// 基础组件
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary";
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  variant = "primary",
  disabled = false,
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
};
```

### 组件组合

```tsx
interface CardProps {
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, children, footer }) => (
  <div className="card">
    <div className="card-header">
      <h2>{title}</h2>
    </div>
    <div className="card-body">{children}</div>
    {footer && <div className="card-footer">{footer}</div>}
  </div>
);

// 使用
const App = () => (
  <Card title="用户信息" footer={<span>更新时间: 2025</span>}>
    <p>这里是内容</p>
  </Card>
);
```

## 2. Hooks

### useState & useEffect

```tsx
import { useState, useEffect } from "react";

interface User {
  id: number;
  name: string;
  email: string;
}

const UserProfile: React.FC<{ userId: number }> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchUser = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/users/${userId}`);
        if (!res.ok) throw new Error("Failed to fetch");
        const data = await res.json();
        if (!cancelled) {
          setUser(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchUser();
    return () => { cancelled = true; }; // 清理函数
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return null;

  return <div>{user.name} ({user.email})</div>;
};
```

### 自定义 Hook

```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// 使用
const [theme, setTheme] = useLocalStorage("theme", "light");
```

### useMemo & useCallback

```tsx
const ExpensiveList: React.FC<{ items: string[]; filter: string }> = ({
  items,
  filter,
}) => {
  const filtered = useMemo(
    () => items.filter((item) => item.includes(filter)),
    [items, filter]
  );

  const handleClick = useCallback((item: string) => {
    console.log("Clicked:", item);
  }, []);

  return (
    <ul>
      {filtered.map((item) => (
        <li key={item} onClick={() => handleClick(item)}>
          {item}
        </li>
      ))}
    </ul>
  );
};
```

### useRef

```tsx
const TextInputWithFocus: React.FC = () => {
  const inputRef = useRef<HTMLInputElement>(null);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>聚焦</button>
    </>
  );
};
```

## 3. 状态管理

### Context API

```tsx
interface AuthState {
  user: { name: string; email: string } | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthState["user"]>(null);

  const login = async (email: string, password: string) => {
    const res = await fetch("/api/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    setUser(data.user);
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
```

### useReducer

```tsx
type Action =
  | { type: "ADD"; payload: string }
  | { type: "REMOVE"; payload: number }
  | { type: "TOGGLE"; payload: number };

interface TodoState {
  todos: { text: string; done: boolean }[];
}

function todoReducer(state: TodoState, action: Action): TodoState {
  switch (action.type) {
    case "ADD":
      return { todos: [...state.todos, { text: action.payload, done: false }] };
    case "REMOVE":
      return { todos: state.todos.filter((_, i) => i !== action.payload) };
    case "TOGGLE":
      return {
        todos: state.todos.map((todo, i) =>
          i === action.payload ? { ...todo, done: !todo.done } : todo
        ),
      };
  }
}

const TodoApp: React.FC = () => {
  const [state, dispatch] = useReducer(todoReducer, { todos: [] });
  // dispatch({ type: "ADD", payload: "Learn React" })
};
```

## 4. 路由 (React Router v6)

```tsx
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useParams,
  useNavigate,
  Navigate,
} from "react-router-dom";

const Layout: React.FC = () => (
  <div>
    <nav>
      <Link to="/">首页</Link>
      <Link to="/about">关于</Link>
      <Link to="/users">用户</Link>
    </nav>
    <Outlet /> {/* 子路由渲染位置 */}
  </div>
);

const UserProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  return (
    <div>
      <h1>User {id}</h1>
      <button onClick={() => navigate("/")}>返回首页</button>
    </div>
  );
};

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="users" element={<Users />}>
          <Route path=":id" element={<UserProfile />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  </BrowserRouter>
);
```

## 5. 最佳实践

| 实践 | 说明 |
|------|------|
| 组件拆分 | 单一职责，每个组件做一件事 |
| 避免内联函数 | 对性能敏感场景使用 `useCallback` |
| 使用 TypeScript | 提供完整的类型安全 |
| 状态就近管理 | 状态放在需要它的最近父组件 |
| 使用 `key` | 列表渲染必须提供稳定的 `key` |
| 错误边界 | 使用 `ErrorBoundary` 捕获渲染错误 |
| 懒加载 | 使用 `React.lazy` + `Suspense` 按需加载 |

## 相关页面

- [[TypeScript开发指南]] - TypeScript 类型系统
- [[Vue开发指南]] - Vue 框架对比
- [[设计模式进阶]] - 设计模式在 React 中的应用

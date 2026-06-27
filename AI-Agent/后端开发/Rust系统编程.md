---
title: Rust 系统编程
aliases:
  - Rust编程
  - Rust语言
  - Rust所有权
tags:
  - rust
  - systems-programming
  - ownership
  - concurrency
  - async
  - macros
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: AI-Agent Wiki
difficulty: advanced
project: AI-Agent
---

# Rust 系统编程

## 概述

Rust 是一门追求**安全**、**并发**和**高性能**的系统编程语言。它通过所有权系统在编译期消除内存安全问题（空指针、悬垂引用、数据竞争），同时不需要垃圾回收器。本文覆盖所有权、借用、生命周期、并发、异步编程和宏。

---

## 1. 所有权（Ownership）

### 1.1 三大规则

1. **每个值有且仅有一个所有者**
2. **当所有者离开作用域，值被自动释放**
3. **赋值或传参时所有权转移（Move）**

```rust
fn main() {
    // String 分配在堆上，s 拥有该数据
    let s1 = String::from("hello");
    let s2 = s1; // 所有权从 s1 转移到 s2

    // println!("{}", s1);  // 编译错误！s1 已被 move，不可再使用
    println!("{}", s2);     // 正确

    // 基本类型（i32, f64, bool 等）实现 Copy trait，赋值时复制而非 move
    let x = 42;
    let y = x;
    println!("x = {}, y = {}", x, y); // 都可用
}
```

### 1.2 函数与所有权

```rust
fn take_ownership(s: String) {
    println!("获取所有权: {}", s);
} // s 离开作用域，String 的内存被释放

fn make_copy(n: i32) {
    println!("复制值: {}", n);
}

fn give_back() -> String {
    String::from("returned")
}

fn main() {
    let s = String::from("hello world");
    take_ownership(s);
    // println!("{}", s);  // 错误！所有权已转移

    let num = 100;
    make_copy(num);
    println!("num 仍可用: {}", num); // 正确，i32 是 Copy 类型

    let returned = give_back();
    println!("收回了所有权: {}", returned);
}
```

### 1.3 深拷贝

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1.clone(); // 显式深拷贝
    println!("s1 = {}, s2 = {}", s1, s2); // 两者都可用
}
```

---

## 2. 借用与引用（Borrowing & References）

### 2.1 不可变引用

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
} // s 是引用，不拥有数据，不释放

fn main() {
    let s = String::from("hello");
    let len = calculate_length(&s); // 借用
    println!("'{}' 的长度是 {}", s, len); // s 仍然可用
}
```

### 2.2 可变引用

```rust
fn push_world(s: &mut String) {
    s.push_str(", world");
}

fn main() {
    let mut s = String::from("hello");
    push_world(&mut s);
    println!("{}", s); // "hello, world"
}
```

### 2.3 借用规则

| 规则 | 说明 |
|------|------|
| 同一时刻 | 可以有**多个不可变引用** `&T` |
| 同一时刻 | 可以有**一个可变引用** `&mut T` |
| 互斥 | **可变引用与不可变引用不能同时存在** |
| 作用域 | 引用的生命周期不能超过被引用者的生命周期 |

```rust
fn main() {
    let mut s = String::from("hello");

    let r1 = &s;      // 不可变借用
    let r2 = &s;      // 不可变借用（可以多个）
    println!("{} {}", r1, r2); // 最后一次使用 r1/r2 的位置

    let r3 = &mut s;  // 可变借用（r1/r2 已不再使用，所以合法）
    r3.push_str("!");
    println!("{}", r3);
}
```

### 2.4 悬垂引用（Dangling Reference）预防

```rust
// 编译器会阻止以下代码：
// fn dangle() -> &String {
//     let s = String::from("hello");
//     &s  // 错误！s 在函数结束时被释放，引用悬垂
// }

// 正确做法：返回所有权
fn no_dangle() -> String {
    let s = String::from("hello");
    s // 转移所有权给调用者
}
```

---

## 3. 生命周期（Lifetimes）

生命周期标注告诉编译器引用之间的关系，确保引用不会比被引用者活得更久。

### 3.1 函数中的生命周期

```rust
// 'a 表示返回值的生命周期与 x、y 中较短的那个一致
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn main() {
    let s1 = String::from("long string");
    let result;
    {
        let s2 = String::from("short");
        result = longest(s1.as_str(), s2.as_str());
        println!("最长的: {}", result); // 合法：result 在 s2 仍有效时使用
    }
    // println!("{}", result); // 错误！s2 已离开作用域，result 可能悬垂
}
```

### 3.2 结构体中的生命周期

```rust
// Examiner 持有对 text 的引用，不能比 text 活得长
struct TextExaminer<'a> {
    text: &'a str,
}

impl<'a> TextExaminer<'a> {
    fn new(text: &'a str) -> Self {
        TextExaminer { text }
    }

    fn first_word(&self) -> &str {
        // 返回值生命周期与 &self 相同（编译器自动推断）
        match self.text.split_whitespace().next() {
            Some(word) => word,
            None => "",
        }
    }

    fn word_count(&self) -> usize {
        self.text.split_whitespace().count()
    }
}

fn main() {
    let text = String::from("hello rust world");
    let examiner = TextExaminer::new(&text);
    println!("第一个词: {}", examiner.first_word());
    println!("词数: {}", examiner.word_count());
}
```

### 3.3 静态生命周期

```rust
// 'static 表示引用在整个程序运行期间有效
fn main() {
    let s: &'static str = "这是一个字符串字面量"; // 所有字面量都是 'static
    println!("{}", s);
}
```

### 3.4 生命周期省略规则

编译器在以下三种模式下自动推断生命周期（无需显式标注）：

1. 每个引用参数有自己的生命周期
2. 如果只有一个输入生命周期参数，它被赋给所有输出引用
3. 如果有 `&self`/`&mut self`，`self` 的生命周期被赋给所有输出引用

```rust
// 省略标注 —— 编译器自动推断为：
// fn first_word<'a>(s: &'a str) -> &'a str {
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &byte) in bytes.iter().enumerate() {
        if byte == b' ' {
            return &s[0..i];
        }
    }
    s
}
```

---

## 4. 并发编程

### 4.1 线程

```rust
use std::thread;
use std::time::Duration;

fn main() {
    // 创建线程
    let handle = thread::spawn(|| {
        for i in 1..=5 {
            println!("子线程: {}", i);
            thread::sleep(Duration::from_millis(50));
        }
        "子线程返回值"
    });

    for i in 1..=3 {
        println!("主线程: {}", i);
        thread::sleep(Duration::from_millis(50));
    }

    // 等待子线程结束并获取返回值
    let result = handle.join().unwrap();
    println!("线程返回: {}", result);
}
```

### 4.2 Move 闭包

```rust
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];

    let handle = thread::spawn(move || {
        // move 关键字强制闭包获取 data 的所有权
        println!("线程中访问 data: {:?}", data);
    });

    handle.join().unwrap();
}
```

### 4.3 消息传递

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    // 多生产者
    let tx2 = tx.clone();

    thread::spawn(move || {
        let msgs = vec!["hello", "from", "thread1"];
        for msg in msgs {
            tx.send(msg).unwrap();
            thread::sleep(Duration::from_millis(100));
        }
    });

    thread::spawn(move || {
        let msgs = vec!["hi", "from", "thread2"];
        for msg in msgs {
            tx2.send(msg).unwrap();
        }
    });

    // 接收端
    for received in rx {
        println!("收到: {}", received);
    }
}
```

### 4.4 共享状态 — Mutex 与 Arc

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // Arc: 原子引用计数（线程安全共享所有权）
    // Mutex: 互斥锁（确保同一时刻只有一个线程访问数据）
    let counter = Arc::new(Mutex::new(0));

    let handles: Vec<_> = (0..10)
        .map(|_| {
            let counter = Arc::clone(&counter);
            thread::spawn(move || {
                let mut num = counter.lock().unwrap();
                *num += 1;
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    println!("最终计数: {}", *counter.lock().unwrap());
}
```

### 4.5 RwLock — 读写锁

```rust
use std::sync::{Arc, RwLock};
use std::thread;

fn main() {
    let data = Arc::new(RwLock::new(vec![1, 2, 3]));

    let read_handle = {
        let data = Arc::clone(&data);
        thread::spawn(move || {
            let r = data.read().unwrap();
            println!("读取数据: {:?}", *r);
        })
    };

    let write_handle = {
        let data = Arc::clone(&data);
        thread::spawn(move || {
            let mut w = data.write().unwrap();
            w.push(4);
            w.push(5);
            println!("写入后: {:?}", *w);
        })
    };

    read_handle.join().unwrap();
    write_handle.join().unwrap();
}
```

---

## 5. 异步编程

### 5.1 async/await 基础

```rust
use tokio;
use std::time::Duration;

#[tokio::main]
async fn main() {
    // 并发执行多个异步任务
    let (r1, r2, r3) = tokio::join!(
        fetch_data("api/users"),
        fetch_data("api/posts"),
        fetch_data("api/comments"),
    );
    println!("结果: {} / {} / {}", r1, r2, r3);
}

async fn fetch_data(endpoint: &str) -> String {
    println!("开始请求 {}...", endpoint);
    tokio::time::sleep(Duration::from_millis(500)).await;
    format!("来自 {} 的响应", endpoint)
}
```

### 5.2 异步 HTTP 服务器

```rust
use axum::{
    routing::{get, post, put, delete},
    extract::{Path, State, Json},
    response::IntoResponse,
    Router,
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use uuid::Uuid;

#[derive(Clone, Serialize, Deserialize)]
struct User {
    id: String,
    name: String,
    email: String,
}

#[derive(Deserialize)]
struct CreateUser {
    name: String,
    email: String,
}

#[derive(Clone)]
struct AppState {
    users: Arc<RwLock<std::collections::HashMap<String, User>>>,
}

#[tokio::main]
async fn main() {
    let state = AppState {
        users: Arc::new(RwLock::new(std::collections::HashMap::new())),
    };

    let app = Router::new()
        .route("/users", get(list_users).post(create_user))
        .route("/users/:id", get(get_user).put(update_user).delete(delete_user))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("服务器启动: http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}

async fn list_users(State(state): State<AppState>) -> impl IntoResponse {
    let users = state.users.read().await;
    let list: Vec<&User> = users.values().collect();
    Json(list)
}

async fn get_user(
    Path(id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<User>, StatusCode> {
    let users = state.users.read().await;
    users.get(&id)
        .map(|u| Json(u.clone()))
        .ok_or(StatusCode::NOT_FOUND)
}

async fn create_user(
    State(state): State<AppState>,
    Json(payload): Json<CreateUser>,
) -> impl IntoResponse {
    let user = User {
        id: Uuid::new_v4().to_string(),
        name: payload.name,
        email: payload.email,
    };
    {
        let mut users = state.users.write().await;
        users.insert(user.id.clone(), user.clone());
    }
    (StatusCode::CREATED, Json(user))
}

async fn delete_user(
    Path(id): Path<String>,
    State(state): State<AppState>,
) -> StatusCode {
    let mut users = state.users.write().await;
    if users.remove(&id).is_some() {
        StatusCode::NO_CONTENT
    } else {
        StatusCode::NOT_FOUND
    }
}
```

### 5.3 异步数据库（sqlx）

```rust
use sqlx::postgres::PgPoolOptions;
use sqlx::FromRow;

#[derive(Debug, FromRow)]
struct User {
    id: i32,
    name: String,
    email: String,
}

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    let pool = PgPoolOptions::new()
        .max_connections(10)
        .connect("postgres://user:pass@localhost/mydb")
        .await?;

    // 查询多行
    let users: Vec<User> = sqlx::query_as("SELECT id, name, email FROM users")
        .fetch_all(&pool)
        .await?;
    for user in &users {
        println!("{:?}", user);
    }

    // 参数化查询（防注入）
    let user: User = sqlx::query_as(
        "SELECT id, name, email FROM users WHERE email = $1"
    )
    .bind("test@example.com")
    .fetch_one(&pool)
    .await?;

    // 插入
    sqlx::query("INSERT INTO users (name, email) VALUES ($1, $2)")
        .bind("Alice")
        .bind("alice@example.com")
        .execute(&pool)
        .await?;

    Ok(())
}
```

---

## 6. 宏（Macros）

### 6.1 声明宏

```rust
// vec! 宏的简化实现
macro_rules! my_vec {
    // 匹配空
    () => { Vec::new() };
    // 匹配 $(...),* —— 逗号分隔的重复
    ($($x:expr),*) => {{
        let mut v = Vec::new();
        $( v.push($x); )*
        v
    }};
    // 支持尾部逗号
    ($($x:expr,)*) => {{
        my_vec!($($x),*)
    }};
}

fn main() {
    let v1 = my_vec!();
    let v2 = my_vec!(1, 2, 3);
    let v3 = my_vec![1, 2, 3,];
    println!("{:?} {:?} {:?}", v1, v2, v3);
}
```

### 6.2 自定义 derive 宏

```rust
// Cargo.toml: proc-macro = true
// 在单独 crate 中实现

// my_derive/src/lib.rs
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.name;
    let builder_name = format!("{}Builder", name);
    let builder_ident = syn::Ident::new(&builder_name, name.span());

    let fields = match &input.data {
        syn::Data::Struct(syn::DataStruct {
            fields: syn::Fields::Named(fields),
            ..
        }) => &fields.named,
        _ => panic!("Builder 只支持命名字段的结构体"),
    };

    let field_names: Vec<_> = fields.iter().map(|f| &f.ident).collect();
    let field_types: Vec<_> = fields.iter().map(|f| &f.ty).collect();

    let expanded = quote! {
        pub struct #builder_ident {
            #(#field_names: Option<#field_types>),*
        }

        impl #builder_ident {
            #(pub fn #field_names(mut self, val: #field_types) -> Self {
                self.#field_names = Some(val);
                self
            })*

            pub fn build(self) -> Result<#name, String> {
                Ok(#name {
                    #(#field_names: self.#field_names.ok_or_else(|| {
                        format!("字段 {:?} 未设置", stringify!(#field_names))
                    })?),*
                })
            }
        }

        impl #name {
            pub fn builder() -> #builder_ident {
                #builder_ident {
                    #(#field_names: None),*
                }
            }
        }
    };

    TokenStream::from(expanded)
}

// 使用：
// #[derive(Builder)]
// struct User { name: String, email: String }
// let user = User::builder().name("Alice".into()).email("a@b.com".into()).build().unwrap();
```

---

## 7. 最佳实践

### 7.1 设计原则

- ✅ **优先使用借用而非所有权转移**，避免不必要的 clone
- ✅ **用 `&str` 代替 `&String`** 作为函数参数（更通用）
- ✅ **用 `&[T]` 代替 `&Vec<T>`** 作为函数参数
- ✅ **合理使用 `Box<T>`** 递归类型或超大对象
- ✅ **使用 `Rc<T>` / `Arc<T>`** 共享只读 / 跨线程共享
- ✅ **使用 `enum` + `match`** 代替继承多态
- ✅ **使用 `Option` / `Result`** 代替 null 和异常
- ✅ **使用 `?` 操作符**传播错误
- ✅ **为公开 API 编写文档注释** `///`
- ❌ 不要滥用 `unsafe`
- ❌ 不要在不需要时使用 `clone()`
- ❌ 不要用 `unwrap()` / `expect()` 处理可恢复错误

### 7.2 Cargo 工程化

```toml
[package]
name = "my-project"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1", features = ["full"] }
axum = "0.7"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.7", features = ["runtime-tokio", "postgres", "uuid"] }
uuid = { version = "1", features = ["v4", "serde"] }
tracing = "0.1"
tracing-subscriber = "0.3"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
```

### 7.3 错误处理模式

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("数据库错误: {0}")]
    Database(#[from] sqlx::Error),

    #[error("资源未找到: {0}")]
    NotFound(String),

    #[error("参数无效: {0}")]
    InvalidInput(String),

    #[error("认证失败")]
    Unauthorized,

    #[error("内部错误: {0}")]
    Internal(#[from] Box<dyn std::error::Error + Send + Sync>),
}

pub type AppResult<T> = Result<T, AppError>;

// 使用
async fn get_user(pool: &sqlx::PgPool, id: i32) -> AppResult<User> {
    let user = sqlx::query_as("SELECT * FROM users WHERE id = $1")
        .bind(id)
        .fetch_optional(pool)
        .await?
        .ok_or_else(|| AppError::NotFound(format!("用户 #{}", id)))?;
    Ok(user)
}
```

---

## 8. 相关页面

- [[Java Spring Boot 开发]]
- [[Node.js 后端开发]]
- [[Python 异步编程]]
- [[gRPC 服务开发]]
- [[内存安全与垃圾回收]]
- [[并发编程模型对比]]
- [[系统编程语言对比]]

---
title: Rust高级编程
aliases:
  - Rust进阶
  - Rust Advanced Programming
tags:
  - rust
  - 系统编程
  - 内存安全
  - 并发
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: Rust官方文档 + 社区最佳实践
difficulty: advanced
project: AI-Agent-Wiki
---

# Rust 高级编程

> Rust 是一门注重内存安全、并发安全和性能的系统编程语言。本文涵盖 trait 系统、生命周期、智能指针、unsafe、过程宏、async/await 等高级主题。

---

## 目录

- [1. Trait 系统](#1-trait-系统)
- [2. 生命周期](#2-生命周期)
- [3. 智能指针](#3-智能指针)
- [4. Unsafe Rust](#4-unsafe-rust)
- [5. 过程宏](#5-过程宏)
- [6. Async / Await](#6-async--await)
- [7. 最佳实践](#7-最佳实践)
- [8. 相关页面](#8-相关页面)

---

## 1. Trait 系统

Trait 是 Rust 中对行为进行抽象的核心机制，类似于 Java/Go 中的 Interface，但更强大。

### 1.1 定义与实现

```rust
// 定义一个 Trait
trait Summary {
    fn summarize(&self) -> String;

    // 默认实现
    fn summarize_author(&self) -> String {
        String::from("Unknown Author")
    }
}

struct Article {
    title: String,
    author: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{} - by {}", self.title, self.author)
    }

    // 覆盖默认实现
    fn summarize_author(&self) -> String {
        self.author.clone()
    }
}
```

### 1.2 Trait 作为参数与返回值

```rust
// Trait Bound 语法
fn notify<T: Summary>(item: &T) {
    println!("Breaking: {}", item.summarize());
}

// impl Trait 语法（等价写法）
fn notify_v2(item: &impl Summary) {
    println!("Breaking: {}", item.summarize());
}

// 多个 Trait Bound
fn notify_all<T: Summary + std::fmt::Display>(item: &T) {
    println!("{}: {}", item, item.summarize());
}

// where 子句
fn some_function<T, U>(t: &T, u: &U) -> String
where
    T: Summary + Clone,
    U: std::fmt::Debug,
{
    format!("{:?}", u)
}

// 返回实现了 Trait 的类型
fn create_summary() -> impl Summary {
    Article {
        title: String::from("Hello Rust"),
        author: String::from("Alice"),
        content: String::new(),
    }
}
```

### 1.3 Trait Object 与动态分发

```rust
// 使用 dyn 关键字实现动态分发
fn print_summaries(items: &[Box<dyn Summary>]) {
    for item in items {
        println!("{}", item.summarize());
    }
}

fn main() {
    let articles: Vec<Box<dyn Summary>> = vec![
        Box::new(Article {
            title: String::from("News 1"),
            author: String::from("Bob"),
            content: String::new(),
        }),
    ];
    print_summaries(&articles);
}
```

### 1.4 关联类型

```rust
trait Iterator {
    type Item; // 关联类型

    fn next(&mut self) -> Option<Self::Item>;
}

struct Counter {
    count: u32,
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        if self.count < 5 {
            self.count += 1;
            Some(self.count)
        } else {
            None
        }
    }
}
```

### 1.5 泛型 Trait 与默认泛型类型参数

```rust
// 从右侧融合
trait Add<Rhs = Self> {
    type Output;

    fn add(self, rhs: Rhs) -> Self::Output;
}

#[derive(Debug, Clone, Copy)]
struct Point { x: i32, y: i32 }

impl Add for Point {
    type Output = Point;

    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}
```

### 1.6 Supertrait

```rust
use std::fmt;

// 要求实现者也必须实现 Display
trait OutlinePrint: fmt::Display {
    fn outline_print(&self) {
        let output = self.to_string();
        let len = output.len();
        println!("{} {}", "*".repeat(len + 4), "*");
        println!("* {:^width$} *", output, width = len);
        println!("{} {}", "*".repeat(len + 4), "*");
    }
}
```

### 1.7 Newtype 模式

```rust
// 当外部类型无法直接 impl 时，用 Newtype 包装
struct Wrapper(Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}
```

---

## 2. 生命周期

生命周期（Lifetime）是 Rust 编译器用来确保引用始终有效的机制。

### 2.1 避免悬垂引用

```rust
// 编译器通过生命周期标注确保引用不会失效
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn main() {
    let string1 = String::from("long string");
    let string2 = String::from("short");
    let result = longest(string1.as_str(), string2.as_str());
    println!("Longest: {}", result);
}
```

### 2.2 结构体中的生命周期

```rust
// 结构体中包含引用时必须标注生命周期
struct Excerpt<'a> {
    part: &'a str,
}

impl<'a> Excerpt<'a> {
    // 返回值的生命周期与 part 关联
    fn announce_and_return(&self, announcement: &str) -> &str {
        println!("Attention: {}", announcement);
        self.part
    }
}
```

### 2.3 生命周期省略规则

```rust
// 三条省略规则：
// 1. 每个引用参数获得自己的生命周期
// 2. 如果只有一个输入生命周期参数，它被赋给所有输出
// 3. 如果有 &self 或 &mut self，其生命周期被赋给所有输出

// 编译器自动推断（无需标注）
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}
```

### 2.4 静态生命周期

```rust
// 'static 表示引用在整个程序运行期间有效
let s: &'static str = "I live forever";

// 嵌入到二进制文件中的字符串字面量具有 'static 生命周期
```

### 2.5 泛型 + Trait + 生命周期结合

```rust
use std::fmt::Display;

fn longest_with_announcement<'a, T>(
    x: &'a str,
    y: &'a str,
    ann: T,
) -> &'a str
where
    T: Display,
{
    println!("Announcement! {}", ann);
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

---

## 3. 智能指针

智能指针拥有数据，比普通引用提供更多功能（自动释放、引用计数等）。

### 3.1 `Box<T>` — 堆分配

```rust
fn main() {
    let b = Box::new(5);
    println!("b = {}", b); // 自动解引用

    // 递归类型的典型用法
    #[derive(Debug)]
    enum List {
        Cons(i32, Box<List>),
        Nil,
    }

    let list = List::Cons(1,
        Box::new(List::Cons(2,
            Box::new(List::Cons(3,
                Box::new(List::Nil))))));
    println!("{:?}", list);
}
```

### 3.2 `Rc<T>` — 引用计数（单线程）

```rust
use std::rc::Rc;

fn main() {
    let data = Rc::new(String::from("shared data"));

    let a = Rc::clone(&data);
    let b = Rc::clone(&data);

    println!("count = {}", Rc::strong_count(&data)); // 3
    println!("a = {}, b = {}", a, b);
}
```

### 3.3 `RefCell<T>` — 内部可变性（单线程）

```rust
use std::cell::RefCell;

fn main() {
    let data = RefCell::new(vec![1, 2, 3]);

    // 运行时借用检查
    data.borrow_mut().push(4); // 可变借用
    println!("{:?}", data.borrow()); // 不可变借用
}
```

### 3.4 `Arc<T>` — 原子引用计数（多线程）

```rust
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3]);

    let handles: Vec<_> = (0..3)
        .map(|i| {
            let data = Arc::clone(&data);
            thread::spawn(move || {
                println!("Thread {}: {:?}", i, data);
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }
}
```

### 3.5 `Mutex<T>` / `RwLock<T>` — 线程安全内部可变性

```rust
use std::sync::{Arc, Mutex};

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = std::thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}
```

### 3.6 自定义智能指针 — 实现 `Deref` / `Drop`

```rust
use std::ops::Deref;

struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(x: T) -> MyBox<T> {
        MyBox(x)
    }
}

impl<T> Deref for MyBox<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<T> Drop for MyBox<T> {
    fn drop(&mut self) {
        println!("Dropping MyBox");
    }
}
```

---

## 4. Unsafe Rust

当编译器的安全保证过于保守时，可以使用 `unsafe` 绕过部分检查。

### 4.1 Unsafe 的五项能力

```rust
// 1. 解引用裸指针
let mut num = 5;
let r1 = &num as *const i32;
let r2 = &mut num as *mut i32;
unsafe {
    println!("r1 = {}", *r1);
    *r2 = 10;
}

// 2. 调用不安全函数或方法
unsafe fn dangerous() -> i32 {
    42
}
unsafe {
    let result = dangerous();
    println!("dangerous returned: {}", result);
}

// 3. 访问或修改可变静态变量
static mut COUNTER: u32 = 0;
fn add_to_count(inc: u32) {
    unsafe {
        COUNTER += inc;
    }
}

// 4. 实现不安全 trait
unsafe trait Foo {
    // 方法...
}
unsafe impl Foo for i32 {
    // 实现...
}

// 5. 访问 union 的字段
#[repr(C)]
union MyUnion {
    f1: u32,
    f2: f32,
}
let u = MyUnion { f1: 1 };
unsafe {
    let f = u.f2;
    println!("union field: {}", f);
}
```

### 4.2 FFI（外部函数接口）

```rust
extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("Absolute value of -3: {}", abs(-3));
    }
}

// 从其他语言调用 Rust
#[no_mangle]
pub extern "C" fn call_from_c() {
    println!("Called from C!");
}
```

### 4.3 安全抽象

```rust
// 将 unsafe 封装在安全 API 中
fn split_at_mut(values: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = values.len();
    assert!(mid <= len);

    // 使用 unsafe 来获取两个可变切片（安全编译器无法理解这是安全的）
    let ptr = values.as_mut_ptr();
    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}
```

---

## 5. 过程宏

过程宏（Procedural Macros）允许在编译时生成代码。

### 5.1 三种过程宏类型

#### 派生宏（Derive Macro）

```rust
// 在 hello_macro_derive/src/lib.rs
use proc_macro::TokenStream;
use quote::quote;
use syn;

#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    // 解析 Rust 代码
    let ast = syn::parse(input).unwrap();

    // 生成 trait 实现
    impl_hello_macro(&ast)
}

fn impl_hello_macro(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;
    let gen = quote! {
        impl HelloMacro for #name {
            fn hello_macro() {
                println!("Hello, Macro! My name is {}!", stringify!(#name));
            }
        }
    };
    gen.into()
}
```

#### 属性宏（Attribute Macro）

```rust
#[proc_macro_attribute]
pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {
    // attr: 路由路径
    // item: 函数定义
    // 可以修改或替换函数
    item
}

// 使用
// #[route(GET, "/")]
// fn index() { ... }
```

#### 函数式宏（Function-like Macro）

```rust
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
    // 解析类似 SQL 的语法并生成查询代码
    // ...
    TokenStream::new()
}

// 使用
// let query = sql!(SELECT * FROM users WHERE active = true);
```

### 5.2 声明式宏（macro_rules!）

```rust
#[macro_export]
macro_rules! vec_of {
    ($($x:expr),*) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}

fn main() {
    let v = vec_of![1, 2, 3];
    println!("{:?}", v);
}
```

---

## 6. Async / Await

Rust 的异步编程基于 Future 和零成本抽象，不依赖运行时（需要手动选择如 Tokio）。

### 6.1 基本用法

```rust
use std::time::Duration;

// async fn 返回一个实现了 Future 的匿名类型
async fn do_async() {
    println!("Hello");
    // await 挂起当前任务，不阻塞线程
    tokio::time::sleep(Duration::from_secs(1)).await;
    println!("World");
}
```

### 6.2 Tokio 运行时

```rust
// Cargo.toml: tokio = { version = "1", features = ["full"] }
#[tokio::main]
async fn main() {
    // 创建并发任务
    let handle1 = tokio::spawn(async {
        tokio::time::sleep(Duration::from_millis(100)).await;
        println!("Task 1 done");
    });

    let handle2 = tokio::spawn(async {
        tokio::time::sleep(Duration::from_millis(50)).await;
        println!("Task 2 done");
    });

    // 等待所有任务完成
    let _ = tokio::join!(handle1, handle2);
}
```

### 6.3 并发 vs 串行

```rust
async fn fetch_data(id: u32) -> String {
    tokio::time::sleep(Duration::from_millis(100)).await;
    format!("data-{}", id)
}

// 串行执行（总时间约 300ms）
async fn serial() {
    let a = fetch_data(1).await;
    let b = fetch_data(2).await;
    let c = fetch_data(3).await;
    println!("{}, {}, {}", a, b, c);
}

// 并发执行（总时间约 100ms）
async fn concurrent() {
    let (a, b, c) = tokio::join!(
        fetch_data(1),
        fetch_data(2),
        fetch_data(3),
    );
    println!("{}, {}, {}", a, b, c);
}
```

### 6.4 Channel 通信

```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(32);

    tokio::spawn(async move {
        for i in 0..10 {
            tx.send(i).await.unwrap();
        }
    });

    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }
}
```

### 6.5 Select — 多路复用

```rust
use tokio::select;

#[tokio::main]
async fn main() {
    let (tx1, mut rx1) = mpsc::channel::<String>(10);
    let (tx2, mut rx2) = mpsc::channel::<String>(10);

    tokio::spawn(async move {
        tx1.send("from channel 1".to_string()).await.unwrap();
    });
    tokio::spawn(async move {
        tx2.send("from channel 2".to_string()).await.unwrap();
    });

    loop {
        select! {
            Some(msg) = rx1.recv() => println!("rx1: {}", msg),
            Some(msg) = rx2.recv() => println!("rx2: {}", msg),
            else => break,
        }
    }
}
```

### 6.6 Stream — 异步迭代器

```rust
use tokio_stream::{self as stream, StreamExt};

#[tokio::main]
async fn main() {
    let mut stream = stream::iter(vec![1, 2, 3, 4, 5]);

    while let Some(item) = stream.next().await {
        println!("Item: {}", item);
    }
}
```

### 6.7 Send / Sync 与异步

```rust
use std::rc::Rc;

// Rc 不是 Send，不能跨 await 点使用
// async fn bad() {
//     let rc = Rc::new(5);
//     some_async().await; // 编译错误：Rc 不满足 Send
//     println!("{}", rc);
// }

// 正确做法：使用 Arc
use std::sync::Arc;
async fn good() {
    let arc = Arc::new(5);
    tokio::time::sleep(Duration::from_millis(1)).await;
    println!("{}", arc);
}
```

---

## 7. 最佳实践

### 7.1 通用建议

| 场景 | 推荐 |
|------|------|
| 需要共享只读数据（单线程） | `Rc<T>` |
| 需要共享可变数据（多线程） | `Arc<Mutex<T>>` 或 `Arc<RwLock<T>>` |
| 需要延迟计算 | Iterator / Lazy |
| 动态分发 | `Box<dyn Trait>` |
| 自定义析构 | 实现 `Drop` |
| 类型安全抽象 | Newtype 模式 |

### 7.2 错误处理

```rust
use std::fmt;

// 自定义错误类型
#[derive(Debug)]
enum AppError {
    Io(std::io::Error),
    Parse(std::num::ParseIntError),
    Custom(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            AppError::Io(e) => write!(f, "IO error: {}", e),
            AppError::Parse(e) => write!(f, "Parse error: {}", e),
            AppError::Custom(msg) => write!(f, "Custom error: {}", msg),
        }
    }
}

impl std::error::Error for AppError {}

// From 自动转换
impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::Io(e)
    }
}

// 使用 ? 运算符
fn read_config() -> Result<i32, AppError> {
    let content = std::fs::read_to_string("config.txt")?; // 自动转换为 AppError
    let num: i32 = content.trim().parse().map_err(AppError::Parse)?;
    Ok(num)
}
```

### 7.3 零拷贝与借用

```rust
// 尽量使用 &str 而非 String，避免不必要的分配
fn process(data: &str) -> &str {
    // 零拷贝处理
    &data[..data.len().min(10)]
}
```

### 7.4 Clippy 与格式化

```bash
# 代码检查
cargo clippy -- -W clippy::all

# 自动格式化
cargo fmt

# 安全审计
cargo audit
```

---

## 8. 相关页面

- [[Kotlin开发指南]] — Kotlin 协程与 Rust async/await 的对比
- [[C++现代特性]] — 智能指针对比（unique_ptr vs Box、shared_ptr vs Arc）
- [[函数式编程]] — Rust 的 Iterator trait 与函数式概念
- [[Rust异步编程]] — 深入 async 生态
- [[系统编程基础]] — 内存模型与并发

---

## 参考资源

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust By Example](https://doc.rust-lang.org/rust-by-example/)
- [Rust Async Book](https://rust-lang.github.io/async-book/)
- [Tokio Tutorial](https://tokio.rs/tokio/tutorial)

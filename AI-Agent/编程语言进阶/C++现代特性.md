---
title: C++现代特性
aliases:
  - C++进阶
  - Modern C++
  - C++17/20/23
tags:
  - cpp
  - cpp17
  - cpp20
  - cpp23
  - 系统编程
  - 模板元编程
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: ISO C++标准 + cppreference
difficulty: advanced
project: AI-Agent-Wiki
---

# C++ 现代特性

> 本文涵盖 C++17/20/23 的现代特性，包括智能指针、移动语义、概念（Concepts）、协程（Coroutines）、模块（Modules）等核心主题。

---

## 目录

- [1. C++17 新特性](#1-c17-新特性)
- [2. C++20 新特性](#2-c20-新特性)
- [3. C++23 新特性](#3-c23-新特性)
- [4. 智能指针](#4-智能指针)
- [5. 移动语义](#5-移动语义)
- [6. 概念（Concepts）](#6-概念concepts)
- [7. 协程（Coroutines）](#7-协程coroutines)
- [8. 模块（Modules）](#8-模块modules)
- [9. 最佳实践](#9-最佳实践)
- [10. 相关页面](#10-相关页面)

---

## 1. C++17 新特性

### 1.1 结构化绑定

```cpp
#include <tuple>
#include <map>
#include <string>
#include <iostream>

int main() {
    // 解构 pair / tuple
    auto [x, y] = std::make_pair(1, 2.5);
    std::cout << x << ", " << y << '\n'; // 1, 2.5

    // 解构 map 元素
    std::map<std::string, int> m{{"a", 1}, {"b", 2}};
    for (const auto& [key, value] : m) {
        std::cout << key << " = " << value << '\n';
    }

    // 解构结构体
    struct Point { double x, y; };
    Point p{3.0, 4.0};
    auto& [px, py] = p;
    std::cout << px << ", " << py << '\n'; // 3, 4

    return 0;
}
```

### 1.2 `if constexpr`

```cpp
#include <type_traits>

// 编译时条件分支
template<typename T>
auto get_value(T t) {
    if constexpr (std::is_pointer_v<T>) {
        return *t;  // 如果是指针，解引用
    } else {
        return t;   // 否则直接返回
    }
}

// 避免使用 SFINAE / tag dispatch
template<typename T>
void process(T value) {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "Integral: " << value << '\n';
    } else if constexpr (std::is_floating_point_v<T>) {
        std::cout << "Float: " << value << '\n';
    } else {
        std::cout << "Other type\n";
    }
}
```

### 1.3 `std::optional` / `std::variant` / `std::any`

```cpp
#include <optional>
#include <variant>
#include <any>
#include <string>
#include <iostream>

// std::optional: 可能有值也可能没有
std::optional<int> find_even(const std::vector<int>& v) {
    for (int x : v) {
        if (x % 2 == 0) return x;
    }
    return std::nullopt;
}

// std::variant: 类型安全的 union
using Result = std::variant<int, std::string, double>;

// std::any: 任意类型
int main() {
    auto result = find_even({1, 3, 5, 8});
    if (result) {
        std::cout << "Found: " << *result << '\n'; // 8
    }

    Result r = 42;
    r = "hello"s;
    r = 3.14;

    // visit: 模式匹配 variant
    std::visit([](auto&& arg) {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, int>)
            std::cout << "int: " << arg << '\n';
        else if constexpr (std::is_same_v<T, std::string>)
            std::cout << "string: " << arg << '\n';
        else
            std::cout << "double: " << arg << '\n';
    }, r);

    // std::any
    std::any a = 42;
    a = std::string("hello");
    std::cout << std::any_cast<std::string>(a) << '\n';

    return 0;
}
```

### 1.4 `std::string_view`

```cpp
#include <string_view>

// 轻量级、非拥有的字符串视图（零拷贝）
void process(std::string_view sv) {
    std::cout << sv.substr(0, 5) << '\n';
}

int main() {
    std::string s = "Hello, World";
    process(s);             // 从 std::string 构造
    process("literal");     // 从 C 字符串构造
    process({s.data() + 7, 5}); // 子串

    return 0;
}
```

### 1.5 并行 STL

```cpp
#include <algorithm>
#include <execution>
#include <vector>

int main() {
    std::vector<int> v(1'000'000);
    std::iota(v.begin(), v.end(), 0);

    // 并行排序
    std::sort(std::execution::par, v.begin(), v.end());

    // 并行 for_each
    std::for_each(std::execution::par_unseq, v.begin(), v.end(),
        [](int& x) { x *= 2; });

    // 执行策略:
    // seq:          顺序执行
    // par:          并行执行（多线程）
    // par_unseq:    并行+向量化（SIMD）

    return 0;
}
```

### 1.6 折叠表达式

```cpp
#include <iostream>

// 一元右折叠
template<typename... Args>
void print_all(Args... args) {
    ((std::cout << args << ' '), ...); // 逗号折叠
}

// 二元右折叠: 求和
template<typename... Args>
auto sum(Args... args) {
    return (args + ...); // 等价于 (args[0] + (args[1] + ... + args[n]))
}

// 二元左折叠: 带初始值
template<typename... Args>
auto sum_with_init(Args... args) {
    return (0 + ... + args); // 从 0 开始累加
}

int main() {
    print_all(1, 2.5, "hello", 'x'); // 1 2.5 hello x
    std::cout << sum(1, 2, 3, 4, 5) << '\n'; // 15
    return 0;
}
```

---

## 2. C++20 新特性

### 2.1 Concepts（概念）

详见 [第 6 节](#6-概念concepts)。

### 2.2 Ranges（范围）

```cpp
#include <ranges>
#include <vector>
#include <algorithm>
#include <iostream>

int main() {
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // 管道式操作（延迟计算）
    auto result = v
        | std::views::filter([](int x) { return x % 2 == 0; })  // 过滤偶数
        | std::views::transform([](int x) { return x * x; })    // 平方
        | std::views::take(3);                                   // 取前3个

    for (int x : result) {
        std::cout << x << ' '; // 4 16 36
    }
    std::cout << '\n';

    // iota: 无限序列
    auto squares = std::views::iota(1)
        | std::views::transform([](int x) { return x * x; })
        | std::views::take(5);

    for (int x : squares) {
        std::cout << x << ' '; // 1 4 9 16 25
    }
    std::cout << '\n';

    return 0;
}
```

### 2.3 协程（Coroutines）

详见 [第 7 节](#7-协程coroutines)。

### 2.4 模块（Modules）

详见 [第 8 节](#8-模块modules)。

### 2.5 `consteval` / `constinit`

```cpp
// consteval: 必须在编译时求值
consteval int compile_time_square(int x) {
    return x * x;
}

// constexpr: 可以在编译时或运行时求值
constexpr int maybe_square(int x) {
    return x * x;
}

// constinit: 必须在编译时初始化，但可以运行时修改
constinit int global_value = compile_time_square(5); // 25

int main() {
    constexpr int a = maybe_square(5); // 编译时
    int b = maybe_square(6);           // 运行时

    static_assert(compile_time_square(4) == 16);
    static_assert(a == 25);

    // int x = 0;
    // compile_time_square(x); // 编译错误: x 不是常量表达式

    return 0;
}
```

### 2.6 三路比较运算符 (`<=>`)

```cpp
#include <compare>
#include <string>

class Person {
public:
    std::string name;
    int age;

    // 三路比较运算符: 一次性生成所有比较运算符
    auto operator<=>(const Person&) const = default;

    // 自定义三路比较
    std::strong_ordering operator<=>(const Person& other) const {
        if (auto cmp = name <=> other.name; cmp != 0) return cmp;
        return age <=> other.age;
    }
};

int main() {
    Person a{"Alice", 30};
    Person b{"Bob", 25};

    // 自动获得 <, >, <=, >=, ==, !=
    bool result = (a < b); // 比较 name，如果相同则比较 age
    return 0;
}
```

### 2.7 `std::format`

```cpp
#include <format>
#include <iostream>

int main() {
    // Python 风格的格式化（取代 printf / iostream 复杂语法）
    std::string s1 = std::format("Hello, {}!", "World");
    std::string s2 = std::format("{1} before {0}", "A", "B");
    std::string s3 = std::format("Pi ≈ {:.2f}", 3.14159);
    std::string s4 = std::format("Hex: {:x}, Binary: {:b}", 255, 10);

    std::cout << s1 << '\n'; // Hello, World!
    std::cout << s2 << '\n'; // B before A
    std::cout << s3 << '\n'; // Pi ≈ 3.14
    std::cout << s4 << '\n'; // Hex: ff, Binary: 1010

    return 0;
}
```

---

## 3. C++23 新特性

### 3.1 `std::expected`

```cpp
#include <expected>
#include <string>
#include <iostream>

// 类似 Rust 的 Result<T, E>
std::expected<int, std::string> parse_int(std::string_view sv) {
    try {
        return std::stoi(std::string(sv));
    } catch (...) {
        return std::unexpected("Parse failed");
    }
}

int main() {
    auto result = parse_int("42");
    if (result.has_value()) {
        std::cout << "Value: " << *result << '\n';
    } else {
        std::cout << "Error: " << result.error() << '\n';
    }

    // monadic 操作
    auto transformed = parse_int("10")
        .and_then([](int x) -> std::expected<int, std::string> {
            return x * 2;
        })
        .transform([](int x) { return std::to_string(x); });

    if (transformed) {
        std::cout << *transformed << '\n'; // "20"
    }

    return 0;
}
```

### 3.2 `std::print`

```cpp
#include <print>
#include <vector>

int main() {
    // 直接打印，无需 std::format + std::cout
    std::println("Hello, {}!", "World"); // 自动换行
    std::print("No newline: {}", 42);

    // 打印容器
    std::vector<int> v{1, 2, 3};
    std::println("{}", v); // [1, 2, 3] (部分实现)

    return 0;
}
```

### 3.3 Deducing `this`

```cpp
#include <iostream>

// 显式传递 this 参数，实现 CRTP 的简化
struct Node {
    int value;

    // this 现在是显式参数
    template<typename Self>
    constexpr auto&& get_value(this Self&& self) {
        return std::forward<Self>(self).value;
    }

    // 链式调用（Fluent Interface）
    template<typename Self>
    constexpr auto& set_value(this Self&& self, int v) {
        self.value = v;
        return self;
    }
};

int main() {
    Node n{42};
    std::cout << n.get_value() << '\n'; // 42

    return 0;
}
```

### 3.4 `std::span`

```cpp
#include <span>
#include <vector>
#include <array>
#include <iostream>

// 类似 string_view，但是用于任意连续内存序列
void process(std::span<int> data) {
    for (auto& x : data) {
        x *= 2;
    }
}

int main() {
    // 从不同来源构造 span
    int arr[] = {1, 2, 3};
    std::vector<int> v = {4, 5, 6};
    std::array<int, 3> a = {7, 8, 9};

    process(arr);
    process(v);
    process(a);

    // 固定大小的 span
    std::span<int, 3> fixed_span{arr};

    // 子视图
    std::span<int> sub = std::span{v}.subspan(1, 2); // {5, 6}

    return 0;
}
```

---

## 4. 智能指针

### 4.1 `std::unique_ptr` — 独占所有权

```cpp
#include <memory>
#include <iostream>

class Resource {
public:
    Resource() { std::cout << "Acquired\n"; }
    ~Resource() { std::cout << "Released\n"; }
    void use() { std::cout << "Using\n"; }
};

void example() {
    // 创建 unique_ptr
    auto ptr = std::make_unique<Resource>();
    ptr->use();

    // 转移所有权（移动语义）
    auto ptr2 = std::move(ptr);
    // ptr 现在为 nullptr

    // 自定义删除器
    auto file_ptr = std::unique_ptr<FILE, decltype(&fclose)>(
        fopen("test.txt", "w"), &fclose);

} // ptr2 自动释放（RAII）
```

### 4.2 `std::shared_ptr` — 共享所有权

```cpp
#include <memory>
#include <iostream>

class Widget {
public:
    Widget(int id) : id_(id) {
        std::cout << "Widget " << id_ << " created\n";
    }
    ~Widget() {
        std::cout << "Widget " << id_ << " destroyed\n";
    }
private:
    int id_;
};

void example() {
    auto p1 = std::make_shared<Widget>(1);

    {
        auto p2 = p1; // 引用计数 +1
        std::cout << "Count: " << p1.use_count() << '\n'; // 2
    } // p2 销毁，引用计数 -1

    std::cout << "Count: " << p1.use_count() << '\n'; // 1
}

// ⚠️ 循环引用问题
void bad_example() {
    struct Node {
        std::shared_ptr<Node> next;
        // 如果两个 Node 互相引用 → 内存泄漏！
    };

    auto a = std::make_shared<Node>();
    auto b = std::make_shared<Node>();
    a->next = b;
    // b->next = a; // 循环引用 → 永不释放
}
```

### 4.3 `std::weak_ptr` — 弱引用

```cpp
#include <memory>
#include <iostream>

void example() {
    auto shared = std::make_shared<int>(42);
    std::weak_ptr<int> weak = shared;

    // 检查是否过期
    if (auto locked = weak.lock()) {
        std::cout << "Value: " << *locked << '\n'; // 42
    }

    shared.reset(); // 释放 shared_ptr

    // weak_ptr 现在已过期
    if (weak.expired()) {
        std::cout << "Resource has been freed\n";
    }
}

// 正确解决循环引用
struct TreeNode {
    std::shared_ptr<TreeNode> parent;  // 或 weak_ptr
    std::vector<std::shared_ptr<TreeNode>> children;

    // 使用 weak_ptr 打破循环
    std::weak_ptr<TreeNode> parent_weak;
};
```

### 4.4 使用建议

```cpp
// ✅ 优先使用 make_unique / make_shared
auto p1 = std::make_unique<int>(42);     // 异常安全
auto p2 = std::make_shared<int>(42);     // 减少内存分配次数

// ❌ 避免
// std::unique_ptr<int> p(new int(42));  // 不异常安全
// std::shared_ptr<int> p(new int(42));  // 两次内存分配

// 使用 unique_ptr 表达工厂模式
class Factory {
public:
    virtual ~Factory() = default;
    virtual std::unique_ptr<Product> create() = 0;
};

// enable_shared_from_this
class Manager : public std::enable_shared_from_this<Manager> {
public:
    std::shared_ptr<Manager> getPtr() {
        return shared_from_this(); // 安全地获取指向自己的 shared_ptr
    }
};
```

---

## 5. 移动语义

### 5.1 右值引用与移动构造

```cpp
#include <utility>
#include <vector>
#include <iostream>

class Buffer {
    size_t size_;
    int* data_;
public:
    // 构造
    explicit Buffer(size_t n) : size_(n), data_(new int[n]()) {
        std::cout << "Construct " << size_ << '\n';
    }

    // 析构
    ~Buffer() {
        delete[] data_;
        if (data_) std::cout << "Destroy " << size_ << '\n';
    }

    // 拷贝构造（深拷贝）
    Buffer(const Buffer& other)
        : size_(other.size_), data_(new int[other.size_]) {
        std::copy(other.data_, other.data_ + size_, data_);
        std::cout << "Copy " << size_ << '\n';
    }

    // 移动构造（浅拷贝 + 置空源对象）
    Buffer(Buffer&& other) noexcept
        : size_(other.size_), data_(other.data_) {
        other.size_ = 0;
        other.data_ = nullptr;
        std::cout << "Move " << size_ << '\n';
    }

    // 拷贝赋值
    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = new int[size_];
            std::copy(other.data_, other.data_ + size_, data_);
        }
        return *this;
    }

    // 移动赋值
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = other.data_;
            other.size_ = 0;
            other.data_ = nullptr;
        }
        return *this;
    }
};

int main() {
    Buffer a(1000);
    Buffer b = std::move(a); // 调用移动构造（避免深拷贝）

    Buffer c(500);
    c = std::move(b);        // 调用移动赋值

    return 0;
}
```

### 5.2 `std::move` 与 `std::forward`

```cpp
#include <utility>
#include <string>

// std::move: 将左值转换为右值引用（无条件转换）
void example_move() {
    std::string s = "Hello";
    std::string moved = std::move(s); // s 现在处于有效但未指定状态
    // s.empty() == true（通常）
}

// std::forward: 完美转发（条件转换）
template<typename T>
void wrapper(T&& arg) {
    // std::forward 保持 arg 的左右值属性
    target(std::forward<T>(arg));
}

void target(int& x)       { std::cout << "lvalue\n"; }
void target(const int& x) { std::cout << "const lvalue\n"; }
void target(int&& x)      { std::cout << "rvalue\n"; }

int main() {
    int a = 10;
    const int b = 20;

    wrapper(a);  // lvalue
    wrapper(b);  // const lvalue
    wrapper(30); // rvalue
    return 0;
}
```

### 5.3 返回值优化（RVO/NRVO）

```cpp
#include <string>

class BigObject {
public:
    BigObject() = default;
    BigObject(const BigObject&) { /* expensive copy */ }
    BigObject(BigObject&&) noexcept { /* cheap move */ }
};

// RVO (Return Value Optimization): 编译器直接在调用者的栈帧上构造
BigObject create_rvo() {
    return BigObject(); // 返回纯右值
}

// NRVO (Named Return Value Optimization)
BigObject create_nrvo() {
    BigObject obj;
    // ... 初始化 obj
    return obj; // 命名对象，编译器可能优化掉拷贝
}

// C++17 保证 RVO（对纯右值）
void use() {
    BigObject obj = create_rvo(); // 保证不拷贝/移动
}
```

### 5.4 引用折叠规则

```cpp
// 引用折叠规则:
// &  + &  → &
// &  + && → &
// && + &  → &
// && + && → &&

template<typename T>
void func(T&& arg) {
    // T&& 是"转发引用"（universal reference）
    // 如果传入 lvalue: T = U&, arg 类型 = U& (折叠)
    // 如果传入 rvalue: T = U,  arg 类型 = U&&
}

int main() {
    int x = 42;
    func(x);   // T = int&, arg = int&
    func(42);  // T = int,  arg = int&&
    return 0;
}
```

---

## 6. 概念（Concepts）

Concepts 是 C++20 引入的约束模板参数的机制，提供更清晰的错误信息和更好的代码表达力。

### 6.1 定义概念

```cpp
#include <concepts>
#include <iostream>

// 使用 requires 定义概念
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

// 组合概念
template<typename T>
concept SignedNumeric = Numeric<T> && std::is_signed_v<T>;

// 使用 requires 表达式
template<typename T>
concept Iterable = requires(T t) {
    t.begin();
    t.end();
    typename T::value_type;
};

// 多重 requires 子句
template<typename T>
concept Hashable = requires(T t) {
    { std::hash<T>{}(t) } -> std::convertible_to<std::size_t>;
};
```

### 6.2 使用概念约束模板

```cpp
// 方式 1: requires 子句
template<typename T>
requires Numeric<T>
T add(T a, T b) {
    return a + b;
}

// 方式 2: 简化的 requires
template<typename T>
T multiply(T a, T b) requires Numeric<T> {
    return a * b;
}

// 方式 3: 概念直接替代 typename
template<Numeric T>
T divide(T a, T b) {
    return a / b;
}

// 方式 4: auto + 概念
Numeric auto compute(Numeric auto a, Numeric auto b) {
    return a + b;
}

int main() {
    std::cout << add(1, 2) << '\n';       // OK
    std::cout << add(1.5, 2.5) << '\n';   // OK
    // add("a", "b"); // 编译错误: const char* 不满足 Numeric
    return 0;
}
```

### 6.3 标准库概念

```cpp
#include <concepts>

// std::integral, std::floating_point
template<std::integral T>
T factorial(T n) {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

// std::convertible_to
template<typename From, typename To>
requires std::convertible_to<From, To>
To safe_cast(From value) {
    return static_cast<To>(value);
}

// std::same_as
template<typename T, typename U>
requires std::same_as<T, U>
bool are_same_type() { return true; }

// std::derived_from
template<typename Derived, typename Base>
requires std::derived_from<Derived, Base>
void process_polymorphic(const Derived& d) {
    // 安全地以 Base 处理 Derived
}

// std::regular: 可拷贝 + 可默认构造 + 可比较
template<std::regular T>
class Stack {
    std::vector<T> data_;
public:
    void push(const T& v) { data_.push_back(v); }
    void push(T&& v) { data_.push_back(std::move(v)); }
    // ...
};
```

### 6.4 复合约束

```cpp
#include <concepts>

// requires 要求序列
template<typename T>
concept Stackable = requires(T a, T b) {
    { a.push(b) } -> std::same_as<void>;
    { a.pop() } -> std::same_as<void>;
    { a.top() } -> std::convertible_to<typename T::value_type>;
    { a.empty() } -> std::convertible_to<bool>;
};

// 嵌套 requires
template<typename T>
concept Serializable = requires(const T& t) {
    { t.serialize() } -> std::convertible_to<std::string>;
    requires std::default_initializable<T>;
};
```

---

## 7. 协程（Coroutines）

C++20 协程是可以暂停和恢复执行的函数。

### 7.1 协程基础

```cpp
#include <coroutine>
#include <iostream>

// 协程返回对象类型
struct Task {
    struct promise_type {
        Task get_return_object() {
            return { std::coroutine_handle<promise_type>::from_promise(*this) };
        }
        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;

    Task(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Task() { if (handle) handle.destroy(); }

    void resume() { handle.resume(); }
    bool done() const { return handle.done(); }
};

// 定义一个协程
Task my_coroutine() {
    std::cout << "Step 1\n";
    co_await std::suspend_always{}; // 挂起点
    std::cout << "Step 2\n";
    co_await std::suspend_always{}; // 挂起点
    std::cout << "Step 3\n";
}

int main() {
    Task t = my_coroutine();
    std::cout << "Created\n";

    t.resume(); // 输出: Step 1
    std::cout << "Suspended\n";

    t.resume(); // 输出: Step 2
    t.resume(); // 输出: Step 3

    std::cout << "Done: " << t.done() << '\n';
    return 0;
}
```

### 7.2 生成器（Generator）

```cpp
#include <coroutine>
#include <iostream>

// Generator: 协程逐步产出值
template<typename T>
struct Generator {
    struct promise_type {
        T current_value;

        Generator get_return_object() {
            return { std::coroutine_handle<promise_type>::from_promise(*this) };
        }
        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        std::suspend_always yield_value(T value) {
            current_value = std::move(value);
            return {};
        }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };

    using handle_type = std::coroutine_handle<promise_type>;
    handle_type handle;

    Generator(handle_type h) : handle(h) {}
    ~Generator() { if (handle) handle.destroy(); }

    // 迭代器接口
    struct iterator {
        handle_type handle;

        iterator& operator++() {
            handle.resume();
            return *this;
        }
        T& operator*() { return handle.promise().current_value; }
        bool operator==(std::default_sentinel_t) const { return handle.done(); }
    };

    iterator begin() {
        handle.resume();
        return { handle };
    }
    std::default_sentinel_t end() { return {}; }
};

// 使用 co_yield 产出值
Generator<int> range(int start, int end) {
    for (int i = start; i < end; ++i) {
        co_yield i;
    }
}

Generator<int> fibonacci() {
    int a = 0, b = 1;
    while (true) {
        co_yield a;
        auto next = a + b;
        a = b;
        b = next;
    }
}

int main() {
    // 使用 range
    for (int x : range(1, 6)) {
        std::cout << x << ' '; // 1 2 3 4 5
    }
    std::cout << '\n';

    // 使用无限序列 + take
    auto fib = fibonacci();
    int count = 0;
    for (int x : fib) {
        if (count++ >= 10) break;
        std::cout << x << ' '; // 0 1 1 2 3 5 8 13 21 34
    }
    std::cout << '\n';

    return 0;
}
```

### 7.3 异步协程（Awaitable）

```cpp
#include <coroutine>
#include <iostream>
#include <thread>
#include <future>

// 简单的异步 awaiter
struct AsyncAwaiter {
    bool await_ready() { return false; }
    void await_suspend(std::coroutine_handle<> h) {
        std::thread([h]() {
            std::this_thread::sleep_for(std::chrono::seconds(1));
            h.resume(); // 在新线程恢复协程
        }).detach();
    }
    void await_resume() {}
};

struct AsyncTask {
    struct promise_type {
        AsyncTask get_return_object() {
            return { std::coroutine_handle<promise_type>::from_promise(*this) };
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;
    AsyncTask(std::coroutine_handle<promise_type> h) : handle(h) {}
};

AsyncTask async_work() {
    std::cout << "Before async on thread: "
              << std::this_thread::get_id() << '\n';
    co_await AsyncAwaiter{};
    std::cout << "After async on thread: "
              << std::this_thread::get_id() << '\n';
}

int main() {
    async_work();
    std::this_thread::sleep_for(std::chrono::seconds(2));
    return 0;
}
```

---

## 8. 模块（Modules）

模块是 C++20 引入的替代头文件的代码组织机制。

### 8.1 基本模块

```cpp
// math.cppm (模块接口文件)
export module math;

export int add(int a, int b) {
    return a + b;
}

export int multiply(int a, int b) {
    return a * b;
}

// 非导出的内部实现
int helper() {
    return 42;
}

// 导出命名空间
export namespace math {
    double pi = 3.14159265358979;
    double circle_area(double r) { return pi * r * r; }
}
```

```cpp
// main.cpp
import math;
#include <iostream>

int main() {
    std::cout << add(2, 3) << '\n';           // 5
    std::cout << multiply(4, 5) << '\n';       // 20
    std::cout << math::circle_area(2.0) << '\n'; // ~12.57

    // helper(); // 编译错误: helper 未导出
    return 0;
}
```

### 8.2 模块分区

```cpp
// math.core.cppm
export module math:core;

export int add(int a, int b) { return a + b; }
export int subtract(int a, int b) { return a - b; }

// math.advanced.cppm
export module math:advanced;

import :core; // 导入同一模块的分区

export int compute(int a, int b) {
    return add(a, b) * 2; // 使用 core 中的 add
}

// math.cppm (主模块接口)
export module math;
export import :core;      // 重新导出分区
export import :advanced;
```

### 8.3 头文件单元与全局模块片段

```cpp
// 兼容传统头文件
module;
#include <iostream>
#include <vector>
export module mymodule;

// 全局模块片段中的 include 不会被导出
// 但模块内的代码可以使用它们

export void print_vector(const std::vector<int>& v) {
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}
```

### 8.4 编译命令示例

```bash
# GCC
g++ -std=c++20 -fmodules-ts -c math.cppm -o math.gcm
g++ -std=c++20 -fmodules-ts main.cpp math.gcm -o program

# Clang
clang++ -std=c++20 --precompile math.cppm -o math.pcm
clang++ -std=c++20 -fprebuilt-module-path=. main.cpp -o program

# MSVC
cl /std:c++20 /interface /c math.cppm
cl /std:c++20 /reference math=math.ifc main.cpp
```

---

## 9. 最佳实践

### 9.1 现代 C++ 核心原则

| 原则 | 说明 |
|------|------|
| **RAII** | 资源获取即初始化，利用析构函数自动管理资源 |
| **零开销** | 不使用的特性不需要付出代价，使用的特性比手写更好 |
| **const 正确性** | 默认使用 const，只在需要修改时去掉 |
| **值语义** | 优先值传递，需要多态时才使用指针 |
| **移动优先** | 实现移动构造/赋值，避免不必要的拷贝 |
| **编译时计算** | 尽可能使用 constexpr / consteval |

### 9.2 规则五/规则三/规则零

```cpp
// 规则零: 使用 RAII 类型管理所有资源，无需手写析构/拷贝/移动
class GoodClass {
    std::vector<int> data_;  // 自动管理
    std::string name_;       // 自动管理
public:
    // 无需定义任何特殊成员函数
    // 编译器生成的默认行为完全正确
};

// 规则五: 如果定义了其中一个，应该定义全部五个
class ResourceHolder {
    int* data_;
    size_t size_;
public:
    // 1. 析构函数
    ~ResourceHolder() { delete[] data_; }

    // 2. 拷贝构造
    ResourceHolder(const ResourceHolder& other)
        : data_(new int[other.size_]), size_(other.size_) {
        std::copy(other.data_, other.data_ + size_, data_);
    }

    // 3. 拷贝赋值
    ResourceHolder& operator=(const ResourceHolder& other) {
        if (this != &other) {
            auto* new_data = new int[other.size_];
            std::copy(other.data_, other.data_ + other.size_, new_data);
            delete[] data_;
            data_ = new_data;
            size_ = other.size_;
        }
        return *this;
    }

    // 4. 移动构造
    ResourceHolder(ResourceHolder&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    // 5. 移动赋值
    ResourceHolder& operator=(ResourceHolder&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }
};
```

### 9.3 constexpr 与编译时计算

```cpp
#include <array>
#include <algorithm>

// 编译时排序
constexpr std::array<int, 5> sorted_constexpr() {
    std::array<int, 5> arr{5, 3, 1, 4, 2};
    // C++20: constexpr 支持 std::sort
    std::sort(arr.begin(), arr.end());
    return arr;
}

// 编译时验证
constexpr bool is_sorted(std::array<int, 5> arr) {
    for (size_t i = 1; i < arr.size(); ++i) {
        if (arr[i] < arr[i-1]) return false;
    }
    return true;
}

int main() {
    constexpr auto sorted = sorted_constexpr();
    static_assert(is_sorted(sorted), "Should be sorted at compile time");
    static_assert(sorted[0] == 1);

    return 0;
}
```

### 9.4 异常安全保证

```cpp
#include <memory>
#include <vector>

class Stack {
    std::vector<int> data_;
public:
    // 强异常安全保证: copy-and-swap 惯用法
    void push(int value) {
        data_.push_back(value); // vector::push_back 提供强保证
    }

    // push_two: 如果第二个失败，需要回滚第一个
    void push_two(int a, int b) {
        auto copy = data_;      // 先拷贝
        copy.push_back(a);
        copy.push_back(b);
        data_.swap(copy);       // 原子操作，不抛异常
    }
};
```

---

## 10. 相关页面

- [[Rust高级编程]] — Rust vs C++ 智能指针对比（Box/unique_ptr, Arc/shared_ptr）
- [[Kotlin开发指南]] — Kotlin 协程 vs C++20 协程对比
- [[Swift开发指南]] — Swift 泛型 vs C++ 模板对比
- [[函数式编程]] — C++ 的函数式特性（lambdas, std::function, Ranges）
- [[系统编程基础]] — 内存模型、ABI、编译链接

---

## 参考资源

- [cppreference.com](https://en.cppreference.com/)
- [C++ Reference (learncpp)](https://www.learncpp.com/)
- [ISO C++ Committee](https://isocpp.org/)
- [C++ Coroutines Reference](https://en.cppreference.com/w/cpp/language/coroutines)
- [C++ Ranges Reference](https://en.cppreference.com/w/cpp/ranges)

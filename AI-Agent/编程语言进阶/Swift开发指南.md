---
title: Swift开发指南
aliases:
  - Swift进阶
  - Swift Development Guide
tags:
  - swift
  - ios
  - combine
  - concurrency
  - 函数式响应式
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: Swift官方文档 + 社区最佳实践
difficulty: advanced
project: AI-Agent-Wiki
---

# Swift 开发指南

> Swift 是 Apple 开发的现代、安全、高性能的编程语言。本文涵盖 Optional、闭包、协议、泛型、Combine、Swift Concurrency 等高级主题。

---

## 目录

- [1. Optional](#1-optional)
- [2. 闭包（Closures）](#2-闭包closures)
- [3. 协议（Protocols）](#3-协议protocols)
- [4. 泛型（Generics）](#4-泛型generics)
- [5. Combine 框架](#5-combine-框架)
- [6. Swift Concurrency（async/await）](#6-swift-concurrencyasyncawait)
- [7. 最佳实践](#7-最佳实践)
- [8. 相关页面](#8-相关页面)

---

## 1. Optional

Optional 是 Swift 类型系统的核心安全特性，用类型系统来处理可能缺失的值。

### 1.1 Optional 基本概念

```swift
// Optional<Wrapped> 是一个枚举
// enum Optional<Wrapped> {
//     case some(Wrapped)
//     case none
// }

// ? 是 Optional 的简写
var name: String? = "Alice"
name = nil // OK

// 非 Optional 类型不能为 nil
var age: Int = 30
// age = nil // 编译错误
```

### 1.2 Optional 解包方式

```swift
let optionalName: String? = "Alice"

// 1. 强制解包 (!) — 不推荐，可能崩溃
// let forced = optionalName!

// 2. Optional Binding (if let)
if let name = optionalName {
    print("Name: \(name)") // name 是非 Optional 类型
} else {
    print("Name is nil")
}

// 3. Optional Binding (guard let) — 提前退出
func greet(_ name: String?) {
    guard let name = name else {
        print("No name provided")
        return
    }
    print("Hello, \(name)")
}

// 4. Nil 合并运算符 (??)
let displayName = optionalName ?? "Unknown"

// 5. 隐式解包 Optional (!) — 谨慎使用
var assumedName: String! = "Bob"
print(assumedName) // 自动解包
```

### 1.3 Optional 链式调用

```swift
struct Person {
    var address: Address?
}

struct Address {
    var city: String
    var street: String?
}

let person = Person(address: Address(city: "Beijing", street: "Main St"))

// Optional Chaining: 链路中任何一环为 nil，整个表达式返回 nil
let street = person.address?.street // String??
print(street) // Optional(Optional("Main St"))

// 多层链式调用
if let s = person.address?.street {
    print("Street: \(s)")
}

// Optional Chaining 调用方法
class Calculator {
    func square(_ x: Int) -> Int { x * x }
}

var calc: Calculator? = Calculator()
let result = calc?.square(5) // Int? — 如果 calc 为 nil 则返回 nil
print(result ?? 0) // 25
```

### 1.4 Optional Map / FlatMap

```swift
let optionalNumber: Int? = 42

// map: 对非 nil 的值进行变换
let doubled = optionalNumber.map { $0 * 2 } // Int? -> Optional(84)

// flatMap: 当变换本身返回 Optional 时使用（Swift 5 之前）
// Swift 5+ 推荐使用 compactMap 处理数组中的 nil
let numbers: [Int?] = [1, nil, 3, nil, 5]
let valid = numbers.compactMap { $0 } // [1, 3, 5]
```

### 1.5 可失败初始化器

```swift
struct Temperature {
    let celsius: Double

    // 可失败初始化器
    init?(celsius: Double) {
        guard celsius >= -273.15 else {
            return nil // 绝对零度以下无效
        }
        self.celsius = celsius
    }
}

if let temp = Temperature(celsius: -300) {
    print("Valid: \(temp.celsius)")
} else {
    print("Invalid temperature") // 输出这个
}
```

---

## 2. 闭包（Closures）

闭包是自包含的代码块，可以在代码中传递和引用。

### 2.1 闭包语法

```swift
// 完整语法
let add: (Int, Int) -> Int = { (a: Int, b: Int) -> Int in
    return a + b
}

// 类型推断 + 省略 return（表达式体）
let multiply: (Int, Int) -> Int = { $0 * $1 }

// 简写
let square: (Int) -> Int = { $0 * $0 }

print(add(3, 4))       // 7
print(multiply(3, 4))  // 12
print(square(5))       // 25
```

### 2.2 尾随闭包

```swift
// 函数最后一个参数是闭包时，可以使用尾随闭包语法
func performOperation(_ value: Int, operation: (Int) -> Int) -> Int {
    return operation(value)
}

// 标准调用
let result1 = performOperation(5, operation: { $0 * 2 })

// 尾随闭包
let result2 = performOperation(5) { $0 * 2 }

// 多个尾随闭包 (Swift 5.3+)
func configureView(title: () -> String, action: () -> Void) {
    print("Title: \(title())")
    action()
}

configureView {
    "My View"
} action: {
    print("Tapped!")
}
```

### 2.3 闭包捕获语义

```swift
// 闭包默认捕获引用
var counter = 0
let increment = {
    counter += 1
}
increment()
increment()
print(counter) // 2

// 捕获列表 — 显式控制捕获方式
class ViewModel {
    var name = "VC"

    func setup() {
        // [weak self] / [unowned self]: 避免 retain cycle
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            print(self.name)
        }

        // 捕获值（非引用）
        let snapshot = self.name
        DispatchQueue.main.async { [snapshot] in
            print(snapshot) // 捕获时的值
        }
    }
}
```

### 2.4 逃逸闭包（@escaping）与非逃逸闭包

```swift
// @noescape (默认): 闭包在函数返回前执行完，不能存储或异步调用
func withLock<T>(_ lock: NSLock, body: () -> T) -> T {
    lock.lock()
    defer { lock.unlock() }
    return body()
}

// @escaping: 闭包可能在函数返回后执行（异步回调、存储到属性）
class NetworkManager {
    private var completionHandler: ((Data) -> Void)?

    func fetch(url: String, completion: @escaping (Data) -> Void) {
        // 存储闭包 → 需要 @escaping
        self.completionHandler = completion

        DispatchQueue.global().async {
            // 模拟网络请求
            let data = Data()
            DispatchQueue.main.async {
                self.completionHandler?(data)
            }
        }
    }
}
```

### 2.5 自动闭包（@autoclosure）

```swift
// @autoclosure: 自动将表达式包装为闭包（实现延迟求值）
func debugLog(_ condition: Bool, _ message: @autoclosure () -> String) {
    if condition {
        print(message()) // 只有在 condition 为 true 时才求值
    }
}

// 调用时直接传表达式，编译器自动包装为闭包
debugLog(true, "Error: \(expensiveOperation())") // expensiveOperation 只在需要时调用

// assert 就是这样实现的
// assert(condition, message)
// message 只有在 condition 为 false 时才求值
```

---

## 3. 协议（Protocols）

协议定义了一组方法和属性的蓝图，任何类型都可以遵循。

### 3.1 协议定义与遵循

```swift
protocol Drawable {
    // 属性要求
    var area: Double { get }
    var name: String { get set }

    // 方法要求
    func draw()
    mutating func resize(scale: Double)

    // 初始化器要求
    init(name: String)
}

class Circle: Drawable {
    var radius: Double
    var name: String
    var area: Double { .pi * radius * radius }

    init(name: String, radius: Double) {
        self.name = name
        self.radius = radius
    }

    required init(name: String) {
        self.name = name
        self.radius = 1.0
    }

    func draw() {
        print("Drawing circle: \(name)")
    }

    func resize(scale: Double) {
        radius *= scale
    }
}
```

### 3.2 协议扩展（默认实现）

```swift
protocol Greetable {
    var name: String { get }
}

// 协议扩展提供默认实现
extension Greetable {
    func greet() {
        print("Hello, \(name)!")
    }

    func formalGreet() {
        print("Good day, \(name).")
    }
}

struct User: Greetable {
    let name: String
    // 自动获得 greet() 和 formalGreet()
}

User(name: "Alice").greet() // "Hello, Alice!"
```

### 3.3 协议作为类型

```swift
// 协议可以像普通类型一样使用
let drawables: [Drawable] = [
    Circle(name: "C1", radius: 5),
    // Square(name: "S1", side: 3),
]

for d in drawables {
    d.draw()
}

// 协议作为函数参数
func totalArea(of shapes: [Drawable]) -> Double {
    shapes.reduce(0) { $0 + $1.area }
}

// 协议作为返回类型
func createShape() -> some Drawable {
    Circle(name: "Default", radius: 1)
}
```

### 3.4 关联类型（Associated Types）

```swift
protocol Container {
    associatedtype Item
    associatedtype Iterator: IteratorProtocol = AnyIterator<Item>

    var count: Int { get }

    mutating func append(_ item: Item)
    subscript(i: Int) -> Item { get }

    // 带约束的关联类型
    associatedtype SubSequence: Container where SubSequence.Item == Item
}

// 实现关联类型协议
struct IntStack: Container {
    // typealias Item = Int // 显式指定，或由类型推断

    private var items = [Int]()

    var count: Int { items.count }

    mutating func append(_ item: Int) {
        items.append(item)
    }

    subscript(i: Int) -> Int {
        items[i]
    }
}
```

### 3.5 面向协议编程（POP）

```swift
protocol Animal {
    var name: String { get }
}

extension Animal {
    func speak() {
        print("\(name) makes a sound")
    }
}

protocol Pet: Animal {
    var owner: String { get }
}

extension Pet {
    func playWith() {
        print("\(name) plays with \(owner)")
    }
}

struct Dog: Pet {
    let name: String
    let owner: String
}

// 多协议组合
func interact(with animal: Animal & Pet) {
    animal.speak()
    animal.playWith()
}

let dog = Dog(name: "Buddy", owner: "Alice")
interact(with: dog)
// "Buddy makes a sound"
// "Buddy plays with Alice"
```

---

## 4. 泛型（Generics）

### 4.1 泛型函数

```swift
func swap<T>(_ a: inout T, _ b: inout T) {
    let temp = a
    a = b
    b = temp
}

var x = 10, y = 20
swap(&x, &y)
print("x=\(x), y=\(y)") // x=20, y=10
```

### 4.2 泛型类型

```swift
struct Stack<Element> {
    private var items: [Element] = []

    mutating func push(_ item: Element) {
        items.append(item)
    }

    mutating func pop() -> Element? {
        return items.popLast()
    }

    var top: Element? { items.last }

    subscript(index: Int) -> Element {
        get { items[index] }
    }
}

var intStack = Stack<Int>()
intStack.push(1)
intStack.push(2)
print(intStack.pop() ?? 0) // 2
```

### 4.3 类型约束

```swift
// 泛型函数约束: T 必须遵循 Equatable
func findIndex<T: Equatable>(of value: T, in array: [T]) -> Int? {
    for (index, item) in array.enumerated() {
        if item == value {
            return index
        }
    }
    return nil
}

// 多重约束
func compare<T: Comparable & Hashable>(_ a: T, _ b: T) -> Bool {
    return a < b
}

// 关联类型约束（协议中的 where 子句）
extension Container where Item: Equatable {
    func indexOf(_ item: Item) -> Int? {
        for i in 0..<count {
            if self[i] == item {
                return i
            }
        }
        return nil
    }
}
```

### 4.4 泛型下标

```swift
struct Matrix {
    let rows: Int, columns: Int
    var grid: [Double]

    init(rows: Int, columns: Int) {
        self.rows = rows
        self.columns = columns
        grid = Array(repeating: 0.0, count: rows * columns)
    }

    // 泛型下标
    subscript(row: Int, col: Int) -> Double {
        get { grid[row * columns + col] }
        set { grid[row * columns + col] = newValue }
    }
}

var matrix = Matrix(rows: 3, columns: 3)
matrix[0, 0] = 1.0
matrix[1, 1] = 1.0
matrix[2, 2] = 1.0
```

### 4.5 Opaque Types (`some`) 与 `any`

```swift
// some: 返回某种遵循协议的具体类型（编译器知道具体类型，对外隐藏）
func makeShape() -> some Drawable {
    Circle(name: "Generated", radius: 5)
}

// associatedtype 的 some 用法
protocol View {
    associatedtype Body: View
    var body: Body { get }
}

// any: 存在类型，运行时类型擦除
let shapes: [any Drawable] = [
    Circle(name: "C1", radius: 1),
    Circle(name: "C2", radius: 2),
]

// Swift 5.7+ 改进：primary associated types
// protocol Container<Item> { ... }
// func use<C: Container<Int>>(_: C) { ... }
```

---

## 5. Combine 框架

Combine 是 Apple 的响应式编程框架，类似于 RxSwift。

### 5.1 核心概念

```swift
import Combine
import Foundation

// Publisher: 发布者，随时间发出值
// Subscriber: 订阅者，接收值
// Operator: 操作符，转换/过滤/组合值
// Subject: 可以手动发送值的 Publisher

// Just: 发出单个值然后完成的 Publisher
Just(42)
    .sink { value in
        print("Received: \(value)") // 42
    }

//PassthroughSubject: 不会保留值，新订阅者不会收到之前发送的值
let subject = PassthroughSubject<Int, Never>()
let cancellable = subject.sink { value in
    print("Value: \(value)")
}
subject.send(1)
subject.send(2)
subject.send(completion: .finished)
```

### 5.2 操作符

```swift
let publisher = (1...10).publisher

let cancellable = publisher
    .filter { $0 % 2 == 0 }          // 过滤偶数
    .map { $0 * 10 }                  // 映射
    .collect()                        // 收集为数组
    .sink { values in
        print(values) // [20, 40, 60, 80, 100]
    }

// flatMap: 将每个值映射为新的 Publisher 并合并
struct User {
    let id: Int
    let name: String
}

func fetchUser(id: Int) -> AnyPublisher<User, Error> {
    Just(User(id: id, name: "User\(id)"))
        .setFailureType(to: Error.self)
        .eraseToAnyPublisher()
}

let ids = [1, 2, 3].publisher
let cancellable2 = ids
    .flatMap { fetchUser(id: $0) }
    .sink(receiveCompletion: { _ in
        print("All done")
    }, receiveValue: { user in
        print("User: \(user.name)")
    })
```

### 5.3 自定义 Publisher

```swift
// 使用 CurrentValueSubject 创建可保留状态的 Publisher
class CounterViewModel: ObservableObject {
    @Published var count: Int = 0 // SwiftUI 集成

    // 或者使用 Combine 显式声明
    let countSubject = CurrentValueSubject<Int, Never>(0)

    func increment() {
        count += 1
        countSubject.send(count)
    }
}

// debounce / throttle
let subject = PassthroughSubject<String, Never>()

let cancellable = subject
    .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
    .sink { text in
        print("Debounced: \(text)")
    }

// 模拟搜索输入
subject.send("H")
subject.send("He")
subject.send("Hel")
subject.send("Hello") // 只有 "Hello" 会在 300ms 后触发
```

### 5.4 Combine 与 UIKit/AppKit 绑定

```swift
// Combine KVO 扩展
class MyObject {
    @objc dynamic var title: String = ""
}

let obj = MyObject()
let cancellable = obj.publisher(for: \.title)
    .sink { newTitle in
        print("Title changed to: \(newTitle)")
    }

obj.title = "New Title" // 触发输出
```

---

## 6. Swift Concurrency（async/await）

Swift 5.5 引入的现代并发模型，替代 GCD 和基于闭包的异步代码。

### 6.1 async/await 基础

```swift
// 定义异步函数
func fetchUserID() async -> Int {
    // 模拟网络请求
    try? await Task.sleep(nanoseconds: 1_000_000_000)
    return 42
}

func fetchUserName(id: Int) async -> String {
    try? await Task.sleep(nanoseconds: 500_000_000)
    return "User-\(id)"
}

// 使用 await 调用
func loadUser() async {
    let id = await fetchUserID()
    let name = await fetchUserName(id: id)
    print(name) // "User-42"
}
```

### 6.2 Task — 创建并发任务

```swift
func performConcurrentTasks() async {
    // 并发执行多个任务
    async let id = fetchUserID()
    async let name1 = fetchUserName(id: 1)
    async let name2 = fetchUserName(id: 2)

    // 等待所有结果
    let (userId, n1, n2) = await (id, name1, name2)
    print("\(userId), \(n1), \(n2)")
}

// Task: 创建非结构化并发任务
func startBackgroundTask() {
    Task {
        let result = await fetchUserID()
        print("Background result: \(result)")
    }

    // Task.detached: 不继承当前上下文
    Task.detached(priority: .background) {
        let result = await fetchUserID()
        print("Detached result: \(result)")
    }
}
```

### 6.3 TaskGroup — 结构化并发

```swift
func fetchAllUsers(ids: [Int]) async -> [String] {
    return await withTaskGroup(of: String.self) { group in
        for id in ids {
            group.addTask { await fetchUserName(id: id) }
        }

        var results: [String] = []
        for await result in group {
            results.append(result)
        }
        return results
    }
}

// 使用
Task {
    let names = await fetchAllUsers(ids: [1, 2, 3, 4, 5])
    print(names) // ["User-1", "User-2", "User-3", "User-4", "User-5"]
}
```

### 6.4 Actor — 数据竞争安全

```swift
// Actor 保证对其属性的访问是串行的（自动加锁）
actor BankAccount {
    private(set) var balance: Double

    init(balance: Double) {
        self.balance = balance
    }

    func deposit(_ amount: Double) {
        balance += amount
    }

    func withdraw(_ amount: Double) -> Bool {
        if balance >= amount {
            balance -= amount
            return true
        }
        return false
    }
}

// 使用
Task {
    let account = BankAccount(balance: 1000)
    await account.deposit(500)
    let success = await account.withdraw(200)
    let balance = await account.balance
    print("Balance: \(balance), withdrew: \(success)")
}
```

### 6.5 Sendable

```swift
// Sendable: 标记类型可以安全跨并发域传递
struct User: Sendable { // 值类型天然安全
    let id: Int
    let name: String
}

// actor 自身是 Sendable 的
// @MainActor: 标记代码在主线程执行
@MainActor
class MainViewModel {
    var data: [String] = []

    func update() {
        data.append("item")
    }
}

// @GlobalActor: 自定义全局 Actor
@globalActor
struct MyActor {
    actor MyActorType { }
    static let shared = MyActorType()
}

// @unchecked Sendable: 手动保证线程安全（需开发者负责）
final class ThreadSafeCounter: @unchecked Sendable {
    private let lock = NSLock()
    private var _count = 0

    var count: Int {
        lock.lock()
        defer { lock.unlock() }
        return _count
    }

    func increment() {
        lock.lock()
        _count += 1
        lock.unlock()
    }
}
```

### 6.6 AsyncSequence

```swift
// 自定义 AsyncSequence
struct Counter: AsyncSequence {
    typealias Element = Int
    let upperBound: Int

    struct AsyncIterator: AsyncIteratorProtocol {
        var current = 1
        let upperBound: Int

        mutating func next() async -> Int? {
            guard current <= upperBound else { return nil }
            let result = current
            current += 1
            return result
        }
    }

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(upperBound: upperBound)
    }
}

// 使用
Task {
    for await number in Counter(upperBound: 5) {
        print(number) // 1, 2, 3, 4, 5
    }
}
```

### 6.7 Async/Await 与 Combine 互操作

```swift
// 将 Publisher 转为 async/await
func fetchValue() async throws -> Int {
    let publisher = Just(42).setFailureType(to: Error.self)
    // Swift 5.5+ 将 Publisher 转为 AsyncSequence
    for try await value in publisher.values {
        return value
    }
    throw URLError(.unknown)
}

// 将 async/await 封装为 closure（用于传统回调API）
func withAsyncToCompletion(_ completion: @escaping (Int) -> Void) {
    Task {
        let result = await fetchUserID()
        completion(result)
    }
}
```

---

## 7. 最佳实践

### 7.1 内存管理

```swift
// 避免循环引用 — 使用 weak / unowned
class NetworkService {
    var onDataReceived: ((Data) -> Void)?

    deinit {
        print("NetworkService deinitialized")
    }
}

class ViewController {
    let service = NetworkService()

    func setup() {
        // [weak self] 打破循环引用
        service.onDataReceived = { [weak self] data in
            guard let self = self else { return }
            self.processData(data)
        }
    }

    private func processData(_ data: Data) {
        print("Processing \(data.count) bytes")
    }

    deinit {
        print("ViewController deinitialized")
    }
}
```

### 7.2 错误处理

```swift
// 自定义 Error
enum NetworkError: Error, LocalizedError {
    case invalidURL
    case timeout
    case parsingFailed(String)
    case httpError(Int)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "The URL is invalid."
        case .timeout: return "The request timed out."
        case .parsingFailed(let detail): return "Parsing failed: \(detail)"
        case .httpError(let code): return "HTTP Error: \(code)"
        }
    }
}

// 使用 throws + do-catch
func fetchUser(from url: URL) async throws -> User {
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          200..<300 ~= httpResponse.statusCode else {
        let code = (response as? HTTPURLResponse)?.statusCode ?? -1
        throw NetworkError.httpError(code)
    }

    do {
        return try JSONDecoder().decode(User.self, from: data)
    } catch {
        throw NetworkError.parsingFailed(error.localizedDescription)
    }
}

// 调用
Task {
    do {
        let user = try await fetchUser(from: URL(string: "https://api.example.com/user")!)
        print(user)
    } catch {
        print("Error: \(error.localizedDescription)")
    }
}
```

### 7.3 SwiftUI 集成

```swift
import SwiftUI

// @Published + ObservableObject = SwiftUI 数据绑定
class TodoViewModel: ObservableObject {
    @Published var todos: [String] = []
    @Published var isLoading = false

    @MainActor
    func loadTodos() async {
        isLoading = true
        defer { isLoading = false }

        // 模拟异步加载
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        todos = ["Buy groceries", "Walk dog", "Code review"]
    }
}

struct TodoListView: View {
    @StateObject private var viewModel = TodoViewModel()

    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading {
                    ProgressView("Loading...")
                } else {
                    List(viewModel.todos, id: \.self) { todo in
                        Text(todo)
                    }
                }
            }
            .navigationTitle("Todos")
            .task {
                await viewModel.loadTodos()
            }
        }
    }
}
```

---

## 8. 相关页面

- [[Rust高级编程]] — Rust trait vs Swift protocol 对比
- [[Kotlin开发指南]] — Kotlin 协程 vs Swift Concurrency 对比
- [[C++现代特性]] — Swift 泛型 vs C++ 模板
- [[函数式编程]] — Swift 的函数式特性（map/filter/reduce、闭包）
- [[iOS开发基础]] — Swift 在 Apple 平台的应用

---

## 参考资源

- [The Swift Programming Language](https://docs.swift.org/swift-book/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Combine Framework](https://developer.apple.com/documentation/combine)
- [Swift by Sundell](https://www.swiftbysundell.com/)

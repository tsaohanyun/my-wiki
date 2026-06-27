---
title: Kotlin开发指南
aliases:
  - Kotlin进阶
  - Kotlin Development Guide
tags:
  - kotlin
  - jvm
  - 协程
  - android
  - dsl
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: Kotlin官方文档 + 社区最佳实践
difficulty: advanced
project: AI-Agent-Wiki
---

# Kotlin 开发指南

> Kotlin 是一门现代、静态类型的 JVM 语言，与 Java 100% 互操作。本文涵盖协程、空安全、扩展函数、数据类、密封类、DSL 等高级主题。

---

## 目录

- [1. 协程（Coroutines）](#1-协程coroutines)
- [2. 空安全（Null Safety）](#2-空安全null-safety)
- [3. 扩展函数（Extension Functions）](#3-扩展函数extension-functions)
- [4. 数据类（Data Class）](#4-数据类data-class)
- [5. 密封类（Sealed Class）](#5-密封类sealed-class)
- [6. DSL 构建](#6-dsl-构建)
- [7. 最佳实践](#7-最佳实践)
- [8. 相关页面](#8-相关页面)

---

## 1. 协程（Coroutines）

协程是 Kotlin 对异步编程的核心解决方案，以同步的写法实现异步逻辑。

### 1.1 基础概念

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // launch: 启动一个新协程（fire-and-forget）
    launch {
        delay(1000)
        println("World!")
    }
    println("Hello")
    // join: 等待子协程完成
    // 默认 runBlocking 会等待所有子协程
}

// 核心组件：
// - CoroutineScope: 协程作用域，管理协程生命周期
// - Dispatcher: 调度器，决定协程在哪个线程执行
//   - Dispatchers.Main: UI 线程
//   - Dispatchers.IO: IO 密集型操作
//   - Dispatchers.Default: CPU 密集型操作
//   - Dispatchers.Unconfined: 不限制线程
// - Job: 协程句柄，可用于取消
// - Deferred<T>: 带返回值的异步任务（类似 Promise）
```

### 1.2 async / await

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // 并发执行多个异步任务
    val deferred1 = async(Dispatchers.IO) {
        delay(1000)
        "Result 1"
    }

    val deferred2 = async(Dispatchers.IO) {
        delay(1500)
        "Result 2"
    }

    // await 等待结果
    val result1 = deferred1.await()
    val result2 = deferred2.await()
    println("$result1, $result2") // 总耗时约 1500ms（并发）
}
```

### 1.3 协程作用域与结构化并发

```kotlin
import kotlinx.coroutines.*

// 结构化并发：父协程会等待所有子协程完成
class MyService {
    // 自定义 CoroutineScope
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    fun startWork() {
        scope.launch {
            val data = fetchData()
            updateUI(data)
        }
    }

    // 取消所有子协程
    fun destroy() {
        scope.cancel()
    }

    private suspend fun fetchData(): String {
        delay(1000)
        return "data"
    }

    private fun updateUI(data: String) {
        println("UI: $data")
    }
}
```

### 1.4 Flow — 冷流

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Flow: 类似 RxJava 的 Observable，但是冷流（每次收集都会重新执行）
fun numbers(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(500)
        emit(i)
    }
}

fun main() = runBlocking {
    // 收集 Flow
    numbers().collect { value ->
        println(value)
    }

    // 操作符
    numbers()
        .map { it * it }            // 转换
        .filter { it > 5 }          // 过滤
        .onEach { println("Got: $it") }
        .toList()                   // 收集为 List
        .also { println("Result: $it") } // [9, 16, 25]
}
```

### 1.5 StateFlow / SharedFlow — 热流

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// StateFlow: 持有状态的可观察流（替代 LiveData）
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }
}

// SharedFlow: 向多个收集者广播事件
class EventBus {
    private val _events = MutableSharedFlow<String>(extraBufferCapacity = 10)
    val events: SharedFlow<String> = _events.asSharedFlow()

    suspend fun emitEvent(event: String) {
        _events.emit(event)
    }
}
```

### 1.6 异常处理

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // SupervisorJob: 子协程的失败不会影响其他子协程
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Caught: $exception")
    }

    val job = SupervisorJob()
    val scope = CoroutineScope(job + Dispatchers.Default + handler)

    scope.launch {
        delay(500)
        throw RuntimeException("Task failed")
    }

    scope.launch {
        delay(1000)
        println("Other task succeeded")
    }

    delay(2000)
}

// try-catch 在协程中
suspend fun safeCall(): Result<String> {
    return try {
        val result = apiCall()
        Result.success(result)
    } catch (e: Exception) {
        Result.failure(e)
    }
}

suspend fun apiCall(): String {
    delay(100)
    return "OK"
}
```

### 1.7 Channel — 协程间通信

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

fun main() = runBlocking {
    val channel = Channel<Int>()

    // 生产者
    launch {
        for (i in 1..5) {
            channel.send(i)
        }
        channel.close()
    }

    // 消费者
    for (value in channel) {
        println("Received: $value")
    }
}
```

---

## 2. 空安全（Null Safety）

Kotlin 的类型系统在编译时消除空指针异常的风险。

### 2.1 可空与非空类型

```kotlin
// 非空类型
var a: String = "hello"
// a = null // 编译错误

// 可空类型
var b: String? = "hello"
b = null // OK

// 访问可空类型的属性需要安全调用
println(b?.length) // 安全调用符 ?.  — 如果 b 为 null，返回 null
```

### 2.2 安全调用链与 Elvis 运算符

```kotlin
data class Person(val name: String, val address: Address?)
data class Address(val city: String?, val zipCode: String?)

fun getCity(person: Person?): String {
    // 链式安全调用
    val city = person?.address?.city

    // Elvis 运算符 ??: 如果左侧为 null，返回右侧
    return city ?: "Unknown"
}

// 安全转换
val obj: Any = "hello"
val str: String? = obj as? String // 如果类型不匹配返回 null
println(str?.length)
```

### 2.3 非空断言（谨慎使用）

```kotlin
var name: String? = "Alice"

// !! 非空断言：如果为 null，抛出 NullPointerException
val length: Int = name!!.length

// 仅在确定不可能为 null 时使用，生产代码应尽量避免
```

### 2.4 let / run / also 与空安全

```kotlin
// let: 仅在非空时执行块
val name: String? = "Bob"
name?.let {
    println("Name length: ${it.length}")
}

// run: 对象上执行块
val result = name?.run {
    "Name is $this, length is $length"
}
println(result)

// also: 用于副作用（链式调用中插入额外操作）
name?.also {
    println("Processing name: $it")
}
    ?.let { it.uppercase() }
    ?.also { println("Uppercased: $it") }
```

### 2.5 lateinit 与 lazy

```kotlin
class Service {
    // lateinit: 延迟初始化非空属性（用于依赖注入等场景）
    lateinit var config: String

    fun init(c: String) {
        config = c
    }

    fun check(): Boolean {
        // 检查是否已初始化
        return ::config.isInitialized
    }

    // lazy: 惰性初始化（首次访问时初始化）
    val expensiveValue: String by lazy {
        println("Computing...")
        "computed"
    }
}
```

---

## 3. 扩展函数（Extension Functions）

扩展函数允许在不修改原始类的情况下添加新功能。

### 3.1 基本用法

```kotlin
// 为 String 添加扩展函数
fun String.lastChar(): Char {
    return this[length - 1]
}

fun main() {
    println("Kotlin".lastChar()) // 'n'
}
```

### 3.2 扩展属性

```kotlin
val String.lastChar: Char
    get() = this[length - 1]

// 注意：扩展属性不能有 backing field，因此不能初始化
// var String.lastChar: Char
//     get() = this[length - 1]
//     set(value) { this = this.dropLast(1) + value } // 只能通过计算实现

fun main() {
    println("Kotlin".lastChar) // 'n'
}
```

### 3.3 扩展函数与多态

```kotlin
open class Animal
class Dog : Animal()
class Cat : Animal()

// 扩展函数是静态解析的（不支持多态）
fun Animal.describe() = "Animal"
fun Dog.describe() = "Dog"
fun Cat.describe() = "Cat"

fun main() {
    val animal: Animal = Dog()
    println(animal.describe()) // "Animal" — 注意：不是 "Dog"！
}
```

### 3.4 泛型扩展函数

```kotlin
// T.() -> R: 带接收者的 Lambda（扩展函数类型的 Lambda）
fun <T, R> T.applyTransform(transform: T.() -> R): R {
    return this.transform()
}

fun main() {
    val result = "hello".applyTransform {
        this.uppercase()
    }
    println(result) // "HELLO"
}
```

### 3.5 可空接收者

```kotlin
// 允许在 null 上调用扩展函数
fun String?.orDefault(default: String): String {
    return this ?: default
}

fun main() {
    val s: String? = null
    println(s.orDefault("default")) // "default"
}
```

---

## 4. 数据类（Data Class）

数据类自动生成 `equals()`、`hashCode()`、`toString()`、`copy()` 等方法。

### 4.1 基本定义

```kotlin
data class User(
    val id: Long,
    val name: String,
    val email: String,
    val age: Int = 0, // 默认值
)

fun main() {
    val user = User(1, "Alice", "alice@example.com")

    // 自动生成的 toString
    println(user) // User(id=1, name=Alice, email=alice@example.com, age=0)

    // copy: 创建副本（可修改部分属性）
    val updated = user.copy(name = "Bob", age = 30)
    println(updated) // User(id=1, name=Bob, email=alice@example.com, age=30)

    // 解构声明
    val (id, name, email) = user
    println("$id, $name, $email")
}
```

### 4.2 解构声明

```kotlin
data class Point(val x: Int, val y: Int)

fun main() {
    val p = Point(10, 20)

    // 解构声明
    val (x, y) = p
    println("x=$x, y=$y")

    // 在 for 循环中解构
    val points = listOf(Point(1, 2), Point(3, 4))
    for ((x, y) in points) {
        println("($x, $y)")
    }

    // 在 Map 中使用
    val map = mapOf("a" to 1, "b" to 2)
    for ((key, value) in map) {
        println("$key = $value")
    }
}
```

### 4.3 与密封类结合使用

```kotlin
// 配合密封类表示状态
sealed class UiState {
    data class Loading(val progress: Int) : UiState()
    data class Success<T>(val data: T) : UiState()
    data class Error(val message: String) : UiState()
    object Empty : UiState()
}
```

---

## 5. 密封类（Sealed Class）

密封类限制了一个值只能是一组固定类型之一，确保 `when` 表达式穷尽所有可能。

### 5.1 定义与使用

```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Failure(val error: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

fun <T> handleResult(result: Result<T>) {
    // when 表达式必须覆盖所有子类（穷尽性检查）
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Failure -> println("Error: ${result.error.message}")
        Result.Loading -> println("Loading...")
        // 不需要 else 分支！如果将来添加新子类，编译器会报错
    }
}
```

### 5.2 状态机模式

```kotlin
sealed class ConnectionState {
    object Disconnected : ConnectionState()
    object Connecting : ConnectionState()
    data class Connected(val serverName: String) : ConnectionState()
    data class Error(val message: String, val retryable: Boolean) : ConnectionState()
}

class ConnectionManager {
    private var state: ConnectionState = ConnectionState.Disconnected

    fun connect(server: String) {
        state = ConnectionState.Connecting
        // ... 模拟连接
        state = ConnectionState.Connected(server)
    }

    fun disconnect() {
        when (val s = state) {
            is ConnectionState.Connected -> {
                println("Disconnecting from ${s.serverName}")
                state = ConnectionState.Disconnected
            }
            is ConnectionState.Error -> {
                if (s.retryable) connect("default")
            }
            else -> {} // Disconnected, Connecting
        }
    }
}
```

### 5.3 密封接口（Kotlin 1.5+）

```kotlin
sealed interface Action {
    data class Click(val x: Int, val y: Int) : Action
    data class Input(val text: String) : Action
    object Scroll : Action
}

// 多个密封接口组合
sealed interface Parcelable
sealed interface Debuggable

data class UserAction(
    val name: String,
) : Action, Parcelable, Debuggable
```

---

## 6. DSL 构建

Kotlin 的 DSL 能力使其能够创建类型安全的、声明式的领域特定语言。

### 6.1 带接收者的 Lambda

```kotlin
// 带接收者的 Lambda 类型: T.() -> R
// 在 Lambda 内部，T 的成员可以直接访问

class StringBuilder {
    private val content = StringBuilder()

    fun append(text: String) {
        content.append(text)
    }

    fun build(): String = content.toString()
}

// 定义 DSL 构建函数
fun buildString(action: StringBuilder.() -> Unit): String {
    val sb = StringBuilder()
    sb.action() // 在 sb 的上下文中执行 action
    return sb.build()
}

fun main() {
    val result = buildString {
        append("Hello")
        append(", ")
        append("World!")
    }
    println(result) // "Hello, World!"
}
```

### 6.2 HTML DSL

```kotlin
// 定义 HTML 标签基类
abstract class Tag(val name: String) {
    private val children = mutableListOf<Tag>()
    private val attributes = mutableListOf<Pair<String, String>>()

    protected fun <T : Tag> initTag(tag: T, init: T.() -> Unit): T {
        tag.init()
        children.add(tag)
        return tag
    }

    override fun toString(): String {
        val attrs = if (attributes.isEmpty()) "" else attributes.joinToString("") { " ${it.first}=\"${it.second}\"" }
        return if (children.isEmpty()) {
            "<$name$attrs />"
        } else {
            "<$name$attrs>${children.joinToString("")}</$name>"
        }
    }
}

class Html : Tag("html") {
    fun body(init: Body.() -> Unit) = initTag(Body(), init)
}

class Body : Tag("body") {
    fun p(text: String) = initTag(Paragraph(), {}) { /* set text */ }
    fun p(init: Paragraph.() -> Unit) = initTag(Paragraph(), init)
}

class Paragraph : Tag("p") {
    var text: String = ""
}

// DSL 入口函数
fun html(init: Html.() -> Unit): Html {
    val html = Html()
    html.init()
    return html
}

fun main() {
    val page = html {
        body {
            p {
                text = "Hello DSL!"
            }
        }
    }
    println(page)
}
```

### 6.3 Gradle DSL 风格配置

```kotlin
@DslMarker
annotation class ConfigDsl

@ConfigDsl
class ServerConfig {
    var port: Int = 8080
    var host: String = "localhost"
    private val routes = mutableListOf<Route>()

    fun route(path: String, init: Route.() -> Unit) {
        routes.add(Route(path).apply(init))
    }

    fun build(): String {
        return "Server($host:$port) with ${routes.size} routes"
    }
}

@ConfigDsl
class Route(val path: String) {
    var method: String = "GET"
    var handler: String = "default"
}

fun server(init: ServerConfig.() -> Unit): ServerConfig {
    return ServerConfig().apply(init)
}

fun main() {
    val config = server {
        port = 9000
        host = "0.0.0.0"

        route("/api/users") {
            method = "GET"
            handler = "userList"
        }

        route("/api/orders") {
            method = "POST"
            handler = "createOrder"
        }
    }

    println(config.build())
}
```

### 6.4 @DslMarker 限制作用域

```kotlin
// @DslMarker 防止在嵌套 DSL 中意外访问外层接收者
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class Table
@HtmlDsl
class Tr {
    // 如果没有 @DslMarker，在 tr {} 内部可以直接调用 table {} 等
    // 有了 @DslMarker，只能访问 Tr 的方法
}

// 这样就不会出现隐式访问错误
```

---

## 7. 最佳实践

### 7.1 协程最佳实践

| 场景 | 推荐 |
|------|------|
| ViewModel/Controller 层 | `viewModelScope` / `lifecycleScope` |
| IO 操作 | `Dispatchers.IO` |
| CPU 密集型 | `Dispatchers.Default` |
| UI 更新 | `Dispatchers.Main` |
| 事件流 | `Flow` / `StateFlow` |
| 并发安全 | `Mutex` 或 `AtomicReference` |

### 7.2 避免内存泄漏

```kotlin
// ❌ 错误: 使用 GlobalScope 导致泄漏
// GlobalScope.launch { ... }

// ✅ 正确: 使用绑定到生命周期的 scope
class MyActivity : AppCompatActivity() {
    // 使用 lifecycleScope（Android）
    fun loadData() {
        lifecycleScope.launch {
            val data = fetchData()
            showData(data)
        }
    }
}

// ✅ 正确: 自定义 scope 并在适当时机取消
class Repository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun close() {
        scope.cancel()
    }
}
```

### 7.3 纯函数与不可变性

```kotlin
// 使用 data class 的 copy 创建不可变修改
data class AppState(
    val users: List<User> = emptyList(),
    val loading: Boolean = false,
)

// Reducer 风格的状态管理
fun reduce(state: AppState, action: Action): AppState {
    return when (action) {
        is Action.LoadUsers -> state.copy(loading = true)
        is Action.UsersLoaded -> state.copy(loading = false, users = action.users)
        else -> state
    }
}
```

### 7.4 委托属性

```kotlin
import kotlin.properties.Delegates

class Config {
    // observable: 属性变更时回调
    var port: Int by Delegates.observable(8080) { _, old, new ->
        println("port changed: $old -> $new")
    }

    // vetoable: 可否决变更
    var retries: Int by Delegates.vetoable(3) { _, old, new ->
        new >= 0 // 只允许非负值
    }

    // 在 Map 中存储属性
    private val map = mutableMapOf<String, Any?>(
        "name" to "default",
        "timeout" to 5000,
    )
    val name: String by map
    val timeout: Int by map
}
```

---

## 8. 相关页面

- [[Rust高级编程]] — Rust async/await 与 Kotlin 协程对比
- [[C++现代特性]] — C++20 协程 vs Kotlin 协程
- [[Swift开发指南]] — Swift async/await vs Kotlin 协程
- [[函数式编程]] — Kotlin 的函数式特性（高阶函数、不可变性）
- [[Android开发基础]] — Kotlin 在 Android 中的应用

---

## 参考资源

- [Kotlin 官方文档](https://kotlinlang.org/docs/home.html)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Kotlin Flow](https://kotlinlang.org/docs/flow.html)
- [Kotlin DSL Reference](https://kotlinlang.org/docs/type-safe-builders.html)

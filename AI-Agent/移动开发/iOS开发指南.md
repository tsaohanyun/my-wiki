---
title: iOS开发指南
aliases:
  - iOS开发
  - Swift开发
  - SwiftUI开发
  - iOS App开发
tags:
  - ios
  - swift
  - swiftui
  - combine
  - coredata
  - mobile-dev
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: Apple官方文档、社区最佳实践
difficulty: intermediate
project: AI-Agent
---

# iOS开发指南

## 概述

iOS 开发以 Swift 为主要编程语言，SwiftUI 为现代声明式 UI 框架，Combine 提供响应式编程能力，CoreData 作为持久化方案。本指南涵盖 SwiftUI、Combine、CoreData 和 App 生命周期等核心主题。

---

## 一、SwiftUI

### 1.1 基础视图与修饰符

```swift
import SwiftUI

struct ContentView: View {
    @State private var username: String = ""
    @State private var isOn: Bool = false

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "person.circle.fill")
                .resizable()
                .frame(width: 80, height: 80)
                .foregroundStyle(.blue)

            TextField("用户名", text: $username)
                .textFieldStyle(.roundedBorder)
                .padding(.horizontal)

            Toggle("启用通知", isOn: $isOn)
                .padding(.horizontal)

            if isOn {
                Text("通知已开启 ✅")
                    .font(.subheadline)
                    .foregroundStyle(.green)
            }

            Button(action: {
                print("提交: \(username)")
            }) {
                Text("提交")
                    .font(.headline)
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(.blue)
                    )
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 40)
    }
}

#Preview {
    ContentView()
}
```

### 1.2 列表与 ForEach

```swift
struct Article: Identifiable, Codable {
    let id: UUID
    let title: String
    let summary: String
    let isFavorite: Bool
}

struct ArticleListView: View {
    @State private var articles: [Article] = []
    @State private var searchText: String = ""

    var filteredArticles: [Article] {
        if searchText.isEmpty {
            return articles
        }
        return articles.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
    }

    var body: some View {
        NavigationStack {
            List(filteredArticles) { article in
                NavigationLink(value: article) {
                    ArticleRow(article: article)
                }
            }
            .navigationTitle("文章")
            .searchable(text: $searchText, prompt: "搜索文章")
            .navigationDestination(for: Article.self) { article in
                ArticleDetailView(article: article)
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: addArticle) {
                        Image(systemName: "plus")
                    }
                }
            }
        }
    }

    private func addArticle() {
        articles.append(Article(id: UUID(), title: "新文章", summary: "摘要内容", isFavorite: false))
    }
}

struct ArticleRow: View {
    let article: Article

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(article.title).font(.headline)
                Text(article.summary).font(.subheadline).foregroundStyle(.secondary)
            }
            Spacer()
            if article.isFavorite {
                Image(systemName: "star.fill").foregroundStyle(.yellow)
            }
        }
    }
}
```

### 1.3 自定义组件

```swift
// 可复用的卡片组件
struct FeatureCard: View {
    let icon: String
    let title: String
    let description: String
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.title2)
                    .frame(width: 50, height: 50)
                    .background(Color.blue.opacity(0.1))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .foregroundStyle(.blue)

                VStack(alignment: .leading, spacing: 4) {
                    Text(title).font(.headline)
                    Text(description).font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
                Image(systemName: "chevron.right").foregroundStyle(.tertiary)
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 16))
        }
        .buttonStyle(.plain)
    }
}

// 使用
FeatureCard(
    icon: "gearshape",
    title: "设置",
    description: "管理应用偏好"
) {
    // 跳转到设置页
}
```

---

## 二、状态管理

### 2.1 @State / @Binding

```swift
struct ParentView: View {
    @State private var progress: Double = 0.5

    var body: some View {
        VStack {
            Text("进度: \(Int(progress * 100))%")
            Slider(value: $progress)
            ChildView(progress: $progress)
        }
    }
}

struct ChildView: View {
    @Binding var progress: Double

    var body: some View {
        ProgressView(value: progress)
    }
}
```

### 2.2 @EnvironmentObject（全局状态）

```swift
// 定义环境对象
class AppState: ObservableObject {
    @Published var user: User?
    @Published var isAuthenticated: Bool = false
    @Published var themeColor: Color = .blue

    func logout() {
        user = nil
        isAuthenticated = false
    }
}

// 注入
@main
struct MyApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

// 消费
struct ContentView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack {
            if appState.isAuthenticated {
                Text("欢迎, \(appState.user?.name ?? "")")
            } else {
                LoginView()
            }
        }
    }
}
```

### 2.3 @Observable（iOS 17+ 新宏）

```swift
import Observation

@Observable
class ViewModel {
    var items: [Item] = []
    var isLoading: Bool = false
    var error: String?

    func loadData() async {
        isLoading = true
        defer { isLoading = false }

        do {
            items = try await APIClient.shared.fetchItems()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

// 使用
struct ItemListView: View {
    @State private var viewModel = ViewModel()

    var body: some View {
        List(viewModel.items) { item in
            Text(item.name)
        }
        .overlay {
            if viewModel.isLoading { ProgressView() }
        }
        .task { await viewModel.loadData() }
    }
}
```

---

## 三、Combine 框架

### 3.1 Publisher 与 Subscriber 基础

```swift
import Combine

// 网络请求示例
class UserRepository {
    private let session = URLSession.shared
    private var cancellables = Set<AnyCancellable>()

    func fetchUser(id: Int) -> AnyPublisher<User, Error> {
        guard let url = URL(string: "https://api.example.com/users/\(id)") else {
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
        }

        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: User.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

// 订阅
class UserViewModel: ObservableObject {
    @Published var user: User?
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()
    private let repository = UserRepository()

    func loadUser(id: Int) {
        repository.fetchUser(id: id)
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] user in
                    self?.user = user
                }
            )
            .store(in: &cancellables)
    }
}
```

### 3.2 表单验证链

```swift
class RegistrationViewModel: ObservableObject {
    @Published var email = ""
    @Published var password = ""
    @Published var confirmPassword = ""

    @Published var isFormValid = false
    @Published var emailError: String?
    @Published var passwordError: String?

    private var cancellables = Set<AnyCancellable>()

    init() {
        // 邮箱验证
        $email
            .map { email in
                let regex = #"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"#
                return NSPredicate(format: "SELF MATCHES %@", regex)
                    .evaluate(with: email)
            }
            .map { isValid in isValid ? nil : "请输入有效的邮箱地址" }
            .assign(to: \.emailError, on: self)
            .store(in: &cancellables)

        // 密码匹配验证
        Publishers.CombineLatest($password, $confirmPassword)
            .map { $0 == $1 && $0.count >= 8 }
            .assign(to: \.isFormValid, on: self)
            .store(in: &cancellables)
    }
}
```

### 3.3 使用 async/await（Combine 替代方案）

```swift
class ProductService {
    func fetchProducts() async throws -> [Product] {
        let url = URL(string: "https://api.example.com/products")!
        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              200...299 ~= httpResponse.statusCode else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode([Product].self, from: data)
    }
}

// 在 SwiftUI 中使用
struct ProductListView: View {
    @State private var products: [Product] = []
    @State private var isLoading = false

    var body: some View {
        List(products) { product in
            ProductRow(product: product)
        }
        .overlay { if isLoading { ProgressView() } }
        .task {
            isLoading = true
            defer { isLoading = false }
            do {
                products = try await ProductService().fetchProducts()
            } catch {
                print("加载失败: \(error)")
            }
        }
        .refreshable {
            products = try await ProductService().fetchProducts()
        }
    }
}
```

---

## 四、CoreData 持久化

### 4.1 定义数据模型

```swift
import CoreData
import Foundation

// CoreData Entity (可选代码定义)
@objc(TaskEntity)
public class TaskEntity: NSManagedObject {
    @NSManaged public var id: UUID
    @NSManaged public var title: String
    @NSManaged public var isCompleted: Bool
    @NSManaged public var createdAt: Date
    @NSManaged public var priority: Int16
}

extension TaskEntity {
    public static func fetchRequest() -> NSFetchRequest<TaskEntity> {
        return NSFetchRequest<TaskEntity>(entityName: "TaskEntity")
    }
}
```

### 4.2 CoreData Stack 封装

```swift
class CoreDataStack {
    static let shared = CoreDataStack()

    let container: NSPersistentContainer

    private init() {
        container = NSPersistentContainer(name: "AppModel")
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("CoreData 加载失败: \(error)")
            }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
    }

    var viewContext: NSManagedObjectContext { container.viewContext }

    func saveContext() {
        let context = container.viewContext
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("保存失败: \(error)")
            }
        }
    }

    // 后台上下文
    func newBackgroundContext() -> NSManagedObjectContext {
        let context = container.newBackgroundContext()
        context.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        return context
    }
}
```

### 4.3 使用 @FetchRequest 在 SwiftUI 中查询

```swift
struct TaskListView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \TaskEntity.createdAt, ascending: false)],
        predicate: NSPredicate(format: "isCompleted == NO"),
        animation: .default
    )
    private var tasks: FetchedResults<TaskEntity>

    var body: some View {
        NavigationStack {
            List {
                ForEach(tasks) { task in
                    TaskRow(task: task)
                }
                .onDelete(perform: deleteTask)
            }
            .navigationTitle("待办事项")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    NavigationLink("添加") { AddTaskView() }
                }
            }
        }
    }

    private func deleteTask(offsets: IndexSet) {
        withAnimation {
            offsets.map { tasks[$0] }.forEach(viewContext.delete)
            CoreDataStack.shared.saveContext()
        }
    }
}
```

### 4.4 CRUD 操作

```swift
class TaskRepository {
    let context: NSManagedObjectContext

    init(context: NSManagedObjectContext = CoreDataStack.shared.viewContext) {
        self.context = context
    }

    func create(title: String, priority: Int16 = 0) {
        let task = TaskEntity(context: context)
        task.id = UUID()
        task.title = title
        task.isCompleted = false
        task.createdAt = Date()
        task.priority = priority
        save()
    }

    func toggleComplete(_ task: TaskEntity) {
        task.isCompleted.toggle()
        save()
    }

    func update(_ task: TaskEntity, title: String) {
        task.title = title
        save()
    }

    func delete(_ task: TaskEntity) {
        context.delete(task)
        save()
    }

    func fetchCompleted() -> [TaskEntity] {
        let request = TaskEntity.fetchRequest()
        request.predicate = NSPredicate(format: "isCompleted == YES")
        request.sortDescriptors = [NSSortDescriptor(keyPath: \TaskEntity.createdAt, ascending: false)]
        return (try? context.fetch(request)) ?? []
    }

    private func save() {
        do { try context.save() }
        catch { print("保存失败: \(error)") }
    }
}
```

---

## 五、App 生命周期

### 5.1 SwiftUI App 生命周期

```swift
import SwiftUI

@main
struct MyApp: App {
    // 应用启动时执行
    init() {
        configureAppearance()
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .onAppear { print("RootView 出现") }
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            handleScenePhase(newPhase)
        }
    }

    private func handleScenePhase(_ phase: ScenePhase) {
        switch phase {
        case .active:
            print("App 进入前台活动状态")
        case .inactive:
            print("App 失去焦点（来电、控制中心等）")
        case .background:
            print("App 进入后台")
        @unknown default:
            break
        }
    }

    private func configureAppearance() {
        // 配置全局外观
        UINavigationBar.appearance().titleTextAttributes = [
            .foregroundColor: UIColor.systemBlue
        ]
    }
}
```

### 5.2 处理 Deep Link

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onOpenURL { url in
                    handleDeepLink(url)
                }
        }
    }

    private func handleDeepLink(_ url: URL) {
        // myapp://article/123
        guard url.scheme == "myapp" else { return }

        switch url.host {
        case "article":
            let id = url.pathComponents.dropFirst().first
            print("打开文章: \(id ?? "")")
        case "profile":
            print("打开个人资料")
        default:
            break
        }
    }
}
```

### 5.3 后台任务

```swift
import BackgroundTasks

class BackgroundTaskManager {
    static let shared = BackgroundTaskManager()

    func register() {
        // 注册后台刷新任务
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.myapp.refresh",
            using: nil
        ) { task in
            self.handleAppRefresh(task as! BGAppRefreshTask)
        }

        // 注册后台处理任务
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.myapp.processing",
            using: nil
        ) { task in
            self.handleProcessing(task as! BGProcessingTask)
        }
    }

    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: "com.myapp.refresh")
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15分钟后

        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("无法调度后台刷新: \(error)")
        }
    }

    private func handleAppRefresh(_ task: BGAppRefreshTask) {
        scheduleAppRefresh() // 重新调度下一次

        task.expirationHandler = {
            // 超时处理
        }

        Task {
            await syncData()
            task.setTaskCompleted(success: true)
        }
    }

    private func handleProcessing(_ task: BGProcessingTask) {
        task.expirationHandler = { /* 超时清理 */ }

        Task {
            await performHeavyWork()
            task.setTaskCompleted(success: true)
        }
    }

    private func syncData() async { /* 同步逻辑 */ }
    private func performHeavyWork() async { /* 重型任务 */ }
}
```

---

## 六、最佳实践

### 6.1 Swift 并发（async/await + Actor）

```swift
actor DataStore {
    private var cache: [String: Data] = [:]

    func getData(forKey key: String) async -> Data? {
        if let cached = cache[key] {
            return cached
        }
        let data = try? await fetchData(for: key)
        if let data = data {
            cache[key] = data
        }
        return data
    }

    private func fetchData(for key: String) async throws -> Data {
        // 网络请求
        let url = URL(string: "https://api.example.com/data/\(key)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }
}
```

### 6.2 项目结构

```
MyApp/
├── App/
│   ├── MyAppApp.swift            # App 入口
│   └── AppDelegate.swift         # UIKit 兼容（如需要）
├── Core/
│   ├── Models/                   # 数据模型
│   ├── Services/                 # 业务服务层
│   ├── Repositories/             # 数据仓库
│   └── Extensions/               # Swift 扩展
├── Features/
│   ├── Home/
│   │   ├── HomeView.swift
│   │   ├── HomeViewModel.swift
│   │   └── Components/
│   ├── Profile/
│   └── Settings/
├── DesignSystem/                 # 设计系统
│   ├── Colors.swift
│   ├── Typography.swift
│   └── Components/
├── Resources/
│   ├── Assets.xcassets
│   └── Localizable.strings
└── CoreData/
    ├── MyApp.xcdatamodeld
    └── CoreDataStack.swift
```

### 6.3 性能优化清单

| 优化项 | 说明 |
|--------|------|
| LazyVStack/LazyHStack | 替代 VStack/HStack 渲染大量视图 |
| @ViewBuilder | 减少条件分支产生的中间视图 |
| Instruments | 使用 Time Profiler / Core Animation 检测性能 |
| 图片优化 | 使用正确格式（HEIC）、适当尺寸、异步解码 |
| 避免主线程阻塞 | 网络请求和计算放在后台线程 |
| 内存管理 | 使用 weak/unowned 避免循环引用 |

---

## 相关页面

- [[Android开发指南]] - Android 平台开发对标
- [[Flutter跨平台开发]] - 跨平台方案对比
- [[React Native开发]] - JS 跨平台方案
- [[移动端架构模式]] - iOS 项目架构设计

---

## 参考资源

- [Apple SwiftUI 教程](https://developer.apple.com/tutorials/swiftui)
- [Apple Combine 文档](https://developer.apple.com/documentation/combine)
- [CoreData 编程指南](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreData/)
- [Swift 并发文档](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Hacking with Swift](https://www.hackingwithswift.com/)

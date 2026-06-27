---
title: "iOS开发基础"
aliases:
  - "iOS开发"
  - "Swift开发"
  - "SwiftUI"
  - "iOS基础"
tags:
  - mobile
  - ios
  - swift
  - swiftui
  - apple
type: "guide"
status: "active"
created: 2026-06-28
updated: 2026-06-28
source: "AI-Agent Wiki"
difficulty: "intermediate"
project: "Mobile Development"
---

# iOS 开发基础

> iOS 开发主要使用 Swift 语言，UI 框架包括现代化的 SwiftUI 和传统的 UIKit。

## 目录

- [SwiftUI](#swiftui)
- [UIKit](#uikit)
- [Combine 框架](#combine-框架)
- [CoreData](#coredata)
- [网络请求](#网络请求)
- [最佳实践](#最佳实践)
- [相关页面](#相关页面)

---

## SwiftUI

### 基础视图

```swift
import SwiftUI

struct ContentView: View {
    @State private var count = 0
    @State private var inputText = ""
    @State private var selectedColor: Color = .blue

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // 显示计数
                Text("Count: \(count)")
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundStyle(count > 10 ? .green : .primary)
                    .contentTransition(.numericText())
                    .animation(.spring, value: count)

                // 按钮组
                HStack(spacing: 20) {
                    Button(action: { count -= 1 }) {
                        Image(systemName: "minus.circle.fill")
                            .font(.system(size: 44))
                            .foregroundStyle(.red)
                    }

                    Button(action: { count += 1 }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.system(size: 44))
                            .foregroundStyle(.blue)
                    }
                }

                // TextField
                TextField("输入文字", text: $inputText)
                    .textFieldStyle(.roundedBorder)
                    .padding(.horizontal)

                if !inputText.isEmpty {
                    Text("你输入了: \(inputText)")
                        .foregroundStyle(.secondary)
                        .transition(.opacity.combined(with: .move(edge: .bottom)))
                }

                // Picker
                Picker("颜色", selection: $selectedColor) {
                    ForEach([Color.blue, .green, .orange, .purple], id: \.self) { color in
                        Text(color.description)
                            .tag(color)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)

                Spacer()
            }
            .padding()
            .navigationTitle("SwiftUI Demo")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    NavigationLink(destination: SettingsView()) {
                        Image(systemName: "gearshape")
                    }
                }
            }
        }
    }
}

#Preview {
    ContentView()
}
```

### List 与 Navigation

```swift
struct UserListView: View {
    @State private var users: [User] = User.sample
    @State private var searchText = ""

    var filteredUsers: [User] {
        guard !searchText.isEmpty else { return users }
        return users.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.email.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        List {
            ForEach(filteredUsers) { user in
                NavigationLink(value: user) {
                    HStack(spacing: 12) {
                        AsyncImage(url: URL(string: user.avatar)) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                        } placeholder: {
                            Circle()
                                .fill(Color.gray.opacity(0.2))
                                .overlay(ProgressView())
                        }
                        .frame(width: 48, height: 48)
                        .clipShape(Circle())

                        VStack(alignment: .leading, spacing: 4) {
                            Text(user.name)
                                .font(.headline)
                            Text(user.email)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .onDelete(perform: deleteUser)
            .onMove(perform: moveUser)
        }
        .searchable(text: $searchText, prompt: "搜索用户")
        .navigationDestination(for: User.self) { user in
            UserDetailView(user: user)
        }
        .navigationTitle("用户")
        .toolbar {
            EditButton()
        }
    }

    private func deleteUser(at offsets: IndexSet) {
        users.remove(atOffsets: offsets)
    }

    private func moveUser(from source: IndexSet, to destination: Int) {
        users.move(fromOffsets: source, toOffset: destination)
    }
}

struct User: Identifiable, Hashable {
    let id: UUID
    let name: String
    let email: String
    let avatar: String

    static let sample: [User] = [
        User(id: UUID(), name: "张三", email: "zhangsan@example.com", avatar: "https://i.pravatar.cc/150?u=1"),
        User(id: UUID(), name: "李四", email: "lisi@example.com", avatar: "https://i.pravatar.cc/150?u=2"),
        User(id: UUID(), name: "王五", email: "wangwu@example.com", avatar: "https://i.pravatar.cc/150?u=3"),
    ]
}
```

### 自定义修饰符和组件

```swift
// 自定义 ViewModifier
struct CardStyle: ViewModifier {
    var padding: CGFloat = 16
    var cornerRadius: CGFloat = 12

    func body(content: Content) -> some View {
        content
            .padding(padding)
            .background(Color(.secondarySystemBackground))
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
            .shadow(color: .black.opacity(0.05), radius: 8, y: 4)
    }
}

extension View {
    func cardStyle(padding: CGFloat = 16, cornerRadius: CGFloat = 12) -> some View {
        modifier(CardStyle(padding: padding, cornerRadius: cornerRadius))
    }
}

// 使用
VStack {
    Text("Hello")
    Text("World")
}
.cardStyle()
```

---

## UIKit

### UITableViewController

```swift
import UIKit

class ProductTableViewController: UITableViewController {

    private var products: [Product] = []
    private let cellIdentifier = "ProductCell"

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadData()
    }

    private func setupUI() {
        title = "商品列表"
        tableView.register(ProductCell.self, forCellReuseIdentifier: cellIdentifier)
        tableView.refreshControl = UIRefreshControl()
        tableView.refreshControl?.addTarget(self, action: #selector(handleRefresh), for: .valueChanged)

        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(handleAdd)
        )
    }

    @objc private func handleRefresh() {
        loadData()
    }

    @objc private func handleAdd() {
        let alert = UIAlertController(title: "新增商品", message: nil, preferredStyle: .alert)
        alert.addTextField { $0.placeholder = "商品名称" }
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
            guard let name = alert.textFields?.first?.text, !name.isEmpty else { return }
            self?.products.insert(Product(id: UUID(), name: name, price: 0), at: 0)
            self?.tableView.insertRows(at: [IndexPath(row: 0, section: 0)], with: .automatic)
        })
        present(alert, animated: true)
    }

    private func loadData() {
        // 模拟网络请求
        DispatchQueue.global().asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.products = Product.sampleData
            DispatchQueue.main.async {
                self?.tableView.reloadData()
                self?.tableView.refreshControl?.endRefreshing()
            }
        }
    }

    // MARK: - UITableViewDataSource
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        products.count
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as! ProductCell
        cell.configure(with: products[indexPath.row])
        return cell
    }

    // MARK: - UITableViewDelegate
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let detailVC = ProductDetailViewController()
        detailVC.product = products[indexPath.row]
        navigationController?.pushViewController(detailVC, animated: true)
    }

    override func tableView(_ tableView: UITableView, trailingSwipeActionsConfigurationForRowAt indexPath: IndexPath) -> UISwipeActionsConfiguration? {
        let delete = UIContextualAction(style: .destructive, title: "删除") { [weak self] _, _, completion in
            self?.products.remove(at: indexPath.row)
            tableView.deleteRows(at: [indexPath], with: .automatic)
            completion(true)
        }
        return UISwipeActionsConfiguration(actions: [delete])
    }
}

// 自定义 Cell
class ProductCell: UITableViewCell {
    static let identifier = "ProductCell"

    private let nameLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 16, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let priceLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 14)
        label.textColor = .systemOrange
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let productImageView: UIImageView = {
        let iv = UIImageView()
        iv.contentMode = .scaleAspectFill
        iv.clipsToBounds = true
        iv.layer.cornerRadius = 8
        iv.translatesAutoresizingMaskIntoConstraints = false
        return iv
    }()

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupViews()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    private func setupViews() {
        contentView.addSubview(productImageView)
        contentView.addSubview(nameLabel)
        contentView.addSubview(priceLabel)

        NSLayoutConstraint.activate([
            productImageView.leadingAnchor.constraint(equalTo: contentView.layoutMarginsGuide.leadingAnchor),
            productImageView.centerYAnchor.constraint(equalTo: contentView.centerYAnchor),
            productImageView.widthAnchor.constraint(equalToConstant: 56),
            productImageView.heightAnchor.constraint(equalToConstant: 56),

            nameLabel.leadingAnchor.constraint(equalTo: productImageView.trailingAnchor, constant: 12),
            nameLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),

            priceLabel.leadingAnchor.constraint(equalTo: nameLabel.leadingAnchor),
            priceLabel.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 4),
        ])
    }

    func configure(with product: Product) {
        nameLabel.text = product.name
        priceLabel.text = "¥\(String(format: "%.2f", product.price))"
    }
}
```

### UICollectionView + Compositional Layout

```swift
class GalleryViewController: UIViewController, UICollectionViewDataSource, UICollectionViewDelegate {

    private var collectionView: UICollectionView!

    override func viewDidLoad() {
        super.viewDidLoad()
        setupCollectionView()
    }

    private func setupCollectionView() {
        // 瀑布流布局
        let layout = UICollectionViewCompositionalLayout { _, environment in
            let containerWidth = environment.container.effectiveContentSize.width
            let spacing: CGFloat = 8
            let columns: CGFloat = 2
            let itemWidth = (containerWidth - spacing * (columns + 1)) / columns

            let itemSize = NSCollectionLayoutSize(
                widthDimension: .fractionalWidth(1.0),
                heightDimension: .estimated(200)
            )
            let item = NSCollectionLayoutItem(layoutSize: itemSize)

            let groupSize = NSCollectionLayoutSize(
                widthDimension: .fractionalWidth(1.0),
                heightDimension: .estimated(200)
            )
            let group = NSCollectionLayoutGroup.horizontal(
                layoutSize: groupSize,
                subitem: item,
                count: Int(columns)
            )
            group.interItemSpacing = .fixed(spacing)

            let section = NSCollectionLayoutSection(group: group)
            section.interGroupSpacing = spacing
            section.contentInsets = NSDirectionalEdgeInsets(
                top: spacing, leading: spacing, bottom: spacing, trailing: spacing
            )
            return section
        }

        collectionView = UICollectionView(frame: .zero, collectionViewLayout: layout)
        collectionView.dataSource = self
        collectionView.delegate = self
        collectionView.register(GalleryCell.self, forCellWithReuseIdentifier: GalleryCell.identifier)
        collectionView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(collectionView)

        NSLayoutConstraint.activate([
            collectionView.topAnchor.constraint(equalTo: view.topAnchor),
            collectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            collectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            collectionView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
        ])
    }
}
```

---

## Combine 框架

### 基础用法

```swift
import Combine
import Foundation

class LoginViewModel: ObservableObject {
    @Published var email = ""
    @Published var password = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var isLoggedIn = false

    private var cancellables = Set<AnyCancellable>()
    private let apiService: APIService

    init(apiService: APIService) {
        self.apiService = apiService

        // 监听 email 变化，清除错误
        $email
            .dropFirst()
            .sink { [weak self] _ in
                self?.errorMessage = nil
            }
            .store(in: &cancellables)
    }

    // 表单验证
    var isFormValid: Bool {
        !email.isEmpty &&
        email.contains("@") &&
        password.count >= 6
    }

    func login() {
        guard isFormValid else {
            errorMessage = "请输入有效的邮箱和密码（至少6位）"
            return
        }

        isLoading = true
        errorMessage = nil

        apiService.login(email: email, password: password)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] _ in
                    self?.isLoggedIn = true
                }
            )
            .store(in: &cancellables)
    }

    deinit {
        cancellables.forEach { $0.cancel() }
    }
}

// 在 SwiftUI 中使用
struct LoginView: View {
    @StateObject private var viewModel = LoginViewModel(apiService: APIService.shared)

    var body: some View {
        Form {
            Section {
                TextField("邮箱", text: $viewModel.email)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                SecureField("密码", text: $viewModel.password)
            }

            if let error = viewModel.errorMessage {
                Section {
                    Text(error).foregroundStyle(.red)
                }
            }

            Section {
                Button(action: viewModel.login) {
                    HStack {
                        Spacer()
                        if viewModel.isLoading {
                            ProgressView()
                        } else {
                            Text("登录").fontWeight(.semibold)
                        }
                        Spacer()
                    }
                }
                .disabled(!viewModel.isFormValid || viewModel.isLoading)
            }
        }
        .navigationTitle("登录")
    }
}
```

### 自定义 Publisher

```swift
// 自定义网络请求 Publisher
extension URLSession {
    func dataTaskPublisher(for url: URL) -> AnyPublisher<Data, APIError> {
        URLSession.shared.dataTaskPublisher(for: url)
            .mapError { APIError.network($0) }
            .map(\.data)
            .eraseToAnyPublisher()
    }
}

// Throttle / Debounce 示例
class SearchViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var results: [SearchResult] = []

    private var cancellables = Set<AnyCancellable>()

    init() {
        $searchText
            .debounce(for: .milliseconds(500), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .flatMap { query -> AnyPublisher<[SearchResult], Never> in
                APIService.shared.search(query: query)
                    .map { $0 }
                    .catch { _ in Just([]) }
                    .eraseToAnyPublisher()
            }
            .receive(on: DispatchQueue.main)
            .assign(to: \.results, on: self)
            .store(in: &cancellables)
    }
}
```

---

## CoreData

### 模型定义与操作

```swift
import CoreData
import Foundation

// CoreDataManager 单例
class CoreDataManager {
    static let shared = CoreDataManager()

    let container: NSPersistentContainer

    private init() {
        container = NSPersistentContainer(name: "AppModel")
        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("CoreData error: \(error)")
            }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
    }

    var viewContext: NSManagedObjectContext { container.viewContext }

    func save() {
        let context = viewContext
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Save error: \(error)")
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

// Repository
protocol TaskRepository {
    func fetchAll() -> [TaskEntity]
    func create(title: String, notes: String?) -> TaskEntity
    func update(_ task: TaskEntity)
    func delete(_ task: TaskEntity)
}

class TaskRepositoryImpl: TaskRepository {
    private let manager = CoreDataManager.shared

    func fetchAll() -> [TaskEntity] {
        let request: NSFetchRequest<TaskEntity> = TaskEntity.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \TaskEntity.createdAt, ascending: false)]
        return (try? manager.viewContext.fetch(request)) ?? []
    }

    func create(title: String, notes: String?) -> TaskEntity {
        let task = TaskEntity(context: manager.viewContext)
        task.id = UUID()
        task.title = title
        task.notes = notes
        task.completed = false
        task.createdAt = Date()
        manager.save()
        return task
    }

    func update(_ task: TaskEntity) {
        manager.save()
    }

    func delete(_ task: TaskEntity) {
        manager.viewContext.delete(task)
        manager.save()
    }
}

// 后台批量操作
extension TaskRepositoryImpl {
    func batchImport(tasks: [(title: String, notes: String?)]) {
        let context = manager.newBackgroundContext()
        context.perform {
            tasks.forEach { item in
                let task = TaskEntity(context: context)
                task.id = UUID()
                task.title = item.title
                task.notes = item.notes
                task.completed = false
                task.createdAt = Date()
            }
            do {
                try context.save()
            } catch {
                print("Batch import error: \(error)")
            }
        }
    }
}
```

### SwiftUI 与 CoreData 集成

```swift
import SwiftUI
import CoreData

@main
struct MyApp: App {
    let persistenceController = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}

// 在 View 中使用 @FetchRequest
struct TaskListView: View {
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \TaskEntity.createdAt, ascending: false)],
        animation: .default
    )
    private var tasks: FetchedResults<TaskEntity>

    @State private var showingAddSheet = false

    var body: some View {
        NavigationStack {
            List {
                ForEach(tasks) { task in
                    HStack {
                        Image(systemName: task.completed ? "checkmark.circle.fill" : "circle")
                            .foregroundStyle(task.completed ? .green : .gray)
                        Text(task.title ?? "")
                            .strikethrough(task.completed)
                    }
                    .onTapGesture { task.completed.toggle() }
                }
                .onDelete(perform: deleteTask)
            }
            .navigationTitle("Tasks")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showingAddSheet = true } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddSheet) {
                AddTaskView()
            }
        }
    }

    private func deleteTask(at offsets: IndexSet) {
        offsets.map { tasks[$0] }.forEach { task in
            PersistenceController.shared.container.viewContext.delete(task)
        }
        try? PersistenceController.shared.container.viewContext.save()
    }
}
```

---

## 网络请求

### 使用 async/await

```swift
import Foundation

enum APIError: Error, LocalizedError {
    case invalidURL
    case network(Error)
    case decoding(Error)
    case server(Int, String)
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .network(let e): return "Network error: \(e.localizedDescription)"
        case .decoding(let e): return "Decoding error: \(e)"
        case .server(let code, let msg): return "Server error (\(code)): \(msg)"
        case .unauthorized: return "Please log in again"
        }
    }
}

// 泛型 API Client
class APIClient {
    static let shared = APIClient()

    private let baseURL = URL(string: "https://api.example.com")!
    private let session: URLSession
    private let tokenStore: TokenStore

    init(session: URLSession = .shared, tokenStore: TokenStore = .shared) {
        self.session = session
        self.tokenStore = tokenStore
    }

    func request<T: Decodable>(
        _ endpoint: String,
        method: HTTPMethod = .GET,
        body: Encodable? = nil,
        queryItems: [URLQueryItem] = []
    ) async throws -> T {
        var components = URLComponents(url: baseURL.appendingPathComponent(endpoint), resolvingAgainstBaseURL: false)!
        if !queryItems.isEmpty { components.queryItems = queryItems }

        guard let url = components.url else { throw APIError.invalidURL }

        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = tokenStore.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.network(URLError(.badServerResponse))
        }

        switch httpResponse.statusCode {
        case 200..<300:
            do {
                return try JSONDecoder.apiDecoder.decode(T.self, from: data)
            } catch {
                throw APIError.decoding(error)
            }
        case 401:
            throw APIError.unauthorized
        default:
            let message = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.server(httpResponse.statusCode, message)
        }
    }
}

// HTTP 方法
enum HTTPMethod: String {
    case GET, POST, PUT, PATCH, DELETE
}

// JSONDecoder 扩展
extension JSONDecoder {
    static let apiDecoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        decoder.dateDecodingStrategy = .custom { formatter.date(from: $0.decode(String.self))! }
        return decoder
    }()
}

// 使用示例
struct Post: Codable, Identifiable {
    let id: Int
    let title: String
    let body: String
    let userId: Int
}

class PostService {
    private let client = APIClient.shared

    func fetchPosts() async throws -> [Post] {
        try await client.request("/posts")
    }

    func fetchPost(id: Int) async throws -> Post {
        try await client.request("/posts/\(id)")
    }

    func createPost(title: String, body: String, userId: Int) async throws -> Post {
        struct CreatePostRequest: Encodable {
            let title: String
            let body: String
            let userId: Int
        }
        return try await client.request("/posts", method: .POST, body: CreatePostRequest(
            title: title, body: body, userId: userId
        ))
    }
}
```

### URLSession 上传/下载

```swift
// 文件上传
func uploadImage(_ imageData: Data, fileName: String) async throws -> String {
    let boundary = UUID().uuidString
    var request = URLRequest(url: URL(string: "https://api.example.com/upload")!)
    request.httpMethod = "POST"
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

    var body = Data()
    body.append("--\(boundary)\r\n".data(using: .utf8)!)
    body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
    body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
    body.append(imageData)
    body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
    request.httpBody = body

    let (data, _) = try await URLSession.shared.data(for: request)
    let result = try JSONDecoder().decode(UploadResponse.self, from: data)
    return result.url
}

// 断点续传下载
class DownloadManager: NSObject, URLSessionDownloadDelegate {
    private var progressHandler: ((Double) -> Void)?

    func download(from url: URL, progress: @escaping (Double) -> Void) {
        progressHandler = progress
        let config = URLSessionConfiguration.background(withIdentifier: "com.app.download")
        let session = URLSession(configuration: config, delegate: self, delegateQueue: nil)
        let task = session.downloadTask(with: url)
        task.resume()
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        DispatchQueue.main.async { self.progressHandler?(progress) }
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {
        // 处理下载完成的文件
    }
}
```

---

## 最佳实践

### 开发规范

| 领域 | 推荐 |
|------|------|
| 最低版本 | iOS 16+ (全面采用 SwiftUI 新特性) |
| UI 框架 | 新项目 **SwiftUI**，旧项目可 **UIKit + SwiftUI** 混用 |
| 架构 | **MVVM** + Combine 或 **TCA** (The Composable Architecture) |
| 依赖注入 | **Resolver** 或自建 DI Container |
| 网络 | **async/await** + 泛型 APIClient |
| 本地存储 | **CoreData** (复杂模型) 或 **SwiftData** (iOS 17+) |
| 测试 | **XCTest** + **Quick/Nimble** |
| CI/CD | **Xcode Cloud** 或 **Fastlane** |
| 代码规范 | **SwiftFormat** + **SwiftLint** |

### 性能优化要点

```swift
// 1. 使用 LazyVStack / LazyHStack 替代 VStack/HStack 处理长列表
LazyVStack {
    ForEach(items) { item in
        ItemView(item: item)
    }
}

// 2. 图片缓存
// 使用 Kingfisher 或 AsyncImage + URLCache
URLCache.shared = URLCache(
    memoryCapacity: 50_000_000,   // 50MB
    diskCapacity: 200_000_000,    // 200MB
    diskPath: nil
)

// 3. 避免主线程阻塞
Task.detached(priority: .userInitiated) {
    let processed = await heavyComputation()
    await MainActor.run {
        self.result = processed
    }
}
```

---

## 相关页面

- [[Android开发指南]]
- [[React Native开发指南]]
- [[Flutter跨平台开发]]
- [[移动端架构模式]]

---

> 最后更新：2026-06-28

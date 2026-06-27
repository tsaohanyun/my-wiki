---
title: Android开发指南
aliases:
  - Android开发
  - Kotlin开发
  - Jetpack Compose
  - Android App开发
tags:
  - android
  - kotlin
  - jetpack-compose
  - viewmodel
  - room
  - workmanager
  - mobile-dev
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: Android官方文档、社区最佳实践
difficulty: intermediate
project: AI-Agent
---

# Android开发指南

## 概述

Android 开发以 Kotlin 为主要语言，Jetpack Compose 为现代声明式 UI 框架，配合 ViewModel、Room、WorkManager 等 Jetpack 组件构建高质量应用。本指南涵盖 Compose UI、ViewModel 状态管理、Room 数据库、WorkManager 后台任务等核心内容。

---

## 一、Jetpack Compose

### 1.1 基础 Composable

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun GreetingScreen() {
    var name by remember { mutableStateOf("") }
    var greeting by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = greeting.ifEmpty { "请输入你的名字" },
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("名字") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { greeting = "你好，$name！" },
            modifier = Modifier.fillMaxWidth(),
            enabled = name.isNotBlank()
        ) {
            Text("打招呼")
        }
    }
}
```

### 1.2 LazyColumn（列表）

```kotlin
data class Task(
    val id: Long,
    val title: String,
    val isDone: Boolean,
    val priority: Priority
)

enum class Priority { LOW, MEDIUM, HIGH }

@Composable
fun TaskListScreen(
    tasks: List<Task>,
    onToggle: (Task) -> Unit,
    onDelete: (Task) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            items = tasks,
            key = { it.id }
        ) { task ->
            TaskItem(
                task = task,
                onToggle = { onToggle(task) },
                onDelete = { onDelete(task) }
            )
        }
    }
}

@Composable
fun TaskItem(
    task: Task,
    onToggle: () -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = task.isDone,
                onCheckedChange = { onToggle() }
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = task.title,
                    style = MaterialTheme.typography.bodyLarge,
                    textDecoration = if (task.isDone) TextDecoration.LineThrough else TextDecoration.None
                )
                PriorityChip(priority = task.priority)
            }
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Delete, contentDescription = "删除")
            }
        }
    }
}
```

### 1.3 Navigation Compose

```kotlin
// build.gradle: implementation "androidx.navigation:navigation-compose:2.7.7"

import androidx.navigation.NavType
import androidx.navigation.compose.*
import androidx.navigation.navArgument

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigateToDetail = { id ->
                    navController.navigate("detail/$id")
                }
            )
        }
        composable(
            route = "detail/{taskId}",
            arguments = listOf(navArgument("taskId") { type = NavType.LongType })
        ) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getLong("taskId") ?: -1L
            DetailScreen(taskId = taskId, onBack = { navController.popBackStack() })
        }
        composable("settings") {
            SettingsScreen()
        }
    }
}
```

### 1.4 底部导航栏

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val screens = listOf(
        BottomNavItem("home", "首页", Icons.Default.Home),
        BottomNavItem("search", "搜索", Icons.Default.Search),
        BottomNavItem("profile", "我的", Icons.Default.Person)
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentRoute = navBackStackEntry?.destination?.route

                screens.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = screen.label) },
                        label = { Text(screen.label) },
                        selected = currentRoute == screen.route,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(paddingValues)
        ) {
            composable("home") { HomeScreen() }
            composable("search") { SearchScreen() }
            composable("profile") { ProfileScreen() }
        }
    }
}
```

---

## 二、ViewModel 与状态管理

### 2.1 ViewModel 基础

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class TaskViewModel(
    private val repository: TaskRepository
) : ViewModel() {

    // UI 状态
    private val _uiState = MutableStateFlow(TaskUiState())
    val uiState: StateFlow<TaskUiState> = _uiState.asStateFlow()

    init {
        loadTasks()
    }

    fun loadTasks() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                repository.getAllTasks().collect { tasks ->
                    _uiState.update {
                        it.copy(tasks = tasks, isLoading = false, error = null)
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(isLoading = false, error = e.message)
                }
            }
        }
    }

    fun addTask(title: String, priority: Priority) {
        viewModelScope.launch {
            repository.insert(Task(title = title, isDone = false, priority = priority))
        }
    }

    fun toggleTask(task: Task) {
        viewModelScope.launch {
            repository.update(task.copy(isDone = !task.isDone))
        }
    }

    fun deleteTask(task: Task) {
        viewModelScope.launch {
            repository.delete(task)
        }
    }
}

data class TaskUiState(
    val tasks: List<Task> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

### 2.2 在 Compose 中使用 ViewModel

```kotlin
@Composable
fun TaskScreen(viewModel: TaskViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    var showAddDialog by remember { mutableStateOf(false) }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(onClick = { showAddDialog = true }) {
                Icon(Icons.Default.Add, contentDescription = "添加")
            }
        }
    ) { padding ->
        Box(modifier = Modifier.padding(padding).fillMaxSize()) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }
                uiState.error != null -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("加载失败: ${uiState.error}")
                        Button(onClick = { viewModel.loadTasks() }) {
                            Text("重试")
                        }
                    }
                }
                else -> {
                    TaskListScreen(
                        tasks = uiState.tasks,
                        onToggle = viewModel::toggleTask,
                        onDelete = viewModel::deleteTask
                    )
                }
            }
        }
    }

    if (showAddDialog) {
        AddTaskDialog(
            onDismiss = { showAddDialog = false },
            onConfirm = { title, priority ->
                viewModel.addTask(title, priority)
                showAddDialog = false
            }
        )
    }
}
```

### 2.3 使用 ViewModelFactory + 依赖注入

```kotlin
// 手动 Factory
class TaskViewModelFactory(
    private val repository: TaskRepository
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(TaskViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return TaskViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// 使用
val viewModel: TaskViewModel = viewModel(
    factory = TaskViewModelFactory(repository)
)
```

### 2.4 使用 Hilt 依赖注入

```kotlin
// build.gradle:
// implementation "com.google.dagger:hilt-android:2.51"
// kapt "com.google.dagger:hilt-compiler:2.51"
// implementation "androidx.hilt:hilt-navigation-compose:1.2.0"

@HiltAndroidApp
class MyApp : Application()

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }

    @Provides
    fun provideTaskDao(db: AppDatabase): TaskDao = db.taskDao()
}

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    @Provides
    @Singleton
    fun provideTaskRepository(dao: TaskDao): TaskRepository = TaskRepositoryImpl(dao)
}

@HiltViewModel
class TaskViewModel @Inject constructor(
    private val repository: TaskRepository
) : ViewModel() {
    // ... 同上
}

// 在 Compose 中获取
@Composable
fun TaskScreen() {
    val viewModel: TaskViewModel = hiltViewModel()
    // ...
}
```

---

## 三、Room 数据库

### 3.1 定义 Entity

```kotlin
import androidx.room.*

@Entity(tableName = "tasks")
data class TaskEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val description: String? = null,
    val isDone: Boolean = false,
    val priority: Int = 0,
    val createdAt: Long = System.currentTimeMillis(),
    val dueDate: Long? = null
)

// 关联关系
@Entity(
    tableName = "categories",
    foreignKeys = [
        ForeignKey(
            entity = TaskEntity::class,
            parentColumns = ["id"],
            childColumns = ["taskId"],
            onDelete = ForeignKey.CASCADE
        )
    ]
)
data class CategoryEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String,
    val taskId: Long
)
```

### 3.2 定义 DAO

```kotlin
@Dao
interface TaskDao {

    @Query("SELECT * FROM tasks ORDER BY createdAt DESC")
    fun getAllTasks(): Flow<List<TaskEntity>>

    @Query("SELECT * FROM tasks WHERE isDone = 0 ORDER BY priority DESC")
    fun getPendingTasks(): Flow<List<TaskEntity>>

    @Query("SELECT * FROM tasks WHERE id = :id")
    suspend fun getTaskById(id: Long): TaskEntity?

    @Query("SELECT * FROM tasks WHERE title LIKE '%' || :keyword || '%'")
    fun searchTasks(keyword: String): Flow<List<TaskEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(task: TaskEntity): Long

    @Insert
    suspend fun insertAll(tasks: List<TaskEntity>)

    @Update
    suspend fun update(task: TaskEntity)

    @Delete
    suspend fun delete(task: TaskEntity)

    @Query("DELETE FROM tasks WHERE isDone = 1")
    suspend fun deleteCompletedTasks()

    @Query("SELECT COUNT(*) FROM tasks WHERE isDone = 0")
    fun getPendingCount(): Flow<Int>

    // 事务
    @Transaction
    suspend fun updateAndDelete(old: TaskEntity, new: TaskEntity) {
        delete(old)
        insert(new)
    }
}
```

### 3.3 定义 Database

```kotlin
@Database(
    entities = [TaskEntity::class, CategoryEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun taskDao(): TaskDao
    abstract fun categoryDao(): CategoryDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
```

### 3.4 Repository 模式

```kotlin
class TaskRepositoryImpl(
    private val taskDao: TaskDao
) : TaskRepository {

    override fun getAllTasks(): Flow<List<TaskEntity>> = taskDao.getAllTasks()

    override fun getPendingTasks(): Flow<List<TaskEntity>> = taskDao.getPendingTasks()

    override suspend fun insert(task: TaskEntity): Long = taskDao.insert(task)

    override suspend fun update(task: TaskEntity) = taskDao.update(task)

    override suspend fun delete(task: TaskEntity) = taskDao.delete(task)

    override suspend fun deleteCompleted() = taskDao.deleteCompletedTasks()

    override fun searchTasks(keyword: String): Flow<List<TaskEntity>> =
        taskDao.searchTasks(keyword)
}

interface TaskRepository {
    fun getAllTasks(): Flow<List<TaskEntity>>
    fun getPendingTasks(): Flow<List<TaskEntity>>
    suspend fun insert(task: TaskEntity): Long
    suspend fun update(task: TaskEntity)
    suspend fun delete(task: TaskEntity)
    suspend fun deleteCompleted()
    fun searchTasks(keyword: String): Flow<List<TaskEntity>>
}
```

### 3.5 数据库迁移

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE tasks ADD COLUMN dueDate INTEGER")
    }
}

// 使用
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .addMigrations(MIGRATION_1_2)
    .build()
```

---

## 四、WorkManager 后台任务

### 4.1 定义 Worker

```kotlin
import android.content.Context
import androidx.work.*

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val inputData = inputData.getString("task_id") ?: return Result.failure()

            // 执行同步逻辑
            val apiService = RetrofitClient.apiService
            val response = apiService.syncTasks(inputData)

            if (response.isSuccessful) {
                // 返回结果数据
                Result.success(workDataOf("synced_count" to response.body()?.count))
            } else {
                Result.retry()
            }
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}
```

### 4.2 调度任务

```kotlin
class WorkScheduler(private val context: Context) {

    // 一次性任务
    fun scheduleOneTimeSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()

        val inputData = workDataOf("task_id" to "batch_001")

        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(constraints)
            .setInputData(inputData)
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                OneTimeWorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .addTag("sync_work")
            .build()

        WorkManager.getInstance(context)
            .enqueue(request)
    }

    // 周期性任务（最小间隔 15 分钟）
    fun schedulePeriodicSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // WiFi
            .setRequiresCharging(true)
            .build()

        val request = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .addTag("periodic_sync")
            .build()

        WorkManager.getInstance(context)
            .enqueueUniquePeriodicWork(
                "periodic_sync",
                ExistingPeriodicWorkPolicy.KEEP,
                request
            )
    }

    // 延迟任务
    fun scheduleDelayedWork() {
        val request = OneTimeWorkRequestBuilder<CleanupWorker>()
            .setInitialDelay(30, TimeUnit.MINUTES)
            .build()

        WorkManager.getInstance(context).enqueue(request)
    }

    // 链式任务
    fun scheduleChainedWork() {
        val downloadWork = OneTimeWorkRequestBuilder<DownloadWorker>().build()
        val processWork = OneTimeWorkRequestBuilder<ProcessWorker>().build()
        val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>().build()

        WorkManager.getInstance(context)
            .beginWith(downloadWork)
            .then(processWork)
            .then(uploadWork)
            .enqueue()
    }
}
```

### 4.3 观察任务状态

```kotlin
class WorkStatusViewModel(
    private val workManager: WorkManager
) : ViewModel() {

    fun observeSyncWork(): Flow<WorkInfo?> {
        return workManager
            .getWorkInfosByTagFlow("sync_work")
            .map { infos -> infos.firstOrNull() }
    }

    fun cancelSyncWork() {
        workManager.cancelAllWorkByTag("sync_work")
    }
}

// 在 Compose 中观察
@Composable
fun SyncStatusScreen(viewModel: WorkStatusViewModel) {
    val workInfo by viewModel.observeSyncWork().collectAsState(initial = null)

    when (workInfo?.state) {
        WorkInfo.State.RUNNING -> Text("同步中...")
        WorkInfo.State.SUCCEEDED -> Text("同步成功 ✅")
        WorkInfo.State.FAILED -> Text("同步失败 ❌")
        WorkInfo.State.ENQUEUED -> Text("等待中...")
        else -> Text("空闲")
    }
}
```

---

## 五、网络请求（Retrofit + Coroutines）

```kotlin
// build.gradle:
// implementation "com.squareup.retrofit2:retrofit:2.11.0"
// implementation "com.squareup.retrofit2:converter-moshi:2.11.0"
// implementation "com.squareup.okhttp3:logging-interceptor:4.12.0"

// API 接口
interface ApiService {
    @GET("tasks")
    suspend fun getTasks(): List<TaskDto>

    @POST("tasks")
    suspend fun createTask(@Body task: TaskDto): TaskDto

    @PUT("tasks/{id}")
    suspend fun updateTask(@Path("id") id: Long, @Body task: TaskDto): TaskDto

    @DELETE("tasks/{id}")
    suspend fun deleteTask(@Path("id") id: Long)
}

// Retrofit 客户端
object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"

    val apiService: ApiService by lazy {
        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                    else HttpLoggingInterceptor.Level.NONE
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor())
            .addInterceptor(logging)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}

class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = TokenManager.getToken()
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer $token")
            .addHeader("Accept", "application/json")
            .build()
        return chain.proceed(request)
    }
}
```

---

## 六、最佳实践

### 6.1 项目结构

```
app/src/main/java/com/example/myapp/
├── MyApp.kt                        # Application 类
├── MainActivity.kt                  # 单 Activity 入口
├── core/
│   ├── database/                    # Room 数据库
│   │   ├── AppDatabase.kt
│   │   ├── dao/
│   │   └── entity/
│   ├── network/                     # 网络层
│   │   ├── ApiService.kt
│   │   ├── RetrofitClient.kt
│   │   └── dto/
│   ├── di/                          # 依赖注入模块
│   └── common/                      # 通用工具
├── data/
│   └── repository/                  # Repository 实现
├── domain/
│   ├── model/                       # 领域模型
│   └── repository/                  # Repository 接口
├── features/
│   ├── home/
│   │   ├── HomeScreen.kt
│   │   ├── HomeViewModel.kt
│   │   └── components/
│   ├── task/
│   └── settings/
└── ui/
    ├── theme/                       # Material 主题
    │   ├── Color.kt
    │   ├── Type.kt
    │   └── Theme.kt
    └── components/                  # 共享 UI 组件
```

### 6.2 性能优化清单

| 优化项 | 说明 |
|--------|------|
| 使用 Compose 1.x+ | 最新版本性能优化显著 |
| `key` 参数 | 列表项使用唯一 key 提升 diff 效率 |
| `derivedStateOf` | 减少不必要的重组 |
| `remember` | 避免每次重组时重新计算 |
| 协程 + Flow | 异步操作使用 Kotlin Coroutines |
| ViewBinding | 如使用 View 体系，用 ViewBinding 替代 findViewById |
| ProGuard/R8 | 开启混淆和压缩减小 APK 体积 |
| Baseline Profile | 使用 Macrobenchmark 生成基线配置 |

### 6.3 Compose 性能优化示例

```kotlin
// ✅ 使用 derivedStateOf 减少重组
@Composable
fun TaskCounter(tasks: List<Task>) {
    val pendingCount by remember {
        derivedStateOf { tasks.count { !it.isDone } }
    }
    Text("待完成: $pendingCount")
}

// ✅ 使用 stable 注解避免不必要重组
@Immutable
data class UserState(
    val name: String,
    val avatarUrl: String
)

// ✅ 延迟读取状态
@Composable
fun ScrollHeader(scrollState: ScrollState) {
    val alpha by remember {
        derivedStateOf {
            if (scrollState.value > 100) 1f else scrollState.value / 100f
        }
    }
    // 只在 alpha 变化时重组
}
```

---

## 相关页面

- [[iOS开发指南]] - iOS 平台开发对标
- [[Flutter跨平台开发]] - 跨平台方案对比
- [[React Native开发]] - JS 跨平台方案
- [[移动端架构模式]] - Android 项目架构设计

---

## 参考资源

- [Android 开发者官网](https://developer.android.com/)
- [Jetpack Compose 文档](https://developer.android.com/jetpack/compose)
- [Room 持久化库](https://developer.android.com/training/data-storage/room)
- [WorkManager 指南](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Hilt 依赖注入](https://developer.android.com/training/dependency-injection/hilt-android)
- [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)

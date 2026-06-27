---
title: Flutter跨平台开发
aliases:
  - Flutter开发
  - Flutter Cross Platform
  - Flutter Widget开发
tags:
  - flutter
  - mobile-dev
  - cross-platform
  - dart
  - widget
  - state-management
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: Flutter官方文档、社区最佳实践
difficulty: intermediate
project: AI-Agent
---

# Flutter跨平台开发

## 概述

Flutter 是 Google 推出的开源 UI 工具包，使用 Dart 语言，通过单一代码库构建高性能、高保真的 iOS、Android、Web 和桌面应用。其核心特性包括：热重载（Hot Reload）、自绘引擎（Skia/Impeller）、声明式 UI、丰富的 Widget 库。

---

## 一、Widget 体系

Flutter 中一切皆为 Widget。Widget 分为 `StatelessWidget` 和 `StatefulWidget` 两类。

### 1.1 StatelessWidget

```dart
import 'package:flutter/material.dart';

class GreetingCard extends StatelessWidget {
  final String title;
  final String subtitle;

  const GreetingCard({
    super.key,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}
```

### 1.2 StatefulWidget

```dart
class CounterWidget extends StatefulWidget {
  const CounterWidget({super.key});

  @override
  State<CounterWidget> createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _count = 0;

  void _increment() => setState(() => _count++);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('Count: $_count', style: const TextStyle(fontSize: 32)),
        const SizedBox(height: 16),
        ElevatedButton(
          onPressed: _increment,
          child: const Text('Increment'),
        ),
      ],
    );
  }
}
```

### 1.3 常用布局 Widget

```dart
// Row / Column - 线性布局
Row(
  mainAxisAlignment: MainAxisAlignment.spaceAround,
  children: [
    Icon(Icons.star, color: Colors.amber),
    Icon(Icons.star, color: Colors.amber),
    Icon(Icons.star_border, color: Colors.amber),
  ],
)

// Stack - 层叠布局
Stack(
  alignment: Alignment.center,
  children: [
    Container(width: 200, height: 200, color: Colors.blue),
    Positioned(
      bottom: 10,
      child: Text('Overlay', style: TextStyle(color: Colors.white)),
    ),
  ],
)

// ListView.builder - 列表
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(
      leading: CircleAvatar(child: Text('${index + 1}')),
      title: Text(items[index].title),
      subtitle: Text(items[index].description),
      onTap: () => _handleTap(items[index]),
    );
  },
)
```

---

## 二、状态管理

### 2.1 Provider（官方推荐入门方案）

```dart
// pubspec.yaml: dependencies: provider: ^6.1.0

// 定义 Model
class CounterModel extends ChangeNotifier {
  int _count = 0;
  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }
}

// 在顶层提供
void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CounterModel()),
        // 可添加更多 Provider
      ],
      child: const MyApp(),
    ),
  );
}

// 消费数据
class CounterView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final count = context.watch<CounterModel>().count;

    return Scaffold(
      body: Center(child: Text('$count', style: TextStyle(fontSize: 48))),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.read<CounterModel>().increment(),
        child: Icon(Icons.add),
      ),
    );
  }
}
```

### 2.2 Riverpod（类型安全、可测试）

```dart
// pubspec.yaml: dependencies: flutter_riverpod: ^2.5.0

// 定义 Provider
final counterProvider = StateNotifierProvider<CounterNotifier, int>((ref) {
  return CounterNotifier();
});

class CounterNotifier extends StateNotifier<int> {
  CounterNotifier() : super(0);

  void increment() => state++;
  void decrement() => state--;
  void reset() => state = 0;
}

// 使用 ConsumerWidget
class CounterPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Riverpod Counter')),
      body: Center(child: Text('$count', style: TextStyle(fontSize: 48))),
      floatingActionButton: FloatingActionButton(
        onPressed: () => ref.read(counterProvider.notifier).increment(),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

### 2.3 Bloc / Cubit

```dart
// pubspec.yaml: dependencies: flutter_bloc: ^8.1.0

// 定义 Event 和 State
abstract class CounterEvent {}
class IncrementEvent extends CounterEvent {}
class DecrementEvent extends CounterEvent {}

class CounterState {
  final int count;
  const CounterState(this.count);
}

// 定义 Bloc
class CounterBloc extends Bloc<CounterEvent, CounterState> {
  CounterBloc() : super(const CounterState(0)) {
    on<IncrementEvent>((event, emit) => emit(CounterState(state.count + 1)));
    on<DecrementEvent>((event, emit) => emit(CounterState(state.count - 1)));
  }
}

// 在 UI 中使用 BlocBuilder
BlocBuilder<CounterBloc, CounterState>(
  builder: (context, state) {
    return Text('${state.count}', style: TextStyle(fontSize: 48));
  },
)

// 使用 Cubit（简化版）
class CounterCubit extends Cubit<int> {
  CounterCubit() : super(0);
  void increment() => emit(state + 1);
}
```

---

## 三、路由与导航

### 3.1 命名路由（基础）

```dart
// 定义路由表
MaterialApp(
  initialRoute: '/',
  routes: {
    '/': (context) => const HomePage(),
    '/detail': (context) => const DetailPage(),
    '/settings': (context) => const SettingsPage(),
  },
);

// 导航
Navigator.pushNamed(context, '/detail');
Navigator.pushNamed(context, '/detail', arguments: {'id': 42});

// 接收参数
class DetailPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final args = ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    final id = args['id'];
    return Scaffold(body: Center(child: Text('Item $id')));
  }
}
```

### 3.2 GoRouter（声明式路由，官方推荐）

```dart
// pubspec.yaml: dependencies: go_router: ^14.0.0

final goRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/detail/:id',
      builder: (context, state) {
        final id = state.pathParameters['id']!;
        return DetailPage(id: id);
      },
    ),
    ShellRoute(
      builder: (context, state, child) => MainShell(child: child),
      routes: [
        GoRoute(path: '/home', builder: (_, __) => const HomeTab()),
        GoRoute(path: '/profile', builder: (_, __) => const ProfileTab()),
      ],
    ),
  ],
  // 重定向守卫
  redirect: (context, state) {
    final isLoggedIn = AuthService.instance.isLoggedIn;
    if (!isLoggedIn && state.matchedLocation != '/login') {
      return '/login';
    }
    return null;
  },
);

void main() {
  runApp(MaterialApp.router(routerConfig: goRouter));
}
```

---

## 四、网络请求

### 4.1 使用 dio 进行 HTTP 请求

```dart
// pubspec.yaml: dependencies: dio: ^5.4.0

class ApiService {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: 'https://api.example.com',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
    headers: {'Content-Type': 'application/json'},
  ));

  ApiService() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // 添加 Token
        final token = SecureStorage.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        // 统一错误处理
        if (error.response?.statusCode == 401) {
          // Token 过期处理
        }
        handler.next(error);
      },
    ));
  }

  Future<List<Post>> fetchPosts() async {
    final response = await _dio.get('/posts');
    return (response.data as List)
        .map((json) => Post.fromJson(json))
        .toList();
  }

  Future<Post> createPost(Post post) async {
    final response = await _dio.post('/posts', data: post.toJson());
    return Post.fromJson(response.data);
  }
}
```

### 4.2 JSON 序列化（json_serializable）

```dart
// pubspec.yaml dev_dependencies: json_serializable, build_runner

import 'package:json_annotation/json_annotation.dart';
part 'post.g.dart';

@JsonSerializable()
class Post {
  final int id;
  final String title;
  final String body;
  final int userId;

  Post({required this.id, required this.title, required this.body, required this.userId});

  factory Post.fromJson(Map<String, dynamic> json) => _$PostFromJson(json);
  Map<String, dynamic> toJson() => _$PostToJson(this);
}

// 生成代码: flutter pub run build_runner build
```

---

## 五、插件开发

### 5.1 创建 Flutter Plugin

```bash
flutter create --template=plugin --platforms=android,ios -a kotlin -i swift my_plugin
```

### 5.2 Dart 端接口

```dart
// lib/my_plugin.dart
import 'dart:async';
import 'package:flutter/services.dart';

class MyPlugin {
  static const MethodChannel _channel = MethodChannel('my_plugin');

  static Future<String?> getPlatformVersion() async {
    return await _channel.invokeMethod<String>('getPlatformVersion');
  }

  static Future<void> showToast(String message) async {
    await _channel.invokeMethod<void>('showToast', {'message': message});
  }

  // 事件通道 - 持续通信
  static const EventChannel _eventChannel = EventChannel('my_plugin/events');
  static Stream<dynamic> get sensorStream => _eventChannel.receiveBroadcastStream();
}
```

### 5.3 Android 端实现（Kotlin）

```kotlin
// android/src/main/kotlin/com/example/my_plugin/MyPlugin.kt
package com.example.my_plugin

import android.content.Context
import android.widget.Toast
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugin.common.MethodChannel.MethodCallHandler

class MyPlugin(private val context: Context) : MethodCallHandler {
    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        when (call.method) {
            "getPlatformVersion" -> {
                result.success("Android ${android.os.Build.VERSION.RELEASE}")
            }
            "showToast" -> {
                val message = call.argument<String>("message") ?: ""
                Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
                result.success(null)
            }
            else -> result.notImplemented()
        }
    }
}
```

### 5.4 iOS 端实现（Swift）

```swift
// ios/Classes/MyPlugin.swift
import Flutter
import UIKit

public class MyPlugin: NSObject, FlutterPlugin {
    public static func register(with registrar: FlutterPluginRegistrar) {
        let channel = FlutterMethodChannel(
            name: "my_plugin",
            binaryMessenger: registrar.messenger()
        )
        let instance = MyPlugin()
        registrar.addMethodChannelDelegate(instance, channel: channel)
    }

    public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
        switch call.method {
        case "getPlatformVersion":
            result("iOS \(UIDevice.current.systemVersion)")
        case "showToast":
            if let args = call.arguments as? [String: Any],
               let message = args["message"] as? String {
                // iOS 没有 Toast，可用自定义 View 模拟
                print("Toast: \(message)")
                result(nil)
            }
        default:
            result(FlutterMethodNotImplemented)
        }
    }
}
```

---

## 六、最佳实践

### 6.1 项目结构

```
lib/
├── main.dart                    # 入口文件
├── app.dart                     # App 根 Widget
├── core/                        # 核心通用层
│   ├── constants/
│   ├── theme/
│   ├── utils/
│   └── network/
├── data/                        # 数据层
│   ├── models/
│   ├── repositories/
│   └── datasources/
├── domain/                      # 领域层
│   ├── entities/
│   └── usecases/
├── presentation/                # 展示层
│   ├── pages/
│   ├── widgets/
│   └── providers/
└── router/                      # 路由配置
    └── app_router.dart
```

### 6.2 性能优化清单

| 优化项 | 说明 |
|-------|------|
| `const` 构造器 | 尽可能使用 `const Widget()`，避免不必要的重建 |
| `RepaintBoundary` | 隔离频繁重绘区域 |
| `ListView.builder` | 避免一次性创建全部子项 |
| 图片缓存 | 使用 `cached_network_image` 包 |
| 避免大 Widget 树 | 拆分 Widget，缩小重建范围 |
| 使用 `const` Color/TextStyle | 避免每帧创建新对象 |
| Profile 模式测试 | `flutter run --profile` 检测性能瓶颈 |

### 6.3 代码规范

```dart
// ✅ 好的做法：提取可复用 Widget
class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;

  const PrimaryButton({super.key, required this.label, this.onPressed});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        minimumSize: const Size(double.infinity, 48),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: Text(label),
    );
  }
}

// ❌ 避免：在 build 方法中创建大量对象
@override
Widget build(BuildContext context) {
  // 不要这样做
  final textStyle = TextStyle(fontSize: 16, color: Colors.black);
  final padding = EdgeInsets.all(16);
  final decoration = BoxDecoration(borderRadius: BorderRadius.circular(8));
  // ...
}
```

---

## 相关页面

- [[移动端架构模式]] - MVVM、Clean Architecture 在 Flutter 中的应用
- [[React Native开发]] - 另一个主流跨平台框架对比
- [[iOS开发指南]] - Flutter iOS 平台特定实现
- [[Android开发指南]] - Flutter Android 平台特定实现

---

## 参考资源

- [Flutter 官方文档](https://docs.flutter.dev/)
- [Dart 语言之旅](https://dart.dev/language)
- [Riverpod 文档](https://riverpod.dev/)
- [Bloc 库文档](https://bloclibrary.dev/)
- [GoRouter 文档](https://pub.dev/packages/go_router)
- [Flutter 性能优化最佳实践](https://docs.flutter.dev/perf/best-practices)

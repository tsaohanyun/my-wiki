---
title: "React Native开发指南"
aliases:
  - "RN开发"
  - "React Native"
  - "RN指南"
tags:
  - mobile
  - react-native
  - cross-platform
  - javascript
  - frontend
type: "guide"
status: "active"
created: 2026-06-28
updated: 2026-06-28
source: "AI-Agent Wiki"
difficulty: "intermediate"
project: "Mobile Development"
---

# React Native 开发指南

> React Native 是由 Meta (Facebook) 开发的开源跨平台移动应用框架，使用 JavaScript/TypeScript 编写，可同时编译为 iOS 和 Android 原生应用。

## 目录

- [核心组件](#核心组件)
- [Navigation 导航](#navigation-导航)
- [状态管理](#状态管理)
- [原生模块](#原生模块)
- [性能优化](#性能优化)
- [最佳实践](#最佳实践)
- [相关页面](#相关页面)

---

## 核心组件

### 基础组件概览

| 组件 | 说明 | 类比 Web |
|------|------|----------|
| `View` | 容器组件 | `<div>` |
| `Text` | 文本显示 | `<span>` / `<p>` |
| `Image` | 图片展示 | `<img>` |
| `ScrollView` | 可滚动容器 | overflow scroll div |
| `FlatList` | 高性能列表 | virtual list |
| `TouchableOpacity` | 可点击区域 | `<button>` |
| `TextInput` | 文本输入 | `<input>` |

### 函数组件示例

```tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from 'react-native';

interface Props {
  title: string;
  onSubmit: (value: string) => void;
}

export const SearchBar: React.FC<Props> = ({ title, onSubmit }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = () => {
    if (query.trim()) {
      onSubmit(query.trim());
      setQuery('');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="请输入搜索内容..."
          value={query}
          onChangeText={setQuery}
          returnKeyType="search"
          onSubmitEditing={handleSubmit}
        />
        <TouchableOpacity style={styles.button} onPress={handleSubmit}>
          <Text style={styles.buttonText}>搜索</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 12,
    color: '#1a1a1a',
  },
  inputContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    height: 44,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### FlatList 高性能列表

```tsx
import React, { useCallback } from 'react';
import { FlatList, View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';

interface User {
  id: string;
  name: string;
  avatar: string;
  email: string;
}

export const UserList: React.FC<{ users: User[]; onItemPress: (user: User) => void }> = ({
  users,
  onItemPress,
}) => {
  const renderItem = useCallback(
    ({ item }: { item: User }) => (
      <TouchableOpacity style={styles.card} onPress={() => onItemPress(item)}>
        <Image source={{ uri: item.avatar }} style={styles.avatar} />
        <View style={styles.info}>
          <Text style={styles.name}>{item.name}</Text>
          <Text style={styles.email}>{item.email}</Text>
        </View>
      </TouchableOpacity>
    ),
    [onItemPress]
  );

  const keyExtractor = useCallback((item: User) => item.id, []);

  const ItemSeparatorComponent = useCallback(
    () => <View style={styles.separator} />,
    []
  );

  return (
    <FlatList
      data={users}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      ItemSeparatorComponent={ItemSeparatorComponent}
      onEndReachedThreshold={0.5}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={11}
    />
  );
};

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#fff',
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginRight: 12,
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  email: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  separator: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: '#e0e0e0',
    marginHorizontal: 12,
  },
});
```

---

## Navigation 导航

### React Navigation 安装

```bash
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context
```

### Stack Navigator

```tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Button, Text, View } from 'react-native';

// ===== 类型定义 =====
export type RootStackParamList = {
  Home: undefined;
  Detail: { id: string; title?: string };
  Profile: { userId: string };
};

// ===== 页面组件 =====
const HomeScreen = ({ navigation }) => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>Home Screen</Text>
    <Button
      title="Go to Detail"
      onPress={() => navigation.navigate('Detail', { id: '42', title: '详情页' })}
    />
  </View>
);

const DetailScreen = ({ route, navigation }) => {
  const { id, title } = route.params;
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>{title ?? 'Detail'} - ID: {id}</Text>
      <Button title="Go Back" onPress={() => navigation.goBack()} />
    </View>
  );
};

// ===== 导航配置 =====
const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: '#007AFF' },
          headerTintColor: '#fff',
          headerTitleStyle: { fontWeight: 'bold' },
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: '首页' }}
        />
        <Stack.Screen
          name="Detail"
          component={DetailScreen}
          options={({ route }) => ({ title: route.params.title ?? '详情' })}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### Tab Navigator

```tsx
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#999',
        tabBarStyle: { paddingBottom: 4, height: 56 },
      }}
    >
      <Tab.Screen name="HomeTab" component={HomeScreen} options={{ tabBarLabel: '首页' }} />
      <Tab.Screen name="ProfileTab" component={ProfileScreen} options={{ tabBarLabel: '我的' }} />
    </Tab.Navigator>
  );
}
```

### 深层链接 (Deep Linking)

```tsx
const linking = {
  prefixes: ['myapp://', 'https://myapp.com'],
  config: {
    screens: {
      Home: '',
      Detail: 'detail/:id',
      Profile: 'profile/:userId',
    },
  },
};

<NavigationContainer linking={linking}>
  {/* ... */}
</NavigationContainer>
```

---

## 状态管理

### Zustand (推荐轻量方案)

```tsx
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  token: string | null;
  user: { id: string; name: string; avatar: string } | null;
  isAuthenticated: boolean;
  login: (token: string, user: AuthState['user']) => void;
  logout: () => void;
  updateUser: (partial: Partial<NonNullable<AuthState['user']>>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
      updateUser: (partial) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...partial } : null,
        })),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// 使用示例
function ProfileHeader() {
  const { user, logout } = useAuthStore();
  if (!user) return null;
  return (
    <View>
      <Text>{user.name}</Text>
      <Button title="退出登录" onPress={logout} />
    </View>
  );
}
```

### Redux Toolkit

```tsx
import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Provider, useSelector, useDispatch } from 'react-redux';

// ===== Async Thunk =====
export const fetchPosts = createAsyncThunk(
  'posts/fetchPosts',
  async (_, { rejectWithValue }) => {
    try {
      const res = await fetch('https://api.example.com/posts');
      if (!res.ok) throw new Error('Failed to fetch');
      return await res.json();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

// ===== Slice =====
const postsSlice = createSlice({
  name: 'posts',
  initialState: {
    data: [],
    loading: false,
    error: null as string | null,
  },
  reducers: {
    clearPosts: (state) => {
      state.data = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPosts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPosts.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchPosts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

// ===== Store =====
const store = configureStore({
  reducer: {
    posts: postsSlice.reducer,
  },
});

type RootState = ReturnType<typeof store.getState>;
type AppDispatch = typeof store.dispatch;

// ===== Hooks =====
export const usePosts = () => {
  const { data, loading, error } = useSelector((s: RootState) => s.posts);
  const dispatch = useDispatch<AppDispatch>();
  return { data, loading, error, fetch: () => dispatch(fetchPosts()) };
};

// ===== Provider =====
export default function App() {
  return (
    <Provider store={store}>
      <PostsScreen />
    </Provider>
  );
}
```

---

## 原生模块

### iOS 原生模块 (Swift)

```swift
// MyNativeModule.swift
import Foundation

@objc(MyNativeModule)
class MyNativeModule: NSObject {

  @objc
  func getDeviceBatteryLevel(_ resolve: RCTPromiseResolveBlock, reject: RCTPromiseRejectBlock) {
    UIDevice.current.isBatteryMonitoringEnabled = true
    let level = UIDevice.current.batteryLevel
    if level >= 0 {
      resolve(["level": level, "state": UIDevice.current.batteryState.rawValue])
    } else {
      reject("UNAVAILABLE", "Battery info unavailable", nil)
    }
  }

  @objc
  static func requiresMainQueueSetup() -> Bool {
    return false
  }

  @objc
  func constantsToExport() -> [String: Any]! {
    return ["platform": "iOS"]
  }
}
```

```swift
// MyNativeModule.mm (Objective-C++桥接)
#import <React/RCTBridgeModule.h>

@interface RCT_EXTERN_MODULE(MyNativeModule, NSObject)

RCT_EXTERN_METHOD(getDeviceBatteryLevel:
                  (RCTPromiseResolveBlock)resolve
                  reject:(RCTPromiseRejectBlock)reject)

@end
```

### Android 原生模块 (Kotlin)

```kotlin
// MyNativeModule.kt
package com.myapp

import com.facebook.react.bridge.*
import android.content.Intent
import android.net.Uri

class MyNativeModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String = "MyNativeModule"

    @ReactMethod
    fun openUrl(url: String, promise: Promise) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            reactContext.startActivity(intent)
            promise.resolve(true)
        } catch (e: Exception) {
            promise.reject("OPEN_URL_ERROR", e.message)
        }
    }

    @ReactMethod
    fun getDeviceInfo(promise: Promise) {
        val info = Arguments.createMap().apply {
            putString("model", android.os.Build.MODEL)
            putString("brand", android.os.Build.BRAND)
            putString("version", android.os.Build.VERSION.RELEASE)
            putInt("sdk", android.os.Build.VERSION.SDK_INT)
        }
        promise.resolve(info)
    }

    // 支持事件监听
    @ReactMethod
    fun addListener(eventName: String) { /* Setup */ }

    @ReactMethod
    fun removeListeners(count: Int) { /* Cleanup */ }
}
```

```kotlin
// MyNativePackage.kt
package com.myapp

import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.uimanager.ViewManager

class MyNativePackage : ReactPackage {
    override fun createNativeModules(reactContext: ReactApplicationContext): List<NativeModule> =
        listOf(MyNativeModule(reactContext))

    override fun createViewManagers(reactContext: ReactApplicationContext): List<ViewManager<*, *>> =
        emptyList()
}
```

### JS 侧使用

```tsx
import { NativeModules, Platform, NativeEventEmitter } from 'react-native';

const { MyNativeModule } = NativeModules;

// 调用原生方法
async function getBatteryLevel() {
  try {
    const result = await MyNativeModule.getDeviceBatteryLevel?.();
    console.log('Battery:', result);
  } catch (e) {
    console.error('Native call failed:', e);
  }
}

// 事件监听
const eventEmitter = new NativeEventEmitter(MyNativeModule);
const subscription = eventEmitter.addListener('onSensorUpdate', (data) => {
  console.log('Sensor data:', data);
});

// 清理
useEffect(() => {
  return () => subscription.remove();
}, []);
```

---

## 性能优化

### 1. 列表优化

```tsx
// ✅ 正确：使用 FlatList 并配置优化项
<FlatList
  data={data}
  renderItem={renderItem}
  keyExtractor={keyExtractor}
  removeClippedSubviews={true}   // 卸载屏幕外的组件
  maxToRenderPerBatch={6}        // 减少每批渲染数量
  initialNumToRender={6}         // 首屏渲染项数
  windowSize={10}                // 渲染窗口大小
/>

// ✅ 使用 React.memo 防止不必要重渲染
const ListItem = React.memo(({ item }: { item: User }) => (
  <View>
    <Text>{item.name}</Text>
  </View>
), (prev, next) => prev.item.id === next.item.id);
```

### 2. 图片优化

```tsx
import FastImage from 'react-native-fast-image';

// ✅ 使用 FastImage 替代 Image，支持缓存和占位
<FastImage
  style={styles.image}
  source={{
    uri: imageUrl,
    priority: FastImage.priority.normal,
    cache: FastImage.cacheControl.immutable,
  }}
  resizeMode={FastImage.resizeMode.cover}
/>
```

### 3. Hermes 引擎

```json
// android/app/build.gradle
project.ext.react = [
    enableHermes: true
]
```

```ruby
# ios/Podfile
use_react_native!(
  :hermes_enabled => true
)
```

### 4. 避免内联函数和对象

```tsx
// ❌ 错误：每次渲染都创建新对象
<View style={{ flex: 1, padding: 16 }}>
  <TouchableOpacity onPress={() => handleClick(id)}>
    <Text>Click</Text>
  </TouchableOpacity>
</View>

// ✅ 正确：提取样式和回调
const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
});

const handlePress = useCallback(() => handleClick(id), [id]);

<View style={styles.container}>
  <TouchableOpacity onPress={handlePress}>
    <Text>Click</Text>
  </TouchableOpacity>
</View>
```

### 5. Profiler 性能分析

```tsx
import { useFrameCallback } from 'react-native-reanimated';

// 使用 React Profiler 检测渲染性能
<React.Profiler id="UserList" onRender={(id, phase, actualTime) => {
  if (actualTime > 16) {
    console.warn(`Slow render: ${id} took ${actualTime}ms`);
  }
}}>
  <UserList users={users} />
</React.Profiler>
```

---

## 最佳实践

### 项目结构

```
src/
├── components/        # 可复用组件
│   ├── ui/           # 基础UI组件 (Button, Input, Card)
│   └── business/     # 业务组件
├── screens/          # 页面
├── navigation/       # 导航配置
├── store/            # 状态管理
│   ├── slices/
│   └── index.ts
├── services/         # API 请求
├── hooks/            # 自定义 Hooks
├── utils/            # 工具函数
├── types/            # 类型定义
├── theme/            # 主题配置
│   ├── colors.ts
│   ├── spacing.ts
│   └── typography.ts
└── constants/        # 常量
```

### 开发规范

| 规范 | 建议 |
|------|------|
| 语言 | 始终使用 **TypeScript** |
| 导航 | 使用 **React Navigation v7** |
| 状态管理 | 小项目用 **Zustand**，大型项目用 **Redux Toolkit** |
| 样式 | 使用 **StyleSheet.create** 或 **Tamagui/Unistyles** |
| API 请求 | 使用 **React Query** 管理服务端状态 |
| 代码规范 | 配置 **ESLint + Prettier + Husky** |
| 测试 | **Jest + React Native Testing Library** |
| CI/CD | **Fastlane** 自动化构建发布 |

---

## 相关页面

- [[Flutter跨平台开发]]
- [[移动端架构模式]]
- [[iOS开发基础]]
- [[Android开发指南]]

---

> 最后更新：2026-06-28

---
title: React Native开发
aliases:
  - RN开发
  - React Native
  - RN跨平台
tags:
  - react-native
  - mobile-dev
  - cross-platform
  - javascript
  - typescript
  - navigation
type: guide
status: published
created: 2026-06-28
updated: 2026-06-28
source: React Native官方文档、社区最佳实践
difficulty: intermediate
project: AI-Agent
---

# React Native开发

## 概述

React Native（RN）是 Meta（Facebook）开源的跨平台移动开发框架，使用 JavaScript/TypeScript 编写，渲染为真正的原生组件。核心优势：Learn once, write anywhere、丰富的 npm 生态、热更新支持、大型团队广泛采用。

---

## 一、核心组件

### 1.1 基础组件

```tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Image,
  ActivityIndicator,
} from 'react-native';

interface User {
  id: number;
  name: string;
  email: string;
}

const UserProfile: React.FC<{ user: User }> = ({ user }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user.name);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Image
          source={{ uri: `https://i.pravatar.cc/150?u=${user.id}` }}
          style={styles.avatar}
        />
        {isEditing ? (
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="输入姓名"
          />
        ) : (
          <Text style={styles.name}>{name}</Text>
        )}
        <Text style={styles.email}>{user.email}</Text>

        <TouchableOpacity
          style={styles.button}
          onPress={() => setIsEditing(!isEditing)}
        >
          <Text style={styles.buttonText}>
            {isEditing ? '保存' : '编辑'}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  content: { alignItems: 'center', padding: 24 },
  avatar: { width: 120, height: 120, borderRadius: 60, marginBottom: 16 },
  name: { fontSize: 24, fontWeight: 'bold', color: '#1a1a1a' },
  email: { fontSize: 16, color: '#666', marginBottom: 24 },
  input: {
    fontSize: 24, fontWeight: 'bold',
    borderBottomWidth: 1, borderBottomColor: '#007AFF',
    paddingVertical: 4, width: 200, textAlign: 'center',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 32, paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});

export default UserProfile;
```

### 1.2 使用 FlatList 渲染长列表

```tsx
import { FlatList, ListRenderItem } from 'react-native';

interface Article {
  id: string;
  title: string;
  summary: string;
}

const ArticleList: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      const data = await api.getArticles();
      setArticles(data);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const renderItem: ListRenderItem<Article> = ({ item }) => (
    <TouchableOpacity style={styles.card} onPress={() => navigation.navigate('Detail', { id: item.id })}>
      <Text style={styles.cardTitle}>{item.title}</Text>
      <Text style={styles.cardSummary} numberOfLines={2}>{item.summary}</Text>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <FlatList
      data={articles}
      keyExtractor={(item) => item.id}
      renderItem={renderItem}
      refreshing={refreshing}
      onRefresh={() => { setRefreshing(true); loadArticles(); }}
      onEndReached={loadMore}
      onEndReachedThreshold={0.3}
      ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
      contentContainerStyle={{ padding: 16 }}
    />
  );
};
```

### 1.3 使用 React Native Paper（Material Design 组件库）

```tsx
import { Provider as PaperProvider, Button, Card, TextInput as PaperInput } from 'react-native-paper';

const App = () => (
  <PaperProvider>
    <Card style={{ margin: 16 }}>
      <Card.Title title="登录" subtitle="请输入您的凭据" />
      <Card.Content>
        <PaperInput label="邮箱" mode="outlined" keyboardType="email-address" />
        <PaperInput label="密码" mode="outlined" secureTextEntry style={{ marginTop: 12 }} />
      </Card.Content>
      <Card.Actions>
        <Button mode="contained" onPress={handleLogin}>登录</Button>
      </Card.Actions>
    </Card>
  </PaperProvider>
);
```

---

## 二、Navigation 导航

### 2.1 React Navigation 安装与配置

```bash
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context
# 底部 Tab
npm install @react-navigation/bottom-tabs
# 抽屉导航
npm install @react-navigation/drawer
```

### 2.2 Stack Navigator

```tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

export type RootStackParamList = {
  Home: undefined;
  Detail: { id: string };
  Profile: { userId: number };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

// 类型安全的导航 Hook
import { useNavigation, useRoute } from '@react-navigation/native';

const HomeScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList, 'Home'>>();

  return (
    <TouchableOpacity onPress={() => navigation.navigate('Detail', { id: '123' })}>
      <Text>查看详情</Text>
    </TouchableOpacity>
  );
};

const DetailScreen = () => {
  const route = useRoute<RouteProp<RootStackParamList, 'Detail'>>();
  const { id } = route.params;

  return <Text>详情页 ID: {id}</Text>;
};

const App = () => (
  <NavigationContainer>
    <Stack.Navigator
      initialRouteName="Home"
      screenOptions={{
        headerStyle: { backgroundColor: '#007AFF' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen name="Home" component={HomeScreen} options={{ title: '首页' }} />
      <Stack.Screen name="Detail" component={DetailScreen} options={{ title: '详情' }} />
      <Stack.Screen name="Profile" component={ProfileScreen} />
    </Stack.Navigator>
  </NavigationContainer>
);
```

### 2.3 Bottom Tab Navigator

```tsx
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator();

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        const icons: Record<string, string> = {
          Home: focused ? 'home' : 'home-outline',
          Search: focused ? 'search' : 'search-outline',
          Profile: focused ? 'person' : 'person-outline',
        };
        return <Icon name={icons[route.name]} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#007AFF',
      tabBarInactiveTintColor: '#gray',
    })}
  >
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Search" component={SearchScreen} />
    <Tab.Screen name="Profile" component={ProfileScreen} />
  </Tab.Navigator>
);
```

### 2.4 嵌套导航器

```tsx
// Stack 中嵌套 Tab
<Stack.Navigator>
  <Stack.Screen name="Main" component={MainTabs} options={{ headerShown: false }} />
  <Stack.Screen name="Modal" component={ModalScreen} options={{ presentation: 'modal' }} />
</Stack.Navigator>
```

---

## 三、状态管理

### 3.1 Zustand（轻量级状态管理）

```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  user: User | null;
  token: string | null;
  theme: 'light' | 'dark';
  login: (user: User, token: string) => void;
  logout: () => void;
  toggleTheme: () => void;
}

const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      theme: 'light',
      login: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
      toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
    }),
    { name: 'app-storage' }
  )
);

// 在组件中使用
const ProfileScreen = () => {
  const user = useAppStore((state) => state.user);
  const logout = useAppStore((state) => state.logout);

  if (!user) return <LoginScreen />;
  return (
    <View>
      <Text>{user.name}</Text>
      <Button title="退出" onPress={logout} />
    </View>
  );
};
```

### 3.2 Redux Toolkit（大型项目推荐）

```tsx
import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// 异步 Action
export const fetchArticles = createAsyncThunk(
  'articles/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      return await api.getArticles();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

// Slice
const articlesSlice = createSlice({
  name: 'articles',
  initialState: { items: [], loading: false, error: null },
  reducers: {
    clearArticles: (state) => { state.items = []; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchArticles.pending, (state) => { state.loading = true; })
      .addCase(fetchArticles.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchArticles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

// 配置 Store
const store = configureStore({
  reducer: { articles: articlesSlice.reducer },
});

// 在 App 中注入
import { Provider } from 'react-redux';
<Provider store={store}><App /></Provider>;
```

---

## 四、原生模块开发

### 4.1 创建原生模块（iOS - Swift）

```swift
// ios/MyApp/NativeModule.swift
import Foundation

@objc(NativeModule)
class NativeModule: NSObject {
  @objc static func requiresMainQueueSetup() -> Bool { return false }

  @objc func getDeviceId(_ resolve: RCTPromiseResolveBlock, reject: RCTPromiseRejectBlock) {
    let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? "unknown"
    resolve(deviceId)
  }

  @objc func vibrate(_ pattern: NSDictionary) {
    // 自定义震动
    let style = UIImpactFeedbackGenerator.FeedbackStyle.heavy
    let generator = UIImpactFeedbackGenerator(style: style)
    generator.impactOccurred()
  }
}

// 注册模块
@objc(NativeModule)
extension NativeModule: RCTBridgeModule {
  @objc func constantsToExport() -> [String: Any]! {
    return ["version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] ?? ""]
  }
}
```

### 4.2 创建原生模块（Android - Kotlin）

```kotlin
// android/app/src/main/java/com/myapp/NativeModule.kt
package com.myapp

import android.os.Build
import android.provider.Settings
import com.facebook.react.bridge.*

class NativeModule(reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String = "NativeModule"

    @ReactMethod
    fun getDeviceId(promise: Promise) {
        try {
            val deviceId = Settings.Secure.getString(
                reactApplicationContext.contentResolver,
                Settings.Secure.ANDROID_ID
            )
            promise.resolve(deviceId)
        } catch (e: Exception) {
            promise.reject("DEVICE_ID_ERROR", e.message)
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    fun getApiKey(): String {
        return BuildConfig.API_KEY
    }
}
```

### 4.3 JavaScript 桥接

```tsx
import { NativeModules, Platform } from 'react-native';

const { NativeModule } = NativeModules;

// 调用原生方法
const getDeviceId = async (): Promise<string> => {
  try {
    const id = await NativeModule.getDeviceId();
    return id;
  } catch (e) {
    console.error('获取设备ID失败', e);
    return 'unknown';
  }
};

// TypeScript 类型声明（可选）
declare global {
  namespace NativeModules {
    interface NativeModule {
      getDeviceId: () => Promise<string>;
      vibrate: (pattern: object) => void;
    }
  }
}
```

### 4.4 原生 UI 组件

```tsx
// 创建自定义原生视图
import { requireNativeComponent, ViewProps } from 'react-native';

interface MapViewProps extends ViewProps {
  zoomLevel?: number;
  onRegionChange?: (event: NativeSyntheticEvent<{ latitude: number; longitude: number }>) => void;
}

const NativeMapView = requireNativeComponent<MapViewProps>('RCTMapView');

const MapView: React.FC<MapViewProps> = (props) => (
  <NativeMapView {...props} />
);

export default MapView;
```

---

## 五、性能优化

### 5.1 列表优化

```tsx
// ✅ 使用 FlatList 而非 ScrollView 渲染长列表
// ✅ 正确使用 keyExtractor
// ✅ 使用 getItemLayout 提升滚动性能
<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}
  getItemLayout={(_, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  // 窗口大小优化
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}
/>
```

### 5.2 图片优化

```tsx
// 使用 react-native-fast-image 替代 Image
import FastImage from 'react-native-fast-image';

<FastImage
  style={styles.image}
  source={{
    uri: imageUrl,
    priority: FastImage.priority.normal,
    cache: FastImage.cacheControl.immutable,
  }}
  resizeMode={FastImage.resizeMode.cover}
/>

// 预加载图片
FastImage.preload([
  { uri: 'https://example.com/image1.jpg' },
  { uri: 'https://example.com/image2.jpg' },
]);
```

### 5.3 减少重渲染

```tsx
import React, { memo, useCallback, useMemo } from 'react';

// ✅ 使用 React.memo 避免不必要的重渲染
const ExpensiveItem = memo(({ item, onPress }: Props) => {
  return (
    <TouchableOpacity onPress={onPress}>
      <Text>{item.title}</Text>
    </TouchableOpacity>
  );
});

// ✅ 使用 useCallback 缓存函数引用
const handleItemPress = useCallback((id: string) => {
  navigation.navigate('Detail', { id });
}, [navigation]);

// ✅ 使用 useMemo 缓存计算结果
const sortedItems = useMemo(() => {
  return [...items].sort((a, b) => a.name.localeCompare(b.name));
}, [items]);
```

### 5.4 Hermes 引擎

```groovy
// android/app/build.gradle
project.ext.react = [
    enableHermes: true  // 启用 Hermes JS 引擎
]
```

```ruby
# ios/Podfile
use_react_native!(
  :hermes_enabled => true
)
```

### 5.5 性能检测工具

| 工具 | 用途 |
|------|------|
| Flipper | 调试、网络监控、布局检查 |
| React DevTools | 组件树检查 |
| Flashlight | 性能分析 |
| `console.time` | 简易计时 |

---

## 六、最佳实践

### 6.1 项目结构

```
src/
├── api/                    # API 请求层
│   ├── client.ts           # Axios/请求封装
│   └── endpoints/
├── components/             # 共享组件
│   ├── common/
│   └── ui/
├── navigation/             # 导航配置
│   ├── AppNavigator.tsx
│   └── types.ts
├── screens/                # 页面
│   ├── HomeScreen.tsx
│   └── DetailScreen.tsx
├── store/                  # 状态管理
│   ├── index.ts
│   └── slices/
├── hooks/                  # 自定义 Hooks
├── utils/                  # 工具函数
├── theme/                  # 主题配置
│   ├── colors.ts
│   └── spacing.ts
└── types/                  # TypeScript 类型
```

### 6.2 TypeScript 严格模式

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

---

## 相关页面

- [[Flutter跨平台开发]] - 另一个主流跨平台框架对比
- [[移动端架构模式]] - RN 项目中的架构设计
- [[iOS开发指南]] - RN iOS 原生模块开发
- [[Android开发指南]] - RN Android 原生模块开发

---

## 参考资源

- [React Native 官方文档](https://reactnative.dev/docs/getting-started)
- [React Navigation 文档](https://reactnavigation.org/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Native Paper](https://reactnativepaper.com/)
- [Hermes 引擎](https://hermesengine.dev/)

---
title: MongoDB实战指南
aliases:
  - MongoDB高级教程
  - MongoDB最佳实践
  - Mongo数据库指南
tags:
  - 数据库
  - MongoDB
  - NoSQL
  - 文档数据库
type: 技术指南
status: 已完成
created: 2026-06-27
updated: 2026-06-27
source: 官方文档 + 实战经验
difficulty: 中高级
project: AI-Agent
---

# MongoDB实战指南

## 概述

MongoDB是流行的NoSQL文档数据库，以灵活的文档模型、强大的聚合框架和水平扩展能力著称。

## 1. 文档模型设计

### 1.1 文档结构最佳实践

```javascript
// 用户文档示例
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  username: "john_doe",
  email: "john@example.com",
  profile: {
    firstName: "John",
    lastName: "Doe",
    avatar: "https://example.com/avatar.jpg",
    socialLinks: {
      github: "https://github.com/johndoe",
      twitter: "@johndoe"
    }
  },
  addresses: [
    {
      type: "home",
      street: "123 Main St",
      city: "New York",
      state: "NY",
      zip: "10001",
      isPrimary: true
    },
    {
      type: "work",
      street: "456 Office Blvd",
      city: "New York",
      state: "NY",
      zip: "10002",
      isPrimary: false
    }
  ],
  preferences: {
    language: "en",
    timezone: "America/New_York",
    notifications: {
      email: true,
      sms: false,
      push: true
    }
  },
  createdAt: ISODate("2024-01-15T10:30:00Z"),
  updatedAt: ISODate("2024-06-20T15:45:00Z"),
  version: 3
}
```

### 1.2 嵌入 vs 引用

```javascript
// 方式1：嵌入文档（适用于1:1或1:少量关系）
// 优点：原子更新、单次查询获取所有数据
db.products.insertOne({
  name: "iPhone 15",
  price: 999,
  specifications: {
    screen: "6.1 inch",
    storage: 128,
    color: "Black"
  },
  reviews: [
    { user: "Alice", rating: 5, comment: "Great phone!" },
    { user: "Bob", rating: 4, comment: "Good but expensive" }
  ]
});

// 方式2：引用文档（适用于1:多或需要独立访问的关系）
// 优点：避免文档过大、独立更新
db.orders.insertOne({
  userId: ObjectId("507f1f77bcf86cd799439011"),
  items: [
    { productId: ObjectId("607f1f77bcf86cd799439022"), quantity: 2 },
    { productId: ObjectId("607f1f77bcf86cd799439033"), quantity: 1 }
  ],
  totalAmount: 2997,
  status: "pending",
  createdAt: ISODate()
});

// 查询时使用$lookup关联
db.orders.aggregate([
  { $match: { status: "pending" } },
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" }
]);
```

### 1.3 Schema设计模式

```javascript
// 模式1：多态模式（不同类型的文档存同一集合）
db.notifications.insertOne({
  type: "email",
  recipient: "user@example.com",
  subject: "Welcome!",
  body: "Welcome to our platform",
  sentAt: ISODate()
});

db.notifications.insertOne({
  type: "push",
  userId: ObjectId("507f1f77bcf86cd799439011"),
  title: "New message",
  body: "You have a new message",
  deviceToken: "abc123",
  sentAt: ISODate()
});

// 模式2：桶模式（时间序列数据）
db.sensorReadings.insertOne({
  sensorId: "sensor_001",
  startDate: ISODate("2024-06-01T00:00:00Z"),
  endDate: ISODate("2024-06-01T01:00:00Z"),
  measurements: [
    { timestamp: ISODate("2024-06-01T00:00:00Z"), value: 23.5 },
    { timestamp: ISODate("2024-06-01T00:05:00Z"), value: 23.7 },
    // ... 更多测量值
  ],
  count: 12
});

// 模式3：属性模式（动态属性）
db.products.insertOne({
  name: "Laptop",
  category: "electronics",
  attributes: {
    "brand": "Apple",
    "ram": "16GB",
    "storage": "512GB SSD",
    "screen_size": "13.3 inch",
    "weight": "1.4 kg"
  }
});
```

## 2. 聚合管道

### 2.1 基础聚合操作

```javascript
// 数据统计
db.orders.aggregate([
  // 阶段1：筛选
  { $match: { 
    createdAt: { $gte: ISODate("2024-01-01") },
    status: "completed"
  }},
  // 阶段2：分组
  { $group: {
    _id: { 
      month: { $month: "$createdAt" },
      year: { $year: "$createdAt" }
    },
    totalOrders: { $sum: 1 },
    totalRevenue: { $sum: "$amount" },
    avgOrderValue: { $avg: "$amount" },
    maxOrder: { $max: "$amount" }
  }},
  // 阶段3：排序
  { $sort: { "_id.year": 1, "_id.month": 1 } },
  // 阶段4：格式化输出
  { $project: {
    _id: 0,
    period: { 
      $concat: [
        { $toString: "$_id.year" }, 
        "-", 
        { $toString: "$_id.month" }
      ]
    },
    totalOrders: 1,
    totalRevenue: { $round: ["$totalRevenue", 2] },
    avgOrderValue: { $round: ["$avgOrderValue", 2] }
  }}
]);
```

### 2.2 高级聚合操作

```javascript
// 多集合关联查询
db.orders.aggregate([
  { $match: { status: "completed" } },
  // 关联用户集合
  { $lookup: {
    from: "users",
    localField: "userId",
    foreignField: "_id",
    pipeline: [
      { $project: { name: 1, email: 1 } }
    ],
    as: "user"
  }},
  { $unwind: "$user" },
  // 关联产品集合
  { $unwind: "$items" },
  { $lookup: {
    from: "products",
    localField: "items.productId",
    foreignField: "_id",
    as: "product"
  }},
  { $unwind: "$product" },
  // 按类别统计
  { $group: {
    _id: "$product.category",
    totalSales: { $sum: { $multiply: ["$items.quantity", "$product.price"] } },
    orderCount: { $sum: 1 },
    uniqueCustomers: { $addToSet: "$userId" }
  }},
  { $project: {
    category: "$_id",
    totalSales: 1,
    orderCount: 1,
    uniqueCustomerCount: { $size: "$uniqueCustomers" }
  }},
  { $sort: { totalSales: -1 } }
]);

// 图查找（社交网络）
db.follows.aggregate([
  { $match: { followerId: ObjectId("507f1f77bcf86cd799439011") } },
  { $graphLookup: {
    from: "follows",
    startWith: "$followingId",
    connectFromField: "followingId",
    connectToField: "followerId",
    maxDepth: 2,
    as: "network"
  }},
  { $unwind: "$network" },
  { $group: {
    _id: "$network.followingId",
    connectionDepth: { $min: "$network.depth" }
  }}
]);
```

### 2.3 聚合管道优化

```javascript
// 使用allowDiskUse处理大数据集
db.largeCollection.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 } } }
], { allowDiskUse: true });

// 索引优化：在$match和$sort阶段使用索引
// 确保有合适的索引
db.orders.createIndex({ status: 1, createdAt: -1 });

// 使用$facet进行并行聚合
db.products.aggregate([
  { $facet: {
    "byCategory": [
      { $group: { _id: "$category", count: { $sum: 1 } } }
    ],
    "priceStats": [
      { $group: {
        _id: null,
        avgPrice: { $avg: "$price" },
        minPrice: { $min: "$price" },
        maxPrice: { $max: "$price" }
      }}
    ],
    "topProducts": [
      { $sort: { sales: -1 } },
      { $limit: 10 },
      { $project: { name: 1, sales: 1 } }
    ]
  }}
]);
```

## 3. 索引策略

### 3.1 索引类型

```javascript
// 单字段索引
db.users.createIndex({ email: 1 });

// 复合索引
db.orders.createIndex({ userId: 1, createdAt: -1 });

// 唯一索引
db.users.createIndex({ email: 1 }, { unique: true });

// 文本索引
db.articles.createIndex({ title: "text", content: "text" });

// 地理空间索引
db.places.createIndex({ location: "2dsphere" });

// 哈希索引
db.sessions.createIndex({ sessionId: "hashed" });

// TTL索引（自动过期）
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });

// 部分索引
db.orders.createIndex(
  { status: 1 },
  { partialFilterExpression: { status: "pending" } }
);

// 稀疏索引
db.users.createIndex({ phone: 1 }, { sparse: true });
```

### 3.2 索引优化

```javascript
// 查看集合索引
db.users.getIndexes();

// 查看查询执行计划
db.users.find({ email: "john@example.com" }).explain("executionStats");

// 索引使用统计
db.users.aggregate([{ $indexStats: {} }]);

// 后台创建索引（生产环境）
db.largeCollection.createIndex({ field: 1 }, { background: true });

// 隐藏索引（测试删除影响）
db.users.hideIndex({ email: 1 });
db.users.unhideIndex({ email: 1 });
```

## 4. 分片集群

### 4.1 分片架构

```javascript
// 启用数据库分片
sh.enableSharding("mydb");

// 对集合进行分片
// 范围分片
sh.shardCollection("mydb.orders", { userId: 1 });

// 哈希分片（均匀分布）
sh.shardCollection("mydb.logs", { _id: "hashed" });

// 复合分片键
sh.shardCollection("mydb.events", { tenantId: 1, createdAt: 1 });

// 查看分片状态
sh.status();

// 查看分片分布
db.orders.getShardDistribution();
```

### 4.2 分片键选择

```javascript
// 好的分片键特征：
// 1. 高基数（cardinality）
// 2. 写分布均匀
// 3. 查询隔离性好

// 示例：电商订单分片
// 使用 userId 作为分片键
// 优点：同一用户的订单在同一分片，查询高效
sh.shardCollection("ecommerce.orders", { userId: 1 });

// 示例：日志系统分片
// 使用哈希分片确保均匀分布
sh.shardCollection("logs.entries", { _id: "hashed" });

// 避免的分片键：
// - 单调递增的字段（如ObjectId）会导致热点
// - 低基数字段（如status）会导致数据分布不均
```

### 4.3 集群管理

```javascript
// 添加分片
sh.addShard("shard2/mongo2:27017");

// 移除分片
sh.removeShard("shard3");

// 查看集群配置
use config
db.shards.find();
db.chunks.find();

// 手动分裂块
sh.splitAt("mydb.orders", { userId: 1000 });

// 迁移块
sh.moveChunk("mydb.orders", { userId: 500 }, "shard2");
```

## 5. 事务处理

### 5.1 多文档事务

```javascript
// MongoDB 4.0+ 支持多文档事务
const session = db.getMongo().startSession();
session.startTransaction();

try {
  const users = session.getDatabase("mydb").users;
  const orders = session.getDatabase("mydb").orders;
  
  // 扣减用户余额
  users.updateOne(
    { _id: userId, balance: { $gte: orderAmount } },
    { $inc: { balance: -orderAmount } },
    { session }
  );
  
  // 创建订单
  orders.insertOne({
    userId: userId,
    amount: orderAmount,
    status: "pending",
    createdAt: new Date()
  }, { session });
  
  session.commitTransaction();
  print("Transaction committed");
} catch (error) {
  session.abortTransaction();
  print("Transaction aborted:", error);
} finally {
  session.endSession();
}
```

### 5.2 Change Streams

```javascript
// 监听集合变更
const changeStream = db.orders.watch();

changeStream.on("change", (change) => {
  switch (change.operationType) {
    case "insert":
      print("New order:", change.fullDocument);
      break;
    case "update":
      print("Order updated:", change.documentKey._id);
      break;
    case "delete":
      print("Order deleted:", change.documentKey._id);
      break;
  }
});

// 带过滤的变更流
const pipeline = [
  { $match: { 
    "operationType": { $in: ["insert", "update"] },
    "fullDocument.status": "completed"
  }}
];

const filteredStream = db.orders.watch(pipeline);
```

## 6. 最佳实践

### 6.1 性能优化

- 为常用查询创建合适的索引
- 使用投影限制返回字段
- 避免返回大量数据，使用分页
- 使用 `explain()` 分析查询计划

### 6.2 数据模型设计

- 根据查询模式设计文档结构
- 适度嵌入，避免文档过大（16MB限制）
- 对频繁更新的字段考虑引用而非嵌入
- 使用Schema验证确保数据一致性

### 6.3 运维建议

```javascript
// 启用Schema验证
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email"],
      properties: {
        username: {
          bsonType: "string",
          description: "must be a string and is required"
        },
        email: {
          bsonType: "string",
          pattern: "^.+@.+$",
          description: "must be a valid email"
        }
      }
    }
  }
});

// 定期维护
db.runCommand({ compact: "collection_name" });
db.repairDatabase();
```

## 相关页面

- [[PostgreSQL高级指南]] - 关系型数据库
- [[Redis高级应用]] - 缓存和内存数据库
- [[数据库迁移策略]] - 数据库版本控制和迁移
- [[数据库性能调优]] - 性能优化综合指南

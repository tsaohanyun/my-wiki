project: hermes
---
title: Hermes 常见问题排查
aliases: [故障排查, Troubleshooting, 常见错误]
tags: [hermes, 排错, 运维]
type: guide
status: published
created: 2026-06-27
updated: 2026-06-27
source: session-history
difficulty: intermediate
---
# Hermes 常见问题排查

## 启动警告

### Warning: Unknown toolsets: messaging

**原因**：`config.yaml`中配置了`messaging`toolset，但CLI模式不支持

**解决**：
```bash
# 删除config.yaml中的messaging配置
sed -i '/- messaging/d' ~/.hermes/config.yaml
```

**影响**：无。messaging是给Gateway消息平台模式使用的，CLI模式下本来就不生效。

## 内存问题

### Swap使用过高

**检查**：
```bash
free -h
```

**优化**：
1. 关闭不需要的服务（如hermes dashboard）
2. 清理内存缓存
3. 增加物理内存

## SSH连接问题

### 双向隧道不通

**检查清单**：
1. SSH服务是否运行
2. 防火墙是否放行端口
3. 公钥是否配置正确
4. 跳板机是否正常

详见：[[网络连接拓扑]]

## 相关页面

- [[Hermes-Agent架构总览]]
- [[Hermes-WebUI配置与管理]]
- [[SSH隧道与远程管理]]
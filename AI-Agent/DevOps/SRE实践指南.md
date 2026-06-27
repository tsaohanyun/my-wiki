---
title: SRE实践指南
aliases:
  - SRE Best Practices
  - Site Reliability Engineering
  - 站点可靠性工程
tags:
  - devops
  - sre
  - reliability
  - monitoring
  - incident-management
  - observability
type: reference
status: active
created: 2025-01-15
updated: 2025-01-15
source: internal
difficulty: advanced
project: AI-Agent
---

# SRE实践指南

## 概述

站点可靠性工程（SRE）是一种将软件工程方法应用于基础设施和运维问题的学科。SRE团队通过自动化、监控和事件响应来确保系统的可靠性、可用性和性能。

## SLI/SLO/SLA

### 服务级别指标（SLI）

SLI是衡量服务可靠性的量化指标。

```yaml
# SLI定义示例
sli_definitions:
  availability:
    description: "服务可用性"
    metric: |
      sum(rate(http_requests_total{code!~"5.."}[5m])) 
      / 
      sum(rate(http_requests_total[5m]))
    target: 99.9%
    
  latency:
    description: "请求延迟"
    metric: |
      histogram_quantile(0.99, 
        sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
      )
    target: p99 < 500ms
    
  error_rate:
    description: "错误率"
    metric: |
      sum(rate(http_requests_total{code=~"5.."}[5m])) 
      / 
      sum(rate(http_requests_total[5m]))
    target: < 0.1%
    
  throughput:
    description: "吞吐量"
    metric: |
      sum(rate(http_requests_total[5m]))
    target: > 1000 req/s
```

### 服务级别目标（SLO）

```yaml
# SLO配置
apiVersion: sloth.slok.dev/v1
kind: PrometheusServiceLevel
metadata:
  name: api-service-slo
  namespace: production
spec:
  service: "api-service"
  labels:
    team: "backend"
    tier: "critical"
  
  slos:
    # 可用性SLO
    - name: "availability"
      objective: 99.9
      description: "API可用性SLO"
      sli:
        events:
          error_query: |
            sum(rate(http_requests_total{
              job="api-service",
              code=~"5.."
            }[{{.window}}]))
          total_query: |
            sum(rate(http_requests_total{
              job="api-service"
            }[{{.window}}]))
      alerting:
        name: "HighErrorRate"
        labels:
          severity: critical
        annotations:
          summary: "高错误率警报"
        page_alert:
          labels:
            severity: page
        ticket_alert:
          labels:
            severity: ticket
    
    # 延迟SLO
    - name: "latency"
      objective: 99.0
      description: "API延迟SLO (P99 < 500ms)"
      sli:
        events:
          error_query: |
            sum(rate(http_request_duration_seconds_count{
              job="api-service",
              le="0.5"
            }[{{.window}}]))
          total_query: |
            sum(rate(http_request_duration_seconds_count{
              job="api-service"
            }[{{.window}}]))
      alerting:
        name: "HighLatency"
        labels:
          severity: warning
```

### 服务级别协议（SLA）

```markdown
# 服务级别协议模板

## 1. 服务描述
- 服务名称: [服务名称]
- 服务范围: [描述服务覆盖的功能]
- 排除项: [不在SLA范围内的内容]

## 2. 可用性承诺
- 月度可用性目标: 99.9%
- 计划维护窗口: 每月第一个周日 02:00-06:00 UTC
- 不可用定义: 连续5分钟以上服务不可访问

## 3. 性能承诺
- P50延迟: < 200ms
- P95延迟: < 500ms
- P99延迟: < 1000ms

## 4. 支持响应时间
| 严重程度 | 响应时间 | 解决时间 |
|---------|---------|---------|
| P1-紧急 | 15分钟 | 4小时 |
| P2-高 | 1小时 | 8小时 |
| P3-中 | 4小时 | 24小时 |
| P4-低 | 1个工作日 | 5个工作日 |

## 5. 补偿机制
- 可用性 99.0% - 99.9%: 10%服务信用
- 可用性 95.0% - 99.0%: 25%服务信用
- 可用性 < 95.0%: 50%服务信用

## 6. 报告和审查
- 月度可用性报告
- 季度服务审查会议
- 年度SLA更新
```

## 错误预算

### 错误预算计算

```python
# error_budget.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class ErrorBudget:
    """错误预算管理"""
    
    slo_target: float  # 例如 99.9%
    window_days: int   # 计算窗口（天）
    
    @property
    def allowed_downtime_minutes(self) -> float:
        """允许的停机时间（分钟）"""
        total_minutes = self.window_days * 24 * 60
        return total_minutes * (1 - self.slo_target / 100)
    
    def calculate_budget(
        self,
        total_requests: int,
        failed_requests: int
    ) -> dict:
        """计算当前错误预算状态"""
        
        success_rate = (total_requests - failed_requests) / total_requests * 100
        error_rate = failed_requests / total_requests * 100
        
        # 计算已消耗的错误预算
        allowed_error_rate = 100 - self.slo_target
        budget_consumed = (error_rate / allowed_error_rate) * 100
        
        return {
            "current_sli": success_rate,
            "slo_target": self.slo_target,
            "error_rate": error_rate,
            "allowed_error_rate": allowed_error_rate,
            "budget_consumed_percent": min(budget_consumed, 100),
            "budget_remaining_percent": max(100 - budget_consumed, 0),
            "is_budget_exhausted": budget_consumed >= 100
        }

# 使用示例
budget = ErrorBudget(slo_target=99.9, window_days=30)
result = budget.calculate_budget(
    total_requests=10000000,
    failed_requests=5000
)
print(f"错误预算剩余: {result['budget_remaining_percent']:.1f}%")
```

### 错误预算策略

```yaml
# 错误预算策略配置
error_budget_policies:
  # 预算充足 (>50%)
  budget_healthy:
    condition: "budget_remaining > 50%"
    actions:
      - 允许发布新功能
      - 允许进行计划维护
      - 正常开发节奏
    
  # 预算中等 (25%-50%)
  budget_warning:
    condition: "25% < budget_remaining <= 50%"
    actions:
      - 减少发布频率
      - 增加测试覆盖
      - 优先修复稳定性问题
      - 通知团队领导
    
  # 预算紧张 (10%-25%)
  budget_critical:
    condition: "10% < budget_remaining <= 25%"
    actions:
      - 暂停非关键发布
      - 只允许bug修复
      - 增加监控频率
      - 启动稳定性专项
    
  # 预算耗尽 (<10%)
  budget_exhausted:
    condition: "budget_remaining <= 10%"
    actions:
      - 冻结所有发布
      - 全力修复可靠性问题
      - 升级到管理层
      - 事后复盘
```

### 错误预算告警

```yaml
# Prometheus告警规则
groups:
  - name: error_budget_alerts
    rules:
      # 错误预算消耗警告
      - alert: ErrorBudgetBurnRateHigh
        expr: |
          (
            1 - (
              sum(rate(http_requests_total{code!~"5.."}[1h]))
              /
              sum(rate(http_requests_total[1h]))
            )
          ) > (1 - 0.999)
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "错误预算消耗率过高"
          description: "过去1小时错误预算消耗率超过预期"
      
      # 错误预算即将耗尽
      - alert: ErrorBudgetExhaustedSoon
        expr: |
          (
            1 - (
              sum(rate(http_requests_total{code!~"5.."}[30d]))
              /
              sum(rate(http_requests_total[30d]))
            )
          ) / (1 - 0.999) > 0.8
        for: 1h
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "错误预算即将耗尽"
          description: "错误预算已消耗超过80%"
      
      # 错误预算完全耗尽
      - alert: ErrorBudgetExhausted
        expr: |
          (
            1 - (
              sum(rate(http_requests_total{code!~"5.."}[30d]))
              /
              sum(rate(http_requests_total[30d]))
            )
          ) / (1 - 0.999) >= 1.0
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "错误预算已耗尽"
          description: "错误预算已完全消耗，暂停所有非关键变更"
```

## 事故管理

### 事故响应流程

```
┌──────────────────────────────────────────────────────────────────────┐
│                         事故响应流程                                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │  检测   │───→│  分类   │───→│  响应   │───→│  修复   │          │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │
│       │              │              │              │                 │
│       ▼              ▼              ▼              ▼                 │
│  监控告警        确定严重程度     组建团队       根因分析             │
│  用户报告        分配优先级      通信协调       实施修复             │
│  自动检测        通知相关人员    状态更新       验证修复             │
│                                                                      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                         │
│  │  恢复   │───→│  复盘   │───→│  改进   │                         │
│  └─────────┘    └─────────┘    └─────────┘                         │
│       │              │              │                                │
│       ▼              ▼              ▼                                │
│  服务恢复        时间线回顾      行动项                              │
│  监控验证        根因分析        流程优化                            │
│  用户通知        经验教训        自动化改进                          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 事故严重程度定义

```yaml
# 事故严重程度定义
severity_levels:
  SEV1_CRITICAL:
    description: "核心服务完全不可用"
    examples:
      - 主站完全无法访问
      - 数据丢失或损坏
      - 安全漏洞被利用
    response_time: "15分钟"
    update_frequency: "每30分钟"
    escalation: "立即升级到CTO"
    requires_postmortem: true
    
  SEV2_HIGH:
    description: "核心服务严重降级"
    examples:
      - 服务响应时间>5秒
      - 错误率>10%
      - 部分功能不可用
    response_time: "30分钟"
    update_frequency: "每1小时"
    escalation: "1小时后升级到VP"
    requires_postmortem: true
    
  SEV3_MEDIUM:
    description: "非核心服务受影响"
    examples:
      - 非关键功能异常
      - 性能轻微下降
      - 单个区域问题
    response_time: "2小时"
    update_frequency: "每4小时"
    escalation: "4小时后升级"
    requires_postmortem: false
    
  SEV4_LOW:
    description: "轻微问题"
    examples:
      - UI显示异常
      - 非关键错误日志
      - 边缘场景问题
    response_time: "24小时"
    update_frequency: "每日"
    escalation: "按需升级"
    requires_postmortem: false
```

### 事故响应Playbook

```markdown
# 事故响应Playbook - API服务不可用

## 检测信号
- 监控告警: API错误率>5%
- 用户报告: 无法访问服务
- 合作伙伴: 收到超时错误

## 初始响应 (0-5分钟)
1. 确认事故 - 检查监控面板
2. 创建事故频道 #incident-YYYY-MM-DD-HHMM
3. 通知On-Call团队
4. 更新状态页面为"调查中"

## 诊断步骤 (5-30分钟)
1. 检查服务健康状态
   ```bash
   kubectl get pods -n production
   kubectl logs -f deployment/api-service -n production --tail=100
   ```

2. 检查资源使用
   ```bash
   kubectl top pods -n production
   kubectl describe nodes
   ```

3. 检查依赖服务
   - 数据库连接状态
   - Redis缓存状态
   - 外部API可用性

4. 检查最近变更
   - 最近部署记录
   - 配置变更
   - 证书有效期

## 缓解措施
### 选项1: 回滚部署
```bash
kubectl rollout undo deployment/api-service -n production
```

### 选项2: 扩容
```bash
kubectl scale deployment/api-service --replicas=10 -n production
```

### 选项3: 启用限流
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: rate-limit
spec:
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/udpa.type.v1.TypedStruct
          type_url: type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          value:
            stat_prefix: http_local_rate_limiter
            token_bucket:
              max_tokens: 1000
              tokens_per_fill: 100
              fill_interval: 1s
```

## 沟通模板
### 状态更新模板
```
[UPDATE] YYYY-MM-DD HH:MM UTC
状态: 调查中/识别/修复中/已恢复
影响: [描述当前影响]
进展: [描述采取的措施]
下一步: [描述下一步计划]
ETA: [预计恢复时间]
```

### 恢复确认模板
```
[RESOLVED] YYYY-MM-DD HH:MM UTC
事故已解决
持续时间: X小时Y分钟
根因: [简述根因]
修复措施: [描述采取的措施]
后续行动: [链接到复盘文档]
```

## 事故管理工具配置

### PagerDuty配置

```yaml
# PagerDuty服务配置
service:
  name: "API Service - Production"
  description: "核心API服务"
  escalation_policy: "Engineering Escalation"
  alert_creation: "create_alerts"
  incident_urgency_rule:
    type: "constant"
    urgency: "high"
  
  # 告警规则
  alert_grouping:
    type: "intelligent"
    config:
      timeout: 300
  
  # 自动化动作
  auto_resolution:
    enabled: true
    timeout: 14400  # 4小时
```

### Opsgenie配置

```yaml
# Opsgenie团队配置
team:
  name: "Backend Engineering"
  members:
    - user: "alice@example.com"
      role: "admin"
    - user: "bob@example.com"
      role: "user"
  
  # 轮值配置
  oncall:
    name: "Backend On-Call"
    rotations:
      - name: "Primary"
        start_date: "2025-01-01T00:00:00Z"
        duration:
          type: "weekly"
          length: 1
        participants:
          - type: "user"
            username: "alice@example.com"
          - type: "user"
            username: "bob@example.com"
```

## 事后复盘

### 复盘文档模板

```markdown
# 事故复盘文档

## 基本信息
- **事故ID**: INC-2025-001
- **日期**: 2025-01-15
- **持续时间**: 2小时30分钟 (14:00-16:30 UTC)
- **严重程度**: SEV2
- **主持人**: [姓名]
- **参与者**: [姓名列表]

## 摘要
API服务在2025-01-15 14:00 UTC开始出现间歇性超时，影响约30%的用户请求。
根本原因是数据库连接池配置不当，导致连接耗尽。

## 时间线
| 时间 (UTC) | 事件 |
|-----------|------|
| 14:00 | 监控告警触发: API错误率上升至5% |
| 14:05 | On-Call工程师确认事故，创建事故频道 |
| 14:10 | 开始调查，检查服务日志 |
| 14:20 | 发现数据库连接超时错误 |
| 14:30 | 尝试扩容数据库连接池 |
| 14:45 | 连接池扩容未解决问题 |
| 15:00 | 发现连接泄漏bug |
| 15:30 | 部署热修复版本 |
| 15:45 | 错误率开始下降 |
| 16:00 | 服务完全恢复 |
| 16:30 | 关闭事故，开始复盘 |

## 根本原因分析
### 直接原因
数据库连接池中的连接在异常情况下未正确释放，导致连接泄漏。

### 根本原因
1. **代码缺陷**: 异常处理路径未包含连接释放逻辑
2. **测试不足**: 缺少连接池压力测试
3. **监控缺失**: 未监控连接池使用率

### 5个为什么分析
1. 为什么服务超时? → 数据库连接耗尽
2. 为什么连接耗尽? → 连接泄漏
3. 为什么有连接泄漏? → 异常处理未释放连接
4. 为什么代码有缺陷? → 代码审查未发现
5. 为什么审查未发现? → 缺少连接池测试场景

## 影响评估
- **用户影响**: 约30%用户遇到超时错误
- **业务影响**: 暂无收入损失
- **持续时间**: 2小时30分钟
- **SLI影响**: 月度可用性从99.95%降至99.90%

## 行动项
| 序号 | 行动项 | 负责人 | 截止日期 | 状态 |
|-----|--------|--------|---------|------|
| 1 | 修复连接泄漏bug | Alice | 2025-01-16 | ✅完成 |
| 2 | 添加连接池监控 | Bob | 2025-01-20 | 进行中 |
| 3 | 编写连接池压力测试 | Carol | 2025-01-25 | 待开始 |
| 4 | 更新代码审查清单 | David | 2025-01-22 | 待开始 |
| 5 | 实现自动连接池扩缩容 | Eve | 2025-02-01 | 待开始 |

## 经验教训
### 做得好的
- 快速检测到问题（5分钟内）
- 有效的团队协作
- 及时的用户沟通

### 需要改进的
- 连接池监控不足
- 缺少压力测试
- 代码审查流程需要改进

## 参考资料
- [相关PR](https://github.com/org/repo/pull/123)
- [监控面板](https://grafana.example.com/dashboard/xxx)
- [原始告警](https://pagerduty.com/incidents/xxx)
```

### 复盘会议议程

```markdown
# 复盘会议议程

## 会议信息
- 时间: 事故后48小时内
- 时长: 60分钟
- 参与者: 事故响应团队、相关开发人员、SRE

## 议程
1. **开场 (5分钟)**
   - 说明会议目的和规则
   - 强调无责文化

2. **时间线回顾 (15分钟)**
   - 按时间顺序回顾事件
   - 补充遗漏的信息

3. **根因分析 (20分钟)**
   - 讨论5个为什么
   - 识别系统性问题

4. **行动项讨论 (15分钟)**
   - 确定改进措施
   - 分配责任人
   - 设定截止日期

5. **总结 (5分钟)**
   - 确认行动项
   - 安排跟进会议
```

## 监控和可观测性

### 监控架构

```yaml
# Prometheus配置
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts/*.yml"
  - "recording_rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels:
          [
            __meta_kubernetes_namespace,
            __meta_kubernetes_service_name,
            __meta_kubernetes_endpoint_port_name,
          ]
        action: keep
        regex: default;kubernetes;https

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels:
          [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name
```

### Grafana仪表板

```json
{
  "dashboard": {
    "title": "SRE Dashboard",
    "panels": [
      {
        "title": "Service Availability (SLI)",
        "type": "gauge",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{code!~\"5..\"}[30d])) / sum(rate(http_requests_total[30d])) * 100",
            "legendFormat": "Availability"
          }
        ],
        "thresholds": {
          "steps": [
            { "color": "red", "value": null },
            { "color": "yellow", "value": 99.5 },
            { "color": "green", "value": 99.9 }
          ]
        }
      },
      {
        "title": "Error Budget Remaining",
        "type": "stat",
        "targets": [
          {
            "expr": "(1 - (1 - sum(rate(http_requests_total{code!~\"5..\"}[30d])) / sum(rate(http_requests_total[30d]))) / (1 - 0.999)) * 100",
            "legendFormat": "Budget Remaining"
          }
        ]
      },
      {
        "title": "Request Latency P99",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "P99 Latency"
          }
        ]
      }
    ]
  }
}
```

## 最佳实践

### 1. 可靠性文化

- 建立无责文化
- 鼓励报告问题
- 从失败中学习
- 持续改进流程

### 2. 自动化优先

- 自动化重复任务
- 自动化故障恢复
- 自动化容量管理
- 自动化安全响应

### 3. 渐进式发布

- 使用金丝雀发布
- 蓝绿部署
- 特性标志
- A/B测试

### 4. 容量规划

```python
# 容量规划公式
def calculate_capacity(
    current_rps: float,
    growth_rate: float,
    months: int,
    headroom: float = 1.5
) -> float:
    """计算所需容量"""
    future_rps = current_rps * (1 + growth_rate) ** months
    required_capacity = future_rps * headroom
    return required_capacity

# 示例
current_rps = 1000
monthly_growth = 0.1  # 10%月增长
planning_months = 6
required = calculate_capacity(current_rps, monthly_growth, planning_months)
print(f"6个月后需要容量: {required:.0f} RPS")
```

### 5. 混沌工程

```yaml
# Chaos Mesh实验配置
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-failure
  namespace: production
spec:
  action: pod-failure
  mode: one
  selector:
    labelSelectors:
      app: api-service
  duration: "30s"
  scheduler:
    cron: "@every 1h"

---
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
  namespace: production
spec:
  action: delay
  mode: one
  selector:
    labelSelectors:
      app: database
  delay:
    latency: "100ms"
    jitter: "50ms"
  duration: "5m"
  direction: to
  target:
    selector:
      labelSelectors:
        app: api-service
```

## 相关页面

- [[CI-CD流水线设计]] - 部署可靠性
- [[基础设施即代码]] - 基础设施可靠性
- [[容器安全最佳实践]] - 安全可靠性
- [[GitOps工作流]] - 配置管理可靠性

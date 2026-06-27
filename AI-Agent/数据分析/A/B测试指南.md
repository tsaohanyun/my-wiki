---
title: A/B测试指南
aliases:
  - AB测试
  - A/B Testing Guide
  - 实验设计
  - 分组实验
tags:
  - A/B测试
  - 实验设计
  - 统计学
  - 假设检验
  - 数据分析
type: wiki
status: published
created: 2025-01-01
updated: 2025-01-15
source: 数据分析团队
difficulty: intermediate
project: AI-Agent
---

# A/B测试指南

## 概述

A/B测试（也称分组实验）是通过随机对照实验来比较两个或多个版本效果的统计方法。它是数据驱动决策的核心工具，广泛应用于产品优化、算法评估、UI设计等领域。

---

## 实验设计

### A/B测试流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 1.提出   │───>│ 2.计算   │───>│ 3.实验   │───>│ 4.数据   │───>│ 5.分析   │
│ 假设     │    │ 样本量   │    │ 分流执行 │    │ 收集     │    │ 决策     │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### 假设建立

```python
"""
A/B测试实验设计框架
"""
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

class MetricType(Enum):
    """指标类型"""
    BINARY = "binary"           # 二值型：转化率、点击率
    CONTINUOUS = "continuous"   # 连续型：客单价、停留时长
    COUNT = "count"             # 计数型：访问次数、购买次数

@dataclass
class Metric:
    """实验指标定义"""
    name: str
    metric_type: MetricType
    is_primary: bool = True          # 是否主指标
    baseline_value: float = 0.0      # 基线值
    minimum_detectable_effect: float = 0.0  # 最小可检测效应(MDE)
    direction: str = "increase"      # 期望方向: increase/decrease
    
@dataclass
class Experiment:
    """实验定义"""
    name: str
    hypothesis: str                  # 假设
    metrics: List[Metric]
    variants: List[str] = field(default_factory=lambda: ["control", "treatment"])
    traffic_split: dict = field(default_factory=lambda: {"control": 0.5, "treatment": 0.5})
    significance_level: float = 0.05  # 显著性水平 α
    power: float = 0.80              # 统计功效 1-β
    duration_days: int = 14          # 实验持续天数
    stratification_keys: List[str] = field(default_factory=list)  # 分层维度

# 定义实验示例
experiment = Experiment(
    name="新推荐算法效果验证",
    hypothesis="新推荐算法（基于Transformer）的点击率比基线（协同过滤）提升至少3%",
    metrics=[
        Metric(
            name="CTR",
            metric_type=MetricType.BINARY,
            is_primary=True,
            baseline_value=0.15,
            minimum_detectable_effect=0.03,
            direction="increase"
        ),
        Metric(
            name="人均GMV",
            metric_type=MetricType.CONTINUOUS,
            is_primary=False,
            baseline_value=120.0,
            minimum_detectable_effect=0.05,
            direction="increase"
        ),
        Metric(
            name="页面停留时长",
            metric_type=MetricType.CONTINUOUS,
            is_primary=False,
            baseline_value=180.0,
            minimum_detectable_effect=0.10,
            direction="increase"
        ),
    ],
    traffic_split={"control": 0.5, "treatment": 0.5},
    significance_level=0.05,
    power=0.80,
    duration_days=14,
    stratification_keys=["platform", "user_segment"]
)

print(f"实验: {experiment.name}")
print(f"假设: {experiment.hypothesis}")
print(f"主指标: {experiment.metrics[0].name} (MDE={experiment.metrics[0].minimum_detectable_effect*100}%)")
```

---

## 统计显著性

### 假设检验基础

```python
import numpy as np
from scipy import stats

class ABTestAnalyzer:
    """A/B测试统计分析"""
    
    def __init__(self, alpha=0.05):
        self.alpha = alpha
    
    def two_proportion_ztest(self, 
                              n_control, conv_control,
                              n_treatment, conv_treatment):
        """
        双比例Z检验（适用于二值型指标如转化率）
        
        H₀: p_treatment - p_control = 0
        H₁: p_treatment - p_control ≠ 0
        """
        p_control = conv_control / n_control
        p_treatment = conv_treatment / n_treatment
        
        # 合并比例
        p_pool = (conv_control + conv_treatment) / (n_control + n_treatment)
        
        # 标准误
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n_control + 1/n_treatment))
        
        # Z统计量
        z_stat = (p_treatment - p_control) / se
        
        # p值（双尾检验）
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        # 置信区间
        se_diff = np.sqrt(p_control*(1-p_control)/n_control + 
                          p_treatment*(1-p_treatment)/n_treatment)
        z_crit = stats.norm.ppf(1 - self.alpha/2)
        ci_lower = (p_treatment - p_control) - z_crit * se_diff
        ci_upper = (p_treatment - p_control) + z_crit * se_diff
        
        # 相对提升
        lift = (p_treatment - p_control) / p_control * 100
        
        return {
            'control_rate': p_control,
            'treatment_rate': p_treatment,
            'absolute_diff': p_treatment - p_control,
            'relative_lift_pct': lift,
            'z_statistic': z_stat,
            'p_value': p_value,
            'ci_95': (ci_lower, ci_upper),
            'significant': p_value < self.alpha
        }
    
    def two_sample_ttest(self, 
                         control_values, treatment_values):
        """
        双样本t检验（适用于连续型指标如客单价）
        
        H₀: μ_treatment - μ_control = 0
        H₁: μ_treatment - μ_control ≠ 0
        """
        control_values = np.array(control_values)
        treatment_values = np.array(treatment_values)
        
        # Welch's t-test（不假设方差齐性）
        t_stat, p_value = stats.ttest_ind(
            treatment_values, control_values, equal_var=False
        )
        
        # 置信区间
        n_c, n_t = len(control_values), len(treatment_values)
        mean_c, mean_t = control_values.mean(), treatment_values.mean()
        var_c, var_t = control_values.var(ddof=1), treatment_values.var(ddof=1)
        
        se = np.sqrt(var_c/n_c + var_t/n_t)
        df = (var_c/n_c + var_t/n_t)**2 / (
            (var_c/n_c)**2/(n_c-1) + (var_t/n_t)**2/(n_t-1)
        )
        t_crit = stats.t.ppf(1 - self.alpha/2, df)
        diff = mean_t - mean_c
        ci_lower = diff - t_crit * se
        ci_upper = diff + t_crit * se
        
        # Cohen's d 效应量
        pooled_std = np.sqrt(((n_c-1)*var_c + (n_t-1)*var_t) / (n_c+n_t-2))
        cohens_d = diff / pooled_std
        
        return {
            'control_mean': mean_c,
            'treatment_mean': mean_t,
            'absolute_diff': diff,
            'relative_lift_pct': (diff / mean_c) * 100 if mean_c != 0 else float('inf'),
            't_statistic': t_stat,
            'degrees_of_freedom': df,
            'p_value': p_value,
            'ci_95': (ci_lower, ci_upper),
            'cohens_d': cohens_d,
            'significant': p_value < self.alpha
        }

# ===== 使用示例 =====
analyzer = ABTestAnalyzer(alpha=0.05)

# 示例1：转化率A/B测试
print("=" * 60)
print("实验1: 点击率A/B测试")
print("=" * 60)
result = analyzer.two_proportion_ztest(
    n_control=50000, conv_control=7500,    # 对照组: 15% CTR
    n_treatment=50000, conv_treatment=8000  # 实验组: 16% CTR
)
print(f"对照组CTR: {result['control_rate']:.4f} ({result['control_rate']*100:.2f}%)")
print(f"实验组CTR: {result['treatment_rate']:.4f} ({result['treatment_rate']*100:.2f}%)")
print(f"相对提升: {result['relative_lift_pct']:.2f}%")
print(f"Z统计量: {result['z_statistic']:.4f}")
print(f"P值: {result['p_value']:.6f}")
print(f"95%置信区间: [{result['ci_95'][0]:.4f}, {result['ci_95'][1]:.4f}]")
print(f"结论: {'统计显著 ✅' if result['significant'] else '不显著 ❌'}")

# 示例2：客单价A/B测试
print("\n" + "=" * 60)
print("实验2: 客单价A/B测试")
print("=" * 60)
np.random.seed(42)
control_gmv = np.random.lognormal(mean=4.5, sigma=0.8, size=5000)
treatment_gmv = np.random.lognormal(mean=4.55, sigma=0.8, size=5000)

result2 = analyzer.two_sample_ttest(control_gmv, treatment_gmv)
print(f"对照组均值: ¥{result2['control_mean']:.2f}")
print(f"实验组均值: ¥{result2['treatment_mean']:.2f}")
print(f"相对提升: {result2['relative_lift_pct']:.2f}%")
print(f"P值: {result2['p_value']:.6f}")
print(f"Cohen's d: {result2['cohens_d']:.4f}")
print(f"结论: {'统计显著 ✅' if result2['significant'] else '不显著 ❌'}")
```

### 多重检验校正

```python
from statsmodels.stats.multitest import multipletests

class MultipleTestingCorrector:
    """多重比较校正"""
    
    @staticmethod
    def bonferroni(p_values, alpha=0.05):
        """Bonferroni校正（最保守）"""
        reject, corrected_p, _, _ = multipletests(p_values, alpha=alpha, method='bonferroni')
        return reject, corrected_p
    
    @staticmethod
    def benjamini_hochberg(p_values, alpha=0.05):
        """BH方法控制FDR（推荐）"""
        reject, corrected_p, _, _ = multipletests(p_values, alpha=alpha, method='fdr_bh')
        return reject, corrected_p
    
    @staticmethod
    def holm(p_values, alpha=0.05):
        """Holm-Bonferroni方法"""
        reject, corrected_p, _, _ = multipletests(p_values, alpha=alpha, method='holm')
        return reject, corrected_p

# 示例：同时测试5个指标
p_values = [0.012, 0.043, 0.001, 0.215, 0.038]
metric_names = ["CTR", "GMV", "转化率", "跳出率", "停留时长"]

corrector = MultipleTestingCorrector()

print("多重检验校正结果:")
print("-" * 70)
print(f"{'指标':<10} {'原始P值':<10} {'Bonferroni':<12} {'BH-FDR':<12} {'Holm':<10}")
print("-" * 70)

_, bonf_p = corrector.bonferroni(p_values)
_, bh_p = corrector.benjamini_hochberg(p_values)
_, holm_p = corrector.holm(p_values)

for i, name in enumerate(metric_names):
    print(f"{name:<10} {p_values[i]:<10.4f} {bonf_p[i]:<12.4f} {bh_p[i]:<12.4f} {holm_p[i]:<10.4f}")
```

---

## 样本量计算

```python
from scipy.stats import norm

def calculate_sample_size_binary(baseline_rate, mde, alpha=0.05, power=0.80):
    """
    计算二值型指标（如转化率）所需的样本量
    
    参数:
        baseline_rate: 基线转化率
        mde: 最小可检测效应（相对提升）
        alpha: 显著性水平
        power: 统计功效
    """
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    
    # 标准公式
    n = ((z_alpha * np.sqrt(2 * p1 * (1 - p1)) +
          z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p2 - p1) ** 2
    
    return int(np.ceil(n))

def calculate_sample_size_continuous(baseline_mean, baseline_std, mde, alpha=0.05, power=0.80):
    """
    计算连续型指标（如客单价）所需的样本量
    
    参数:
        baseline_mean: 基线均值
        baseline_std: 基线标准差
        mde: 最小可检测效应（相对提升）
        alpha: 显著性水平
        power: 统计功效
    """
    delta = baseline_mean * mde  # 绝对差异
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    
    n = 2 * ((z_alpha + z_beta) * baseline_std / delta) ** 2
    
    return int(np.ceil(n))

# 计算示例
print("样本量计算结果:")
print("=" * 60)

# 场景1：转化率从15%提升5%
n1 = calculate_sample_size_binary(baseline_rate=0.15, mde=0.05)
print(f"转化率 15% → 15.75% (MDE=5%): 每组需要 {n1:,} 样本")

# 场景2：转化率从15%提升10%
n2 = calculate_sample_size_binary(baseline_rate=0.15, mde=0.10)
print(f"转化率 15% → 16.5% (MDE=10%): 每组需要 {n2:,} 样本")

# 场景3：客单价提升5%
n3 = calculate_sample_size_continuous(
    baseline_mean=120, baseline_std=80, mde=0.05
)
print(f"客单价 ¥120 提升5%: 每组需要 {n3:,} 样本")

# 场景4：根据日流量计算所需天数
daily_traffic = 10000
n_needed = calculate_sample_size_binary(baseline_rate=0.15, mde=0.03)
days = int(np.ceil(n_needed * 2 / daily_traffic))
print(f"\n日流量 {daily_traffic:,}，检测3%提升需要 {days} 天")
```

### 序贯检验（可提前停止）

```python
class SequentialTester:
    """
    序贯检验：允许在实验过程中进行中期分析，
    在保证错误率的前提下可以提前停止实验
    """
    
    def __init__(self, alpha=0.05, max_looks=5):
        self.alpha = alpha
        self.max_looks = max_looks
        # O'Brien-Fleming边界
        self.boundaries = self._obrien_fleming_boundaries()
    
    def _obrien_fleming_boundaries(self):
        """计算O'Brien-Fleming停止边界"""
        from scipy.stats import norm
        boundaries = []
        for k in range(1, self.max_looks + 1):
            # OBF boundary
            z_boundary = norm.ppf(1 - self.alpha/2) * np.sqrt(self.max_looks / k)
            p_boundary = 2 * (1 - norm.cdf(z_boundary))
            boundaries.append({
                'look': k,
                'z_boundary': z_boundary,
                'p_boundary': p_boundary
            })
        return boundaries
    
    def check_stopping(self, look_number, p_value):
        """检查是否可以提前停止"""
        if look_number > self.max_looks:
            return False, "超出最大分析次数"
        
        boundary = self.boundaries[look_number - 1]
        can_stop = p_value <= boundary['p_boundary']
        
        return can_stop, {
            'look': look_number,
            'p_value': p_value,
            'boundary': boundary['p_boundary'],
            'decision': '停止实验 - 显著' if can_stop else '继续实验'
        }

# 示例
seq_tester = SequentialTester(alpha=0.05, max_looks=5)
print("O'Brien-Fleming 序贯检验边界:")
print("-" * 50)
for b in seq_tester.boundaries:
    print(f"  第{b['look']}次分析: Z边界={b['z_boundary']:.3f}, P边界={b['p_boundary']:.4f}")

# 模拟中期分析
print("\n模拟中期分析:")
mock_p_values = [0.12, 0.045, 0.008]
for i, p in enumerate(mock_p_values):
    can_stop, info = seq_tester.check_stopping(i + 1, p)
    print(f"  第{i+1}次分析: P值={p:.4f}, 边界={info['boundary']:.4f} → {info['decision']}")
```

---

## 结果分析

### 实验结果报告

```python
import pandas as pd
from datetime import datetime

class ExperimentReport:
    """实验结果报告生成"""
    
    def __init__(self, experiment: Experiment):
        self.experiment = experiment
        self.results = {}
    
    def add_result(self, metric_name, analysis_result):
        self.results[metric_name] = analysis_result
    
    def generate_report(self) -> str:
        """生成Markdown格式的实验报告"""
        lines = [
            f"# 实验报告: {self.experiment.name}",
            f"",
            f"## 基本信息",
            f"- **假设**: {self.experiment.hypothesis}",
            f"- **实验周期**: {self.experiment.duration_days} 天",
            f"- **显著性水平**: α = {self.experiment.significance_level}",
            f"- **统计功效**: 1-β = {self.experiment.power}",
            f"- **流量分配**: {self.experiment.traffic_split}",
            f"",
            f"## 指标结果",
            f"",
            f"| 指标 | 对照组 | 实验组 | 相对提升 | P值 | 95%CI | 结论 |",
            f"|------|--------|--------|----------|-----|-------|------|",
        ]
        
        for metric in self.experiment.metrics:
            if metric.name in self.results:
                r = self.results[metric.name]
                sig = "✅ 显著" if r['significant'] else "❌ 不显著"
                
                if metric.metric_type == MetricType.BINARY:
                    ctrl = f"{r['control_rate']*100:.2f}%"
                    treat = f"{r['treatment_rate']*100:.2f}%"
                else:
                    ctrl = f"{r['control_mean']:.2f}"
                    treat = f"{r['treatment_mean']:.2f}"
                
                lines.append(
                    f"| {metric.name} | {ctrl} | {treat} | "
                    f"{r['relative_lift_pct']:+.2f}% | {r['p_value']:.4f} | "
                    f"[{r['ci_95'][0]:.4f}, {r['ci_95'][1]:.4f}] | {sig} |"
                )
        
        lines.extend([
            "",
            "## 结论与建议",
        ])
        
        # 自动结论
        primary_result = self.results.get(self.experiment.metrics[0].name)
        if primary_result and primary_result['significant']:
            lift = primary_result['relative_lift_pct']
            if lift > 0:
                lines.append(f"- ✅ **主指标{self.experiment.metrics[0].name}显著提升 {lift:+.2f}%，建议上线实验版本**")
            else:
                lines.append(f"- ❌ **主指标显著下降 {lift:+.2f}%，不建议上线**")
        else:
            lines.append(f"- ⚠️ **主指标未达到统计显著性，建议延长实验或增加流量**")
        
        return "\n".join(lines)
    
    def save_report(self, filepath):
        report = self.generate_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        return report

# 生成报告
report = ExperimentReport(experiment)
report.add_result("CTR", analyzer.two_proportion_ztest(
    n_control=50000, conv_control=7500,
    n_treatment=50000, conv_treatment=8000
))
report_content = report.generate_report()
print(report_content)
```

### 常见陷阱与规避

| 陷阱 | 说明 | 规避方法 |
|------|------|----------|
| 偷看数据 | 实验未完成就下结论 | 使用序贯检验或固定分析时间 |
| 新奇效应 | 用户因新鲜感短暂提升 | 观察趋势是否稳定，延长实验 |
| 辛普森悖论 | 整体显著但分组不一致 | 检查分层分析结果 |
| 样本污染 | 用户在组间切换 | 用设备ID而非用户ID分组 |
| 多重比较 | 测试太多指标导致假阳性 | 使用BH-FDR或Bonferroni校正 |
| 季节效应 | 特殊时期影响数据 | 使用同期对照或去除异常日期 |
| 溢出效应 | 实验组影响对照组 | 地理分组或集群随机化 |

---

## 最佳实践

1. **明确主指标**：实验前确定1-2个主指标，避免事后挑选指标
2. **预注册实验**：在实验前记录假设、指标、样本量计划
3. **SSS检查**：确保样本量（Sample）、显著性（Significance）、效应量（Size）合理
4. **实验时长**：至少覆盖一个完整的业务周期（通常≥2周）
5. **AA测试**：在正式实验前运行AA测试验证分流系统正确性
6. **护栏指标**：设置护栏指标（如系统延迟、错误率），一旦恶化立即停止
7. **分层分析**：对不同用户群体进行分层分析，发现异质性效果
8. **网络效应**：注意社交类产品的实验溢出效应
9. **文档记录**：完整记录实验设计、执行过程和分析结论
10. **长期效果**：重要决策前进行回溯分析，验证效果是否持续

```python
# AA测试验证代码
def aa_test(control_a, control_b, n_simulations=1000):
    """
    AA测试：验证两组对照组之间无系统性差异
    """
    false_positive_count = 0
    alpha = 0.05
    
    for _ in range(n_simulations):
        # 随机抽样
        sample_a = np.random.choice(control_a, size=5000, replace=True)
        sample_b = np.random.choice(control_b, size=5000, replace=True)
        
        _, p_value = stats.ttest_ind(sample_a, sample_b)
        if p_value < alpha:
            false_positive_count += 1
    
    fpr = false_positive_count / n_simulations
    print(f"AA测试假阳性率: {fpr:.1%} (期望接近 {alpha:.1%})")
    print(f"结论: {'分流正常 ✅' if abs(fpr - alpha) < 0.02 else '分流存在问题 ⚠️'}")
    return fpr
```

---

## 相关页面

- [[机器学习入门]] - 算法效果对比实验
- [[深度学习基础]] - 模型A/B测试与灰度发布
- [[数据仓库设计]] - 实验数据的存储设计
- [[实时数据处理]] - 实时实验指标监控与告警

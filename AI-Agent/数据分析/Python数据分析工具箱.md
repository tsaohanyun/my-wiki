---
title: Python数据分析工具箱
aliases: [Python分析, 数据分析工具, Pandas工具]
tags: [python, 数据分析, pandas]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 数据分析
---
# Python 数据分析工具箱

## 概述

本工具箱提供Python数据分析的常用代码模板和最佳实践。

## 1. 数据读取

### CSV文件

```python
import pandas as pd

# 读取CSV
df = pd.read_csv('data.csv', encoding='utf-8')

# 指定列
df = pd.read_csv('data.csv', usecols=['col1', 'col2'])

# 指定数据类型
df = pd.read_csv('data.csv', dtype={'id': str, 'amount': float})
```

### Excel文件

```python
# 读取Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# 读取多个sheet
sheets = pd.read_excel('data.xlsx', sheet_name=None)
```

### 数据库

```python
import pymysql

# 连接MySQL
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    database='mydb'
)

# 读取数据
df = pd.read_sql('SELECT * FROM table_name', conn)
```

## 2. 数据清洗

### 缺失值处理

```python
# 检查缺失值
df.isnull().sum()

# 删除缺失值
df.dropna()

# 填充缺失值
df.fillna(0)
df.fillna(df.mean())
df.fillna(method='ffill')
```

### 重复值处理

```python
# 检查重复值
df.duplicated().sum()

# 删除重复值
df.drop_duplicates()

# 按指定列去重
df.drop_duplicates(subset=['col1', 'col2'])
```

### 数据类型转换

```python
# 转换类型
df['date'] = pd.to_datetime(df['date'])
df['amount'] = df['amount'].astype(float)
df['id'] = df['id'].astype(str)
```

## 3. 数据分析

### 描述性统计

```python
# 基本统计
df.describe()

# 分组统计
df.groupby('category')['amount'].agg(['mean', 'sum', 'count'])

# 透视表
pd.pivot_table(df, values='amount', index='category', columns='type', aggfunc='sum')
```

### 时间序列分析

```python
# 设置时间索引
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# 重采样
df.resample('M')['amount'].sum()  # 按月汇总
df.resample('W')['amount'].mean()  # 按周平均

# 滚动计算
df['MA7'] = df['amount'].rolling(window=7).mean()  # 7日移动平均
```

### 相关性分析

```python
# 计算相关系数
correlation = df[['col1', 'col2', 'col3']].corr()

# 可视化
import seaborn as sns
sns.heatmap(correlation, annot=True, cmap='coolwarm')
```

## 4. 数据可视化

### Matplotlib

```python
import matplotlib.pyplot as plt

# 折线图
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['amount'])
plt.title('Amount Trend')
plt.xlabel('Date')
plt.ylabel('Amount')
plt.show()

# 柱状图
df.groupby('category')['amount'].sum().plot(kind='bar')

# 饼图
df['category'].value_counts().plot(kind='pie', autopct='%1.1f%%')
```

### Plotly

```python
import plotly.express as px

# 交互式图表
fig = px.line(df, x='date', y='amount', color='category')
fig.show()

# 散点图
fig = px.scatter(df, x='col1', y='col2', size='amount', color='category')
fig.show()
```

## 5. 常用函数

### 数据筛选

```python
# 条件筛选
df[df['amount'] > 100]
df[df['category'].isin(['A', 'B'])]
df[(df['amount'] > 100) & (df['category'] == 'A')]

# 查询
df.query('amount > 100 and category == "A"')
```

### 数据转换

```python
# 应用函数
df['amount_log'] = df['amount'].apply(lambda x: np.log(x))

# 映射
df['status'] = df['code'].map({1: '正常', 0: '异常'})

# 分箱
df['level'] = pd.cut(df['amount'], bins=[0, 100, 500, 1000], labels=['低', '中', '高'])
```

### 字符串处理

```python
# 提取数字
df['number'] = df['text'].str.extract('(\d+)')

# 替换
df['text'] = df['text'].str.replace('old', 'new')

# 拆分
df['parts'] = df['text'].str.split(',')
```

## 相关页面

- [[SQL查询模板]]
- [[数据可视化工具]]
- [[数据质量工具箱]]
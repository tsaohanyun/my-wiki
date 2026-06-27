---
title: Python数据处理
aliases:
  - Python数据处理
  - Data Processing
tags:
  - python
  - pandas
  - data
  - data-cleaning
  - data-transformation
  - big-data
  - etl
type: wiki
status: published
created: 2026-06-28
updated: 2026-06-28
source: ""
difficulty: advanced
project: AI-Agent
---

# Python数据处理

Python是数据处理领域的首选语言，Pandas、NumPy等库提供了强大的数据处理能力。本页面涵盖从基础操作到高级数据处理的完整实战指南。

## 1. Pandas高级操作

### 1.1 数据读取与写入

```python
import pandas as pd
import numpy as np
from pathlib import Path
import json

# 读取CSV文件
def read_csv_advanced():
    """高级CSV读取"""
    # 基本读取
    df = pd.read_csv('data.csv')
    
    # 指定编码和分隔符
    df = pd.read_csv('data.csv', encoding='utf-8', sep=',')
    
    # 指定列
    df = pd.read_csv('data.csv', usecols=['col1', 'col2', 'col3'])
    
    # 指定数据类型
    df = pd.read_csv('data.csv', dtype={'id': str, 'value': float})
    
    # 解析日期
    df = pd.read_csv('data.csv', parse_dates=['date_column'])
    
    # 处理大文件（分块读取）
    chunks = pd.read_csv('large_data.csv', chunksize=10000)
    df = pd.concat(chunks, ignore_index=True)
    
    return df

# 读取Excel文件
def read_excel_advanced():
    """高级Excel读取"""
    # 读取指定sheet
    df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
    
    # 读取多个sheet
    all_sheets = pd.read_excel('data.xlsx', sheet_name=None)
    
    # 指定列范围
    df = pd.read_excel('data.xlsx', usecols='A:D')
    
    # 跳过行
    df = pd.read_excel('data.xlsx', skiprows=2, nrows=100)
    
    return df

# 读取JSON数据
def read_json_advanced():
    """高级JSON读取"""
    # 读取JSON文件
    df = pd.read_json('data.json')
    
    # 从字符串读取
    json_str = '[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]'
    df = pd.read_json(json_str)
    
    # 嵌套JSON处理
    with open('nested_data.json', 'r') as f:
        data = json.load(f)
    
    # 使用json_normalize展平嵌套数据
    df = pd.json_normalize(data, record_path='records', meta=['id', 'name'])
    
    return df

# 读取数据库
def read_from_database():
    """从数据库读取数据"""
    from sqlalchemy import create_engine
    
    # 创建连接
    engine = create_engine('postgresql://user:***@localhost:5432/mydb')
    
    # 使用SQL查询
    df = pd.read_sql('SELECT * FROM users WHERE age > 25', engine)
    
    # 使用表名
    df = pd.read_sql_table('users', engine)
    
    # 使用chunks处理大表
    chunks = pd.read_sql('SELECT * FROM large_table', engine, chunksize=10000)
    df = pd.concat(chunks, ignore_index=True)
    
    return df

# 数据写入
def write_data():
    """数据写入各种格式"""
    df = pd.DataFrame({
        'name': ['John', 'Jane', 'Bob'],
        'age': [30, 25, 35],
        'city': ['New York', 'London', 'Paris']
    })
    
    # 写入CSV
    df.to_csv('output.csv', index=False, encoding='utf-8-sig')
    
    # 写入Excel
    df.to_excel('output.xlsx', index=False, sheet_name='Data')
    
    # 写入JSON
    df.to_json('output.json', orient='records', force_ascii=False)
    
    # 写入多个sheet
    with pd.ExcelWriter('multi_sheet.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.describe().to_excel(writer, sheet_name='Statistics')
    
    # 写入数据库
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///data.db')
    df.to_sql('users', engine, if_exists='replace', index=False)
```

### 1.2 数据选择与过滤

```python
import pandas as pd
import numpy as np

# 创建示例数据
def create_sample_data():
    np.random.seed(42)
    df = pd.DataFrame({
        'id': range(1, 101),
        'name': [f'User_{i}' for i in range(1, 101)],
        'age': np.random.randint(18, 65, 100),
        'salary': np.random.randint(3000, 20000, 100),
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 100),
        'city': np.random.choice(['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'], 100),
        'hire_date': pd.date_range('2020-01-01', periods=100, freq='D'),
        'performance_score': np.random.uniform(60, 100, 100).round(2)
    })
    return df

# 基本选择
def basic_selection(df):
    """基本数据选择"""
    # 选择单列
    ages = df['age']
    
    # 选择多列
    subset = df[['name', 'age', 'salary']]
    
    # 使用loc（基于标签）
    row = df.loc[0]  # 第一行
    rows = df.loc[0:5]  # 前6行
    cell = df.loc[0, 'name']  # 单元格
    
    # 使用iloc（基于位置）
    row = df.iloc[0]
    rows = df.iloc[0:5]
    cell = df.iloc[0, 1]
    
    return subset

# 条件过滤
def conditional_filtering(df):
    """条件过滤"""
    # 单条件
    young_users = df[df['age'] < 30]
    
    # 多条件（AND）
    filtered = df[(df['age'] > 25) & (df['salary'] > 10000)]
    
    # 多条件（OR）
    filtered = df[(df['department'] == 'IT') | (df['department'] == 'HR')]
    
    # 使用isin
    filtered = df[df['department'].isin(['IT', 'Finance'])]
    
    # 使用between
    filtered = df[df['age'].between(25, 35)]
    
    # 字符串过滤
    filtered = df[df['name'].str.contains('User_1')]
    
    # 正则表达式
    filtered = df[df['name'].str.match(r'User_\d{2}$')]
    
    # 查询方法
    filtered = df.query('age > 25 and salary > 10000')
    filtered = df.query('department == "IT" and city == "Beijing"')
    
    return filtered

# 高级选择
def advanced_selection(df):
    """高级数据选择"""
    # 随机抽样
    sample = df.sample(n=10)
    sample = df.sample(frac=0.1)  # 10%抽样
    
    # nlargest和nsmallest
    top_earners = df.nlargest(5, 'salary')
    bottom_performers = df.nsmallest(5, 'performance_score')
    
    # 条件赋值
    df['salary_level'] = 'Low'
    df.loc[df['salary'] > 10000, 'salary_level'] = 'High'
    df.loc[df['salary'].between(5000, 10000), 'salary_level'] = 'Medium'
    
    # 使用where
    df['high_performer'] = df['performance_score'].where(df['performance_score'] > 80, 0)
    
    # 使用mask
    df['masked_salary'] = df['salary'].mask(df['age'] < 25, 0)
    
    return df
```

### 1.3 数据聚合与分组

```python
import pandas as pd
import numpy as np

def aggregation_operations(df):
    """聚合操作"""
    # 基本统计
    stats = {
        'mean_age': df['age'].mean(),
        'median_salary': df['salary'].median(),
        'std_performance': df['performance_score'].std(),
        'min_age': df['age'].min(),
        'max_salary': df['salary'].max(),
        'total_count': len(df)
    }
    
    # 描述性统计
    description = df.describe()
    
    # 相关性分析
    correlation = df[['age', 'salary', 'performance_score']].corr()
    
    return stats, description, correlation

def groupby_operations(df):
    """分组操作"""
    # 基本分组
    dept_stats = df.groupby('department').agg({
        'salary': ['mean', 'median', 'std', 'min', 'max'],
        'age': ['mean', 'count'],
        'performance_score': 'mean'
    })
    
    # 多级分组
    city_dept_stats = df.groupby(['city', 'department']).agg({
        'salary': 'mean',
        'id': 'count'
    }).reset_index()
    
    # 自定义聚合函数
    def salary_range(x):
        return x.max() - x.min()
    
    custom_agg = df.groupby('department').agg({
        'salary': [salary_range, lambda x: x.quantile(0.75)]
    })
    
    # 转换
    df['salary_zscore'] = df.groupby('department')['salary'].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    
    # 过滤
    high_perf_dept = df.groupby('department').filter(
        lambda x: x['performance_score'].mean() > 75
    )
    
    return dept_stats, city_dept_stats, df

def pivot_table_operations(df):
    """透视表操作"""
    # 基本透视表
    pivot = pd.pivot_table(
        df,
        values='salary',
        index='department',
        columns='city',
        aggfunc='mean'
    )
    
    # 多聚合函数
    pivot_multi = pd.pivot_table(
        df,
        values=['salary', 'performance_score'],
        index='department',
        columns='city',
        aggfunc={'salary': 'mean', 'performance_score': ['mean', 'count']}
    )
    
    # 添加边际值
    pivot_with_margins = pd.pivot_table(
        df,
        values='salary',
        index='department',
        columns='city',
        aggfunc='mean',
        margins=True,
        margins_name='Total'
    )
    
    return pivot, pivot_multi, pivot_with_margins

def cross_tabulation(df):
    """交叉表"""
    # 基本交叉表
    cross = pd.crosstab(df['department'], df['city'])
    
    # 带归一化
    cross_norm = pd.crosstab(df['department'], df['city'], normalize='index')
    
    # 带边际值
    cross_margins = pd.crosstab(df['department'], df['city'], margins=True)
    
    return cross, cross_norm, cross_margins
```

## 2. 数据清洗

### 2.1 缺失值处理

```python
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer

def missing_value_analysis(df):
    """缺失值分析"""
    # 检查缺失值
    missing_count = df.isnull().sum()
    missing_percent = (df.isnull().sum() / len(df)) * 100
    
    missing_info = pd.DataFrame({
        'Missing Count': missing_count,
        'Missing Percent': missing_percent
    })
    
    # 筛选有缺失值的列
    missing_cols = missing_info[missing_info['Missing Count'] > 0]
    
    return missing_info, missing_cols

def handle_missing_values(df):
    """处理缺失值"""
    # 删除缺失值
    df_dropped = df.dropna()  # 删除任何包含缺失值的行
    df_dropped_cols = df.dropna(axis=1)  # 删除任何包含缺失值的列
    
    # 填充缺失值
    df_filled_zero = df.fillna(0)
    df_filled_mean = df.fillna(df.mean())
    df_filled_median = df.fillna(df.median())
    df_filled_mode = df.fillna(df.mode().iloc[0])
    
    # 前向填充和后向填充
    df_ffill = df.fillna(method='ffill')
    df_bfill = df.fillna(method='bfill')
    
    # 插值
    df_interpolated = df.interpolate(method='linear')
    
    return df_dropped, df_filled_mean, df_interpolated

def advanced_imputation(df):
    """高级缺失值填充"""
    # 使用SimpleImputer
    imputer = SimpleImputer(strategy='mean')  # 'median', 'most_frequent', 'constant'
    df_imputed = pd.DataFrame(
        imputer.fit_transform(df.select_dtypes(include=[np.number])),
        columns=df.select_dtypes(include=[np.number]).columns
    )
    
    # 使用KNNImputer
    knn_imputer = KNNImputer(n_neighbors=5)
    df_knn_imputed = pd.DataFrame(
        knn_imputer.fit_transform(df.select_dtypes(include=[np.number])),
        columns=df.select_dtypes(include=[np.number]).columns
    )
    
    return df_imputed, df_knn_imputed
```

### 2.2 异常值处理

```python
import pandas as pd
import numpy as np
from scipy import stats

def detect_outliers(df, column):
    """检测异常值"""
    # IQR方法
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers_iqr = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    
    # Z-score方法
    z_scores = np.abs(stats.zscore(df[column]))
    outliers_zscore = df[z_scores > 3]
    
    # 修改的Z-score方法
    median = df[column].median()
    mad = np.median(np.abs(df[column] - median))
    modified_z_scores = 0.6745 * (df[column] - median) / mad
    outliers_modified = df[np.abs(modified_z_scores) > 3.5]
    
    return outliers_iqr, outliers_zscore, outliers_modified

def handle_outliers(df, column, method='iqr'):
    """处理异常值"""
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 截断
        df[column] = df[column].clip(lower_bound, upper_bound)
        
    elif method == 'zscore':
        z_scores = np.abs(stats.zscore(df[column]))
        df = df[z_scores <= 3]
        
    elif method == 'percentile':
        lower = df[column].quantile(0.01)
        upper = df[column].quantile(0.99)
        df[column] = df[column].clip(lower, upper)
    
    return df

def winsorize_data(df, column, limits=(0.05, 0.05)):
    """Winsorize处理"""
    from scipy.stats import mstats
    df[column] = mstats.winsorize(df[column], limits=limits)
    return df
```

### 2.3 数据类型转换

```python
import pandas as pd
import numpy as np

def convert_dtypes(df):
    """数据类型转换"""
    # 数值类型转换
    df['int_col'] = df['int_col'].astype('int32')
    df['float_col'] = df['float_col'].astype('float64')
    
    # 字符串类型
    df['str_col'] = df['str_col'].astype('str')
    
    # 类别类型（节省内存）
    df['category_col'] = df['category_col'].astype('category')
    
    # 日期类型
    df['date_col'] = pd.to_datetime(df['date_col'])
    df['date_col'] = pd.to_datetime(df['date_col'], format='%Y-%m-%d')
    
    # 布尔类型
    df['bool_col'] = df['bool_col'].astype(bool)
    
    return df

def optimize_dtypes(df):
    """优化数据类型以节省内存"""
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
        else:
            num_unique = len(df[col].unique())
            num_total = len(df[col])
            if num_unique / num_total < 0.5:
                df[col] = df[col].astype('category')
    
    return df
```

## 3. 数据转换

### 3.1 字符串操作

```python
import pandas as pd
import re

def string_operations(df):
    """字符串操作"""
    # 基本操作
    df['name_upper'] = df['name'].str.upper()
    df['name_lower'] = df['name'].str.lower()
    df['name_title'] = df['name'].str.title()
    
    # 去除空白
    df['name_stripped'] = df['name'].str.strip()
    df['name_lstripped'] = df['name'].str.lstrip()
    df['name_rstripped'] = df['name'].str.rstrip()
    
    # 替换
    df['name_replaced'] = df['name'].str.replace('old', 'new')
    df['name_regex'] = df['name'].str.replace(r'\d+', '', regex=True)
    
    # 分割
    df[['first_name', 'last_name']] = df['full_name'].str.split(' ', expand=True)
    
    # 提取
    df['area_code'] = df['phone'].str.extract(r'\((\d{3})\)')
    
    # 包含
    df['has_email'] = df['contact'].str.contains('@', na=False)
    
    # 长度
    df['name_length'] = df['name'].str.len()
    
    # 填充
    df['id_padded'] = df['id'].astype(str).str.zfill(6)
    
    return df

def text_processing(text_series):
    """文本处理"""
    # 清理文本
    cleaned = text_series.str.lower()
    cleaned = cleaned.str.replace(r'[^\w\s]', '', regex=True)
    cleaned = cleaned.str.replace(r'\s+', ' ', regex=True)
    cleaned = cleaned.str.strip()
    
    # 分词
    words = cleaned.str.split()
    
    # 提取数字
    numbers = text_series.str.extractall(r'(\d+)').groupby(level=0).agg(list)
    
    return cleaned, words, numbers
```

### 3.2 日期时间操作

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def datetime_operations(df):
    """日期时间操作"""
    # 转换为datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # 提取组件
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['second'] = df['date'].dt.second
    df['dayofweek'] = df['date'].dt.dayofweek  # 0=Monday
    df['dayofyear'] = df['date'].dt.dayofyear
    df['weekofyear'] = df['date'].dt.isocalendar().week
    df['quarter'] = df['date'].dt.quarter
    
    # 日期名称
    df['day_name'] = df['date'].dt.day_name()
    df['month_name'] = df['date'].dt.month_name()
    
    # 计算时间差
    df['days_since'] = (pd.Timestamp.now() - df['date']).dt.days
    
    # 日期运算
    df['next_week'] = df['date'] + timedelta(days=7)
    df['next_month'] = df['date'] + pd.DateOffset(months=1)
    
    # 日期过滤
    df_this_year = df[df['date'].dt.year == 2026]
    df_this_month = df[(df['date'].dt.year == 2026) & (df['date'].dt.month == 6)]
    
    # 重采样
    df.set_index('date', inplace=True)
    monthly = df.resample('M').sum()
    weekly = df.resample('W').mean()
    
    return df

def date_range_operations():
    """日期范围操作"""
    # 创建日期范围
    dates = pd.date_range(start='2026-01-01', end='2026-12-31', freq='D')
    
    # 工作日
    business_days = pd.bdate_range(start='2026-01-01', end='2026-12-31')
    
    # 指定周期
    monthly = pd.date_range(start='2026-01-01', periods=12, freq='M')
    
    return dates, business_days, monthly
```

### 3.3 数据合并与重塑

```python
import pandas as pd
import numpy as np

def merge_operations():
    """数据合并操作"""
    # 创建示例数据
    df1 = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
        'department_id': [1, 2, 1, 3, 2]
    })
    
    df2 = pd.DataFrame({
        'department_id': [1, 2, 3],
        'department_name': ['IT', 'HR', 'Finance']
    })
    
    # 内连接
    merged_inner = pd.merge(df1, df2, on='department_id', how='inner')
    
    # 左连接
    merged_left = pd.merge(df1, df2, on='department_id', how='left')
    
    # 右连接
    merged_right = pd.merge(df1, df2, on='department_id', how='right')
    
    # 外连接
    merged_outer = pd.merge(df1, df2, on='department_id', how='outer')
    
    # 多列合并
    df3 = pd.DataFrame({
        'id': [1, 2, 3],
        'date': ['2026-01-01', '2026-01-02', '2026-01-03'],
        'value': [100, 200, 300]
    })
    
    merged_multi = pd.merge(df1, df3, on=['id', 'date'], how='inner')
    
    return merged_inner, merged_left, merged_right, merged_outer

def concat_operations():
    """数据拼接操作"""
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
    df3 = pd.DataFrame({'A': [9, 10], 'B': [11, 12]})
    
    # 垂直拼接
    vertical = pd.concat([df1, df2, df3], axis=0)
    
    # 水平拼接
    horizontal = pd.concat([df1, df2, df3], axis=1)
    
    # 忽略索引
    vertical_reset = pd.concat([df1, df2, df3], ignore_index=True)
    
    # 添加标识
    vertical_labeled = pd.concat(
        [df1, df2, df3],
        keys=['df1', 'df2', 'df3']
    )
    
    return vertical, horizontal, vertical_reset

def reshape_operations(df):
    """数据重塑操作"""
    # 创建示例数据
    df_long = pd.DataFrame({
        'date': ['2026-01-01', '2026-01-01', '2026-01-02', '2026-01-02'],
        'product': ['A', 'B', 'A', 'B'],
        'sales': [100, 200, 150, 250]
    })
    
    # 宽格式转长格式（melt）
    df_melted = pd.melt(
        df_long,
        id_vars=['date', 'product'],
        value_vars=['sales'],
        var_name='metric',
        value_name='value'
    )
    
    # 长格式转宽格式（pivot）
    df_wide = df_long.pivot(
        index='date',
        columns='product',
        values='sales'
    ).reset_index()
    
    # pivot_table（支持聚合）
    df_pivot = pd.pivot_table(
        df_long,
        values='sales',
        index='date',
        columns='product',
        aggfunc='sum'
    )
    
    # stack和unstack
    df_multi = df_long.set_index(['date', 'product'])
    df_unstacked = df_multi.unstack()
    df_stacked = df_unstacked.stack()
    
    return df_long, df_melted, df_wide, df_pivot
```

## 4. 大数据处理

### 4.1 Dask并行计算

```python
import dask.dataframe as dd
import dask.array as da
from dask.diagnostics import ProgressBar
import pandas as pd

def dask_operations():
    """Dask并行计算"""
    # 读取大文件
    df = dd.read_csv('large_file_*.csv')
    
    # 基本操作
    result = df.groupby('column').agg({'value': 'mean'})
    
    # 延迟计算
    with ProgressBar():
        result_computed = result.compute()
    
    # 过滤
    filtered = df[df['value'] > 100]
    
    # 合并
    df1 = dd.read_csv('file1.csv')
    df2 = dd.read_csv('file2.csv')
    merged = dd.merge(df1, df2, on='id')
    
    # 保存结果
    merged.to_parquet('output.parquet', engine='pyarrow')
    
    return result_computed

def dask_array_operations():
    """Dask数组操作"""
    # 创建大数组
    x = da.random.random((10000, 10000), chunks=(1000, 1000))
    
    # 计算操作
    result = (x + x.T).mean(axis=0)
    
    # 计算结果
    with ProgressBar():
        result_computed = result.compute()
    
    return result_computed
```

### 4.2 Polars高性能数据处理

```python
import polars as pl
import numpy as np

def polars_operations():
    """Polars高性能数据处理"""
    # 创建DataFrame
    df = pl.DataFrame({
        'name': ['John', 'Jane', 'Bob', 'Alice'],
        'age': [30, 25, 35, 28],
        'salary': [50000, 60000, 70000, 55000]
    })
    
    # 读取文件
    df_csv = pl.read_csv('data.csv')
    df_parquet = pl.read_parquet('data.parquet')
    
    # 过滤
    filtered = df.filter(pl.col('age') > 28)
    
    # 选择
    selected = df.select(['name', 'salary'])
    
    # 添加列
    df_with_bonus = df.with_columns([
        (pl.col('salary') * 0.1).alias('bonus')
    ])
    
    # 分组聚合
    grouped = df.group_by('department').agg([
        pl.col('salary').mean().alias('avg_salary'),
        pl.col('age').count().alias('count')
    ])
    
    # 排序
    sorted_df = df.sort('salary', descending=True)
    
    # 窗口函数
    df_with_rank = df.with_columns([
        pl.col('salary').rank().over('department').alias('salary_rank')
    ])
    
    # 保存
    df.write_parquet('output.parquet')
    df.write_csv('output.csv')
    
    return df
```

### 4.3 PySpark分布式计算

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

def pyspark_operations():
    """PySpark分布式计算"""
    # 创建Spark会话
    spark = SparkSession.builder \
        .appName("DataProcessing") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    # 读取数据
    df = spark.read.csv('data.csv', header=True, inferSchema=True)
    df = spark.read.parquet('data.parquet')
    
    # 基本操作
    df.select('name', 'age').show()
    df.filter(F.col('age') > 25).show()
    
    # 添加列
    df_with_bonus = df.withColumn('bonus', F.col('salary') * 0.1)
    
    # 聚合
    df.groupBy('department') \
        .agg(
            F.avg('salary').alias('avg_salary'),
            F.count('*').alias('count'),
            F.max('age').alias('max_age')
        ) \
        .show()
    
    # 窗口函数
    windowSpec = Window.partitionBy('department').orderBy(F.desc('salary'))
    
    df_with_rank = df.withColumn(
        'salary_rank',
        F.rank().over(windowSpec)
    )
    
    # SQL查询
    df.createOrReplaceTempView('employees')
    result = spark.sql("""
        SELECT department, AVG(salary) as avg_salary
        FROM employees
        GROUP BY department
        ORDER BY avg_salary DESC
    """)
    
    # 保存
    df.write.parquet('output.parquet', mode='overwrite')
    df.write.csv('output.csv', mode='overwrite', header=True)
    
    # 停止Spark会话
    spark.stop()
    
    return result
```

## 5. 实战案例

### 5.1 销售数据分析

```python
import pandas as pd
import numpy as np
from datetime import datetime

class SalesAnalyzer:
    """销售数据分析器"""
    
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path, parse_dates=['order_date'])
        self.prepare_data()
    
    def prepare_data(self):
        """数据准备"""
        # 添加时间列
        self.df['year'] = self.df['order_date'].dt.year
        self.df['month'] = self.df['order_date'].dt.month
        self.df['quarter'] = self.df['order_date'].dt.quarter
        self.df['day_of_week'] = self.df['order_date'].dt.dayofweek
        
        # 计算总金额
        self.df['total_amount'] = self.df['quantity'] * self.df['unit_price']
    
    def monthly_sales_summary(self):
        """月度销售汇总"""
        monthly = self.df.groupby(['year', 'month']).agg({
            'total_amount': 'sum',
            'order_id': 'nunique',
            'customer_id': 'nunique'
        }).reset_index()
        
        monthly.columns = ['year', 'month', 'total_sales', 'order_count', 'customer_count']
        
        # 计算环比增长
        monthly['sales_growth'] = monthly['total_sales'].pct_change() * 100
        
        return monthly
    
    def top_products(self, n=10):
        """Top N产品"""
        return self.df.groupby('product_name').agg({
            'total_amount': 'sum',
            'quantity': 'sum',
            'order_id': 'nunique'
        }).sort_values('total_amount', ascending=False).head(n)
    
    def customer_analysis(self):
        """客户分析"""
        customer_stats = self.df.groupby('customer_id').agg({
            'order_id': 'nunique',
            'total_amount': 'sum',
            'order_date': ['min', 'max']
        })
        
        customer_stats.columns = ['order_count', 'total_spent', 'first_order', 'last_order']
        
        # 客户分层
        customer_stats['customer_segment'] = pd.cut(
            customer_stats['total_spent'],
            bins=[0, 1000, 5000, 10000, float('inf')],
            labels=['Bronze', 'Silver', 'Gold', 'Platinum']
        )
        
        return customer_stats
    
    def generate_report(self):
        """生成分析报告"""
        report = {
            '总销售额': self.df['total_amount'].sum(),
            '总订单数': self.df['order_id'].nunique(),
            '总客户数': self.df['customer_id'].nunique(),
            '平均订单金额': self.df.groupby('order_id')['total_amount'].sum().mean(),
            '月度销售趋势': self.monthly_sales_summary(),
            'Top产品': self.top_products(),
            '客户分析': self.customer_analysis()
        }
        
        return report

# 使用示例
# analyzer = SalesAnalyzer('sales_data.csv')
# report = analyzer.generate_report()
```

### 5.2 日志数据分析

```python
import pandas as pd
import re
from collections import Counter

class LogAnalyzer:
    """日志数据分析器"""
    
    def __init__(self, log_path):
        self.logs = self.parse_logs(log_path)
    
    def parse_logs(self, log_path):
        """解析日志文件"""
        log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)'
        
        records = []
        with open(log_path, 'r') as f:
            for line in f:
                match = re.match(log_pattern, line.strip())
                if match:
                    records.append({
                        'timestamp': pd.to_datetime(match.group(1)),
                        'level': match.group(2),
                        'message': match.group(3)
                    })
        
        return pd.DataFrame(records)
    
    def error_analysis(self):
        """错误分析"""
        errors = self.logs[self.logs['level'] == 'ERROR']
        
        # 错误类型统计
        error_types = errors['message'].str.extract(r'(\w+Error)')[0].value_counts()
        
        # 按小时统计
        errors_by_hour = errors.groupby(errors['timestamp'].dt.hour).size()
        
        return error_types, errors_by_hour
    
    def traffic_analysis(self):
        """流量分析"""
        # 每小时请求数
        hourly_requests = self.logs.groupby(self.logs['timestamp'].dt.hour).size()
        
        # 高峰时段
        peak_hour = hourly_requests.idxmax()
        
        return hourly_requests, peak_hour
```

## 最佳实践

### 1. 性能优化
```python
# 使用适当的数据类型
df['category'] = df['category'].astype('category')

# 使用向量化操作
df['result'] = df['a'] + df['b']  # 而不是循环

# 使用eval和query
df.eval('result = a + b', inplace=True)
df.query('age > 25 and salary > 50000')

# 使用chunk处理大文件
for chunk in pd.read_csv('large.csv', chunksize=10000):
    process(chunk)
```

### 2. 内存管理
```python
# 监控内存使用
print(df.info(memory_usage='deep'))

# 优化内存
df = optimize_dtypes(df)

# 及时删除不需要的变量
del large_df
import gc
gc.collect()
```

### 3. 数据验证
```python
# 使用pandera进行数据验证
import pandera as pa
from pandera import Column, Check, DataFrameSchema

schema = DataFrameSchema({
    'id': Column(int, Check.greater_than(0)),
    'name': Column(str, Check.str_length(1, 100)),
    'age': Column(int, Check.in_range(0, 150)),
    'email': Column(str, Check.str_matches(r'^[\w\.-]+@[\w\.-]+\.\w+$'))
})

# 验证数据
validated_df = schema.validate(df)
```

### 4. 错误处理
```python
def safe_read_csv(file_path):
    """安全读取CSV"""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        return None
    except pd.errors.EmptyDataError:
        print(f"文件为空: {file_path}")
        return None
    except Exception as e:
        print(f"读取错误: {e}")
        return None
```

## 相关页面

- [[Python自动化办公]] - 办公文档处理
- [[Python爬虫实战]] - 网络数据采集
- [[Python Web开发]] - Web应用开发
- [[Python机器学习实战]] - 机器学习应用

## 参考资源

- [Pandas官方文档](https://pandas.pydata.org/docs/)
- [Polars官方文档](https://pola-rs.github.io/polars-book/)
- [Dask官方文档](https://docs.dask.org/)
- [PySpark官方文档](https://spark.apache.org/docs/latest/api/python/)

---

*最后更新：2026年6月28日*
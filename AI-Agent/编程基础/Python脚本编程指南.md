---
title: Python脚本编程指南
aliases: [Python教程, 脚本编程, Python基础]
tags: [python, 编程, 脚本]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: beginner
project: 编程
---
# Python 脚本编程指南

## 概述

本指南提供Python脚本编程的常用代码模板和最佳实践。

## 1. 基础语法

### 变量和数据类型

```python
# 变量赋值
name = "John"
age = 30
height = 1.75
is_student = True

# 数据类型
print(type(name))      # <class 'str'>
print(type(age))       # <class 'int'>
print(type(height))    # <class 'float'>
print(type(is_student)) # <class 'bool'>
```

### 列表操作

```python
# 创建列表
fruits = ["apple", "banana", "cherry"]

# 访问元素
print(fruits[0])      # apple
print(fruits[-1])     # cherry

# 添加元素
fruits.append("orange")
fruits.insert(1, "grape")

# 删除元素
fruits.remove("banana")
del fruits[0]

# 列表切片
print(fruits[1:3])    # ['grape', 'cherry']
print(fruits[:2])     # ['grape', 'cherry']
print(fruits[1:])     # ['cherry', 'orange']
```

### 字典操作

```python
# 创建字典
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# 访问值
print(person["name"])  # John
print(person.get("age"))  # 30

# 添加/修改
person["email"] = "john@example.com"
person["age"] = 31

# 删除
del person["city"]

# 遍历
for key, value in person.items():
    print(f"{key}: {value}")
```

## 2. 控制结构

### 条件语句

```python
# if-elif-else
x = 10

if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")

# 三元表达式
result = "Positive" if x > 0 else "Negative"
```

### 循环

```python
# for循环
for i in range(5):
    print(i)

# 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# while循环
count = 0
while count < 5:
    print(count)
    count += 1

# 列表推导式
squares = [x**2 for x in range(10)]
even_numbers = [x for x in range(10) if x % 2 == 0]
```

## 3. 函数定义

### 基础函数

```python
# 定义函数
def greet(name):
    """打招呼"""
    return f"Hello, {name}!"

# 调用函数
message = greet("John")
print(message)
```

### 参数类型

```python
# 默认参数
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# 可变参数
def sum_numbers(*args):
    return sum(args)

# 关键字参数
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

# 混合参数
def func(a, b, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")
```

### Lambda函数

```python
# Lambda函数
square = lambda x: x**2
print(square(5))  # 25

# 与map/filter结合
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
even = list(filter(lambda x: x % 2 == 0, numbers))
```

## 4. 文件操作

### 读写文件

```python
# 写文件
with open("output.txt", "w") as f:
    f.write("Hello, World!")

# 读文件
with open("output.txt", "r") as f:
    content = f.read()
    print(content)

# 逐行读取
with open("output.txt", "r") as f:
    for line in f:
        print(line.strip())
```

### CSV文件

```python
import csv

# 写CSV
with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age", "city"])
    writer.writerow(["John", 30, "New York"])

# 读CSV
with open("data.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

### JSON文件

```python
import json

# 写JSON
data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

# 读JSON
with open("data.json", "r") as f:
    data = json.load(f)
    print(data)
```

## 5. 异常处理

### try-except

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"Error: {e}")
else:
    print("No error occurred")
finally:
    print("This always executes")
```

### 自定义异常

```python
class CustomError(Exception):
    pass

def divide(a, b):
    if b == 0:
        raise CustomError("Cannot divide by zero")
    return a / b

try:
    result = divide(10, 0)
except CustomError as e:
    print(f"Custom error: {e}")
```

## 6. 类和对象

### 基础类

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, my name is {self.name}"
    
    def __str__(self):
        return f"Person(name={self.name}, age={self.age})"

# 使用类
person = Person("John", 30)
print(person.greet())
print(person)
```

### 继承

```python
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id
    
    def study(self):
        return f"{self.name} is studying"

# 使用继承
student = Student("John", 30, "12345")
print(student.greet())
print(student.study())
```

## 7. 模块导入

### 标准库

```python
import os
import sys
import json
import datetime
import collections
from pathlib import Path

# 使用模块
print(os.getcwd())
print(sys.version)
print(datetime.datetime.now())
```

### 第三方库

```python
import requests
import pandas as pd
import numpy as np

# HTTP请求
response = requests.get("https://api.example.com/data")
data = response.json()

# 数据处理
df = pd.DataFrame(data)
print(df.head())
```

## 8. 装饰器

### 基础装饰器

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

### 带参数的装饰器

```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("John")
```

## 9. 生成器

### 基础生成器

```python
def my_generator():
    yield 1
    yield 2
    yield 3

# 使用生成器
gen = my_generator()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
```

### 生成器表达式

```python
# 生成器表达式
squares = (x**2 for x in range(10))

# 使用生成器
for square in squares:
    print(square)
```

## 10. 并发编程

### 多线程

```python
import threading

def worker():
    print("Worker thread")

# 创建线程
thread = threading.Thread(target=worker)
thread.start()
thread.join()
```

### 多进程

```python
import multiprocessing

def worker():
    print("Worker process")

# 创建进程
process = multiprocessing.Process(target=worker)
process.start()
process.join()
```

### 异步编程

```python
import asyncio

async def worker():
    print("Start")
    await asyncio.sleep(1)
    print("End")

# 运行异步函数
asyncio.run(worker())
```

## 相关页面

- [[Python运维脚本库]]
- [[Python数据分析工具箱]]
- [[Git版本控制指南]]

---
title: Go语言开发指南
aliases: [Go教程, Golang, Go语言基础]
tags: [go, golang, 开发]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 编程
---
# Go 语言开发指南

## 概述

本指南提供Go语言开发的常用代码模板和最佳实践。

## 1. 基础语法

### 变量声明

```go
// 变量声明
var name string = "John"
var age int = 30

// 短变量声明
name := "John"
age := 30

// 多变量声明
var (
    name string = "John"
    age  int    = 30
)

// 常量
const Pi = 3.14159
const (
    StatusOK    = 200
    StatusError = 500
)
```

### 数据类型

```go
// 基本类型
var str string = "Hello"
var num int = 42
var float float64 = 3.14
var bool bool = true

// 复合类型
var arr [5]int = [5]int{1, 2, 3, 4, 5}
var slice []int = []int{1, 2, 3}
var dict map[string]int = map[string]int{"a": 1, "b": 2}

// 结构体
type Person struct {
    Name string
    Age  int
}
```

## 2. 控制结构

### 条件语句

```go
// if-else
if x > 0 {
    fmt.Println("Positive")
} else if x < 0 {
    fmt.Println("Negative")
} else {
    fmt.Println("Zero")
}

// if初始化语句
if err := doSomething(); err != nil {
    fmt.Println("Error:", err)
}

// switch
switch day {
case "Monday":
    fmt.Println("Monday")
case "Tuesday":
    fmt.Println("Tuesday")
default:
    fmt.Println("Other day")
}
```

### 循环

```go
// for循环
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// while风格
for i < 10 {
    fmt.Println(i)
    i++
}

// 无限循环
for {
    // break退出
}

// range遍历
for index, value := range slice {
    fmt.Println(index, value)
}

for key, value := range dict {
    fmt.Println(key, value)
}
```

## 3. 函数定义

### 基础函数

```go
// 函数定义
func greet(name string) string {
    return "Hello, " + name + "!"
}

// 多返回值
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// 命名返回值
func divide(a, b int) (result int, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return
    }
    result = a / b
    return
}
```

### 可变参数

```go
func sum(numbers ...int) int {
    total := 0
    for _, num := range numbers {
        total += num
    }
    return total
}

// 使用
result := sum(1, 2, 3, 4, 5)
```

### 匿名函数

```go
// 匿名函数
add := func(a, b int) int {
    return a + b
}

result := add(1, 2)

// 闭包
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
fmt.Println(c()) // 1
fmt.Println(c()) // 2
```

## 4. 结构体和方法

### 结构体定义

```go
type Person struct {
    Name string
    Age  int
}

// 创建实例
p := Person{Name: "John", Age: 30}
p := Person{"John", 30}

// 访问字段
fmt.Println(p.Name)
p.Age = 31
```

### 方法定义

```go
// 值接收者方法
func (p Person) Greet() string {
    return "Hello, " + p.Name + "!"
}

// 指针接收者方法
func (p *Person) SetAge(age int) {
    p.Age = age
}

// 使用
p := Person{Name: "John", Age: 30}
fmt.Println(p.Greet())
p.SetAge(31)
```

### 结构体嵌入

```go
type Address struct {
    City  string
    State string
}

type Person struct {
    Name    string
    Age     int
    Address // 嵌入Address
}

p := Person{
    Name: "John",
    Age:  30,
    Address: Address{
        City:  "New York",
        State: "NY",
    },
}

fmt.Println(p.City) // 直接访问嵌入字段
```

## 5. 接口

### 接口定义

```go
type Shape interface {
    Area() float64
    Perimeter() float64
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

// 使用
var s Shape = Circle{Radius: 5}
fmt.Println(s.Area())
```

### 空接口

```go
// 空接口可以存储任意类型
var i interface{} = "Hello"
i = 42
i = true

// 类型断言
str, ok := i.(string)
if ok {
    fmt.Println(str)
}

// 类型开关
switch v := i.(type) {
case string:
    fmt.Println("string:", v)
case int:
    fmt.Println("int:", v)
default:
    fmt.Println("unknown")
}
```

## 6. 错误处理

### 错误创建

```go
import "errors"

// 创建错误
err := errors.New("something went wrong")

// 格式化错误
err := fmt.Errorf("failed to open %s: %v", filename, err)
```

### 错误处理模式

```go
func doSomething() error {
    result, err := riskyOperation()
    if err != nil {
        return fmt.Errorf("riskyOperation failed: %w", err)
    }
    // 使用result
    return nil
}

// 使用
if err := doSomething(); err != nil {
    log.Fatal(err)
}
```

### 自定义错误

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error: %s - %s", e.Field, e.Message)
}

// 使用
err := &ValidationError{Field: "email", Message: "invalid format"}
```

## 7. 并发编程

### Goroutine

```go
// 启动goroutine
go func() {
    fmt.Println("Hello from goroutine")
}()

// 等待goroutine
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    fmt.Println("Hello from goroutine")
}()
wg.Wait()
```

### Channel

```go
// 创建channel
ch := make(chan int)
ch := make(chan int, 10) // 带缓冲

// 发送数据
ch <- 42

// 接收数据
value := <-ch

// 关闭channel
close(ch)

// 遍历channel
for value := range ch {
    fmt.Println(value)
}
```

### Select

```go
select {
case msg := <-ch1:
    fmt.Println("Received from ch1:", msg)
case msg := <-ch2:
    fmt.Println("Received from ch2:", msg)
case <-time.After(time.Second):
    fmt.Println("Timeout")
default:
    fmt.Println("No data available")
}
```

## 8. 包管理

### 包定义

```go
// mypackage/mypackage.go
package mypackage

func Hello() string {
    return "Hello from mypackage"
}
```

### 包导入

```go
import (
    "fmt"
    "mypackage"
)

func main() {
    fmt.Println(mypackage.Hello())
}
```

### Go Modules

```bash
# 初始化模块
go mod init myproject

# 添加依赖
go get github.com/pkg/errors

# 整理依赖
go mod tidy

# 下载依赖
go mod download
```

## 9. 测试

### 单元测试

```go
// mypackage_test.go
package mypackage

import "testing"

func TestHello(t *testing.T) {
    result := Hello()
    expected := "Hello from mypackage"
    if result != expected {
        t.Errorf("Hello() = %s, want %s", result, expected)
    }
}

func TestAdd(t *testing.T) {
    tests := []struct {
        a, b, expected int
    }{
        {1, 2, 3},
        {0, 0, 0},
        {-1, 1, 0},
    }
    
    for _, test := range tests {
        result := Add(test.a, test.b)
        if result != test.expected {
            t.Errorf("Add(%d, %d) = %d, want %d", test.a, test.b, result, test.expected)
        }
    }
}
```

### 表驱动测试

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"zero", 0, 0, 0},
        {"negative", -1, 1, 0},
    }
    
    for _, test := range tests {
        t.Run(test.name, func(t *testing.T) {
            result := Add(test.a, test.b)
            if result != test.expected {
                t.Errorf("Add(%d, %d) = %d, want %d", test.a, test.b, result, test.expected)
            }
        })
    }
}
```

## 10. 常用标准库

### fmt包

```go
// 格式化输出
fmt.Println("Hello")
fmt.Printf("Name: %s, Age: %d\n", name, age)
fmt.Sprintf("Hello, %s!", name)
```

### strings包

```go
import "strings"

// 字符串操作
strings.ToUpper("hello")         // "HELLO"
strings.ToLower("HELLO")         // "hello"
strings.Contains("hello", "ell") // true
strings.HasPrefix("hello", "he") // true
strings.HasSuffix("hello", "lo") // true
strings.Split("a,b,c", ",")      // ["a", "b", "c"]
strings.Join([]string{"a", "b"}, ",") // "a,b"
```

### strconv包

```go
import "strconv"

// 类型转换
strconv.Itoa(42)           // "42"
strconv.Atoi("42")         // 42, nil
strconv.ParseFloat("3.14", 64) // 3.14, nil
```

### time包

```go
import "time"

// 时间操作
now := time.Now()
fmt.Println(now.Format("2006-01-02 15:04:05"))

// 时间解析
t, _ := time.Parse("2006-01-02", "2026-06-27")

// 时间计算
future := now.Add(24 * time.Hour)
diff := future.Sub(now)
```

## 相关页面

- [[Python脚本编程指南]]
- [[Docker容器化指南]]
- [[Kubernetes容器编排指南]]

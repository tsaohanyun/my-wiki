---
title: JavaScript前端开发指南
aliases: [JS教程, 前端开发, JavaScript基础]
tags: [javascript, 前端, 开发]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: beginner
project: 前端
---
# JavaScript 前端开发指南

## 概述

本指南提供JavaScript前端开发的常用代码模板和最佳实践。

## 1. 基础语法

### 变量声明

```javascript
// ES6变量声明
let name = "John";      // 可变变量
const age = 30;          // 不可变变量

// 变量命名规则
let userName = "John";   // 驼峰命名
let MAX_SIZE = 100;      // 常量大写
let _private = true;     // 下划线前缀
```

### 数据类型

```javascript
// 基本类型
let str = "Hello";           // 字符串
let num = 42;                // 数字
let bool = true;             // 布尔值
let nullVal = null;          // null
let undefinedVal = undefined; // undefined

// 引用类型
let arr = [1, 2, 3];        // 数组
let obj = { name: "John" }; // 对象
let func = function() {};   // 函数
```

### 字符串操作

```javascript
let str = "Hello, World!";

// 字符串方法
str.length;                  // 13
str.toUpperCase();           // "HELLO, WORLD!"
str.toLowerCase();           // "hello, world!"
str.indexOf("World");        // 7
str.slice(0, 5);             // "Hello"
str.replace("World", "JS");  // "Hello, JS!"
str.split(", ");             // ["Hello", "World!"]

// 模板字符串
let name = "John";
let greeting = `Hello, ${name}!`;
```

## 2. 数组操作

### 数组方法

```javascript
let arr = [1, 2, 3, 4, 5];

// 添加/删除元素
arr.push(6);           // 末尾添加
arr.pop();             // 末尾删除
arr.unshift(0);        // 开头添加
arr.shift();           // 开头删除

// 数组遍历
arr.forEach(function(item, index) {
    console.log(index, item);
});

// 数组映射
let doubled = arr.map(function(item) {
    return item * 2;
});

// 数组过滤
let even = arr.filter(function(item) {
    return item % 2 === 0;
});

// 数组归并
let sum = arr.reduce(function(acc, item) {
    return acc + item;
}, 0);

// 数组查找
let found = arr.find(function(item) {
    return item > 3;
});

let index = arr.findIndex(function(item) {
    return item > 3;
});
```

### 数组解构

```javascript
let [a, b, c] = [1, 2, 3];
// a = 1, b = 2, c = 3

let [first, ...rest] = [1, 2, 3, 4, 5];
// first = 1, rest = [2, 3, 4, 5]
```

## 3. 对象操作

### 对象方法

```javascript
let person = {
    name: "John",
    age: 30,
    greet: function() {
        return `Hello, ${this.name}!`;
    }
};

// 访问属性
person.name;           // "John"
person["age"];         // 30

// 添加/删除属性
person.email = "john@example.com";
delete person.age;

// 对象遍历
for (let key in person) {
    console.log(key, person[key]);
}

Object.keys(person);   // ["name", "greet", "email"]
Object.values(person); // ["John", function, "john@example.com"]
Object.entries(person); // [["name", "John"], ...]
```

### 对象解构

```javascript
let { name, age } = person;
// name = "John", age = 30

let { name: userName, age: userAge } = person;
// userName = "John", userAge = 30
```

## 4. 函数定义

### 函数声明

```javascript
// 函数声明
function greet(name) {
    return `Hello, ${name}!`;
}

// 函数表达式
let greet = function(name) {
    return `Hello, ${name}!`;
};

// 箭头函数
let greet = (name) => {
    return `Hello, ${name}!`;
};

// 简化箭头函数
let greet = name => `Hello, ${name}!`;
```

### 函数参数

```javascript
// 默认参数
function greet(name = "World") {
    return `Hello, ${name}!`;
}

// 剩余参数
function sum(...numbers) {
    return numbers.reduce((acc, num) => acc + num, 0);
}

// 参数解构
function printPerson({ name, age }) {
    console.log(`${name} is ${age} years old`);
}
```

## 5. 异步编程

### 回调函数

```javascript
function fetchData(callback) {
    setTimeout(() => {
        callback({ data: "Hello" });
    }, 1000);
}

fetchData(function(result) {
    console.log(result);
});
```

### Promise

```javascript
function fetchData() {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve({ data: "Hello" });
        }, 1000);
    });
}

fetchData()
    .then(result => console.log(result))
    .catch(error => console.error(error));
```

### async/await

```javascript
async function fetchData() {
    try {
        let response = await fetch("https://api.example.com/data");
        let data = await response.json();
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}
```

## 6. DOM操作

### 获取元素

```javascript
// 通过ID获取
let element = document.getElementById("myId");

// 通过类名获取
let elements = document.getElementsByClassName("myClass");

// 通过标签名获取
let elements = document.getElementsByTagName("div");

// 通过选择器获取
let element = document.querySelector(".myClass");
let elements = document.querySelectorAll(".myClass");
```

### 操作元素

```javascript
// 修改内容
element.innerHTML = "<p>Hello</p>";
element.textContent = "Hello";

// 修改样式
element.style.color = "red";
element.style.fontSize = "16px";

// 修改属性
element.setAttribute("class", "myClass");
element.getAttribute("class");
element.removeAttribute("class");

// 添加/删除类
element.classList.add("active");
element.classList.remove("active");
element.classList.toggle("active");
```

### 事件处理

```javascript
// 添加事件监听
element.addEventListener("click", function(event) {
    console.log("Clicked!");
});

// 移除事件监听
element.removeEventListener("click", handler);

// 事件对象
element.addEventListener("click", function(event) {
    event.preventDefault();      // 阻止默认行为
    event.stopPropagation();     // 阻止冒泡
    console.log(event.target);   // 触发事件的元素
});
```

## 7. ES6+特性

### 类

```javascript
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        return `Hello, ${this.name}!`;
    }
    
    static create(name, age) {
        return new Person(name, age);
    }
}

class Student extends Person {
    constructor(name, age, studentId) {
        super(name, age);
        this.studentId = studentId;
    }
    
    study() {
        return `${this.name} is studying`;
    }
}
```

### 模块

```javascript
// 导出
export const name = "John";
export function greet() {
    return "Hello!";
}

// 默认导出
export default class Person {
    // ...
}

// 导入
import { name, greet } from "./module";
import Person from "./module";
import * as module from "./module";
```

### Map和Set

```javascript
// Map
let map = new Map();
map.set("name", "John");
map.get("name");        // "John"
map.has("name");        // true
map.delete("name");
map.size;

// Set
let set = new Set([1, 2, 3, 3]);
set.add(4);
set.has(3);             // true
set.delete(3);
set.size;               // 3
```

## 8. 错误处理

### try-catch

```javascript
try {
    // 可能出错的代码
    let result = someFunction();
} catch (error) {
    console.error("Error:", error.message);
} finally {
    // 总是执行
    console.log("Finally");
}
```

### 自定义错误

```javascript
class CustomError extends Error {
    constructor(message, code) {
        super(message);
        this.code = code;
    }
}

try {
    throw new CustomError("Something went wrong", 500);
} catch (error) {
    if (error instanceof CustomError) {
        console.log(error.code, error.message);
    }
}
```

## 9. 工具函数

### 防抖和节流

```javascript
// 防抖
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// 节流
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
```

### 深拷贝

```javascript
function deepClone(obj) {
    if (obj === null || typeof obj !== "object") {
        return obj;
    }
    
    if (obj instanceof Date) {
        return new Date(obj.getTime());
    }
    
    if (obj instanceof Array) {
        return obj.map(item => deepClone(item));
    }
    
    if (obj instanceof Object) {
        let copy = {};
        Object.keys(obj).forEach(key => {
            copy[key] = deepClone(obj[key]);
        });
        return copy;
    }
}
```

## 10. 性能优化

### 事件委托

```javascript
// ❌ 低效（为每个元素添加事件）
document.querySelectorAll("li").forEach(li => {
    li.addEventListener("click", handleClick);
});

// ✅ 高效（事件委托）
document.querySelector("ul").addEventListener("click", function(event) {
    if (event.target.tagName === "LI") {
        handleClick(event);
    }
});
```

### 虚拟滚动

```javascript
// 使用虚拟滚动处理大列表
class VirtualScroller {
    constructor(container, itemHeight, renderItem) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItem = renderItem;
        this.items = [];
        this.startIndex = 0;
        
        container.addEventListener("scroll", () => this.onScroll());
    }
    
    setItems(items) {
        this.items = items;
        this.render();
    }
    
    onScroll() {
        this.startIndex = Math.floor(this.container.scrollTop / this.itemHeight);
        this.render();
    }
    
    render() {
        // 只渲染可见项
    }
}
```

## 相关页面

- [[前端设计系统]]
- [[HTML原型生成]]
- [[前端演示]]

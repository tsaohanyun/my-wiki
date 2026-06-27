---
title: "Shell脚本编程指南"
aliases:
  - Bash脚本编程
  - Shell编程
  - Bash指南
tags:
  - shell
  - bash
  - 脚本
  - 运维
  - 自动化
type: reference
status: active
created: 2025-01-01
updated: 2025-06-27
source: internal
difficulty: beginner
project: AI-Agent
---

# Shell脚本编程指南

## 概述

Shell脚本是运维自动化的基础工具。本文档涵盖Bash脚本的核心语法和实用技巧。

---

## 1. 脚本基础

### 1.1 Shebang与执行权限

```bash
#!/bin/bash
# 设置执行权限
chmod +x script.sh
# 执行脚本
./script.sh
# 或
bash script.sh
```

### 1.2 严格模式

```bash
#!/bin/bash
set -euo pipefail
# -e: 命令失败时立即退出
# -u: 使用未定义变量时报错
# -o pipefail: 管道中任意命令失败则整体失败
IFS=$'\n\t'  # 安全的内部字段分隔符
```

---

## 2. 变量

### 2.1 变量定义与使用

```bash
# 定义变量（等号两边不能有空格）
NAME="server-01"
PORT=8080
IS_ACTIVE=true

# 使用变量
echo "服务器: ${NAME}"
echo "端口: ${PORT}"

# 只读变量
readonly PI=3.14159

# 删除变量
unset TEMP_VAR
```

### 2.2 特殊变量

```bash
#!/bin/bash
echo "脚本名称: $0"
echo "参数个数: $#"
echo "所有参数: $@"
echo "所有参数(单字符串): $*"
echo "上一个命令退出码: $?"
echo "当前进程PID: $$"
echo "后台运行的最近PID: $!"
```

### 2.3 字符串操作

```bash
STR="Hello World"

# 字符串长度
echo ${#STR}          # 11

# 子字符串
echo ${STR:0:5}       # "Hello"

# 字符串替换
echo ${STR/World/Bash}  # "Hello Bash"

# 默认值
echo ${UNSET_VAR:-"默认值"}
echo ${UNSET_VAR:="赋默认值"}

# 模式匹配删除
FILE="archive.tar.gz"
echo ${FILE%.tar.gz}   # "archive"
echo ${FILE##*.}        # "gz"
```

### 2.4 数组

```bash
# 索引数组
FRUITS=("apple" "banana" "cherry")
echo ${FRUITS[0]}        # "apple"
echo ${FRUITS[@]}         # 所有元素
echo ${#FRUITS[@]}        # 数组长度

# 添加元素
FRUITS+=("date")

# 关联数组（Bash 4+）
declare -A SERVERS
SERVERS[web]="192.168.1.10"
SERVERS[db]="192.168.1.20"
echo ${SERVERS[web]}

# 遍历数组
for fruit in "${FRUITS[@]}"; do
    echo "$fruit"
done

# 遍历关联数组
for key in "${!SERVERS[@]}"; do
    echo "$key -> ${SERVERS[$key]}"
done
```

---

## 3. 条件判断

### 3.1 if 语句

```bash
# 基本语法
if [ "$count" -gt 10 ]; then
    echo "大于10"
elif [ "$count" -eq 10 ]; then
    echo "等于10"
else
    echo "小于10"
fi

# [[ ]] 更安全（支持正则）
if [[ "$input" =~ ^[0-9]+$ ]]; then
    echo "是数字"
fi

# 逻辑运算
if [[ "$a" -gt 0 && "$b" -gt 0 ]]; then
    echo "都大于0"
fi
```

### 3.2 文件测试

```bash
FILE="/etc/nginx/nginx.conf"

[ -f "$FILE" ]    # 文件存在且是普通文件
[ -d "$DIR" ]     # 目录存在
[ -r "$FILE" ]    # 可读
[ -w "$FILE" ]    # 可写
[ -x "$FILE" ]    # 可执行
[ -s "$FILE" ]    # 文件非空
[ -L "$FILE" ]    # 是符号链接
[ "$A" -nt "$B" ] # A比B新
[ "$A" -ot "$B" ] # A比B旧
```

### 3.3 case 语句

```bash
case "$1" in
    start)
        start_service
        ;;
    stop|shutdown)
        stop_service
        ;;
    restart)
        stop_service
        start_service
        ;;
    status)
        check_status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

---

## 4. 循环

### 4.1 for 循环

```bash
# 列表遍历
for server in web01 web02 web03; do
    echo "部署到 $server"
done

# C风格for循环
for ((i=0; i<10; i++)); do
    echo "序号: $i"
done

# 序列
for i in {1..100}; do
    echo $i
done

# 带步长
for i in {0..100..5}; do
    echo $i
done

# 遍历文件
for file in /var/log/*.log; do
    echo "处理: $file"
done

# 命令替换
for user in $(cat /etc/passwd | cut -d: -f1); do
    echo "用户: $user"
done
```

### 4.2 while 循环

```bash
# 基本while
counter=0
while [ $counter -lt 5 ]; do
    echo "计数: $counter"
    ((counter++))
done

# 读取文件
while IFS= read -r line; do
    echo "行: $line"
done < /etc/hosts

# 读取命令输出
while IFS=: read -r user _ uid _; do
    if [ "$uid" -ge 1000 ]; then
        echo "普通用户: $user (UID=$uid)"
    fi
done < /etc/passwd

# 无限循环
while true; do
    check_health || send_alert
    sleep 60
done
```

### 4.3 select 菜单

```bash
echo "选择操作:"
select opt in "启动服务" "停止服务" "重启服务" "退出"; do
    case $opt in
        "启动服务") start_service; break ;;
        "停止服务") stop_service; break ;;
        "重启服务") restart_service; break ;;
        "退出") exit 0 ;;
        *) echo "无效选项" ;;
    esac
done
```

---

## 5. 函数

### 5.1 函数定义

```bash
# 方式一
function greet() {
    local name="$1"
    echo "Hello, $name!"
}

# 方式二
log_info() {
    local msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] INFO: $msg"
}

# 调用
greet "World"
log_info "服务启动成功"
```

### 5.2 返回值

```bash
# 通过return返回状态码
is_running() {
    local pid="$1"
    if kill -0 "$pid" 2>/dev/null; then
        return 0  # 成功
    else
        return 1  # 失败
    fi
}

# 通过echo返回数据
get_ip() {
    local iface="$1"
    ip -4 addr show "$iface" | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
}

# 使用
if is_running 1234; then
    echo "进程运行中"
fi

MY_IP=$(get_ip eth0)
echo "IP地址: $MY_IP"
```

### 5.3 陷阱处理（Trap）

```bash
cleanup() {
    echo "清理临时文件..."
    rm -f "$TEMP_FILE"
    echo "清理完成"
}

trap cleanup EXIT  # 脚本退出时自动调用

TEMP_FILE=$(mktemp)
echo "临时文件: $TEMP_FILE"

# 也可以捕获特定信号
trap 'echo "收到SIGINT"; exit 1' INT
trap 'echo "收到SIGTERM"; exit 1' TERM
```

---

## 6. 输入/输出与重定向

```bash
# 标准输出/错误重定向
command > output.log 2>&1
command &> output.log         # 等价写法
command > /dev/null 2>&1      # 丢弃所有输出

# 追加
echo "日志条目" >> app.log

# Here Document
cat <<EOF > /etc/nginx/conf.d/app.conf
server {
    listen 80;
    server_name ${DOMAIN};
    root /var/www/${DOMAIN};
}
EOF

# Here String
grep "error" <<< "$log_content"

# 进程替换
diff <(sort file1.txt) <(sort file2.txt)
```

---

## 7. 实用技巧

### 7.1 参数解析

```bash
#!/bin/bash
set -euo pipefail

usage() {
    echo "用法: $0 [-h] [-v] [-c config] [-n name]"
    echo "  -h  显示帮助"
    echo "  -v  详细模式"
    echo "  -c  配置文件路径"
    echo "  -n  名称"
    exit 0
}

VERBOSE=false
CONFIG=""
NAME=""

while getopts "hvc:n:" opt; do
    case $opt in
        h) usage ;;
        v) VERBOSE=true ;;
        c) CONFIG="$OPTARG" ;;
        n) NAME="$OPTARG" ;;
        *) usage ;;
    esac
done
shift $((OPTIND - 1))

$VERBOSE && echo "配置: $CONFIG, 名称: $NAME"
```

### 7.2 并行执行

```bash
#!/bin/bash

# 使用 & 和 wait
for server in {1..10}; do
    (
        echo "部署 server-$server ..."
        sleep 2
        echo "server-$server 完成"
    ) &
done
wait  # 等待所有后台任务完成

# 使用 xargs 并行
cat servers.txt | xargs -P 5 -I {} ssh {} "uptime"

# 使用 GNU parallel
parallel -j 4 ssh {} uptime ::: server{1..10}
```

### 7.3 锁机制

```bash
#!/bin/bash
LOCKFILE="/tmp/script.lock"

# 创建锁
acquire_lock() {
    if [ -f "$LOCKFILE" ]; then
        local pid=$(cat "$LOCKFILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "另一个实例正在运行 (PID: $pid)"
            exit 1
        fi
    fi
    echo $$ > "$LOCKFILE"
    trap 'rm -f "$LOCKFILE"' EXIT
}

acquire_lock
echo "开始执行..."
```

### 7.4 日志框架

```bash
#!/bin/bash

LOG_FILE="/var/log/myscript.log"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

declare -A LOG_LEVELS=([DEBUG]=0 [INFO]=1 [WARN]=2 [ERROR]=3 [FATAL]=4)

log() {
    local level="$1"
    local msg="$2"
    local current=${LOG_LEVELS[$LOG_LEVEL]}
    local target=${LOG_LEVELS[$level]}

    [ "$target" -lt "$current" ] && return

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S.%3N')
    local line="[$timestamp] [$level] [$$] $msg"
    echo "$line" | tee -a "$LOG_FILE" >&2
}

log_debug "调试信息"
log_info "正常信息"
log_warn "警告信息"
log_error "错误信息"
log_fatal "致命错误"
```

---

## 最佳实践

| 编号 | 实践 | 说明 |
|------|------|------|
| 1 | 始终使用 `set -euo pipefail` | 防止错误静默传播 |
| 2 | 变量加双引号 | 防止单词分割和通配符展开 |
| 3 | 使用 `local` 声明函数变量 | 避免变量污染全局作用域 |
| 4 | 使用 `[[ ]]` 替代 `[ ]` | 更安全的条件判断 |
| 5 | 用 `mktemp` 创建临时文件 | 配合 `trap EXIT` 清理 |
| 6 | 日志输出到 stderr | stdout 留给数据输出 |
| 7 | 使用 ShellCheck 检查 | `shellcheck script.sh` |
| 8 | 注释复杂逻辑 | 维护性优先 |

---

## 相关页面

- [[Terraform基础设施即代码]] - 基础设施自动化管理
- [[Grafana可视化指南]] - 日志与监控可视化
- [[ELK进阶配置]] - 日志收集与分析
- [[监控告警体系设计]] - 监控告警完整方案

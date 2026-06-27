---
title: Linux运维常用命令
aliases: [Linux命令, 运维命令, Shell命令]
tags: [linux, 运维, shell]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: beginner
project: 运维
---
# Linux 运维常用命令

## 概述

本指南提供Linux运维的常用命令和最佳实践。

## 1. 文件操作

### 文件查看

```bash
# 查看文件内容
cat filename

# 分页查看
less filename
more filename

# 查看前10行
head -n 10 filename

# 查看后10行
tail -n 10 filename

# 实时查看文件更新
tail -f filename
```

### 文件搜索

```bash
# 按名称搜索
find /path -name "*.log"

# 按类型搜索
find /path -type f -name "*.txt"

# 按大小搜索
find /path -size +100M

# 按时间搜索
find /path -mtime -7  # 7天内修改的文件

# 搜索文件内容
grep "keyword" filename
grep -r "keyword" /path  # 递归搜索
grep -i "keyword" filename  # 忽略大小写
```

### 文件权限

```bash
# 查看权限
ls -la

# 修改权限
chmod 755 filename
chmod u+x filename

# 修改所有者
chown user:group filename

# 递归修改
chown -R user:group /path
```

## 2. 进程管理

### 进程查看

```bash
# 查看所有进程
ps aux

# 按CPU排序
ps aux --sort=-%cpu

# 按内存排序
ps aux --sort=-%mem

# 查看指定进程
ps aux | grep nginx

# 实时查看进程
top
htop
```

### 进程控制

```bash
# 杀死进程
kill pid
kill -9 pid  # 强制杀死

# 杀死所有同名进程
killall nginx

# 后台运行
command &

# 查看后台任务
jobs

# 切换到前台
fg %job_id
```

## 3. 系统信息

### 系统状态

```bash
# 系统信息
uname -a

# 主机名
hostname

# 系统启动时间
uptime

# 内存使用
free -h

# 磁盘使用
df -h

# 磁盘空间
du -sh /path
```

### 网络信息

```bash
# IP地址
ip addr
ifconfig

# 网络连接
netstat -tuln
ss -tuln

# 路由表
ip route
route -n

# DNS查询
nslookup domain
dig domain
```

## 4. 网络操作

### 网络测试

```bash
# ping测试
ping google.com

# 端口测试
telnet host port
nc -zv host port

# 跟踪路由
traceroute host

# 网络抓包
tcpdump -i eth0
```

### 文件传输

```bash
# SCP传输
scp file user@host:/path
scp user@host:/path/file .

# rsync同步
rsync -avz /src/ user@host:/dst/

# wget下载
wget url

# curl请求
curl url
curl -X POST -d '{"key":"value"}' url
```

## 5. 系统管理

### 服务管理

```bash
# systemd服务
systemctl start service
systemctl stop service
systemctl restart service
systemctl status service
systemctl enable service
systemctl disable service

# 查看服务日志
journalctl -u service
journalctl -f -u service
```

### 定时任务

```bash
# 编辑定时任务
crontab -e

# 查看定时任务
crontab -l

# 定时任务格式
# 分 时 日 月 周 命令
0 2 * * * /path/script.sh  # 每天凌晨2点
```

### 用户管理

```bash
# 添加用户
useradd username

# 设置密码
passwd username

# 删除用户
userdel username

# 添加用户到组
usermod -aG groupname username

# 查看用户信息
id username
```

## 6. 日志管理

### 系统日志

```bash
# 查看系统日志
tail -f /var/log/syslog
tail -f /var/log/messages

# 查看认证日志
tail -f /var/log/auth.log

# 查看内核日志
dmesg
```

### 日志轮转

```bash
# 查看logrotate配置
cat /etc/logrotate.conf

# 手动轮转
logrotate -f /etc/logrotate.d/nginx
```

## 7. 性能监控

### CPU监控

```bash
# CPU使用率
top
vmstat 1
mpstat -P ALL 1

# CPU信息
lscpu
cat /proc/cpuinfo
```

### 内存监控

```bash
# 内存使用
free -h
vmstat 1

# 内存详情
cat /proc/meminfo
```

### 磁盘监控

```bash
# 磁盘使用
df -h

# 磁盘IO
iostat -x 1

# 磁盘详情
lsblk
fdisk -l
```

## 8. 压缩解压

### tar命令

```bash
# 打包
tar -cvf archive.tar /path

# 解包
tar -xvf archive.tar

# 打包压缩
tar -czvf archive.tar.gz /path

# 解压
tar -xzvf archive.tar.gz
```

### zip命令

```bash
# 压缩
zip -r archive.zip /path

# 解压
unzip archive.zip
```

## 9. 文本处理

### awk命令

```bash
# 打印指定列
awk '{print $1, $3}' filename

# 按条件过滤
awk '$3 > 100' filename

# 统计行数
awk 'END {print NR}' filename
```

### sed命令

```bash
# 替换文本
sed 's/old/new/g' filename

# 删除行
sed '3d' filename  # 删除第3行
sed '/pattern/d' filename  # 删除匹配行

# 插入行
sed '3i\new line' filename
```

## 相关页面

- [[Python运维脚本库]]
- [[SSH隧道与远程管理]]
- [[Docker容器化指南]]

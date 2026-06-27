---
title: "Linux内核调优"
aliases:
  - "Linux Kernel Tuning"
  - "内核优化"
  - "内核参数调优"
tags:
  - linux
  - kernel
  - performance
  - tuning
  - 运维进阶
type: reference
status: active
created: 2025-06-28
updated: 2025-06-28
source: "Linux官方文档、Red Hat调优指南、个人实践经验"
difficulty: advanced
project: "AI-Agent运维知识库"
---

# Linux内核调优

## 概述

Linux内核调优是高级运维的核心技能，涉及对CPU调度、内存管理、I/O子系统和网络栈的深度优化。合理的内核参数配置可以显著提升系统吞吐量、降低延迟、增强稳定性。

---

## 一、CPU调度优化

### 1.1 CPU调度器概述

Linux默认使用 **CFS (Completely Fair Scheduler)**（5.13+内核引入EEVDF），通过红黑树管理进程的虚拟运行时间（vruntime），确保公平分配CPU时间。

### 1.2 CPU亲和性（CPU Affinity）

通过 `taskset` 或 `sched_setaffinity` 将进程绑定到特定CPU核心，减少上下文切换和缓存失效。

```bash
# 查看进程当前CPU亲和性
taskset -p <pid>

# 绑定进程到CPU 0和1
taskset -cp 0,1 <pid>

# 启动时绑定
taskset -c 0,1 ./my_service
```

```c
// C代码示例：设置CPU亲和性
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>

int set_cpu_affinity(pid_t pid, int cpu) {
    cpu_set_t mask;
    CPU_ZERO(&mask);
    CPU_SET(cpu, &mask);
    if (sched_setaffinity(pid, sizeof(mask), &mask) == -1) {
        perror("sched_setaffinity");
        return -1;
    }
    return 0;
}
```

### 1.3 IRQ亲和性（IRQ Affinity）

将硬件中断绑定到特定CPU核心，避免IRQ风暴集中在单核：

```bash
# 查看网卡中断分配
cat /proc/interrupts | grep eth0

# 将中断(如IRQ 32)绑定到CPU 2
echo 4 > /proc/irq/32/smp_affinity   # 4 = 二进制 100，即CPU 2

# 批量设置网卡中断亲和性脚本
#!/bin/bash
NIC=eth0
IRQS=$(grep "$NIC" /proc/interrupts | cut -d: -f1 | tr -d ' ')
CPU=0
for IRQ in $IRQS; do
    echo $((1 << CPU)) > /proc/irq/$IRQ/smp_affinity
    CPU=$((CPU + 1))
done
```

### 1.4 调度器参数

```bash
# 查看当前调度器策略
cat /proc/sys/kernel/sched_latency_ns        # 目标调度延迟(默认6000000ns=6ms)
cat /proc/sys/kernel/sched_min_granularity_ns # 最小调度粒度(默认750000ns)
cat /proc/sys/kernel/sched_wakeup_granularity_ns # 唤醒抢占粒度(默认1000000ns)

# 低延迟场景(如交易系统)
sysctl -w kernel.sched_latency_ns=3000000
sysctl -w kernel.sched_min_granularity_ns=300000
sysctl -w kernel.sched_wakeup_granularity_ns=500000

# 高吞吐场景
sysctl -w kernel.sched_latency_ns=24000000
sysctl -w kernel.sched_min_granularity_ns=3000000
```

### 1.5 NUMA优化

```bash
# 查看NUMA拓扑
numactl --hardware
lscpu | grep NUMA

# 使用numactl绑定内存和CPU
numactl --cpunodebind=0 --membind=0 ./my_service

# 配置NUMA平衡
cat /proc/sys/kernel/numa_balancing
sysctl -w kernel.numa_balancing=1

# 使用numad自动管理NUMA亲和性
systemctl start numad
```

---

## 二、内存管理优化

### 2.1 内存参数总览

```bash
# 查看内存状态
free -h
cat /proc/meminfo
vmstat 1 5
```

### 2.2 Swappiness与Cache

```bash
# swappiness: 控制使用swap的倾向 (0-100, 默认60)
# 数据库/高性能场景设为 1-10
sysctl -w vm.swappiness=10

#vfs_cache_pressure: 控制回收dentry/inode缓存的倾向 (默认100)
# 降低值保留更多文件系统缓存
sysctl -w vm.vfs_cache_pressure=50

# dirty_ratio: 脏页占内存比例达到此值时，进程自行写入 (默认20)
sysctl -w vm.dirty_ratio=10

# dirty_background_ratio: 脏页达到此值时，内核后台写入 (默认10)
sysctl -w vm.dirty_background_ratio=5

# dirty_expire_centisecs: 脏数据存活时间(单位1/100秒，默认3000=30秒)
sysctl -w vm.dirty_expire_centisecs=1500

# 持久化配置
cat >> /etc/sysctl.conf << 'EOF'
vm.swappiness = 10
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
vm.dirty_expire_centisecs = 1500
vm.dirty_writeback_centisecs = 1500
EOF
sysctl -p
```

### 2.3 大页（HugePages）

大页减少页表遍历开销，适用于数据库（Oracle、PostgreSQL）和大内存应用：

```bash
# 查看大页状态
cat /proc/meminfo | grep -i huge

# 配置大页数量(假设每页2MB，需要分配4GB)
echo 2048 > /proc/sys/vm/nr_hugepages

# 永久配置
cat >> /etc/sysctl.conf << 'EOF'
vm.nr_hugepages = 2048
EOF

# 透明大页(THP) - 通常数据库建议关闭
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

### 2.4 OOM Killer调优

```bash
# OOM时禁止杀死的进程(如关键服务)
echo -17 > /proc/<pid>/oom_score_adj   # -17 = 完全禁止OOM kill

# 调整进程被OOM杀死的优先级(-1000到1000，越高越容易被杀)
echo 500 > /proc/<pid>/oom_score_adj

# 内核panic on OOM (不推荐，但某些核心系统使用)
sysctl -w vm.panic_on_oom=0

# overcommit策略
# 0: 启发式判断(默认)  1: 总是允许  2: 严格检查
sysctl -w vm.overcommit_memory=1
sysctl -w vm.overcommit_ratio=80
```

### 2.5 内存回收与Watermark

```bash
# zone的min/low/high watermark
cat /proc/zoneinfo | grep -E "Node|min|low|high|managed"

# min_free_kbytes: 保留的最小空闲内存
sysctl -w vm.min_free_kbytes=524288   # 512MB

# 水位线缩放因子(百分比)
sysctl -w vm.watermark_scale_factor=150
```

---

## 三、I/O子系统优化

### 3.1 I/O调度器

```bash
# 查看磁盘当前调度器
cat /sys/block/sda/queue/scheduler

# SSD推荐: none/mq-deadline
echo none > /sys/block/sda/queue/scheduler

# 机械硬盘推荐: bfq/mq-deadline (公平调度)
echo mq-deadline > /sys/block/sda/queue/scheduler

# NVMe通常使用none(无调度器)，减少延迟
echo none > /sys/block/nvme0n1/queue/scheduler
```

| 调度器 | 适用场景 | 特点 |
|--------|----------|------|
| `none` (noop) | NVMe/SSD | FIFO，无重排，最低延迟 |
| `mq-deadline` | SSD/通用 | 请求截止时间，防饥饿 |
| `bfq` | 机械硬盘/桌面 | 公平带宽分配，交互友好 |
| `kyber` | NVMe/高速SSD | 自适应，按延迟分桶 |

### 3.2 队列深度与预读

```bash
# 队列深度
cat /sys/block/sda/queue/nr_requests
echo 512 > /sys/block/sda/queue/nr_requests

# 读写预读
blockdev --getra /dev/sda          # 查看预读值
blockdev --setra 4096 /dev/sda     # 设置预读为4096扇区(2MB)

# I/O超时
echo 60 > /sys/block/sda/device/timeout

# 永久配置
cat >> /etc/udev/rules.d/60-io.rules << 'EOF'
ACTION=="add", KERNEL=="sd[a-z]", ATTR{queue/scheduler}="mq-deadline"
ACTION=="add", KERNEL=="nvme[0-9]+n[0-9]+", ATTR{queue/scheduler}="none"
ACTION=="add", KERNEL=="sd[a-z]", ATTR{queue/read_ahead_kb}="2048"
EOF
```

### 3.3 文件系统挂载优化

```bash
# ext4 挂载优化
mount -o noatime,nodiratime,data=writeback,barrier=0 /dev/sda1 /data

# /etc/fstab 持久化
/dev/sda1 /data ext4 noatime,nodiratime,data=writeback,barrier=0 0 0

# XFS 挂载优化(适合大文件)
mount -o noatime,nodiratime,largeio,inode64 /dev/sdb1 /mnt/xfs

# XFS格式化时指定参数
mkfs.xfs -f -d agcount=32 -l size=256m /dev/sdb1
```

### 3.4 I/O性能验证

```bash
# fio基准测试 - 随机读写
fio --name=rand-rw --ioengine=libaio --iodepth=32 \
    --rw=randrw --rwmixread=70 --bs=4k --direct=1 \
    --numjobs=4 --size=4G --runtime=60 --time_based \
    --group_reporting --filename=/dev/sdb

# 持续监控I/O
iostat -xm 1 10
```

---

## 四、网络栈优化

### 4.1 TCP核心参数

```bash
# === sysctl.conf 网络优化完整配置 ===

# TCP缓冲区
net.core.rmem_max = 16777216        # 接收缓冲区最大值(16MB)
net.core.wmem_max = 16777216        # 发送缓冲区最大值(16MB)
net.core.rmem_default = 262144      # 接收缓冲区默认值(256KB)
net.core.wmem_default = 262144      # 发送缓冲区默认值(256KB)
net.ipv4.tcp_rmem = 4096 87380 16777216   # TCP接收缓冲区(min/default/max)
net.ipv4.tcp_wmem = 4096 65536 16777216   # TCP发送缓冲区(min/default/max)

# 连接队列
net.core.somaxconn = 65535          # 全连接队列最大长度
net.core.netdev_max_backlog = 65535 # 网卡接收队列最大长度
net.ipv4.tcp_max_syn_backlog = 65535 # SYN队列最大长度

# TIME_WAIT优化
net.ipv4.tcp_max_tw_buckets = 1048576  # 最大TIME_WAIT数量
net.ipv4.tcp_tw_reuse = 1              # 允许TIME_WAIT复用(安全)
net.ipv4.tcp_fin_timeout = 15          # FIN-WAIT-2超时(默认60s)

# Keepalive
net.ipv4.tcp_keepalive_time = 600      # 空闲后发送keepalive(默认7200s)
net.ipv4.tcp_keepalive_intvl = 30      # keepalive探测间隔
net.ipv4.tcp_keepalive_probes = 3      # keepalive探测次数

# 快速回收与Fast Open
net.ipv4.tcp_fastopen = 3              # 启用TCP Fast Open(客户端+服务端)
net.ipv4.tcp_slow_start_after_idle = 0 # 禁用空闲后慢启动

# 拥塞控制算法
net.ipv4.tcp_congestion_control = bbr  # BBR拥塞控制
net.core.default_qdisc = fq            # 公平队列(BBR推荐搭配)

# 其他
net.ipv4.tcp_syncookies = 1            # 防SYN Flood
net.ipv4.tcp_no_metrics_save = 1       # 不缓存路由指标
net.ipv4.ip_local_port_range = 10000 65535  # 本地端口范围

sysctl -p
```

### 4.2 启用BBR拥塞控制

```bash
# 查看可用拥塞控制算法
sysctl net.ipv4.tcp_available_congestion_control

# 查看当前算法
sysctl net.ipv4.tcp_congestion_control

# 启用BBR(需内核4.9+)
sysctl -w net.core.default_qdisc=fq
sysctl -w net.ipv4.tcp_congestion_control=bbr

# 验证
lsmod | grep bbr
```

### 4.3 网卡中断与RPS/RFS

```bash
# 多队列网卡绑定
ethtool -L eth0 combined 8          # 设置8个收发队列

# RPS (Receive Packet Steering) - 软件RSS
# 将包分发到多个CPU处理
for i in /sys/class/net/eth0/queues/rx-*/rps_cpus; do
    echo ff > "$i"   # 所有CPU
done

# RFS (Receive Flow Steering) - 保持流亲和性
echo 32768 > /proc/sys/net/core/rps_sock_flow_entries
for i in /sys/class/net/eth0/queues/rx-*/rps_flow_cnt; do
    echo 4096 > "$i"
done

# 开启GRO/GSO
ethtool -K eth0 gro on gso on tso on
```

### 4.4 连接跟踪优化

```bash
# conntrack表大小
sysctl -w net.netfilter.nf_conntrack_max = 1048576
sysctl -w net.netfilter.nf_conntrack_buckets = 262144

# 超时优化
sysctl -w net.netfilter.nf_conntrack_tcp_timeout_established = 3600
sysctl -w net.netfilter.nf_conntrack_tcp_timeout_time_wait = 30
sysctl -w net.netfilter.nf_conntrack_tcp_timeout_close_wait = 30

# 查看当前conntrack使用
cat /proc/sys/net/netfilter/nf_conntrack_count
```

---

## 五、使用 tuned 自动化调优

```bash
# 安装tuned
yum install -y tuned
systemctl enable --now tuned

# 查看可用profile
tuned-adm list

# 常用profile
tuned-adm profile throughput-performance   # 高吞吐
tuned-adm profile latency-performance      # 低延迟
tuned-adm profile network-latency          # 网络低延迟
tuned-adm profile virtual-guest            # 虚拟机

# 自定义profile
mkdir -p /etc/tuned/my-profile
cat > /etc/tuned/my-profile/tuned.conf << 'EOF'
[main]
summary=Custom high-performance profile

[cpu]
governor=performance
energy_perf_bias=performance

[vm]
transparent_hugepages=never

[sysctl]
vm.swappiness = 10
net.ipv4.tcp_congestion_control = bbr
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
EOF

tuned-adm profile my-profile
```

---

## 六、监控与验证

### 6.1 关键监控指标

```bash
# 实时CPU上下文切换
vmstat 1
#   cs列: 上下文切换次数(>100000/s需关注)

# CPU调度延迟
perf sched latency

# 内存压力
cat /proc/pressure/memory

# I/O压力
cat /proc/pressure/io

# CPU压力
cat /proc/pressure/cpu
```

### 6.2 压力测试

```bash
# 使用stress-ng进行CPU/内存压测
stress-ng --cpu 4 --io 2 --vm 2 --vm-bytes 1G --timeout 60s --metrics-brief

# 网络基准
iperf3 -c <server_ip> -P 4 -t 30   # 多线程带宽测试

# 综合负载
sysbench --test=cpu --cpu-max-prime=20000 --threads=4 run
```

---

## 最佳实践

| 场景 | 关键调优项 | 注意事项 |
|------|-----------|----------|
| **数据库服务器** | swappiness=1, THP=never, 大页, IO调度=deadline | 先备份默认配置 |
| **Web服务器** | somaxconn=65535, BBR, netdev_max_backlog | 逐项调整并监控 |
| **高并发网关** | conntrack调优, RPS/RFS, 端口范围扩大 | 注意内存消耗 |
| **存储服务器** | IO调度, 预读, XFS, 队列深度 | 避免barrier=0用于关键数据 |
| **虚拟化宿主** | NUMA绑定, CPU隔离, transparent_hugepage=madvise | 避免NUMA跨节点 |

### 通用原则

1. **测量优先**：调优前先用基准工具（fio, iperf3, stress-ng）建立基线
2. **逐项调整**：每次只改一个参数，验证效果后再继续
3. **持久化**：临时 `sysctl -w` 测试有效后写入 `/etc/sysctl.conf`
4. **备份配置**：修改前 `sysctl -a > /tmp/sysctl_backup.txt`
5. **监控验证**：使用 `psipy`, `vmstat`, `iostat` 持续监控效果
6. **内核升级**：某些优化需要较新内核版本（BBR需4.9+，EEVDF需6.6+）

---

## 相关页面

- [[性能分析工具]] - 使用perf、eBPF等工具定位性能瓶颈
- [[高并发架构调优]] - Nginx与内核网络参数协同调优
- [[数据库高可用方案]] - 数据库服务器内核调优参考
- [[混沌工程]] - 在压力下验证调优效果

---

## 参考资料

- [Linux Kernel Documentation](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/)
- [Red Hat Performance Tuning Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/monitoring_and_managing_system_status_and_performance)
- [kernel.org TCP tuning](https://www.kernel.org/doc/html/latest/networking/ip-sysctl.html)
- Brendan Gregg: *Systems Performance* (2nd Edition)

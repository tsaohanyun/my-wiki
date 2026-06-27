---
title: "嵌入式Linux开发"
aliases:
  - Embedded Linux
  - 嵌入式Linux
  - Linux嵌入式
tags:
  - embedded
  - linux
  - buildroot
  - yocto
  - device-tree
  - cross-compile
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: "原创整理"
difficulty: advanced
project: "嵌入式开发Wiki"
---

# 嵌入式Linux开发

## 概述

嵌入式Linux开发是物联网、工业控制、消费电子等领域的核心技术栈。它涵盖从交叉编译工具链搭建到完整Linux系统定制（Buildroot/Yocto）、设备树配置及驱动开发等完整流程。

---

## 目录

1. [交叉编译工具链](#1-交叉编译工具链)
2. [Buildroot 系统构建](#2-buildroot-系统构建)
3. [Yocto 项目](#3-yocto-项目)
4. [设备树 Device Tree](#4-设备树-device-tree)
5. [最佳实践](#5-最佳实践)
6. [相关页面](#相关页面)

---

## 1. 交叉编译工具链

### 1.1 什么是交叉编译

在宿主机（x86_64 PC）上编译目标机（ARM/MIPS等架构）可执行代码的过程。

| 工具链类型 | 说明 | 适用场景 |
|---|---|---|
| Linaro Toolchain | Linaro维护，支持ARM | 快速原型开发 |
| Crosstool-NG | 可定制构建工具链 | 自定义需求 |
| GCC ARM | GCC官方ARM交叉编译器 | 通用ARM开发 |
| LLVM/Clang | 基于LLVM的交叉编译 | 新架构支持 |

### 1.2 安装交叉编译工具链

```bash
# Ubuntu/Debian 安装 ARM GCC 工具链
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# AArch64 工具链
sudo apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# 验证安装
arm-linux-gnueabihf-gcc --version
aarch64-linux-gnu-gcc --version
```

### 1.3 交叉编译示例

#### C程序

```c
// hello.c
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("Hello Embedded Linux!\n");
    printf("Running on ARM target.\n");
    return 0;
}
```

```bash
# 使用 ARM 交叉编译器编译
arm-linux-gnueabihf-gcc -o hello hello.c -Wall -O2

# 验证文件架构
file hello
# 输出示例: hello: ELF 32-bit LSB executable, ARM, EABI5 ...
```

#### 使用 CMake 进行交叉编译

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(CrossCompileDemo C)

set(CMAKE_C_STANDARD 99)

add_executable(hello hello.c)
target_compile_options(hello PRIVATE -Wall -Wextra -O2)
```

```cmake
# toolchain-arm.cmake - 交叉编译工具链文件
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(CMAKE_C_COMPILER   arm-linux-gnueabihf-gcc)
set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

```bash
# 使用工具链文件进行 CMake 交叉编译
mkdir build && cd build
cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-arm.cmake ..
make -j$(nproc)
```

### 1.4 交叉编译第三方库示例（以 zlib 为例）

```bash
# 下载并交叉编译 zlib
wget https://zlib.net/zlib-1.3.1.tar.gz
tar xzf zlib-1.3.1.tar.gz
cd zlib-1.3.1

CC=arm-linux-gnueabihf-gcc \
CFLAGS="-O2 -Wall" \
./configure --prefix=/opt/arm-libs/zlib

make -j$(nproc)
make install
```

---

## 2. Buildroot 系统构建

### 2.1 Buildroot 简介

Buildroot 是一个使用 Makefile 和 Kconfig 构建嵌入式Linux系统的框架，能够自动完成交叉编译工具链、内核、 bootloader、根文件系统的构建。

### 2.2 获取和配置

```bash
# 克隆 Buildroot（推荐使用 LTS 版本）
git clone https://git.buildroot.net/buildroot
cd buildroot

# 使用 QEMU ARM vexpress 配置作为起点
make qemu_arm_vexpress_defconfig

# 打开菜单配置
make menuconfig
```

### 2.3 关键配置项

| 配置路径 | 说明 |
|---|---|
| Target options → Target Architecture | 选择目标架构（ARM little-endian等） |
| Toolchain → Toolchain type | 选择内部/外部工具链 |
| System configuration | 主机名、root密码、网络配置 |
| Filesystem images | 根文件系统格式（ext4, squashfs等） |
| Target packages | 选择需要的用户空间包 |
| Kernel → Linux Kernel | 配置内核版本和选项 |

### 2.4 添加自定义包

```makefile
# package/myapp/myapp.mk
MYAPP_VERSION = 1.0.0
MYAPP_SITE = $(BR2_PACKAGE_MYAPP_SITE)
MYAPP_SITE_METHOD = local
MYAPP_DEPENDENCIES = libopenssl

define MYAPP_BUILD_CMDS
    $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) all
endef

define MYAPP_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/myapp $(TARGET_DIR)/usr/bin/myapp
    $(INSTALL) -D -m 0644 $(@D)/myapp.conf $(TARGET_DIR)/etc/myapp.conf
endef

define MYAPP_INSTALL_INIT_SYSV
    $(INSTALL) -D -m 0755 package/myapp/S99myapp \
        $(TARGET_DIR)/etc/init.d/S99myapp
endef

$(eval $(generic-package))
```

```ini
# package/myapp/Config.in
config BR2_PACKAGE_MYAPP
    bool "myapp"
    select BR2_PACKAGE_LIBOPENSSL
    help
      Custom application for embedded target.
```

### 2.5 构建完整系统

```bash
# 完整构建（首次约 30-60 分钟）
make -j$(nproc)

# 构建产物位置
ls -la output/images/
# sdcard.img  - SD卡镜像
# zImage      - 内核镜像
# rootfs.ext4 - 根文件系统
# *.dtb       - 设备树二进制

# 使用 QEMU 测试
qemu-system-arm -M vexpress-a9 \
    -kernel output/images/zImage \
    -dtb output/images/vexpress-v2p-ca9.dtb \
    -sd output/images/sdcard.img \
    -append "root=/dev/mmcblk0p2 console=ttyAMA0" \
    -nographic -m 512M
```

### 2.6 保存和恢复配置

```bash
# 保存自定义配置
make savedefconfig

# 配置文件保存在 configs/<custom>_defconfig
# 下次可直接使用
make <custom>_defconfig
```

---

## 3. Yocto 项目

### 3.1 Yocto 简介

Yocto Project 是一个开源协作项目，提供模板、工具和方法，帮助创建面向嵌入式产品的自定义Linux系统。它比 Buildroot 更强大，适合大规模商业产品开发。

### 3.2 环境准备

```bash
# 安装依赖
sudo apt-get install gawk wget git diffstat unzip texinfo gcc-multilib \
    build-essential chrpath socat cpio python3 python3-pip python3-pexpect \
    xz-utils debianutils iputils-ping python3-git python3-jinja2 \
    python3-subunit zstd liblz4-tool

# 下载 Yocto (推荐 LTS 版本)
git clone -b kirkstone git://git.yoctoproject.org/poky.git
cd poky
git clone -b kirkstone git://git.openembedded.org/meta-openembedded
```

### 3.3 初始化构建环境

```bash
# 初始化环境（每次开发前执行）
source oe-init-build-env build-dir

# 默认机器
# conf/local.conf 中 MACHINE ??= "qemuarm"
```

### 3.4 创建自定义 Recipe

```bash
# 创建自定义层
bitbake-layers create-layer meta-myproject
bitbake-layers add-layer meta-myproject
```

```python
# meta-myproject/recipes-myapp/myapp/myapp.bb

SUMMARY = "My Embedded Application"
DESCRIPTION = "Custom application for embedded Linux target"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://myapp.c \
    file://myapp.service \
    file://myapp.conf \
"

S = "${WORKDIR}"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o myapp myapp.c
}

do_install() {
    install -d ${D}${bindir}
    install -d ${D}${sysconfdir}
    install -d ${D}${systemd_system_unitdir}

    install -m 0755 myapp ${D}${bindir}/
    install -m 0644 myapp.conf ${D}${sysconfdir}/
    install -m 0644 myapp.service ${D}${systemd_system_unitdir}/
}

# 使用 systemd 服务
inherit systemd
SYSTEMD_AUTO_ENABLE = "enable"
SYSTEMD_SERVICE:${PN} = "myapp.service"

# 包依赖
RDEPENDS:${PN} += "bash"
```

```ini
# meta-myproject/recipes-myapp/myapp/myapp.service
[Unit]
Description=My Application Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/myapp
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3.5 构建镜像

```bash
# 构建基本镜像
bitbake core-image-minimal

# 构建带更多功能的镜像
bitbake core-image-sato

# 构建自定义镜像（在 local.conf 中添加自定义包）
# IMAGE_INSTALL:append = " myapp"

# 输出位置
# build-dir/tmp/deploy/images/qemuarm/
```

### 3.6 自定义镜像 Recipe

```python
# meta-myproject/recipes-core/images/my-image.bb

SUMMARY = "Custom Embedded Linux Image"
LICENSE = "MIT"

inherit core-image

# 基础包
IMAGE_INSTALL += " \
    packagegroup-core-boot \
    packagegroup-core-full-cmdline \
    openssh \
    openssh-sftp-server \
    nano \
    htop \
    i2c-tools \
    can-utils \
    myapp \
"

# 额外特性
IMAGE_FEATURES += " \
    ssh-server-openssh \
    tools-debug \
    package-management \
"

# 设置 root 密码
inherit extrausers
EXTRA_USERS_PARAMS = "usermod -P embedded root;"
```

### 3.7 Yocto 常用命令

```bash
# 清除某个 recipe 的构建
bitbake -c clean myapp

# 重新编译
bitbake -c compile -f myapp

# 查看所有任务
bitbake -c listtasks myapp

# 查看依赖关系
bitbake -g myapp

# 进入开发 shell
bitbake -c devshell myapp
```

---

## 4. 设备树 Device Tree

### 4.1 设备树概念

设备树（Device Tree）是描述硬件的数据结构，使Linux内核与硬件描述分离。它由源文件（`.dts`）编译为二进制（`.dtb`）。

```
.dts (设备树源文件)
  └── .dtsi (设备树包含文件，类似头文件)
.dtb (编译后的设备树二进制，由 bootloader 传递给内核)
```

### 4.2 设备树源码结构

```dts
// vexpress-v2p-ca9.dts 示例
/dts-v1/;

#include "vexpress-v2m.dtsi"

/ {
    model = "ARM Versatile Express";
    compatible = "arm,vexpress,v2p-ca9", "arm,vexpress";

    #address-cells = <2>;
    #size-cells = <2>;
    interrupt-parent = <&gic>;

    cpus {
        #address-cells = <1>;
        #size-cells = <0>;

        cpu@0 {
            device_type = "cpu";
            compatible = "arm,cortex-a9";
            reg = <0>;
            next-level-cache = <&L2>;
        };
    };

    memory@60000000 {
        device_type = "memory";
        reg = <0 0x60000000 0 0x40000000>; /* 1GB */
    };

    gic: interrupt-controller@1e001000 {
        compatible = "arm,cortex-a9-gic";
        #interrupt-cells = <3>;
        #address-cells = <0>;
        interrupt-controller;
        reg = <0 0x1e001000 0 0x1000>,
              <0 0x1e000100 0 0x100>;
    };

    uart0: serial@1e090000 {
        compatible = "arm,pl011", "arm,primecell";
        reg = <0 0x1e090000 0 0x1000>;
        interrupts = <0 5 4>;  /* GIC SPI interrupt 5, level-high */
        clocks = <&oscclk2>, <&oscclk1>;
        clock-names = "uartclk", "apb_pclk";
        status = "okay";
    };
};
```

### 4.3 常用设备树节点

#### GPIO 控制器

```dts
gpio0: gpio@1e000000 {
    compatible = "arm,pl061", "arm,primecell";
    reg = <0 0x1e000000 0 0x1000>;
    gpio-controller;
    #gpio-cells = <2>;
    interrupt-controller;
    #interrupt-cells = <2>;
    status = "okay";
};
```

#### I2C 总线

```dts
i2c0: i2c@1e000800 {
    compatible = "arm,versatile-i2c";
    reg = <0 0x1e000800 0 0x1000>;
    #address-cells = <1>;
    #size-cells = <0>;
    clock-frequency = <400000>;  /* 400kHz */
    status = "okay";

    /* I2C 设备节点 */
    temperature-sensor@48 {
        compatible = "ti,tmp102";
        reg = <0x48>;
    };

    eeprom@50 {
        compatible = "atmel,24c256";
        reg = <0x50>;
        pagesize = <64>;
    };
};
```

#### SPI 总线

```dts
spi0: spi@1e000c00 {
    compatible = "arm,pl022", "arm,primecell";
    reg = <0 0x1e000c00 0 0x1000>;
    #address-cells = <1>;
    #size-cells = <0>;
    status = "okay";

    flash@0 {
        compatible = "winbond,w25q128";
        reg = <0>;
        spi-max-frequency = <50000000>;  /* 50MHz */
        #address-cells = <1>;
        #size-cells = <1>;

        partition@0 {
            label = "bootloader";
            reg = <0x000000 0x040000>;
            read-only;
        };

        partition@40000 {
            label = "kernel";
            reg = <0x040000 0x400000>;
        };

        partition@440000 {
            label = "rootfs";
            reg = <0x440000 0xBC0000>;
        };
    };
};
```

### 4.4 编译设备树

```bash
# 使用内核自带工具编译
# 在内核源码目录下
make ARCH=arm dtbs

# 手动编译
dtc -I dts -O dtb -o board.dtb board.dts

# 反编译 dtb 为 dts
dtc -I dtb -O dts -o board.dts board.dtb

# 设备树覆盖（Device Tree Overlay）
dtc -@ -I dts -O dtb -o overlay.dtbo overlay.dts
```

### 4.5 设备树覆盖（Overlay）

```dts
// overlay.dts - 动态加载设备树片段
/dts-v1/;
/plugin/;

&i2c0 {
    status = "okay";

    new-sensor@40 {
        compatible = "bosch,bme280";
        reg = <0x40>;
    };
};
```

### 4.6 在运行时查看设备树

```bash
# 查看完整设备树
ls /sys/firmware/devicetree/base/

# 查看特定节点
cat /sys/firmware/devicetree/base/model

# 查看兼容性
cat /sys/firmware/devicetree/base/compatible

# 查看内核解析后的设备树
ls /proc/device-tree/
```

---

## 5. 最佳实践

### 5.1 工具链管理

- **使用工具链管理器**：如 `crosstool-NG` 或 `gcc-arm-embedded`，避免手动编译
- **固定版本**：生产环境锁定工具链版本，避免不兼容
- **验证ABI**：确保工具链ABI与目标系统匹配（如 `gnueabihf` vs `gnueabi`）

### 5.2 Buildroot vs Yocto 选择

| 特性 | Buildroot | Yocto |
|---|---|---|
| 学习曲线 | 低 | 高 |
| 构建速度 | 快（分钟级） | 慢（小时级） |
| 包管理 | 无（静态镜像） | 支持 RPM/DEB/IPK |
| 社区支持 | 活跃 | 非常活跃 |
| 商业支持 | 有限 | 广泛（公司参与） |
| 适用场景 | 简单产品、原型 | 复杂产品、长期维护 |

### 5.3 安全加固

```bash
# 禁用不必要的服务
# 在 /etc/inittab 或 systemd 中注释不需要的服务

# 配置防火墙（如果使用 iptables）
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # SSH
iptables -A INPUT -j DROP
iptables-save > /etc/iptables/rules.v4

# 配置只读根文件系统（squashfs + overlayfs）
```

### 5.4 性能优化

```bash
# 禁用内核调试选项（生产环境）
# CONFIG_DEBUG_INFO is not set
# CONFIG_KALLSYMS is not set

# 使用 squashfs + lz4 压缩减小镜像体积
# Buildroot: BR2_TARGET_ROOTFS_SQUASHFS4_LZ4=y

# 启用 zRAM 压缩内存
echo lz4 > /sys/block/zram0/comp_algorithm
echo 256M > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon /dev/zram0
```

### 5.5 调试技巧

```bash
# 使用 gdbserver 远程调试
# 目标机
gdbserver :9090 ./myapp

# 宿主机
arm-linux-gnueabihf-gdb ./myapp
(gdb) target remote <target_ip>:9090
(gdb) continue

# 使用 strace 跟踪系统调用
strace -f -e trace=open,read,write ./myapp

# 查看内核日志
dmesg | tail -20

# 使用 ftrace 跟踪内核函数
echo function > /sys/kernel/debug/tracing/current_tracer
echo schedule > /sys/kernel/debug/tracing/set_ftrace_filter
cat /sys/kernel/debug/tracing/trace
```

---

## 相关页面

- [[RTOS开发指南]] - FreeRTOS 任务调度与同步机制
- [[STM32开发指南]] - STM32 HAL库与外设开发
- [[树莓派开发指南]] - 树莓派 GPIO 与传感器开发
- [[单片机通信协议]] - UART/SPI/I2C/CAN 通信详解

---

## 参考资源

- [Buildroot 官方文档](https://buildroot.org/docs.html)
- [Yocto Project 文档](https://docs.yoctoproject.org/)
- [Device Tree 规范](https://www.devicetree.org/)
- [ARM 交叉编译指南](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain)
- [嵌入式 Linux Wiki](https://elinux.org/Main_Page)

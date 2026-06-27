---
title: "嵌入式Linux开发"
aliases:
  - Embedded Linux Development
  - 嵌入式Linux
  - Linux嵌入式
tags:
  - embedded
  - linux
  - buildroot
  - yocto
  - driver
  - device-tree
  - cross-compile
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: "原创整理 + 官方文档"
difficulty: advanced
project: "嵌入式IoT知识库"
---

# 嵌入式Linux开发

> 本页面涵盖嵌入式Linux开发的核心知识：交叉编译工具链、Buildroot / Yocto 构建系统、设备树配置、内核驱动开发等。

---

## 目录

- [1. 交叉编译工具链](#1-交叉编译工具链)
- [2. Buildroot 构建系统](#2-buildroot-构建系统)
- [3. Yocto Project](#3-yocto-project)
- [4. 设备树 (Device Tree)](#4-设备树-device-tree)
- [5. 内核驱动开发](#5-内核驱动开发)
- [6. 最佳实践](#6-最佳实践)
- [相关页面](#相关页面)

---

## 1. 交叉编译工具链

### 1.1 什么是交叉编译

交叉编译是在宿主机（如 x86_64 PC）上编译出目标平台（如 ARM、RISC-V）可执行代码的过程。

### 1.2 获取工具链

```bash
# 方式一：使用 Linaro 官方工具链
wget https://releases.linaro.org/components/toolchain/binaries/latest-7/aarch64-linux-gnu/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu.tar.xz
tar xf gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu.tar.xz
export CROSS_COMPILE=$(pwd)/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu/bin/aarch64-linux-gnu-

# 方式二：使用 crosstool-NG 自定义构建
git clone https://github.com/crosstool-ng/crosstool-ng.git
cd crosstool-ng
./bootstrap
./configure --enable-local
make && make install
ct-ng aarch64-rpi3-linux-gnu
ct-ng build
```

### 1.3 交叉编译示例

```bash
# 设置环境变量
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-

# 交叉编译 C 程序
cat > hello.c << 'EOF'
#include <stdio.h>
int main() {
    printf("Hello from Embedded Linux!\n");
    return 0;
}
EOF

aarch64-linux-gnu-gcc -o hello hello.c -static
file hello
# 输出: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), statically linked

# 交叉编译 autotools 项目
./configure --host=aarch64-linux-gnu --prefix=/opt/target
make -j$(nproc)
make DESTDIR=$(pwd)/output install
```

### 1.4 交叉编译 CMake 项目

```cmake
# toolchain-aarch64.cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
set(CMAKE_FIND_ROOT_PATH /opt/aarch64-rootfs)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```

```bash
mkdir build && cd build
cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-aarch64.cmake ..
make -j$(nproc)
```

---

## 2. Buildroot 构建系统

### 2.1 Buildroot 简介

Buildroot 是一个简单高效的嵌入式 Linux 系统构建框架，使用 Makefile + Kconfig 管理整个系统构建。

### 2.2 快速开始

```bash
# 下载 Buildroot
git clone https://git.buildroot.net/buildroot
cd buildroot

# 选择默认配置
make defconfig                    # 通用默认
make raspberrypi4_64_defconfig    # 树莓派4 64位

# 配置内核和软件包
make menuconfig
```

### 2.3 关键配置项

```
Target options --->
  Target Architecture (ARM little-endian)
  Target Architecture Variant (cortex-A72)

Toolchain --->
  Toolchain type (External toolchain)
  Toolchain (Linaro ARM 2020.08)

System configuration --->
  Root filesystem overlay directories: $(BR2_EXTERNAL)/overlay/
  Custom scripts (post-build): support/scripts/post-build.sh

Kernel --->
  Linux Kernel (Enabled)
  Kernel configuration (Use a defconfig)
  Defconfig name: bcm2711

Target packages --->
  Networking applications --->
    [*] mosquitto
    [*] openssh
  Libraries --->
    [*] json-c
    [*] libcurl
```

### 2.4 添加自定义软件包

```makefile
# package/myapp/myapp.mk
MYAPP_VERSION = 1.0
MYAPP_SITE = $(BR2_EXTERNAL_MYAPP_PATH)/src/myapp
MYAPP_SITE_METHOD = local
MYAPP_DEPENDENCIES = libcurl json-c

define MYAPP_BUILD_CMDS
    $(MAKE) CC="$(TARGET_CC)" -C $(@D)
endef

define MYAPP_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/myapp $(TARGET_DIR)/usr/bin/myapp
    $(INSTALL) -D -m 0644 $(@D)/myapp.conf $(TARGET_DIR)/etc/myapp.conf
endef

$(eval $(generic-package))
```

```python
# package/myapp/Config.in
config BR2_PACKAGE_MYAPP
    bool "myapp"
    select BR2_PACKAGE_LIBCURL
    select BR2_PACKAGE_JSON_C
    help
      My custom IoT application.
```

### 2.5 构建与烧录

```bash
# 完整构建（首次约 30-60 分钟）
make -j$(nproc)

# 构建产物
ls output/images/
# sdcard.img  zImage  bcm2711-rpi-4-b.dtb  rootfs.ext4

# 烧录到 SD 卡
sudo dd if=output/images/sdcard.img of=/dev/sdX bs=4M status=progress
sync
```

---

## 3. Yocto Project

### 3.1 Yocto 简介

Yocto Project 是一个更强大的嵌入式 Linux 构建框架，提供层叠式架构、包管理、SDK 生成等高级功能。

### 3.2 快速开始

```bash
# 安装 Poky 基础发行版
git clone git://git.yoctoproject.org/poky
cd poky
git checkout kirkstone   # LTS 版本

# 初始化构建环境
source oe-init-build-env

# 编辑配置
# conf/local.conf
#   MACHINE ??= "raspberrypi4-64"
#   DL_DIR ?= "${TOPDIR}/../downloads"
#   IMAGE_FEATURES += "ssh-server-openssh"

# 开始构建
bitbake core-image-minimal
```

### 3.3 编写自定义 Recipe

```bash
# meta-custom/recipes-myapp/myapp/myapp.bb

SUMMARY = "My IoT Application"
DESCRIPTION = "Custom IoT sensor data collection daemon"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=..."

SRC_URI = "git://github.com/myorg/myapp.git;protocol=https;branch=main"
SRCREV = "${AUTOREV}"
S = "${WORKDIR}/git"

DEPENDS = "curl json-c"

inherit cmake pkgconfig

do_install:append() {
    install -d ${D}${sysconfdir}
    install -m 0644 ${S}/config/myapp.conf ${D}${sysconfdir}/
}

FILES:${PN} += "${sysconfdir}/myapp.conf"
```

### 3.4 创建自定义 Layer

```bash
# 使用 bitbake-layers 创建新层
bitbake-layers create-layer meta-custom

# 添加层到构建
bitbake-layers add-layer meta-custom

# 生成 SDK
bitbake -c populate_sdk core-image-minimal
# 产物在 tmp/deploy/sdk/ 下
```

### 3.5 Yocto 镜像定制

```bash
# custom-image.bb
require recipes-core/images/core-image-base.bb

IMAGE_FEATURES += "ssh-server-openssh package-management"

IMAGE_INSTALL += " \
    packagegroup-core-full-cmdline \
    mosquitto mosquitto-clients \
    python3 python3-pip \
    libgpiod libgpiod-tools \
    i2c-tools \
    custom-myapp \
"
```

---

## 4. 设备树 (Device Tree)

### 4.1 设备树概念

设备树（Device Tree）是一种描述硬件配置的数据结构，使内核与具体硬件描述分离。

### 4.2 基本语法

```dts
// 设备树源文件示例：自定义 LED 和 I2C 传感器
/dts-v1/;
/plugin/;

/ {
    compatible = "myboard,myboard-v1", "brcm,bcm2711";

    // LED 节点
    leds {
        compatible = "gpio-leds";

        status_led {
            label = "status";
            gpios = <&gpio 17 GPIO_ACTIVE_HIGH>;
            default-state = "off";
            linux,default-trigger = "heartbeat";
        };

        wifi_led {
            label = "wifi";
            gpios = <&gpio 18 GPIO_ACTIVE_HIGH>;
            default-state = "off";
        };
    };

    // I2C 传感器节点
    &i2c1 {
        #address-cells = <1>;
        #size-cells = <0>;
        status = "okay";

        bme280@76 {
            compatible = "bosch,bme280";
            reg = <0x76>;
            status = "okay";
        };

        oled@3c {
            compatible = "solomon,ssd1306fb-i2c";
            reg = <0x3c>;
            solomon,width = <128>;
            solomon,height = <64>;
            solomon,page-offset = <0>;
            status = "okay";
        };
    };
};
```

### 4.3 编译与反编译设备树

```bash
# 编译 DTS -> DTB
dtc -I dts -O dtb -o myboard.dtb myboard.dts

# 反编译 DTB -> DTS
dtc -I dtb -O dts -o myboard.dts myboard.dtb

# 在目标板上查看设备树
ls /proc/device-tree/
ls /sys/firmware/devicetree/base/

# 验证节点是否加载
ls /sys/bus/i2c/devices/
cat /sys/class/leds/status/trigger
```

### 4.4 Overlay 设备树

```bash
# 启用 Overlay 编译
make dtbs

# 运行时应用 Overlay（需要 CONFIG_OF_OVERLAY）
mkdir -p /sys/kernel/config/device-tree/overlays/my_overlay
echo -n "1" > /sys/kernel/config/configfs/init

# dtbo 数据写入
cat my_overlay.dtbo > /sys/kernel/config/device-tree/overlays/my_overlay/dtbo
echo 1 > /sys/kernel/config/device-tree/overlays/my_overlay/status
```

---

## 5. 内核驱动开发

### 5.1 字符设备驱动

```c
// chardev.c — 简单字符设备驱动
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/gpio.h>

#define DEVICE_NAME "gpio_ctrl"
#define GPIO_PIN 17
#define BUF_SIZE 256

static dev_t dev_num;
static struct cdev gpio_cdev;
static struct class *gpio_class;

static ssize_t gpio_write(struct file *file, const char __user *buf,
                          size_t count, loff_t *ppos)
{
    char kbuf[BUF_SIZE];
    size_t len = min(count, (size_t)(BUF_SIZE - 1));

    if (copy_from_user(kbuf, buf, len))
        return -EFAULT;

    kbuf[len] = '\0';

    if (kbuf[0] == '1')
        gpio_set_value(GPIO_PIN, 1);
    else if (kbuf[0] == '0')
        gpio_set_value(GPIO_PIN, 0);

    return len;
}

static ssize_t gpio_read(struct file *file, char __user *buf,
                         size_t count, loff_t *ppos)
{
    char val = gpio_get_value(GPIO_PIN) ? '1' : '0';
    return copy_to_user(buf, &val, 1) ? -EFAULT : 1;
}

static const struct file_operations gpio_fops = {
    .owner = THIS_MODULE,
    .write = gpio_write,
    .read  = gpio_read,
};

static int __init gpio_init(void)
{
    // 申请 GPIO
    if (gpio_request(GPIO_PIN, "gpio_ctrl_pin")) {
        pr_err("Failed to request GPIO %d\n", GPIO_PIN);
        return -EBUSY;
    }
    gpio_direction_output(GPIO_PIN, 0);

    // 动态分配设备号
    alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);

    // 初始化 cdev
    cdev_init(&gpio_cdev, &gpio_fops);
    gpio_cdev.owner = THIS_MODULE;
    cdev_add(&gpio_cdev, dev_num, 1);

    // 创建设备节点
    gpio_class = class_create(THIS_MODULE, DEVICE_NAME);
    device_create(gpio_class, NULL, dev_num, NULL, DEVICE_NAME);

    pr_info("GPIO control driver loaded (major=%d)\n", MAJOR(dev_num));
    return 0;
}

static void __exit gpio_exit(void)
{
    device_destroy(gpio_class, dev_num);
    class_destroy(gpio_class);
    cdev_del(&gpio_cdev);
    unregister_chrdev_region(dev_num, 1);
    gpio_free(GPIO_PIN);
    pr_info("GPIO control driver unloaded\n");
}

module_init(gpio_init);
module_exit(gpio_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("IoT Developer");
MODULE_DESCRIPTION("Simple GPIO Character Device Driver");
```

### 5.2 Makefile

```makefile
obj-m += chardev.o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
```

```bash
# 编译并加载
make
sudo insmod chardev.ko

# 测试
echo "1" > /dev/gpio_ctrl    # 点亮 LED
cat /dev/gpio_ctrl           # 读取 GPIO 状态

# 卸载
sudo rmmod chardev
```

### 5.3 平台驱动（Platform Driver）

```c
// platform_sensor.c — 平台总线驱动
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/of_device.h>

struct sensor_data {
    int reg_addr;
    struct device *dev;
};

static const struct of_device_id sensor_of_match[] = {
    { .compatible = "bosch,bme280", .data = (void *)0x76 },
    { .compatible = "bosch,bmp280", .data = (void *)0x77 },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, sensor_of_match);

static int sensor_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    const struct of_device_id *match;
    struct sensor_data *data;

    dev_info(dev, "Sensor driver probing...\n");

    data = devm_kzalloc(dev, sizeof(*data), GFP_KERNEL);
    if (!data)
        return -ENOMEM;

    match = of_match_device(sensor_of_match, dev);
    if (match)
        data->reg_addr = (int)(long)match->data;

    platform_set_drvdata(pdev, data);
    dev_info(dev, "Sensor at I2C addr 0x%02x\n", data->reg_addr);

    return 0;
}

static int sensor_remove(struct platform_device *pdev)
{
    dev_info(&pdev->dev, "Sensor driver removed\n");
    return 0;
}

static struct platform_driver sensor_driver = {
    .probe  = sensor_probe,
    .remove = sensor_remove,
    .driver = {
        .name = "bme280_sensor",
        .of_match_table = sensor_of_match,
    },
};

module_platform_driver(sensor_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("BME280 Platform Driver");
```

---

## 6. 最佳实践

### 6.1 构建系统选择

| 特性 | Buildroot | Yocto |
|------|-----------|-------|
| 学习曲线 | 低 | 高 |
| 构建速度 | 快（约30分钟） | 慢（首次2-4小时） |
| 包管理 | 无（整体rootfs） | 支持 RPM/DEB/IPK |
| 可维护性 | 适合中小型项目 | 适合大规模生产 |
| SDK 生成 | 基础 | 完整工具链 + SDK |
| 社区支持 | 活跃 | 非常活跃（企业级） |

### 6.2 安全加固

```bash
# 1. 启用内核安全特性
CONFIG_SECURITY=y
CONFIG_SECURITY_YAMA=y
CONFIG_HARDENED_USERCOPY=y
CONFIG_FORTIFY_SOURCE=y
CONFIG_STACKPROTECTOR_STRONG=y
CONFIG_MODULE_SIG=y

# 2. 禁用不必要的内核模块
# 通过 defconfig 移除不需要的功能

# 3. 启用 Secure Boot
# 使用 U-Boot Verified Boot 或 FIT Image 签名

# 4. Rootfs 只读
mount -o remount,ro /
# 使用 OverlayFS 管理可写层
```

### 6.3 调试技巧

```bash
# 内核日志
dmesg | tail -20
dmesg --follow   # 实时跟踪

# GPIO 调试（libgpiod）
gpioinfo gpiochip0
gpioset gpiochip0 17=1
gpioget gpiochip0 18

# I2C 调试
i2cdetect -y 1
i2cget -y 1 0x76 0xD0   # 读 BME280 ID 寄存器

# 使用 ftrace 追踪内核函数
echo function > /sys/kernel/debug/tracing/current_tracer
echo schedule > /sys/kernel/debug/tracing/set_ftrace_filter
cat /sys/kernel/debug/tracing/trace

# 性能分析
perf record -a -g -- sleep 10
perf report
```

---

## 相关页面

- [[MQTT协议实战]] — IoT 消息协议在嵌入式设备上的应用
- [[单片机开发指南]] — STM32 / FreeRTOS 裸机与 RTOS 开发
- [[IoT平台搭建]] — 设备管理与数据采集平台
- [[边缘AI部署]] — 在嵌入式 Linux 上部署 AI 模型

---

> **最后更新**：2026-06-28 | **维护者**：嵌入式IoT知识库

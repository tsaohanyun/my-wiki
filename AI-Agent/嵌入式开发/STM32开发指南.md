---
title: "STM32开发指南"
aliases:
  - STM32
  - STM32 HAL
  - STM32 CubeMX
  - STM32开发
tags:
  - embedded
  - stm32
  - hal
  - cubemx
  - dma
  - interrupt
  - communication
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: "原创整理"
difficulty: intermediate
project: "嵌入式开发Wiki"
---

# STM32开发指南

## 概述

STM32 是意法半导体（ST）推出的基于 ARM Cortex-M 内核的 32 位微控制器系列。本指南涵盖 HAL 库使用、CubeMX 配置、中断管理、DMA 传输、以及常用通信接口（UART/SPI/I2C）的开发方法。

---

## 目录

1. [STM32 系列概览](#1-stm32-系列概览)
2. [STM32CubeMX 配置](#2-stm32cubemx-配置)
3. [HAL 库基础](#3-hal-库基础)
4. [中断管理](#4-中断管理)
5. [DMA 传输](#5-dma-传输)
6. [通信接口](#6-通信接口)
7. [ADC 与 DAC](#7-adc-与-dac)
8. [定时器与 PWM](#8-定时器与-pwm)
9. [最佳实践](#9-最佳实践)
10. [相关页面](#相关页面)

---

## 1. STM32 系列概览

| 系列 | 内核 | 定位 | 典型应用 |
|---|---|---|---|
| STM32F0 | Cortex-M0 | 入门级 | 简单控制、家电 |
| STM32F1 | Cortex-M3 | 主流型 | 通用控制 |
| STM32F4 | Cortex-M4F | 高性能 | 电机控制、音频 |
| STM32F7 | Cortex-M7 | 超高性能 | 图形显示、AI |
| STM32H7 | Cortex-M7+M4 | 双核旗舰 | 高端工业 |
| STM32L4 | Cortex-M4F | 超低功耗 | 可穿戴、IoT |
| STM32G4 | Cortex-M4F | 混合信号 | 电机控制、电源 |
| STM32U5 | Cortex-M33 | 超低功耗+安全 | IoT安全 |
| STM32MP1 | Cortex-A7+M4 | 微处理器 | 高端嵌入式 |

---

## 2. STM32CubeMX 配置

### 2.1 工程创建流程

```
1. 打开 STM32CubeMX → New Project
2. 选择 MCU 型号（如 STM32F407VGT6）
3. 配置外设引脚（Pinout & Configuration）
4. 配置时钟树（Clock Configuration）
5. 配置 NVIC 中断优先级
6. 生成代码（Project Manager → Generate Code）
7. 在 IDE 中打开工程
```

### 2.2 关键配置项

#### 时钟配置

```c
// system_stm32f4xx.c / main.c 中由CubeMX生成
void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    // 配置外部高速晶振 8MHz
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 8;      // VCO输入 = 8/8 = 1MHz
    RCC_OscInitStruct.PLL.PLLN = 336;     // VCO输出 = 1*336 = 336MHz
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;  // SYSCLK = 336/2 = 168MHz
    RCC_OscInitStruct.PLL.PLLQ = 7;       // USB = 336/7 = 48MHz

    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        Error_Handler();
    }

    // 配置系统时钟
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK |
                                   RCC_CLOCKTYPE_SYSCLK |
                                   RCC_CLOCKTYPE_PCLK1 |
                                   RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;     // HCLK = 168MHz
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;      // APB1 = 42MHz
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;      // APB2 = 84MHz

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK) {
        Error_Handler();
    }
}
```

### 2.3 GPIO 配置

```c
// 在 CubeMX 中配置后，生成的初始化代码
void MX_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // 使能 GPIO 时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    // LED 输出（推挽）
    GPIO_InitStruct.Pin = GPIO_PIN_0 | GPIO_PIN_1;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    // 按键输入（上拉，中断模式）
    GPIO_InitStruct.Pin = GPIO_PIN_13;  // PC13 - User Button
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;  // 下降沿中断
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

    // 配置外部中断优先级
    HAL_NVIC_SetPriority(EXTI15_10_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
}
```

---

## 3. HAL 库基础

### 3.1 HAL 库 vs 标准外设库（SPL）

| 特性 | HAL 库 | 标准外设库 (SPL) |
|---|---|---|
| 抽象层级 | 高（硬件抽象层） | 低（直接寄存器封装） |
| 跨芯片兼容 | 好 | 差 |
| CubeMX 支持 | ✅ | ❌ |
| 代码体积 | 较大 | 较小 |
| 执行效率 | 中等 | 高 |
| ST 推荐度 | ⭐⭐⭐ | 已停止更新 |

### 3.2 HAL 库回调机制

```c
// HAL 库使用弱函数（__weak）实现回调
// 用户可以重写这些函数来自定义行为

// UART 接收完成回调
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        // USART1 接收完成处理
        uint8_t receivedByte = g_rxBuffer[0];
        RingBuffer_Write(&uartRxBuf, receivedByte);

        // 重新开启接收
        HAL_UART_Receive_IT(huart, g_rxBuffer, 1);
    }
}

// ADC 转换完成回调
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) {
        g_adcValue = HAL_ADC_GetValue(hadc);
        g_adcReady = 1;
    }
}

// 定时器周期回调
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM6) {
        g_timerFlag = 1;
    }
}
```

### 3.3 错误处理

```c
// 默认错误处理（CubeMX生成）
void Error_Handler(void) {
    __disable_irq();
    while (1) {
        // LED 快闪表示错误
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_0);
        HAL_Delay(100);
    }
}

// 自定义错误处理（带错误码）
#define ERR_UART_INIT    0x01
#define ERR_SPI_INIT     0x02
#define ERR_ADC_INIT     0x03

void Custom_ErrorHandler(uint32_t errorCode) {
    // 记录错误码到备份寄存器
    RTC->BKP0R = errorCode;

    // 通过LED闪烁次数表示错误类型
    while (1) {
        for (uint32_t i = 0; i < errorCode; i++) {
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_SET);
            HAL_Delay(200);
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET);
            HAL_Delay(200);
        }
        HAL_Delay(1000);
    }
}
```

---

## 4. 中断管理

### 4.1 NVIC 优先级

```c
// ARM Cortex-M 使用 4 位优先级（共16级）
// 数值越小优先级越高

// 抢占优先级 vs 子优先级
// HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4)
// 表示4位全部用于抢占优先级（推荐）

// 设置中断优先级
HAL_NVIC_SetPriority(USART1_IRQn, 0, 0);   // 最高
HAL_NVIC_SetPriority(EXTI0_IRQn, 1, 0);
HAL_NVIC_SetPriority(TIM2_IRQn, 2, 0);
HAL_NVIC_SetPriority(SysTick_IRQn, 15, 0);  // 最低
```

### 4.2 外部中断（EXTI）

```c
// 外部中断配置
void EXTI_Config(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOB_CLK_ENABLE();

    // PB12 外部中断，下降沿触发
    GPIO_InitStruct.Pin = GPIO_PIN_12;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    HAL_NVIC_SetPriority(EXTI15_10_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
}

// 中断服务函数（在 stm32f4xx_it.c 中）
void EXTI15_10_IRQHandler(void) {
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_12);
}

// 用户回调
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_12) {
        // 消抖
        HAL_Delay(20);
        if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_12) == GPIO_PIN_RESET) {
            g_buttonPressed = 1;
        }
    }
}
```

### 4.3 串口中断接收

```c
// 初始化变量
uint8_t g_rxByte;
uint8_t g_rxBuffer[256];
uint16_t g_rxIndex = 0;

// 开启中断接收
void UART_StartReceiving(UART_HandleTypeDef *huart) {
    HAL_UART_Receive_IT(huart, &g_rxByte, 1);
}

// 接收完成回调
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART2) {
        if (g_rxByte == '\n' || g_rxByte == '\r') {
            g_rxBuffer[g_rxIndex] = '\0';
            g_rxComplete = 1;
            g_rxIndex = 0;
        } else {
            if (g_rxIndex < sizeof(g_rxBuffer) - 1) {
                g_rxBuffer[g_rxIndex++] = g_rxByte;
            }
        }
        // 继续接收下一个字节
        HAL_UART_Receive_IT(huart, &g_rxByte, 1);
    }
}

// 空闲中断接收（更适合不定长数据）
void UART_EnableIdleIT(UART_HandleTypeDef *huart) {
    __HAL_UART_ENABLE_IT(huart, UART_IT_IDLE);
}

void USART2_IRQHandler(void) {
    if (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_IDLE)) {
        __HAL_UART_CLEAR_IDLEFLAG(&huart2);

        // 停止DMA传输
        HAL_UART_DMAStop(&huart2);

        // 计算接收长度
        uint16_t len = RX_BUF_SIZE - __HAL_DMA_GET_COUNTER(huart2.hdmarx);
        if (len > 0) {
            g_rxLength = len;
            g_rxComplete = 1;
        }

        // 重新启动DMA接收
        HAL_UART_Receive_DMA(&huart2, g_rxDmaBuffer, RX_BUF_SIZE);
    }
    HAL_UART_IRQHandler(&huart2);
}
```

---

## 5. DMA 传输

### 5.1 DMA 基础

DMA（直接内存访问）允许外设与内存之间直接传输数据，无需CPU干预，大幅提升系统效率。

```c
// DMA 流/通道映射（STM32F4）
// 每个 DMA 请求需要指定 Stream 和 Channel
// 如 USART1_TX → DMA2 Stream7 Channel4
```

### 5.2 DMA 配置（CubeMX生成）

```c
// DMA 初始化
void MX_DMA_Init(void) {
    __HAL_RCC_DMA2_CLK_ENABLE();

    // NVIC 配置 DMA中断
    HAL_NVIC_SetPriority(DMA2_Stream7_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(DMA2_Stream7_IRQn);
}
```

### 5.3 UART DMA 发送/接收

```c
#define TX_BUF_SIZE  256
#define RX_BUF_SIZE  256

uint8_t g_txBuf[TX_BUF_SIZE];
uint8_t g_rxBuf[RX_BUF_SIZE];
volatile uint8_t g_txComplete = 1;
volatile uint8_t g_rxComplete = 0;

// DMA 发送
HAL_StatusTypeDef UART_Send_DMA(UART_HandleTypeDef *huart,
                                 const uint8_t *data, uint16_t len) {
    if (!g_txComplete) {
        return HAL_BUSY;
    }

    memcpy(g_txBuf, data, len);
    g_txComplete = 0;

    return HAL_UART_Transmit_DMA(huart, g_txBuf, len);
}

// 发送完成回调
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
    g_txComplete = 1;
}

// 启动 DMA 接收
void UART_Start_Rx_DMA(UART_HandleTypeDef *huart) {
    HAL_UART_Receive_DMA(huart, g_rxBuf, RX_BUF_SIZE);
}

// 接收完成回调
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    g_rxComplete = 1;
}
```

### 5.4 ADC DMA 连续采样

```c
#define ADC_CHANNELS  3
#define ADC_SAMPLES   64

volatile uint16_t g_adcRawData[ADC_CHANNELS * ADC_SAMPLES];
volatile uint8_t g_adcConvComplete = 0;

// 初始化 ADC DMA
void ADC_DMA_Start(ADC_HandleTypeDef *hadc) {
    HAL_ADC_Start_DMA(hadc, (uint32_t *)g_adcRawData, ADC_CHANNELS * ADC_SAMPLES);
}

// DMA 转换完成回调
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
    g_adcConvComplete = 1;
}

// 计算平均值（滑动平均滤波）
void ADC_ProcessData(void) {
    if (!g_adcConvComplete) return;

    uint32_t sum[ADC_CHANNELS] = {0};

    for (uint16_t i = 0; i < ADC_SAMPLES; i++) {
        for (uint16_t ch = 0; ch < ADC_CHANNELS; ch++) {
            sum[ch] += g_adcRawData[i * ADC_CHANNELS + ch];
        }
    }

    for (uint16_t ch = 0; ch < ADC_CHANNELS; ch++) {
        g_adcAvgValue[ch] = sum[ch] / ADC_SAMPLES;
    }

    g_adcConvComplete = 0;
    // 重新开始
    HAL_ADC_Start_DMA(&hadc1, (uint32_t *)g_adcRawData, ADC_CHANNELS * ADC_SAMPLES);
}
```

---

## 6. 通信接口

### 6.1 UART 通信

```c
// UART 初始化（CubeMX生成）
UART_HandleTypeDef huart2;

void MX_USART2_UART_Init(void) {
    huart2.Instance = USART2;
    huart2.Init.BaudRate = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;

    if (HAL_UART_Init(&huart2) != HAL_OK) {
        Error_Handler();
    }
}

// printf 重定向（使用 UART 输出）
#include <stdio.h>

// 方式1：重写 fputc（适用于 Keil / GCC）
int fputc(int ch, FILE *f) {
    HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}

// 方式2：ITM 打印（SWO 调试接口）
int fputc(int ch, FILE *f) {
    ITM_SendChar(ch);
    return ch;
}
```

### 6.2 SPI 通信

```c
SPI_HandleTypeDef hspi1;

void MX_SPI1_Init(void) {
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;  // 168/16/2=5.25MHz
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_ENABLE;
    hspi1.Init.CRCPolynomial = 7;

    if (HAL_SPI_Init(&hspi1) != HAL_OK) {
        Error_Handler();
    }
}

// SPI 读写示例（Flash W25Q128）
#define W25Q_CS_LOW()   HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET)
#define W25Q_CS_HIGH()  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET)

// W25Q 命令定义
#define W25Q_CMD_READ    0x03
#define W25Q_CMD_WRITE   0x02
#define W25Q_CMD_WREN    0x06
#define W25Q_CMD_RDID    0x9F
#define W25Q_CMD_RDSR    0x05

// 读取 JEDEC ID
uint32_t W25Q_ReadID(void) {
    uint8_t cmd = W25Q_CMD_RDID;
    uint8_t id[3] = {0};

    W25Q_CS_LOW();
    HAL_SPI_Transmit(&hspi1, &cmd, 1, HAL_MAX_DELAY);
    HAL_SPI_Receive(&hspi1, id, 3, HAL_MAX_DELAY);
    W25Q_CS_HIGH();

    return (id[0] << 16) | (id[1] << 8) | id[2];
}

// 读取数据
void W25Q_Read(uint32_t addr, uint8_t *buf, uint16_t len) {
    uint8_t cmd[4] = {
        W25Q_CMD_READ,
        (addr >> 16) & 0xFF,
        (addr >> 8) & 0xFF,
        addr & 0xFF
    };

    W25Q_CS_LOW();
    HAL_SPI_Transmit(&hspi1, cmd, 4, HAL_MAX_DELAY);
    HAL_SPI_Receive(&hspi1, buf, len, HAL_MAX_DELAY);
    W25Q_CS_HIGH();
}

// 写入数据（需先擦除）
void W25Q_PageWrite(uint32_t addr, uint8_t *data, uint16_t len) {
    uint8_t cmd[4];

    // 写使能
    cmd[0] = W25Q_CMD_WREN;
    W25Q_CS_LOW();
    HAL_SPI_Transmit(&hspi1, cmd, 1, HAL_MAX_DELAY);
    W25Q_CS_HIGH();

    // 写数据
    cmd[0] = W25Q_CMD_WRITE;
    cmd[1] = (addr >> 16) & 0xFF;
    cmd[2] = (addr >> 8) & 0xFF;
    cmd[3] = addr & 0xFF;

    W25Q_CS_LOW();
    HAL_SPI_Transmit(&hspi1, cmd, 4, HAL_MAX_DELAY);
    HAL_SPI_Transmit(&hspi1, data, len, HAL_MAX_DELAY);
    W25Q_CS_HIGH();

    // 等待写入完成
    W25Q_WaitBusy();
}

// 等待Flash空闲
void W25Q_WaitBusy(void) {
    uint8_t cmd = W25Q_CMD_RDSR;
    uint8_t status = 0;

    do {
        W25Q_CS_LOW();
        HAL_SPI_Transmit(&hspi1, &cmd, 1, HAL_MAX_DELAY);
        HAL_SPI_Receive(&hspi1, &status, 1, HAL_MAX_DELAY);
        W25Q_CS_HIGH();
    } while (status & 0x01);  // BUSY bit
}
```

### 6.3 I2C 通信

```c
I2C_HandleTypeDef hi2c1;

void MX_I2C1_Init(void) {
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 400000;   // 400kHz Fast Mode
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;

    if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
        Error_Handler();
    }
}

// MPU6050 I2C 驱动示例
#define MPU6050_ADDR        (0x68 << 1)  // HAL需要8位地址
#define MPU6050_WHO_AM_I    0x75
#define MPU6050_PWR_MGMT_1  0x6B
#define MPU6050_ACCEL_XOUT_H 0x3B

// 检测设备
HAL_StatusTypeDef MPU6050_Test(void) {
    uint8_t whoami;
    return HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, MPU6050_WHO_AM_I,
                            I2C_MEMADD_SIZE_8BIT, &whoami, 1, 1000);
}

// 初始化 MPU6050
void MPU6050_Init(void) {
    uint8_t data = 0x00;  // 唤醒
    HAL_I2C_Mem_Write(&hi2c1, MPU6050_ADDR, MPU6050_PWR_MGMT_1,
                      I2C_MEMADD_SIZE_8BIT, &data, 1, 1000);
    HAL_Delay(100);
}

// 读取加速度数据
typedef struct {
    int16_t accel_x, accel_y, accel_z;
    int16_t temp;
    int16_t gyro_x, gyro_y, gyro_z;
} MPU6050_Data_t;

void MPU6050_ReadAll(MPU6050_Data_t *data) {
    uint8_t buf[14];

    // 从 0x3B 开始读取14字节
    HAL_I2C_Mem_Read(&hi2c1, MPU6050_ADDR, MPU6050_ACCEL_XOUT_H,
                     I2C_MEMADD_SIZE_8BIT, buf, 14, 1000);

    data->accel_x = (int16_t)((buf[0] << 8) | buf[1]);
    data->accel_y = (int16_t)((buf[2] << 8) | buf[3]);
    data->accel_z = (int16_t)((buf[4] << 8) | buf[5]);
    data->temp    = (int16_t)((buf[6] << 8) | buf[7]);
    data->gyro_x  = (int16_t)((buf[8] << 8) | buf[9]);
    data->gyro_y  = (int16_t)((buf[10] << 8) | buf[11]);
    data->gyro_z  = (int16_t)((buf[12] << 8) | buf[13]);
}

// 使用 DMA 读取 I2C
void MPU6050_ReadAll_DMA(MPU6050_Data_t *data) {
    static uint8_t dmaBuf[14];

    HAL_I2C_Mem_Read_DMA(&hi2c1, MPU6050_ADDR, MPU6050_ACCEL_XOUT_H,
                         I2C_MEMADD_SIZE_8BIT, dmaBuf, 14);

    // 在 HAL_I2C_MemRxCpltCallback 中处理数据
}
```

---

## 7. ADC 与 DAC

### 7.1 ADC 多通道扫描

```c
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;

#define ADC_CH_COUNT  4
volatile uint16_t g_adcValues[ADC_CH_COUNT];

void MX_ADC1_Init(void) {
    ADC_ChannelConfTypeDef sConfig = {0};

    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = ENABLE;              // 扫描模式
    hadc1.Init.ContinuousConvMode = ENABLE;        // 连续转换
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = ADC_CH_COUNT;     // 4个通道
    hadc1.Init.DMAContinuousRequests = ENABLE;     // DMA连续请求

    if (HAL_ADC_Init(&hadc1) != HAL_OK) {
        Error_Handler();
    }

    // 配置通道（顺序：PA0=CH0, PA1=CH1, PA2=CH2, PA3=CH3）
    uint32_t channels[] = {ADC_CHANNEL_0, ADC_CHANNEL_1,
                           ADC_CHANNEL_2, ADC_CHANNEL_3};

    for (uint8_t i = 0; i < ADC_CH_COUNT; i++) {
        sConfig.Channel = channels[i];
        sConfig.Rank = i + 1;
        sConfig.SamplingTime = ADC_SAMPLETIME_56CYCLES;

        if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) {
            Error_Handler();
        }
    }
}

// 启动 ADC+DMA
void ADC_StartConversion(void) {
    HAL_ADC_Start_DMA(&hadc1, (uint32_t *)g_adcValues, ADC_CH_COUNT);
}

// 获取转换后的电压
float ADC_GetVoltage(uint8_t channel) {
    if (channel >= ADC_CH_COUNT) return 0.0f;
    // 12位ADC, 参考电压3.3V
    return (float)g_adcValues[channel] * 3.3f / 4095.0f;
}
```

### 7.2 DAC 输出

```c
DAC_HandleTypeDef hdac;

void MX_DAC_Init(void) {
    DAC_ChannelConfTypeDef sConfig = {0};

    hdac.Instance = DAC;
    if (HAL_DAC_Init(&hdac) != HAL_OK) {
        Error_Handler();
    }

    sConfig.DAC_Trigger = DAC_TRIGGER_T2_TRGO;   // TIM2 触发
    sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;

    if (HAL_DAC_ConfigChannel(&hdac, &sConfig, DAC_CHANNEL_1) != HAL_OK) {
        Error_Handler();
    }
}

// 输出正弦波（查表法 + DMA）
#define SINE_TABLE_SIZE  256
static const uint16_t sineTable[SINE_TABLE_SIZE] = { /* 预计算的正弦表 */ };

void DAC_OutputSineWave(void) {
    HAL_DAC_Start_DMA(&hdac, DAC_CHANNEL_1,
                      (uint32_t *)sineTable, SINE_TABLE_SIZE,
                      DAC_ALIGN_12B_R);
}
```

---

## 8. 定时器与 PWM

### 8.1 基本定时

```c
TIM_HandleTypeDef htim6;

void MX_TIM6_Init(void) {
    htim6.Instance = TIM6;
    htim6.Init.Prescaler = 8399;       // 84MHz/(8399+1) = 10kHz
    htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim6.Init.Period = 9999;           // 10kHz/(9999+1) = 1Hz (1秒)
    htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;

    if (HAL_TIM_Base_Init(&htim6) != HAL_OK) {
        Error_Handler();
    }
}

// 启动定时器中断
HAL_TIM_Base_Start_IT(&htim6);

// 定时器中断回调
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM6) {
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);  // LED闪烁
    }
}
```

### 8.2 PWM 输出

```c
TIM_HandleTypeDef htim3;

void MX_TIM3_PWM_Init(void) {
    TIM_OC_InitTypeDef sConfigOC = {0};

    htim3.Instance = TIM3;
    htim3.Init.Prescaler = 83;          // 84MHz/(83+1) = 1MHz
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 999;            // 1MHz/(999+1) = 1kHz PWM频率
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;

    HAL_TIM_PWM_Init(&htim3);

    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 500;              // 50%占空比
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;

    HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1);

    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
}

// 动态修改占空比
void PWM_SetDuty(TIM_HandleTypeDef *htim, uint32_t channel, float percent) {
    uint32_t arr = __HAL_TIM_GET_AUTORELOAD(htim);
    uint32_t pulse = (uint32_t)((float)arr * percent / 100.0f);
    __HAL_TIM_SET_COMPARE(htim, channel, pulse);
}

// 呼吸灯效果
void LED_BreathingEffect(void) {
    static uint8_t brightness = 0;
    static int8_t direction = 1;

    for (;;) {
        PWM_SetDuty(&htim3, TIM_CHANNEL_1, brightness);
        brightness += direction;
        if (brightness >= 100 || brightness == 0) {
            direction = -direction;
        }
        HAL_Delay(10);
    }
}
```

### 8.3 输入捕获（测量频率）

```c
// 配置 TIM2 CH1 为输入捕获
void MX_TIM2_IC_Init(void) {
    TIM_IC_InitTypeDef sConfigIC = {0};

    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 83;          // 84MHz/(83+1) = 1MHz (1us分辨率)
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 0xFFFFFFFF;

    HAL_TIM_IC_Init(&htim2);

    sConfigIC.ICPolarity = TIM_ICPOLARITY_RISING;
    sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
    sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
    sConfigIC.ICFilter = 0;

    HAL_TIM_IC_ConfigChannel(&htim2, &sConfigIC, TIM_CHANNEL_1);
}

volatile uint32_t g_captureValue1 = 0;
volatile uint32_t g_captureValue2 = 0;
volatile uint8_t g_captureDone = 0;

// 输入捕获回调
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2 && htim->Channel == HAL_TIM_ACTIVE_CHANNEL_1) {
        if (g_captureDone == 0) {
            g_captureValue1 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
            g_captureDone = 1;
        } else {
            g_captureValue2 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
            g_captureDone = 2;
        }
    }
}

// 计算频率
float IC_GetFrequency(void) {
    if (g_captureDone == 2 && g_captureValue2 > g_captureValue1) {
        uint32_t diff = g_captureValue2 - g_captureValue1;
        g_captureDone = 0;
        return 1000000.0f / (float)diff;  // 1MHz时钟
    }
    return 0.0f;
}
```

---

## 9. 最佳实践

### 9.1 代码组织

```
Project/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── stm32f4xx_it.h
│   │   └── stm32f4xx_hal_conf.h
│   └── Src/
│       ├── main.c
│       ├── stm32f4xx_it.c
│       └── system_stm32f4xx.c
├── Drivers/          # HAL库 + CMSIS（CubeMX管理）
├── App/
│   ├── Inc/
│   │   ├── app_config.h
│   │   ├── app_sensors.h
│   │   └── app_comm.h
│   └── Src/
│       ├── app_sensors.c
│       └── app_comm.c
└── MDK-ARM/          # IDE工程文件
```

### 9.2 CubeMX 使用技巧

1. **不要修改 USER CODE BEGIN/END 之间的区域之外**：CubeMX 重新生成时会覆盖
2. **使用 User Labels**：在 CubeMX 中为引脚命名，生成有意义的宏定义
3. **备份 .ioc 文件**：这是 CubeMX 的工程文件，保存了所有配置

### 9.3 调试技巧

```c
// 使用 ITM 打印（无UART开销）
#include "stm32f4xx_hal.h"

#define ITM_Port8(n)    (*((volatile unsigned char *)(0xE0000000+4*n)))
#define ITM_Port16(n)   (*((volatile unsigned short*)(0xE0000000+4*n)))
#define ITM_Port32(n)   (*((volatile unsigned long *)(0xE0000000+4*n)))
#define DEMCR           (*((volatile unsigned long *)(0xE000EDFC)))
#define TRCENA          0x01000000

struct __FILE { int handle; };
FILE __stdout;
FILE __stdin;

int fputc(int ch, FILE *f) {
    if (DEMCR & TRCENA) {
        while (ITM_Port32(0) == 0);
        ITM_Port8(0) = ch;
    }
    return ch;
}

// 使用 DWT 周期计数器精确计时
#define DWT_Init()      do { CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk; \
                              DWT->CYCCNT = 0; DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk; } while(0)
#define DWT_GetTicks()  (DWT->CYCCNT)
#define DWT_Reset()     (DWT->CYCCNT = 0)

// 示例：测量函数执行时间
void MeasureFunctionTime(void) {
    DWT_Reset();
    // 被测代码
    SomeFunction();
    uint32_t ticks = DWT_GetTicks();
    float us = (float)ticks / 168.0f;  // 168MHz时钟
    printf("Execution time: %.2f us\n", us);
}
```

### 9.4 Flash 读写

```c
// 写入数据到 Flash（STM32F4）
#define FLASH_USER_START_ADDR  0x08060000
#define FLASH_USER_END_ADDR    0x08080000

HAL_StatusTypeDef Flash_Write(uint32_t address, uint32_t *data, uint16_t count) {
    HAL_StatusTypeDef status;

    // 1. 解锁 Flash
    status = HAL_FLASH_Unlock();
    if (status != HAL_OK) return status;

    // 2. 擦除扇区
    FLASH_EraseInitTypeDef EraseInitStruct;
    uint32_t SectorError;

    EraseInitStruct.TypeErase = FLASH_TYPEERASE_SECTORS;
    EraseInitStruct.VoltageRange = FLASH_VOLTAGE_RANGE_3;
    EraseInitStruct.Sector = FLASH_SECTOR_7;
    EraseInitStruct.NbSectors = 1;

    status = HAL_FLASHEx_Erase(&EraseInitStruct, &SectorError);
    if (status != HAL_OK) {
        HAL_FLASH_Lock();
        return status;
    }

    // 3. 写入数据（按字写入）
    for (uint16_t i = 0; i < count; i++) {
        status = HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD,
                                    address + i * 4, data[i]);
        if (status != HAL_OK) {
            HAL_FLASH_Lock();
            return status;
        }
    }

    // 4. 锁定 Flash
    HAL_FLASH_Lock();
    return HAL_OK;
}

// 读取 Flash 数据
void Flash_Read(uint32_t address, uint32_t *data, uint16_t count) {
    for (uint16_t i = 0; i < count; i++) {
        data[i] = *(__IO uint32_t *)(address + i * 4);
    }
}
```

### 9.5 看门狗配置

```c
// 独立看门狗（IWDG）
IWDG_HandleTypeDef hiwdg;

void MX_IWDG_Init(void) {
    hiwdg.Instance = IWDG;
    hiwdg.Init.Prescaler = IWDG_PRESCALER_64;   // LSI=32kHz, 32k/64=500Hz
    hiwdg.Init.Reload = 0xFFF;                    // 4095/500 ≈ 8.2秒超时

    if (HAL_IWDG_Init(&hiwdg) != HAL_OK) {
        Error_Handler();
    }
}

// 在主循环中喂狗
void HAL_IWDG_Refresh(void) {
    HAL_IWDG_Refresh(&hiwdg);
}

// 窗口看门狗（WWDG）- 更精确的超时控制
void MX_WWDG_Init(void) {
    // 窗口看门狗需要在特定窗口内刷新
    // 适用于需要精确时序的场景
}
```

---

## 相关页面

- [[RTOS开发指南]] - FreeRTOS 任务调度与同步机制
- [[嵌入式Linux开发]] - 嵌入式Linux系统构建与设备树
- [[树莓派开发指南]] - 树莓派 GPIO 与传感器开发
- [[单片机通信协议]] - UART/SPI/I2C/CAN 通信协议详解

---

## 参考资源

- [STM32 HAL 库文档](https://www.st.com/en/embedded-software/stm32cube-mcu-mpu-packages.html)
- [STM32CubeMX 下载](https://www.st.com/en/development-tools/stm32cubemx.html)
- [STM32 参考手册](https://www.st.com/resource/en/reference_manual/dm00031020-stm32f405-415-stm32f407-417-stm32f427-437-and-stm32f429-439-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf)
- [STM32 社区](https://community.st.com/)
- [HAL 驱动教程](https://controllerstech.com/)

---
title: "RTOS开发指南"
aliases:
  - RTOS
  - FreeRTOS
  - 实时操作系统
  - 任务调度
tags:
  - embedded
  - rtos
  - freertos
  - task-scheduling
  - semaphore
  - message-queue
type: guide
status: active
created: 2026-06-28
updated: 2026-06-28
source: "原创整理"
difficulty: advanced
project: "嵌入式开发Wiki"
---

# RTOS开发指南

## 概述

实时操作系统（RTOS）专为确定性响应设计，广泛应用于工业控制、汽车电子、医疗设备等领域。本指南以 **FreeRTOS** 为核心，涵盖任务调度、信号量、消息队列、内存管理等核心概念。

---

## 目录

1. [RTOS 基础概念](#1-rtos-基础概念)
2. [FreeRTOS 任务管理](#2-freertos-任务管理)
3. [任务间通信与同步](#3-任务间通信与同步)
4. [消息队列](#4-消息队列)
5. [定时器与软定时器](#5-定时器与软定时器)
6. [内存管理](#6-内存管理)
7. [最佳实践](#7-最佳实践)
8. [相关页面](#相关页面)

---

## 1. RTOS 基础概念

### 1.1 RTOS vs 裸机

| 特性 | 裸机（前后台系统） | RTOS |
|---|---|---|
| 架构 | 超级循环 + 中断 | 多任务抢占调度 |
| 响应时间 | 不确定 | 确定性（可计算最坏情况） |
| 模块化 | 差 | 好 |
| 资源消耗 | 极低 | 低（几KB RAM） |
| 适用场景 | 简单控制 | 复杂多任务系统 |

### 1.2 常见 RTOS 对比

| RTOS | 开源 | 特点 | 典型应用 |
|---|---|---|---|
| FreeRTOS | MIT | 轻量、社区活跃 | IoT、消费电子 |
| RT-Thread | Apache 2.0 | 中文生态、组件丰富 | 国内 IoT 项目 |
| Zephyr | Apache 2.0 | Linux基金会、安全性强 | 可穿戴、工业 |
| μC/OS-III | 商业许可 | 认证完善 | 航空、医疗 |
| ThreadX | MIT（开源） | Azure RTOS、高性能 | 消费电子 |

### 1.3 FreeRTOS 核心概念

```
┌─────────────────────────────────────────────┐
│            Application Code                  │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │
│  │Task 1│  │Task 2│  │Task 3│  │ ISR  │    │
│  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘   │
├─────┼─────────┼─────────┼─────────┼────────┤
│     │   FreeRTOS API 层  │         │        │
│  ┌──┴───────┬──┴───────┬──┴────┬───┴────┐  │
│  │Scheduler│Semaphore │ Queue │  Timer  │  │
│  └─────────┴──────────┴───────┴─────────┘  │
├─────────────────────────────────────────────┤
│            Hardware (MCU)                    │
└─────────────────────────────────────────────┘
```

---

## 2. FreeRTOS 任务管理

### 2.1 任务创建

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务函数原型
void vTaskSensor(void *pvParameters);
void vTaskDisplay(void *pvParameters);
void vTaskCommunication(void *pvParameters);

// 任务句柄（用于后续管理）
static TaskHandle_t xTaskSensorHandle = NULL;
static TaskHandle_t xTaskDisplayHandle = NULL;

// 任务参数结构体
typedef struct {
    uint32_t sample_rate;
    uint8_t  channel;
} SensorParams_t;

int main(void) {
    // 硬件初始化
    HAL_Init();
    SystemClock_Config();

    // 静态分配的任务参数
    static SensorParams_t sensorParams = {
        .sample_rate = 100,  // 100ms
        .channel = 1
    };

    // 创建任务
    BaseType_t result;

    result = xTaskCreate(
        vTaskSensor,          // 任务函数
        "SensorTask",         // 任务名（调试用）
        256,                  // 栈深度（字，256*4=1024字节）
        &sensorParams,        // 传入参数
        configMAX_PRIORITIES - 1,  // 最高优先级
        &xTaskSensorHandle    // 任务句柄
    );

    if (result != pdPASS) {
        // 任务创建失败处理
        Error_Handler();
    }

    xTaskCreate(
        vTaskDisplay,
        "DisplayTask",
        512,
        NULL,
        tskIDLE_PRIORITY + 1,
        &xTaskDisplayHandle
    );

    xTaskCreate(
        vTaskCommunication,
        "CommTask",
        1024,
        NULL,
        tskIDLE_PRIORITY + 2,
        NULL
    );

    // 启动调度器（永不返回）
    vTaskStartScheduler();

    // 如果调度器启动失败
    while (1);
}

// 传感器采集任务
void vTaskSensor(void *pvParameters) {
    SensorParams_t *params = (SensorParams_t *)pvParameters;
    TickType_t xLastWakeTime = xTaskGetTickCount();

    for (;;) {
        // 读取传感器数据
        uint16_t value = ADC_Read(params->channel);

        // 周期性延时（精确到tick）
        vTaskDelayUntil(&xLastWakeTime,
                        pdMS_TO_TICKS(params->sample_rate));
    }
}

// 显示任务
void vTaskDisplay(void *pvParameters) {
    for (;;) {
        Display_Update();
        vTaskDelay(pdMS_TO_TICKS(50));  // 50ms延时
    }
}

// 通信任务
void vTaskCommunication(void *pvParameters) {
    for (;;) {
        Comm_ProcessIncoming();
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

### 2.2 任务优先级

```c
// FreeRTOS 优先级: 数字越大优先级越高
// configMAX_PRIORITIES 定义最大优先级数

// 优先级分配建议:
#define PRIO_TASK_EMERGENCY   (configMAX_PRIORITIES - 1)  // 紧急任务（最高）
#define PRIO_TASK_CONTROL     (configMAX_PRIORITIES - 2)  // 控制环
#define PRIO_TASK_SENSOR      (configMAX_PRIORITIES - 3)  // 数据采集
#define PRIO_TASK_COMM        (configMAX_PRIORITIES - 4)  // 通信
#define PRIO_TASK_DISPLAY     (tskIDLE_PRIORITY + 2)      // 显示
#define PRIO_TASK_LOGGING     (tskIDLE_PRIORITY + 1)      // 日志
```

### 2.3 任务删除与状态查询

```c
// 删除任务
void vTaskDelete(TaskHandle_t xTaskToDelete);

// 示例：动态创建/删除任务
void TaskController(void *pvParameters) {
    TaskHandle_t xWorkerTask = NULL;

    for (;;) {
        EventBits_t events = xEventGroupWaitBits(
            xEventGroup,
            EVT_START_WORKER | EVT_STOP_WORKER,
            pdTRUE, pdFALSE, portMAX_DELAY
        );

        if (events & EVT_START_WORKER) {
            if (xWorkerTask == NULL) {
                xTaskCreate(vWorkerTask, "Worker", 256,
                           NULL, PRIO_WORKER, &xWorkerTask);
            }
        }

        if (events & EVT_STOP_WORKER) {
            if (xWorkerTask != NULL) {
                vTaskDelete(xWorkerTask);
                xWorkerTask = NULL;
            }
        }
    }
}

// 获取任务运行时统计
void PrintTaskStats(void) {
    // 需要启用 configUSE_TRACE_FACILITY 和
    // configGENERATE_RUN_TIME_STATS
    char buf[512];
    vTaskList(buf);
    printf("Task       State  Prio  Stack  Num\n");
    printf("%s\n", buf);
}

// 获取任务运行时间统计
void PrintRuntimeStats(void) {
    char buf[512];
    vTaskGetRunTimeStats(buf);
    printf("Task       Abs Time   %% Time\n");
    printf("%s\n", buf);
}
```

---

## 3. 任务间通信与同步

### 3.1 信号量

#### 二值信号量（Binary Semaphore）

```c
#include "semphr.h"

SemaphoreHandle_t xBinarySemaphore;

// 初始化
void App_Init(void) {
    xBinarySemaphore = xSemaphoreCreateBinary();
    if (xBinarySemaphore == NULL) {
        Error_Handler();  // 创建失败
    }
}

// ISR 中释放信号量
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    // 从ISR释放信号量
    xSemaphoreGiveFromISR(xBinarySemaphore,
                          &xHigherPriorityTaskWoken);

    // 如果唤醒了更高优先级的任务，请求上下文切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 任务中等待信号量
void vTaskButtonHandler(void *pvParameters) {
    for (;;) {
        // 阻塞等待信号量（无限等待）
        if (xSemaphoreTake(xBinarySemaphore, portMAX_DELAY) == pdTRUE) {
            Button_ProcessEvent();
        }
    }
}
```

#### 计数信号量（Counting Semaphore）

```c
SemaphoreHandle_t xCountingSemaphore;

void ResourcePool_Init(void) {
    // 最大计数5，初始计数5（5个可用资源）
    xCountingSemaphore = xSemaphoreCreateCounting(5, 5);
}

// 获取资源
BaseType_t AcquireResource(void) {
    // 等待最多100ms
    return xSemaphoreTake(xCountingSemaphore, pdMS_TO_TICKS(100));
}

// 释放资源
void ReleaseResource(void) {
    xSemaphoreGive(xCountingSemaphore);
}

// ISR 中使用
void UART_RxISR(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    BaseType_t xSendResult;

    // 数据到达时释放计数信号量
    xSendResult = xSemaphoreGiveFromISR(
        xCountingSemaphore,
        &xHigherPriorityTaskWoken
    );

    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

#### 互斥量

```c
SemaphoreHandle_t xMutex;

void SharedResource_Init(void) {
    // 创建互斥量（支持优先级继承）
    xMutex = xSemaphoreCreateMutex();
    configASSERT(xMutex != NULL);
}

// 保护共享资源（如全局日志缓冲区）
void Log_Write(const char *message) {
    // 获取互斥量（最多等待200ms）
    if (xSemaphoreTake(xMutex, pdMS_TO_TICKS(200)) == pdTRUE) {
        // 临界区：安全访问共享资源
        LogBuffer_Append(message);

        // 释放互斥量
        xSemaphoreGive(xMutex);
    } else {
        // 获取互斥量超时
        ErrorHandler_Report(ERR_MUTEX_TIMEOUT);
    }
}
```

> ⚠️ **互斥量 vs 二值信号量**：互斥量支持优先级继承，适合保护共享资源；二值信号量适合中断到任务的通知。互斥量**不能**在ISR中使用。

### 3.2 事件组

```c
#include "event_groups.h"

// 定义事件位
#define EVT_SENSOR_READY  (1 << 0)
#define EVT_NETWORK_UP    (1 << 1)
#define EVT_CONFIG_LOADED (1 << 2)
#define EVT_ALL           (EVT_SENSOR_READY | EVT_NETWORK_UP | EVT_CONFIG_LOADED)

EventGroupHandle_t xSystemEvents;

void System_Init(void) {
    xSystemEvents = xEventGroupCreate();
}

// 等待多个事件全部发生
void vTaskMainController(void *pvParameters) {
    for (;;) {
        // 等待所有事件（AND逻辑）
        EventBits_t bits = xEventGroupWaitBits(
            xSystemEvents,
            EVT_ALL,
            pdTRUE,    // 退出时清除事件
            pdTRUE,    // 等待所有事件（AND）
            portMAX_DELAY
        );

        if ((bits & EVT_ALL) == EVT_ALL) {
            System_Run();
        }
    }
}

// 等待任意一个事件发生（OR逻辑）
void vTaskAlertHandler(void *pvParameters) {
    for (;;) {
        EventBits_t bits = xEventGroupWaitBits(
            xSystemEvents,
            EVT_SENSOR_READY | EVT_NETWORK_UP,
            pdFALSE,   // 不清除
            pdFALSE,   // 任意一个（OR）
            portMAX_DELAY
        );

        if (bits & EVT_SENSOR_READY) {
            ProcessSensorData();
        }
        if (bits & EVT_NETWORK_UP) {
            SyncData();
        }
    }
}

// 设置事件
void OnSensorReady(void) {
    xEventGroupSetBits(xSystemEvents, EVT_SENSOR_READY);
}

// ISR 中设置事件
void ISR_Handler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xEventGroupSetBitsFromISR(
        xSystemEvents,
        EVT_NETWORK_UP,
        &xHigherPriorityTaskWoken
    );
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

---

## 4. 消息队列

### 4.1 基本队列操作

```c
#include "queue.h"

// 定义消息结构体
typedef struct {
    uint8_t  msg_id;
    uint16_t length;
    uint8_t  data[32];
} Message_t;

QueueHandle_t xMessageQueue;

#define QUEUE_LENGTH  20
#define QUEUE_ITEM_SIZE sizeof(Message_t)

void Queue_Init(void) {
    xMessageQueue = xQueueCreate(QUEUE_LENGTH, QUEUE_ITEM_SIZE);
    configASSERT(xMessageQueue != NULL);
}

// 发送任务
void vTaskProducer(void *pvParameters) {
    Message_t msg;
    uint8_t seq = 0;

    for (;;) {
        msg.msg_id = MSG_TYPE_SENSOR;
        msg.length = snprintf((char *)msg.data, 32,
                              "SEQ:%d TEMP:%d",
                              seq++, ReadTemperature());

        // 发送消息到队列（最多等待100ms）
        if (xQueueSend(xMessageQueue, &msg, pdMS_TO_TICKS(100)) != pdPASS) {
            // 队列满
            Log_Write("Queue full, message dropped");
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

// 接收任务
void vTaskConsumer(void *pvParameters) {
    Message_t receivedMsg;

    for (;;) {
        // 从队列接收消息（无限等待）
        if (xQueueReceive(xMessageQueue, &receivedMsg, portMAX_DELAY) == pdPASS) {
            switch (receivedMsg.msg_id) {
                case MSG_TYPE_SENSOR:
                    ProcessSensorMessage(&receivedMsg);
                    break;
                case MSG_TYPE_COMMAND:
                    ProcessCommandMessage(&receivedMsg);
                    break;
                default:
                    Log_Write("Unknown message type");
                    break;
            }
        }
    }
}
```

### 4.2 ISR 中使用队列

```c
// UART 接收中断处理
void USART1_RX_InterruptHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    Message_t isrMsg;

    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE)) {
        isrMsg.msg_id = MSG_TYPE_UART_RX;
        isrMsg.length = 1;
        isrMsg.data[0] = (uint8_t)(huart1.Instance->DR & 0xFF);

        // 从ISR发送到队列
        xQueueSendFromISR(
            xMessageQueue,
            &isrMsg,
            &xHigherPriorityTaskWoken
        );
    }

    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 4.3 队列集

```c
// 同时等待多个队列
QueueSetHandle_t xQueueSet;
QueueHandle_t xQueue1, xQueue2;

void QueueSet_Init(void) {
    // 创建队列集（总容量 = 队列1容量 + 队列2容量）
    xQueueSet = xQueueCreateSet(20 + 10);

    xQueue1 = xQueueCreate(20, sizeof(Message_t));
    xQueue2 = xQueueCreate(10, sizeof(uint32_t));

    // 将队列加入队列集
    xQueueAddToSet(xQueue1, xQueueSet);
    xQueueAddToSet(xQueue2, xQueueSet);
}

void vTaskMultiQueueHandler(void *pvParameters) {
    for (;;) {
        // 等待任意队列有数据
        QueueSetMemberHandle_t xActivatedMember =
            xQueueSelectFromSet(xQueueSet, portMAX_DELAY);

        if (xActivatedMember == xQueue1) {
            Message_t msg;
            xQueueReceive(xQueue1, &msg, 0);
            HandleMessage(&msg);
        } else if (xActivatedMember == xQueue2) {
            uint32_t value;
            xQueueReceive(xQueue2, &value, 0);
            HandleValue(value);
        }
    }
}
```

---

## 5. 定时器与软定时器

### 5.1 FreeRTOS 软件定时器

```c
#include "timers.h"

TimerHandle_t xTimerHeartbeat;
TimerHandle_t xTimerWatchdog;

// 定时器回调函数（在定时器服务任务中执行）
void vHeartbeatCallback(TimerHandle_t xTimer) {
    // LED 心跳闪烁
    HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
}

void vWatchdogCallback(TimerHandle_t xTimer) {
    // 看门狗超时处理
    Log_Write("Watchdog timeout!");
    NVIC_SystemReset();
}

void Timers_Init(void) {
    // 创建周期定时器（200ms周期）
    xTimerHeartbeat = xTimerCreate(
        "Heartbeat",                 // 名称
        pdMS_TO_TICKS(200),          // 周期
        pdTRUE,                      // 自动重载（周期）
        (void *)0,                   // 定时器ID
        vHeartbeatCallback           // 回调函数
    );

    // 创建单次定时器（5秒超时）
    xTimerWatchdog = xTimerCreate(
        "Watchdog",
        pdMS_TO_TICKS(5000),
        pdFALSE,                     // 单次
        (void *)1,
        vWatchdogCallback
    );

    // 启动定时器
    xTimerStart(xTimerHeartbeat, 0);
    xTimerStart(xTimerWatchdog, 0);
}

// 喂狗（重置看门狗定时器）
void FeedWatchdog(void) {
    xTimerReset(xTimerWatchdog, pdMS_TO_TICKS(10));
}
```

> ⚠️ **注意**：定时器回调函数在定时器服务任务中运行，**不要**在回调中调用阻塞API（如 `vTaskDelay`）。回调应尽量短小。

---

## 6. 内存管理

### 6.1 FreeRTOS 堆管理方案

| 方案 | 特点 | 适用场景 |
|---|---|---|
| heap_1 | 只分配不释放 | 确定性系统 |
| heap_2 | 简单合并，不分碎片 | 旧系统兼容 |
| heap_3 | 封装标准 malloc/free | 已有标准库 |
| heap_4 | 合并空闲块 | **推荐**（通用） |
| heap_5 | 多个非连续内存区域 | 复杂内存布局 |

### 6.2 heap_4 配置

```c
// FreeRTOSConfig.h
#define configTOTAL_HEAP_SIZE         ((size_t)(64 * 1024))  // 64KB
#define configUSE_MALLOC_FAILED_HOOK  1

// 堆分配失败钩子
void vApplicationMallocFailedHook(void) {
    Log_Write("ERROR: Malloc failed!");
    taskDISABLE_INTERRUPTS();
    while (1);
}
```

### 6.3 栈溢出检测

```c
// FreeRTOSConfig.h
#define configCHECK_FOR_STACK_OVERFLOW  2

// 栈溢出钩子
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    (void)xTask;
    Log_Write("ERROR: Stack overflow in task: %s", pcTaskName);
    while (1);
}
```

### 6.4 堆使用统计

```c
// 获取空闲堆大小
size_t freeHeap = xPortGetFreeHeapSize();
Log_Write("Free heap: %d bytes", freeHeap);

// 获取历史最小空闲堆大小（用于评估堆是否够用）
size_t minEverFree = xPortGetMinimumEverFreeHeapSize();
Log_Write("Min ever free heap: %d bytes", minEverFree);

// 获取任务栈剩余空间（需要启用 trace）
UBaseType_t stackHighWater = uxTaskGetStackHighWaterMark(NULL);
Log_Write("Stack remaining: %d words", stackHighWater);
```

---

## 7. 最佳实践

### 7.1 任务设计原则

1. **单一职责**：每个任务只做一件事
2. **避免忙等待**：使用 `vTaskDelay` 或阻塞API而非 `while(1)` 空转
3. **合理优先级**：关键任务高优先级，非关键任务低优先级
4. **栈大小评估**：使用 `uxTaskGetStackHighWaterMark` 监控实际使用量

### 7.2 FreeRTOSConfig 关键配置

```c
// FreeRTOSConfig.h - 生产环境推荐配置
#define configUSE_PREEMPTION            1       // 抢占式调度
#define configUSE_PORT_OPTIMISED_TASK_SELECTION 1
#define configUSE_TICKLESS_IDLE         1       // 低功耗tickless
#define configCPU_CLOCK_HZ              (72000000ULL)
#define configTICK_RATE_HZ              ((TickType_t)1000)  // 1kHz tick
#define configMAX_PRIORITIES            (7)     // 7个优先级
#define configMINIMAL_STACK_SIZE        ((uint16_t)128)     // 最小栈128字
#define configTOTAL_HEAP_SIZE           ((size_t)(32 * 1024))
#define configMAX_TASK_NAME_LEN         (16)
#define configUSE_MUTEXES               1
#define configUSE_RECURSIVE_MUTEXES     1
#define configUSE_COUNTING_SEMAPHORES   1
#define configUSE_QUEUE_SETS            1
#define configUSE_TIME_SLICING          1
#define configUSE_NEWLIB_REENTRANT      1       // newlib 线程安全
#define configENABLE_BACKWARD_COMPATIBILITY 0
#define configSUPPORT_STATIC_ALLOCATION 1       // 静态分配支持
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configCHECK_FOR_STACK_OVERFLOW  2
#define configUSE_STATS_FORMATTING_FUNCTIONS 2
#define configUSE_TRACE_FACILITY        1
#define configGENERATE_RUN_TIME_STATS   1
```

### 7.3 中断优先级注意事项（ARM Cortex-M）

```c
// ⚠️ 关键：FreeRTOS 中断优先级配置
// Cortex-M 使用数值越大优先级越低

// configMAX_SYSCALL_INTERRUPT_PRIORITY 以下的ISR可以调用FreeRTOS API
// 在 FreeRTOSConfig.h:
#define configKERNEL_INTERRUPT_PRIORITY         255     // 最低优先级
#define configMAX_SYSCALL_INTERRUPT_PRIORITY    191     // 可调用API的最高优先级

// 正确：低于阈值的ISR可以调用API
void LowPriorityISR(void) {
    BaseType_t xWoken = pdFALSE;
    xSemaphoreGiveFromISR(xSemaphore, &xWoken);  // ✅
    portYIELD_FROM_ISR(xWoken);
}

// 错误：高优先级ISR不能调用FreeRTOS API
void HighPriorityISR(void) {
    // xSemaphoreGiveFromISR(...);  // ❌ 会导致崩溃
    // 高优先级ISR只能设置标志位，由低优先级处理
}
```

### 7.4 优先级反转与解决

```c
// 场景：低优先级任务持有互斥量，高优先级任务等待
// 解决：使用 Mutex（支持优先级继承）而非 Binary Semaphore

// ✅ 正确：使用 Mutex 保护共享资源
SemaphoreHandle_t xMutex = xSemaphoreCreateMutex();
// Mutex 会自动提升持有者的优先级

// ❌ 错误：使用 Binary Semaphore 会导致优先级反转
// SemaphoreHandle_t xSem = xSemaphoreCreateBinary();
```

### 7.5 系统tickless模式

```c
// 启用低功耗模式
// FreeRTOSConfig.h:
#define configUSE_TICKLESS_IDLE 1

// 自定义低功耗回调
void vPortSuppressTicksAndSleep(TickType_t xExpectedIdleTime) {
    // 1. 停止SysTick
    SysTick->CTRL &= ~SysTick_CTRL_ENABLE_Msk;

    // 2. 配置低功耗定时器
    LPTIM_SetTimeout(xExpectedIdleTime);

    // 3. 进入STOP模式
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);

    // 4. 唤醒后恢复时钟
    SystemClock_Config();

    // 5. 通知FreeRTOS实际睡眠时间
    TickType_t actualTicks = LPTIM_GetElapsedTicks();
    vTaskStepTick(actualTicks);
}
```

---

## 相关页面

- [[嵌入式Linux开发]] - 嵌入式Linux系统构建与设备树
- [[STM32开发指南]] - STM32 HAL库与硬件外设
- [[树莓派开发指南]] - 树莓派外设与Python开发
- [[单片机通信协议]] - UART/SPI/I2C/CAN 通信协议详解

---

## 参考资源

- [FreeRTOS 官方文档](https://www.freertos.org/Documentation)
- [Mastering the FreeRTOS Kernel](https://www.freertos.org/Documentation/RTOS_book.html)
- [FreeRTOS GitHub](https://github.com/FreeRTOS/FreeRTOS)
- [RT-Thread 文档中心](https://www.rt-thread.org/document/site/)
- [Zephyr Project 文档](https://docs.zephyrproject.org/)

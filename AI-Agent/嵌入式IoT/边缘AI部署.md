---
title: "边缘AI部署"
aliases:
  - Edge AI Deployment
  - 边缘AI
  - TinyML
  - 嵌入式AI
  - Edge Inference
tags:
  - edge-ai
  - tflite
  - onnx
  - tinyml
  - quantization
  - inference
  - embedded-ai
type: reference
status: published
created: 2026-06-28
updated: 2026-06-28
source: "原创整理 + TensorFlow Lite / ONNX Runtime 官方文档"
difficulty: advanced
project: "嵌入式IoT知识库"
---

# 边缘AI部署

> 本页面涵盖在嵌入式设备和边缘端部署 AI 模型的完整流程：TensorFlow Lite、ONNX Runtime、模型量化与剪枝、TinyML、硬件加速方案。

---

## 目录

- [1. 边缘AI 概述](#1-边缘ai-概述)
- [2. TensorFlow Lite 部署](#2-tensorflow-lite-部署)
- [3. ONNX Runtime 部署](#3-onnx-runtime-部署)
- [4. 模型量化与优化](#4-模型量化与优化)
- [5. TinyML — 超低功耗 AI](#5-tinyml--超低功耗-ai)
- [6. 硬件加速方案](#6-硬件加速方案)
- [7. 最佳实践](#7-最佳实践)
- [相关页面](#相关页面)

---

## 1. 边缘AI 概述

### 1.1 为什么需要边缘 AI

```
传统云计算 AI                    边缘 AI
┌──────┐    数据上传     ┌──────┐     ┌──────────┐
│ 设备  │ ────────────► │ 云端  │     │ 设备      │
│       │               │ GPU   │     │ NPU/TPU  │
│       │ ◄──────────── │ 推理  │     │ 本地推理  │
└──────┘    结果返回     └──────┘     └──────────┘

延迟: 100-500ms                  延迟: 1-50ms
带宽: 高                          带宽: 低
隐私: 数据离开设备                 隐私: 数据本地处理
离线: 不可用                      离线: 可用
```

### 1.2 硬件平台对比

| 平台 | 算力 (TOPS) | 功耗 | 价格 | 适用场景 |
|------|------------|------|------|----------|
| Raspberry Pi 5 | ~0.1 | 5-8W | $80 | 轻量推理 |
| Jetson Nano | 0.5 | 5-10W | $99 | 初级视觉 |
| Jetson Orin Nano | 40 | 7-15W | $249 | 中级视觉 |
| Google Coral TPU | 4 | 2W | $70 | TFLite 加速 |
| Rockchip RK3588 | 6 | 5-10W | $150 | NPU 推理 |
| ESP32-S3 | ~0.01 | 0.5W | $5 | TinyML |
| STM32H7 | ~0.001 | 0.3W | $10 | 关键词检测 |

---

## 2. TensorFlow Lite 部署

### 2.1 模型转换流程

```
训练 (TensorFlow/Keras)
    ↓
导出 SavedModel / .h5
    ↓
转换为 TFLite 模型
    ↓
量化/优化
    ↓
部署到边缘设备
```

### 2.2 训练并导出模型

```python
import tensorflow as tf
import numpy as np

# 训练一个简单的图像分类模型（CIFAR-10 子集）
def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(32, 32, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

# 加载数据并训练
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = create_model()
model.fit(x_train, y_train, epochs=10, validation_data=(x_test, y_test))

# 保存模型
model.save("cifar10_model.keras")
```

### 2.3 转换为 TFLite

```python
def convert_to_tflite(model_path, output_path, quantize=False):
    """将 Keras 模型转换为 TFLite 格式"""
    converter = tf.lite.TFLiteConverter.from_keras_model(model_path)

    if quantize:
        # === 动态范围量化 (int8 权重, float 激活) ===
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()

    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    import os
    size = os.path.getsize(output_path) / 1024
    print(f"Model saved: {output_path} ({size:.1f} KB)")

# 不量化版本
convert_to_tflite(model, "cifar10_float.tflite", quantize=False)

# 动态量化版本
convert_to_tflite(model, "cifar10_dynamic.tflite", quantize=True)
```

### 2.4 全整数量化（INT8）

```python
def convert_to_int8(model, representative_data, output_path):
    """全 INT8 量化 — 适用于 Coral TPU / NPU"""

    def representative_dataset():
        for sample in representative_data[:100]:
            yield [np.expand_dims(sample, axis=0).astype(np.float32)]

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # 启用全整数量化
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type  = tf.int8   # 输入类型
    converter.inference_output_type = tf.int8   # 输出类型

    tflite_model = converter.convert()

    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    import os
    print(f"INT8 model: {output_path} ({os.path.getsize(output_path)/1024:.1f} KB)")

# 使用校准数据集进行量化
convert_to_int8(model, x_train, "cifar10_int8.tflite")
```

### 2.5 在 Python 上运行 TFLite 推理

```python
import time
import numpy as np
import tflite_runtime.interpreter as tflite

class TFLiteClassifier:
    def __init__(self, model_path):
        # 加载模型
        self.interpreter = tflite.Interpreter(
            model_path=model_path,
            num_threads=4
        )
        self.interpreter.allocate_tensors()

        # 获取输入/输出信息
        self.input_details  = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.input_shape  = self.input_details[0]['shape']
        self.input_dtype  = self.input_details[0]['dtype']
        self.output_shape = self.output_details[0]['shape']

        print(f"Input:  shape={self.input_shape}, dtype={self.input_dtype}")
        print(f"Output: shape={self.output_shape}")

    def predict(self, input_data):
        """执行推理"""
        # 预处理输入
        if self.input_dtype == np.int8:
            input_scale  = self.input_details[0]['quantization'][0]
            input_zero   = self.input_details[0]['quantization'][1]
            input_data = (input_data / input_scale + input_zero).astype(np.int8)

        # 设置输入张量
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        # 推理
        start = time.perf_counter()
        self.interpreter.invoke()
        elapsed = (time.perf_counter() - start) * 1000

        # 获取输出
        output = self.interpreter.get_tensor(self.output_details[0]['index'])

        # 反量化输出
        if self.output_details[0]['dtype'] == np.int8:
            output_scale = self.output_details[0]['quantization'][0]
            output_zero  = self.output_details[0]['quantization'][1]
            output = (output.astype(np.float32) - output_zero) * output_scale

        return output, elapsed

# 使用示例
classifier = TFLiteClassifier("cifar10_int8.tflite")

labels = ['airplane', 'auto', 'bird', 'cat', 'deer',
          'dog', 'frog', 'horse', 'ship', 'truck']

# 单张图片推理
image = np.random.rand(1, 32, 32, 3).astype(np.float32)
output, latency = classifier.predict(image)
predicted = labels[np.argmax(output)]

print(f"Prediction: {predicted} (confidence: {np.max(output):.4f})")
print(f"Latency: {latency:.2f} ms")
```

### 2.6 C++ TFLite 部署（嵌入式 Linux）

```cpp
// tflite_inference.cpp — C++ TFLite 推理
#include <tensorflow/lite/interpreter.h>
#include <tensorflow/lite/kernels/register.h>
#include <tensorflow/lite/model.h>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>

class TFLiteModel {
public:
    bool load(const std::string& model_path) {
        // 加载模型
        model_ = tflite::FlatBufferModel::BuildFromFile(model_path.c_str());
        if (!model_) {
            std::cerr << "Failed to load model: " << model_path << std::endl;
            return false;
        }
        model_->error_reporter();

        // 创建解释器
        tflite::ops::builtin::BuiltinOpResolver resolver;
        tflite::InterpreterBuilder builder(*model_, resolver);
        builder(&interpreter_);
        if (!interpreter_) {
            std::cerr << "Failed to create interpreter" << std::endl;
            return false;
        }

        // 配置线程数
        interpreter_->SetNumThreads(4);

        // 分配张量
        if (interpreter_->AllocateTensors() != kTfLiteOk) {
            std::cerr << "Failed to allocate tensors" << std::endl;
            return false;
        }

        // 获取输入/输出信息
        input_  = interpreter_->typed_input_tensor<float>(0);
        output_ = interpreter_->typed_output_tensor<float>(0);

        auto in_shape = interpreter_->tensor(interpreter_->inputs()[0])->dims;
        std::cout << "Input shape: ";
        for (int i = 0; i < in_shape->size; i++)
            std::cout << in_shape->data[i] << " ";
        std::cout << std::endl;

        return true;
    }

    int predict(const cv::Mat& image) {
        // 预处理：resize + normalize
        cv::Mat resized;
        cv::resize(image, resized, cv::Size(32, 32));
        cv::cvtColor(resized, resized, cv::COLOR_BGR2RGB);
        resized.convertTo(resized, CV_32F, 1.0 / 255.0);

        // 复制到输入张量
        float* input = input_;
        for (int c = 0; c < 3; c++)
            for (int h = 0; h < 32; h++)
                for (int w = 0; w < 32; w++)
                    input[c * 32 * 32 + h * 32 + w] =
                        resized.at<cv::Vec3f>(h, w)[c];

        // 推理
        auto start = std::chrono::high_resolution_clock::now();
        interpreter_->Invoke();
        auto end = std::chrono::high_resolution_clock::now();
        auto ms = std::chrono::duration_cast<
            std::chrono::microseconds>(end - start).count() / 1000.0;

        // 获取预测结果
        int best = 0;
        float max_val = output_[0];
        for (int i = 1; i < 10; i++) {
            if (output_[i] > max_val) {
                max_val = output_[i];
                best = i;
            }
        }

        std::cout << "Predict: " << best
                  << " (" << max_val << ")"
                  << " [" << ms << " ms]" << std::endl;

        return best;
    }

private:
    std::unique_ptr<tflite::FlatBufferModel> model_;
    std::unique_ptr<tflite::Interpreter> interpreter_;
    float* input_  = nullptr;
    float* output_ = nullptr;
};

int main(int argc, char* argv[]) {
    TFLiteModel model;
    if (!model.load("cifar10_float.tflite")) return -1;

    cv::Mat image = cv::imread(argv[1]);
    if (image.empty()) {
        std::cerr << "Failed to load image: " << argv[1] << std::endl;
        return -1;
    }

    model.predict(image);
    return 0;
}
```

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(tflite_inference)

find_package(OpenCV REQUIRED)

# TFLite 库路径（预编译）
set(TFLITE_LIB_DIR "/usr/local/lib/tflite")

add_executable(tflite_inference tflite_inference.cpp)
target_link_libraries(tflite_inference
    ${OpenCV_LIBS}
    ${TFLITE_LIB_DIR}/libtensorflow-lite.a
    -lpthread -ldl
)
```

---

## 3. ONNX Runtime 部署

### 3.1 导出 ONNX 模型

```python
import torch
import torch.nn as nn

# PyTorch 模型 → ONNX
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

model = SimpleCNN()
model.eval()

# 导出 ONNX
dummy_input = torch.randn(1, 3, 32, 32)

torch.onnx.export(
    model,
    dummy_input,
    "cifar10_model.onnx",
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={
        'input':  {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

print("ONNX model exported successfully")
```

### 3.2 ONNX Runtime Python 推理

```python
import onnxruntime as ort
import numpy as np
import time

# 创建推理会话（选择执行提供者）
providers = [
    # 'CUDAExecutionProvider',     # GPU（NVIDIA）
    # 'TensorrtExecutionProvider',  # TensorRT 加速
    # 'RockchipExecutionProvider',  # RK NPU
    'CPUExecutionProvider',         # CPU 回退
]

session = ort.InferenceSession(
    "cifar10_model.onnx",
    providers=providers
)

input_name  = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

print(f"Providers: {session.get_providers()}")
print(f"Input:  {session.get_inputs()[0].shape}")
print(f"Output: {session.get_outputs()[0].shape}")

# 推理
input_data = np.random.randn(1, 3, 32, 32).astype(np.float32)

# 性能基准测试
N = 100
start = time.perf_counter()
for _ in range(N):
    output = session.run([output_name], {input_name: input_data})
elapsed = time.perf_counter() - start

print(f"Average latency: {elapsed/N*1000:.2f} ms ({N} runs)")
print(f"Throughput: {N/elapsed:.1f} FPS")

# 输出 Softmax 概率
logits = output[0][0]
probs = np.exp(logits) / np.sum(np.exp(logits))
print(f"Top-3: {np.argsort(probs)[-3:][::-1]}")
```

### 3.3 ONNX Runtime C++ 部署

```cpp
// onnx_inference.cpp
#include <onnxruntime_cxx_api.h>
#include <iostream>
#include <vector>
#include <chrono>

int main() {
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "EdgeAI");
    Ort::SessionOptions session_opts;
    session_opts.SetIntraOpNumThreads(4);
    session_opts.SetGraphOptimizationLevel(
        GraphOptimizationLevel::ORT_ENABLE_EXTENDED
    );

    // 加载模型
    Ort::Session session(env, "cifar10_model.onnx", session_opts);

    // 获取输入/输出信息
    Ort::AllocatorWithDefaultOptions allocator;
    auto input_name = session.GetInputNameAllocated(0, allocator);
    auto output_name = session.GetOutputNameAllocated(0, allocator);

    auto input_shape = session.GetInputTypeInfo(0)
                          .GetTensorTypeAndShapeInfo().GetShape();

    std::cout << "Input: " << input_name.get() << " shape: ";
    for (auto d : input_shape) std::cout << d << " ";
    std::cout << std::endl;

    // 准备输入数据
    std::vector<float> input_data(3 * 32 * 32, 0.5f);
    std::vector<int64_t> input_dims = {1, 3, 32, 32};

    auto memory_info = Ort::MemoryInfo::CreateCpu(
        OrtArenaAllocator, OrtMemTypeDefault);

    Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
        memory_info, input_data.data(), input_data.size(),
        input_dims.data(), input_dims.size()
    );

    // 推理
    const char* input_names[] = {input_name.get()};
    const char* output_names[] = {output_name.get()};

    auto start = std::chrono::high_resolution_clock::now();
    auto outputs = session.Run(
        Ort::RunOptions{nullptr},
        input_names, &input_tensor, 1,
        output_names, 1
    );
    auto end = std::chrono::high_resolution_clock::now();

    auto ms = std::chrono::duration_cast<
        std::chrono::microseconds>(end - start).count() / 1000.0;

    // 输出结果
    float* output = outputs[0].GetTensorMutableData<float>();
    int best = 0;
    for (int i = 1; i < 10; i++) {
        if (output[i] > output[best]) best = i;
    }

    std::cout << "Predict: " << best << " [" << ms << " ms]" << std::endl;
    return 0;
}
```

---

## 4. 模型量化与优化

### 4.1 量化方法对比

| 方法 | 精度损失 | 模型大小 | 推理速度 | 硬件要求 |
|------|----------|----------|----------|----------|
| FP32 (原始) | 基准 | 1x | 基准 | 通用 |
| FP16 | ~0.1% | 0.5x | ~1.5x | GPU/NPU |
| 动态量化 (权重量化) | ~1% | 0.25x | ~2x | CPU |
| INT8 静态量化 | ~1-2% | 0.25x | ~3x | TPU/NPU |
| INT4 量化 | ~3-5% | 0.125x | ~4x | 特定 NPU |
| 混合精度 | ~0.5% | 0.5x | ~2x | 现代 GPU |

### 4.2 PyTorch 训练后量化

```python
import torch
import torch.quantization as quant

# 训练后动态量化（适合 LSTM / Transformer）
model_dynamic = quant.quantize_dynamic(
    model,
    {nn.Linear, nn.LSTM},
    dtype=torch.qint8
)
torch.save(model_dynamic.state_dict(), "model_dynamic.pt")

# 静态量化（适合 CNN）— 需要校准数据
model.qconfig = quant.get_default_qconfig('fbgemm')  # x86 CPU
# model.qconfig = quant.get_default_qconfig('qnnpack')  # ARM CPU

model_prepared = quant.prepare(model)
# 用校准数据运行前向传播
for data in calibration_loader:
    model_prepared(data)
model_quantized = quant.convert(model_prepared)

torch.save(model_quantized.state_dict(), "model_int8.pt")

# 比较模型大小
original_size = sum(p.nelement() * p.element_size() for p in model.parameters())
quantized_size = sum(p.nelement() * p.element_size() for p in model_quantized.parameters())
print(f"Original: {original_size/1024:.1f} KB → Quantized: {quantized_size/1024:.1f} KB")
```

### 4.3 模型剪枝

```python
import torch.nn.utils.prune as prune

# 结构化剪枝 — 移除整个通道
def structured_prune(model, amount=0.3):
    """对卷积层进行 L1 结构化剪枝"""
    for name, module in model.named_modules():
        if isinstance(module, nn.Conv2d):
            prune.ln_structured(module, name='weight', amount=amount, n=2, dim=0)
            prune.remove(module, 'weight')
            sparsity = 100. * float(torch.sum(module.weight == 0)) / module.weight.nelement()
            print(f"Layer {name}: {sparsity:.1f}% pruned")
    return model

# 非结构化剪枝
def unstructured_prune(model, amount=0.5):
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            prune.l1_unstructured(module, name='weight', amount=amount)
    return model

# 使用示例
pruned_model = structured_prune(model, amount=0.3)

# 剪枝后微调（恢复精度）
# optimizer = torch.optim.Adam(pruned_model.parameters(), lr=1e-4)
# train_one_epoch(pruned_model, train_loader, optimizer)
```

### 4.4 知识蒸馏

```python
import torch.nn.functional as F

def knowledge_distillation(teacher, student, train_loader, epochs=10):
    """知识蒸馏：大模型(Teacher) → 小模型(Student)"""
    optimizer = torch.optim.Adam(student.parameters(), lr=1e-3)

    teacher.eval()
    student.train()

    T = 4.0       # 温度参数
    alpha = 0.7   # 蒸馏损失权重

    for epoch in range(epochs):
        for images, labels in train_loader:
            # Teacher 软标签
            with torch.no_grad():
                teacher_logits = teacher(images)
                teacher_probs = F.softmax(teacher_logits / T, dim=1)

            # Student 预测
            student_logits = student(images)
            student_log_probs = F.log_softmax(student_logits / T, dim=1)

            # 组合损失：KL 散度 + 硬标签
            distill_loss = F.kl_div(
                student_log_probs, teacher_probs,
                reduction='batchmean'
            ) * (T ** 2)

            hard_loss = F.cross_entropy(student_logits, labels)
            loss = alpha * distill_loss + (1 - alpha) * hard_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch+1}: loss={loss.item():.4f}")

# teacher = ResNet50()  # 大模型
# student = SimpleCNN()  # 小模型
# knowledge_distillation(teacher, student, train_loader)
```

---

## 5. TinyML — 超低功耗 AI

### 5.1 TinyML 适用场景

```
关键词检测 (KWS)     — 唤醒词 "Hey Siri"
手势识别              — 加速度传感器模式匹配
异常检测              — 电机振动监测
人员检测              — 低分辨率摄像头
时间序列预测          — 预测性维护
```

### 5.2 TensorFlow Lite Micro (ESP32 / STM32)

```cpp
// esp32_tinyml_kws.ino — ESP32 关键词检测
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

// 嵌入模型（编译进固件）
#include "micro_speech_model_data.h"  // 量化后的 KWS 模型

// 推理所需内存
constexpr int kTensorArenaSize = 30 * 1024;  // 30KB
uint8_t tensor_arena[kTensorArenaSize];

tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* model_input  = nullptr;
TfLiteTensor* model_output = nullptr;

void setup() {
    Serial.begin(115200);

    // 加载模型
    const tflite::Model* model =
        tflite::GetModel(g_micro_speech_model_data);

    // 注册需要的算子
    static tflite::MicroMutableOpResolver<5> resolver;
    resolver.AddFullyConnected();
    resolver.AddReshape();
    resolver.AddSoftmax();
    resolver.AddConv2D();
    resolver.AddMaxPool2D();

    // 创建解释器
    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize
    );
    interpreter = &static_interpreter;

    // 分配张量
    interpreter->AllocateTensors();

    model_input  = interpreter->input(0);
    model_output = interpreter->output(0);

    Serial.println("TinyML KWS Ready");
    Serial.printf("Arena used: %d bytes\n",
                  interpreter->arena_used_bytes());
}

void loop() {
    // 从麦克风采集音频（16kHz, 1秒）
    int8_t* audio_data = model_input->data.int8;
    capture_audio(audio_data, model_input->bytes);

    // 推理
    unsigned long start = micros();
    TfLiteStatus invoke_status = interpreter->Invoke();
    unsigned long elapsed = micros() - start;

    if (invoke_status != kTfLiteOk) {
        Serial.println("Invoke failed!");
        return;
    }

    // 解析输出
    const char* labels[] = {"silence", "unknown", "yes", "no"};
    int best = 0;
    int8_t max_val = model_output->data.int8[0];
    for (int i = 1; i < 4; i++) {
        if (model_output->data.int8[i] > max_val) {
            max_val = model_output->data.int8[i];
            best = i;
        }
    }

    if (strcmp(labels[best], "silence") != 0) {
        Serial.printf("Detected: %s (%d) [%.1f ms]\n",
                      labels[best], max_val, elapsed / 1000.0);
    }

    delay(100);
}
```

### 5.3 Edge Impulse 工作流

```bash
# Edge Impulse CLI — 边缘 AI 全流程工具
# 安装
npm install -g edge-impulse-cli

# 1. 数据采集（通过手机/设备）
edge-impulse-data-forwarder --frequency 100
# 将传感器数据通过串口发送到 Edge Impulse 云端

# 2. 项目配置（Web 界面）
# https://studio.edgeimpulse.com
# 创建项目 → 上传数据 → 设计模型 → 训练 → 测试

# 3. 导出模型（C++ Library）
edge-impulse-runner --download modelfile.eim

# 4. 本地部署
edge-impulse-runner --model modelfile.eim

# 5. 部署到 STM32
# 导出为 C++ SDK，集成到 Keil/CubeIDE 项目
```

---

## 6. 硬件加速方案

### 6.1 Google Coral Edge TPU

```python
# Coral Edge TPU 推理（需要 INT8 量化的 TFLite 模型）
from pycoral.adapters import common
from pycoral.adapters import classify
from pycoral.utils.edgetpu import make_interpreter
import time

# 加载 Edge TPU 模型
interpreter = make_interpreter("mobilenet_v2_int8_edgetpu.tflite")
interpreter.allocate_tensors()

input_detail  = interpreter.get_input_details()[0]
output_detail = interpreter.get_output_details()[0]

print(f"Input:  {input_detail['shape']} ({input_detail['dtype']})")
print(f"Output: {output_detail['shape']}")

# 推理
import numpy as np
input_data = np.random.randint(
    -128, 127, input_detail['shape'], dtype=np.int8
)
common.set_input(interpreter, input_data)

# 性能基准
for _ in range(10):  # 预热
    interpreter.invoke()

N = 100
start = time.perf_counter()
for _ in range(N):
    interpreter.invoke()
elapsed = time.perf_counter() - start

results = classify.get_classes(interpreter, top_k=3)
print(f"Top results: {results}")
print(f"Average latency: {elapsed/N*1000:.2f} ms ({N/elapsed:.0f} FPS)")
```

### 6.2 NVIDIA Jetson (TensorRT)

```python
# 使用 TensorRT 加速（Jetson 平台）
import tensorrt as trt
import pycuda.driver as cuda
import numpy as np

# 模型转换：ONNX → TensorRT Engine
def build_engine(onnx_path, engine_path, fp16=True):
    """构建 TensorRT 引擎"""
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

    with trt.Builder(TRT_LOGGER) as builder:
        builder.max_batch_size = 1
        builder.max_workspace_size = 1 << 30  # 1GB

        flag = 0
        if fp16 and builder.platform_has_fast_fp16:
            flag = 1 << int(trt.BuilderFlag.FP16)
            print("FP16 mode enabled")

        with builder.create_network(flag) as network:
            parser = trt.OnnxParser(network, TRT_LOGGER)

            with open(onnx_path, 'rb') as f:
                if not parser.parse(f.read()):
                    for i in range(parser.num_errors):
                        print(parser.get_error(i))
                    return None

            engine = builder.build_cuda_engine(network)

            with open(engine_path, 'wb') as f:
                f.write(engine.serialize())

            return engine

# 构建引擎
engine = build_engine("model.onnx", "model_fp16.engine", fp16=True)
print("TensorRT engine built!")
```

### 6.3 Rockchip RKNN (RK3588 NPU)

```python
# RKNN Toolkit Lite — 在 RK3588 上使用 NPU
from rknnlite.api import RKNNLite

# 加载 RKNN 模型（从 ONNX/PyTorch 转换）
rknn = RKNNLite()

ret = rknn.load_rknn('yolov5s_rk3588.rknn')
if ret != 0:
    print(f"Load model failed: {ret}")
    exit()

# 初始化运行时（NPU 核心 0）
ret = rknn.init_runtime(core_mask=RKNNLite.NPU_CORE_0_1_2)
if ret != 0:
    print(f"Init runtime failed: {ret}")
    exit()

# 获取输入/输出信息
rknn.get_input_details()
rknn.get_output_details()

# 推理
import numpy as np
from PIL import Image

img = Image.open('test.jpg').resize((640, 640))
input_data = np.expand_dims(np.array(img), axis=0)

outputs = rknn.inference(inputs=[input_data])

print(f"Output shape: {outputs[0].shape}")

# 释放
rknn.release()
```

```bash
# 在 PC 上将 ONNX 转换为 RKNN 模型
# rknn_convert.py
from rknn.api import RKNN

rknn = RKNN()

# 配置
rknn.config(
    mean_values=[[0, 0, 0]],
    std_values=[[255, 255, 255]],
    target_platform='rk3588',
    optimization_level=3
)

# 加载 ONNX 模型
ret = rknn.load_onnx(model='yolov5s.onnx')

# 构建 RKNN 模型
ret = rknn.build(do_quantization=False)

# 导出
ret = rknn.export_rknn('yolov5s_rk3588.rknn')

rknn.release()
print("RKNN model exported!")
```

---

## 7. 最佳实践

### 7.1 模型选择决策树

```
部署 AI 模型决策:

设备 RAM < 512KB ?
  ├── 是 → TinyML (TFLite Micro, INT8)
  │       适用: 关键词检测, 简单分类
  │
  └── 否 → 设备有专用 AI 加速器 (NPU/TPU)?
      ├── 是 → 使用厂商 SDK (RKNN/Coral/TensorRT)
      │       模型: INT8 量化
      │
      └── 否 → 设备有 GPU?
          ├── 是 → ONNX Runtime + CUDA / TFLite GPU Delegate
          │       模型: FP16
          │
          └── 否 → TFLite / ONNX Runtime (CPU)
                  模型: INT8 或 FP32 (取决于 CPU 性能)
```

### 7.2 性能优化清单

| 优化项 | 效果 | 复杂度 |
|--------|------|--------|
| INT8 量化 | 3-4x 加速 | 中 |
| 模型剪枝 | 2x 减小 | 中 |
| 知识蒸馏 | 精度恢复 | 高 |
| 算子融合 | 1.5x 加速 | 低（自动） |
| 硬件加速器 | 10-100x 加速 | 中 |
| 输入分辨率降低 | 平方级加速 | 低 |
| 批量推理 | 吞吐量提升 | 中 |
| 内存复用 | 减少 RAM 占用 | 低 |

### 7.3 端到端部署流程

```bash
#!/bin/bash
# deploy_edge_ai.sh — 边缘 AI 部署脚本

# 1. 环境准备
pip install tflite-runtime onnxruntime

# 2. 模型转换与量化
python3 convert_model.py \
    --input model.h5 \
    --output model_int8.tflite \
    --quantize int8 \
    --calibrate calibration_data/

# 3. 模型验证
python3 validate_model.py model_int8.tflite --test-data test_set/

# 4. 部署到设备
scp model_int8.tflite device@192.168.1.50:/opt/models/

# 5. 启动推理服务
ssh device@192.168.1.50 'cd /opt/ai && python3 inference_server.py &'

# 6. 性能监控
ssh device@192.168.1.50 'python3 benchmark.py --model model_int8.tflite --runs 1000'
```

### 7.4 持续学习与模型更新

```python
# 边缘设备上的在线学习/增量学习
class EdgeContinuousLearning:
    """边缘设备增量学习框架"""

    def __init__(self, base_model_path, buffer_size=100):
        self.base_model_path = base_model_path
        self.data_buffer = []
        self.buffer_size = buffer_size
        self.confidence_threshold = 0.85

    def inference_with_feedback(self, input_data, true_label=None):
        """推理 + 可选的反馈学习"""
        # 推理
        prediction, confidence = self.predict(input_data)

        # 低置信度或有人工标签 → 缓存数据
        if confidence < self.confidence_threshold or true_label is not None:
            label = true_label if true_label else prediction
            self.data_buffer.append((input_data, label))

            # 缓冲区满 → 触发增量训练
            if len(self.data_buffer) >= self.buffer_size:
                self.incremental_train()
                self.data_buffer.clear()

        return prediction, confidence

    def incremental_train(self):
        """增量训练（轻量级微调）"""
        # 使用缓存的样本微调模型
        # 在边缘设备上仅做少量迭代
        print(f"Incremental training with {len(self.data_buffer)} samples")
        # ...
```

---

## 相关页面

- [[嵌入式Linux开发]] — 边缘 AI 设备的系统平台
- [[单片机开发指南]] — TinyML 在单片机上的实现
- [[MQTT协议实战]] — 推理结果的 MQTT 上报
- [[IoT平台搭建]] — 模型管理与 OTA 固件升级

---

> **最后更新**：2026-06-28 | **维护者**：嵌入式IoT知识库

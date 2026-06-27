---
title: LLM微调指南
aliases:
  - Fine-tuning
  - LoRA微调
  - QLoRA
  - 模型训练
tags:
  - fine-tuning
  - LoRA
  - QLoRA
  - LLM
  - 训练
type: guide
status: active
created: 2026-06-27
updated: 2026-06-27
source: internal
difficulty: advanced
project: AI-Agent
---

# LLM微调指南

> 模型微调是在预训练模型基础上，使用特定领域数据进行二次训练，使模型适应特定任务。

## 1. 何时需要微调

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 特定格式输出 | Prompt Engineering | 成本低，效果快 |
| 领域知识补充 | RAG | 无需训练，知识可更新 |
| 特定风格/语气 | 微调 | 模型需要学习新行为模式 |
| 复杂任务适配 | 微调 | Prompt难以覆盖所有情况 |
| 大量高质量数据 | 微调 | 充分利用数据价值 |

## 2. 数据准备

### 2.1 数据格式

```python
# OpenAI微调格式
training_data = [
    {
        "messages": [
            {"role": "system", "content": "你是一个专业的法律顾问助手。"},
            {"role": "user", "content": "什么是合同违约？"},
            {"role": "assistant", "content": "合同违约是指合同当事人一方不履行合同义务或履行合同义务不符合约定的行为。根据《民法典》相关规定，违约方应承担继续履行、采取补救措施或赔偿损失等违约责任。"}
        ]
    },
    # 更多样本...
]

# HuggingFace格式 (Alpaca格式)
alpaca_data = [
    {
        "instruction": "解释什么是机器学习",
        "input": "",
        "output": "机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习和改进，而无需被明确编程。通过算法分析数据模式，机器学习模型可以做出预测或决策。"
    }
]
```

### 2.2 数据清洗与验证

```python
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class DataQualityConfig:
    min_input_length: int = 10
    max_input_length: int = 4096
    min_output_length: int = 20
    max_output_length: int = 4096
    max_turns: int = 10
    remove_duplicates: bool = True
    check_encoding: bool = True

class DataValidator:
    """训练数据质量检查器"""

    def __init__(self, config: DataQualityConfig = None):
        self.config = config or DataQualityConfig()
        self.errors = []
        self.warnings = []

    def validate(self, data: List[Dict]) -> Dict:
        """验证训练数据"""
        self.errors = []
        self.warnings = []

        seen_hashes = set()
        valid_count = 0

        for i, item in enumerate(data):
            item_errors = self._validate_item(i, item)
            if item_errors:
                self.errors.extend(item_errors)
                continue

            # 去重检查
            if self.config.remove_duplicates:
                content_hash = self._hash_item(item)
                if content_hash in seen_hashes:
                    self.warnings.append(f"样本 {i}: 重复样本")
                    continue
                seen_hashes.add(content_hash)

            valid_count += 1

        return {
            "total": len(data),
            "valid": valid_count,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_rate": len(self.errors) / len(data) if data else 0
        }

    def _validate_item(self, idx: int, item: Dict) -> List[str]:
        errors = []
        messages = item.get("messages", [])

        if not messages:
            errors.append(f"样本 {idx}: 缺少messages字段")
            return errors

        if len(messages) > self.config.max_turns:
            errors.append(f"样本 {idx}: 对话轮次过多 ({len(messages)})")

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role not in ("system", "user", "assistant"):
                errors.append(f"样本 {idx}: 无效角色 '{role}'")

            if role == "user" and len(content) < self.config.min_input_length:
                errors.append(f"样本 {idx}: 用户输入过短")

            if role == "assistant" and len(content) < self.config.min_output_length:
                errors.append(f"样本 {idx}: 助手输出过短")

        return errors

    def _hash_item(self, item: Dict) -> str:
        import hashlib
        content = json.dumps(item, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content.encode()).hexdigest()


def clean_training_data(data: List[Dict]) -> List[Dict]:
    """清洗训练数据"""
    cleaned = []
    for item in data:
        messages = item.get("messages", [])
        # 清理空白字符
        for msg in messages:
            msg["content"] = msg["content"].strip()
            # 移除空消息
        messages = [m for m in messages if m.get("content")]

        if messages:
            cleaned.append({"messages": messages})

    return cleaned
```

### 2.3 数据集构建

```python
class DatasetBuilder:
    """训练数据集构建器"""

    def __init__(self, system_prompt: str = ""):
        self.system_prompt = system_prompt
        self.examples = []

    def add_example(self, user_input: str, assistant_output: str, system: str = None):
        """添加训练样本"""
        messages = []
        if system or self.system_prompt:
            messages.append({"role": "system", "content": system or self.system_prompt})
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": assistant_output})
        self.examples.append({"messages": messages})

    def add_conversation(self, messages: List[Dict]):
        """添加多轮对话"""
        if self.system_prompt and messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        self.examples.append({"messages": messages})

    def load_from_jsonl(self, path: str):
        """从JSONL文件加载"""
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                self.examples.append(json.loads(line))

    def export(self, path: str, split_ratio: float = 0.9):
        """导出为训练集和验证集"""
        import random
        random.shuffle(self.examples)

        split_idx = int(len(self.examples) * split_ratio)
        train_data = self.examples[:split_idx]
        val_data = self.examples[split_idx:]

        with open(f"{path}/train.jsonl", 'w', encoding='utf-8') as f:
            for item in train_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        with open(f"{path}/val.jsonl", 'w', encoding='utf-8') as f:
            for item in val_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        print(f"训练集: {len(train_data)} 条, 验证集: {len(val_data)} 条")
```

## 3. LoRA微调

### 3.1 LoRA原理

LoRA通过在Transformer层中注入可训练的低秩分解矩阵，大幅减少可训练参数：

```
原始权重 W (d×d) → 冻结
新增 W = W + α·BA，其中 B(d×r), A(r×d), r << d
可训练参数量: 2×d×r（远小于 d²）
```

### 3.2 使用Hugging Face PEFT进行LoRA微调

```python
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
)
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from datasets import load_dataset

def setup_lora_model(model_name: str = "meta-llama/Llama-2-7b-hf"):
    """加载模型并配置LoRA"""

    # 加载基座模型
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    # LoRA配置
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,                    # LoRA秩（通常8-64）
        lora_alpha=32,           # 缩放因子（通常为2×r）
        lora_dropout=0.05,       # Dropout
        target_modules=[         # 要适配的模块
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        bias="none",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()  # 显示可训练参数比例

    return model, tokenizer


def train_lora(model, tokenizer, train_data_path: str, val_data_path: str, output_dir: str):
    """执行LoRA训练"""

    # 加载数据集
    dataset = load_dataset("json", data_files={
        "train": train_data_path,
        "validation": val_data_path,
    })

    # 数据预处理
    def preprocess(examples):
        texts = []
        for messages in examples["messages"]:
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
            texts.append(text)

        model_inputs = tokenizer(
            texts, max_length=2048, truncation=True, padding="max_length"
        )
        model_inputs["labels"] = model_inputs["input_ids"].copy()
        return model_inputs

    tokenized_dataset = dataset.map(preprocess, batched=True, remove_columns=["messages"])

    # 训练参数
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        weight_decay=0.01,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=100,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to="none",
        bf16=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    return trainer
```

## 4. QLoRA（量化LoRA）

QLoRA通过4-bit量化+LoRA，在消费级GPU上微调大模型。

```python
from transformers import BitsAndBytesConfig

def setup_qlora_model(model_name: str = "meta-llama/Llama-2-7b-hf"):
    """4-bit QLoRA配置"""

    # 量化配置
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",           # NF4量化
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,       # 双重量化
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    from peft import prepare_model_for_kbit_training
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,                     # QLoRA通常用更小的r
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        bias="none",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    return model

# GPU显存估算：
# 7B模型  QLoRA: ~6GB VRAM   LoRA: ~16GB VRAM
# 13B模型 QLoRA: ~10GB VRAM  LoRA: ~32GB VRAM
# 70B模型 QLoRA: ~36GB VRAM  LoRA: ~160GB VRAM
```

## 5. 使用OpenAI API微调

```python
from openai import OpenAI
import time

class OpenAIFineTuner:
    """OpenAI模型微调封装"""

    def __init__(self):
        self.client = OpenAI()

    def upload_data(self, file_path: str) -> str:
        """上传训练文件"""
        response = self.client.files.create(
            file=open(file_path, "rb"),
            purpose="fine-tune"
        )
        print(f"文件已上传: {response.id}")
        return response.id

    def create_job(self, training_file_id: str, model: str = "gpt-3.5-turbo",
                   suffix: str = None) -> str:
        """创建微调任务"""
        params = {
            "training_file": training_file_id,
            "model": model,
            "hyperparameters": {
                "n_epochs": 3,
                "batch_size": "auto",
                "learning_rate_multiplier": "auto",
            }
        }
        if suffix:
            params["suffix"] = suffix

        job = self.client.fine_tuning.jobs.create(**params)
        print(f"微调任务已创建: {job.id}")
        return job.id

    def monitor_job(self, job_id: str):
        """监控微调进度"""
        while True:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            print(f"状态: {job.status}")

            if job.status == "succeeded":
                print(f"完成！模型: {job.fine_tuned_model}")
                return job.fine_tuned_model
            elif job.status == "failed":
                print(f"失败: {job.error}")
                return None

            time.sleep(30)

    def use_finetuned_model(self, model_name: str, messages: List[Dict]) -> str:
        """使用微调后的模型"""
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content


# 使用示例
# tuner = OpenAIFineTuner()
# file_id = tuner.upload_data("train.jsonl")
# job_id = tuner.create_job(file_id, suffix="my-custom-model")
# model_name = tuner.monitor_job(job_id)
```

## 6. 评估方法

### 6.1 自动评估

```python
import numpy as np
from typing import List, Dict

class ModelEvaluator:
    """模型评估工具"""

    def __init__(self, client: OpenAI):
        self.client = client

    def evaluate_perplexity(self, model, tokenizer, eval_texts: List[str]) -> float:
        """计算困惑度"""
        total_loss = 0
        total_tokens = 0

        for text in eval_texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs, labels=inputs["input_ids"])
                total_loss += outputs.loss.item() * inputs["input_ids"].shape[1]
                total_tokens += inputs["input_ids"].shape[1]

        avg_loss = total_loss / total_tokens
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        return perplexity

    def evaluate_task(self, test_data: List[Dict], model_name: str) -> Dict:
        """评估任务完成质量"""
        correct = 0
        total = len(test_data)
        results = []

        for item in test_data:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=item["messages"][:-1],  # 去掉最后一个assistant消息
                temperature=0
            )
            predicted = response.choices[0].message.content
            expected = item["messages"][-1]["content"]

            # 使用GPT-4评估
            score = self._llm_judge(predicted, expected, item["messages"][-2]["content"])
            results.append({
                "input": item["messages"][-2]["content"],
                "expected": expected,
                "predicted": predicted,
                "score": score
            })

        avg_score = sum(r["score"] for r in results) / len(results)
        return {
            "average_score": avg_score,
            "total": total,
            "details": results
        }

    def _llm_judge(self, predicted: str, expected: str, question: str) -> float:
        """使用LLM评判回答质量"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"""请评估以下回答的质量（0-1分）。

问题：{question}
标准答案：{expected}
模型回答：{predicted}

评分标准：
- 0.0: 完全错误
- 0.25: 部分正确但有重大错误
- 0.5: 基本正确但不够完整
- 0.75: 正确且较完整
- 1.0: 完全正确且完整

只返回数字分数："""
            }],
            temperature=0
        )
        try:
            return float(response.choices[0].message.content.strip())
        except:
            return 0.5

    def compare_models(self, test_data: List[Dict],
                       baseline_model: str, finetuned_model: str) -> Dict:
        """对比基座模型和微调模型"""
        baseline_results = self.evaluate_task(test_data, baseline_model)
        finetuned_results = self.evaluate_task(test_data, finetuned_model)

        return {
            "baseline_score": baseline_results["average_score"],
            "finetuned_score": finetuned_results["average_score"],
            "improvement": finetuned_results["average_score"] - baseline_results["average_score"],
            "improvement_pct": (
                (finetuned_results["average_score"] - baseline_results["average_score"])
                / baseline_results["average_score"] * 100
            )
        }
```

### 6.2 评估指标汇总

| 指标 | 适用场景 | 说明 |
|------|----------|------|
| Perplexity | 语言建模 | 越低越好，衡量模型预测能力 |
| BLEU | 翻译/摘要 | 基于n-gram的文本相似度 |
| ROUGE | 摘要 | 基于召回的文本相似度 |
| F1 Score | QA/分类 | 精确率和召回率的调和平均 |
| Human Eval | 通用 | 人工评估，最可靠但成本高 |
| LLM Judge | 通用 | 用强模型评估弱模型，性价比高 |

## 7. 最佳实践

| 实践 | 说明 |
|------|------|
| **数据质量优先** | 100条高质量数据 > 1000条低质量数据 |
| **从LoRA开始** | 先用LoRA快速验证，再考虑全量微调 |
| **合理设置超参** | lr=1e-4~3e-4, epochs=2-5, batch_size根据GPU调整 |
| **持续评估** | 每个checkpoint都评估，防止过拟合 |
| **保存检查点** | 定期保存，方便回滚 |
| **监控loss** | 训练loss和验证loss差距过大说明过拟合 |
| **数据增强** | 对少量数据使用GPT-4扩写 |
| **A/B测试** | 线上对比微调模型和基座模型效果 |

## 8. 相关页面

- [[Prompt Engineering指南]] - 微调前先尝试Prompt优化
- [[RAG系统设计]] - RAG作为微调的替代/补充方案
- [[Agent架构模式]] - 微调模型在Agent中的应用
- [[AI应用开发实践]] - 微调模型的部署和监控

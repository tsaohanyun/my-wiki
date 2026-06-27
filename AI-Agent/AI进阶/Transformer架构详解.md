---
title: Transformer架构详解
aliases:
  - Transformer Architecture
  - Transformer详解
  - 自注意力机制
tags:
  - AI
  - ML
  - DeepLearning
  - NLP
  - Transformer
  - Attention
type: wiki
status: published
created: 2026-06-28
updated: 2026-06-28
source: "Attention Is All You Need (Vaswani et al., 2017)"
difficulty: advanced
project: AI-Agent
---

# Transformer 架构详解

> Transformer 是现代大语言模型（LLM）的基石架构，由 Google 团队在 2017 年论文 *"Attention Is All You Need"* 中提出。它完全摒弃了 RNN/CNN 的序列依赖，依靠 **自注意力机制** 实现高效的并行计算与长距离依赖建模。

---

## 1. 核心概念总览

| 组件 | 功能 | 关键公式 |
|------|------|----------|
| Self-Attention | 捕捉序列内部 token 间关系 | $\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$ |
| Multi-Head Attention | 多视角并行注意力 | $\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,\dots,\text{head}_h)W^O$ |
| Positional Encoding | 注入位置信息 | $PE_{(pos,2i)} = \sin(pos/10000^{2i/d})$ |
| Feed-Forward Network | 非线性变换 | $\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$ |
| Layer Norm & Residual | 稳定训练 | $x = \text{LayerNorm}(x + \text{Sublayer}(x))$ |

---

## 2. Self-Attention（自注意力机制）

### 2.1 原理

对于输入序列 $X \in \mathbb{R}^{n \times d}$，通过三个可学习权重矩阵 $W_Q, W_K, W_V$ 将其映射为 **Query、Key、Value** 三组向量：

```
Q = X @ W_Q    # (n, d_k)
K = X @ W_K    # (n, d_k)
V = X @ W_V    # (n, d_v)

# 注意力分数
scores = Q @ K.T / sqrt(d_k)          # (n, n)
attn_weights = softmax(scores, dim=-1) # (n, n)
output = attn_weights @ V              # (n, d_v)
```

### 2.2 PyTorch 实现示例

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class ScaledDotProductAttention(nn.Module):
    """缩放点积注意力"""
    def __init__(self, temperature, attn_dropout=0.1):
        super().__init__()
        self.temperature = temperature
        self.dropout = nn.Dropout(attn_dropout)

    def forward(self, q, k, v, mask=None):
        # q: (batch, heads, seq_len, d_k)
        attn = torch.matmul(q / self.temperature, k.transpose(-2, -1))

        if mask is not None:
            attn = attn.masked_fill(mask == 0, -1e9)

        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn)
        output = torch.matmul(attn, v)
        return output, attn


class MultiHeadAttention(nn.Module):
    """多头注意力层"""
    def __init__(self, n_head, d_model, d_k, d_v, dropout=0.1):
        super().__init__()
        self.n_head = n_head
        self.d_k = d_k
        self.d_v = d_v

        self.w_qs = nn.Linear(d_model, n_head * d_k, bias=False)
        self.w_ks = nn.Linear(d_model, n_head * d_k, bias=False)
        self.w_vs = nn.Linear(d_model, n_head * d_v, bias=False)
        self.fc = nn.Linear(n_head * d_v, d_model)

        self.attention = ScaledDotProductAttention(temperature=math.sqrt(d_k))
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, q, k, v, mask=None):
        d_k, d_v, n_head = self.d_k, self.d_v, self.n_head
        sz_b, len_q, len_k, len_v = q.size(0), q.size(1), k.size(1), v.size(1)

        residual = q
        q = self.layer_norm(q)

        # 线性映射并分头
        q = self.w_qs(q).view(sz_b, len_q, n_head, d_k).transpose(1, 2)
        k = self.w_ks(k).view(sz_b, len_k, n_head, d_k).transpose(1, 2)
        v = self.w_vs(v).view(sz_b, len_v, n_head, d_v).transpose(1, 2)

        if mask is not None:
            mask = mask.unsqueeze(1)  # (batch, 1, 1, seq_len)

        # 注意力计算
        out, attn = self.attention(q, k, v, mask=mask)

        # 合并多头
        out = out.transpose(1, 2).contiguous().view(sz_b, len_q, -1)
        out = self.dropout(self.fc(out))
        out = out + residual

        return out, attn
```

---

## 3. Positional Encoding（位置编码）

由于 Transformer 不含任何序列顺序信息，必须显式注入位置信号。

### 3.1 正弦/余弦编码（原始论文）

```python
class SinusoidalPositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
```

### 3.2 可学习位置编码

```python
class LearnablePositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        self.pe = nn.Parameter(torch.randn(1, max_len, d_model) * 0.02)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
```

### 3.3 RoPE（旋转位置编码）

> RoPE 是目前大模型（LLaMA、Qwen 等）最常用的位置编码方案。

```python
def precompute_freqs_cis(dim, end, theta=10000.0):
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))
    t = torch.arange(end)
    freqs = torch.outer(t, freqs)
    freqs_cis = torch.polar(torch.ones_like(freqs), freqs)
    return freqs_cis

def apply_rotary_emb(xq, xk, freqs_cis):
    xq_ = torch.view_as_complex(xq.float().reshape(*xq.shape[:-1], -1, 2))
    xk_ = torch.view_as_complex(xk.float().reshape(*xk.shape[:-1], -1, 2))
    freqs_cis = freqs_cis.view(1, xq_.shape[1], 1, xq_.shape[-1])
    xq_out = torch.view_as_real(xq_ * freqs_cis).flatten(3)
    xk_out = torch.view_as_real(xk_ * freqs_cis).flatten(3)
    return xq_out.type_as(xq), xk_out.type_as(xk)
```

### 3.4 各编码方案对比

| 方案 | 外推性 | 参数量 | 代表模型 |
|------|--------|--------|----------|
| Sinusoidal | 一般 | 0 | 原始 Transformer |
| Learnable | 差 | 大 | GPT-2, BERT |
| ALiBi | 好 | 0 | BLOOM |
| RoPE | 好 | 0 | LLaMA, Qwen |
| YaRN/RoPE-NTK | 优秀 | 0 | 长上下文扩展 |

---

## 4. Encoder-Decoder 架构

### 4.1 整体结构

```
输入序列 → [Embedding + PosEnc] → Encoder × N → Memory
                                                    ↓
输出序列 → [Embedding + PosEnc] → Decoder × N → Linear → Softmax → 输出概率
```

- **Encoder**: 双向自注意力，适用于理解任务（BERT）
- **Decoder**: 因果自注意力 + 交叉注意力，适用于生成任务（GPT）
- **Encoder-Decoder**: 适用于 seq2seq 任务（T5, BART）

### 4.2 完整 Transformer Block

```python
class EncoderLayer(nn.Module):
    def __init__(self, d_model, n_head, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(n_head, d_model, d_model // n_head, d_model // n_head, dropout)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        attn_out, _ = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        ffn_out = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_out))
        return x


class DecoderLayer(nn.Module):
    def __init__(self, d_model, n_head, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(n_head, d_model, d_model // n_head, d_model // n_head, dropout)
        self.cross_attn = MultiHeadAttention(n_head, d_model, d_model // n_head, d_model // n_head, dropout)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, enc_output, tgt_mask=None, src_mask=None):
        # 因果自注意力
        attn_out, _ = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_out))
        # 交叉注意力
        cross_out, _ = self.cross_attn(x, enc_output, enc_output, src_mask)
        x = self.norm2(x + self.dropout(cross_out))
        # FFN
        ffn_out = self.ffn(x)
        x = self.norm3(x + self.dropout(ffn_out))
        return x
```

---

## 5. 关键 Mask 机制

```python
def create_causal_mask(seq_len):
    """因果掩码：防止 decoder 看到未来 token"""
    mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)
    return mask  # (1, 1, seq_len, seq_len)

def create_padding_mask(input_ids, pad_id=0):
    """填充掩码：忽略 padding token"""
    return (input_ids != pad_id).unsqueeze(1).unsqueeze(1)  # (batch, 1, 1, seq_len)
```

---

## 6. 常见变体

| 变体 | 特点 | 代表模型 |
|------|------|----------|
| Encoder-Only | 双向注意力，擅长理解 | BERT, RoBERTa, DeBERTa |
| Decoder-Only | 因果注意力，擅长生成 | GPT, LLaMA, Qwen, Mistral |
| Encoder-Decoder | 交叉注意力，擅长翻译/摘要 | T5, BART, Whisper |
| MoE Transformer | 稀疏专家混合 | Mixtral, DeepSeek-MoE |
| Linear Attention | $O(n)$ 复杂度 | Performer, Linformer |

---

## 7. 最佳实践

1. **预归一化 vs 后归一化**：现代大模型普遍采用 Pre-Norm（先 LayerNorm 再做 Attention），训练更稳定。
2. **激活函数选择**：推荐使用 SwiGLU 或 GeGLU 替代 ReLU，表现更好。
3. **上下文长度扩展**：使用 RoPE + NTK-aware 插值或 YaRN 方案。
4. **注意力计算优化**：Flash Attention 可将注意力计算速度提升 2-4 倍，显著减少显存占用。
5. **KV Cache**：推理阶段使用 KV Cache 避免重复计算历史 token 的 Key/Value。
6. **GQA/MQA**：分组查询注意力（如 LLaMA-2/3）减少 KV Cache 显存占用。

```python
# 使用 Flash Attention
import torch.nn.functional as F

# PyTorch 2.0+ 内置支持
output = F.scaled_dot_product_attention(q, k, v, is_causal=True)
```

---

## 8. 相关页面

- [[大模型训练工程]] — Transformer 大规模训练的分布式策略
- [[LangChain开发指南]] — 基于 Transformer 模型的应用开发
- [[向量数据库实战]] — Embedding 模型与向量存储
- [[AI安全与对齐]] — 大模型安全对齐技术

---

## 9. 参考文献

1. Vaswani, A. et al. (2017). *Attention Is All You Need.* NeurIPS.
2. Su, J. et al. (2021). *RoFormer: Enhanced Transformer with Rotary Position Embedding.*
3. Dao, T. et al. (2022). *FlashAttention: Fast and Memory-Efficient Exact Attention.*
4. Shazeer, N. (2020). *GLU Variants Improve Transformer.*

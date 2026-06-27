---
title: RAG系统设计
aliases:
  - 检索增强生成
  - Retrieval Augmented Generation
  - 向量检索
tags:
  - RAG
  - LLM
  - 向量数据库
  - 检索
  - embeddings
type: guide
status: active
created: 2026-06-27
updated: 2026-06-27
source: internal
difficulty: advanced
project: AI-Agent
---

# RAG系统设计

> RAG（Retrieval Augmented Generation）通过检索外部知识库来增强LLM的生成能力，解决知识过时和幻觉问题。

## 1. RAG架构总览

```
用户查询 → 查询理解 → 检索 → 重排序 → 上下文构建 → LLM生成 → 后处理 → 输出
                ↑                                    |
                └──── 反馈优化 ←──────────────────────┘
```

## 2. 文档处理与分块

### 2.1 文档加载器

```python
from pathlib import Path
from typing import List, Dict
import hashlib

class Document:
    def __init__(self, content: str, metadata: Dict):
        self.content = content
        self.metadata = metadata
        self.doc_id = hashlib.md5(content.encode()).hexdigest()

class DocumentLoader:
    """多格式文档加载器"""

    @staticmethod
    def load_txt(path: str) -> List[Document]:
        text = Path(path).read_text(encoding='utf-8')
        return [Document(content=text, metadata={"source": path, "type": "txt"})]

    @staticmethod
    def load_markdown(path: str) -> List[Document]:
        text = Path(path).read_text(encoding='utf-8')
        # 按一级标题分割
        sections = text.split('\n# ')
        documents = []
        for i, section in enumerate(sections):
            title = section.split('\n')[0].strip() if i > 0 else "首页"
            documents.append(Document(
                content=section.strip(),
                metadata={"source": path, "type": "md", "section": title}
            ))
        return documents

    @staticmethod
    def load_pdf(path: str) -> List[Document]:
        try:
            import pdfplumber
            documents = []
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        documents.append(Document(
                            content=text,
                            metadata={"source": path, "type": "pdf", "page": i + 1}
                        ))
            return documents
        except ImportError:
            raise ImportError("请安装 pdfplumber: pip install pdfplumber")
```

### 2.2 文档分块策略

```python
from dataclasses import dataclass
import re

@dataclass
class ChunkConfig:
    chunk_size: int = 512        # 分块大小（token数）
    chunk_overlap: int = 50      # 重叠token数
    min_chunk_size: int = 50     # 最小分块大小
    separators: List[str] = None # 分隔符优先级

    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\n", "。", ".", "！", "!", "？", "?", "；", ";", " "]

class TextChunker:
    """智能文本分块器"""

    def __init__(self, config: ChunkConfig = None):
        self.config = config or ChunkConfig()

    def chunk_by_separators(self, text: str) -> List[str]:
        """递归分块：按分隔符优先级分割"""
        if len(text) <= self.config.chunk_size:
            return [text] if len(text) >= self.config.min_chunk_size else []

        for sep in self.config.separators:
            if sep in text:
                parts = text.split(sep)
                chunks = []
                current_chunk = ""

                for part in parts:
                    if len(current_chunk) + len(part) + len(sep) <= self.config.chunk_size:
                        current_chunk += (sep if current_chunk else "") + part
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = part

                if current_chunk and len(current_chunk) >= self.config.min_chunk_size:
                    chunks.append(current_chunk)

                # 处理重叠
                return self._add_overlap(chunks)

        # 无合适分隔符，强制按长度分割
        return [text[i:i+self.config.chunk_size]
                for i in range(0, len(text), self.config.chunk_size - self.config.chunk_overlap)]

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """为分块添加重叠"""
        if len(chunks) <= 1 or self.config.chunk_overlap == 0:
            return chunks

        result = [chunks[0]]
        for i in range(1, len(chunks)):
            # 从前一个块取末尾作为当前块开头
            prev_tail = chunks[i-1][-self.config.chunk_overlap:]
            result.append(prev_tail + chunks[i])
        return result

    def chunk_by_semantic(self, text: str, embeddings_model=None) -> List[str]:
        """语义分块（基于主题变化）"""
        sentences = re.split(r'(?<=[。！？.!?])', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not embeddings_model or len(sentences) < 2:
            return self.chunk_by_separators(text)

        # 计算相邻句子的语义相似度
        embeddings = embeddings_model.encode(sentences)
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            similarities.append(sim)

        # 在相似度低的位置分割（主题切换点）
        threshold = sum(similarities) / len(similarities) - 0.1
        chunks = []
        current_chunk = sentences[0]

        for i, sim in enumerate(similarities):
            if sim < threshold or len(current_chunk) > self.config.chunk_size:
                chunks.append(current_chunk)
                current_chunk = sentences[i + 1]
            else:
                current_chunk += sentences[i + 1]

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    @staticmethod
    def _cosine_similarity(a, b) -> float:
        import numpy as np
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

## 3. 向量数据库

### 3.1 Embedding生成

```python
from openai import OpenAI
import numpy as np

class EmbeddingService:
    """Embedding服务封装"""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model
        self.dimension = 1536  # text-embedding-3-small

    def embed(self, texts: List[str]) -> np.ndarray:
        """批量生成embedding"""
        # OpenAI限制每批最多8191条
        all_embeddings = []
        batch_size = 1000

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)

        return np.array(all_embeddings)

    def embed_query(self, query: str) -> np.ndarray:
        """单条查询embedding"""
        return self.embed([query])[0]
```

### 3.2 向量存储（FAISS实现）

```python
import faiss
import pickle
from pathlib import Path

class FAISSVectorStore:
    """基于FAISS的向量存储"""

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # 内积（余弦相似度需先归一化）
        self.documents = []
        self.doc_id_map = {}

    def add(self, embeddings: np.ndarray, documents: List[Document]):
        """添加文档向量"""
        # L2归一化，使内积等价于余弦相似度
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))

        start_idx = len(self.documents)
        for i, doc in enumerate(documents):
            idx = start_idx + i
            self.documents.append(doc)
            self.doc_id_map[doc.doc_id] = idx

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """相似度搜索"""
        query = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query)

        scores, indices = self.index.search(query, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "score": float(score)
                })
        return results

    def save(self, path: str):
        """持久化存储"""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(save_path / "index.faiss"))
        with open(save_path / "documents.pkl", 'wb') as f:
            pickle.dump(self.documents, f)

    def load(self, path: str):
        """加载存储"""
        save_path = Path(path)
        self.index = faiss.read_index(str(save_path / "index.faiss"))
        with open(save_path / 'documents.pkl', 'rb') as f:
            self.documents = pickle.load(f)
```

### 3.3 Milvus向量数据库集成

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

class MilvusVectorStore:
    """基于Milvus的向量存储（生产环境推荐）"""

    def __init__(self, collection_name: str, dimension: int = 1536):
        connections.connect("default", host="localhost", port="19530")
        self.collection_name = collection_name
        self.dimension = dimension
        self._create_collection()

    def _create_collection(self):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        schema = CollectionSchema(fields, description="RAG vector store")

        if self.collection_name not in [c.name for c in Collection.list_collections()]:
            self.collection = Collection(self.collection_name, schema)
            # 创建索引
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            self.collection.create_index("embedding", index_params)
        else:
            self.collection = Collection(self.collection_name)
            self.collection.load()

    def insert(self, embeddings: List[List[float]], documents: List[Document]):
        """批量插入"""
        data = [
            embeddings,
            [doc.content for doc in documents],
            [doc.metadata.get("source", "") for doc in documents],
            [doc.metadata for doc in documents],
        ]
        self.collection.insert(data)
        self.collection.flush()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """相似度搜索"""
        self.collection.load()
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 16}},
            limit=top_k,
            output_fields=["content", "source", "metadata"]
        )

        return [{
            "content": hit.entity.get("content"),
            "source": hit.entity.get("source"),
            "metadata": hit.entity.get("metadata"),
            "score": hit.score
        } for hit in results[0]]
```

## 4. 检索策略

### 4.1 混合检索（Hybrid Search）

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    """混合检索：结合向量检索和BM25关键词检索"""

    def __init__(self, vector_store, embedding_service, alpha: float = 0.7):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.alpha = alpha  # 向量检索权重

        # BM25索引
        self.bm25 = None
        self.corpus_tokens = []

    def build_bm25_index(self, documents: List[Document]):
        """构建BM25索引"""
        self.bm25_documents = documents
        self.corpus_tokens = [self._tokenize(doc.content) for doc in documents]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def _tokenize(self, text: str) -> List[str]:
        """中文分词"""
        import jieba
        return list(jieba.cut(text))

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """混合检索"""
        # 向量检索
        query_emb = self.embedding_service.embed_query(query)
        vector_results = self.vector_store.search(query_emb, top_k=top_k * 2)

        # BM25检索
        query_tokens = self._tokenize(query)
        bm25_scores = self.bm25.get_scores(query_tokens)
        bm25_top_idx = np.argsort(bm25_scores)[-top_k * 2:][::-1]

        # 分数归一化并合并
        scores = {}

        # 向量分数
        if vector_results:
            max_vec_score = max(r["score"] for r in vector_results)
            for r in vector_results:
                doc_id = r["document"].doc_id
                scores[doc_id] = {
                    "score": self.alpha * (r["score"] / max_vec_score),
                    "document": r["document"]
                }

        # BM25分数
        if len(bm25_top_idx) > 0:
            max_bm25 = max(bm25_scores[idx] for idx in bm25_top_idx)
            for idx in bm25_top_idx:
                doc = self.bm25_documents[idx]
                bm25_norm = bm25_scores[idx] / max_bm25 if max_bm25 > 0 else 0
                if doc.doc_id in scores:
                    scores[doc.doc_id]["score"] += (1 - self.alpha) * bm25_norm
                else:
                    scores[doc.doc_id] = {
                        "score": (1 - self.alpha) * bm25_norm,
                        "document": doc
                    }

        # 排序返回
        sorted_results = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return sorted_results[:top_k]
```

### 4.2 查询改写与扩展

```python
class QueryProcessor:
    """查询预处理：改写、扩展、分解"""

    def __init__(self, client: OpenAI, model: str = "gpt-4"):
        self.client = client
        self.model = model

    def rewrite(self, query: str) -> str:
        """查询改写：使检索更准确"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"""请将以下用户查询改写为更适合搜索的形式，保持语义但使用更标准的表述：

原始查询：{query}

改写后的查询："""
            }],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    def expand(self, query: str, n: int = 3) -> List[str]:
        """查询扩展：生成多个相关查询"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"""基于以下查询，生成{n}个相关的不同角度的查询，用于提高检索召回率。
每个查询占一行。

原始查询：{query}

相关查询："""
            }],
            temperature=0.7
        )
        queries = response.choices[0].message.content.strip().split('\n')
        return [query] + [q.strip() for q in queries if q.strip()][:n]

    def decompose(self, query: str) -> List[str]:
        """问题分解：将复杂问题拆为子问题"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"""将以下复杂问题分解为2-4个简单的子问题，每个子问题可以独立检索答案。

原始问题：{query}

子问题（每行一个）："""
            }],
            temperature=0
        )
        return [q.strip() for q in response.choices[0].message.content.strip().split('\n') if q.strip()]
```

### 4.3 重排序 (Re-ranking)

```python
class CrossEncoderReranker:
    """使用Cross-Encoder进行重排序"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: List[Document], top_k: int = 5) -> List[Dict]:
        """重排序"""
        pairs = [(query, doc.content) for doc in documents]
        scores = self.model.predict(pairs)

        scored_docs = [
            {"document": doc, "score": float(score)}
            for doc, score in zip(documents, scores)
        ]
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]
```

## 5. RAG Pipeline

```python
class RAGPipeline:
    """完整的RAG管道"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.client = OpenAI()
        self.embedding_service = EmbeddingService()
        self.vector_store = FAISSVectorStore()
        self.query_processor = QueryProcessor(self.client)
        self.chunker = TextChunker(ChunkConfig(chunk_size=512, chunk_overlap=50))

    def ingest(self, documents: List[Document]):
        """文档入库"""
        chunks = []
        for doc in documents:
            text_chunks = self.chunker.chunk_by_separators(doc.content)
            for i, chunk_text in enumerate(text_chunks):
                chunk_doc = Document(
                    content=chunk_text,
                    metadata={**doc.metadata, "chunk_index": i}
                )
                chunks.append(chunk_doc)

        embeddings = self.embedding_service.embed([c.content for c in chunks])
        self.vector_store.add(embeddings, chunks)
        print(f"已入库 {len(chunks)} 个文档分块")

    def query(self, question: str, top_k: int = 5) -> str:
        """查询并生成回答"""
        # 1. 查询处理
        expanded_queries = self.query_processor.expand(question)

        # 2. 检索
        all_results = []
        for q in expanded_queries:
            query_emb = self.embedding_service.embed_query(q)
            results = self.vector_store.search(query_emb, top_k=top_k)
            all_results.extend(results)

        # 去重
        seen = set()
        unique_results = []
        for r in all_results:
            doc_id = r["document"].doc_id
            if doc_id not in seen:
                seen.add(doc_id)
                unique_results.append(r)

        unique_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = unique_results[:top_k]

        # 3. 构建上下文
        context = "\n\n---\n\n".join(
            f"[来源: {r['document'].metadata.get('source', '未知')}]\n{r['document'].content}"
            for r in top_results
        )

        # 4. 生成回答
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """你是一个知识问答助手。请根据提供的参考资料回答问题。
要求：
- 只基于提供的资料回答，不要编造信息
- 如果资料不足以回答问题，明确说明
- 引用信息时注明来源"""},
                {"role": "user", "content": f"""参考资料：
{context}

问题：{question}

请回答："""}
            ],
            temperature=0
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "sources": [r["document"].metadata for r in top_results],
            "scores": [r["score"] for r in top_results]
        }
```

## 6. 最佳实践

| 实践 | 说明 |
|------|------|
| **分块大小** | 通常256-512 token，根据文档类型调整 |
| **分块重叠** | 10-20%重叠避免信息断裂 |
| **混合检索** | 向量+关键词提升召回率 |
| **重排序** | Cross-Encoder显著提升精度 |
| **查询扩展** | 多角度查询提高覆盖率 |
| **元数据过滤** | 利用元数据缩小检索范围 |
| **评估指标** | 跟踪Recall@K、MRR、Answer Relevance |
| **增量更新** | 支持文档的增量索引和更新 |

## 7. 相关页面

- [[Prompt Engineering指南]] - RAG中提示词的设计
- [[LLM微调指南]] - 当RAG效果不佳时考虑微调Embedding模型
- [[Agent架构模式]] - RAG在Agent系统中的集成
- [[AI应用开发实践]] - RAG系统的工程化部署

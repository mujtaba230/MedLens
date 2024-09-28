import asyncio
import time
from typing import List, Dict, Any, Optional

import httpx
from sentence_transformers import SentenceTransformer, CrossEncoder

from app.core.config import get_settings

settings = get_settings()

RAG_SYSTEM_PROMPT = """You are a clinical assistant. Answer the user's medical query using ONLY the provided document context. If the context does not contain enough information, say so. Do not hallucinate. Cite document IDs in your answer.

Context:
{context}

Question: {query}

Answer:"""


class Chunker:
    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.overlap = overlap or settings.CHUNK_OVERLAP

    def fixed_chunk(self, text: str) -> List[Dict[str, Any]]:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append({
                "text": chunk_text,
                "start_word": start,
                "end_word": end,
                "strategy": "fixed"
            })
            start += self.chunk_size - self.overlap
        return chunks

    def semantic_chunk(self, text: str) -> List[Dict[str, Any]]:
        sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if s.strip()]
        chunks = []
        current_chunk = []
        current_len = 0
        start_sent = 0

        for i, sent in enumerate(sentences):
            sent_len = len(sent.split())
            if current_len + sent_len > self.chunk_size and current_chunk:
                chunks.append({
                    "text": ". ".join(current_chunk) + ".",
                    "start_sent": start_sent,
                    "end_sent": i - 1,
                    "strategy": "semantic"
                })
                overlap_sents = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk[-1:]
                current_chunk = overlap_sents + [sent]
                current_len = sum(len(s.split()) for s in current_chunk)
                start_sent = i - len(overlap_sents)
            else:
                current_chunk.append(sent)
                current_len += sent_len

        if current_chunk:
            chunks.append({
                "text": ". ".join(current_chunk) + ".",
                "start_sent": start_sent,
                "end_sent": len(sentences) - 1,
                "strategy": "semantic"
            })
        return chunks


class VectorStore:
    def __init__(self):
        self.collection_name = settings.MILVUS_COLLECTION
        self._client = None
        self._dimension = 384

    def _get_client(self):
        if self._client is None:
            try:
                from pymilvus import MilvusClient
                self._client = MilvusClient(uri=f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
            except Exception:
                self._client = None
        return self._client

    def ensure_collection(self):
        client = self._get_client()
        if client is None:
            return False
        try:
            if not client.has_collection(self.collection_name):
                client.create_collection(
                    collection_name=self.collection_name,
                    dimension=self._dimension,
                    auto_id=True
                )
            return True
        except Exception:
            return False

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        client = self._get_client()
        if client is None:
            return
        self.ensure_collection()
        data = []
        for chunk, emb in zip(chunks, embeddings):
            data.append({
                "vector": emb,
                "text": chunk["text"],
                "document_id": chunk.get("document_id", 0),
                "chunk_index": chunk.get("chunk_index", 0),
                "strategy": chunk.get("strategy", "fixed")
            })
        if data:
            try:
                client.insert(collection_name=self.collection_name, data=data)
            except Exception as e:
                print(f"Milvus insert error: {e}")

    def search(self, query_embedding: List[float], top_k: int = 10, filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        client = self._get_client()
        if client is None:
            return []
        try:
            results = client.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                limit=top_k,
                output_fields=["text", "document_id", "chunk_index", "strategy"]
            )
            chunks = []
            for hits in results:
                for hit in hits:
                    entity = hit.entity
                    chunks.append({
                        "document_id": entity.get("document_id", 0),
                        "chunk_text": entity.get("text", ""),
                        "score": float(hit.distance),
                        "metadata": {
                            "chunk_index": entity.get("chunk_index", 0),
                            "strategy": entity.get("strategy", "fixed")
                        }
                    })
            return chunks
        except Exception as e:
            print(f"Milvus search error: {e}")
            return []


class RAGService:
    def __init__(self):
        self._embedding_model = None
        self._reranker = None
        self.vector_store = VectorStore()
        self.chunker = Chunker()

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._embedding_model

    @property
    def reranker(self):
        if self._reranker is None:
            try:
                self._reranker = CrossEncoder(settings.RERANKER_MODEL)
            except Exception:
                self._reranker = None
        return self._reranker

    def chunk_document(self, text: str, strategy: str = "semantic") -> List[Dict[str, Any]]:
        if strategy == "semantic":
            return self.chunker.semantic_chunk(text)
        return self.chunker.fixed_chunk(text)

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        return self.embedding_model.encode(query, convert_to_numpy=True).tolist()

    def index_document(self, document_id: int, text: str, strategy: str = "semantic"):
        chunks = self.chunk_document(text, strategy)
        for i, chunk in enumerate(chunks):
            chunk["document_id"] = document_id
            chunk["chunk_index"] = i
        embeddings = self.embed_chunks(chunks)
        self.vector_store.add_chunks(chunks, embeddings)
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 10, filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        q_emb = self.embed_query(query)
        vector_results = self.vector_store.search(q_emb, top_k=top_k * 2, filters=filters)

        # Keyword fallback using simple BM25-like scoring
        query_words = set(query.lower().split())
        for r in vector_results:
            chunk_words = set(r["chunk_text"].lower().split())
            keyword_score = len(query_words & chunk_words) / max(len(query_words), 1)
            r["score"] = r["score"] * 0.7 + keyword_score * 0.3

        # Rerank if available
        if self.reranker and vector_results:
            pairs = [(query, r["chunk_text"]) for r in vector_results]
            rerank_scores = self.reranker.predict(pairs)
            for r, score in zip(vector_results, rerank_scores):
                r["score"] = float(score)

        vector_results.sort(key=lambda x: x["score"], reverse=True)
        return vector_results[:top_k]

    async def generate_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        context = "\n\n".join([
            f"[Document {c['document_id']}] {c['chunk_text']}" for c in chunks
        ])
        prompt = RAG_SYSTEM_PROMPT.format(context=context, query=query)

        provider = settings.LLM_PROVIDER
        if provider == "openai" and settings.OPENAI_API_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": settings.OPENAI_MODEL,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.2,
                            "max_tokens": 1500
                        },
                        timeout=60
                    )
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error generating answer: {e}"
        elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": settings.ANTHROPIC_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": settings.ANTHROPIC_MODEL,
                            "max_tokens": 1500,
                            "messages": [{"role": "user", "content": prompt}]
                        },
                        timeout=60
                    )
                    resp.raise_for_status()
                    return resp.json()["content"][0]["text"]
            except Exception as e:
                return f"Error generating answer: {e}"
        else:
            return f"[Mock LLM] Based on {len(chunks)} retrieved chunks: {chunks[0]['chunk_text'][:200]}..." if chunks else "No relevant context found."

    async def query(self, query: str, top_k: int = 5, filters: Optional[dict] = None) -> Dict[str, Any]:
        start = time.time()
        chunks = await asyncio.to_thread(self.retrieve, query, top_k, filters)
        answer = await self.generate_answer(query, chunks)
        latency = (time.time() - start) * 1000

        return {
            "query": query,
            "answer": answer,
            "retrieved_chunks": chunks,
            "sources": [{"document_id": c["document_id"], "score": c["score"]} for c in chunks],
            "latency_ms": latency
        }


rag_service = RAGService()

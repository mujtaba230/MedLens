from pydantic import BaseModel
from typing import List, Optional


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[dict] = None


class RetrievedChunk(BaseModel):
    document_id: int
    chunk_text: str
    score: float
    metadata: dict


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    sources: List[dict]
    latency_ms: float

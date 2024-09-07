from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
# Explicit model imports ensure Base.metadata.create_all() registers all tables
import app.models  # noqa: F401
from app.api import auth_router, documents_router, entities_router, rag_router, audit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="MedLens AI",
    description="MedLens AI: ingest healthcare documents, extract clinical entities, map to ICD-10/CPT, and query via RAG.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(entities_router)
app.include_router(rag_router)
app.include_router(audit_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "medlens-ai"}

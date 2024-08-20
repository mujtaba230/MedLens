# MedLens AI

A production-grade system for ingesting healthcare documents, extracting clinical entities, mapping to standard medical codes (ICD-10, CPT, SNOMED-CT), and enabling semantic search via Retrieval-Augmented Generation (RAG) with RBAC and full audit logging.

## Architecture

- **Backend**: FastAPI with async SQLAlchemy, RBAC (JWT), audit logging
- **Frontend**: React + Vite with drag-and-drop upload, chat-style RAG search, entity viewer, and audit dashboard
- **AI Pipeline**: OCR (Tesseract/pypdf), LLM entity extraction (OpenAI/Anthropic), Sentence Transformers embeddings, Milvus vector DB, cross-encoder reranking
- **Dataset**: Synthetic patient records (Faker) + simulated PDFs with configurable noise

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           Auth, Documents, Entities, RAG, Audit routers
│   │   ├── core/          Config, database, security, dependencies
│   │   ├── models/        SQLAlchemy models (User, Document, Entity, AuditLog)
│   │   ├── schemas/       Pydantic request/response schemas
│   │   ├── services/      OCR, extraction, code mapping, RAG, audit
│   │   └── main.py        FastAPI app entrypoint
│   ├── scripts/           seed_db.py
│   ├── tests/             pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/         Login, Upload, Documents, Search, Audit
│   │   ├── services/      API client (axios)
│   │   ├── hooks/         useAuth hook
│   │   ├── components/    Layout
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── ai_pipeline/
│   ├── embeddings.py      Standalone Milvus indexing
│   └── evaluation.py    RAG evaluation metrics
├── dataset/
│   ├── generate_synthetic.py    1000+ patient records
│   ├── simulate_documents.py    Convert to PDFs with noise
│   ├── llm_generate.py          Radiology/lab reports
│   └── benchmark_queries.json   Evaluation queries
├── docker-compose.yml
├── start.sh
└── .env.example
```

## Quick Start

### 1. Infrastructure (Docker)

```bash
docker-compose up -d
```

This starts PostgreSQL, Milvus (vector DB), Redis, and MinIO.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seed default users
cp ../.env.example .env
python scripts/seed_db.py

# Start server
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`

### Default Credentials

| Username | Password   | Role    |
|----------|------------|---------|
| admin    | admin123   | Admin   |
| doctor1  | doctor123  | Doctor  |
| doctor2  | doctor123  | Doctor  |
| auditor  | auditor123 | Auditor |

## API Endpoints

| Endpoint                    | Method | Description              | Roles              |
|-----------------------------|--------|--------------------------|--------------------|
| `/auth/register`            | POST   | Register new user        | Admin              |
| `/auth/login`               | POST   | Login, get JWT           | Any                |
| `/documents/upload`         | POST   | Upload PDF               | Doctor, Admin      |
| `/documents/`               | GET    | List documents           | Any (filtered)     |
| `/documents/{id}`           | GET    | Get document details     | Any (owner/admin)  |
| `/documents/{id}/process`   | POST   | OCR / text extraction    | Doctor, Admin      |
| `/entities/extract/{id}`    | POST   | Run entity extraction    | Doctor, Admin      |
| `/entities/{id}`            | GET    | Get extracted entities   | Any (owner/admin)  |
| `/entities/{id}/codes`    | GET    | Get ICD-10/CPT codes     | Any                |
| `/rag/query`                | POST   | Semantic search query    | Doctor, Admin      |
| `/audit/logs`               | GET    | View audit logs          | Admin, Auditor     |

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable            | Description                          |
|---------------------|--------------------------------------|
| `DATABASE_URL`      | PostgreSQL async connection string   |
| `MILVUS_HOST`       | Milvus vector DB host                |
| `REDIS_URL`         | Redis cache/queue URL                |
| `SECRET_KEY`        | JWT signing secret                   |
| `LLM_PROVIDER`      | `openai` or `anthropic`              |
| `OPENAI_API_KEY`    | OpenAI API key                       |
| `ANTHROPIC_API_KEY` | Anthropic API key                    |
| `EMBEDDING_MODEL`   | SentenceTransformer model name       |
| `TESSERACT_CMD`     | Tesseract binary path                |

## Dataset Generation

Generate synthetic clinical data and simulated PDFs:

```bash
cd dataset

# 1. Generate 1000 synthetic patient records
python generate_synthetic.py --patients 1000 --output synthetic_patients.json

# 2. Convert to PDFs with OCR noise
python simulate_documents.py --input synthetic_patients.json --output-dir simulated_pdfs --typos 0.02

# 3. Generate LLM-style radiology/lab reports
python llm_generate.py --output-dir llm_documents --count 200
```

## Evaluation

Run RAG evaluation against benchmark queries:

```bash
cd ai_pipeline
python evaluation.py --queries ../dataset/benchmark_queries.json
```

Metrics tracked:
- Retrieval Accuracy (overlap with expected docs)
- Mean Reciprocal Rank (MRR)
- Precision@5
- Response correctness (manual/LLM judged)
- Latency (mean, median, p95)

## Chunking Strategies

The RAG pipeline supports two chunking modes:
- **Fixed chunking**: Word-based with configurable size/overlap
- **Semantic chunking**: Sentence-boundary respecting with overlap

Set via `strategy` parameter when indexing documents.

## RBAC & Audit

- Three roles: `doctor`, `admin`, `auditor`
- JWT-based authentication with 60-minute expiry
- Every API action logged: user_id, action, resource, query, timestamp, IP
- Audit dashboard filterable by user and action type

## Docker Deployment

```bash
docker-compose up --build
```

The `docker-compose.yml` orchestrates:
- `postgres`: Metadata and audit logs
- `milvus-standalone`: Vector embeddings storage
- `redis`: Session/cache backend
- `backend`: FastAPI application

## Testing

```bash
cd backend
pytest tests/
```

## License

MIT

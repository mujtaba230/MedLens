"""Standalone embedding and indexing script for the RAG pipeline."""
import argparse
import os
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "healthcare_docs"


def index_documents(doc_dir: str, milvus_uri: str = "http://localhost:19530"):
    model = SentenceTransformer(MODEL_NAME)
    client = MilvusClient(uri=milvus_uri)

    if not client.has_collection(COLLECTION):
        client.create_collection(collection_name=COLLECTION, dimension=384, auto_id=True)

    files = [f for f in os.listdir(doc_dir) if f.endswith(".txt")]
    print(f"Indexing {len(files)} documents...")

    for fname in files:
        with open(os.path.join(doc_dir, fname)) as f:
            text = f.read()
        chunks = semantic_chunk(text)
        embeddings = model.encode([c["text"] for c in chunks], convert_to_numpy=True).tolist()

        data = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            data.append({
                "vector": emb,
                "text": chunk["text"],
                "document_id": fname,
                "chunk_index": i,
                "strategy": "semantic",
            })
        if data:
            client.insert(collection_name=COLLECTION, data=data)
            print(f"  Indexed {fname}: {len(data)} chunks")

    print("Done.")


def semantic_chunk(text: str, chunk_size: int = 512, overlap: int = 50):
    sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if s.strip()]
    chunks = []
    current_chunk = []
    current_len = 0
    for i, sent in enumerate(sentences):
        sent_len = len(sent.split())
        if current_len + sent_len > chunk_size and current_chunk:
            chunks.append({"text": ". ".join(current_chunk) + "."})
            overlap_sents = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk[-1:]
            current_chunk = overlap_sents + [sent]
            current_len = sum(len(s.split()) for s in current_chunk)
        else:
            current_chunk.append(sent)
            current_len += sent_len
    if current_chunk:
        chunks.append({"text": ". ".join(current_chunk) + "."})
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-dir", required=True)
    parser.add_argument("--milvus-uri", default="http://localhost:19530")
    args = parser.parse_args()
    index_documents(args.doc_dir, args.milvus_uri)


if __name__ == "__main__":
    main()

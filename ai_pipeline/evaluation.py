"""Evaluation metrics for RAG retrieval and response quality."""
import asyncio
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    query: str
    expected_docs: List[str]
    retrieved_docs: List[str]
    response_correct: bool
    latency_ms: float


def compute_retrieval_accuracy(results: List[EvaluationResult]) -> float:
    if not results:
        return 0.0
    scores = []
    for r in results:
        expected = set(r.expected_docs)
        retrieved = set(r.retrieved_docs)
        if expected:
            scores.append(len(expected & retrieved) / len(expected))
    return sum(scores) / len(scores) if scores else 0.0


def compute_mean_reciprocal_rank(results: List[EvaluationResult]) -> float:
    if not results:
        return 0.0
    ranks = []
    for r in results:
        for i, doc in enumerate(r.retrieved_docs, start=1):
            if doc in r.expected_docs:
                ranks.append(1.0 / i)
                break
        else:
            ranks.append(0.0)
    return sum(ranks) / len(ranks)


def compute_precision_at_k(results: List[EvaluationResult], k: int = 5) -> float:
    if not results:
        return 0.0
    scores = []
    for r in results:
        top_k = r.retrieved_docs[:k]
        expected = set(r.expected_docs)
        if top_k:
            scores.append(len(expected & set(top_k)) / len(top_k))
    return sum(scores) / len(scores) if scores else 0.0


def compute_response_accuracy(results: List[EvaluationResult]) -> float:
    if not results:
        return 0.0
    return sum(1 for r in results if r.response_correct) / len(results)


def compute_latency_stats(results: List[EvaluationResult]) -> Dict[str, float]:
    if not results:
        return {"mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0}
    latencies = sorted([r.latency_ms for r in results])
    n = len(latencies)
    return {
        "mean_ms": sum(latencies) / n,
        "median_ms": latencies[n // 2],
        "p95_ms": latencies[int(n * 0.95)],
    }


async def run_benchmark(queries_file: str, rag_service=None) -> Dict[str, Any]:
    with open(queries_file) as f:
        benchmark = json.load(f)

    results = []
    for item in benchmark:
        start = time.time()
        if rag_service:
            answer_data = await rag_service.query(item["query"])
            retrieved = [str(c["document_id"]) for c in answer_data["retrieved_chunks"]]
            latency = answer_data["latency_ms"]
        else:
            retrieved = []
            latency = (time.time() - start) * 1000

        results.append(EvaluationResult(
            query=item["query"],
            expected_docs=item.get("expected_docs", []),
            retrieved_docs=retrieved,
            response_correct=item.get("expected_answer") is None,
            latency_ms=latency,
        ))

    metrics = {
        "retrieval_accuracy": compute_retrieval_accuracy(results),
        "mrr": compute_mean_reciprocal_rank(results),
        "precision_at_5": compute_precision_at_k(results, k=5),
        "response_accuracy": compute_response_accuracy(results),
        **compute_latency_stats(results),
    }
    return metrics


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default="benchmark_queries.json")
    args = parser.parse_args()

    metrics = asyncio.run(run_benchmark(args.queries))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

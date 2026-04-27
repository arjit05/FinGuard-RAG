"""
Evaluation runner for FinGuard RAG.
Can be run directly or via GET /evaluate endpoint.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.sanitiser import sanitise
from pipeline.retrieval import hybrid_retrieve
from pipeline.reranker import rerank
from pipeline.generator import generate
from pipeline.guardrails import validate
from config import RETRIEVAL_SCORE_THRESHOLD

BENCHMARK_PATH = Path(__file__).parent / "benchmark.json"
RESULTS_PATH = Path(__file__).parent / "results.json"

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _sem_model = SentenceTransformer("all-MiniLM-L6-v2")
    _sem_available = True
except Exception:
    _sem_available = False


def _semantic_sim(a: str, b: str) -> float:
    if not _sem_available:
        return 0.0
    import numpy as np
    vecs = _sem_model.encode([a, b])
    cos = float(
        np.dot(vecs[0], vecs[1]) / (np.linalg.norm(vecs[0]) * np.linalg.norm(vecs[1]) + 1e-9)
    )
    return max(0.0, cos)


def _exact_match(expected: str, actual: str) -> bool:
    return expected.lower().strip() in actual.lower()


def _run_query(question: str, language: str = "en") -> dict:
    ok, cleaned, reason = sanitise(question)
    if not ok:
        return {"answer": "", "source": "", "confidence": "UNSURE", "retrieval_score": 0.0,
                "guardrails_passed": True, "failed_rules": [], "error": reason}
    candidates = hybrid_retrieve(cleaned)
    reranked, max_score = rerank(cleaned, candidates)
    answer_text = generate(cleaned, reranked, max_score, language=language)
    retrieved_texts = [c["text"] for c in reranked]
    gr = validate(answer_text, cleaned, max_score, retrieved_texts)

    lines = gr.sanitised_response.splitlines()
    parsed = {"answer": "", "source": "", "confidence": "UNSURE"}
    for line in lines:
        if line.startswith("Answer:"):
            parsed["answer"] = line[len("Answer:"):].strip()
        elif line.startswith("Source:"):
            parsed["source"] = line[len("Source:"):].strip()
        elif line.startswith("Confidence:"):
            parsed["confidence"] = line[len("Confidence:"):].strip()

    return {
        "answer": parsed["answer"],
        "source": parsed["source"],
        "confidence": parsed["confidence"],
        "retrieval_score": round(max_score, 4),
        "guardrails_passed": gr.passed,
        "failed_rules": gr.failed_rules,
    }


def run_evaluation() -> dict:
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        benchmark = json.load(f)

    results = []
    exact_matches = 0
    semantic_sims = []
    guardrail_passes = 0
    hallucination_count = 0
    refusal_count = 0
    latencies = []

    for item in benchmark:
        q_id = item["id"]
        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_source = item["expected_source"]
        language = item.get("language", "en")
        is_out_of_corpus = item["category"] == "Out-of-corpus"

        t0 = time.time()
        try:
            resp = _run_query(question, language)
        except Exception as e:
            resp = {"answer": "", "source": "", "confidence": "UNSURE",
                    "retrieval_score": 0.0, "guardrails_passed": False,
                    "failed_rules": [str(e)], "error": str(e)}
        elapsed = round(time.time() - t0, 3)
        latencies.append(elapsed)

        actual_answer = resp.get("answer", "")
        confidence = resp.get("confidence", "UNSURE")
        gp = resp.get("guardrails_passed", False)
        retrieval_score = resp.get("retrieval_score", 0.0)

        em = _exact_match(expected_answer, actual_answer) if not is_out_of_corpus else (confidence == "UNSURE")
        sem = _semantic_sim(expected_answer, actual_answer) if not is_out_of_corpus else (1.0 if confidence == "UNSURE" else 0.0)
        is_refusal = confidence == "UNSURE"
        is_hallucination = (retrieval_score < RETRIEVAL_SCORE_THRESHOLD and confidence in ("HIGH", "MEDIUM"))

        if em:
            exact_matches += 1
        semantic_sims.append(sem)
        if gp:
            guardrail_passes += 1
        if is_hallucination:
            hallucination_count += 1
        if is_refusal:
            refusal_count += 1

        results.append({
            "id": q_id,
            "question": question,
            "expected_answer": expected_answer,
            "actual_answer": actual_answer,
            "confidence": confidence,
            "retrieval_score": retrieval_score,
            "exact_match": em,
            "semantic_sim": round(sem, 4),
            "guardrails_passed": gp,
            "failed_rules": resp.get("failed_rules", []),
            "is_refusal": is_refusal,
            "is_hallucination": is_hallucination,
            "latency_s": elapsed,
        })

    n = len(benchmark)
    metrics = {
        "total_questions": n,
        "exact_match_accuracy": round(exact_matches / n, 4),
        "semantic_accuracy_mean": round(sum(semantic_sims) / n, 4),
        "semantic_accuracy_above_08": round(sum(1 for s in semantic_sims if s >= 0.8) / n, 4),
        "guardrail_pass_rate": round(guardrail_passes / n, 4),
        "hallucination_rate": round(hallucination_count / n, 4),
        "refusal_rate": round(refusal_count / n, 4),
        "avg_latency_s": round(sum(latencies) / n, 3),
        "p95_latency_s": round(sorted(latencies)[int(0.95 * n)], 3),
    }

    output = {"metrics": metrics, "results": results}
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n=== FinGuard RAG Evaluation Results ===")
    print(f"{'Metric':<35} {'Value':>10}")
    print("-" * 47)
    for k, v in metrics.items():
        pct = f"{v * 100:.1f}%" if isinstance(v, float) and "latency" not in k else str(v)
        print(f"{k:<35} {pct:>10}")
    print(f"\nFull results written to: {RESULTS_PATH}")
    return output


if __name__ == "__main__":
    run_evaluation()

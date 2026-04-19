from sentence_transformers import CrossEncoder

from config import RERANK_MODEL, RERANK_TOP_K, RETRIEVAL_SCORE_THRESHOLD

_cross_encoder: CrossEncoder | None = None


def _get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = CrossEncoder(RERANK_MODEL)
    return _cross_encoder


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = RERANK_TOP_K,
) -> tuple[list[dict], float]:
    """Return (reranked_top_k_chunks, max_cross_encoder_score)."""
    if not candidates:
        return [], 0.0

    model = _get_cross_encoder()
    pairs = [(query, c["text"]) for c in candidates]
    scores = model.predict(pairs).tolist()

    scored = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    max_score = top[0][0] if top else 0.0
    reranked = []
    for score, chunk in top:
        chunk = dict(chunk)
        chunk["rerank_score"] = score
        reranked.append(chunk)

    return reranked, float(max_score)

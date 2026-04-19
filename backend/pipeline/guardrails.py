import re
from dataclasses import dataclass, field

try:
    from langdetect import detect as _langdetect
except Exception:
    def _langdetect(text: str) -> str:
        return "en"

from config import RETRIEVAL_SCORE_THRESHOLD, MIN_RESPONSE_WORDS, MAX_RESPONSE_WORDS

_RETURN_PROMISE_PHRASES = [
    "guaranteed return", "assured return", "risk-free", "guaranteed profit",
    "no risk", "100% safe investment", "guaranteed income",
]

_LEGAL_ADVICE_PHRASES = [
    "you should file a case", "sue them", "file a lawsuit",
    "take legal action", "file a complaint in court",
]

_SPECULATIVE_PATTERNS = [
    re.compile(r"\bmight\s+(give|earn|return|yield|generate)\b", re.I),
    re.compile(r"\bcould\s+(earn|give|return|yield|generate)\b", re.I),
    re.compile(r"\bexpected\s+return(s)?\b", re.I),
    re.compile(r"\bpotential\s+(return|gain|profit|earning)s?\b", re.I),
    re.compile(r"\blikely\s+to\s+(give|earn|return|yield)\b", re.I),
]

_COMPETITOR_NAMES = [
    "hdfc", "icici", "kotak", "paytm", "axis bank", "yes bank",
    "indusind", "bajaj finserv", "policybazaar", "groww", "zerodha",
]

_PII_PATTERNS = [
    (re.compile(r"\b\d{12}\b"), "[AADHAAR_REDACTED]"),
    (re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"), "[PAN_REDACTED]"),
    (re.compile(r"\b[6-9]\d{9}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.\w{2,}\b"), "[EMAIL_REDACTED]"),
]

_CONFIDENCE_RE = re.compile(r"\b(HIGH|MEDIUM|LOW|UNSURE)\b")
_SOURCE_RE = re.compile(r"source\s*:", re.I)


@dataclass
class GuardrailResult:
    passed: bool
    failed_rules: list[str] = field(default_factory=list)
    sanitised_response: str = ""


def _no_return_promises(response: str) -> bool:
    lower = response.lower()
    return not any(phrase in lower for phrase in _RETURN_PROMISE_PHRASES)


def _no_legal_advice(response: str) -> bool:
    lower = response.lower()
    return not any(phrase in lower for phrase in _LEGAL_ADVICE_PHRASES)


def _redact_pii(response: str) -> str:
    for pattern, replacement in _PII_PATTERNS:
        response = pattern.sub(replacement, response)
    return response


def _no_pii_in_response(response: str) -> tuple[bool, str]:
    redacted = _redact_pii(response)
    return redacted == response, redacted


def _cites_source(response: str) -> bool:
    return bool(_SOURCE_RE.search(response))


def _confidence_present(response: str) -> bool:
    return bool(_CONFIDENCE_RE.search(response))


def _no_hallucination_markers(rerank_max_score: float) -> bool:
    return rerank_max_score >= RETRIEVAL_SCORE_THRESHOLD


def _length_reasonable(response: str) -> bool:
    word_count = len(response.split())
    return MIN_RESPONSE_WORDS < word_count < MAX_RESPONSE_WORDS


def _no_speculative_language(response: str) -> bool:
    return not any(p.search(response) for p in _SPECULATIVE_PATTERNS)


def _no_competitor_mention(response: str, retrieved_chunks: list[str] | None = None) -> bool:
    lower = response.lower()
    for name in _COMPETITOR_NAMES:
        if name in lower:
            if retrieved_chunks and any(name in chunk.lower() for chunk in retrieved_chunks):
                continue
            return False
    return True


def _hindi_response_if_hindi_query(query: str, response: str) -> bool:
    try:
        query_lang = _langdetect(query)
    except Exception:
        return True
    if query_lang != "hi":
        return True
    try:
        resp_lang = _langdetect(response)
    except Exception:
        return True
    return resp_lang in ("hi", "en")


def validate(
    response: str,
    query: str,
    rerank_max_score: float,
    retrieved_chunks: list[str] | None = None,
) -> GuardrailResult:
    failed: list[str] = []
    is_unsure = "confidence: unsure" in response.lower() or "i don't have enough information" in response.lower()

    if not _no_return_promises(response):
        failed.append("no_return_promises")

    if not _no_legal_advice(response):
        failed.append("no_legal_advice")

    pii_ok, sanitised = _no_pii_in_response(response)
    if not pii_ok:
        failed.append("no_pii_in_response")
    response = sanitised

    # Skip source, length, and hallucination checks for explicit UNSURE responses
    if not is_unsure:
        if not _cites_source(response):
            failed.append("cites_source")
        if not _no_hallucination_markers(rerank_max_score):
            failed.append("no_hallucination_markers")
        if not _length_reasonable(response):
            failed.append("length_reasonable")

    if not _confidence_present(response):
        failed.append("confidence_present")

    if not _no_speculative_language(response):
        failed.append("no_speculative_language")

    if not _no_competitor_mention(response, retrieved_chunks):
        failed.append("no_competitor_mention")

    if not _hindi_response_if_hindi_query(query, response):
        failed.append("hindi_response_if_hindi_query")

    return GuardrailResult(
        passed=len(failed) == 0,
        failed_rules=failed,
        sanitised_response=response,
    )

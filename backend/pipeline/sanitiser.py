import re

MAX_QUERY_CHARS = 2000

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(previous|above|all|prior)\s+instructions", re.I),
    re.compile(r"you\s+are\s+now\b", re.I),
    re.compile(r"forget\s+(everything|all|your)", re.I),
    re.compile(r"\bact\s+as\b", re.I),
    re.compile(r"\bjailbreak\b", re.I),
    re.compile(r"\bDAN\s+mode\b", re.I),
    re.compile(r"\bsystem\s+prompt\b", re.I),
    re.compile(r"<\|.*?\|>", re.I),
    re.compile(r"disregard\s+(all|previous|prior)\s+(instructions|rules)", re.I),
    re.compile(r"pretend\s+(you\s+are|to\s+be)", re.I),
    re.compile(r"override\s+(your\s+)?(instructions|rules|guidelines)", re.I),
]


def sanitise(query: str) -> tuple[bool, str, str | None]:
    """Return (ok, cleaned_query, reason). If not ok, reason explains rejection."""
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(query):
            return False, query, f"Matched injection pattern: {pattern.pattern}"

    if len(query) > MAX_QUERY_CHARS:
        query = query[:MAX_QUERY_CHARS]
        return True, query, "Query truncated to 2000 characters"

    return True, query, None

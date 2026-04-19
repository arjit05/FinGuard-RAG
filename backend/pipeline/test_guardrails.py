"""pytest test_guardrails.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.guardrails import validate, GuardrailResult

GOOD_RESPONSE = (
    "Answer: Banks cannot charge prepayment penalty on floating rate home loans as per RBI guidelines.\n"
    "Source: RBI_Loans_and_Advances.pdf, Section 4.2, page 1\n"
    "Confidence: HIGH"
)


def test_passing_response():
    gr = validate(GOOD_RESPONSE, "Can bank charge prepayment penalty?", rerank_max_score=0.75)
    assert gr.passed, f"Expected pass but failed: {gr.failed_rules}"


def test_return_promise_fails():
    bad = GOOD_RESPONSE.replace(
        "Banks cannot charge", "This is a guaranteed return investment"
    )
    gr = validate(bad, "query", rerank_max_score=0.75)
    assert "no_return_promises" in gr.failed_rules


def test_legal_advice_fails():
    bad = GOOD_RESPONSE + "\nYou should file a lawsuit against the bank."
    gr = validate(bad, "query", rerank_max_score=0.75)
    assert "no_legal_advice" in gr.failed_rules


def test_pii_redacted():
    with_pii = GOOD_RESPONSE + "\nYour Aadhaar: 123456789012"
    gr = validate(with_pii, "query", rerank_max_score=0.75)
    assert "no_pii_in_response" in gr.failed_rules
    assert "123456789012" not in gr.sanitised_response
    assert "[AADHAAR_REDACTED]" in gr.sanitised_response


def test_no_source_fails():
    no_source = "Answer: Some answer here with enough words to pass length check.\nConfidence: HIGH"
    gr = validate(no_source, "query", rerank_max_score=0.75)
    assert "cites_source" in gr.failed_rules


def test_no_confidence_fails():
    no_conf = "Answer: Some answer.\nSource: RBI_Loans.pdf, page 1"
    gr = validate(no_conf, "query", rerank_max_score=0.75)
    assert "confidence_present" in gr.failed_rules


def test_low_retrieval_score_fails_hallucination():
    gr = validate(GOOD_RESPONSE, "query", rerank_max_score=0.10)
    assert "no_hallucination_markers" in gr.failed_rules


def test_high_retrieval_score_passes_hallucination():
    gr = validate(GOOD_RESPONSE, "query", rerank_max_score=0.80)
    assert "no_hallucination_markers" not in gr.failed_rules


def test_too_short_fails():
    short = "Answer: No.\nSource: RBI.pdf, page 1\nConfidence: HIGH"
    gr = validate(short, "query", rerank_max_score=0.75)
    assert "length_reasonable" in gr.failed_rules


def test_competitor_mention_fails():
    with_competitor = GOOD_RESPONSE + " Unlike HDFC bank, this bank is better."
    gr = validate(with_competitor, "query", rerank_max_score=0.75, retrieved_chunks=[])
    assert "no_competitor_mention" in gr.failed_rules


def test_competitor_in_chunk_passes():
    with_competitor = GOOD_RESPONSE + " Unlike HDFC bank, this bank is better."
    gr = validate(with_competitor, "query", rerank_max_score=0.75,
                  retrieved_chunks=["HDFC bank charges 2% foreclosure fee."])
    assert "no_competitor_mention" not in gr.failed_rules


def test_pan_redacted():
    with_pan = GOOD_RESPONSE + " PAN: ABCDE1234F"
    gr = validate(with_pan, "query", rerank_max_score=0.75)
    assert "[PAN_REDACTED]" in gr.sanitised_response

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verifier import OrthogonalVerifier, ReturnCondition, verify_ai_claim, verify_crypto_route


def test_verifier_passes_all_conditions():
    verifier = OrthogonalVerifier()

    conditions = [
        ReturnCondition("condition_a", True, "Passed.", weight=1.0),
        ReturnCondition("condition_b", True, "Passed.", weight=1.0),
    ]

    result = verifier.evaluate(conditions)

    assert result.decision == "PASS"
    assert result.closure_score == 1.0
    assert result.failed_conditions == []


def test_verifier_blocks_failed_conditions():
    verifier = OrthogonalVerifier()

    conditions = [
        ReturnCondition("condition_a", True, "Passed.", weight=1.0),
        ReturnCondition("condition_b", False, "Failed.", weight=3.0),
    ]

    result = verifier.evaluate(conditions)

    assert result.decision in ["BLOCK", "REVIEW"]
    assert "condition_b" in result.failed_conditions
    assert len(result.failure_certificate) == 1


def test_verifier_reviews_empty_conditions():
    verifier = OrthogonalVerifier()

    result = verifier.evaluate([])

    assert result.decision == "REVIEW"
    assert result.closure_score == 0.0
    assert result.failure_certificate


def test_crypto_route_blocks_false_profit():
    route = {
        "nominal_profit_pct": 0.42,
        "estimated_fees_pct": 0.12,
        "estimated_slippage_pct": 0.38,
        "quote_age_seconds": 6.4,
        "liquidity_score": 0.52,
        "minimum_profit_pct": 0.25,
        "max_quote_age_seconds": 3,
        "minimum_liquidity_score": 0.70,
    }

    result = verify_crypto_route(route)

    assert result.decision == "BLOCK"
    assert "positive_net_profit" in result.failed_conditions
    assert "minimum_profit_buffer" in result.failed_conditions
    assert "fresh_quote" in result.failed_conditions
    assert "liquidity_confidence" in result.failed_conditions


def test_crypto_route_passes_clean_route():
    route = {
        "nominal_profit_pct": 1.00,
        "estimated_fees_pct": 0.10,
        "estimated_slippage_pct": 0.15,
        "quote_age_seconds": 1.0,
        "liquidity_score": 0.90,
        "minimum_profit_pct": 0.25,
        "max_quote_age_seconds": 3,
        "minimum_liquidity_score": 0.70,
    }

    result = verify_crypto_route(route)

    assert result.decision == "PASS"
    assert result.metadata["net_profit_pct"] == 0.75


def test_ai_claim_blocks_unsupported_high_risk_answer():
    payload = {
        "user_request": "Summarize the risk in this technical claim.",
        "ai_answer": "The claim appears valid and production-ready.",
        "answers_original_request": True,
        "evidence_attached": False,
        "uncertainty_flagged": False,
        "no_unsupported_high_risk_claim": False,
    }

    result = verify_ai_claim(payload)

    assert result.decision == "BLOCK"
    assert "evidence_attached" in result.failed_conditions
    assert "uncertainty_flagged" in result.failed_conditions
    assert "no_unsupported_high_risk_claim" in result.failed_conditions
